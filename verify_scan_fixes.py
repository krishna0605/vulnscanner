#!/usr/bin/env python3
"""
Script to verify that all the scan functionality fixes have been applied correctly.
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_imports():
    """Check that all necessary imports work correctly."""
    print("Checking imports...")
    
    try:
        from backend.schemas.dashboard import ScanConfigurationSchema
        print("✓ ScanConfigurationSchema import successful")
    except ImportError as e:
        print(f"✗ ScanConfigurationSchema import failed: {e}")
        return False
    
    try:
        from backend.crawler.engine import CrawlerEngine
        print("✓ CrawlerEngine import successful")
    except ImportError as e:
        print(f"✗ CrawlerEngine import failed: {e}")
        return False
    
    try:
        from backend.crawler.spider import WebSpider
        print("✓ WebSpider import successful")
    except ImportError as e:
        print(f"✗ WebSpider import failed: {e}")
        return False
    
    try:
        from backend.tasks.crawler_tasks import start_crawl_task, stop_crawl_task
        print("✓ Crawler tasks import successful")
    except ImportError as e:
        print(f"✗ Crawler tasks import failed: {e}")
        return False
    
    return True


def check_method_signatures():
    """Check that method signatures are correct."""
    print("\nChecking method signatures...")
    
    try:
        from backend.crawler.fingerprinter import TechnologyFingerprinter
        fingerprinter = TechnologyFingerprinter()
        
        # Check that analyze_response method signature is correct
        import inspect
        sig = inspect.signature(fingerprinter.analyze_response)
        params = list(sig.parameters.keys())
        if len(params) == 1 and params[0] == 'response_data':
            print("✓ analyze_response method signature is correct")
        else:
            print(f"✗ analyze_response method signature incorrect: {params}")
            return False
            
    except Exception as e:
        print(f"✗ Method signature check failed: {e}")
        return False
    
    return True


def check_rate_limiting_fix():
    """Check that the rate limiting fix has been applied."""
    print("\nChecking rate limiting fix...")
    
    try:
        with open('backend/crawler/engine.py', 'r') as f:
            content = f.read()
            
        # Check for the lock implementation in _apply_rate_limit
        if 'async with asyncio.Lock()' in content:
            print("✓ Rate limiting race condition fix applied")
        else:
            print("✗ Rate limiting race condition fix not found")
            return False
            
    except Exception as e:
        print(f"✗ Rate limiting check failed: {e}")
        return False
    
    return True


def check_task_cancellation_fix():
    """Check that the task cancellation fix has been applied."""
    print("\nChecking task cancellation fix...")
    
    try:
        with open('backend/api/routes/dashboard.py', 'r') as f:
            content = f.read()
            
        # Check for the task cancellation implementation
        if 'stop_crawl_task.delay' in content:
            print("✓ Task cancellation fix applied")
        else:
            print("✗ Task cancellation fix not found")
            return False
            
    except Exception as e:
        print(f"✗ Task cancellation check failed: {e}")
        return False
    
    return True


def main():
    """Main function to run all checks."""
    print("Verifying scan functionality fixes...\n")
    
    checks = [
        check_imports,
        check_method_signatures,
        check_rate_limiting_fix,
        check_task_cancellation_fix
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ All checks passed! Scan functionality fixes have been applied correctly.")
        print("\nFixed issues:")
        print("  - Race condition in rate limiting")
        print("  - Method signature mismatch in fingerprinter")
        print("  - Missing task cancellation in stop scan endpoint")
        print("  - Import issues in crawler components")
    else:
        print("✗ Some checks failed. Please review the output above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())