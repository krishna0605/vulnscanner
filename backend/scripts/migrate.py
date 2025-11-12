#!/usr/bin/env python3
"""
Database Migration Management Script

This script provides utilities for managing database migrations,
schema versioning, and database operations for the Enhanced Vulnerability Scanner.

Usage:
    python scripts/migrate.py status          # Show current migration status
    python scripts/migrate.py upgrade         # Upgrade to latest migration
    python scripts/migrate.py downgrade       # Downgrade one migration
    python scripts/migrate.py history         # Show migration history
    python scripts/migrate.py create <name>   # Create new migration
    python scripts/migrate.py reset           # Reset database (dev only)
    python scripts/migrate.py seed            # Seed database with test data
"""

import asyncio
import sys
import sys
from pathlib import Path
import click
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import urlparse

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.config import settings  # noqa: E402

# Ensure a compatible event loop on Windows for psycopg async operations
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        # Fallback silently if policy is not available
        pass
from models.unified_models import Base  # noqa: E402


def get_database_url():
    """Get database URL from settings: prefer DATABASE_URL, then Supabase if not skipped, else SQLite."""
    # Prefer explicit local/remote PostgreSQL via DATABASE_URL
    db_url = getattr(settings, 'database_url', None)
    if db_url:
        pass
    elif not getattr(settings, 'skip_supabase', False) and getattr(settings, 'supabase_db_url', None):
        db_url = settings.supabase_db_url
    else:
        return "sqlite+aiosqlite:///./dev.db"
    
    # Ensure async driver for SQLite
    if db_url.startswith("sqlite+pysqlite://"):
        db_url = db_url.replace("sqlite+pysqlite://", "sqlite+aiosqlite://", 1)
    elif db_url.startswith("sqlite://") and "+aiosqlite" not in db_url:
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    
    # Prefer psycopg3 for async Postgres (better Windows compatibility)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    # Ensure TLS only for Supabase-hosted Postgres
    if db_url.startswith("postgresql+psycopg://") and "sslmode=" not in db_url:
        host = (urlparse(db_url.replace("+psycopg", "")).hostname or "")
        if ("supabase.co" in host) or ("pooler.supabase.com" in host):
            db_url += ("&sslmode=require" if "?" in db_url else "?sslmode=require")
    
    return db_url


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    alembic_cfg = Config(str(backend_path / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_path / "alembic"))
    # Escape '%' for ConfigParser interpolation safety
    db_url = get_database_url()
    safe_url = db_url.replace('%', '%%')
    alembic_cfg.set_main_option("sqlalchemy.url", safe_url)
    return alembic_cfg


@click.group()
def cli():
    """Database migration management commands."""


@cli.command()
def status():
    """Show current migration status."""
    click.echo("🔍 Checking migration status...")
    
    try:
        alembic_cfg = get_alembic_config()
        
        # Get current revision
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        
        script = ScriptDirectory.from_config(alembic_cfg)
        
        def get_current_revision(connection):
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
        
        # For async database
        async def check_status():
            engine = create_async_engine(get_database_url())
            async with engine.connect() as conn:
                current = await conn.run_sync(get_current_revision)
                await engine.dispose()
                return current
        
        current_rev = asyncio.run(check_status())
        head_rev = script.get_current_head()
        
        click.echo(f"📍 Current revision: {current_rev or 'None'}")
        click.echo(f"🎯 Head revision: {head_rev}")
        
        if current_rev == head_rev:
            click.echo("✅ Database is up to date!")
        elif current_rev is None:
            click.echo("⚠️  Database not initialized. Run 'upgrade' to initialize.")
        else:
            click.echo("⚠️  Database needs upgrade. Run 'upgrade' to update.")
            
    except Exception as e:
        click.echo(f"❌ Error checking status: {e}")
        sys.exit(1)


@cli.command()
@click.option('--revision', '-r', default='head', help='Target revision (default: head)')
def upgrade(revision: str):
    """Upgrade database to latest or specified revision."""
    click.echo(f"⬆️  Upgrading database to {revision}...")
    
    try:
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, revision)
        click.echo("✅ Database upgrade completed!")
        
    except Exception as e:
        click.echo(f"❌ Error during upgrade: {e}")
        sys.exit(1)


@cli.command()
@click.option('--revision', '-r', default='-1', help='Target revision (default: -1)')
def downgrade(revision: str):
    """Downgrade database to previous or specified revision."""
    if not settings.DEBUG:
        click.echo("❌ Downgrade only allowed in development mode!")
        sys.exit(1)
    
    click.echo(f"⬇️  Downgrading database to {revision}...")
    
    if not click.confirm("Are you sure you want to downgrade? This may cause data loss."):
        click.echo("❌ Downgrade cancelled.")
        return
    
    try:
        alembic_cfg = get_alembic_config()
        command.downgrade(alembic_cfg, revision)
        click.echo("✅ Database downgrade completed!")
        
    except Exception as e:
        click.echo(f"❌ Error during downgrade: {e}")
        sys.exit(1)


