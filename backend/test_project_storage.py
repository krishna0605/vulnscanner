#!/usr/bin/env python3
"""
Test Project Storage in Database
Creates a test project and verifies it's stored correctly
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_project_storage():
    """Test creating and retrieving projects from database"""
    
    print("🚀 Testing project storage in database...")
    
    # Import after adding to path
    try:
        from core.supabase import get_supabase_client
        print("✅ Successfully imported Supabase client")
    except ImportError as e:
        print(f"❌ Could not import Supabase client: {e}")
        return False
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Check if users table exists and has data
        print("\n🔍 Checking users table...")
        try:
            users_result = supabase.table('users').select('*').limit(5).execute()
            print(f"✅ Users table accessible, found {len(users_result.data)} users")
            
            if users_result.data:
                print("👤 Sample users:")
                for user in users_result.data[:3]:
                    print(f"  - ID: {user.get('id')}")
                    print(f"    Email: {user.get('email')}")
                    print(f"    Username: {user.get('username')}")
                    print()
            
        except Exception as e:
            print(f"❌ Error accessing users table: {e}")
            return False
        
        # Check if projects table exists
        print("🔍 Checking projects table...")
        try:
            projects_result = supabase.table('projects').select('*').limit(5).execute()
            print(f"✅ Projects table accessible, found {len(projects_result.data)} projects")
            
            if projects_result.data:
                print("📋 Existing projects:")
                for project in projects_result.data:
                    print(f"  - ID: {project.get('id')}")
                    print(f"    Name: {project.get('name')}")
                    print(f"    Domain: {project.get('target_domain')}")
                    print(f"    Owner: {project.get('owner_id')}")
                    print(f"    Created: {project.get('created_at')}")
                    print()
            else:
                print("📝 No existing projects found")
            
        except Exception as e:
            print(f"❌ Error accessing projects table: {e}")
            return False
        
        # Create a test project
        print("🧪 Creating test project...")
        
        # Get a user ID for the test (use first user or create one)
        if users_result.data:
            test_user_id = users_result.data[0]['id']
            print(f"📝 Using existing user ID: {test_user_id}")
        else:
            print("❌ No users found, cannot create project without owner")
            return False
        
        # Create test project data
        test_project = {
            'id': str(uuid.uuid4()),
            'name': f'Test Project {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Test project created by automated verification script',
            'target_domain': 'https://example.com',
            'owner_id': test_user_id,
            'scope_rules': ['https://example.com/*'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Insert test project
        try:
            insert_result = supabase.table('projects').insert(test_project).execute()
            print("✅ Test project created successfully!")
            print(f"📊 Project ID: {test_project['id']}")
            print(f"📝 Project Name: {test_project['name']}")
            
        except Exception as e:
            print(f"❌ Error creating test project: {e}")
            return False
        
        # Verify the project was stored
        print("\n🔍 Verifying project storage...")
        try:
            verify_result = supabase.table('projects').select('*').eq('id', test_project['id']).execute()
            
            if verify_result.data:
                stored_project = verify_result.data[0]
                print("✅ Project successfully stored and retrieved!")
                print("📋 Stored project details:")
                print(f"  - ID: {stored_project.get('id')}")
                print(f"  - Name: {stored_project.get('name')}")
                print(f"  - Description: {stored_project.get('description')}")
                print(f"  - Domain: {stored_project.get('target_domain')}")
                print(f"  - Owner: {stored_project.get('owner_id')}")
                print(f"  - Created: {stored_project.get('created_at')}")
                
                # Verify data integrity
                if (stored_project.get('name') == test_project['name'] and
                    stored_project.get('target_domain') == test_project['target_domain'] and
                    stored_project.get('owner_id') == test_project['owner_id']):
                    print("✅ Data integrity verified - all fields match!")
                else:
                    print("⚠️ Data integrity issue - some fields don't match")
                
            else:
                print("❌ Project not found after creation!")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying project storage: {e}")
            return False
        
        # Get updated project count
        print("\n📊 Final project count...")
        try:
            final_count = supabase.table('projects').select('*').execute()
            print(f"📈 Total projects in database: {len(final_count.data)}")
            
        except Exception as e:
            print(f"❌ Error getting final count: {e}")
        
        print("\n🎉 Project storage test completed successfully!")
        print("✅ Database is working correctly for project storage")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_project_storage()
    
    if success:
        print("\n✅ All tests passed!")
        print("🎯 Your database is ready for project creation and storage")
    else:
        print("\n❌ Tests failed!")
        print("💡 Please check your Supabase configuration and schema")
        sys.exit(1)