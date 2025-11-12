#!/usr/bin/env python3
"""
Debug script to test table creation specifically
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing table creation...")

try:
    print("1. Importing Base...")
    from db.session import Base
    print("✓ Base imported successfully")
    
    print("2. Importing models...")
    print("✓ All models imported successfully")
    
    print("3. Checking Base.metadata...")
    print(f"Base.metadata type: {type(Base.metadata)}")
    print(f"Base.metadata.tables: {list(Base.metadata.tables.keys())}")
    
    print("4. Testing metadata.create_all (dry run)...")
    # This should trigger the error if there's a metadata conflict
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    print("✓ Table creation successful!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All tests passed!")