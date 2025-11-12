#!/usr/bin/env python3
"""
Test Supabase Auth directly to isolate the issue.
"""

import time
import random
from core.supabase import get_supabase_client

def test_direct_supabase_auth():
    """Test Supabase Auth directly"""
    print("🚀 Testing Direct Supabase Auth")
    print("=" * 50)
    
    try:
        client = get_supabase_client()
        if not client:
            print("❌ Failed to get Supabase client")
            return False
        
        print("✅ Supabase client obtained")
        
        # Generate unique email
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        unique_email = f"directtest{timestamp}{random_num}@example.com"
        
        print(f"🧪 Testing direct registration with email: {unique_email}")
        
        # Test direct sign_up
        response = client.auth.sign_up({
            "email": unique_email,
            "password": "testpassword123",
            "options": {
                "data": {
                    "full_name": "Direct Test User"
                }
            }
        })
        
        print(f"📊 Response type: {type(response)}")
        print(f"📄 Response: {response}")
        
        if hasattr(response, 'user') and response.user:
            print("✅ Direct registration successful!")
            print(f"👤 User ID: {response.user.id}")
            print(f"📧 Email: {response.user.email}")
            print(f"✉️ Email confirmed: {response.user.email_confirmed_at is not None}")
            
            # Test login
            print(f"\n🧪 Testing direct login with email: {unique_email}")
            login_response = client.auth.sign_in_with_password({
                "email": unique_email,
                "password": "testpassword123"
            })
            
            print(f"📊 Login response type: {type(login_response)}")
            print(f"📄 Login response: {login_response}")
            
            if hasattr(login_response, 'session') and login_response.session:
                print("✅ Direct login successful!")
                print(f"🔑 Access token: {login_response.session.access_token[:50]}...")
                return True
            else:
                print("❌ Direct login failed")
                return False
        else:
            print("❌ Direct registration failed")
            print(f"📄 Full response: {response}")
            return False
            
    except Exception as e:
        print(f"💥 Error during direct test: {e}")
        print(f"📄 Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_supabase_auth()
    if success:
        print("\n🎉 Direct Supabase Auth test successful!")
    else:
        print("\n💥 Direct Supabase Auth test failed!")