"""
API routes for scan results including discovered URLs, forms, and technology fingerprints.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, distinct

from api.deps import get_db
from core.auth_deps import get_user_id
from models import (
    ScanSession, Project, DiscoveredUrl, ExtractedForm, TechnologyFingerprint
)
from schemas.scan_results import (
    DiscoveredURLResponse, DiscoveredURLFilter, DiscoveredURLCreate,
    ExtractedFormResponse, ExtractedFormFilter, ExtractedFormCreate,
    TechnologyFingerprintResponse, TechnologyFingerprintFilter, TechnologyFingerprintCreate,
    ScanResultsSummary, ScanResultsExport
)
from schemas.sqlite_dashboard import PaginationParams
from tasks.report_tasks import generate_report_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["scan-results"])


# Discovered URLs endpoints
@router.get("/scans/{scan_id}/urls", response_model=List[DiscoveredURLResponse])
async def list_scan_urls(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    filters: DiscoveredURLFilter = Depends(),
    pagination: PaginationParams = Depends()
):
    """List discovered URLs for a scan session."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Build query with filters
        query = select(DiscoveredUrl).where(DiscoveredUrl.session_id == scan_id_str)
        
        if filters.status_code:
            query = query.where(DiscoveredUrl.status_code == filters.status_code)
        if filters.content_type:
            query = query.where(DiscoveredUrl.content_type.ilike(f"%{filters.content_type}%"))
        if filters.method:
            query = query.where(DiscoveredUrl.method == filters.method)
        if filters.url_pattern:
            query = query.where(DiscoveredUrl.url.ilike(f"%{filters.url_pattern}%"))
        if filters.min_response_time:
            query = query.where(DiscoveredUrl.response_time >= filters.min_response_time)
        if filters.max_response_time:
            query = query.where(DiscoveredUrl.response_time <= filters.max_response_time)
        
        query = (
            query.order_by(desc(DiscoveredUrl.discovered_at))
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        
        result = await db.execute(query)
        urls = result.scalars().all()
        
        return urls
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing scan URLs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan URLs: {str(e)}"
        )


@router.post("/scans/{scan_id}/urls", response_model=DiscoveredURLResponse, status_code=status.HTTP_201_CREATED)
async def create_discovered_url(
    scan_id: UUID,
    url_data: DiscoveredURLCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Create a new discovered URL entry."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Check for duplicate URL
        existing_query = select(DiscoveredUrl).where(
            and_(
                DiscoveredUrl.session_id == scan_id_str,
                DiscoveredUrl.url == url_data.url,
                DiscoveredUrl.method == url_data.method
            )
        )
        existing_result = await db.execute(existing_query)
        existing_url = existing_result.scalar_one_or_none()
        
        if existing_url:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="URL already exists for this scan"
            )
        
        discovered_url = DiscoveredUrl(
            session_id=scan_id_str,
            **url_data.model_dump()
        )
        
        db.add(discovered_url)
        await db.commit()
        await db.refresh(discovered_url)
        
        return discovered_url
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating discovered URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create discovered URL: {str(e)}"
        )


