"""
Projects API routes.
Handles CRUD operations for projects.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.deps import get_current_user, get_db
from core.config import settings
from models.unified_models import Project, Profile
from schemas.dashboard import ProjectCreate, ProjectUpdate, ProjectResponse


router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's projects with optional search, domain filtering, and pagination."""
    
    # In development, show all projects to simplify local testing and selection
    if settings.development_mode or settings.skip_supabase:
        query = select(Project)
    else:
        query = select(Project).where(Project.owner_id == current_user["id"])    
    
    if search:
        query = query.where(Project.name.ilike(f"%{search}%"))
    
    if domain:
        query = query.where(Project.target_domain == domain)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return [ProjectResponse.model_validate(project) for project in projects]

# Alias route without trailing slash to avoid implicit redirects from clients
@router.get("", response_model=List[ProjectResponse])
async def list_projects_no_slash(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await list_projects(
        skip=skip,
        limit=limit,
        search=search,
        domain=domain,
        current_user=current_user,
        db=db,
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    # Simplify owner_id assignment
    owner_id = str(current_user["id"])
    logger.info(f"Creating project for user {owner_id}")

    # Ensure owner profile exists to satisfy foreign key constraint
    result = await db.execute(select(Profile).where(Profile.id == owner_id))
    profile = result.scalar_one_or_none()

    if not profile:
        logger.info(f"Profile not found for user {owner_id}. Creating a new one.")
        profile = Profile(
            id=owner_id,
            email=current_user.get("email") or f"{owner_id}@local.dev",
            full_name=current_user.get("full_name") or None,
            username=current_user.get("username") or None,
        )
        db.add(profile)
        try:
            await db.flush()
            logger.info(f"Successfully created profile for user {owner_id}")
        except IntegrityError:
            # Race condition: profile was created by another concurrent request
            await db.rollback()
            # Remove pending instance so it won't be re-flushed on the next commit
            try:
                db.expunge(profile)
            except Exception:
                pass
            logger.warning(f"Profile for user {owner_id} already exists.")

    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=owner_id,
        target_domain=project_data.target_domain,
        scope_rules=project_data.scope_rules or []
    )

    try:
        db.add(project)
        await db.commit()
        await db.refresh(project)
        logger.info(f"Successfully created project {project.id} for user {owner_id}")
    except IntegrityError as exc:
        await db.rollback()
        # Log full exception details for diagnostics
        logger.error(f"Failed to create project: {exc}", exc_info=True)
        # Provide a clear client error instead of a generic failure
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create project: {getattr(exc, 'orig', exc)}"
        )

    return ProjectResponse.model_validate(project)


# Alias route without trailing slash for POST to avoid 405 on strict clients
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_no_slash(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_project(
        project_data=project_data,
        current_user=current_user,
        db=db,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project."""
    # In development, bypass owner check to simplify local testing
    if settings.development_mode or settings.skip_supabase:
        query = select(Project).where(Project.id == project_id)
    else:
        query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.owner_id == current_user["id"]
            )
        )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a project."""
    query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.owner_id == current_user["id"]
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project."""
    query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.owner_id == current_user["id"]
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()