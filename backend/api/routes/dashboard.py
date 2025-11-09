"""
Dashboard API endpoints for the vulnerability scanner.
Provides CRUD operations for projects, scans, and real-time data with enhanced authentication.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
# from uuid import UUID  # Not needed for SQLite models

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case

from api.deps import get_db
from models import (
    Project, ScanSession, DiscoveredUrl, ExtractedForm, 
    ScanStatus, RealtimeUpdate
)
from schemas.sqlite_dashboard import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectSummary,
    ScanSessionCreate, ScanSessionResponse, DashboardMetricUpdate,
    DashboardOverview, PaginationParams, ScanSessionFilter, RealTimeUpdate as RealtimeUpdateSchema
)
from core.auth_deps import get_user_id
from core.config import settings
from check_services import run_checks
from api.routes.websocket import manager
from services.dashboard_service import DashboardService
from tasks.crawler_tasks import start_crawl_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


# Database session dependency is imported from api.deps


# Project CRUD endpoints moved to `/api/v1/projects` router for single-source management.


@router.get("/projects/{project_id}/summary", response_model=ProjectSummary)
async def get_project_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """Get project summary statistics."""
    try:
        # Use UUIDs directly for Supabase compatibility
        # Verify project ownership
        project_query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.owner_id == user_id
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get scan statistics
        scan_stats_query = (
            select(
                func.count(ScanSession.id).label("total_scans"),
                func.sum(case((ScanSession.status == ScanStatus.RUNNING, 1), else_=0)).label("active_scans"),
                func.sum(case((ScanSession.status == ScanStatus.COMPLETED, 1), else_=0)).label("completed_scans"),
                func.sum(case((ScanSession.status == ScanStatus.FAILED, 1), else_=0)).label("failed_scans"),
                func.max(ScanSession.start_time).label("last_scan_date")
            )
            .where(ScanSession.project_id == project_id)
        )
        scan_stats_result = await db.execute(scan_stats_query)
        scan_stats = scan_stats_result.first()
        
        # Get URL and form counts
        url_count_query = (
            select(func.count(DiscoveredUrl.id))
            .join(ScanSession)
            .where(ScanSession.project_id == project_id)
        )
        url_count_result = await db.execute(url_count_query)
        total_urls = url_count_result.scalar() or 0
        
        form_count_query = (
            select(func.count(ExtractedForm.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .where(ScanSession.project_id == project_id)
        )
        form_count_result = await db.execute(form_count_query)
        total_forms = form_count_result.scalar() or 0
        
        return ProjectSummary(
            total_scans=scan_stats.total_scans or 0,
            active_scans=scan_stats.active_scans or 0,
            completed_scans=scan_stats.completed_scans or 0,
            failed_scans=scan_stats.failed_scans or 0,
            total_urls_discovered=total_urls,
            total_forms_found=total_forms,
            last_scan_date=scan_stats.last_scan_date
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project summary: {str(e)}"
        )


# Scan session endpoints are handled by `/api/v1` scans router.


# Scan creation is handled by `/api/v1` scans router.


# Scan retrieval is handled by `/api/v1` scans router.


# Scan stop is handled by `/api/v1` scans router.


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    time_range: str = Query("7d", pattern="^(1h|6h|24h|7d|30d|90d)$")
) -> DashboardOverview:
    """
    Get comprehensive dashboard overview with real-time metrics and enhanced analytics.
    """
    logger.info("Starting /dashboard/overview endpoint")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Time Range: {time_range}")

    try:
        # Initialize DashboardService
        logger.info("Initializing DashboardService")
        dashboard_service = DashboardService(db)

        # Fetch data using DashboardService
        logger.info("Fetching user overview data")
        metrics = await dashboard_service.get_user_overview(user_id)

        logger.info("Successfully fetched user overview data")
        return metrics

    except Exception as e:
        logger.error(f"Error in /dashboard/overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard overview: {str(e)}"
        )


@router.get("/metrics/live", response_model=Dict[str, Any])
async def get_live_metrics(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    metric_type: str = Query("all", pattern="^(all|scans|urls|forms|performance)$")
) -> Dict[str, Any]:
    """
    Get live dashboard metrics with real-time updates.
    """
    try:
        dashboard_service = DashboardService(db)
        metrics = await dashboard_service.get_live_metrics(user_id, metric_type)
        
        # Broadcast metric update to connected clients
        await manager.broadcast_dashboard_metric(
            user_id=user_id,
            metric_type=metric_type,
            data=metrics
        )
        
        return {
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error getting live metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get live metrics"
        )


@router.post("/metrics/update")
async def update_dashboard_metric(
    metric_update: DashboardMetricUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """
    Update a dashboard metric and broadcast to all connected clients.
    """
    try:
        # Store the metric update in database
        realtime_update = RealtimeUpdate(
            user_id=user_id,
            update_type="metric_update",
            data={
                "metric_name": metric_update.metric_name,
                "value": metric_update.value,
                "metadata": metric_update.metadata
            },
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(realtime_update)
        await db.commit()
        
        # Broadcast to all connected clients
        background_tasks.add_task(
            manager.broadcast_dashboard_metric,
            user_id=user_id,
            metric_type=metric_update.metric_name,
            data={
                "value": metric_update.value,
                "metadata": metric_update.metadata,
                "timestamp": realtime_update.created_at.isoformat()
            }
        )
        
        return {"status": "success", "update_id": str(realtime_update.id)}
        
    except Exception as e:
        logger.error(f"Error updating dashboard metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dashboard metric"
        )


@router.get("/realtime/updates")
async def get_realtime_updates(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    limit: int = Query(50, ge=1, le=100),
    since: Optional[datetime] = Query(None)
) -> Dict[str, Any]:
    """
    Get recent real-time updates for the user.
    """
    try:
        query = select(RealtimeUpdate).where(RealtimeUpdate.user_id == user_id)
        
        if since:
            query = query.where(RealtimeUpdate.created_at > since)
            
        query = query.order_by(desc(RealtimeUpdate.created_at)).limit(limit)
        
        result = await db.execute(query)
        updates = result.scalars().all()
        
        return {
            "updates": [
                RealtimeUpdateSchema(
                    id=update.id,
                    user_id=update.user_id,
                    update_type=update.update_type,
                    data=update.data,
                    created_at=update.created_at
                )
                for update in updates
            ],
            "count": len(updates),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting realtime updates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get realtime updates"
        )


@router.post("/realtime/broadcast")
async def broadcast_custom_update(
    update_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    """
    Broadcast a custom real-time update to all connected clients.
    """
    try:
        # Validate update data
        if not update_data.get("type") or not update_data.get("data"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update must include 'type' and 'data' fields"
            )
        
        # Store the update
        realtime_update = RealtimeUpdate(
            user_id=user_id,
            update_type=update_data["type"],
            data=update_data["data"],
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(realtime_update)
        await db.commit()
        
        # Broadcast to connected clients
        background_tasks.add_task(
            manager.broadcast_realtime_update,
            user_id=user_id,
            update_type=update_data["type"],
            data=update_data["data"]
        )
        
        return {
            "status": "success",
            "update_id": str(realtime_update.id),
            "broadcast_time": realtime_update.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting custom update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to broadcast update"
        )


@router.get("/analytics/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    time_range: str = Query("7d", pattern="^(1h|6h|24h|7d|30d|90d)$")
) -> Dict[str, Any]:
    """
    Get comprehensive analytics summary for the dashboard.
    """
    try:
        time_delta_map = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        time_delta = time_delta_map[time_range]
        dashboard_service = DashboardService(db)
        analytics = await dashboard_service.get_analytics_summary(user_id, time_delta)
        
        return {
            "analytics": analytics,
            "time_range": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics summary"
        )


@router.get("/projects-summary", response_model=List[Dict[str, Any]])
async def get_projects_summary(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    limit: int = Query(10, ge=1, le=100)
) -> List[Dict[str, Any]]:
    """
    Get projects summary for dashboard display.
    Optimized to avoid N+1 queries by using a single JOIN query.
    """
    try:
        # Create subquery to get the latest scan for each project
        latest_scans_subquery = (
            select(
                ScanSession.project_id,
                func.max(ScanSession.start_time).label('latest_start_time')
            )
            .group_by(ScanSession.project_id)
            .subquery()
        )
        
        # Main query with LEFT JOIN to get projects and their latest scan in one query
        query = (
            select(
                Project.id,
                Project.name,
                Project.target_domain,
                Project.created_at,
                ScanSession.start_time,
                ScanSession.status
            )
            .outerjoin(
                latest_scans_subquery,
                Project.id == latest_scans_subquery.c.project_id
            )
            .outerjoin(
                ScanSession,
                and_(
                    ScanSession.project_id == Project.id,
                    ScanSession.start_time == latest_scans_subquery.c.latest_start_time
                )
            )
            .where(Project.owner_id == user_id)
            .order_by(desc(Project.created_at))
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        projects_summary = []
        for row in rows:
            # Get vulnerability counts (placeholder for now)
            vulnerability_count = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
            
            # Handle scan status conversion
            scan_status = "pending"
            if row.status:
                scan_status = row.status if isinstance(row.status, str) else row.status.value
            
            projects_summary.append({
                "id": str(row.id),
                "name": row.name,
                "target_domain": row.target_domain,
                "last_scan_date": row.start_time.isoformat() if row.start_time else None,
                "vulnerability_count": vulnerability_count,
                "scan_status": scan_status,
                "progress": None
            })
        
        return projects_summary
        
    except Exception as e:
        logger.error(f"Error getting projects summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects summary"
        )


@router.get("/recent-activity", response_model=List[Dict[str, Any]])
async def get_recent_activity(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict[str, Any]]:
    """
    Get recent activity for dashboard display.
    """
    try:
        # Use UUID directly for Supabase compatibility
        
        # Get recent scans and projects
        recent_scans_query = (
            select(ScanSession, Project.name.label("project_name"))
            .join(Project)
            .where(Project.owner_id == user_id)
            .order_by(desc(ScanSession.start_time))
            .limit(limit)
        )
        result = await db.execute(recent_scans_query)
        recent_scans = result.all()
        
        activities = []
        for scan, project_name in recent_scans:
            activity_type = "scan_completed" if scan.status == ScanStatus.COMPLETED else "scan_started"
            if scan.status == ScanStatus.FAILED:
                activity_type = "scan_failed"
            
            activities.append({
                "id": str(scan.id),
                "type": activity_type,
                "title": f"Scan {scan.status if isinstance(scan.status, str) else scan.status.value} for {project_name}",
                "description": f"Target: {project_name}",
                "timestamp": scan.start_time.isoformat(),
                "project_name": project_name,
                "severity": None,
                "metadata": {
                    "project_id": str(scan.project_id),
                    "scan_id": str(scan.id)
                }
            })
        
        return activities
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent activity"
        )


@router.get("/vulnerability-trends", response_model=List[Dict[str, Any]])
async def get_vulnerability_trends(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
    days: int = Query(30, ge=1, le=365)
) -> List[Dict[str, Any]]:
    """
    Get vulnerability trends for dashboard charts.
    """
    try:
        # For now, return empty trends as we don't have vulnerability data yet
        # This will be populated when vulnerability detection is implemented
        trends = []
        
        # Generate empty trend data for the requested days
        from datetime import date, timedelta
        start_date = date.today() - timedelta(days=days)
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            trends.append({
                "date": current_date.isoformat(),
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            })
        
        return trends
        
    except Exception as e:
        logger.error(f"Error getting vulnerability trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vulnerability trends"
        )


@router.get("/scan-statistics", response_model=Dict[str, Any])
async def get_scan_statistics(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
) -> Dict[str, Any]:
    """
    Get scan statistics for dashboard display.
    """
    try:
        # Use UUID directly for Supabase compatibility
        
        # Get scan statistics
        stats_query = (
            select(
                func.count(ScanSession.id).label("total_scans"),
                func.sum(case((ScanSession.status == ScanStatus.RUNNING, 1), else_=0)).label("active_scans"),
                func.sum(case((ScanSession.status == ScanStatus.COMPLETED, 1), else_=0)).label("completed_scans"),
                func.sum(case((ScanSession.status == ScanStatus.FAILED, 1), else_=0)).label("failed_scans"),
                func.avg(
                    case(
                        (ScanSession.end_time.isnot(None), 
                         func.extract('epoch', ScanSession.end_time - ScanSession.start_time)),
                        else_=None
                    )
                ).label("avg_duration")
            )
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        result = await db.execute(stats_query)
        stats = result.first()
        
        total_scans = stats.total_scans or 0
        completed_scans = stats.completed_scans or 0
        success_rate = (completed_scans / total_scans * 100) if total_scans > 0 else 0
        
        return {
            "total_scans": total_scans,
            "active_scans": stats.active_scans or 0,
            "completed_scans": completed_scans,
            "failed_scans": stats.failed_scans or 0,
            "avg_duration": float(stats.avg_duration or 0),
            "success_rate": success_rate
        }
        
    except Exception as e:
        logger.error(f"Error getting scan statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scan statistics"
        )


@router.get("/health")
async def dashboard_health_check(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id)
) -> Dict[str, Any]:
    """
    Health check endpoint for dashboard services.
    """
    try:
        # Check core infrastructure services
        infra_status = run_checks(settings)
        
        # Check WebSocket manager status
        connection_stats = await manager.get_connection_stats()

        return {
            "status": "healthy" if all(not v.startswith("Failed") for v in infra_status.values()) else "degraded",
            "infrastructure": infra_status,
            "websocket_connections": connection_stats["active_connections"],
            "active_users": connection_stats["unique_users"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Dashboard health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }