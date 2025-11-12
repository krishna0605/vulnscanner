import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import our models and configuration
from db.base import metadata as target_metadata  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

"""Target metadata is provided by db.base.metadata which imports all models."""

def get_database_url() -> str:
    """Resolve SQLAlchemy URL for Alembic from environment variables.

    - Prefer `DATABASE_URL_SYNC` (psycopg v3)
    - Fallback to `DATABASE_URL_ASYNC` and convert async drivers to sync
    - Fallback to local SQLite for dev if nothing is set
    """
    db_url = os.environ.get("DATABASE_URL_SYNC", "")
    if not db_url:
        db_url = os.environ.get("DATABASE_URL_ASYNC", "")
    if not db_url:
        # Final fallback for development
        return "sqlite+pysqlite:///./dev.db"

    # Normalize SQLite to sync driver for migrations
    if db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite+aiosqlite://", "sqlite+pysqlite://", 1)
    elif db_url.startswith("sqlite://") and "+pysqlite" not in db_url:
        db_url = db_url.replace("sqlite://", "sqlite+pysqlite://", 1)

    # Convert async Postgres driver to sync if needed
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Ensure TLS only for Supabase-hosted Postgres
    if db_url.startswith("postgresql+psycopg://") and "sslmode=" not in db_url:
        host = (urlparse(db_url.replace("+psycopg", "")).hostname or "")
        if ("supabase.co" in host) or ("pooler.supabase.com" in host):
            db_url += ("&sslmode=require" if "?" in db_url else "?sslmode=require")

    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """Exclude certain objects from autogeneration."""
    if type_ == "table" and name == "schema_versions":
        return False
    return True


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section, {})
    # Escape '%' for ConfigParser-style consumers (defensive)
    db_url = get_database_url()
    # If using a sync driver, but async engine here, switch to asyncpg
    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("sqlite+pysqlite://"):
        db_url = db_url.replace("sqlite+pysqlite://", "sqlite+aiosqlite://", 1)
    configuration["sqlalchemy.url"] = db_url.replace('%', '%%')
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using a synchronous SQLAlchemy Engine.

    This avoids requiring async drivers (e.g., asyncpg) when running Alembic
    and is more compatible on Windows/Python 3.14 environments.
    """
    url = get_database_url()
    # Ensure a sync driver is used
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite+aiosqlite://", "sqlite+pysqlite://", 1)

    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
# Ensure compatible event loop on Windows for psycopg async operations
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass
