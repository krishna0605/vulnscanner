"""
Scans API routes.
Handles scan session management and lifecycle.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from api.deps import get_current_user, get_db
from models.unified_models import Project, ScanSession, ScanStatus
from schemas.dashboard import ScanSessionCreate, ScanSessionResponse
from tasks.crawler_tasks import start_crawl_task, stop_crawl_task
from core.config import settings
from kombu.exceptions import OperationalError
try:
    # Optional Celery-specific operational error for broader broker failures
    from celery.exceptions import OperationalError as CeleryOperationalError  # type: ignore
except Exception:
    CeleryOperationalError = OperationalError  # fallback to kombu error


router = APIRouter(prefix="/api/v1", tags=["scans"])
logger = logging.getLogger(__name__)


@router.get("/projects/{project_id}/scans", response_model=List[ScanSessionResponse])
async def list_project_scans(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ScanStatus] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List scans for a specific project."""
    # Verify project ownership; in development allow accessing any project by ID
    if settings.development_mode or settings.skip_supabase:
        project_query = select(Project).where(Project.id == str(project_id))
    else:
        project_query = select(Project).where(
            and_(
                Project.id == str(project_id),
                Project.owner_id == str(current_user["id"])  # ensure string comparison
            )
        )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get scans for the project
    query = select(ScanSession).where(ScanSession.project_id == project_id)
    
    if status:
        query = query.where(ScanSession.status == status.value if hasattr(status, "value") else status)
    
    query = query.offset(skip).limit(limit).order_by(ScanSession.created_at.desc())
    result = await db.execute(query)
    scans = result.scalars().all()
    
    return [ScanSessionResponse.model_validate(scan) for scan in scans]


@router.post("/projects/{project_id}/scans", status_code=status.HTTP_201_CREATED)
async def create_scan(
    project_id: str,
    scan_data: Optional[ScanSessionCreate] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new scan session."""
    # Verify project ownership; in development allow accessing any project by ID
    if settings.development_mode or settings.skip_supabase:
        project_query = select(Project).where(Project.id == str(project_id))
    else:
        project_query = select(Project).where(
            and_(
                Project.id == str(project_id),
                Project.owner_id == str(current_user["id"])  # ensure string comparison
            )
        )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Build configuration starting from user-provided fields
    base_config: dict = {}
    if scan_data and getattr(scan_data, "configuration", None) is not None:
        if hasattr(scan_data.configuration, "model_dump"):
            base_config = scan_data.configuration.model_dump(exclude_unset=True)
        elif isinstance(scan_data.configuration, dict):
            base_config = dict(scan_data.configuration)

    # Minimal defaults expected by tests
    if "max_pages" not in base_config:
        base_config["max_pages"] = 1000
    if "requests_per_second" not in base_config:
        base_config["requests_per_second"] = 10

    scan = ScanSession(
        project_id=project_id,
        created_by=current_user["id"],
        configuration=base_config,
        status=ScanStatus.PENDING
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Determine target URL (prefer explicit configuration or project domain)
    target_url = base_config.get("target_url") or project.target_domain or ""
    if target_url and not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = f"https://{target_url}"

    if not target_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Target URL is required. Set project target_domain or include target_url in configuration."
        )

    # Enqueue background crawl task
    try:
        async_result = start_crawl_task.delay(
            project_id=str(project_id),
            url=target_url,
            scan_id=str(scan.id),
            config=base_config,
        )
        return {
            "scan_id": str(scan.id),
            "task_id": async_result.id,
            "status": "enqueued",
        }
    except (OperationalError, CeleryOperationalError) as e:
        logger.error(
            "Celery broker unavailable for scan %s: %s",
            str(scan.id), str(e)
        )
        # Return immediate error to the client; do not attempt local fallback
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue is unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(
            "Task enqueue error for scan %s: %s",
            str(scan.id), str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue scan task."
        )


@router.get("/scans/{scan_id}", response_model=ScanSessionResponse)
async def get_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific scan session."""
    # In development, bypass owner check to simplify local testing
    if settings.development_mode or settings.skip_supabase:
        query = select(ScanSession).where(ScanSession.id == str(scan_id))
    else:
        query = select(ScanSession).join(Project).where(
            and_(
                ScanSession.id == str(scan_id),
                Project.owner_id == str(current_user["id"])  # ensure string comparison
            )
        )
    result = await db.execute(query)
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return ScanSessionResponse.model_validate(scan)


@router.put("/scans/{scan_id}/stop", response_model=ScanSessionResponse)
async def stop_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop a running scan."""
    # In development, bypass owner check to simplify local testing
    if settings.development_mode or settings.skip_supabase:
        query = select(ScanSession).where(ScanSession.id == str(scan_id))
    else:
        query = select(ScanSession).join(Project).where(
            and_(
                ScanSession.id == str(scan_id),
                Project.owner_id == str(current_user["id"])  # ensure string comparison
            )
        )
    result = await db.execute(query)
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    if scan.status not in [ScanStatus.PENDING, ScanStatus.QUEUED, ScanStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scan cannot be stopped in current state"
        )
    
    # Enqueue background stop task (best-effort)
    try:
        stop_crawl_task.delay(str(scan.id))
    except Exception:
        # Do not fail the request if task enqueue fails
        pass

    scan.status = ScanStatus.CANCELLED
    await db.commit()
    await db.refresh(scan)
    
    return ScanSessionResponse.model_validate(scan)


@router.delete("/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a scan session."""
    # In development, bypass owner check to simplify local testing
    if settings.development_mode or settings.skip_supabase:
        query = select(ScanSession).where(ScanSession.id == str(scan_id))
    else:
        query = select(ScanSession).join(Project).where(
            and_(
                ScanSession.id == str(scan_id),
                Project.owner_id == str(current_user["id"])  # ensure string comparison
            )
        )
    result = await db.execute(query)
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    if scan.status == ScanStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete running scan"
        )
    
    await db.delete(scan)
    await db.commit()