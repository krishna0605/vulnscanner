"""
Health check and monitoring endpoints for the Enhanced Vulnerability Scanner.

This module provides comprehensive health checks for all system components
including database, Redis, Celery workers, and external dependencies.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import aiohttp
import redis.asyncio as redis
from pydantic import BaseModel

from core.config import get_settings
from core.supabase import get_supabase_client
from monitoring.logging_config import LoggerMixin


class HealthStatus(str, Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status for a single component."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    last_checked: datetime


class SystemHealth(BaseModel):
    """Overall system health status."""
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: float
    components: List[ComponentHealth]
    summary: Dict[str, int]


class HealthChecker(LoggerMixin):
    """
    Comprehensive health checker for all system components.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.start_time = time.time()
        self._redis_client: Optional[redis.Redis] = None
    
    async def get_redis_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis_client
    
    async def check_database(self) -> ComponentHealth:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            supabase = get_supabase_client()
            
            # Test basic connectivity
            response = supabase.table('profiles').select('id').limit(1).execute()
            
            response_time = (time.time() - start_time) * 1000
            
            # Check if response is valid
            if hasattr(response, 'data'):
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                    response_time_ms=response_time,
                    details={
                        "provider": "supabase",
                        "connection_pool": "active"
                    },
                    last_checked=datetime.utcnow()
                )
            else:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.DEGRADED,
                    message="Database responded but with unexpected format",
                    response_time_ms=response_time,
                    last_checked=datetime.utcnow()
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Database health check failed: {e}")
            
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_redis(self) -> ComponentHealth:
        """Check Redis connectivity and performance."""
        start_time = time.time()
        
        try:
            redis_client = await self.get_redis_client()
            
            # Test basic connectivity with ping
            await redis_client.ping()
            
            # Test read/write operations
            test_key = "health_check_test"
            test_value = str(int(time.time()))
            
            await redis_client.set(test_key, test_value, ex=60)
            retrieved_value = await redis_client.get(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if retrieved_value == test_value:
                # Get Redis info
                info = await redis_client.info()
                
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message="Redis connection and operations successful",
                    response_time_ms=response_time,
                    details={
                        "version": info.get("redis_version"),
                        "connected_clients": info.get("connected_clients"),
                        "used_memory_human": info.get("used_memory_human"),
                        "uptime_in_seconds": info.get("uptime_in_seconds")
                    },
                    last_checked=datetime.utcnow()
                )
            else:
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.DEGRADED,
                    message="Redis read/write test failed",
                    response_time_ms=response_time,
                    last_checked=datetime.utcnow()
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Redis health check failed: {e}")
            
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=response_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_celery(self) -> ComponentHealth:
        """Check Celery worker status and queue health."""
        start_time = time.time()
        
        try:
            from tasks.celery_app import celery_app
            
            # Check active workers
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            
            response_time = (time.time() - start_time) * 1000
            
            if active_workers:
                worker_count = len(active_workers)
                
                # Get queue lengths
                redis_client = await self.get_redis_client()
                queue_lengths = {}
                
                for queue in ['celery', 'crawler', 'reports']:
                    try:
                        length = await redis_client.llen(queue)
                        queue_lengths[queue] = length
                    except Exception:
                        queue_lengths[queue] = "unknown"
                
                return ComponentHealth(
                    name="celery",
                    status=HealthStatus.HEALTHY,
                    message=f"Celery workers active: {worker_count}",
                    response_time_ms=response_time,
                    details={
                        "active_workers": worker_count,
                        "worker_names": list(active_workers.keys()),
                        "queue_lengths": queue_lengths
                    },
                    last_checked=datetime.utcnow()
                )
            else:
                return ComponentHealth(
                    name="celery",
                    status=HealthStatus.UNHEALTHY,
                    message="No active Celery workers found",
                    response_time_ms=response_time,
                    last_checked=datetime.utcnow()
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Celery health check failed: {e}")
            
            return ComponentHealth(
                name="celery",
                status=HealthStatus.UNHEALTHY,
                message=f"Celery check failed: {str(e)}",
                response_time_ms=response_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_external_services(self) -> ComponentHealth:
        """Check external service dependencies."""
        start_time = time.time()
        
        try:
            # Test external HTTP connectivity
            timeout = aiohttp.ClientTimeout(total=5.0)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Test DNS resolution and basic HTTP connectivity
                async with session.get('https://httpbin.org/status/200') as response:
                    if response.status == 200:
                        response_time = (time.time() - start_time) * 1000
                        
                        return ComponentHealth(
                            name="external_services",
                            status=HealthStatus.HEALTHY,
                            message="External connectivity verified",
                            response_time_ms=response_time,
                            details={
                                "dns_resolution": "working",
                                "http_connectivity": "working"
                            },
                            last_checked=datetime.utcnow()
                        )
                    else:
                        response_time = (time.time() - start_time) * 1000
                        return ComponentHealth(
                            name="external_services",
                            status=HealthStatus.DEGRADED,
                            message=f"External service returned status {response.status}",
                            response_time_ms=response_time,
                            last_checked=datetime.utcnow()
                        )
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.warning(f"External services health check failed: {e}")
            
            return ComponentHealth(
                name="external_services",
                status=HealthStatus.DEGRADED,
                message=f"External connectivity issues: {str(e)}",
                response_time_ms=response_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_disk_space(self) -> ComponentHealth:
        """Check available disk space."""
        start_time = time.time()
        
        try:
            import shutil
            
            # Check disk space for logs and temp directories
            total, used, free = shutil.disk_usage("/")
            
            free_percent = (free / total) * 100
            response_time = (time.time() - start_time) * 1000
            
            if free_percent > 20:
                status = HealthStatus.HEALTHY
                message = f"Disk space healthy: {free_percent:.1f}% free"
            elif free_percent > 10:
                status = HealthStatus.DEGRADED
                message = f"Disk space low: {free_percent:.1f}% free"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Disk space critical: {free_percent:.1f}% free"
            
            return ComponentHealth(
                name="disk_space",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "total_gb": round(total / (1024**3), 2),
                    "used_gb": round(used / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "free_percent": round(free_percent, 1)
                },
                last_checked=datetime.utcnow()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Disk space check failed: {e}")
            
            return ComponentHealth(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space check failed: {str(e)}",
                response_time_ms=response_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_memory_usage(self) -> ComponentHealth:
        """Check system memory usage."""
        start_time = time.time()
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            response_time = (time.time() - start_time) * 1000
            
            if memory.percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"
            elif memory.percent < 90:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {memory.percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {memory.percent:.1f}%"
            
            return ComponentHealth(
                name="memory",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": round(memory.percent, 1),
                    "cached_gb": round(memory.cached / (1024**3), 2) if hasattr(memory, 'cached') else None
                },
                last_checked=datetime.utcnow()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Memory check failed: {e}")
            
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                response_time_ms=response_time,
                last_checked=datetime.utcnow()
            )
    
    async def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status."""
        self.logger.info("Starting system health check")
        
        # Run all health checks concurrently
        health_checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_celery(),
            self.check_external_services(),
            self.check_disk_space(),
            self.check_memory_usage(),
            return_exceptions=True
        )
        
        # Filter out exceptions and create component list
        components = []
        for check in health_checks:
            if isinstance(check, ComponentHealth):
                components.append(check)
            else:
                # Handle exceptions in health checks
                self.logger.error(f"Health check exception: {check}")
                components.append(ComponentHealth(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(check)}",
                    last_checked=datetime.utcnow()
                ))
        
        # Determine overall system status
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0
        }
        
        for component in components:
            status_counts[component.status] += 1
        
        # Overall status logic
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        uptime = time.time() - self.start_time
        
        system_health = SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            uptime_seconds=uptime,
            components=components,
            summary={
                "healthy": status_counts[HealthStatus.HEALTHY],
                "degraded": status_counts[HealthStatus.DEGRADED],
                "unhealthy": status_counts[HealthStatus.UNHEALTHY],
                "total": len(components)
            }
        )
        
        self.logger.info(
            f"System health check completed: {overall_status}",
            extra={
                "overall_status": overall_status,
                "component_count": len(components),
                "uptime_seconds": uptime
            }
        )
        
        return system_health
    
    async def cleanup(self):
        """Clean up resources."""
        if self._redis_client:
            await self._redis_client.close()


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# FastAPI dependency
async def health_check_dependency() -> SystemHealth:
    """FastAPI dependency for health checks."""
    checker = get_health_checker()
    return await checker.get_system_health()


# Example usage and testing
if __name__ == "__main__":
    async def test_health_checks():
        """Test health check functionality."""
        checker = HealthChecker()
        
        print("Running individual health checks...")
        
        # Test individual components
        db_health = await checker.check_database()
        print(f"Database: {db_health.status} - {db_health.message}")
        
        redis_health = await checker.check_redis()
        print(f"Redis: {redis_health.status} - {redis_health.message}")
        
        # Test overall system health
        print("\nRunning comprehensive health check...")
        system_health = await checker.get_system_health()
        
        print(f"Overall Status: {system_health.status}")
        print(f"Uptime: {system_health.uptime_seconds:.2f} seconds")
        print(f"Components: {system_health.summary}")
        
        for component in system_health.components:
            print(f"  {component.name}: {component.status} ({component.response_time_ms:.2f}ms)")
        
        await checker.cleanup()
    
    # Run test
    asyncio.run(test_health_checks())