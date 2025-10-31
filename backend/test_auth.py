#!/usr/bin/env python3
"""
Test authentication endpoints with Supabase backend
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    """Test user registration"""
    print("🧪 Testing user registration...")
    
    # Test data
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Registration successful!")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ User already exists - that's okay!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🧪 Testing user login...")
    
    # Test with the user we created in test_supabase_connection.py
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful!")
                print(f"Access Token: {data['access_token'][:50]}...")
                return data["access_token"]
            else:
                print("❌ Login response missing access token!")
                return None
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def main():
    print("🚀 Testing authentication with Supabase backend...")
    print("=" * 50)
    
    # Test registration
    register_success = test_register()
    
    # Test login
    token = test_login()
    
    print("\n" + "=" * 50)
    if register_success and token:
        print("✅ All authentication tests passed!")
        print("🎉 Supabase integration is working correctly!")
    else:
        print("❌ Some authentication tests failed!")

if __name__ == "__main__":
    main()