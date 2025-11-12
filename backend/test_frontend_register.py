#!/usr/bin/env python3
"""
Test user registration through the frontend API
"""
import requests

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_register_user():
    """Test user registration through the backend API"""
    print("🧪 Testing user registration...")
    
    # Test credentials
    email = "test@example.com"
    password = "testpassword123"
    
    # Registration data
    register_data = {
        "email": email,
        "password": password,
        "full_name": "Test User"
    }
    
    try:
        # Try to register through backend API
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ User registration successful!")
            return True
        elif response.status_code == 400:
            response_data = response.json()
            if "already exists" in response_data.get("detail", "").lower():
                print("ℹ️  User already exists - that's okay!")
                return True
            else:
                print(f"❌ Registration failed: {response_data.get('detail', 'Unknown error')}")
                return False
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login_user():
    """Test user login through the backend API"""
    print("\n🧪 Testing user login...")
    
    # Test credentials
    email = "test@example.com"
    password = "testpassword123"
    
    # Login data
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        # Try to login through backend API
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            if access_token:
                print("✅ User login successful!")
                print(f"🎫 Access Token: {access_token[:50]}...")
                return access_token
            else:
                print("❌ Login response missing access token!")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_api(token):
    """Test authenticated API call"""
    print("\n🧪 Testing authenticated API call...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BACKEND_URL}/api/v1/overview",
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authenticated API call successful!")
            return True
        else:
            print(f"❌ Authenticated API call failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authenticated API call error: {e}")
        return False

def main():
    print("🚀 Frontend Registration Test")
    print("=" * 50)
    
    # Test registration
    registration_success = test_register_user()
    
    if registration_success:
        # Test login
        token = test_login_user()
        
        if token:
            # Test authenticated API call
            api_success = test_authenticated_api(token)
            
            print("\n" + "=" * 50)
            if api_success:
                print("🎉 Full authentication flow successful!")
                print("💡 Frontend should now work with authentication")
            else:
                print("💥 Authentication works but API call failed!")
        else:
            print("\n💥 Registration worked but login failed!")
    else:
        print("\n💥 Registration failed!")

if __name__ == "__main__":
    main()