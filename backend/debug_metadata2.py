#!/usr/bin/env python3
"""
Debug script to test the exact same imports as manage_db.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing exact imports from manage_db.py...")

try:
    print("1. Testing core.config...")
    print("✓ core.config imported successfully")
except Exception as e:
    print(f"✗ core.config failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Testing db.init_database...")
    print("✓ db.init_database imported successfully")
except Exception as e:
    print(f"✗ db.init_database failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing db.versioning...")
    print("✓ db.versioning imported successfully")
except Exception as e:
    print(f"✗ db.versioning failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing migrations.migrate_to_unified_schema...")
    print("✓ migrations.migrate_to_unified_schema imported successfully")
except Exception as e:
    print(f"✗ migrations.migrate_to_unified_schema failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All imports successful!")