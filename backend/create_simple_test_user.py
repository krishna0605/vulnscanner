#!/usr/bin/env python3
"""
Simple script to create a test user for authentication testing
"""
import asyncio
import sys
from datetime import datetime
from sqlalchemy import text
from core.database import get_async_session
from core.security import get_password_hash

async def create_test_user():
    """Create a test user in the database."""
    try:
        print("🚀 Creating test user...")
        
        # Get database session
        async_session = get_async_session()
        
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
            print("Creating new test user...")
            hashed_password = get_password_hash("testpassword123")
            
            # Insert user
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
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            await session.commit()
            print("✅ Test user created successfully!")
            
            # Verify creation
            result = await session.execute(
                text("SELECT id, email, full_name FROM users WHERE email = :email"),
                {"email": "test@example.com"}
            )
            new_user = result.fetchone()
            if new_user:
                print(f"📄 User ID: {new_user.id}")
                print(f"📄 Email: {new_user.email}")
                print(f"📄 Full Name: {new_user.full_name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("=" * 50)
    print("🧪 TEST USER CREATION")
    print("=" * 50)
    
    success = await create_test_user()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ TEST USER SETUP COMPLETE")
        print("=" * 50)
        print("\n📝 Test Login Credentials:")
        print("Email: test@example.com")
        print("Password: testpassword123")
        print("\n💡 You can now test project creation with these credentials!")
    else:
        print("\n❌ Failed to create test user")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())