#!/usr/bin/env python3
"""
Test the exact login flow that the frontend uses
"""
import requests
import json

def test_frontend_login_flow():
    """Test the exact login flow that the frontend uses"""
    print("🧪 Testing frontend login flow...")
    
    # Test credentials from user
    email = "test@example.com"
    password = "testpassword123"
    
    # Backend API URL (same as frontend uses)
    API_BASE_URL = "http://127.0.0.1:8000"
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("-" * 50)
    
    try:
        # Make the exact same request as frontend
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            headers={'Content-Type': 'application/json'},
            json={'email': email, 'password': password}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"🎫 Access Token: {data.get('access_token', 'MISSING')[:50]}...")
            print(f"🔐 Token Type: {data.get('token_type', 'MISSING')}")
            return True
        else:
            print(f"❌ Login failed!")
            try:
                error_data = response.json()
                print(f"💥 Error Details: {error_data}")
            except:
                print(f"💥 Raw Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server is not running!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_backend_health():
    """Test if backend is running"""
    print("\n🏥 Testing backend health...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"⚠️ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Frontend Login Flow Test")
    print("=" * 50)
    
    # Test backend health first
    backend_healthy = test_backend_health()
    
    if backend_healthy:
        # Test login flow
        login_success = test_frontend_login_flow()
        
        print("\n" + "=" * 50)
        if login_success:
            print("🎉 Frontend login flow should work!")
            print("💡 The issue might be in the frontend configuration.")
        else:
            print("💥 Frontend login flow is broken!")
            print("💡 Check backend authentication or user creation.")
    else:
        print("\n💥 Backend is not accessible!")
        print("💡 Make sure the backend server is running on port 8000.")