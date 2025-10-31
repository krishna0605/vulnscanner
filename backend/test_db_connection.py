#!/usr/bin/env python3
"""
Test database connection
"""
import asyncio
from db.session import async_session
import sqlalchemy as sa

async def test_db_connection():
    print("🧪 Testing database connection...")
    
    try:
        async with async_session() as session:
            # Simple query to test connection
            result = await session.execute(sa.text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful! Test query result: {row}")
            
            # Test if users table exists
            try:
                result = await session.execute(sa.text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"✅ Users table exists with {count} users")
                return True
            except Exception as e:
                print(f"❌ Users table query failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_db_connection())