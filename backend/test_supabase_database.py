#!/usr/bin/env python3
"""
Test Supabase database access to diagnose auth issues.
"""

from core.supabase import get_supabase_client, get_supabase_admin_client

def test_supabase_database():
    """Test Supabase database access"""
    print("🚀 Testing Supabase Database Access")
    print("=" * 50)
    
    try:
        # Test regular client
        client = get_supabase_client()
        if not client:
            print("❌ Failed to get Supabase client")
            return False
        
        print("✅ Supabase client obtained")
        
        # Test admin client
        admin_client = get_supabase_admin_client()
        if not admin_client:
            print("❌ Failed to get Supabase admin client")
            return False
        
        print("✅ Supabase admin client obtained")
        
        # Test basic database query
        print("\n🧪 Testing basic database query...")
        try:
            response = client.table('users').select('*').limit(1).execute()
            print(f"✅ Users table query successful: {len(response.data)} rows")
        except Exception as e:
            print(f"⚠️  Users table query failed: {e}")
        
        # Test projects table
        try:
            response = client.table('projects').select('*').limit(1).execute()
            print(f"✅ Projects table query successful: {len(response.data)} rows")
        except Exception as e:
            print(f"⚠️  Projects table query failed: {e}")
        
        # Check auth configuration
        print("\n🔧 Checking auth configuration...")
        try:
            # Try to get current session (should be None for unauthenticated)
            session = client.auth.get_session()
            print(f"📊 Current session: {session}")
        except Exception as e:
            print(f"⚠️  Session check failed: {e}")
        
        # Test admin operations
        print("\n🔧 Testing admin operations...")
        try:
            # Try to list users with admin client (this might reveal auth issues)
            response = admin_client.auth.admin.list_users()
            print(f"✅ Admin list users successful: {len(response.users) if hasattr(response, 'users') else 'Unknown'} users")
        except Exception as e:
            print(f"⚠️  Admin list users failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"💥 Error during database test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supabase_database()
    if success:
        print("\n🎉 Supabase database test completed!")
    else:
        print("\n💥 Supabase database test failed!")