@router.get("/scans/{scan_id}/urls/{url_id}", response_model=DiscoveredURLResponse)
async def get_discovered_url(
    scan_id: UUID,
    url_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Get a specific discovered URL."""
    try:
        # Convert UUIDs to strings for SQLite compatibility
        scan_id_str = str(scan_id)
        url_id_str = str(url_id)
        
        query = (
            select(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    DiscoveredUrl.id == url_id_str,
                    DiscoveredUrl.session_id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        result = await db.execute(query)
        url = result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discovered URL not found"
            )
        
        return url
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting discovered URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve discovered URL: {str(e)}"
        )


# Extracted Forms endpoints
@router.get("/scans/{scan_id}/forms", response_model=List[ExtractedFormResponse])
async def list_scan_forms(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    filters: ExtractedFormFilter = Depends(),
    pagination: PaginationParams = Depends()
):
    """List extracted forms for a scan session."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Build query with filters
        query = (
            select(ExtractedForm)
            .join(DiscoveredUrl)
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        
        if filters.form_method:
            query = query.where(ExtractedForm.form_method == filters.form_method)
        if filters.has_csrf_token is not None:
            if filters.has_csrf_token:
                query = query.where(func.json_array_length(ExtractedForm.csrf_tokens) > 0)
            else:
                query = query.where(func.json_array_length(ExtractedForm.csrf_tokens) == 0)
        if filters.authentication_required is not None:
            query = query.where(ExtractedForm.authentication_required == filters.authentication_required)
        if filters.action_pattern:
            query = query.where(ExtractedForm.form_action.ilike(f"%{filters.action_pattern}%"))
        
        query = (
            query.order_by(desc(DiscoveredUrl.discovered_at))
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        
        result = await db.execute(query)
        forms = result.scalars().all()
        
        return forms
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing scan forms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan forms: {str(e)}"
        )


@router.post("/scans/{scan_id}/forms", response_model=ExtractedFormResponse, status_code=status.HTTP_201_CREATED)
async def create_extracted_form(
    scan_id: UUID,
    form_data: ExtractedFormCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Create a new extracted form entry."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify URL belongs to the scan and user owns it
        url_query = (
            select(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    DiscoveredUrl.id == form_data.url_id,
                    DiscoveredUrl.session_id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        url_result = await db.execute(url_query)
        url = url_result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found for this scan"
            )
        
        extracted_form = ExtractedForm(**form_data.model_dump())
        
        db.add(extracted_form)
        await db.commit()
        await db.refresh(extracted_form)
        
        return extracted_form
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating extracted form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create extracted form: {str(e)}"
        )


@router.get("/scans/{scan_id}/forms/{form_id}", response_model=ExtractedFormResponse)
async def get_extracted_form(
    scan_id: UUID,
    form_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Get a specific extracted form."""
    try:
        # Convert UUIDs to strings for SQLite compatibility
        scan_id_str = str(scan_id)
        form_id_str = str(form_id)
        
        query = (
            select(ExtractedForm)
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    ExtractedForm.id == form_id_str,
                    DiscoveredUrl.session_id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        result = await db.execute(query)
        form = result.scalar_one_or_none()
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Extracted form not found"
            )
        
        return form
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting extracted form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve extracted form: {str(e)}"
        )


# Technology Fingerprints endpoints
@router.get("/scans/{scan_id}/technologies", response_model=List[TechnologyFingerprintResponse])
async def list_scan_technologies(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    filters: TechnologyFingerprintFilter = Depends(),
    pagination: PaginationParams = Depends()
):
    """List technology fingerprints for a scan session."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Build query with filters
        query = (
            select(TechnologyFingerprint)
            .join(DiscoveredUrl)
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        
        if filters.server_software:
            query = query.where(TechnologyFingerprint.server_software.ilike(f"%{filters.server_software}%"))
        if filters.programming_language:
            query = query.where(TechnologyFingerprint.programming_language.ilike(f"%{filters.programming_language}%"))
        if filters.framework:
            query = query.where(TechnologyFingerprint.framework.ilike(f"%{filters.framework}%"))
        if filters.cms:
            query = query.where(TechnologyFingerprint.cms.ilike(f"%{filters.cms}%"))
        
        query = (
            query.order_by(desc(TechnologyFingerprint.detected_at))
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        
        result = await db.execute(query)
        technologies = result.scalars().all()
        
        return technologies
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing scan technologies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan technologies: {str(e)}"
        )


@router.post("/scans/{scan_id}/technologies", response_model=TechnologyFingerprintResponse, status_code=status.HTTP_201_CREATED)
async def create_technology_fingerprint(
    scan_id: UUID,
    tech_data: TechnologyFingerprintCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Create a new technology fingerprint entry."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify URL belongs to the scan and user owns it
        url_query = (
            select(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    DiscoveredUrl.id == tech_data.url_id,
                    DiscoveredUrl.session_id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        url_result = await db.execute(url_query)
        url = url_result.scalar_one_or_none()
        
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found for this scan"
            )
        
        technology_fingerprint = TechnologyFingerprint(**tech_data.model_dump())
        
        db.add(technology_fingerprint)
        await db.commit()
        await db.refresh(technology_fingerprint)
        
        return technology_fingerprint
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating technology fingerprint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create technology fingerprint: {str(e)}"
        )


@router.get("/scans/{scan_id}/technologies/{tech_id}", response_model=TechnologyFingerprintResponse)
async def get_technology_fingerprint(
    scan_id: UUID,
    tech_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Get a specific technology fingerprint."""
    try:
        # Convert UUIDs to strings for SQLite compatibility
        scan_id_str = str(scan_id)
        tech_id_str = str(tech_id)
        
        query = (
            select(TechnologyFingerprint)
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    TechnologyFingerprint.id == tech_id_str,
                    DiscoveredUrl.session_id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        result = await db.execute(query)
        tech = result.scalar_one_or_none()
        
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technology fingerprint not found"
            )
        
        return tech
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technology fingerprint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve technology fingerprint: {str(e)}"
        )


# Scan Results Summary and Export endpoints
@router.get("/scans/{scan_id}/summary", response_model=ScanResultsSummary)
async def get_scan_results_summary(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Get a summary of scan results."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Get counts
        urls_count_query = select(func.count(DiscoveredUrl.id)).where(DiscoveredUrl.session_id == scan_id_str)
        urls_count_result = await db.execute(urls_count_query)
        urls_count = urls_count_result.scalar()
        
        forms_count_query = (
            select(func.count(ExtractedForm.id))
            .join(DiscoveredUrl)
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        forms_count_result = await db.execute(forms_count_query)
        forms_count = forms_count_result.scalar()
        
        tech_count_query = (
            select(func.count(TechnologyFingerprint.id))
            .join(DiscoveredUrl)
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        tech_count_result = await db.execute(tech_count_query)
        tech_count = tech_count_result.scalar()
        
        # Get unique domains
        domains_query = (
            select(func.count(distinct(func.split_part(DiscoveredUrl.url, '/', 3))))
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        domains_result = await db.execute(domains_query)
        unique_domains = domains_result.scalar()
        
        # Get status code distribution
        status_codes_query = (
            select(DiscoveredUrl.status_code, func.count(DiscoveredUrl.id))
            .where(DiscoveredUrl.session_id == scan_id_str)
            .group_by(DiscoveredUrl.status_code)
        )
        status_codes_result = await db.execute(status_codes_query)
        status_code_distribution = {str(code): count for code, count in status_codes_result.all() if code}
        
        return ScanResultsSummary(
            scan_id=scan_id,
            total_urls=urls_count,
            total_forms=forms_count,
            total_technologies=tech_count,
            unique_domains=unique_domains,
            status_code_distribution=status_code_distribution,
            generated_at=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan results summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan results summary: {str(e)}"
        )


@router.get("/scans/{scan_id}/export")
async def export_scan_results_direct(
    scan_id: UUID,
    format: str = Query(..., pattern="^(json|csv|pdf)$"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Export scan results directly in the specified format."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Get all scan data
        urls_query = select(DiscoveredUrl).where(DiscoveredUrl.session_id == scan_id_str)
        urls_result = await db.execute(urls_query)
        urls = urls_result.scalars().all()
        
        forms_query = (
            select(ExtractedForm)
            .join(DiscoveredUrl)
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        forms_result = await db.execute(forms_query)
        forms = forms_result.scalars().all()
        
        techs_query = (
            select(TechnologyFingerprint)
            .join(DiscoveredUrl)
            .where(DiscoveredUrl.session_id == scan_id_str)
        )
        techs_result = await db.execute(techs_query)
        techs = techs_result.scalars().all()
        
        if format == "json":
            from fastapi.responses import JSONResponse
            data = {
                "scan_id": str(scan_id),
                "scan_status": scan.status.value if hasattr(scan.status, 'value') else str(scan.status),
                "start_time": scan.start_time.isoformat() if scan.start_time else None,
                "end_time": scan.end_time.isoformat() if scan.end_time else None,
                "urls": [
                    {
                        "url": url.url,
                        "method": url.method,
                        "status_code": url.status_code,
                        "content_type": url.content_type,
                        "page_title": url.page_title
                    } for url in urls
                ],
                "forms": [
                    {
                        "form_action": form.form_action,
                        "form_method": form.form_method,
                        "form_fields": form.form_fields
                    } for form in forms
                ],
                "technologies": [
                    {
                        "server_software": tech.server_software,
                        "programming_language": tech.programming_language,
                        "framework": tech.framework,
                        "cms": tech.cms
                    } for tech in techs
                ]
            }
            return JSONResponse(content=data, headers={"content-type": "application/json"})
        
        elif format == "csv":
            import csv
            import io
            from fastapi.responses import StreamingResponse
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(["url", "method", "status_code", "content_type", "page_title"])
            
            # Write URL data
            for url in urls:
                writer.writerow([
                    url.url,
                    url.method,
                    url.status_code,
                    url.content_type,
                    url.page_title
                ])
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}_results.csv"}
            )
        
        elif format == "pdf":
            # For now, return a simple text response indicating PDF generation
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(
                content=f"PDF export for scan {scan_id} - Feature coming soon",
                media_type="application/pdf"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting scan results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export scan results: {str(e)}"
        )


@router.post("/scans/{scan_id}/export", response_model=Dict[str, Any])
async def export_scan_results(
    scan_id: UUID,
    export_request: ScanResultsExport,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Export scan results in the specified format."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Start background task for report generation
        task = generate_report_task.delay(
            scan_id=str(scan_id),
            format=export_request.format,
            user_id=user_id
        )
        
        return {
            "task_id": task.id,
            "status": "processing",
            "scan_id": str(scan_id),
            "format": export_request.format,
            "message": "Report generation started. You will be notified when complete."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting scan results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export scan results: {str(e)}"
        )


@router.get("/scans/{scan_id}/export/{task_id}/status")
async def get_export_status(
    scan_id: UUID,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Get the status of an export task."""
    try:
        # Convert UUID to string for SQLite compatibility
        scan_id_str = str(scan_id)
        
        # Verify scan ownership
        scan_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id_str,
                    Project.owner_id == user_id
                )
            )
        )
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan session not found"
            )
        
        # Get task status from Celery
        from tasks.celery_app import celery_app
        task = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "scan_id": str(scan_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export status: {str(e)}"
        )