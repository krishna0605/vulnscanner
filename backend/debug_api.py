#!/usr/bin/env python3
"""
Debug script to test the API directly
"""

import asyncio
from httpx import AsyncClient
from main import app

async def test_api():
    from httpx import ASGITransport
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("Testing API directly...")
        
        # Test without auth first
        response = await client.get("/api/v1/projects")
        print(f"No auth - Status: {response.status_code}")
        print(f"No auth - Response: {response.text}")
        
        # Test with fake auth header
        headers = {"Authorization": "Bearer fake-token"}
        response = await client.get("/api/v1/projects", headers=headers)
        print(f"With fake auth - Status: {response.status_code}")
        print(f"With fake auth - Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_api())