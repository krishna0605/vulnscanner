#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, and_
from db.session import get_db
from models.unified_models import ScanSession, Project

async def debug_join_issue():
    """Debug the join issue in list_scan_urls"""
    
    scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
    user_id = "44f6c96c-d525-4dbd-8a7a-7a10995526b5"
    
    async for session in get_db():
        print("=== DEBUGGING JOIN ISSUE ===")
        
        # Test 1: Check if scan exists
        scan_query = select(ScanSession).where(ScanSession.id == scan_id)
        result = await session.execute(scan_query)
        scan = result.scalar_one_or_none()
        print(f"1. Scan exists: {scan is not None}")
        if scan:
            print(f"   Scan project_id: {scan.project_id}")
        
        # Test 2: Check if project exists and owner matches
        if scan:
            project_query = select(Project).where(Project.id == scan.project_id)
            result = await session.execute(project_query)
            project = result.scalar_one_or_none()
            print(f"2. Project exists: {project is not None}")
            if project:
                print(f"   Project owner_id: {project.owner_id}")
                print(f"   User_id: {user_id}")
                print(f"   Owner matches: {project.owner_id == user_id}")
        
        # Test 3: Try the original query with implicit join
        print("\n3. Testing original query with implicit join:")
        try:
            scan_query = (
                select(ScanSession)
                .join(Project)
                .where(
                    and_(
                        ScanSession.id == scan_id,
                        Project.owner_id == user_id
                    )
                )
            )
            print(f"   Query: {scan_query}")
            result = await session.execute(scan_query)
            scan = result.scalar_one_or_none()
            print(f"   Result: {scan is not None}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Try with explicit join condition
        print("\n4. Testing with explicit join condition:")
        try:
            scan_query = (
                select(ScanSession)
                .join(Project, ScanSession.project_id == Project.id)
                .where(
                    and_(
                        ScanSession.id == scan_id,
                        Project.owner_id == user_id
                    )
                )
            )
            print(f"   Query: {scan_query}")
            result = await session.execute(scan_query)
            scan = result.scalar_one_or_none()
            print(f"   Result: {scan is not None}")
        except Exception as e:
            print(f"   Error: {e}")
        
        break

if __name__ == "__main__":
    asyncio.run(debug_join_issue())