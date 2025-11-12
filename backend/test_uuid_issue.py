#!/usr/bin/env python3

import asyncio
from sqlalchemy import select
from db.session import get_db
from models.unified_models import ScanSession

async def test_uuid_handling():
    """Test UUID parameter handling in SQLite"""
    
    scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
    user_id = "44f6c96c-d525-4dbd-8a7a-7a10995526b5"
    
    async for db in get_db():
        print(f"Testing with scan_id: {scan_id}")
        print(f"Testing with user_id: {user_id}")
        print()
        
        # Test 1: Direct scan lookup
        print("1. Direct scan lookup...")
        direct_query = select(ScanSession).where(ScanSession.id == scan_id)
        direct_result = await db.execute(direct_query)
        direct_scan = direct_result.scalar_one_or_none()
        
        if direct_scan:
            print(f"   ✓ Direct scan found: {direct_scan.id}")
        else:
            print("   ✗ Direct scan not found")
        
        print()
        
        # Test 2: Check what's actually in the database
        print("2. Checking all scan IDs in database...")
        all_scans_query = select(ScanSession.id)
        all_scans_result = await db.execute(all_scans_query)
        all_scan_ids = [row[0] for row in all_scans_result.fetchall()]
        
        print(f"   Found {len(all_scan_ids)} scans:")
        for scan_id_db in all_scan_ids:
            print(f"     - {scan_id_db} (type: {type(scan_id_db)})")
            if scan_id_db == scan_id:
                print("       ✓ MATCHES our target scan_id")
        
        print()
        
        # Test 3: Test parameter binding
        print("3. Testing parameter binding...")
        param_query = select(ScanSession).where(ScanSession.id == scan_id)
        compiled = param_query.compile(compile_kwargs={"literal_binds": True})
        print(f"   Compiled SQL: {compiled}")
        
        print()
        
        # Test 4: Test with explicit string conversion
        print("4. Testing with explicit string conversion...")
        str_query = select(ScanSession).where(ScanSession.id == str(scan_id))
        str_result = await db.execute(str_query)
        str_scan = str_result.scalar_one_or_none()
        
        if str_scan:
            print(f"   ✓ String conversion scan found: {str_scan.id}")
        else:
            print("   ✗ String conversion scan not found")
        
        break

if __name__ == "__main__":
    asyncio.run(test_uuid_handling())