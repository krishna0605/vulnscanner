from fastapi import APIRouter
from sqlalchemy import text
from db.session import async_session
from core.config import settings
from tasks.celery_app import celery_app
import asyncio
from typing import Any

try:
    import redis.asyncio as aioredis  # redis>=5
except Exception:  # pragma: no cover
    aioredis = None

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health_v1():
    """Versioned health endpoint for frontend checks.

    Performs a lightweight DB connectivity check and returns a
    concise status payload expected by the frontend.
    """
    db_ok = False
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    # Result backend (Redis) quick ping
    redis_ok = False
    try:
        backend_url = settings.get_result_backend_url()
        if backend_url.startswith("redis://") and aioredis is not None:
            # Use short timeouts to avoid hanging
            r = aioredis.from_url(backend_url, socket_timeout=0.5, socket_connect_timeout=0.5)
            pong = await r.ping()
            await r.close()
            redis_ok = bool(pong)
        else:
            # Non-Redis backend; mark as True to avoid false negatives
            redis_ok = True
    except Exception:
        redis_ok = False

    # Celery worker quick ping (1s timeout)
    celery_ok = False
    try:
        # Run control.ping in a thread to avoid blocking event loop
        def _ping() -> Any:
            return celery_app.control.ping(timeout=1)

        replies = await asyncio.to_thread(_ping)
        celery_ok = bool(replies)
    except Exception:
        celery_ok = False

    return {
        "status": "healthy" if (db_ok and redis_ok) else "degraded",
        "database": db_ok,
        "redis": redis_ok,
        "celery": celery_ok,
    }