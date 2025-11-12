"""
Integration tests for projects API endpoints.
Tests project CRUD operations, ownership, and access control.
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from main import app


class TestProjectsAPI:
    """Integration tests for projects endpoints."""
    
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
    def sample_project_data(self):
        """Sample project creation data."""
        return {
            "name": "Test Project",
            "description": "A test project for vulnerability scanning",
            "target_domain": "https://example.com",
            "scope_rules": [
                "https://example.com/*",
                "https://subdomain.example.com/*"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_list_projects_empty(self, client: AsyncClient, mock_user, auth_headers):
        """Test listing projects when user has no projects."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                # Mock database session
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock empty query result
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                mock_db.execute.return_value = mock_result
                
                response = await client.get("/api/v1/projects/", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_list_projects_with_data(self, client: AsyncClient, mock_user, auth_headers):
        """Test listing projects with existing projects."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project data
                mock_project = MagicMock()
                mock_project.id = uuid4()
                mock_project.name = "Test Project"
                mock_project.description = "Test Description"
                mock_project.target_domain = "https://example.com"
                mock_project.scope_rules = ["https://example.com/*"]
                mock_project.owner_id = mock_user["id"]
                mock_project.created_at = datetime.now()
                mock_project.updated_at = datetime.now()
                
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_project]
                mock_db.execute.return_value = mock_result
                
                response = await client.get("/api/v1/projects/", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 1
                assert data[0]["name"] == "Test Project"
                assert data[0]["target_domain"] == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_list_projects_with_search(self, client: AsyncClient, mock_user, auth_headers):
        """Test listing projects with search filter."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                mock_db.execute.return_value = mock_result
                
                response = await client.get(
                    "/api/v1/projects/?search=test&limit=50", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                # Verify that the search parameter was processed
                mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_projects_with_domain_filter(self, client: AsyncClient, mock_user, auth_headers):
        """Test listing projects with domain filter."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                mock_db.execute.return_value = mock_result
                
                response = await client.get(
                    "/api/v1/projects/?domain=example.com", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_list_projects_pagination(self, client: AsyncClient, mock_user, auth_headers):
        """Test projects list pagination."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                mock_db.execute.return_value = mock_result
                
                response = await client.get(
                    "/api/v1/projects/?skip=10&limit=20", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_list_projects_unauthorized(self, client: AsyncClient):
        """Test listing projects without authentication."""
        response = await client.get("/api/v1/projects/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_create_project_success(self, client: AsyncClient, mock_user, auth_headers, sample_project_data):
        """Test successful project creation."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock successful project creation
                mock_project = MagicMock()
                mock_project.id = uuid4()
                mock_project.name = sample_project_data["name"]
                mock_project.description = sample_project_data["description"]
                mock_project.target_domain = sample_project_data["target_domain"]
                mock_project.scope_rules = sample_project_data["scope_rules"]
                mock_project.owner_id = mock_user["id"]
                mock_project.created_at = datetime.now()
                mock_project.updated_at = datetime.now()
                
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                # Mock the project creation process
                with patch('models.unified_models.Project', return_value=mock_project):
                    response = await client.post(
                        "/api/v1/projects/", 
                        json=sample_project_data,
                        headers=auth_headers
                    )
                
                assert response.status_code == status.HTTP_201_CREATED
                data = response.json()
                assert data["name"] == sample_project_data["name"]
                assert data["target_domain"] == sample_project_data["target_domain"]
    
    @pytest.mark.asyncio
    async def test_create_project_invalid_domain(self, client: AsyncClient, mock_user, auth_headers):
        """Test project creation with invalid domain."""
        invalid_project_data = {
            "name": "Test Project",
            "description": "Test Description",
            "target_domain": "invalid-domain",  # Invalid URL
            "scope_rules": []
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            response = await client.post(
                "/api/v1/projects/", 
                json=invalid_project_data,
                headers=auth_headers
            )
            
            # Should fail validation
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_project_missing_fields(self, client: AsyncClient, mock_user, auth_headers):
        """Test project creation with missing required fields."""
        incomplete_project_data = {
            "name": "Test Project"
            # Missing required fields
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            response = await client.post(
                "/api/v1/projects/", 
                json=incomplete_project_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_project_unauthorized(self, client: AsyncClient, sample_project_data):
        """Test project creation without authentication."""
        response = await client.post("/api/v1/projects/", json=sample_project_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_project_success(self, client: AsyncClient, mock_user, auth_headers):
        """Test successful project retrieval."""
        project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project data
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.name = "Test Project"
                mock_project.description = "Test Description"
                mock_project.target_domain = "https://example.com"
                mock_project.scope_rules = ["https://example.com/*"]
                mock_project.owner_id = mock_user["id"]
                mock_project.created_at = datetime.now()
                mock_project.updated_at = datetime.now()
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_db.execute.return_value = mock_result
                
                response = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["name"] == "Test Project"
                assert data["target_domain"] == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client: AsyncClient, mock_user, auth_headers):
        """Test retrieving non-existent project."""
        project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project not found
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_project_unauthorized_access(self, client: AsyncClient, auth_headers):
        """Test retrieving project owned by another user."""
        project_id = uuid4()
        other_user = {
            "id": "987fcdeb-51a2-43d1-b456-426614174999",
            "email": "other@example.com"
        }
        
        with patch('core.auth_deps.get_current_user', return_value=other_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project owned by different user
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None  # No project found for this user
                mock_db.execute.return_value = mock_result
                
                response = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_project_success(self, client: AsyncClient, mock_user, auth_headers):
        """Test successful project update."""
        project_id = uuid4()
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description",
            "scope_rules": ["https://example.com/*", "https://api.example.com/*"]
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock existing project
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.name = "Original Name"
                mock_project.description = "Original Description"
                mock_project.target_domain = "https://example.com"
                mock_project.scope_rules = ["https://example.com/*"]
                mock_project.owner_id = mock_user["id"]
                mock_project.created_at = datetime.now()
                mock_project.updated_at = datetime.now()
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_db.execute.return_value = mock_result
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                response = await client.put(
                    f"/api/v1/projects/{project_id}", 
                    json=update_data,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["name"] == update_data["name"]
    
    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client: AsyncClient, mock_user, auth_headers):
        """Test updating non-existent project."""
        project_id = uuid4()
        update_data = {"name": "Updated Name"}
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.put(
                    f"/api/v1/projects/{project_id}", 
                    json=update_data,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_project_success(self, client: AsyncClient, mock_user, auth_headers):
        """Test successful project deletion."""
        project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock existing project
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.owner_id = mock_user["id"]
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_db.execute.return_value = mock_result
                mock_db.delete = MagicMock()
                mock_db.commit = AsyncMock()
                
                response = await client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client: AsyncClient, mock_user, auth_headers):
        """Test deleting non-existent project."""
        project_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                response = await client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_project_unauthorized(self, client: AsyncClient):
        """Test deleting project without authentication."""
        project_id = uuid4()
        
        response = await client.delete(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProjectsIntegration:
    """Integration tests for complete project workflows."""
    
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
    async def test_complete_project_lifecycle(self, client: AsyncClient, mock_user, auth_headers):
        """Test complete project lifecycle: create, read, update, delete."""
        project_data = {
            "name": "Lifecycle Test Project",
            "description": "Testing complete project lifecycle",
            "target_domain": "https://lifecycle.example.com",
            "scope_rules": ["https://lifecycle.example.com/*"]
        }
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Step 1: Create project
                mock_project = MagicMock()
                project_id = uuid4()
                mock_project.id = project_id
                mock_project.name = project_data["name"]
                mock_project.description = project_data["description"]
                mock_project.target_domain = project_data["target_domain"]
                mock_project.scope_rules = project_data["scope_rules"]
                mock_project.owner_id = mock_user["id"]
                mock_project.created_at = datetime.now()
                mock_project.updated_at = datetime.now()
                
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                with patch('models.unified_models.Project', return_value=mock_project):
                    create_response = await client.post(
                        "/api/v1/projects/", 
                        json=project_data,
                        headers=auth_headers
                    )
                
                assert create_response.status_code == status.HTTP_201_CREATED
                create_response.json()
                
                # Step 2: Read project
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_db.execute.return_value = mock_result
                
                read_response = await client.get(
                    f"/api/v1/projects/{project_id}", 
                    headers=auth_headers
                )
                
                assert read_response.status_code == status.HTTP_200_OK
                read_project = read_response.json()
                assert read_project["name"] == project_data["name"]
                
                # Step 3: Update project
                update_data = {
                    "name": "Updated Lifecycle Project",
                    "description": "Updated description for lifecycle test"
                }
                
                # Update mock project attributes
                mock_project.name = update_data["name"]
                mock_project.description = update_data["description"]
                
                update_response = await client.put(
                    f"/api/v1/projects/{project_id}", 
                    json=update_data,
                    headers=auth_headers
                )
                
                assert update_response.status_code == status.HTTP_200_OK
                updated_project = update_response.json()
                assert updated_project["name"] == update_data["name"]
                
                # Step 4: Delete project
                mock_db.delete = MagicMock()
                
                delete_response = await client.delete(
                    f"/api/v1/projects/{project_id}", 
                    headers=auth_headers
                )
                
                assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_project_ownership_isolation(self, client: AsyncClient, auth_headers):
        """Test that users can only access their own projects."""
        user1 = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user1@example.com"
        }
        user2 = {
            "id": "987fcdeb-51a2-43d1-b456-426614174999",
            "email": "user2@example.com"
        }
        
        project_id = uuid4()
        
        # User 1 creates a project
        with patch('core.auth_deps.get_current_user', return_value=user1):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock project owned by user1
                mock_project = MagicMock()
                mock_project.id = project_id
                mock_project.owner_id = user1["id"]
                mock_project.name = "User1 Project"
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_project
                mock_db.execute.return_value = mock_result
                
                # User1 can access their project
                response = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
                assert response.status_code == status.HTTP_200_OK
        
        # User 2 tries to access user1's project
        with patch('core.auth_deps.get_current_user', return_value=user2):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock no project found for user2 (ownership check)
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute.return_value = mock_result
                
                # User2 cannot access user1's project
                response = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_project_validation_edge_cases(self, client: AsyncClient, mock_user, auth_headers):
        """Test project validation with various edge cases."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            # Test 1: Very long project name
            long_name_data = {
                "name": "A" * 300,  # Very long name
                "description": "Test",
                "target_domain": "https://example.com",
                "scope_rules": []
            }
            
            response = await client.post(
                "/api/v1/projects/", 
                json=long_name_data,
                headers=auth_headers
            )
            # Should fail validation if name length is limited
            assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
            
            # Test 2: Invalid URL schemes
            invalid_scheme_data = {
                "name": "Test Project",
                "description": "Test",
                "target_domain": "ftp://example.com",  # Invalid scheme for web scanning
                "scope_rules": []
            }
            
            response = await client.post(
                "/api/v1/projects/", 
                json=invalid_scheme_data,
                headers=auth_headers
            )
            # Should fail validation
            assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
            
            # Test 3: Empty scope rules (should be allowed)
            empty_scope_data = {
                "name": "Test Project",
                "description": "Test with empty scope",
                "target_domain": "https://example.com",
                "scope_rules": []
            }
            
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                mock_db.add = MagicMock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                with patch('models.unified_models.Project') as mock_project_class:
                    mock_project = MagicMock()
                    mock_project.id = uuid4()
                    mock_project_class.return_value = mock_project
                    
                    response = await client.post(
                        "/api/v1/projects/", 
                        json=empty_scope_data,
                        headers=auth_headers
                    )
                    
                    # Should succeed
                    assert response.status_code == status.HTTP_201_CREATED