"""
Database initialization module for Enhanced Vulnerability Scanner.
Supports both SQLite (development) and PostgreSQL (production).
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.unified_models import Base  # noqa: E402
from core.config import settings  # noqa: E402


def _normalize_db_url(url: str) -> str:
    """Normalize database URL for async drivers."""
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


async def create_database_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """Create async database engine."""
    if not database_url:
        # Use SQLite for local development when SKIP_SUPABASE is true
        if getattr(settings, 'skip_supabase', False):
            database_url = "sqlite+aiosqlite:///./dev.db"
        else:
            database_url = _normalize_db_url(getattr(settings, 'supabase_db_url', None) or settings.database_url)
    
    # Create engine with appropriate settings
    if "sqlite" in database_url:
        engine = create_async_engine(
            database_url,
            echo=True,
            future=True,
            # SQLite specific settings
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL settings
        engine = create_async_engine(
            database_url,
            echo=True,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    return engine


async def init_database(database_url: Optional[str] = None, drop_existing: bool = False) -> bool:
    """
    Initialize database with all tables.
    
    Args:
        database_url: Database connection URL. If None, uses settings.
        drop_existing: Whether to drop existing tables first.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print("🚀 Initializing database...")
        
        engine = await create_database_engine(database_url)
        
        async with engine.begin() as conn:
            if drop_existing:
                print("⚠️  Dropping existing tables...")
                await conn.run_sync(Base.metadata.drop_all)
            
            print("📋 Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        # Verify tables were created
        async with engine.begin() as conn:
            if "sqlite" in str(engine.url):
                result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
            else:
                result = await conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """))
                tables = [row[0] for row in result.fetchall()]
            
            print(f"✅ Created tables: {sorted(tables)}")
        
        await engine.dispose()
        print("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


async def create_test_profile() -> Optional[str]:
    """
    Create a test profile for development.
    
    Returns:
        str: Profile ID if successful, None otherwise.
    """
    try:
        from models.unified_models import Profile, UserRole
        from db.session import async_session
        import uuid
        
        profile_id = str(uuid.uuid4())
        
        async with async_session() as db:
            # Check if test profile already exists
            existing = await db.get(Profile, profile_id)
            if existing:
                print(f"✅ Test profile already exists: {profile_id}")
                return profile_id
            
            # Create test profile
            test_profile = Profile(
                id=profile_id,
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                role=UserRole.ADMIN,
                hashed_password="$2b$12$dummy_hash_for_testing"  # Dummy hash
            )
            
            db.add(test_profile)
            await db.commit()
            
            print(f"✅ Created test profile: {profile_id}")
            return profile_id
            
    except Exception as e:
        print(f"❌ Failed to create test profile: {e}")
        return None


async def main():
    """Main initialization function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize database")
    parser.add_argument("--drop", action="store_true", help="Drop existing tables")
    parser.add_argument("--url", type=str, help="Database URL")
    parser.add_argument("--create-test-profile", action="store_true", help="Create test profile")
    
    args = parser.parse_args()
    
    # Initialize database
    success = await init_database(args.url, args.drop)
    if not success:
        sys.exit(1)
    
    # Create test profile if requested
    if args.create_test_profile:
        profile_id = await create_test_profile()
        if profile_id:
            print(f"📝 Test profile ID: {profile_id}")
            print("💡 Use this ID in your test data and API calls")


if __name__ == "__main__":
    asyncio.run(main())