#!/usr/bin/env python3
"""
Simple script to create tables in Supabase using direct SQL connection.
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

import asyncpg  # noqa: E402
from passlib.context import CryptContext  # noqa: E402

# Database URL from environment
DATABASE_URL = "postgresql://postgres.ewijwxhjthqsmldaulwh:NktZcudu0PobVb2-7dMC70QaGHXcYfucyPnp4eqJ5fE@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def create_tables_and_user():
    """Create tables and test user in Supabase."""
    try:
        print("🚀 Connecting to Supabase...")
        
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to Supabase successfully!")
        
        # Create users table
        print("Creating users table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create index on email
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        
        print("✅ Users table created successfully!")
        
        # Check if test user exists
        test_email = "test@example.com"
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", test_email
        )
        
        if existing_user:
            print(f"✅ Test user already exists: {test_email}")
        else:
            # Create test user
            print("Creating test user...")
            test_password = "testpassword123"
            hashed_password = hash_password(test_password)
            
            await conn.execute("""
                INSERT INTO users (email, hashed_password, is_active)
                VALUES ($1, $2, $3)
            """, test_email, hashed_password, True)
            
            print(f"✅ Test user created: {test_email}")
        
        # Close connection
        await conn.close()
        
        print("✅ Supabase setup completed successfully!")
        print("\n📝 Test Login Credentials:")
        print("Email: test@example.com")
        print("Password: testpassword123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main function."""
    success = await create_tables_and_user()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)