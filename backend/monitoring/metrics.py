"""
Prometheus metrics configuration for the Enhanced Vulnerability Scanner.

This module provides comprehensive metrics collection for monitoring
API performance, crawler statistics, and system health.
"""

import time
import functools
from typing import Dict, Optional, Callable
from prometheus_client import (
    Counter, Histogram, Gauge, Info, Enum,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from monitoring.logging_config import get_logger, LoggerMixin


# Create custom registry for better control
REGISTRY = CollectorRegistry()

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=REGISTRY
)

api_active_requests = Gauge(
    'api_active_requests',
    'Number of active API requests',
    registry=REGISTRY
)

# Authentication Metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['status', 'method'],
    registry=REGISTRY
)

auth_tokens_active = Gauge(
    'auth_tokens_active',
    'Number of active authentication tokens',
    registry=REGISTRY
)

# Crawler Metrics
crawler_scans_total = Counter(
    'crawler_scans_total',
    'Total number of crawler scans',
    ['status'],
    registry=REGISTRY
)

crawler_urls_discovered = Counter(
    'crawler_urls_discovered_total',
    'Total URLs discovered by crawler',
    ['scan_id', 'status_code'],
    registry=REGISTRY
)

crawler_active_scans = Gauge(
    'crawler_active_scans',
    'Number of currently active crawler scans',
    registry=REGISTRY
)

crawler_scan_duration = Histogram(
    'crawler_scan_duration_seconds',
    'Crawler scan duration in seconds',
    ['scan_type'],
    buckets=[60, 300, 600, 1800, 3600, 7200, 14400],  # 1min to 4hrs
    registry=REGISTRY
)

crawler_requests_per_second = Gauge(
    'crawler_requests_per_second',
    'Current crawler requests per second',
    ['scan_id'],
    registry=REGISTRY
)

# Database Metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    registry=REGISTRY
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
    registry=REGISTRY
)

db_queries_total = Counter(
    'db_queries_total',
    'Total number of database queries',
    ['operation', 'table', 'status'],
    registry=REGISTRY
)

# Celery/Task Queue Metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks',
    ['task_name', 'status'],
    registry=REGISTRY
)

celery_task_duration = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600],
    registry=REGISTRY
)

celery_queue_length = Gauge(
    'celery_queue_length',
    'Number of tasks in Celery queues',
    ['queue_name'],
    registry=REGISTRY
)

celery_workers_active = Gauge(
    'celery_workers_active',
    'Number of active Celery workers',
    registry=REGISTRY
)

# System Metrics
system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type'],  # total, available, used, cached
    registry=REGISTRY
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

system_disk_usage = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['type'],  # total, used, free
    registry=REGISTRY
)

# Application Metrics
app_info = Info(
    'app_info',
    'Application information',
    registry=REGISTRY
)

app_uptime = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds',
    registry=REGISTRY
)

app_health_status = Enum(
    'app_health_status',
    'Application health status',
    states=['healthy', 'degraded', 'unhealthy'],
    registry=REGISTRY
)

# Security Metrics
security_events_total = Counter(
    'security_events_total',
    'Total security events',
    ['event_type', 'severity'],
    registry=REGISTRY
)

rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'user_id'],
    registry=REGISTRY
)