@cli.command()
def history():
    """Show migration history."""
    click.echo("📜 Migration history:")
    
    try:
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg, verbose=True)
        
    except Exception as e:
        click.echo(f"❌ Error showing history: {e}")
        sys.exit(1)


@cli.command()
@click.argument('message')
@click.option('--autogenerate', '-a', is_flag=True, help='Auto-generate migration from model changes')
def create(message: str, autogenerate: bool):
    """Create a new migration."""
    click.echo(f"📝 Creating new migration: {message}")
    
    try:
        alembic_cfg = get_alembic_config()
        
        if autogenerate:
            command.revision(alembic_cfg, message=message, autogenerate=True)
            click.echo("✅ Auto-generated migration created!")
        else:
            command.revision(alembic_cfg, message=message)
            click.echo("✅ Empty migration created!")
            
        click.echo("📝 Don't forget to review and edit the migration file before applying!")
        
    except Exception as e:
        click.echo(f"❌ Error creating migration: {e}")
        sys.exit(1)


@cli.command()
def reset():
    """Reset database (development only)."""
    if not settings.DEBUG:
        click.echo("❌ Database reset only allowed in development mode!")
        sys.exit(1)
    
    click.echo("🔄 Resetting database...")
    
    if not click.confirm("Are you sure? This will DELETE ALL DATA!"):
        click.echo("❌ Reset cancelled.")
        return
    
    try:
        async def reset_db():
            engine = create_async_engine(get_database_url())
            
            # Drop all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                
                # Drop alembic version table
                await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
                
            await engine.dispose()
        
        asyncio.run(reset_db())
        
        # Re-run migrations
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, "head")
        
        click.echo("✅ Database reset and re-initialized!")
        
    except Exception as e:
        click.echo(f"❌ Error during reset: {e}")
        sys.exit(1)


@cli.command()
def seed():
    """Seed database with test data."""
    click.echo("🌱 Seeding database with test data...")
    
    try:
        async def seed_data():
            from datetime import datetime, timezone
            import uuid
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from sqlalchemy.orm import sessionmaker
            
            engine = create_async_engine(get_database_url())
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                # Create test profile
                test_profile_id = str(uuid.uuid4())
                await session.execute(text("""
                    INSERT OR IGNORE INTO profiles (id, username, full_name, role, created_at, updated_at)
                    VALUES (:id, :username, :full_name, :role, :created_at, :updated_at)
                """), {
                    "id": test_profile_id,
                    "username": "testuser",
                    "full_name": "Test User",
                    "role": "user",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
                
                # Create test project
                test_project_id = str(uuid.uuid4())
                await session.execute(text("""
                    INSERT OR IGNORE INTO projects (id, name, description, owner_id, target_domain, scope_rules, created_at, updated_at)
                    VALUES (:id, :name, :description, :owner_id, :target_domain, :scope_rules, :created_at, :updated_at)
                """), {
                    "id": test_project_id,
                    "name": "Test Project",
                    "description": "A test project for development",
                    "owner_id": test_profile_id,
                    "target_domain": "example.com",
                    "scope_rules": "[]",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
                
                # Create test scan session
                test_scan_id = str(uuid.uuid4())
                await session.execute(text("""
                    INSERT OR IGNORE INTO scan_sessions (id, project_id, status, configuration, created_by, start_time)
                    VALUES (:id, :project_id, :status, :configuration, :created_by, :start_time)
                """), {
                    "id": test_scan_id,
                    "project_id": test_project_id,
                    "status": "completed",
                    "configuration": '{"max_depth": 3, "max_pages": 100}',
                    "created_by": test_profile_id,
                    "start_time": datetime.now(timezone.utc)
                })
                
                await session.commit()
                
            await engine.dispose()
            
            click.echo("✅ Test data seeded!")
            click.echo(f"   Profile ID: {test_profile_id}")
            click.echo(f"   Project ID: {test_project_id}")
            click.echo(f"   Scan ID: {test_scan_id}")
        
        asyncio.run(seed_data())
        
    except Exception as e:
        click.echo(f"❌ Error seeding data: {e}")
        sys.exit(1)


@cli.command()
def check():
    """Check database connectivity and schema integrity."""
    click.echo("🔍 Checking database connectivity and schema...")
    
    try:
        async def check_db():
            engine = create_async_engine(get_database_url())
            
            # Test connection
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
                
                # Check if all tables exist
                tables = ['profiles', 'projects', 'scan_sessions', 'discovered_urls', 
                         'extracted_forms', 'technology_fingerprints']
                
                for table in tables:
                    result = await conn.execute(text(f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='{table}'
                    """))
                    if not result.scalar():
                        click.echo(f"❌ Table '{table}' not found!")
                        return False
                
            await engine.dispose()
            return True
        
        if asyncio.run(check_db()):
            click.echo("✅ Database connectivity and schema check passed!")
        else:
            click.echo("❌ Database schema check failed!")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Database check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()