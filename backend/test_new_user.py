#!/usr/bin/env python3
"""
Test registration and login with a new unique user.
"""

import requests
import time
import random

def test_new_user():
    """Test registration and login with a new user"""
    print("🚀 Testing New User Registration and Login")
    print("=" * 50)
    
    # Generate unique email
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    unique_email = f"testuser{timestamp}{random_num}@example.com"
    
    # Registration data
    register_data = {
        "email": unique_email,
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        print(f"🧪 Testing user registration with email: {unique_email}")
        response = requests.post(
            "http://localhost:8000/api/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Registration Status Code: {response.status_code}")
        print(f"📄 Registration Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            
            # Try login immediately
            print("\n🧪 Testing login with new user...")
            login_data = {
                "email": unique_email,
                "password": "testpassword123"
            }
            
            login_response = requests.post(
                "http://localhost:8000/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Login Status Code: {login_response.status_code}")
            print(f"📄 Login Response: {login_response.text}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    print("✅ Login successful!")
                    print(f"🔑 Access Token: {access_token[:50]}...")
                    
                    # Test authenticated API call
                    print("\n🧪 Testing authenticated API call...")
                    auth_headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    overview_response = requests.get(
                        "http://localhost:8000/api/v1/overview",
                        headers=auth_headers
                    )
                    
                    print(f"📊 Overview Status: {overview_response.status_code}")
                    print(f"📄 Overview Response: {overview_response.text}")
                    
                    if overview_response.status_code == 200:
                        print("✅ Complete authentication flow successful!")
                        return True
                    else:
                        print("❌ Authenticated API call failed!")
                        return False
                else:
                    print("❌ No access token in response!")
                    return False
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_new_user()
    if success:
        print("\n🎉 Complete authentication test successful!")
    else:
        print("\n💥 Authentication test failed!")