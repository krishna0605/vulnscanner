#!/usr/bin/env python3
"""
Test login endpoint with existing test user.
"""

import requests

def test_login():
    """Test login with existing test user"""
    print("🚀 Testing Login Endpoint")
    print("=" * 50)
    
    # Login data
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        print("🧪 Testing user login...")
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
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
                    print("✅ Authenticated API call successful!")
                    return True
                else:
                    print("❌ Authenticated API call failed!")
                    return False
            else:
                print("❌ No access token in response!")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error during login test: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    if success:
        print("\n🎉 Login test completed successfully!")
    else:
        print("\n💥 Login test failed!")