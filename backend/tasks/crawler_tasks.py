"""
Crawler tasks for background scan execution.
Handles scan lifecycle, progress tracking, and result storage.
"""

import asyncio
from threading import Thread
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from celery import shared_task

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.dashboard import ScanConfigurationSchema
from ..crawler.engine import CrawlerEngine
from ..services.scan_service import ScanService
from ..db.session import async_session
from ..models.unified_models import Project

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_jitter=True,
    queue="crawler",
)
def start_crawl_task(self, project_id: str, url: str, **options):
    """
    Background task to execute a web crawl.

    Args:
        project_id: ID of the project (UUID string)
        url: Target URL to crawl
        **options: Optional parameters such as scan_id and config

    Returns:
        Small payload indicating enqueue status
    """

    # Extract optional inputs
    scan_id: str | None = options.get("scan_id")
    config_dict: Dict[str, Any] | None = options.get("config")

    async def _run() -> Dict[str, Any]:
        async with async_session() as session:  # type: AsyncSession
            scan_service = ScanService()

            # Resolve configuration
            cfg = config_dict or {}
            config = ScanConfigurationSchema(**cfg)

            # Resolve target URL: prefer provided url; fallback to project target_domain
            target_url = url
            if not target_url:
                proj = await session.execute(select(Project).where(Project.id == project_id))
                project = proj.scalar_one_or_none()
                if not project:
                    raise ValueError(f"Project not found: {project_id}")
                target_url = project.target_domain or ""

            if not target_url:
                raise ValueError("Target URL is empty")
            if not (target_url.startswith("http://") or target_url.startswith("https://")):
                target_url = f"https://{target_url}"

            # Update scan status early if available
            if scan_id:
                await scan_service.update_scan_status(session, scan_id, "running")

            # Initialize and start crawler
            crawler = CrawlerEngine(config=config, session_id=scan_id, db_session=session)
            logger.info(
                f"Starting crawl for scan {scan_id or 'N/A'} on target {target_url}"
            )

            try:
                await crawler.start_crawl(target_url)
            finally:
                # Ensure the crawler session is closed
                await crawler.close()

            # Ensure final status if scan session exists
            if scan_id:
                await scan_service.update_scan_status(session, scan_id, "completed")

            return {
                "task_id": getattr(self.request, "id", None),
                "status": "enqueued",
            }

    def _run_in_thread(coro: asyncio.coroutines.Coroutine) -> Dict[str, Any]:
        """Run an async coroutine in an isolated event loop on a dedicated thread.
    
        This avoids interfering with Celery's worker process/thread and works with
        the default prefork worker. Any exception raised in the coroutine is
        propagated back to the caller.
        """
        result_container: Dict[str, Any] = {}
        error_container: Dict[str, Exception] = {}
    
        def _target():
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(coro)
                result_container.update(result or {})
            except Exception as e:  # noqa: BLE001
                error_container["error"] = e
            finally:
                try:
                    loop.stop()
                except Exception as stop_error:
                    logger.error(f"Error stopping event loop: {stop_error}")
                try:
                    loop.close()
                except Exception as close_error:
                    logger.error(f"Error closing event loop: {close_error}")
    
        t = Thread(target=_target, daemon=True)
        t.start()
        t.join()
    
        if "error" in error_container:
            raise error_container["error"]
        return result_container

    try:
        # Execute the crawl in a fresh event loop on a separate thread.
        return _run_in_thread(_run())
    except Exception as exc:
        logger.error(
            f"Crawl task error for project {project_id} (scan {scan_id or 'N/A'}): {exc}"
        )

        async def _mark_failed():
            if scan_id:
                async with async_session() as session:
                    scan_service = ScanService()
                    await scan_service.update_scan_status(session, scan_id, "failed")

        try:
            # Also run failure marking in an isolated loop/thread to avoid loop conflicts
            _run_in_thread(_mark_failed())
        except Exception as e:
            logger.error(f"Failed to mark scan {scan_id or 'N/A'} as failed: {e}")

        # Determine if error is transient; retry with backoff if allowed
        transient = False
        try:
            import aiohttp, asyncio  # noqa: F401
            if isinstance(exc, (asyncio.TimeoutError,)):
                transient = True
            # Defer import-based type checks safely
            try:
                if isinstance(exc, aiohttp.ClientError):
                    transient = True
            except Exception:
                pass
        except Exception:
            pass

        # Apply retry policy only for transient failures
        if transient and getattr(self, "request", None) and self.request.retries < 3:
            raise self.retry(exc=exc, countdown=min(60, 2 ** self.request.retries * 5))

        # Exhausted retries or permanent error: surface failure
        raise


@shared_task(bind=True, max_retries=5)
def start_crawl_task(self, project_id: str, url: str, scan_id: str, config: dict):
    """Deprecated duplicate definition removed. Use the async-enabled implementation above."""
    # This function intentionally left as a lightweight guard in case of stale imports.
    # Route all calls to the primary implementation for consistency.
    return start_crawl_task.s(project_id=project_id, url=url, scan_id=scan_id, config=config)()

@shared_task(bind=True, max_retries=3)
def stop_crawl_task(self, scan_id: str):
    """Background task to stop a running crawl"""
    try:
        # Retrieve scan stats
        stats = get_scan_stats(scan_id)
        if not stats or "task_id" not in stats:
            raise ValueError(f"No task ID found for scan {scan_id}")

        # Stop the task
        revoke_task(stats["task_id"], terminate=True)
        update_scan_status(scan_id, "cancelled")
    except Exception as exc:
        logger.error(
            "Failed to stop crawl for scan %s: %s", scan_id, str(exc), exc_info=True
        )
        raise self.retry(exc=exc, countdown=30)

