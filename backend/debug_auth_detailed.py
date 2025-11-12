#!/usr/bin/env python3
"""
Detailed authentication debugging script
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.security import verify_password, get_password_hash  # noqa: E402
from db.session import async_session  # noqa: E402
from sqlalchemy import text  # noqa: E402

async def debug_authentication():
    """Debug the authentication process step by step"""
    print("🔍 Starting detailed authentication debugging...")
    
    # Test password hashing and verification
    test_password = "testpassword123"
    print(f"\n1. Testing password: {test_password}")
    
    # Generate a fresh hash
    fresh_hash = get_password_hash(test_password)
    print(f"Fresh hash: {fresh_hash}")
    
    # Test verification with fresh hash
    fresh_verify = verify_password(test_password, fresh_hash)
    print(f"Fresh hash verification: {fresh_verify}")
    
    # Get the hash from database
    async with async_session() as session:
        result = await session.execute(
            text("SELECT id, email, hashed_password FROM profiles WHERE email = :email"),
            {"email": "test@example.com"}
        )
        user_row = result.fetchone()
        
        if user_row:
            user_id, email, stored_hash = user_row
            print("\n2. Database user found:")
            print(f"   ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Stored hash: {stored_hash}")
            
            # Test verification with stored hash
            print("\n3. Testing verification with stored hash...")
            try:
                stored_verify = verify_password(test_password, stored_hash)
                print(f"   Stored hash verification: {stored_verify}")
            except Exception as e:
                print(f"   ERROR during verification: {e}")
                print(f"   Error type: {type(e)}")
                
                # Let's try to understand the hash format
                print("\n4. Analyzing hash format:")
                print(f"   Hash length: {len(stored_hash)}")
                print(f"   Hash starts with: {stored_hash[:20]}...")
                print(f"   Hash contains '$': {'$' in stored_hash}")
                
                # Count the $ separators
                parts = stored_hash.split('$')
                print(f"   Hash parts count: {len(parts)}")
                if len(parts) >= 4:
                    print(f"   Algorithm: {parts[1]}")
                    print(f"   Rounds: {parts[2]}")
                    print(f"   Salt+Hash: {parts[3][:20]}...")
                
        else:
            print("❌ No user found in database!")

if __name__ == "__main__":
    asyncio.run(debug_authentication())