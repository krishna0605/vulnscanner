#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration
Tests CORS, authentication endpoints, and basic API functionality
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🔍 Testing CORS preflight...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    
    try:
        response = requests.options(f"{BACKEND_URL}/api/auth/register", headers=headers)
        print(f"   CORS preflight status: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ CORS preflight failed: {e}")
        return False

def test_registration_from_frontend():
    """Test user registration as if from frontend"""
    print("\n📝 Testing registration from frontend perspective...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Content-Type': 'application/json'
    }
    
    timestamp = int(time.time())
    user_data = {
        "username": f"frontend_test_{timestamp}",
        "email": f"frontend_test_{timestamp}@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Register user
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            headers=headers,
            json=user_data
        )
        
        print(f"   Registration status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"   ✅ User created: {user.get('email')}")
            
            # Now login to get token
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                headers=headers,
                json=login_data
            )
            
            print(f"   Login status: {login_response.status_code}")
            if login_response.status_code == 200:
                token_data = login_response.json()
                print("   ✅ Login successful, token received")
                return token_data.get('access_token'), user
            else:
                print(f"   ❌ Login failed: {login_response.text}")
                return None, user
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Registration/Login error: {e}")
        return None, None

def test_authenticated_request(token, user):
    """Test authenticated request to overview endpoint"""
    print("\n🔐 Testing authenticated request...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/overview", headers=headers)
        print(f"   Overview status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Overview data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   ❌ Overview failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Overview error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\n❤️ Testing health endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        print(f"   Health status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Frontend-Backend Integration Tests")
    print("=" * 50)
    
    # Test 1: CORS
    cors_ok = test_cors_preflight()
    
    # Test 2: Health endpoint
    health_ok = test_health_endpoint()
    
    # Test 3: Registration
    token, user = test_registration_from_frontend()
    registration_ok = token is not None
    
    # Test 4: Authenticated request
    auth_ok = False
    if token:
        auth_ok = test_authenticated_request(token, user)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   CORS Preflight: {'✅ PASS' if cors_ok else '❌ FAIL'}")
    print(f"   Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Registration: {'✅ PASS' if registration_ok else '❌ FAIL'}")
    print(f"   Authentication: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    
    all_passed = cors_ok and health_ok and registration_ok and auth_ok
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Frontend-Backend integration is working correctly!")
        print("   The frontend should be able to communicate with the backend successfully.")
    else:
        print("\n⚠️ Some integration issues detected.")
        print("   Check the failed tests above for details.")

if __name__ == "__main__":
    main()