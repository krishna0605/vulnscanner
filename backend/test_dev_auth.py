#!/usr/bin/env python3
"""
Test the development authentication workaround.
"""

import requests
import json
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:8000/api"

def test_registration():
    """Test user registration with development mode."""
    print("Testing registration with development mode...")
    
    # Generate unique email
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    email = f"devtest_{timestamp}@example.com"
    
    registration_data = {
        "email": email,
        "password": "testpassword123",
        "full_name": "Dev Test User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        if response.status_code in [200, 201]:
            user_data = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {user_data.get('id')}")
            print(f"Email: {user_data.get('email')}")
            print(f"Email Confirmed: {user_data.get('email_confirmed')}")
            return user_data
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login(email, password):
    """Test user login."""
    print(f"\nTesting login for {email}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {token_data.get('access_token')[:50]}...")
            print(f"Token Type: {token_data.get('token_type')}")
            return token_data.get('access_token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_endpoint(access_token):
    """Test an authenticated endpoint."""
    print("\nTesting authenticated endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test /auth/me endpoint
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers
        )
        
        print(f"Auth Me Status: {response.status_code}")
        print(f"Auth Me Response: {response.text}")
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ Authenticated endpoint successful!")
            print(f"User ID: {user_info.get('id')}")
            print(f"Email: {user_info.get('email')}")
            return True
        else:
            print(f"❌ Authenticated endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authenticated endpoint error: {e}")
        return False

def test_overview_endpoint(access_token):
    """Test the overview endpoint that the frontend is calling."""
    print("\nTesting overview endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/overview",
            headers=headers
        )
        
        print(f"Overview Status: {response.status_code}")
        print(f"Overview Response: {response.text}")
        
        if response.status_code == 200:
            overview_data = response.json()
            print("✅ Overview endpoint successful!")
            print(f"Overview data: {json.dumps(overview_data, indent=2)}")
            return True
        else:
            print(f"❌ Overview endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Overview endpoint error: {e}")
        return False

def main():
    """Run all authentication tests."""
    print("🚀 Starting development authentication tests...\n")
    
    # Test registration
    user_data = test_registration()
    if not user_data:
        print("❌ Registration failed, stopping tests")
        return
    
    # Test login
    access_token = test_login(user_data['email'], "testpassword123")
    if not access_token:
        print("❌ Login failed, stopping tests")
        return
    
    # Test authenticated endpoints
    auth_success = test_authenticated_endpoint(access_token)
    overview_success = test_overview_endpoint(access_token)
    
    print("\n📊 Test Results:")
    print("Registration: ✅ Success")
    print("Login: ✅ Success")
    print(f"Auth Me: {'✅ Success' if auth_success else '❌ Failed'}")
    print(f"Overview: {'✅ Success' if overview_success else '❌ Failed'}")
    
    if auth_success and overview_success:
        print("\n🎉 All tests passed! Development authentication is working.")
    else:
        print("\n⚠️ Some tests failed. Check the endpoints.")

if __name__ == "__main__":
    main()