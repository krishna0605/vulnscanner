#!/usr/bin/env python3
"""
Test script to verify project creation through FastAPI backend
"""
import requests
import sys
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is responding"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API is responding")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_project_endpoints():
    """Test project-related endpoints"""
    print("\n🧪 Testing project endpoints...")
    
    # Test GET /api/v1/projects (should require auth)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/projects")
        print(f"📋 GET /api/v1/projects: {response.status_code}")
        if response.status_code == 401:
            print("✅ Authentication required (expected)")
        elif response.status_code == 404:
            print("⚠️  Endpoint not found - may not be implemented yet")
        else:
            print(f"📄 Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing projects endpoint: {e}")

def test_available_endpoints():
    """Test what endpoints are available"""
    print("\n🔍 Checking available endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"🏠 GET /: {response.status_code}")
        if response.status_code == 200:
            print(f"📄 Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Error testing root endpoint: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"💚 GET /health: {response.status_code}")
        if response.status_code == 200:
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication endpoints...")
    
    # Test login endpoint
    try:
        response = requests.post(f"{BASE_URL}/auth/login")
        print(f"🔑 POST /auth/login: {response.status_code}")
        if response.status_code in [400, 422]:
            print("✅ Login endpoint exists (validation error expected)")
        elif response.status_code == 404:
            print("⚠️  Login endpoint not found")
        else:
            print(f"📄 Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing login endpoint: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 PROJECT API TEST")
    print("=" * 60)
    print(f"🚀 Testing API at: {BASE_URL}")
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Test API health
    if not test_api_health():
        print("\n❌ API is not responding. Please ensure the FastAPI server is running.")
        sys.exit(1)
    
    # Test available endpoints
    test_available_endpoints()
    
    # Test auth endpoints
    test_auth_endpoints()
    
    # Test project endpoints
    test_project_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ API TESTS COMPLETED")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("  1. Check if project endpoints are implemented")
    print("  2. Test with proper authentication")
    print("  3. Verify database storage")

if __name__ == "__main__":
    main()