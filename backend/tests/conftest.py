"""
Pytest configuration and shared fixtures for the VulnScanner test suite.
"""

import asyncio
import os
import pytest
import pytest_asyncio
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import delete

# Add backend to path
import sys
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from main import app  # noqa: E402
from db.session import get_db  # noqa: E402
from models.unified_models import Base, Profile, Project, ScanSession, DiscoveredUrl  # noqa: E402


# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with proper cleanup."""
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            # Clean up all data after each test
            await session.rollback()
            
            # Delete all data from tables to ensure clean state
            from models.unified_models import (
                TechnologyFingerprint, ExtractedForm, DiscoveredUrl, 
                ScanSession, Project, Profile
            )
            
            # Delete in reverse dependency order
            for model in [TechnologyFingerprint, ExtractedForm, DiscoveredUrl, 
                         ScanSession, Project, Profile]:
                await session.execute(delete(model))
            
            await session.commit()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with database dependency override."""
    from httpx import ASGITransport
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, test_user: dict) -> AsyncClient:
    """Create an authenticated test client."""
    
    # Import all possible get_current_user functions
    try:
        from core.auth_deps import get_current_user as core_get_current_user, get_user_id
    except ImportError:
        core_get_current_user = None
        get_user_id = None
    
    try:
        from api.deps import get_current_user as api_get_current_user
    except ImportError:
        api_get_current_user = None
    
    async def override_get_current_user():
        return test_user
    
    async def override_get_user_id():
        return test_user["id"]
    
    # Override all possible get_current_user dependencies from different modules
    if core_get_current_user:
        app.dependency_overrides[core_get_current_user] = override_get_current_user
    if api_get_current_user:
        app.dependency_overrides[api_get_current_user] = override_get_current_user
    if get_user_id:
        app.dependency_overrides[get_user_id] = override_get_user_id
    
    yield client
    
    # Remove overrides
    overrides_to_remove = []
    if core_get_current_user:
        overrides_to_remove.append(core_get_current_user)
    if api_get_current_user:
        overrides_to_remove.append(api_get_current_user)
    if get_user_id:
        overrides_to_remove.append(get_user_id)
    
    for override in overrides_to_remove:
        if override in app.dependency_overrides:
            del app.dependency_overrides[override]


@pytest.fixture
def test_user() -> dict:
    """Create a test user with unique values."""
    import time
    unique_id = str(uuid4())
    timestamp = str(int(time.time() * 1000))  # millisecond timestamp
    return {
        "id": unique_id,
        "email": f"test-{unique_id[:8]}-{timestamp}@example.com",
        "full_name": f"Test User {unique_id[:8]}",
        "is_active": True,
        "role": "user"
    }


@pytest_asyncio.fixture
async def test_profile(db_session: AsyncSession, test_user: dict) -> Profile:
    """Create a test user profile in the database."""
    profile = Profile(
        id=test_user["id"],
        email=test_user["email"],
        full_name=test_user["full_name"],
        is_active=test_user["is_active"],
        role=test_user["role"]
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_profile: Profile) -> Project:
    """Create a test project in the database."""
    unique_suffix = str(uuid4())[:8]
    project = Project(
        name=f"Test Project {unique_suffix}",
        description="A test project for unit testing",
        owner_id=test_profile.id,
        target_domain="example.com",
        scope_rules=["https://example.com/*"]
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_scan_session(db_session: AsyncSession, test_project: Project) -> ScanSession:
    """Create a test scan session in the database."""
    scan = ScanSession(
        project_id=test_project.id,
        status="pending",
        configuration={
            "max_depth": 3,
            "max_pages": 100,
            "requests_per_second": 10
        },
        created_by=test_project.owner_id
    )
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)
    return scan


@pytest_asyncio.fixture
async def test_discovered_url(db_session: AsyncSession, test_scan_session: ScanSession) -> DiscoveredUrl:
    """Create a test discovered URL in the database."""
    unique_suffix = str(uuid4())[:8]
    url = DiscoveredUrl(
        session_id=test_scan_session.id,
        url=f"https://example.com/test-page-{unique_suffix}",
        parent_url=f"https://example.com/parent-{unique_suffix}",
        method="GET",
        status_code=200,
        content_type="text/html",
        content_length=1024,
        response_time=150,
        page_title=f"Test Page {unique_suffix}"
    )
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)
    return url


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = MagicMock()
    mock_client.auth.get_user.return_value = {
        "id": "test-user-id",
        "email": "test@example.com",
        "user_metadata": {"full_name": "Test User"}
    }
    return mock_client


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    return mock_redis


@pytest.fixture
def mock_celery_task():
    """Create a mock Celery task."""
    mock_task = MagicMock()
    mock_task.delay.return_value.id = "test-task-id"
    mock_task.delay.return_value.status = "PENDING"
    return mock_task


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    
    # Cleanup
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_project_data(**kwargs):
        """Create project test data."""
        default_data = {
            "name": "Test Project",
            "description": "A test project",
            "target_domain": "example.com",
            "scope_rules": ["https://example.com/*"]
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_scan_config(**kwargs):
        """Create scan configuration test data."""
        default_config = {
            "max_depth": 3,
            "max_pages": 100,
            "requests_per_second": 10,
            "timeout": 30,
            "follow_redirects": True,
            "respect_robots": True,
            "user_agent": "VulnScanner-Test/1.0"
        }
        default_config.update(kwargs)
        return default_config
    
    @staticmethod
    def create_discovered_url_data(**kwargs):
        """Create discovered URL test data."""
        default_data = {
            "url": "https://example.com/test",
            "method": "GET",
            "status_code": 200,
            "content_type": "text/html",
            "content_length": 1024,
            "response_time": 150,
            "page_title": "Test Page"
        }
        default_data.update(kwargs)
        return default_data


@pytest.fixture
def test_data_factory():
    """Provide the test data factory."""
    return TestDataFactory


# Async test helpers
async def async_test_helper(coro):
    """Helper for running async tests."""
    return await coro


# Mock HTTP responses for crawler tests
@pytest.fixture
def mock_http_responses():
    """Mock HTTP responses for crawler testing."""
    return {
        "https://example.com": {
            "status": 200,
            "headers": {"Content-Type": "text/html"},
            "text": """
            <html>
                <head><title>Example Site</title></head>
                <body>
                    <a href="/page1">Page 1</a>
                    <a href="/page2">Page 2</a>
                    <form action="/submit" method="post">
                        <input type="text" name="username">
                        <input type="password" name="password">
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
            """
        },
        "https://example.com/page1": {
            "status": 200,
            "headers": {"Content-Type": "text/html"},
            "text": "<html><head><title>Page 1</title></head><body><h1>Page 1</h1></body></html>"
        },
        "https://example.com/page2": {
            "status": 200,
            "headers": {"Content-Type": "text/html"},
            "text": "<html><head><title>Page 2</title></head><body><h1>Page 2</h1></body></html>"
        }
    }