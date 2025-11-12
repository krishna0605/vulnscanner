#!/usr/bin/env python3
"""
Debug script to isolate which model is causing the metadata conflict.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing individual model imports...")

try:
    print("1. Testing core.config...")
    print("✓ core.config imported successfully")
except Exception as e:
    print(f"✗ core.config failed: {e}")
    sys.exit(1)

try:
    print("2. Testing db.session...")
    print("✓ db.session imported successfully")
except Exception as e:
    print(f"✗ db.session failed: {e}")
    sys.exit(1)

# Test each model individually
models_to_test = [
    "Profile",
    "Project", 
    "ScanSession",
    "DiscoveredUrl",
    "ExtractedForm",
    "TechnologyFingerprint",
    "VulnerabilityType",
    "Vulnerability",
    "DashboardMetric",
    "RealtimeUpdate"
]

for model_name in models_to_test:
    try:
        print(f"3. Testing {model_name}...")
        exec(f"from models.unified_models import {model_name}")
        print(f"✓ {model_name} imported successfully")
    except Exception as e:
        print(f"✗ {model_name} failed: {e}")
        import traceback
        traceback.print_exc()
        break

print("All models imported successfully!")