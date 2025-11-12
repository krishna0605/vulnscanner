#!/usr/bin/env python3
"""
Simple Database Test
Direct test of Supabase connection and project storage
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def simple_db_test():
    """Simple test of database connection and project storage"""
    
    print("🚀 Simple database test...")
    
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        print(f"SUPABASE_URL: {'✅' if supabase_url else '❌'}")
        print(f"SUPABASE_ANON_KEY: {'✅' if supabase_key else '❌'}")
        return False
    
    print("✅ Supabase credentials found")
    print(f"📍 URL: {supabase_url}")
    
    try:
        # Import and create Supabase client directly
        from supabase import create_client
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
    except ImportError as e:
        print(f"❌ Supabase library not available: {e}")
        print("💡 Try: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Error creating Supabase client: {e}")
        return False
    
    # Test 1: Check users table
    print("\n🔍 Test 1: Checking users table...")
    try:
        users_result = supabase.table('users').select('id, email, username').limit(3).execute()
        print(f"✅ Users table accessible, found {len(users_result.data)} users")
        
        if users_result.data:
            print("👤 Sample users:")
            for user in users_result.data:
                print(f"  - {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
        else:
            print("📝 No users found")
            
    except Exception as e:
        print(f"❌ Error accessing users table: {e}")
        print("💡 This might mean the schema hasn't been applied yet")
        return False
    
    # Test 2: Check projects table
    print("\n🔍 Test 2: Checking projects table...")
    try:
        projects_result = supabase.table('projects').select('*').limit(5).execute()
        print(f"✅ Projects table accessible, found {len(projects_result.data)} projects")
        
        if projects_result.data:
            print("📋 Existing projects:")
            for project in projects_result.data:
                print(f"  - {project.get('name')} ({project.get('target_domain')})")
        else:
            print("📝 No projects found")
            
    except Exception as e:
        print(f"❌ Error accessing projects table: {e}")
        print("💡 This might mean the schema hasn't been applied yet")
        return False
    
    # Test 3: Create a test project
    print("\n🧪 Test 3: Creating test project...")
    
    if not users_result.data:
        print("❌ Cannot create project - no users available")
        return False
    
    test_user_id = users_result.data[0]['id']
    
    test_project = {
        'name': f'Test Project {datetime.now().strftime("%H%M%S")}',
        'description': 'Automated test project',
        'target_domain': 'https://test-example.com',
        'owner_id': test_user_id,
        'scope_rules': ['https://test-example.com/*']
    }
    
    try:
        insert_result = supabase.table('projects').insert(test_project).execute()
        
        if insert_result.data:
            created_project = insert_result.data[0]
            print("✅ Test project created successfully!")
            print(f"📊 Project ID: {created_project.get('id')}")
            print(f"📝 Project Name: {created_project.get('name')}")
            
            # Test 4: Verify project was stored
            print("\n🔍 Test 4: Verifying project storage...")
            verify_result = supabase.table('projects').select('*').eq('id', created_project.get('id')).execute()
            
            if verify_result.data:
                print("✅ Project successfully retrieved from database!")
                stored_project = verify_result.data[0]
                print("📋 Verification details:")
                print(f"  - Name matches: {stored_project.get('name') == test_project['name']}")
                print(f"  - Domain matches: {stored_project.get('target_domain') == test_project['target_domain']}")
                print(f"  - Owner matches: {stored_project.get('owner_id') == test_project['owner_id']}")
                
                return True
            else:
                print("❌ Project not found after creation!")
                return False
        else:
            print("❌ No data returned from insert operation")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test project: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 SIMPLE DATABASE TEST")
    print("=" * 50)
    
    success = simple_db_test()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("🎯 Database is working correctly for project storage")
        print("✅ Projects created through your app will be stored properly")
    else:
        print("❌ TESTS FAILED!")
        print("💡 Please check:")
        print("  1. Supabase credentials in .env file")
        print("  2. Schema has been applied to your Supabase database")
        print("  3. Tables exist and are accessible")
    print("=" * 50)