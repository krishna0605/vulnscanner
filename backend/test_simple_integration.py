"""Simple integration test to debug async client issues."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from main import app


@pytest_asyncio.fixture
async def simple_client():
    """Simple test client."""
    # Try using transport instead of app parameter
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_simple_endpoint(simple_client):
    """Test a simple endpoint."""
    response = await simple_client.get("/api/auth/dev-test")
    assert response.status_code == 200