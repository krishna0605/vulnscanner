#!/usr/bin/env python3
"""
Create test data for the SQLite database.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from db.session import async_session
from models.sqlite_models import User, Project, ScanSession, DiscoveredUrl, ScanStatus

async def create_test_data():
    """Create test data for development."""
    print("🚀 Creating test data...")
    
    async with async_session() as db:
        try:
            # Use existing test user with ID 1
            test_user_id = 1
            
            # Create test projects
            project1 = Project(
                name="Example Website Scan",
                description="Security scan of example.com",
                owner_id=test_user_id,
                target_domain="example.com",
                scope_rules='["https://example.com/*"]'
            )
            
            project2 = Project(
                name="Test Application",
                description="Internal application security assessment",
                owner_id=test_user_id,
                target_domain="testapp.local",
                scope_rules='["https://testapp.local/*"]'
            )
            
            db.add(project1)
            db.add(project2)
            await db.flush()  # Get the project IDs
            
            # Create test scan sessions
            scan1 = ScanSession(
                project_id=project1.id,
                status=ScanStatus.COMPLETED.value,
                start_time=datetime.utcnow() - timedelta(hours=2),
                end_time=datetime.utcnow() - timedelta(hours=1),
                configuration='{"max_depth": 3, "max_pages": 100}',
                stats='{"urls_found": 25, "forms_found": 3, "technologies": 5}',
                created_by=test_user_id
            )
            
            scan2 = ScanSession(
                project_id=project1.id,
                status=ScanStatus.RUNNING.value,
                start_time=datetime.utcnow() - timedelta(minutes=30),
                configuration='{"max_depth": 5, "max_pages": 500}',
                stats='{"urls_found": 12, "forms_found": 1, "technologies": 3}',
                created_by=test_user_id
            )
            
            scan3 = ScanSession(
                project_id=project2.id,
                status=ScanStatus.COMPLETED.value,
                start_time=datetime.utcnow() - timedelta(days=1),
                end_time=datetime.utcnow() - timedelta(days=1, hours=-2),
                configuration='{"max_depth": 2, "max_pages": 50}',
                stats='{"urls_found": 15, "forms_found": 2, "technologies": 4}',
                created_by=test_user_id
            )
            
            db.add(scan1)
            db.add(scan2)
            db.add(scan3)
            await db.flush()  # Get the scan IDs
            
            # Create test discovered URLs
            urls = [
                DiscoveredUrl(
                    session_id=scan1.id,
                    url="https://example.com/",
                    method="GET",
                    status_code=200,
                    content_type="text/html",
                    content_length=1024,
                    response_time=150,
                    page_title="Example Domain"
                ),
                DiscoveredUrl(
                    session_id=scan1.id,
                    url="https://example.com/about",
                    method="GET",
                    status_code=200,
                    content_type="text/html",
                    content_length=2048,
                    response_time=200,
                    page_title="About Us"
                ),
                DiscoveredUrl(
                    session_id=scan1.id,
                    url="https://example.com/contact",
                    method="GET",
                    status_code=200,
                    content_type="text/html",
                    content_length=1536,
                    response_time=180,
                    page_title="Contact Us"
                ),
                DiscoveredUrl(
                    session_id=scan2.id,
                    url="https://example.com/login",
                    method="GET",
                    status_code=200,
                    content_type="text/html",
                    content_length=1200,
                    response_time=120,
                    page_title="Login"
                ),
            ]
            
            for url in urls:
                db.add(url)
            
            await db.commit()
            print("✅ Test data created successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating test data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(create_test_data())