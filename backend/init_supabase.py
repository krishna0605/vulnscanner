"""
Initialize Supabase database with users table for authentication.
This script creates the necessary tables and sets up a test user.
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set Windows event loop policy to avoid psycopg issues
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text  # noqa: E402
from db.session import db_url, async_session, engine, init_db  # noqa: E402
from core.security import get_password_hash  # noqa: E402

async def create_tables():
    """Create all tables in the database."""
    try:
        print(f"Connecting to database: {db_url[:50]}...")
        
        # Use the existing init_db function
        print("Creating tables...")
        await init_db()
        print("✅ Tables created successfully!")
        
        return async_session
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

async def create_test_user(async_session):
    """Create a test user for authentication testing."""
    try:
        async with async_session() as session:
            # Check if user already exists
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": "test@example.com"}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print("✅ Test user already exists!")
                return
            
            # Create new test user
            hashed_password = get_password_hash("testpassword123")
            
            # Insert user directly using SQL to avoid ORM issues
            await session.execute(
                text("""
                    INSERT INTO users (email, full_name, hashed_password, is_active)
                    VALUES (:email, :full_name, :hashed_password, :is_active)
                """),
                {
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "hashed_password": hashed_password,
                    "is_active": True
                }
            )
            await session.commit()
            print("✅ Test user created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        raise

async def main():
    """Main function to initialize the database."""
    print("🚀 Initializing Supabase database...")
    
    try:
        # Create tables
        async_session = await create_tables()
        
        # Create test user
        await create_test_user(async_session)
        
        # Close engine
        await engine.dispose()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📝 Test credentials:")
        print("Email: test@example.com")
        print("Password: testpassword123")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())