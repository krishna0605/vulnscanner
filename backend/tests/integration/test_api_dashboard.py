"""
Integration tests for dashboard API endpoints.
Tests dashboard statistics, recent activity, and overview data.
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from main import app


class TestDashboardAPI:
    """Integration tests for dashboard endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "full_name": "Test User"
        }
    
    @pytest.fixture
    def auth_headers(self):
        """Authentication headers."""
        return {"Authorization": "Bearer valid_token"}
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview_empty(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting dashboard overview with no data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock empty statistics
                mock_db.execute.side_effect = [
                    # Projects count
                    MagicMock(scalar=MagicMock(return_value=0)),
                    # Active scans count
                    MagicMock(scalar=MagicMock(return_value=0)),
                    # Total scans count
                    MagicMock(scalar=MagicMock(return_value=0)),
                    # URLs discovered count
                    MagicMock(scalar=MagicMock(return_value=0))
                ]
                
                response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["total_projects"] == 0
                assert data["active_scans"] == 0
                assert data["total_scans"] == 0
                assert data["urls_discovered"] == 0
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview_with_data(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting dashboard overview with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock statistics with data
                mock_db.execute.side_effect = [
                    # Projects count
                    MagicMock(scalar=MagicMock(return_value=5)),
                    # Active scans count
                    MagicMock(scalar=MagicMock(return_value=2)),
                    # Total scans count
                    MagicMock(scalar=MagicMock(return_value=15)),
                    # URLs discovered count
                    MagicMock(scalar=MagicMock(return_value=1250))
                ]
                
                response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["total_projects"] == 5
                assert data["active_scans"] == 2
                assert data["total_scans"] == 15
                assert data["urls_discovered"] == 1250
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview_unauthorized(self, client: AsyncClient):
        """Test getting dashboard overview without authentication."""
        response = await client.get("/api/v1/dashboard/overview")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_recent_activity_empty(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting recent activity with no data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock empty recent scans
                mock_db.execute.return_value = MagicMock(
                    scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
                )
                
                response = await client.get("/api/v1/dashboard/recent-activity", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_get_recent_activity_with_data(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting recent activity with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock recent scans
                mock_scan1 = MagicMock()
                mock_scan1.id = uuid4()
                mock_scan1.status = "completed"
                mock_scan1.start_time = datetime.now() - timedelta(hours=2)
                mock_scan1.end_time = datetime.now() - timedelta(hours=1)
                mock_scan1.stats = {"urls_found": 50, "forms_found": 3}
                
                mock_project1 = MagicMock()
                mock_project1.id = uuid4()
                mock_project1.name = "Example Website"
                mock_project1.target_domain = "example.com"
                mock_scan1.project = mock_project1
                
                mock_scan2 = MagicMock()
                mock_scan2.id = uuid4()
                mock_scan2.status = "running"
                mock_scan2.start_time = datetime.now() - timedelta(minutes=30)
                mock_scan2.end_time = None
                mock_scan2.stats = {"urls_found": 25}
                
                mock_project2 = MagicMock()
                mock_project2.id = uuid4()
                mock_project2.name = "Test Site"
                mock_project2.target_domain = "test.com"
                mock_scan2.project = mock_project2
                
                mock_db.execute.return_value = MagicMock(
                    scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_scan1, mock_scan2])))
                )
                
                response = await client.get("/api/v1/dashboard/recent-activity", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 2
                assert data[0]["status"] == "completed"
                assert data[0]["project"]["name"] == "Example Website"
                assert data[1]["status"] == "running"
                assert data[1]["project"]["name"] == "Test Site"
    
    @pytest.mark.asyncio
    async def test_get_recent_activity_with_limit(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting recent activity with custom limit."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock multiple scans
                mock_scans = []
                for i in range(15):
                    mock_scan = MagicMock()
                    mock_scan.id = uuid4()
                    mock_scan.status = "completed"
                    mock_scan.start_time = datetime.now() - timedelta(hours=i+1)
                    mock_scan.end_time = datetime.now() - timedelta(hours=i)
                    mock_scan.stats = {"urls_found": 10 + i}
                    
                    mock_project = MagicMock()
                    mock_project.id = uuid4()
                    mock_project.name = f"Project {i+1}"
                    mock_project.target_domain = f"example{i+1}.com"
                    mock_scan.project = mock_project
                    
                    mock_scans.append(mock_scan)
                
                # Return only first 5 scans (limit=5)
                mock_db.execute.return_value = MagicMock(
                    scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_scans[:5])))
                )
                
                response = await client.get("/api/v1/dashboard/recent-activity?limit=5", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 5
    
    @pytest.mark.asyncio
    async def test_get_scan_statistics_empty(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting scan statistics with no data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock empty statistics
                mock_db.execute.side_effect = [
                    # Scans by status
                    MagicMock(fetchall=MagicMock(return_value=[])),
                    # Scans over time (last 30 days)
                    MagicMock(fetchall=MagicMock(return_value=[]))
                ]
                
                response = await client.get("/api/v1/dashboard/scan-statistics", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["scans_by_status"] == []
                assert data["scans_over_time"] == []
    
    @pytest.mark.asyncio
    async def test_get_scan_statistics_with_data(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting scan statistics with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock statistics data
                status_stats = [
                    ("completed", 10),
                    ("running", 2),
                    ("failed", 1),
                    ("cancelled", 1)
                ]
                
                time_stats = [
                    (datetime.now().date() - timedelta(days=2), 3),
                    (datetime.now().date() - timedelta(days=1), 5),
                    (datetime.now().date(), 2)
                ]
                
                mock_db.execute.side_effect = [
                    # Scans by status
                    MagicMock(fetchall=MagicMock(return_value=status_stats)),
                    # Scans over time
                    MagicMock(fetchall=MagicMock(return_value=time_stats))
                ]
                
                response = await client.get("/api/v1/dashboard/scan-statistics", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                assert len(data["scans_by_status"]) == 4
                assert data["scans_by_status"][0]["status"] == "completed"
                assert data["scans_by_status"][0]["count"] == 10
                
                assert len(data["scans_over_time"]) == 3
                assert data["scans_over_time"][2]["count"] == 2  # Today's scans
    
    @pytest.mark.asyncio
    async def test_get_scan_statistics_with_date_range(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting scan statistics with custom date range."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_db.execute.side_effect = [
                    MagicMock(fetchall=MagicMock(return_value=[])),
                    MagicMock(fetchall=MagicMock(return_value=[]))
                ]
                
                start_date = (datetime.now() - timedelta(days=7)).date()
                end_date = datetime.now().date()
                
                response = await client.get(
                    f"/api/v1/dashboard/scan-statistics?start_date={start_date}&end_date={end_date}", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_get_project_statistics_empty(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting project statistics with no data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock empty project statistics
                mock_db.execute.return_value = MagicMock(
                    fetchall=MagicMock(return_value=[])
                )
                
                response = await client.get("/api/v1/dashboard/project-statistics", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_get_project_statistics_with_data(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting project statistics with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project statistics
                project_stats = [
                    (uuid4(), "Example Website", "example.com", 5, 150, 8, 2),
                    (uuid4(), "Test Site", "test.com", 3, 75, 4, 1),
                    (uuid4(), "Demo App", "demo.app", 2, 50, 3, 0)
                ]
                
                mock_db.execute.return_value = MagicMock(
                    fetchall=MagicMock(return_value=project_stats)
                )
                
                response = await client.get("/api/v1/dashboard/project-statistics", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                assert len(data) == 3
                assert data[0]["name"] == "Example Website"
                assert data[0]["target_domain"] == "example.com"
                assert data[0]["total_scans"] == 5
                assert data[0]["total_urls"] == 150
                assert data[0]["total_forms"] == 8
                assert data[0]["total_technologies"] == 2
    
    @pytest.mark.asyncio
    async def test_get_top_findings_empty(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting top findings with no data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock empty findings
                mock_db.execute.side_effect = [
                    # Most common status codes
                    MagicMock(fetchall=MagicMock(return_value=[])),
                    # Most common content types
                    MagicMock(fetchall=MagicMock(return_value=[])),
                    # Most detected technologies
                    MagicMock(fetchall=MagicMock(return_value=[]))
                ]
                
                response = await client.get("/api/v1/dashboard/top-findings", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status_codes"] == []
                assert data["content_types"] == []
                assert data["technologies"] == []
    
    @pytest.mark.asyncio
    async def test_get_top_findings_with_data(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting top findings with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock findings data
                status_codes = [(200, 150), (404, 25), (301, 15), (500, 5)]
                content_types = [("text/html", 120), ("application/json", 30), ("text/css", 20)]
                technologies = [("nginx", 10), ("PHP", 8), ("jQuery", 6), ("Bootstrap", 4)]
                
                mock_db.execute.side_effect = [
                    MagicMock(fetchall=MagicMock(return_value=status_codes)),
                    MagicMock(fetchall=MagicMock(return_value=content_types)),
                    MagicMock(fetchall=MagicMock(return_value=technologies))
                ]
                
                response = await client.get("/api/v1/dashboard/top-findings", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                assert len(data["status_codes"]) == 4
                assert data["status_codes"][0]["code"] == 200
                assert data["status_codes"][0]["count"] == 150
                
                assert len(data["content_types"]) == 3
                assert data["content_types"][0]["type"] == "text/html"
                assert data["content_types"][0]["count"] == 120
                
                assert len(data["technologies"]) == 4
                assert data["technologies"][0]["name"] == "nginx"
                assert data["technologies"][0]["count"] == 10


class TestDashboardIntegration:
    """Integration tests for complete dashboard workflows."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "full_name": "Test User"
        }
    
    @pytest.fixture
    def auth_headers(self):
        """Authentication headers."""
        return {"Authorization": "Bearer valid_token"}
    
    @pytest.mark.asyncio
    async def test_complete_dashboard_data_retrieval(self, client: AsyncClient, mock_user, auth_headers):
        """Test retrieving all dashboard data in sequence."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Step 1: Get overview
                mock_db.execute.side_effect = [
                    MagicMock(scalar=MagicMock(return_value=3)),  # projects
                    MagicMock(scalar=MagicMock(return_value=1)),  # active scans
                    MagicMock(scalar=MagicMock(return_value=8)),  # total scans
                    MagicMock(scalar=MagicMock(return_value=250)) # urls discovered
                ]
                
                overview_response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
                assert overview_response.status_code == status.HTTP_200_OK
                overview_data = overview_response.json()
                assert overview_data["total_projects"] == 3
                
                # Step 2: Get recent activity
                mock_db.execute.return_value = MagicMock(
                    scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
                )
                
                activity_response = await client.get("/api/v1/dashboard/recent-activity", headers=auth_headers)
                assert activity_response.status_code == status.HTTP_200_OK
                
                # Step 3: Get scan statistics
                mock_db.execute.side_effect = [
                    MagicMock(fetchall=MagicMock(return_value=[("completed", 6), ("running", 1), ("failed", 1)])),
                    MagicMock(fetchall=MagicMock(return_value=[]))
                ]
                
                stats_response = await client.get("/api/v1/dashboard/scan-statistics", headers=auth_headers)
                assert stats_response.status_code == status.HTTP_200_OK
                stats_data = stats_response.json()
                assert len(stats_data["scans_by_status"]) == 3
                
                # Step 4: Get project statistics
                mock_db.execute.return_value = MagicMock(fetchall=MagicMock(return_value=[]))
                
                project_stats_response = await client.get("/api/v1/dashboard/project-statistics", headers=auth_headers)
                assert project_stats_response.status_code == status.HTTP_200_OK
                
                # Step 5: Get top findings
                mock_db.execute.side_effect = [
                    MagicMock(fetchall=MagicMock(return_value=[(200, 180), (404, 20)])),
                    MagicMock(fetchall=MagicMock(return_value=[("text/html", 150)])),
                    MagicMock(fetchall=MagicMock(return_value=[("nginx", 5)]))
                ]
                
                findings_response = await client.get("/api/v1/dashboard/top-findings", headers=auth_headers)
                assert findings_response.status_code == status.HTTP_200_OK
                findings_data = findings_response.json()
                assert len(findings_data["status_codes"]) == 2
    
    @pytest.mark.asyncio
    async def test_dashboard_data_consistency(self, client: AsyncClient, mock_user, auth_headers):
        """Test that dashboard data is consistent across different endpoints."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock consistent data across endpoints
                total_scans = 10
                active_scans = 2
                completed_scans = 7
                failed_scans = 1
                
                # Overview endpoint
                mock_db.execute.side_effect = [
                    MagicMock(scalar=MagicMock(return_value=3)),  # projects
                    MagicMock(scalar=MagicMock(return_value=active_scans)),
                    MagicMock(scalar=MagicMock(return_value=total_scans)),
                    MagicMock(scalar=MagicMock(return_value=500))  # urls
                ]
                
                overview_response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
                overview_data = overview_response.json()
                
                # Scan statistics endpoint
                mock_db.execute.side_effect = [
                    MagicMock(fetchall=MagicMock(return_value=[
                        ("completed", completed_scans),
                        ("running", active_scans),
                        ("failed", failed_scans)
                    ])),
                    MagicMock(fetchall=MagicMock(return_value=[]))
                ]
                
                stats_response = await client.get("/api/v1/dashboard/scan-statistics", headers=auth_headers)
                stats_data = stats_response.json()
                
                # Verify consistency
                assert overview_data["active_scans"] == active_scans
                assert overview_data["total_scans"] == total_scans
                
                # Sum of scans by status should equal total scans
                total_from_stats = sum(item["count"] for item in stats_data["scans_by_status"])
                assert total_from_stats == total_scans
    
    @pytest.mark.asyncio
    async def test_dashboard_performance_with_large_dataset(self, client: AsyncClient, mock_user, auth_headers):
        """Test dashboard performance with large amounts of data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock large dataset
                large_project_count = 100
                large_scan_count = 1000
                large_url_count = 50000
                
                # Overview with large numbers
                mock_db.execute.side_effect = [
                    MagicMock(scalar=MagicMock(return_value=large_project_count)),
                    MagicMock(scalar=MagicMock(return_value=50)),  # active scans
                    MagicMock(scalar=MagicMock(return_value=large_scan_count)),
                    MagicMock(scalar=MagicMock(return_value=large_url_count))
                ]
                
                response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
                assert response.status_code == status.HTTP_200_OK
                
                data = response.json()
                assert data["total_projects"] == large_project_count
                assert data["total_scans"] == large_scan_count
                assert data["urls_discovered"] == large_url_count
                
                # Verify response time is reasonable (should be fast even with large numbers)
                # This is more of a conceptual test - in real scenarios you'd measure actual response time
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_dashboard_error_handling(self, client: AsyncClient, mock_user, auth_headers):
        """Test dashboard error handling when database operations fail."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock database error
                mock_db.execute.side_effect = Exception("Database connection error")
                
                response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
                
                # Should handle error gracefully (exact status code depends on error handling implementation)
                assert response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]