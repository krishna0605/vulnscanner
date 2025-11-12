#!/usr/bin/env python3
"""
Simple script to create a test user for authentication testing
"""
import asyncio
import sys
from datetime import datetime, timezone
from sqlalchemy import text
from db.session import async_session
from core.security import get_password_hash

async def create_test_user():
    """Create a test user in the database."""
    try:
        print("🚀 Creating test user...")
        
        async with async_session() as session:
            # Check if user already exists
            result = await session.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": "test@example.com"}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"✅ Test user already exists: {existing_user.email} (ID: {existing_user.id})")
                return True
            
            # Create new test user
            hashed_password = get_password_hash("testpassword123")
            now = datetime.now(timezone.utc)
            
            await session.execute(
                text("""
                INSERT INTO users (email, full_name, hashed_password, is_active, created_at, updated_at)
                VALUES (:email, :full_name, :hashed_password, :is_active, :created_at, :updated_at)
                """),
                {
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "hashed_password": hashed_password,
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now
                }
            )
            
            await session.commit()
            
            # Verify user was created
            result = await session.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": "test@example.com"}
            )
            new_user = result.fetchone()
            
            if new_user:
                print("✅ Test user created successfully!")
                print(f"   ID: {new_user.id}")
                print(f"   Email: {new_user.email}")
                print()
                print("🔑 Login Credentials:")
                print("Email: test@example.com")
                print("Password: testpassword123")
                return True
            else:
                print("❌ Failed to create test user")
                return False
                
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_test_user())
    sys.exit(0 if success else 1)