#!/usr/bin/env python3

import asyncio
from sqlalchemy import select, and_
from db.session import get_db
from models.unified_models import ScanSession, Project

async def test_join_issue():
    """Test the specific join query that's failing"""
    
    scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
    user_id = "44f6c96c-d525-4dbd-8a7a-7a10995526b5"
    
    async for db in get_db():
        print(f"Testing join with scan_id: {scan_id}")
        print(f"Testing join with user_id: {user_id}")
        print()
        
        # Test 1: The exact failing query from the API
        print("1. Testing the exact API query...")
        api_query = (
            select(ScanSession)
            .join(Project)
            .where(
                and_(
                    ScanSession.id == scan_id,
                    Project.owner_id == user_id
                )
            )
        )
        
        # Show compiled SQL
        compiled = api_query.compile(compile_kwargs={"literal_binds": True})
        print(f"   Compiled SQL: {compiled}")
        
        api_result = await db.execute(api_query)
        api_scan = api_result.scalar_one_or_none()
        
        if api_scan:
            print(f"   ✓ API query successful: {api_scan.id}")
        else:
            print("   ✗ API query failed")
        
        print()
        
        # Test 2: Check if the scan exists
        print("2. Checking if scan exists...")
        scan_query = select(ScanSession).where(ScanSession.id == scan_id)
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if scan:
            print(f"   ✓ Scan exists: {scan.id}, project_id: {scan.project_id}")
        else:
            print("   ✗ Scan does not exist")
            return
        
        print()
        
        # Test 3: Check if the project exists and ownership
        print("3. Checking project and ownership...")
        project_query = select(Project).where(Project.id == scan.project_id)
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()
        
        if project:
            print(f"   ✓ Project exists: {project.id}, owner_id: {project.owner_id}")
            print(f"   User ID matches: {project.owner_id == user_id}")
        else:
            print("   ✗ Project does not exist")
            return
        
        print()
        
        # Test 4: Test join without where clause
        print("4. Testing join without where clause...")
        join_query = select(ScanSession).join(Project)
        join_result = await db.execute(join_query)
        join_scans = join_result.scalars().all()
        
        print(f"   Found {len(join_scans)} scans in join:")
        for s in join_scans:
            print(f"     - {s.id}")
        
        print()
        
        # Test 5: Test with separate where conditions
        print("5. Testing with separate where conditions...")
        separate_query = (
            select(ScanSession)
            .join(Project)
            .where(ScanSession.id == scan_id)
            .where(Project.owner_id == user_id)
        )
        
        separate_result = await db.execute(separate_query)
        separate_scan = separate_result.scalar_one_or_none()
        
        if separate_scan:
            print(f"   ✓ Separate where conditions successful: {separate_scan.id}")
        else:
            print("   ✗ Separate where conditions failed")
        
        print()
        
        # Test 6: Test with explicit join condition
        print("6. Testing with explicit join condition...")
        explicit_query = (
            select(ScanSession)
            .join(Project, ScanSession.project_id == Project.id)
            .where(
                and_(
                    ScanSession.id == scan_id,
                    Project.owner_id == user_id
                )
            )
        )
        
        explicit_result = await db.execute(explicit_query)
        explicit_scan = explicit_result.scalar_one_or_none()
        
        if explicit_scan:
            print(f"   ✓ Explicit join successful: {explicit_scan.id}")
        else:
            print("   ✗ Explicit join failed")
        
        break

if __name__ == "__main__":
    asyncio.run(test_join_issue())