#!/usr/bin/env python3
"""
Create tables in Supabase using REST API instead of direct database connection.
"""

import requests
import json
from passlib.context import CryptContext

# Supabase configuration
SUPABASE_URL = "https://ewijwxhjthqsmldaulwh.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3aWp3eGhqdGhxc21sZGF1bHdoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTU3NDcwNiwiZXhwIjoyMDc3MTUwNzA2fQ.NktZcudu0PobVb2-7dMC70QaGHXcYfucyPnp4eqJ5fE"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_users_table():
    """Create users table using Supabase REST API."""
    try:
        print("🚀 Creating users table via Supabase REST API...")
        
        # SQL to create users table
        sql_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """
        
        # Use Supabase SQL function
        url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "sql": sql_query
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ Users table created successfully!")
            return True
        else:
            print(f"❌ Failed to create table. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try alternative approach - check if table exists
            print("Trying to check if users table exists...")
            check_url = f"{SUPABASE_URL}/rest/v1/users?select=id&limit=1"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200:
                print("✅ Users table already exists!")
                return True
            else:
                print(f"❌ Users table does not exist and cannot be created")
                return False
                
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        return False

def create_test_user():
    """Create a test user using Supabase REST API."""
    try:
        print("Creating test user...")
        
        # Test user data
        test_email = "test@example.com"
        test_password = "testpassword123"
        hashed_password = hash_password(test_password)
        
        # Check if user already exists
        url = f"{SUPABASE_URL}/rest/v1/users?select=*&email=eq.{test_email}"
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200 and response.json():
            print(f"✅ Test user already exists: {test_email}")
            return True
        
        # Create new user
        user_data = {
            "email": test_email,
            "hashed_password": hashed_password,
            "is_active": True
        }
        
        create_url = f"{SUPABASE_URL}/rest/v1/users"
        create_response = requests.post(create_url, headers=headers, json=user_data)
        
        if create_response.status_code in [200, 201]:
            print(f"✅ Test user created successfully: {test_email}")
            return True
        else:
            print(f"❌ Failed to create test user. Status: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

def main():
    """Main function to set up Supabase via REST API."""
    try:
        print("🚀 Setting up Supabase via REST API...")
        
        # Create users table
        if not create_users_table():
            print("❌ Failed to create users table")
            return False
        
        # Create test user
        if not create_test_user():
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
    exit(0 if success else 1)