"""
Dashboard service layer for business logic and data operations.
Handles complex dashboard operations and data aggregation.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
# from uuid import UUID  # Not needed for SQLite models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
from sqlalchemy.orm import selectinload

from models import (
    Project, ScanSession, DiscoveredUrl, ExtractedForm, 
    TechnologyFingerprint, ScanStatus
)
from schemas.dashboard import (
    DashboardOverview, ProjectSummary, ScanSummary
)
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """Service class for dashboard operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_overview(self, user_id: str) -> DashboardOverview:
        """Get comprehensive dashboard overview for a user."""
        try:
            # Get project statistics
            project_stats = await self._get_project_stats(user_id)
            
            # Get scan statistics
            scan_stats = await self._get_scan_stats(user_id)
            
            # Get discovery statistics
            discovery_stats = await self._get_discovery_stats(user_id)
            
            # Get recent activity
            recent_activity = await self._get_recent_activity(user_id, limit=10)
            
            # Get recent projects and scans
            recent_projects = await self._get_recent_projects(user_id, limit=5)
            recent_scans = await self._get_recent_scans(user_id, limit=5)
            
            return DashboardOverview(
                total_projects=project_stats["total"],
                total_scans=scan_stats["total"],
                active_scans=scan_stats["active"],
                total_urls_discovered=discovery_stats["urls"],
                total_forms_found=discovery_stats["forms"],
                total_technologies_detected=discovery_stats["technologies"],
                recent_projects=recent_projects,
                recent_scans=recent_scans
            )
            
        except Exception as e:
            logger.error(f"Error getting user overview: {e}")
            raise
    
    async def get_project_summary(self, project_id: int, user_id: str) -> ProjectSummary:
        """Get detailed summary for a specific project."""
        try:
            # Verify project ownership
            project = await self._verify_project_access(project_id, user_id)
            
            # Get scan statistics for this project
            scan_stats_query = (
                select(
                    func.count(ScanSession.id).label("total_scans"),
                    func.count().filter(ScanSession.status == ScanStatus.RUNNING).label("active_scans"),
                    func.count().filter(ScanSession.status == ScanStatus.COMPLETED).label("completed_scans"),
                    func.count().filter(ScanSession.status == ScanStatus.FAILED).label("failed_scans"),
                    func.max(ScanSession.start_time).label("last_scan_date")
                )
                .where(ScanSession.project_id == project_id)
            )
            scan_stats_result = await self.db.execute(scan_stats_query)
            scan_stats = scan_stats_result.first()
            
            # Get URL and form counts
            url_count = await self._get_project_url_count(project_id)
            form_count = await self._get_project_form_count(project_id)
            
            return ProjectSummary(
                total_scans=scan_stats.total_scans or 0,
                active_scans=scan_stats.active_scans or 0,
                completed_scans=scan_stats.completed_scans or 0,
                failed_scans=scan_stats.failed_scans or 0,
                total_urls_discovered=url_count,
                total_forms_found=form_count,
                last_scan_date=scan_stats.last_scan_date
            )
            
        except Exception as e:
            logger.error(f"Error getting project summary: {e}")
            raise
    
    async def get_scan_summary(self, scan_id: int, user_id: str) -> ScanSummary:
        """Get detailed summary for a specific scan."""
        try:
            # Verify scan access
            scan = await self._verify_scan_access(scan_id, user_id)
            
            # Get URL statistics
            url_stats_query = (
                select(
                    func.count(DiscoveredUrl.id).label("total_urls"),
                    func.count(func.distinct(DiscoveredUrl.status_code)).label("unique_status_codes"),
                    func.avg(DiscoveredUrl.response_time).label("avg_response_time")
                )
                .where(DiscoveredUrl.session_id == scan_id)
            )
            url_stats_result = await self.db.execute(url_stats_query)
            url_stats = url_stats_result.first()
            
            # Get form and technology counts
            form_count_query = (
                select(func.count(ExtractedForm.id))
                .join(DiscoveredUrl)
                .where(DiscoveredUrl.session_id == scan_id)
            )
            form_count_result = await self.db.execute(form_count_query)
            form_count = form_count_result.scalar() or 0
            
            tech_count_query = (
                select(func.count(TechnologyFingerprint.id))
                .join(DiscoveredUrl)
                .where(DiscoveredUrl.session_id == scan_id)
            )
            tech_count_result = await self.db.execute(tech_count_query)
            tech_count = tech_count_result.scalar() or 0
            
            # Calculate duration
            duration = None
            if scan.end_time and scan.start_time:
                duration = int((scan.end_time - scan.start_time).total_seconds())
            
            return ScanSummary(
                scan_id=scan_id,
                status=scan.status,
                start_time=scan.start_time,
                end_time=scan.end_time,
                duration_seconds=duration,
                urls_discovered=url_stats.total_urls or 0,
                forms_found=form_count,
                technologies_detected=tech_count,
                unique_status_codes=url_stats.unique_status_codes or 0,
                average_response_time=float(url_stats.avg_response_time or 0)
            )
            
        except Exception as e:
            logger.error(f"Error getting scan summary: {e}")
            raise
    
    # DashboardMetric functionality removed for SQLite compatibility
    # async def create_custom_metric(self, user_id: str, metric_data: DashboardMetricCreate) -> DashboardMetricResponse:
    # async def get_metrics_by_name(self, user_id: str, metric_name: str, hours_back: int = 24) -> List[DashboardMetricResponse]:
    
    async def get_technology_distribution(self, user_id: str, project_id: Optional[int] = None) -> Dict[str, int]:
        """Get distribution of detected technologies."""
        try:
            query = (
                select(TechnologyFingerprint)
                .join(DiscoveredUrl)
                .join(ScanSession)
                .join(Project)
                .where(Project.owner_id == user_id)
            )
            
            if project_id:
                query = query.where(Project.id == project_id)
            
            result = await self.db.execute(query)
            fingerprints = result.scalars().all()
            
            tech_distribution = {}
            
            for fp in fingerprints:
                # Count server software
                if fp.server_software:
                    tech_distribution[fp.server_software] = tech_distribution.get(fp.server_software, 0) + 1
                
                # Count programming languages
                if fp.programming_language:
                    tech_distribution[fp.programming_language] = tech_distribution.get(fp.programming_language, 0) + 1
                
                # Count frameworks
                if fp.framework:
                    tech_distribution[fp.framework] = tech_distribution.get(fp.framework, 0) + 1
                
                # Count CMS
                if fp.cms:
                    tech_distribution[fp.cms] = tech_distribution.get(fp.cms, 0) + 1
                
                # Count JavaScript libraries
                if fp.javascript_libraries:
                    for lib in fp.javascript_libraries:
                        tech_distribution[lib] = tech_distribution.get(lib, 0) + 1
            
            return tech_distribution
            
        except Exception as e:
            logger.error(f"Error getting technology distribution: {e}")
            raise
    
    async def get_status_code_distribution(self, user_id: str, project_id: Optional[int] = None) -> Dict[str, int]:
        """Get distribution of HTTP status codes."""
        try:
            query = (
                select(
                    DiscoveredUrl.status_code,
                    func.count(DiscoveredUrl.id).label("count")
                )
                .join(ScanSession)
                .join(Project)
                .where(
                    and_(
                        Project.owner_id == user_id,
                        DiscoveredUrl.status_code.isnot(None)
                    )
                )
                .group_by(DiscoveredUrl.status_code)
            )
            
            if project_id:
                query = query.where(Project.id == project_id)
            
            result = await self.db.execute(query)
            status_counts = result.all()
            
            return {str(status.status_code): status.count for status in status_counts}
            
        except Exception as e:
            logger.error(f"Error getting status code distribution: {e}")
            raise
    
    # Private helper methods
    
    async def _get_project_stats(self, user_id: str) -> Dict[str, int]:
        """Get project statistics for a user."""
        logger.info("Executing _get_project_stats")
        logger.info(f"User ID: {user_id}")
        try:
            # Use UUIDs directly for Supabase compatibility
            query = select(func.count(Project.id)).where(Project.owner_id == user_id)
            logger.info(f"Query: {query}")
            result = await self.db.execute(query)
            total = result.scalar() or 0
            logger.info(f"Total projects: {total}")
            return {"total": total}
        except Exception as e:
            logger.error(f"Error in _get_project_stats: {e}")
            raise
    
    async def _get_scan_stats(self, user_id: str) -> Dict[str, int]:
        """Get scan statistics for a user."""
        # Use UUIDs directly for Supabase compatibility
        query = (
            select(
                func.count(ScanSession.id).label("total"),
                func.count().filter(ScanSession.status == ScanStatus.RUNNING).label("active")
            )
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "total": stats.total or 0,
            "active": stats.active or 0
        }
    
    async def _get_discovery_stats(self, user_id: str) -> Dict[str, int]:
        """Get discovery statistics for a user."""
        # Use UUIDs directly for Supabase compatibility
        
        # URLs
        url_query = (
            select(func.count(DiscoveredUrl.id))
            .join(ScanSession)
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        url_result = await self.db.execute(url_query)
        urls = url_result.scalar() or 0
        
        # Forms
        form_query = (
            select(func.count(ExtractedForm.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(Project.owner_id == user_id_int)
        )
        form_result = await self.db.execute(form_query)
        forms = form_result.scalar() or 0
        
        # Technologies
        tech_query = (
            select(func.count(TechnologyFingerprint.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(Project.owner_id == user_id_int)
        )
        tech_result = await self.db.execute(tech_query)
        technologies = tech_result.scalar() or 0
        
        return {
            "urls": urls,
            "forms": forms,
            "technologies": technologies
        }
    
    async def _get_recent_activity(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity for a user."""
        # Use UUIDs directly for Supabase compatibility
        query = (
            select(ScanSession, Project.name.label("project_name"))
            .join(Project)
            .where(Project.owner_id == user_id)
            .order_by(desc(ScanSession.start_time))
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        scans = result.all()
        
        activity = []
        for scan, project_name in scans:
            activity.append({
                "type": "scan",
                "action": f"Scan {scan.status}",
                "project_name": project_name,
                "project_id": str(scan.project_id),
                "scan_id": str(scan.id),
                "timestamp": scan.start_time
            })
        
        return activity
    
    async def _verify_project_access(self, project_id: str, user_id: str) -> Project:
        """Verify user has access to a project."""
        # Use UUIDs directly for Supabase compatibility
        query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.owner_id == user_id
            )
        )
        result = await self.db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise ValueError("Project not found or access denied")
        
        return project
    
    async def _verify_scan_access(self, scan_id: str, user_id: str) -> ScanSession:
        """Verify user has access to a scan."""
        # Use UUIDs directly for Supabase compatibility
        query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id,
                    Project.owner_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        scan = result.scalar_one_or_none()
        
        if not scan:
            raise ValueError("Scan not found or access denied")
        
        return scan
    
    async def _get_project_url_count(self, project_id: str) -> int:
        """Get total URL count for a project."""
        query = (
            select(func.count(DiscoveredUrl.id))
            .join(ScanSession)
            .where(ScanSession.project_id == project_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_live_metrics(self, user_id: str, metric_type: str = "all") -> Dict[str, Any]:
        """Get live dashboard metrics with real-time data."""
        try:
            metrics = {}
            
            if metric_type in ["all", "scans"]:
                scan_metrics = await self._get_live_scan_metrics(user_id)
                metrics.update(scan_metrics)
            
            if metric_type in ["all", "urls"]:
                url_metrics = await self._get_live_url_metrics(user_id)
                metrics.update(url_metrics)
            
            if metric_type in ["all", "forms"]:
                form_metrics = await self._get_live_form_metrics(user_id)
                metrics.update(form_metrics)
            
            if metric_type in ["all", "performance"]:
                performance_metrics = await self._get_live_performance_metrics(user_id)
                metrics.update(performance_metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting live metrics: {e}")
            raise
    
    async def get_scan_statistics(self, user_id: str, time_delta: timedelta) -> Dict[str, Any]:
        """Get comprehensive scan statistics for a time period."""
        try:
            start_time = datetime.utcnow() - time_delta
            
            # Get scan counts and completion rate
            scan_query = (
                select(
                    func.count(ScanSession.id).label("total_scans"),
                    func.count().filter(ScanSession.status == ScanStatus.COMPLETED).label("completed_scans"),
                    func.count().filter(ScanSession.status == ScanStatus.FAILED).label("failed_scans"),
                    func.avg(
                        func.extract('epoch', ScanSession.end_time - ScanSession.start_time) / 60
                    ).label("avg_duration_minutes")
                )
                .join(Project)
                .where(
                    and_(
                        Project.owner_id == user_id,
                        ScanSession.created_at >= start_time
                    )
                )
            )
            
            scan_result = await self.db.execute(scan_query)
            scan_stats = scan_result.first()
            
            # Get URL and form statistics
            url_stats = await self._get_url_statistics(user_id, start_time)
            form_stats = await self._get_form_statistics(user_id, start_time)
            
            total_scans = scan_stats.total_scans or 0
            completed_scans = scan_stats.completed_scans or 0
            
            return {
                "total_scans": total_scans,
                "completed_scans": completed_scans,
                "failed_scans": scan_stats.failed_scans or 0,
                "completion_rate": (completed_scans / total_scans * 100) if total_scans > 0 else 0.0,
                "avg_duration_minutes": float(scan_stats.avg_duration_minutes or 0),
                "total_urls": url_stats["total"],
                "urls_per_scan": (url_stats["total"] / total_scans) if total_scans > 0 else 0.0,
                "total_forms": form_stats["total"],
                "forms_per_scan": (form_stats["total"] / total_scans) if total_scans > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting scan statistics: {e}")
            raise
    
    async def get_user_projects_summary(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get summary of user's projects with recent activity."""
        try:
            query = (
                select(
                    Project,
                    func.count(ScanSession.id).label("total_scans"),
                    func.max(ScanSession.start_time).label("last_scan_time")
                )
                .outerjoin(ScanSession)
                .where(Project.owner_id == user_id)
                .group_by(Project.id)
                .order_by(desc(Project.created_at))
                .limit(limit)
            )
            
            result = await self.db.execute(query)
            projects_data = result.all()
            
            projects_summary = []
            for project, total_scans, last_scan_time in projects_data:
                projects_summary.append({
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "target_domain": project.target_domain,
                    "total_scans": total_scans or 0,
                    "last_scan_time": last_scan_time,
                    "created_at": project.created_at
                })
            
            return projects_summary
            
        except Exception as e:
            logger.error(f"Error getting user projects summary: {e}")
            raise
    
    async def get_analytics_summary(self, user_id: str, time_delta: timedelta) -> Dict[str, Any]:
        """Get comprehensive analytics summary for dashboard."""
        try:
            start_time = datetime.utcnow() - time_delta
            
            # Get project analytics
            project_analytics = await self._get_project_analytics(user_id, start_time)
            
            # Get scan analytics
            scan_analytics = await self._get_scan_analytics(user_id, start_time)
            
            # Get discovery analytics
            discovery_analytics = await self._get_discovery_analytics(user_id, start_time)
            
            # Get performance analytics
            performance_analytics = await self._get_performance_analytics(user_id, start_time)
            
            return {
                "projects": project_analytics,
                "scans": scan_analytics,
                "discovery": discovery_analytics,
                "performance": performance_analytics,
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": datetime.utcnow().isoformat(),
                    "duration_hours": time_delta.total_seconds() / 3600
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            raise
    
    # Private helper methods for live metrics
    
    async def _get_live_scan_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get live scan metrics."""
        query = (
            select(
                func.count(ScanSession.id).label("total"),
                func.count().filter(ScanSession.status == ScanStatus.RUNNING).label("running"),
                func.count().filter(ScanSession.status == ScanStatus.PENDING).label("pending"),
                func.count().filter(ScanSession.status == ScanStatus.COMPLETED).label("completed"),
                func.count().filter(ScanSession.status == ScanStatus.FAILED).label("failed")
            )
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "scans_total": stats.total or 0,
            "scans_running": stats.running or 0,
            "scans_pending": stats.pending or 0,
            "scans_completed": stats.completed or 0,
            "scans_failed": stats.failed or 0
        }
    
    async def _get_live_url_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get live URL metrics."""
        query = (
            select(
                func.count(DiscoveredUrl.id).label("total"),
                func.count(func.distinct(DiscoveredUrl.url)).label("unique"),
                func.avg(DiscoveredUrl.response_time).label("avg_response_time")
            )
            .join(ScanSession)
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "urls_total": stats.total or 0,
            "urls_unique": stats.unique or 0,
            "avg_response_time": float(stats.avg_response_time or 0)
        }
    
    async def _get_live_form_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get live form metrics."""
        query = (
            select(
                func.count(ExtractedForm.id).label("total"),
                func.count().filter(ExtractedForm.authentication_required == True).label("auth_required")
            )
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "forms_total": stats.total or 0,
            "forms_auth_required": stats.auth_required or 0
        }
    
    async def _get_live_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get live performance metrics."""
        # Get recent scan performance (last 24 hours)
        recent_time = datetime.utcnow() - timedelta(hours=24)
        
        query = (
            select(
                func.count(ScanSession.id).label("recent_scans"),
                func.avg(
                    func.extract('epoch', ScanSession.end_time - ScanSession.start_time)
                ).label("avg_scan_duration"),
                func.avg(DiscoveredUrl.response_time).label("avg_response_time")
            )
            .join(Project)
            .outerjoin(DiscoveredUrl, ScanSession.id == DiscoveredUrl.session_id)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= recent_time
                )
            )
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "recent_scans_24h": stats.recent_scans or 0,
            "avg_scan_duration_seconds": float(stats.avg_scan_duration or 0),
            "avg_response_time_ms": float(stats.avg_response_time or 0)
        }
    
    async def _get_url_statistics(self, user_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get URL statistics for a time period."""
        query = (
            select(func.count(DiscoveredUrl.id))
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time
                )
            )
        )
        
        result = await self.db.execute(query)
        total = result.scalar() or 0
        
        return {"total": total}
    
    async def _get_form_statistics(self, user_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get form statistics for a time period."""
        query = (
            select(func.count(ExtractedForm.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time
                )
            )
        )
        
        result = await self.db.execute(query)
        total = result.scalar() or 0
        
        return {"total": total}
    
    async def _get_project_analytics(self, user_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get project analytics for a time period."""
        query = (
            select(
                func.count(Project.id).label("total"),
                func.count(func.distinct(Project.target_domain)).label("unique_domains")
            )
            .where(
                and_(
                    Project.owner_id == user_id,
                    Project.created_at >= start_time
                )
            )
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "total_projects": stats.total or 0,
            "unique_domains": stats.unique_domains or 0
        }
    
    async def _get_scan_analytics(self, user_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get scan analytics for a time period."""
        query = (
            select(
                func.count(ScanSession.id).label("total"),
                func.count().filter(ScanSession.status == ScanStatus.COMPLETED).label("completed"),
                func.count().filter(ScanSession.status == ScanStatus.FAILED).label("failed"),
                func.avg(
                    func.extract('epoch', ScanSession.end_time - ScanSession.start_time) / 60
                ).label("avg_duration_minutes")
            )
            .join(Project)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time
                )
            )
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        total = stats.total or 0
        completed = stats.completed or 0
        
        return {
            "total_scans": total,
            "completed_scans": completed,
            "failed_scans": stats.failed or 0,
            "success_rate": (completed / total * 100) if total > 0 else 0.0,
            "avg_duration_minutes": float(stats.avg_duration_minutes or 0)
        }
    
    async def _get_discovery_analytics(self, user_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get discovery analytics for a time period."""
        # URLs
        url_query = (
            select(
                func.count(DiscoveredUrl.id).label("total"),
                func.count(func.distinct(DiscoveredUrl.url)).label("unique"),
                func.avg(DiscoveredUrl.response_time).label("avg_response_time")
            )
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time
                )
            )
        )
        
        url_result = await self.db.execute(url_query)
        url_stats = url_result.first()
        
        # Forms
        form_query = (
            select(func.count(ExtractedForm.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time
                )
            )
        )
        
        form_result = await self.db.execute(form_query)
        form_count = form_result.scalar() or 0
        
        # Technologies
        tech_query = (
            select(func.count(TechnologyFingerprint.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .join(Project)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time
                )
            )
        )
        
        tech_result = await self.db.execute(tech_query)
        tech_count = tech_result.scalar() or 0
        
        return {
            "total_urls": url_stats.total or 0,
            "unique_urls": url_stats.unique or 0,
            "avg_response_time": float(url_stats.avg_response_time or 0),
            "total_forms": form_count,
            "total_technologies": tech_count
        }
    
    async def _get_performance_analytics(self, user_id: str, start_time: datetime) -> Dict[str, Any]:
        """Get performance analytics for a time period."""
        query = (
            select(
                func.avg(
                    func.extract('epoch', ScanSession.end_time - ScanSession.start_time)
                ).label("avg_scan_duration"),
                func.min(
                    func.extract('epoch', ScanSession.end_time - ScanSession.start_time)
                ).label("min_scan_duration"),
                func.max(
                    func.extract('epoch', ScanSession.end_time - ScanSession.start_time)
                ).label("max_scan_duration"),
                func.avg(DiscoveredUrl.response_time).label("avg_response_time")
            )
            .join(Project)
            .outerjoin(DiscoveredUrl, ScanSession.id == DiscoveredUrl.session_id)
            .where(
                and_(
                    Project.owner_id == user_id,
                    ScanSession.created_at >= start_time,
                    ScanSession.end_time.isnot(None)
                )
            )
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            "avg_scan_duration_seconds": float(stats.avg_scan_duration or 0),
            "min_scan_duration_seconds": float(stats.min_scan_duration or 0),
            "max_scan_duration_seconds": float(stats.max_scan_duration or 0),
            "avg_response_time_ms": float(stats.avg_response_time or 0)
        }
    
    async def _get_project_form_count(self, project_id: int) -> int:
        """Get total form count for a project."""
        query = (
            select(func.count(ExtractedForm.id))
            .join(DiscoveredUrl)
            .join(ScanSession)
            .where(ScanSession.project_id == project_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_recent_projects(self, user_id: str, limit: int = 5) -> List[ProjectSummary]:
        """Get recent projects for the user."""
        query = (
            select(Project)
            .where(Project.owner_id == user_id)
            .order_by(Project.updated_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        projects = result.scalars().all()
        
        project_summaries = []
        for project in projects:
            # Get basic stats for each project
            scan_count_query = select(func.count(ScanSession.id)).where(ScanSession.project_id == project.id)
            scan_count_result = await self.db.execute(scan_count_query)
            scan_count = scan_count_result.scalar() or 0
            
            url_count_query = (
                select(func.count(DiscoveredUrl.id))
                .join(ScanSession)
                .where(ScanSession.project_id == project.id)
            )
            url_count_result = await self.db.execute(url_count_query)
            url_count = url_count_result.scalar() or 0
            
            project_summaries.append(ProjectSummary(
                id=project.id,
                name=project.name,
                description=project.description or "",
                target_domain=project.target_domain,
                total_scans=scan_count,
                total_urls_discovered=url_count,
                total_forms_found=0,  # Simplified for now
                total_technologies_detected=0,  # Simplified for now
                last_scan_date=None,  # Simplified for now
                created_at=project.created_at,
                updated_at=project.updated_at
            ))
        
        return project_summaries
    
    async def _get_recent_scans(self, user_id: str, limit: int = 5) -> List[ScanSummary]:
        """Get recent scans for the user."""
        query = (
            select(ScanSession, Project.name.label("project_name"))
            .join(Project)
            .where(Project.owner_id == user_id)
            .order_by(ScanSession.start_time.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        scans = result.all()
        
        scan_summaries = []
        for scan, project_name in scans:
            # Get URL count for this scan
            url_count_query = select(func.count(DiscoveredUrl.id)).where(DiscoveredUrl.session_id == scan.id)
            url_count_result = await self.db.execute(url_count_query)
            url_count = url_count_result.scalar() or 0
            
            scan_summaries.append(ScanSummary(
                id=scan.id,
                project_id=scan.project_id,
                status=scan.status,
                start_time=scan.start_time,
                end_time=scan.end_time,
                urls_discovered=url_count,
                forms_extracted=0,  # Simplified for now
                technologies_detected=0  # Simplified for now
            ))
        
        return scan_summaries


