#!/usr/bin/env python3
"""
Simple test to check if the auth endpoints are working.
"""

import requests

def test_dev_endpoint():
    """Test the development test endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/auth/dev-test")
        print(f"Dev test status: {response.status_code}")
        print(f"Dev test response: {response.text}")
    except Exception as e:
        print(f"Dev test error: {e}")

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/health")
        print(f"Health status: {response.status_code}")
        print(f"Health response: {response.text}")
    except Exception as e:
        print(f"Health error: {e}")

def test_registration_raw():
    """Test registration with raw request."""
    try:
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = requests.post(
            "http://localhost:8000/api/auth/register",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Registration status: {response.status_code}")
        print(f"Registration response: {response.text}")
    except Exception as e:
        print(f"Registration error: {e}")

if __name__ == "__main__":
    print("Testing endpoints...")
    test_health_endpoint()
    print()
    test_dev_endpoint()
    print()
    test_registration_raw()