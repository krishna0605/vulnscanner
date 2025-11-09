"""
Service health check utility for the backend infrastructure.

Checks:
- Database connectivity
- Redis availability
- Celery workers responsiveness

Outputs clear human-readable statuses for quick diagnostics.
"""
from __future__ import annotations

import sys
import time
import contextlib
from typing import Dict

from sqlalchemy import create_engine, text

from core.config import Settings, SettingsConfigDict, Settings as _SettingsCls  # type: ignore
from core.config import settings  # runtime settings instance


def _normalize_sync_db_url(url: str) -> str:
    """Normalize async DB URLs to sync driver for quick connectivity checks."""
    if not url:
        return url
    # Common async → sync conversions
    url = url.replace("postgresql+asyncpg", "postgresql")
    url = url.replace("sqlite+aiosqlite", "sqlite")
    # Supabase may use postgres:// shorthand
    url = url.replace("postgres://", "postgresql://")
    return url


def check_database(database_url: str, timeout: float = 3.0) -> str:
    """Attempt a simple DB connection and SELECT 1.

    Returns: "Connected" or "Failed" with reason.
    """
    url = _normalize_sync_db_url(database_url)
    if not url:
        return "Skipped (no database_url configured)"
    try:
        engine = create_engine(url, pool_pre_ping=True, pool_recycle=180)
        with engine.connect() as conn:
            # Apply a short statement timeout if supported
            with contextlib.suppress(Exception):
                conn.execution_options(timeout=timeout)
            conn.execute(text("SELECT 1"))
        return "Connected"
    except Exception as e:
        return f"Failed ({e.__class__.__name__}: {e})"


def check_redis(redis_url: str, timeout: float = 1.0) -> str:
    """Send PING to Redis using redis-py if available.

    Returns: "Connected" or "Failed".
    """
    if not redis_url:
        return "Skipped (no redis_url configured)"
    try:
        import redis  # type: ignore
        client = redis.Redis.from_url(redis_url, socket_timeout=timeout)
        pong = client.ping()
        return "Connected" if pong else "Failed (no PONG)"
    except Exception as e:
        return f"Failed ({e.__class__.__name__}: {e})"


def check_celery(timeout: float = 2.0) -> str:
    """Ping Celery workers via control.inspect().

    Returns: "Connected" if any worker responds; "Failed" otherwise.
    """
    try:
        from tasks.celery_app import celery_app
        insp = celery_app.control.inspect(timeout=timeout)
        res = insp.ping()  # dict or None
        if isinstance(res, dict) and len(res) > 0:
            return f"Connected ({len(res)} worker(s) responding)"
        return "Failed (no workers responded)"
    except Exception as e:
        return f"Failed ({e.__class__.__name__}: {e})"


def run_checks(cfg: _SettingsCls) -> Dict[str, str]:
    """Run all service checks and return a status map."""
    return {
        "Database": check_database(
            cfg.database_url or cfg.database_url_sync or cfg.supabase_db_url
        ),
        "Redis": check_redis(cfg.redis_url),
        "Celery": check_celery(),
    }


def main() -> int:
    statuses = run_checks(settings)
    print("Infrastructure Health Status:\n")
    for name, status in statuses.items():
        print(f"- {name}: {status}")

    # Exit non-zero if any critical service failed (excluding skipped)
    failed = [s for s in statuses.values() if s.startswith("Failed")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())