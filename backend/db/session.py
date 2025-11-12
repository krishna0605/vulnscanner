from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from urllib.parse import urlparse

from backend.core.config import settings

# Note: Removed deprecated asyncio event loop policy code for Python 3.14+ compatibility
# Modern psycopg3 handles Windows event loops properly without manual intervention

# Use a separate metadata instance for testing
metadata = MetaData()

class Base(DeclarativeBase):
    metadata = metadata

# Database engine and session setup
def get_engine():
    return create_async_engine(settings.DATABASE_URL, echo=False, future=True)

def get_session():
    return async_sessionmaker(bind=get_engine(), expire_on_commit=False)


def _is_supabase_url(url: str) -> bool:
    """Detect if the DB URL points to Supabase-hosted Postgres."""
    try:
        parsed = urlparse(url.replace("+psycopg", ""))
        host = parsed.hostname or ""
        return ("supabase.co" in host) or ("pooler.supabase.com" in host)
    except Exception:
        # Fallback heuristic
        return "supabase" in url


def _normalize_db_url(url: str) -> str:
    if not url:
        # Dev fallback to SQLite when Postgres driver unavailable
        return "sqlite+aiosqlite:///./dev.db"
    normalized = url
    # Ensure async driver for SQLite in development
    if normalized.startswith("sqlite+pysqlite://"):
        normalized = normalized.replace("sqlite+pysqlite://", "sqlite+aiosqlite://", 1)
    elif normalized.startswith("sqlite://") and "+aiosqlite" not in normalized:
        normalized = normalized.replace("sqlite://", "sqlite+aiosqlite://", 1)
    # Prefer asyncpg for async runtime engine
    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql+asyncpg://", 1)
    elif normalized.startswith("postgresql://") and "+asyncpg" not in normalized and "+psycopg" not in normalized:
        normalized = normalized.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Ensure TLS only for Supabase-hosted Postgres
    if normalized.startswith("postgresql+asyncpg://") and "sslmode=" not in normalized and _is_supabase_url(normalized):
        normalized += ("&sslmode=require" if "?" in normalized else "?sslmode=require")
    return normalized


"""
Runtime engine selection:
- Prefer Settings.database_url_async
- Fallback to legacy database_url
- Fallback to Supabase URL if not skipped
- Otherwise, local SQLite dev.db
"""
candidate_db = settings.get_runtime_db_url()
if candidate_db:
    db_url = _normalize_db_url(candidate_db)
elif not getattr(settings, 'skip_supabase', False) and getattr(settings, 'supabase_db_url', None):
    db_url = _normalize_db_url(settings.supabase_db_url)
else:
    db_url = "sqlite+aiosqlite:///./dev.db"

engine = create_async_engine(
    db_url,
    echo=getattr(settings, 'db_echo', False),
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """Dependency to get database session (backward compatible)."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_async_session() -> AsyncSession:
    """Preferred FastAPI dependency to get AsyncSession."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Database schema management is handled exclusively by Alembic migrations.