class MetricsCollector(LoggerMixin):
    """
    Centralized metrics collector for the application.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self._setup_app_info()
    
    def _setup_app_info(self):
        """Set up application information metrics."""
        app_info.info({
            'version': '1.0.0',
            'environment': 'production',  # Should come from config
            'build_date': '2024-01-01',   # Should come from build process
            'git_commit': 'unknown'       # Should come from build process
        })
    
    def update_system_metrics(self):
        """Update system-level metrics."""
        try:
            import psutil
            
            # Memory metrics
            memory = psutil.virtual_memory()
            system_memory_usage.labels(type='total').set(memory.total)
            system_memory_usage.labels(type='available').set(memory.available)
            system_memory_usage.labels(type='used').set(memory.used)
            if hasattr(memory, 'cached'):
                system_memory_usage.labels(type='cached').set(memory.cached)
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Disk metrics
            import shutil
            total, used, free = shutil.disk_usage("/")
            system_disk_usage.labels(type='total').set(total)
            system_disk_usage.labels(type='used').set(used)
            system_disk_usage.labels(type='free').set(free)
            
            # Uptime
            uptime = time.time() - self.start_time
            app_uptime.set(uptime)
            
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")
    
    async def update_database_metrics(self):
        """Update database-related metrics."""
        try:
            # This would typically query database connection pool stats
            # For now, we'll simulate with placeholder values
            db_connections_active.set(5)  # Would get from connection pool
            
        except Exception as e:
            self.logger.error(f"Failed to update database metrics: {e}")
    
    async def update_celery_metrics(self):
        """Update Celery/task queue metrics."""
        try:
            from tasks.celery_app import celery_app
            import redis.asyncio as redis
            from core.config import get_settings
            
            # Get active workers
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                celery_workers_active.set(len(active_workers))
            else:
                celery_workers_active.set(0)
            
            # Get queue lengths
            settings = get_settings()
            redis_client = redis.from_url(settings.redis_url)
            
            for queue_name in ['celery', 'crawler', 'reports']:
                try:
                    length = await redis_client.llen(queue_name)
                    celery_queue_length.labels(queue_name=queue_name).set(length)
                except Exception:
                    pass
            
            await redis_client.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update Celery metrics: {e}")
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics."""
        api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        api_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_auth_attempt(self, status: str, method: str):
        """Record authentication attempt."""
        auth_attempts_total.labels(status=status, method=method).inc()
    
    def record_crawler_scan(self, status: str, duration: Optional[float] = None, scan_type: str = "standard"):
        """Record crawler scan metrics."""
        crawler_scans_total.labels(status=status).inc()
        
        if duration is not None:
            crawler_scan_duration.labels(scan_type=scan_type).observe(duration)
    
    def record_crawler_url(self, scan_id: str, status_code: int):
        """Record discovered URL."""
        crawler_urls_discovered.labels(
            scan_id=scan_id,
            status_code=str(status_code)
        ).inc()
    
    def record_db_query(self, operation: str, table: str, duration: float, status: str = "success"):
        """Record database query metrics."""
        db_queries_total.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
        
        db_query_duration.labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def record_celery_task(self, task_name: str, status: str, duration: Optional[float] = None):
        """Record Celery task metrics."""
        celery_tasks_total.labels(task_name=task_name, status=status).inc()
        
        if duration is not None:
            celery_task_duration.labels(task_name=task_name).observe(duration)
    
    def record_security_event(self, event_type: str, severity: str):
        """Record security event."""
        security_events_total.labels(event_type=event_type, severity=severity).inc()
    
    def record_rate_limit_hit(self, endpoint: str, user_id: str):
        """Record rate limit hit."""
        rate_limit_hits_total.labels(endpoint=endpoint, user_id=user_id).inc()
    
    def set_health_status(self, status: str):
        """Set application health status."""
        app_health_status.state(status)
    
    def increment_active_scans(self):
        """Increment active crawler scans."""
        crawler_active_scans.inc()
    
    def decrement_active_scans(self):
        """Decrement active crawler scans."""
        crawler_active_scans.dec()
    
    def set_crawler_rps(self, scan_id: str, rps: float):
        """Set crawler requests per second."""
        crawler_requests_per_second.labels(scan_id=scan_id).set(rps)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to collect API metrics.
    """
    
    def __init__(self, app, collector: Optional[MetricsCollector] = None):
        super().__init__(app)
        self.collector = collector or get_metrics_collector()
        self.logger = get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        
        # Increment active requests
        api_active_requests.inc()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract endpoint pattern (remove path parameters)
            endpoint = self._get_endpoint_pattern(request)
            
            # Record metrics
            self.collector.record_api_request(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception:
            # Record error metrics
            duration = time.time() - start_time
            endpoint = self._get_endpoint_pattern(request)
            
            self.collector.record_api_request(
                method=request.method,
                endpoint=endpoint,
                status_code=500,
                duration=duration
            )
            
            raise
        
        finally:
            # Decrement active requests
            api_active_requests.dec()
    
    def _get_endpoint_pattern(self, request: Request) -> str:
        """Extract endpoint pattern from request."""
        try:
            # Try to get the route pattern
            if hasattr(request, 'scope') and 'route' in request.scope:
                route = request.scope['route']
                if hasattr(route, 'path'):
                    return route.path
            
            # Fallback to path
            path = request.url.path
            
            # Remove common path parameters (UUIDs, IDs)
            import re
            path = re.sub(r'/[0-9a-f-]{36}', '/{id}', path)  # UUIDs
            path = re.sub(r'/\d+', '/{id}', path)  # Numeric IDs
            
            return path
            
        except Exception:
            return request.url.path


def metrics_endpoint() -> Response:
    """
    Endpoint to expose Prometheus metrics.
    """
    # Update system metrics before exposing
    collector = get_metrics_collector()
    collector.update_system_metrics()
    
    # Generate metrics output
    metrics_output = generate_latest(REGISTRY)
    
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )


# Decorator for timing functions
def timed_function(metric_name: str = None, labels: Dict[str, str] = None):
    """
    Decorator to time function execution and record metrics.
    
    Args:
        metric_name: Name of the metric (defaults to function name)
        labels: Additional labels for the metric
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            get_metrics_collector()
            
            try:
                result = await func(*args, **kwargs)
                time.time() - start_time
                
                # Record success metric
                if metric_name:
                    # Custom metric recording would go here
                    pass
                
                return result
                
            except Exception:
                time.time() - start_time
                
                # Record error metric
                if metric_name:
                    # Custom error metric recording would go here
                    pass
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            get_metrics_collector()
            
            try:
                result = func(*args, **kwargs)
                time.time() - start_time
                
                # Record success metric
                if metric_name:
                    # Custom metric recording would go here
                    pass
                
                return result
                
            except Exception:
                time.time() - start_time
                
                # Record error metric
                if metric_name:
                    # Custom error metric recording would go here
                    pass
                
                raise
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Test metrics collection
    collector = get_metrics_collector()
    
    # Simulate some metrics
    collector.record_api_request("GET", "/api/v1/health", 200, 0.05)
    collector.record_api_request("POST", "/api/v1/scans", 201, 0.15)
    collector.record_crawler_scan("completed", 300.0)
    collector.record_db_query("SELECT", "projects", 0.01)
    
    # Update system metrics
    collector.update_system_metrics()
    
    # Generate metrics output
    metrics_output = generate_latest(REGISTRY)
    print("Sample metrics output:")
    print(metrics_output.decode('utf-8')[:500] + "...")