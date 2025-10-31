#!/usr/bin/env python3
"""
Inspect existing table structure in Supabase
"""
import requests
import json
from core.config import Settings

def inspect_tables():
    """Inspect existing table structure."""
    try:
        print("🔍 Inspecting Supabase table structure...")
        
        settings = Settings()
        
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "apikey": settings.supabase_service_role_key
        }
        
        # Get table information from information_schema
        print("\n📊 Checking table schemas...")
        
        # Check users table structure
        print("\n🔍 Users table structure:")
        try:
            # Try to get a sample user to see the structure
            users_url = f"{settings.supabase_url}/rest/v1/users?select=*&limit=1"
            response = requests.get(users_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print("✅ Users table sample:")
                    print(json.dumps(data[0], indent=2))
                else:
                    print("ℹ️  Users table is empty")
            else:
                print(f"⚠️  Users table query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Users table inspection failed: {e}")
        
        # Check projects table structure
        print("\n🔍 Projects table structure:")
        try:
            projects_url = f"{settings.supabase_url}/rest/v1/projects?select=*&limit=1"
            response = requests.get(projects_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print("✅ Projects table sample:")
                    print(json.dumps(data[0], indent=2))
                else:
                    print("ℹ️  Projects table is empty")
            else:
                print(f"⚠️  Projects table query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Projects table inspection failed: {e}")
        
        # Check profiles table (Supabase auth extension)
        print("\n🔍 Profiles table structure:")
        try:
            profiles_url = f"{settings.supabase_url}/rest/v1/profiles?select=*&limit=1"
            response = requests.get(profiles_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print("✅ Profiles table sample:")
                    print(json.dumps(data[0], indent=2))
                else:
                    print("ℹ️  Profiles table is empty")
            else:
                print(f"⚠️  Profiles table query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Profiles table inspection failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table inspection failed: {e}")
        return False

def create_test_user_uuid():
    """Create a test user with proper UUID format."""
    try:
        print("\n🧪 Creating test user with UUID...")
        
        settings = Settings()
        
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "apikey": settings.supabase_service_role_key
        }
        
        # Try creating in profiles table (which extends auth.users)
        profiles_url = f"{settings.supabase_url}/rest/v1/profiles"
        test_user = {
            "id": "00000000-0000-0000-0000-000000000001",  # UUID format
            "username": "testuser",
            "full_name": "Test User",
            "email": "test@example.com",
            "role": "user"
        }
        
        response = requests.post(profiles_url, headers=headers, json=test_user, timeout=10)
        
        if response.status_code in [200, 201]:
            print("✅ Test user created in profiles table")
            return "00000000-0000-0000-0000-000000000001"
        elif response.status_code == 409:
            print("ℹ️  Test user already exists in profiles")
            return "00000000-0000-0000-0000-000000000001"
        else:
            print(f"⚠️  Profile creation failed: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        return None

def create_test_project_uuid(user_id):
    """Create a test project with proper UUID format."""
    try:
        print("\n🧪 Creating test project with UUID...")
        
        settings = Settings()
        
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "apikey": settings.supabase_service_role_key
        }
        
        projects_url = f"{settings.supabase_url}/rest/v1/projects"
        test_project = {
            "name": "Test Project UUID",
            "description": "Test project with UUID owner",
            "target_domain": "example.com",
            "owner_id": user_id
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
        print(f"❌ Project creation failed: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🔍 INSPECTING SUPABASE TABLES")
    print("=" * 60)
    
    # Inspect existing tables
    inspect_success = inspect_tables()
    
    if inspect_success:
        # Try creating test user and project with UUIDs
        user_id = create_test_user_uuid()
        
        if user_id:
            project_success = create_test_project_uuid(user_id)
            
            print("\n" + "=" * 60)
            if project_success:
                print("✅ SUPABASE TABLES WORKING WITH UUIDS!")
            else:
                print("⚠️  TABLES NEED SCHEMA ADJUSTMENT")
            print("=" * 60)
            
            print("\n💡 Key findings:")
            print("- Tables use UUID format, not integers")
            print("- Need to update API to use UUIDs")
            print("- Development mode should use UUID test user")
            
            print("\n🔑 Updated development credentials:")
            print("Token: dev-bypass")
            print(f"User ID: {user_id}")
            print("Email: test@example.com")
        else:
            print("\n❌ Could not create test user")
    else:
        print("\n❌ Table inspection failed")

if __name__ == "__main__":
    main()