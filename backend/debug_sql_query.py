#!/usr/bin/env python3

import asyncio
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models.unified_models import ScanSession, Project

async def test_scan_query():
    """Test the exact SQL query used in list_scan_urls"""
    
    # Database setup
    DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
    engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True to see SQL
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
    user_id = "44f6c96c-d525-4dbd-8a7a-7a10995526b5"
    
    async with async_session() as db:
        print("=== TESTING ORIGINAL QUERY (implicit join) ===")
        try:
            # Original query from the code
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
            
            print(f"Query: {scan_query}")
            scan_result = await db.execute(scan_query)
            scan = scan_result.scalar_one_or_none()
            print(f"Result: {scan}")
            
        except Exception as e:
            print(f"Error with implicit join: {e}")
        
        print("\n=== TESTING EXPLICIT JOIN ===")
        try:
            # Explicit join condition
            scan_query_explicit = (
                select(ScanSession)
                .join(Project, ScanSession.project_id == Project.id)
                .where(
                    and_(
                        ScanSession.id == scan_id,
                        Project.owner_id == user_id
                    )
                )
            )
            
            print(f"Query: {scan_query_explicit}")
            scan_result = await db.execute(scan_query_explicit)
            scan = scan_result.scalar_one_or_none()
            print(f"Result: {scan}")
            
        except Exception as e:
            print(f"Error with explicit join: {e}")
        
        print("\n=== TESTING SIMPLE QUERY ===")
        try:
            # Simple query without join - just check if scan exists
            simple_query = select(ScanSession).where(ScanSession.id == scan_id)
            scan_result = await db.execute(simple_query)
            scan = scan_result.scalar_one_or_none()
            print(f"Scan exists: {scan is not None}")
            if scan:
                print(f"Scan project_id: {scan.project_id}")
                
                # Now check project ownership
                project_query = select(Project).where(
                    and_(
                        Project.id == scan.project_id,
                        Project.owner_id == user_id
                    )
                )
                project_result = await db.execute(project_query)
                project = project_result.scalar_one_or_none()
                print(f"Project owned by user: {project is not None}")
                
        except Exception as e:
            print(f"Error with simple query: {e}")

if __name__ == "__main__":
    asyncio.run(test_scan_query())