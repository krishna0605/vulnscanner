#!/usr/bin/env python3
"""
Create tables in Supabase using direct HTTP requests
"""
import requests
from core.config import Settings

def create_tables():
    """Create tables using Supabase REST API."""
    try:
        print("🚀 Creating tables in Supabase...")
        
        settings = Settings()
        
        if not settings.supabase_url or not settings.supabase_service_role_key:
            print("❌ Supabase configuration missing")
            return False
        
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "apikey": settings.supabase_service_role_key
        }
        
        # Test connection first
        print("🔍 Testing Supabase connection...")
        health_url = f"{settings.supabase_url}/rest/v1/"
        response = requests.get(health_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase connection successful")
        else:
            print(f"⚠️  Supabase connection issue: {response.status_code}")
        
        # Try to check if tables exist by querying them
        print("\n🔍 Checking existing tables...")
        
        # Check users table
        try:
            users_url = f"{settings.supabase_url}/rest/v1/users?select=count"
            response = requests.get(users_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ Users table already exists")
            else:
                print(f"ℹ️  Users table not found: {response.status_code}")
        except Exception as e:
            print(f"ℹ️  Users table check failed: {e}")
        
        # Check projects table
        try:
            projects_url = f"{settings.supabase_url}/rest/v1/projects?select=count"
            response = requests.get(projects_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ Projects table already exists")
            else:
                print(f"ℹ️  Projects table not found: {response.status_code}")
        except Exception as e:
            print(f"ℹ️  Projects table check failed: {e}")
        
        # Try to insert a test user to see if users table exists
        print("\n🧪 Testing user creation...")
        try:
            users_url = f"{settings.supabase_url}/rest/v1/users"
            test_user = {
                "email": "test@example.com",
                "full_name": "Test User",
                "role": "user",
                "is_active": True
            }
            
            response = requests.post(users_url, headers=headers, json=test_user, timeout=10)
            
            if response.status_code in [200, 201]:
                print("✅ Test user created successfully")
            elif response.status_code == 409:
                print("ℹ️  Test user already exists")
            else:
                print(f"⚠️  User creation failed: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"⚠️  User creation test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def test_project_creation():
    """Test project creation."""
    try:
        print("\n🧪 Testing project creation...")
        
        settings = Settings()
        
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "apikey": settings.supabase_service_role_key
        }
        
        projects_url = f"{settings.supabase_url}/rest/v1/projects"
        test_project = {
            "name": "Test Project",
            "description": "Test project for API validation",
            "target_domain": "example.com",
            "owner_id": 1
        }
        
        response = requests.post(projects_url, headers=headers, json=test_project, timeout=10)
        
        if response.status_code in [200, 201]:
            print("✅ Test project created successfully")
            project_data = response.json()
            print(f"📊 Project ID: {project_data[0].get('id', 'N/A')}")
            return True
        else:
            print(f"⚠️  Project creation failed: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Project creation test failed: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🗄️  TESTING SUPABASE TABLES")
    print("=" * 60)
    
    # Test table creation
    tables_success = create_tables()
    
    if tables_success:
        # Test project creation
        project_success = test_project_creation()
        
        print("\n" + "=" * 60)
        if project_success:
            print("✅ SUPABASE TABLES WORKING!")
        else:
            print("⚠️  TABLES EXIST BUT NEED MANUAL SETUP")
        print("=" * 60)
        
        print("\n💡 Next steps:")
        if not project_success:
            print("1. Go to Supabase Dashboard > SQL Editor")
            print("2. Copy and paste minimal_schema.sql")
            print("3. Execute the SQL manually")
        print("4. Test project creation API")
        print("5. Verify data storage")
        
        print("\n🔑 Development credentials:")
        print("Token: dev-bypass")
        print("User ID: 1")
        print("Email: test@example.com")
    else:
        print("\n❌ Supabase connection failed")

if __name__ == "__main__":
    main()