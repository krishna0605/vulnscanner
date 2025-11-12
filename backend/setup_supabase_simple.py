#!/usr/bin/env python3
"""
Simple script to create tables in Supabase using existing database session.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Windows event loop fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text  # noqa: E402
from passlib.context import CryptContext  # noqa: E402

# Import existing database components
from db.session import engine, async_session  # noqa: E402

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def create_tables_and_user():
    """Create tables and test user in Supabase."""
    try:
        print("🚀 Setting up Supabase tables...")
        
        # Create users table using raw SQL
        print("Creating users table...")
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
            # Create index on email
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            """))
        
        print("✅ Users table created successfully!")
        
        # Create test user
        print("Creating test user...")
        test_email = "test@example.com"
        test_password = "testpassword123"
        hashed_password = hash_password(test_password)
        
        async with async_session() as session:
            # Check if user exists
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": test_email}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"✅ Test user already exists: {test_email}")
            else:
                # Insert new user
                await session.execute(
                    text("""
                        INSERT INTO users (email, hashed_password, is_active)
                        VALUES (:email, :hashed_password, :is_active)
                    """),
                    {
                        "email": test_email,
                        "hashed_password": hashed_password,
                        "is_active": True
                    }
                )
                await session.commit()
                print(f"✅ Test user created: {test_email}")
        
        print("✅ Supabase setup completed successfully!")
        print("\n📝 Test Login Credentials:")
        print("Email: test@example.com")
        print("Password: testpassword123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close engine
        await engine.dispose()

async def main():
    """Main function."""
    success = await create_tables_and_user()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)