from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa
import asyncio
import sys

from core.config import settings

# Fix for Windows ProactorEventLoop issue with psycopg
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Base(DeclarativeBase):
  pass


def _normalize_db_url(url: str) -> str:
  if not url:
    # Dev fallback to SQLite when Postgres driver unavailable
    return "sqlite+aiosqlite:///./dev.db"
  normalized = url
  # Prefer psycopg3 for Supabase to avoid asyncpg build issues on Windows
  if normalized.startswith("postgres://"):
    normalized = normalized.replace("postgres://", "postgresql+psycopg://", 1)
  elif normalized.startswith("postgresql://") and "+psycopg" not in normalized:
    normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
  # Ensure TLS for Supabase
  if normalized.startswith("postgresql+psycopg://") and "sslmode=" not in normalized:
    normalized += ("&sslmode=require" if "?" in normalized else "?sslmode=require")
  return normalized


# Use SQLite for local development when SKIP_SUPABASE is true
if getattr(settings, 'skip_supabase', False):
    db_url = "sqlite+aiosqlite:///./dev.db"
else:
    db_url = _normalize_db_url(settings.supabase_db_url or settings.database_url)
engine = create_async_engine(db_url, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
  # Optional: create tables if allowed; Supabase may restrict DDL.
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)