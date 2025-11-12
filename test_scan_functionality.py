#!/usr/bin/env python3
"""
Test script to verify that the scan functionality is working properly.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.schemas.dashboard import ScanConfigurationSchema
from backend.crawler.spider import WebSpider


async def test_scan_functionality():
    """Test the scan functionality with a simple example."""
    print("Testing scan functionality...")
    
    # Create a simple scan configuration
    config = ScanConfigurationSchema(
        max_depth=1,
        max_pages=10,
        requests_per_second=5,
        timeout=30,
        authentication=None
    )
    
    # Test the spider initialization
    print("Testing spider initialization...")
    try:
        spider = WebSpider(config)
        await spider.initialize()
        print("✓ Spider initialization successful")
        
        # Test fetching a simple URL
        print("Testing URL fetch...")
        response = await spider.fetch_url("https://httpbin.org/get")
        if response:
            print("✓ URL fetch successful")
            print(f"  Status code: {response.get('status_code')}")
            print(f"  Content type: {response.get('content_type')}")
        else:
            print("✗ URL fetch failed")
            
        await spider.close()
        
    except Exception as e:
        print(f"✗ Spider test failed: {e}")
        return False
    
    print("Scan functionality test completed.")
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_scan_functionality())
        if result:
            print("\n✓ All tests passed! Scan functionality appears to be working.")
        else:
            print("\n✗ Some tests failed. Please check the output above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)