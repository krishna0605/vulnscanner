#!/usr/bin/env python3
"""
Debug script to test login endpoint and see actual response.
"""

import asyncio
import json
from httpx import AsyncClient, ASGITransport
from main import app

async def test_login_debug():
    """Test login endpoint to see actual response."""
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        print("🧪 Testing login endpoint...")
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except Exception as e:
            print(f"Failed to parse JSON: {e}")

if __name__ == "__main__":
    asyncio.run(test_login_debug())