@shared_task(bind=True, max_retries=3)
def cleanup_expired_scans(self):
    """Background task to clean up expired scans"""
    try:
        expired_scans = get_expired_scans()
        for scan in expired_scans:
            try:
                delete_scan(scan["id"])
            except Exception as exc:
                logger.warning(
                    "Failed to delete expired scan %s: %s", scan["id"], str(exc)
                )
    except Exception as exc:
        logger.error(
            "Cleanup task failed: %s", str(exc), exc_info=True
        )
        raise self.retry(exc=exc, countdown=60)


@shared_task
def validate_target_url(url: str, project_id: int):
    """
    Validate a target URL before starting a scan.
    
    Args:
        url: Target URL to validate
        project_id: Project ID for context
        
    Returns:
        Validation result
    """
    try:
        from crawler.normalizer import URLNormalizer
        from crawler.spider import Spider
        from schemas.dashboard import ScanConfigurationSchema
        
        normalizer = URLNormalizer()
        
        # Basic URL validation
        if not normalizer.is_valid_url(url):
            return {
                "valid": False,
                "error": "Invalid URL format"
            }
        
        # Normalize URL
        normalized_url = normalizer.normalize_url(url)
        
        # Test connectivity
        config = ScanConfigurationSchema(
            target_url=normalized_url,
            max_depth=1,
            max_pages=1,
            timeout=10
        )
        
        async def test_connectivity():
            spider = Spider(config)
            try:
                response = await spider.fetch_url(normalized_url)
                return {
                    "valid": True,
                    "status_code": response.status,
                    "normalized_url": normalized_url,
                    "server": response.headers.get("Server", "Unknown")
                }
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Connection failed: {str(e)}"
                }
            finally:
                await spider.close()
        
        result = asyncio.run(test_connectivity())
        
        logger.info(f"URL validation for {url}: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error validating URL {url}: {exc}")
        return {
            "valid": False,
            "error": str(exc)
        }


@shared_task
def generate_scan_summary(scan_id: int):
    """
    Generate a summary of scan results.
    
    Args:
        scan_id: ID of the scan
        
    Returns:
        Scan summary
    """
    try:
        scan_service = ScanService()
        
        # Get scan details
        scan = scan_service.get_scan_by_id(scan_id)
        if not scan:
            return {"error": "Scan not found"}
        
        # Get scan results
        urls = scan_service.get_scan_urls(scan_id)
        forms = scan_service.get_scan_forms(scan_id)
        technologies = scan_service.get_scan_technologies(scan_id)
        
        # Generate summary
        summary = {
            "scan_id": scan_id,
            "status": scan.status,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "completed_at": scan.stats.get("completed_at") if scan.stats else None,
            "duration": scan.stats.get("duration_seconds") if scan.stats else None,
            "statistics": {
                "total_urls": len(urls),
                "total_forms": len(forms),
                "total_technologies": len(technologies),
                "status_codes": {},
                "content_types": {},
                "domains": set()
            },
            "top_technologies": [],
            "security_score": 0
        }
        
        # Analyze URLs
        for url in urls:
            # Status codes
            status = url.status_code
            if status:
                summary["statistics"]["status_codes"][status] = \
                    summary["statistics"]["status_codes"].get(status, 0) + 1
            
            # Content types
            content_type = url.content_type
            if content_type:
                summary["statistics"]["content_types"][content_type] = \
                    summary["statistics"]["content_types"].get(content_type, 0) + 1
            
            # Domains
            from urllib.parse import urlparse
            domain = urlparse(url.url).netloc
            summary["statistics"]["domains"].add(domain)
        
        # Convert domains set to count
        summary["statistics"]["domains"] = len(summary["statistics"]["domains"])
        
        # Analyze technologies
        tech_counts = {}
        security_headers_count = 0
        
        for tech in technologies:
            if tech.server_software:
                tech_counts[tech.server_software] = tech_counts.get(tech.server_software, 0) + 1
            
            # Count security headers
            if tech.security_headers:
                security_headers_count += len(tech.security_headers)
        
        # Top technologies
        summary["top_technologies"] = [
            {"name": tech, "count": count}
            for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Simple security score based on security headers
        max_security_headers = 10  # Expected number of security headers
        summary["security_score"] = min(100, (security_headers_count / max_security_headers) * 100)
        
        logger.info(f"Generated summary for scan {scan_id}")
        return summary
        
    except Exception as exc:
        logger.error(f"Error generating summary for scan {scan_id}: {exc}")
        return {"error": str(exc)}


@shared_task
def health_check():
    """
    Health check task for monitoring system status.
    
    Returns:
        Health status
    """
    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            # Simple database query
            scan_service = ScanService()
            scan_service.get_recent_scans(limit=1)
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check Redis connectivity
        redis_status = "healthy"
        try:
            from tasks.celery_app import celery_app
            celery_app.backend.get("health_check_key")
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
        
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": db_status,
            "redis": redis_status,
            "overall": "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
        }
        
        logger.info(f"Health check: {health_status}")
        return health_status
        
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall": "unhealthy",
            "error": str(exc)
        }