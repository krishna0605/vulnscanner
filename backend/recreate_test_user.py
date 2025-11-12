#!/usr/bin/env python3
"""
Delete and recreate test user with fresh password hash
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import text
from db.session import async_session
from passlib.context import CryptContext

async def recreate_test_user():
    """Delete and recreate test user."""
    try:
        print("🗑️ Deleting existing test user...")
        
        async with async_session() as session:
            # Delete existing user
            await session.execute(
                text("DELETE FROM profiles WHERE email = :email"),
                {"email": "test@example.com"}
            )
            await session.commit()
            print("✅ Existing user deleted")
            
            # Create new test user with fresh hash
            print("🚀 Creating new test user...")
            # Generate password hash locally to avoid importing security module
            pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("testpassword123")
            print(f"Generated hash: {hashed_password}")
            
            # Generate UUID for the user
            import uuid
            user_id = str(uuid.uuid4())
            
            # Insert user
            await session.execute(
                text("""
                    INSERT INTO profiles (
                        id,
                        email,
                        full_name,
                        hashed_password,
                        role,
                        timezone,
                        preferences,
                        is_active,
                        email_confirmed,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :id,
                        :email,
                        :full_name,
                        :hashed_password,
                        :role,
                        :timezone,
                        :preferences,
                        :is_active,
                        :email_confirmed,
                        :created_at,
                        :updated_at
                    )
                """),
                {
                    "id": user_id,
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "hashed_password": hashed_password,
                    "role": "user",
                    "timezone": "UTC",
                    "preferences": "{}",
                    "is_active": True,
                    "email_confirmed": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            await session.commit()
            print("✅ New test user created successfully!")
            
            # Verify the user was created
            result = await session.execute(
                text("SELECT id, email, hashed_password FROM profiles WHERE email = :email"),
                {"email": "test@example.com"}
            )
            user = result.fetchone()
            if user:
                print(f"✅ User verified: {user.email} (ID: {user.id})")
                print(f"Hash in DB: {user.hashed_password}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(recreate_test_user())