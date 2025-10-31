"""
Crawler tasks for background scan execution.
Handles scan lifecycle, progress tracking, and result storage.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from celery import shared_task, current_task
from celery.exceptions import Retry

from backend.core.database import get_db
from backend.models.schemas import ScanConfiguration
from backend.crawler.engine import CrawlerEngine
from backend.services.scan_service import ScanService
from backend.services.storage_service import StorageService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def start_crawl_task(self, scan_id: int, config_dict: Dict[str, Any], project_id: int):
    """
    Background task to execute a web crawl.
    
    Args:
        scan_id: ID of the scan session
        config_dict: Scan configuration dictionary
        project_id: ID of the project
        
    Returns:
        Scan results summary
    """
    try:
        # Update scan status to running
        scan_service = ScanService()
        scan_service.update_scan_status(scan_id, "running", {
            "task_id": self.request.id,
            "started_at": datetime.utcnow().isoformat(),
            "worker_id": self.request.hostname
        })
        
        # Parse configuration
        config = ScanConfiguration(**config_dict)
        
        # Initialize crawler engine
        crawler = CrawlerEngine(config)
        
        # Set up progress callback
        def progress_callback(stats: Dict[str, Any]):
            """Update scan progress in database"""
            try:
                scan_service.update_scan_progress(scan_id, stats)
                
                # Update Celery task state
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": stats.get("urls_crawled", 0),
                        "total": stats.get("total_urls", 0),
                        "status": f"Crawled {stats.get('urls_crawled', 0)} URLs"
                    }
                )
            except Exception as e:
                logger.error(f"Error updating progress: {e}")
        
        # Execute crawl
        logger.info(f"Starting crawl for scan {scan_id}")
        results = asyncio.run(crawler.crawl(
            target_url=config.target_url,
            progress_callback=progress_callback
        ))
        
        # Store results in database
        scan_service.store_crawl_results(scan_id, results)
        
        # Update scan status to completed
        final_stats = {
            "completed_at": datetime.utcnow().isoformat(),
            "urls_crawled": len(results.get("discovered_urls", [])),
            "forms_found": len(results.get("extracted_forms", [])),
            "technologies_detected": len(results.get("technology_fingerprints", [])),
            "errors": results.get("errors", []),
            "duration_seconds": results.get("duration_seconds", 0)
        }
        
        scan_service.update_scan_status(scan_id, "completed", final_stats)
        
        logger.info(f"Crawl completed for scan {scan_id}")
        return {
            "scan_id": scan_id,
            "status": "completed",
            "stats": final_stats
        }
        
    except Exception as exc:
        logger.error(f"Crawl failed for scan {scan_id}: {exc}")
        
        # Update scan status to failed
        error_stats = {
            "failed_at": datetime.utcnow().isoformat(),
            "error": str(exc),
            "task_id": self.request.id
        }
        
        try:
            scan_service.update_scan_status(scan_id, "failed", error_stats)
        except Exception as db_error:
            logger.error(f"Failed to update scan status: {db_error}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying crawl for scan {scan_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        # Max retries exceeded
        raise exc


@shared_task(bind=True)
def stop_crawl_task(self, scan_id: int):
    """
    Stop a running crawl task.
    
    Args:
        scan_id: ID of the scan to stop
        
    Returns:
        Stop operation result
    """
    try:
        scan_service = ScanService()
        
        # Get scan details
        scan = scan_service.get_scan_by_id(scan_id)
        if not scan:
            return {"error": "Scan not found"}
        
        # Check if scan is running
        if scan.status != "running":
            return {"error": "Scan is not running"}
        
        # Get task ID from scan metadata
        task_id = scan.stats.get("task_id") if scan.stats else None
        if task_id:
            # Revoke the crawl task
            from tasks.celery_app import celery_app
            celery_app.control.revoke(task_id, terminate=True)
        
        # Update scan status
        stop_stats = {
            "stopped_at": datetime.utcnow().isoformat(),
            "stopped_by": "user_request",
            "task_id": task_id
        }
        
        scan_service.update_scan_status(scan_id, "cancelled", stop_stats)
        
        logger.info(f"Crawl stopped for scan {scan_id}")
        return {
            "scan_id": scan_id,
            "status": "cancelled",
            "message": "Scan stopped successfully"
        }
        
    except Exception as exc:
        logger.error(f"Error stopping crawl for scan {scan_id}: {exc}")
        return {"error": str(exc)}


@shared_task
def cleanup_expired_scans():
    """
    Periodic task to clean up expired or stale scans.
    
    Returns:
        Cleanup summary
    """
    try:
        scan_service = ScanService()
        
        # Find scans that have been running for more than 2 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=2)
        
        expired_scans = scan_service.get_expired_scans(cutoff_time)
        
        cleanup_count = 0
        for scan in expired_scans:
            try:
                # Stop the scan
                stop_stats = {
                    "stopped_at": datetime.utcnow().isoformat(),
                    "stopped_by": "cleanup_task",
                    "reason": "expired"
                }
                
                scan_service.update_scan_status(scan.id, "failed", stop_stats)
                cleanup_count += 1
                
                logger.info(f"Cleaned up expired scan {scan.id}")
                
            except Exception as e:
                logger.error(f"Error cleaning up scan {scan.id}: {e}")
        
        logger.info(f"Cleanup completed: {cleanup_count} scans processed")
        return {
            "cleaned_up": cleanup_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in cleanup task: {exc}")
        return {"error": str(exc)}


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
        from backend.crawler.normalizer import URLNormalizer
        from backend.crawler.spider import Spider
        from backend.models.schemas import ScanConfiguration
        
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
        config = ScanConfiguration(
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
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "redis": redis_status,
            "overall": "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
        }
        
        logger.info(f"Health check: {health_status}")
        return health_status
        
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall": "unhealthy",
            "error": str(exc)
        }