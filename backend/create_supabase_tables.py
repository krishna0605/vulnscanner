#!/usr/bin/env python3
"""
Create tables in Supabase using SQL commands.
This script creates the users table and inserts a test user.
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

from supabase import create_client, Client  # noqa: E402
from core.config import settings  # noqa: E402
from core.security import get_password_hash  # noqa: E402

def get_supabase_client() -> Client:
    """Create and return Supabase client."""
    url = settings.supabase_url
    key = settings.supabase_service_role_key
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return create_client(url, key)

def create_users_table(supabase: Client):
    """Create users table using SQL."""
    try:
        print("Creating users table...")
        
        # SQL to create users table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create index on email for faster lookups
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """
        
        # Execute the SQL
        _ = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Users table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        # Try alternative approach using direct table creation
        try:
            print("Trying alternative approach...")
            # Check if table exists by trying to select from it
            supabase.table('users').select('id').limit(1).execute()
            print("✅ Users table already exists!")
            return True
        except Exception as e2:
            print(f"❌ Users table does not exist and cannot be created: {e2}")
            return False

def create_test_user(supabase: Client):
    """Create a test user."""
    try:
        print("Creating test user...")
        
        # Test user data
        test_email = "test@example.com"
        test_password = "testpassword123"
        hashed_password = get_password_hash(test_password)
        
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', test_email).execute()
        
        if existing_user.data:
            print(f"✅ Test user already exists: {test_email}")
            return True
        
        # Insert new user
        user_data = {
            'email': test_email,
            'hashed_password': hashed_password,
            'is_active': True
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            print(f"✅ Test user created successfully: {test_email}")
            return True
        else:
            print("❌ Failed to create test user")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

def main():
    """Main function to set up Supabase tables."""
    try:
        print("🚀 Setting up Supabase tables...")
        
        # Create Supabase client
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Create users table
        if not create_users_table(supabase):
            print("❌ Failed to create users table")
            return False
        
        # Create test user
        if not create_test_user(supabase):
            print("❌ Failed to create test user")
            return False
        
        print("✅ Supabase setup completed successfully!")
        print("\n📝 Test Login Credentials:")
        print("Email: test@example.com")
        print("Password: testpassword123")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)