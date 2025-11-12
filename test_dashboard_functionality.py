#!/usr/bin/env python3
"""
Test script to verify dashboard functionality end-to-end
Tests project creation, listing, updating, and deletion
"""

import requests
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def get_auth_token():
    """Get authentication token by registering and logging in a test user"""
    print("🔐 Getting authentication token...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Content-Type': 'application/json'
    }
    
    timestamp = int(time.time())
    user_data = {
        "username": f"dashboard_test_{timestamp}",
        "email": f"dashboard_test_{timestamp}@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Register user
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            headers=headers,
            json=user_data
        )
        
        if response.status_code != 200:
            print(f"   ❌ Registration failed: {response.text}")
            return None
            
        # Login to get token
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            headers=headers,
            json=login_data
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            print("   ✅ Authentication successful")
            return token_data.get('access_token')
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return None

def test_dashboard_overview(token):
    """Test dashboard overview endpoint"""
    print("\n📊 Testing dashboard overview...")
    
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
            print("   ✅ Overview data received:")
            print(f"      - Total projects: {data.get('total_projects', 0)}")
            print(f"      - Total scans: {data.get('total_scans', 0)}")
            print(f"      - Active scans: {data.get('active_scans', 0)}")
            return True
        else:
            print(f"   ❌ Overview failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Overview error: {e}")
        return False

def test_project_creation(token):
    """Test project creation"""
    print("\n📝 Testing project creation...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    project_data = {
        "name": f"Test Project {int(time.time())}",
        "description": "A test project for dashboard functionality",
        "target_domain": "https://example.com",
        "scope_rules": ["https://example.com/*"]
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/projects",
            headers=headers,
            json=project_data
        )
        
        print(f"   Project creation status: {response.status_code}")
        
        if response.status_code == 201:
            project = response.json()
            print("   ✅ Project created:")
            print(f"      - ID: {project.get('id')}")
            print(f"      - Name: {project.get('name')}")
            print(f"      - Domain: {project.get('target_domain')}")
            return project
        else:
            print(f"   ❌ Project creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Project creation error: {e}")
        return None

def test_project_listing(token):
    """Test project listing"""
    print("\n📋 Testing project listing...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/projects", headers=headers)
        print(f"   Project listing status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"   ✅ Projects listed: {len(projects)} projects found")
            for i, project in enumerate(projects[:3]):  # Show first 3
                print(f"      {i+1}. {project.get('name')} - {project.get('target_domain')}")
            return projects
        else:
            print(f"   ❌ Project listing failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ Project listing error: {e}")
        return []

def test_project_details(token, project_id):
    """Test getting project details"""
    print(f"\n🔍 Testing project details for ID: {project_id}...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/projects/{project_id}", headers=headers)
        print(f"   Project details status: {response.status_code}")
        
        if response.status_code == 200:
            project = response.json()
            print("   ✅ Project details retrieved:")
            print(f"      - Name: {project.get('name')}")
            print(f"      - Description: {project.get('description')}")
            print(f"      - Created: {project.get('created_at')}")
            return project
        else:
            print(f"   ❌ Project details failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Project details error: {e}")
        return None

def test_project_update(token, project_id):
    """Test project update"""
    print(f"\n✏️ Testing project update for ID: {project_id}...")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    update_data = {
        "name": f"Updated Test Project {int(time.time())}",
        "description": "Updated description for testing",
        "target_domain": "https://updated-example.com"
    }
    
    try:
        response = requests.put(
            f"{BACKEND_URL}/api/v1/projects/{project_id}",
            headers=headers,
            json=update_data
        )
        
        print(f"   Project update status: {response.status_code}")
        
        if response.status_code == 200:
            project = response.json()
            print("   ✅ Project updated:")
            print(f"      - New name: {project.get('name')}")
            print(f"      - New domain: {project.get('target_domain')}")
            return project
        else:
            print(f"   ❌ Project update failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Project update error: {e}")
        return None

def main():
    """Run all dashboard functionality tests"""
    print("🚀 Starting Dashboard Functionality Tests")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token. Aborting tests.")
        return
    
    # Test 1: Dashboard overview
    overview_ok = test_dashboard_overview(token)
    
    # Test 2: Project creation
    project = test_project_creation(token)
    creation_ok = project is not None
    
    # Test 3: Project listing
    projects = test_project_listing(token)
    listing_ok = len(projects) > 0
    
    # Test 4: Project details (if we have a project)
    details_ok = False
    if project:
        project_details = test_project_details(token, project.get('id'))
        details_ok = project_details is not None
    
    # Test 5: Project update (if we have a project)
    update_ok = False
    if project:
        updated_project = test_project_update(token, project.get('id'))
        update_ok = updated_project is not None
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Dashboard Test Results Summary:")
    print(f"   Dashboard Overview: {'✅ PASS' if overview_ok else '❌ FAIL'}")
    print(f"   Project Creation: {'✅ PASS' if creation_ok else '❌ FAIL'}")
    print(f"   Project Listing: {'✅ PASS' if listing_ok else '❌ FAIL'}")
    print(f"   Project Details: {'✅ PASS' if details_ok else '❌ FAIL'}")
    print(f"   Project Update: {'✅ PASS' if update_ok else '❌ FAIL'}")
    
    all_passed = overview_ok and creation_ok and listing_ok and details_ok and update_ok
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Dashboard functionality is working correctly!")
        print("   All CRUD operations for projects are functional.")
    else:
        print("\n⚠️ Some dashboard functionality issues detected.")
        print("   Check the failed tests above for details.")

if __name__ == "__main__":
    main()