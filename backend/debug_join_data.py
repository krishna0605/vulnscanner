#!/usr/bin/env python3

import asyncio
from sqlalchemy import select, text
from db.session import get_db
from models import ScanSession, Project

async def debug_join_data():
    """Debug the actual data to understand why the join is failing."""
    
    scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
    user_id = "44f6c96c-d525-4dbd-8a7a-7a10995526b5"
    
    async for db in get_db():
        print("=== DEBUGGING JOIN DATA ===")
        print(f"scan_id: {scan_id}")
        print(f"user_id: {user_id}")
        print()
        
        # 1. Check if scan session exists
        print("1. Checking if scan session exists...")
        scan_query = select(ScanSession).where(ScanSession.id == scan_id)
        scan_result = await db.execute(scan_query)
        scan = scan_result.scalar_one_or_none()
        
        if scan:
            print("   ✓ Scan session found:")
            print(f"     - ID: {scan.id}")
            print(f"     - Project ID: {scan.project_id}")
            print(f"     - Created by: {scan.created_by}")
            print(f"     - Status: {scan.status}")
        else:
            print("   ✗ Scan session NOT found")
            return
        
        print()
        
        # 2. Check if project exists
        print("2. Checking if project exists...")
        project_query = select(Project).where(Project.id == scan.project_id)
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()
        
        if project:
            print("   ✓ Project found:")
            print(f"     - ID: {project.id}")
            print(f"     - Name: {project.name}")
            print(f"     - Owner ID: {project.owner_id}")
        else:
            print("   ✗ Project NOT found")
            return
        
        print()
        
        # 3. Check ownership
        print("3. Checking ownership...")
        print(f"   Project owner_id: {project.owner_id}")
        print(f"   Expected user_id: {user_id}")
        print(f"   Match: {project.owner_id == user_id}")
        
        print()
        
        # 4. Test the exact join query
        print("4. Testing the exact join query...")
        join_query = (
            select(ScanSession)
            .join(Project)
            .where(
                ScanSession.id == scan_id
            )
        )
        join_result = await db.execute(join_query)
        join_scan = join_result.scalar_one_or_none()
        
        if join_scan:
            print("   ✓ Join query successful")
        else:
            print("   ✗ Join query failed")
        
        print()
        
        # 5. Test the join query with ownership filter (comma-separated)
        print("5. Testing join query with ownership filter (comma-separated)...")
        ownership_query = (
            select(ScanSession)
            .join(Project)
            .where(
                ScanSession.id == scan_id,
                Project.owner_id == user_id
            )
        )
        ownership_result = await db.execute(ownership_query)
        ownership_scan = ownership_result.scalar_one_or_none()
        
        if ownership_scan:
            print("   ✓ Ownership query (comma-separated) successful")
        else:
            print("   ✗ Ownership query (comma-separated) failed")
        
        print()
        
        # 5b. Test the join query with ownership filter using and_() - EXACT API REPLICA
        print("5b. Testing join query with ownership filter using and_() - EXACT API REPLICA...")
        from sqlalchemy import and_
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
        api_result = await db.execute(api_query)
        api_scan = api_result.scalar_one_or_none()
        
        if api_scan:
            print("   ✓ API-style query (and_) successful")
        else:
            print("   ✗ API-style query (and_) failed")
        
        print(f"   Query SQL: {api_query}")
        print(f"   Query result: {api_scan}")
        
        print()
        
        # 6. Check the relationship between scan and project
        print("6. Checking scan.project_id vs project.id...")
        print(f"   scan.project_id: {scan.project_id} (type: {type(scan.project_id)})")
        print(f"   project.id: {project.id} (type: {type(project.id)})")
        print(f"   Equal: {scan.project_id == project.id}")
        
        # 7. Raw SQL query to debug
        print()
        print("7. Raw SQL query...")
        raw_query = text("""
            SELECT s.id as scan_id, s.project_id as scan_project_id, 
                   p.id as project_id, p.owner_id as project_owner_id
            FROM scan_sessions s
            LEFT JOIN projects p ON s.project_id = p.id
            WHERE s.id = :scan_id
        """)
        raw_result = await db.execute(raw_query, {"scan_id": scan_id})
        raw_row = raw_result.fetchone()
        
        if raw_row:
            print("   Raw query result:")
            print(f"     - scan_id: {raw_row.scan_id}")
            print(f"     - scan_project_id: {raw_row.scan_project_id}")
            print(f"     - project_id: {raw_row.project_id}")
            print(f"     - project_owner_id: {raw_row.project_owner_id}")
        else:
            print("   Raw query returned no results")
        
        break

if __name__ == "__main__":
    asyncio.run(debug_join_data())