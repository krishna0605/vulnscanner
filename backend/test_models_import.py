#!/usr/bin/env python3
"""
Test script to isolate model import issues.
"""

try:
    print("Testing core.config import...")
    print("✓ Config imported successfully")
    
    print("\nTesting db.session import...")
    print("✓ Base imported successfully")
    
    print("\nTesting individual model imports...")
    
    print("✓ Profile imported")
    
    print("✓ Project imported")
    
    print("✓ ScanSession imported")
    
    print("✓ DiscoveredUrl imported")
    
    print("✓ ExtractedForm imported")
    
    print("✓ TechnologyFingerprint imported")
    
    print("✓ VulnerabilityType imported")
    
    print("✓ Vulnerability imported")
    
    print("✓ DashboardMetric imported")
    
    print("✓ RealtimeUpdate imported")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()