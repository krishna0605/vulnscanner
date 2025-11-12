"""
Integration tests for scans API endpoints.
Tests scan session management, status tracking, and project association.
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from main import app


class TestScansAPI:
    """Integration tests for scans endpoints."""
    
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
    
    @pytest.fixture
    def sample_project_id(self):
        """Sample project ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_scan_config(self):
        """Sample scan configuration."""
        return {
            "max_depth": 3,
            "max_pages": 1000,
            "requests_per_second": 10,
            "timeout": 30,
            "follow_redirects": True,
            "respect_robots": True,
            "user_agent": "Enhanced-Vulnerability-Scanner/1.0",
            "scope_patterns": ["https://example.com/*"],
            "exclude_patterns": ["/admin/*", "/private/*"],
            "authentication": None
        }
    
    @pytest.mark.asyncio
    async def test_list_scans_empty(self, client: AsyncClient, mock_user, auth_headers, sample_project_id):
        """Test listing scans when project has no scans."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project exists and user owns it
                mock_project = MagicMock()
                mock_project.id = sample_project_id
                mock_project.owner_id = mock_user["id"]
                
                # Mock empty scans result
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_result.scalars.return_value.all.return_value = []
                mock_db.execute.return_value = mock_result
                
                response = await client.get(
                    f"/api/v1/projects/{sample_project_id}/scans", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_list_scans_with_data(self, client: AsyncClient, mock_user, auth_headers, sample_project_id):
        """Test listing scans with existing scan sessions."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project exists
                mock_project = MagicMock()
                mock_project.id = sample_project_id
                mock_project.owner_id = mock_user["id"]
                
                # Mock scan data
                mock_scan = MagicMock()
                mock_scan.id = uuid4()
                mock_scan.project_id = sample_project_id
                mock_scan.status = "completed"
                mock_scan.start_time = datetime.now()
                mock_scan.end_time = datetime.now()
                mock_scan.configuration = {"max_depth": 3}
                mock_scan.stats = {"urls_found": 150, "forms_found": 12}
                mock_scan.created_by = mock_user["id"]
                
                # Mock database calls
                mock_db.execute.side_effect = [
                    # First call: check project ownership
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_project)),
                    # Second call: get scans
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_scan]))))
                ]
                
                response = await client.get(
                    f"/api/v1/projects/{sample_project_id}/scans", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 1
                assert data[0]["status"] == "completed"
                assert data[0]["project_id"] == str(sample_project_id)
    
    @pytest.mark.asyncio
    async def test_list_scans_with_status_filter(self, client: AsyncClient, mock_user, auth_headers, sample_project_id):
        """Test listing scans with status filter."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project exists
                mock_project = MagicMock()
                mock_project.id = sample_project_id
                mock_project.owner_id = mock_user["id"]
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_project)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(
                    f"/api/v1/projects/{sample_project_id}/scans?status=running", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_list_scans_project_not_found(self, client: AsyncClient, mock_user, auth_headers):
        """Test listing scans for non-existent project."""
        non_existent_project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project not found
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.get(
                    f"/api/v1/projects/{non_existent_project_id}/scans", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_list_scans_unauthorized_project(self, client: AsyncClient, auth_headers, sample_project_id):
        """Test listing scans for project owned by another user."""
        other_user = {
            "id": "987fcdeb-51a2-43d1-b456-426614174999",
            "email": "other@example.com"
        }
        
        with patch('core.auth_deps.get_current_user', return_value=other_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project not found for this user (ownership check)
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.get(
                    f"/api/v1/projects/{sample_project_id}/scans", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_create_scan_success(self, client: AsyncClient, mock_user, auth_headers, sample_project_id, sample_scan_config):
        """Test successful scan creation."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project exists and user owns it
                mock_project = MagicMock()
                mock_project.id = sample_project_id
                mock_project.owner_id = mock_user["id"]
                mock_project.target_domain = "https://example.com"
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_db.execute.return_value = mock_result
                
                # Mock scan creation
                mock_scan = MagicMock()
                scan_id = uuid4()
                mock_scan.id = scan_id
                mock_scan.project_id = sample_project_id
                mock_scan.status = "pending"
                mock_scan.start_time = datetime.now()
                mock_scan.configuration = sample_scan_config
                mock_scan.stats = {}
                mock_scan.created_by = mock_user["id"]
                
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                # Mock Celery task
                with patch('tasks.crawler_tasks.start_crawl_task.delay') as mock_task:
                    mock_task.return_value.id = "task_123"
                    
                    with patch('models.unified_models.ScanSession', return_value=mock_scan):
                        response = await client.post(
                            f"/api/v1/projects/{sample_project_id}/scans", 
                            json=sample_scan_config,
                            headers=auth_headers
                        )
                
                assert response.status_code == status.HTTP_201_CREATED
                data = response.json()
                assert data["status"] == "pending"
                assert data["project_id"] == str(sample_project_id)
    
    @pytest.mark.asyncio
    async def test_create_scan_invalid_config(self, client: AsyncClient, mock_user, auth_headers, sample_project_id):
        """Test scan creation with invalid configuration."""
        invalid_config = {
            "max_depth": -1,  # Invalid negative value
            "max_pages": 0,   # Invalid zero value
            "requests_per_second": 1000,  # Too high
            "timeout": -5     # Invalid negative timeout
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            response = await client.post(
                f"/api/v1/projects/{sample_project_id}/scans", 
                json=invalid_config,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_scan_project_not_found(self, client: AsyncClient, mock_user, auth_headers, sample_scan_config):
        """Test scan creation for non-existent project."""
        non_existent_project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project not found
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.post(
                    f"/api/v1/projects/{non_existent_project_id}/scans", 
                    json=sample_scan_config,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_scan_success(self, client: AsyncClient, mock_user, auth_headers):
        """Test successful scan retrieval."""
        scan_id = uuid4()
        project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan data with project ownership
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.project_id = project_id
                mock_scan.status = "running"
                mock_scan.start_time = datetime.now()
                mock_scan.end_time = None
                mock_scan.configuration = {"max_depth": 3}
                mock_scan.stats = {"urls_found": 50}
                mock_scan.created_by = mock_user["id"]
                
                # Mock project for ownership check
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_scan
                mock_db.execute.return_value = mock_result
                
                response = await client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "running"
                assert data["id"] == str(scan_id)
    
    @pytest.mark.asyncio
    async def test_get_scan_not_found(self, client: AsyncClient, mock_user, auth_headers):
        """Test retrieving non-existent scan."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan not found
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_scan_unauthorized_access(self, client: AsyncClient, auth_headers):
        """Test retrieving scan from project owned by another user."""
        scan_id = uuid4()
        other_user = {
            "id": "987fcdeb-51a2-43d1-b456-426614174999",
            "email": "other@example.com"
        }
        
        with patch('core.auth_deps.get_current_user', return_value=other_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan exists but belongs to different user
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_project = MagicMock()
                mock_project.owner_id = "different_user_id"
                mock_scan.project = mock_project
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_scan
                mock_db.execute.return_value = mock_result
                
                response = await client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_stop_scan_success(self, client: AsyncClient, mock_user, auth_headers):
        """Test successful scan stopping."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock running scan
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.status = "running"
                mock_scan.task_id = "celery_task_123"
                
                # Mock project ownership
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_scan
                mock_db.execute.return_value = mock_result
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                # Mock Celery task revocation
                with patch('celery.current_app.control.revoke'):
                    response = await client.put(f"/api/v1/scans/{scan_id}/stop", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_stop_scan_already_completed(self, client: AsyncClient, mock_user, auth_headers):
        """Test stopping already completed scan."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock completed scan
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.status = "completed"
                
                # Mock project ownership
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_scan
                mock_db.execute.return_value = mock_result
                
                response = await client.put(f"/api/v1/scans/{scan_id}/stop", headers=auth_headers)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_delete_scan_success(self, client: AsyncClient, mock_user, auth_headers):
        """Test successful scan deletion."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.status = "completed"
                
                # Mock project ownership
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_scan
                mock_db.execute.return_value = mock_result
                mock_db.delete = MagicMock()
                mock_db.commit = AsyncMock()
                
                response = await client.delete(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_delete_running_scan_fails(self, client: AsyncClient, mock_user, auth_headers):
        """Test that deleting running scan fails."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock running scan
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.status = "running"
                
                # Mock project ownership
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_scan
                mock_db.execute.return_value = mock_result
                
                response = await client.delete(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestScansIntegration:
    """Integration tests for complete scan workflows."""
    
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
    async def test_complete_scan_lifecycle(self, client: AsyncClient, mock_user, auth_headers):
        """Test complete scan lifecycle: create, monitor, stop, delete."""
        project_id = uuid4()
        scan_config = {
            "max_depth": 2,
            "max_pages": 100,
            "requests_per_second": 5,
            "timeout": 30,
            "follow_redirects": True,
            "respect_robots": True
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Step 1: Create scan
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.owner_id = mock_user["id"]
                mock_project.target_domain = "https://example.com"
                
                mock_scan = MagicMock()
                scan_id = uuid4()
                mock_scan.id = scan_id
                mock_scan.project_id = project_id
                mock_scan.status = "pending"
                mock_scan.task_id = "celery_task_123"
                mock_scan.configuration = scan_config
                mock_scan.stats = {}
                mock_scan.created_by = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_project))
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                with patch('tasks.crawler_tasks.start_crawl_task.delay') as mock_task:
                    mock_task.return_value.id = "celery_task_123"
                    
                    with patch('models.unified_models.ScanSession', return_value=mock_scan):
                        create_response = await client.post(
                            f"/api/v1/projects/{project_id}/scans", 
                            json=scan_config,
                            headers=auth_headers
                        )
                
                assert create_response.status_code == status.HTTP_201_CREATED
                create_response.json()
                
                # Step 2: Get scan status
                mock_scan.status = "running"
                mock_scan.stats = {"urls_found": 25, "forms_found": 3}
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan))
                
                status_response = await client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert status_response.status_code == status.HTTP_200_OK
                status_data = status_response.json()
                assert status_data["status"] == "running"
                assert status_data["stats"]["urls_found"] == 25
                
                # Step 3: Stop scan
                mock_scan.status = "cancelled"
                
                with patch('celery.current_app.control.revoke'):
                    stop_response = await client.put(f"/api/v1/scans/{scan_id}/stop", headers=auth_headers)
                
                assert stop_response.status_code == status.HTTP_200_OK
                stopped_scan = stop_response.json()
                assert stopped_scan["status"] == "cancelled"
                
                # Step 4: Delete scan
                mock_db.delete = MagicMock()
                
                delete_response = await client.delete(f"/api/v1/scans/{scan_id}", headers=auth_headers)
                
                assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_concurrent_scans_per_project(self, client: AsyncClient, mock_user, auth_headers):
        """Test creating multiple concurrent scans for the same project."""
        project_id = uuid4()
        scan_config = {
            "max_depth": 1,
            "max_pages": 50,
            "requests_per_second": 2
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.owner_id = mock_user["id"]
                mock_project.target_domain = "https://example.com"
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_project))
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                # Create first scan
                with patch('tasks.crawler_tasks.start_crawl_task.delay') as mock_task:
                    mock_task.return_value.id = "task_1"
                    
                    with patch('models.unified_models.ScanSession') as mock_scan_class:
                        mock_scan1 = MagicMock()
                        mock_scan1.id = uuid4()
                        mock_scan1.status = "pending"
                        mock_scan_class.return_value = mock_scan1
                        
                        response1 = await client.post(
                            f"/api/v1/projects/{project_id}/scans", 
                            json=scan_config,
                            headers=auth_headers
                        )
                
                assert response1.status_code == status.HTTP_201_CREATED
                
                # Create second scan
                with patch('tasks.crawler_tasks.start_crawl_task.delay') as mock_task:
                    mock_task.return_value.id = "task_2"
                    
                    with patch('models.unified_models.ScanSession') as mock_scan_class:
                        mock_scan2 = MagicMock()
                        mock_scan2.id = uuid4()
                        mock_scan2.status = "pending"
                        mock_scan_class.return_value = mock_scan2
                        
                        response2 = await client.post(
                            f"/api/v1/projects/{project_id}/scans", 
                            json=scan_config,
                            headers=auth_headers
                        )
                
                assert response2.status_code == status.HTTP_201_CREATED
                
                # Both scans should be created successfully
                scan1_data = response1.json()
                scan2_data = response2.json()
                assert scan1_data["id"] != scan2_data["id"]
    
    @pytest.mark.asyncio
    async def test_scan_configuration_validation_scenarios(self, client: AsyncClient, mock_user, auth_headers):
        """Test various scan configuration validation scenarios."""
        project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project exists
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.owner_id = mock_user["id"]
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_project))
                
                # Test 1: Minimal valid configuration
                minimal_config = {
                    "max_depth": 1,
                    "max_pages": 10
                }
                
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                with patch('tasks.crawler_tasks.start_crawl_task.delay'):
                    with patch('models.unified_models.ScanSession'):
                        response = await client.post(
                            f"/api/v1/projects/{project_id}/scans", 
                            json=minimal_config,
                            headers=auth_headers
                        )
                        
                        assert response.status_code == status.HTTP_201_CREATED
                
                # Test 2: Maximum valid configuration
                max_config = {
                    "max_depth": 10,
                    "max_pages": 100000,
                    "requests_per_second": 100,
                    "timeout": 300,
                    "follow_redirects": True,
                    "respect_robots": True,
                    "user_agent": "Custom-Scanner/2.0",
                    "scope_patterns": ["https://example.com/*", "https://api.example.com/*"],
                    "exclude_patterns": ["/admin/*", "/private/*", "/internal/*"],
                    "authentication": {
                        "type": "basic",
                        "username": "testuser",
                        "password": "testpass"
                    }
                }
                
                with patch('tasks.crawler_tasks.start_crawl_task.delay'):
                    with patch('models.unified_models.ScanSession'):
                        response = await client.post(
                            f"/api/v1/projects/{project_id}/scans", 
                            json=max_config,
                            headers=auth_headers
                        )
                        
                        assert response.status_code == status.HTTP_201_CREATED
                
                # Test 3: Invalid configurations
                invalid_configs = [
                    {"max_depth": 0},  # Too low
                    {"max_depth": 15},  # Too high
                    {"max_pages": 0},  # Too low
                    {"max_pages": 200000},  # Too high
                    {"requests_per_second": 0},  # Too low
                    {"requests_per_second": 200},  # Too high
                    {"timeout": 0},  # Too low
                    {"timeout": 500},  # Too high
                ]
                
                for invalid_config in invalid_configs:
                    response = await client.post(
                        f"/api/v1/projects/{project_id}/scans", 
                        json=invalid_config,
                        headers=auth_headers
                    )
                    
                    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY