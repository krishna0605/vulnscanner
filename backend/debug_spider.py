#!/usr/bin/env python3
"""Debug script to test WebSpider functionality."""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.spider import WebSpider
from schemas.dashboard import ScanConfigurationSchema

async def test_spider():
    """Test spider functionality."""
    config = ScanConfigurationSchema(
        max_depth=3,
        max_pages=100,
        requests_per_second=10,
        timeout=30,
        follow_redirects=True,
        respect_robots=True,
        user_agent="Test-Spider/1.0"
    )
    
    spider = WebSpider(config)
    
    try:
        # Test basic functionality
        print("Testing spider initialization...")
        print(f"Config: {spider.config}")
        print(f"Session: {spider.session}")
        print(f"Rate limiter: {spider.rate_limiter}")
        print(f"Robots cache: {spider.robots_cache}")
        
        # Test session creation
        print("\nTesting session creation...")
        await spider._ensure_session()
        print(f"Session created: {spider.session}")
        print(f"Session timeout: {spider.session.timeout}")
        
        # Test a simple request to httpbin.org (which should work)
        print("\nTesting simple request...")
        url = "https://httpbin.org/status/200"
        response = await spider.fetch_url(url)
        print(f"Response: {response}")
        
        # Test 404 response
        print("\nTesting 404 response...")
        url = "https://httpbin.org/status/404"
        response = await spider.fetch_url(url)
        print(f"404 Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await spider.close()

if __name__ == "__main__":
    asyncio.run(test_spider())