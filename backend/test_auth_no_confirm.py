#!/usr/bin/env python3
"""
Test Supabase Auth with email confirmation disabled.
"""

import time
import random
from core.supabase import get_supabase_admin_client

def test_auth_no_confirm():
    """Test Supabase Auth with admin client (bypasses email confirmation)"""
    print("🚀 Testing Supabase Auth with Admin Client")
    print("=" * 50)
    
    try:
        admin_client = get_supabase_admin_client()
        if not admin_client:
            print("❌ Failed to get Supabase admin client")
            return False
        
        print("✅ Supabase admin client obtained")
        
        # Generate unique email
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        unique_email = f"admintest{timestamp}{random_num}@example.com"
        
        print(f"🧪 Testing admin user creation with email: {unique_email}")
        
        # Test admin create user (bypasses email confirmation)
        response = admin_client.auth.admin.create_user({
            "email": unique_email,
            "password": "testpassword123",
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": "Admin Test User"
            }
        })
        
        print(f"📊 Response type: {type(response)}")
        print(f"📄 Response: {response}")
        
        if hasattr(response, 'user') and response.user:
            print("✅ Admin user creation successful!")
            print(f"👤 User ID: {response.user.id}")
            print(f"📧 Email: {response.user.email}")
            print(f"✉️ Email confirmed: {response.user.email_confirmed_at is not None}")
            
            # Now test regular login with this user
            print(f"\n🧪 Testing login with created user: {unique_email}")
            
            # Use regular client for login
            from core.supabase import get_supabase_client
            client = get_supabase_client()
            
            login_response = client.auth.sign_in_with_password({
                "email": unique_email,
                "password": "testpassword123"
            })
            
            print(f"📊 Login response type: {type(login_response)}")
            
            if hasattr(login_response, 'session') and login_response.session:
                print("✅ Login successful!")
                print(f"🔑 Access token: {login_response.session.access_token[:50]}...")
                return True
            else:
                print("❌ Login failed")
                print(f"📄 Login response: {login_response}")
                return False
        else:
            print("❌ Admin user creation failed")
            print(f"📄 Full response: {response}")
            return False
            
    except Exception as e:
        print(f"💥 Error during admin test: {e}")
        print(f"📄 Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auth_no_confirm()
    if success:
        print("\n🎉 Admin auth test successful!")
    else:
        print("\n💥 Admin auth test failed!")