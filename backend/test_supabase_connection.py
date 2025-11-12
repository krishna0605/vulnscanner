#!/usr/bin/env python3
"""
Test Supabase connection and create user if table exists.
"""

import requests
from passlib.context import CryptContext

# Supabase configuration
SUPABASE_URL = "https://ewijwxhjthqsmldaulwh.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3aWp3eGhqdGhxc21sZGF1bHdoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTU3NDcwNiwiZXhwIjoyMDc3MTUwNzA2fQ.NktZcudu0PobVb2-7dMC70QaGHXcYfucyPnp4eqJ5fE"

# Password hashing - using same scheme as backend
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def test_connection():
    """Test connection to Supabase."""
    try:
        print("🚀 Testing Supabase connection...")
        
        # Test basic connection
        url = f"{SUPABASE_URL}/rest/v1/"
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully connected to Supabase!")
            return True
        else:
            print(f"❌ Failed to connect. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def check_users_table():
    """Check if users table exists."""
    try:
        print("Checking if users table exists...")
        
        url = f"{SUPABASE_URL}/rest/v1/users?select=id&limit=1"
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Users table exists!")
            return True
        elif response.status_code == 404:
            print("❌ Users table does not exist")
            return False
        else:
            print(f"❌ Error checking table. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return False

def create_test_user():
    """Create a test user."""
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
    """Main function to test Supabase."""
    try:
        print("🚀 Testing Supabase setup...")
        
        # Test connection
        if not test_connection():
            print("❌ Cannot connect to Supabase")
            return False
        
        # Check if users table exists
        if not check_users_table():
            print("❌ Users table does not exist")
            print("\n📝 Manual Setup Required:")
            print("1. Go to https://ewijwxhjthqsmldaulwh.supabase.co")
            print("2. Navigate to SQL Editor")
            print("3. Run this SQL:")
            print("""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
            """)
            return False
        
        # Create test user
        if not create_test_user():
            print("❌ Failed to create test user")
            return False
        
        print("✅ Supabase test completed successfully!")
        print("\n📝 Test Login Credentials:")
        print("Email: test@example.com")
        print("Password: testpassword123")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)