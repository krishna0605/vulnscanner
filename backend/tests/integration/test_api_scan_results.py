"""
Integration tests for scan results API endpoints.
Tests retrieval of discovered URLs, forms, technologies, and export functionality.
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from main import app


class TestScanResultsAPI:
    """Integration tests for scan results endpoints."""
    
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
    def sample_scan_id(self):
        """Sample scan ID."""
        return uuid4()
    
    @pytest.fixture
    def mock_scan_with_ownership(self, mock_user, sample_scan_id):
        """Mock scan with proper ownership."""
        mock_scan = MagicMock()
        mock_scan.id = sample_scan_id
        mock_scan.status = "completed"
        
        mock_project = MagicMock()
        mock_project.owner_id = mock_user["id"]
        mock_scan.project = mock_project
        
        return mock_scan
    
    @pytest.mark.asyncio
    async def test_get_discovered_urls_empty(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting discovered URLs when scan has no URLs."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan exists and user has access
                mock_db.execute.side_effect = [
                    # First call: get scan with ownership check
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    # Second call: get URLs (empty)
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/urls", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_get_discovered_urls_with_data(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting discovered URLs with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock URL data
                mock_url1 = MagicMock()
                mock_url1.id = uuid4()
                mock_url1.session_id = sample_scan_id
                mock_url1.url = "https://example.com/"
                mock_url1.parent_url = None
                mock_url1.method = "GET"
                mock_url1.status_code = 200
                mock_url1.content_type = "text/html"
                mock_url1.content_length = 1024
                mock_url1.response_time = 150
                mock_url1.page_title = "Example Homepage"
                mock_url1.discovered_at = datetime.now()
                
                mock_url2 = MagicMock()
                mock_url2.id = uuid4()
                mock_url2.session_id = sample_scan_id
                mock_url2.url = "https://example.com/about"
                mock_url2.parent_url = "https://example.com/"
                mock_url2.method = "GET"
                mock_url2.status_code = 200
                mock_url2.content_type = "text/html"
                mock_url2.content_length = 2048
                mock_url2.response_time = 200
                mock_url2.page_title = "About Us"
                mock_url2.discovered_at = datetime.now()
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_url1, mock_url2]))))
                ]
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/urls", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 2
                assert data[0]["url"] == "https://example.com/"
                assert data[0]["page_title"] == "Example Homepage"
                assert data[1]["url"] == "https://example.com/about"
                assert data[1]["parent_url"] == "https://example.com/"
    
    @pytest.mark.asyncio
    async def test_get_discovered_urls_with_filters(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting discovered URLs with status code and content type filters."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                # Test with status code filter
                response = await client.get(
                    f"/api/v1/scans/{sample_scan_id}/urls?status_code=200", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
                
                # Test with content type filter
                response = await client.get(
                    f"/api/v1/scans/{sample_scan_id}/urls?content_type=text/html", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
                
                # Test with pagination
                response = await client.get(
                    f"/api/v1/scans/{sample_scan_id}/urls?skip=10&limit=50", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_get_discovered_urls_scan_not_found(self, client: AsyncClient, mock_user, auth_headers):
        """Test getting URLs for non-existent scan."""
        non_existent_scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan not found
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
                
                response = await client.get(f"/api/v1/scans/{non_existent_scan_id}/urls", headers=auth_headers)
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_discovered_urls_unauthorized(self, client: AsyncClient, auth_headers, sample_scan_id):
        """Test getting URLs for scan owned by another user."""
        other_user = {
            "id": "987fcdeb-51a2-43d1-b456-426614174999",
            "email": "other@example.com"
        }
        
        with patch('core.auth_deps.get_current_user', return_value=other_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan exists but owned by different user
                mock_scan = MagicMock()
                mock_scan.id = sample_scan_id
                mock_project = MagicMock()
                mock_project.owner_id = "different_user_id"
                mock_scan.project = mock_project
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan))
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/urls", headers=auth_headers)
                
                assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_extracted_forms_empty(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting extracted forms when scan has no forms."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/forms", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_get_extracted_forms_with_data(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting extracted forms with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock form data
                mock_form1 = MagicMock()
                mock_form1.id = uuid4()
                mock_form1.form_action = "/login"
                mock_form1.form_method = "POST"
                mock_form1.form_fields = [
                    {"name": "username", "type": "text", "required": True},
                    {"name": "password", "type": "password", "required": True}
                ]
                mock_form1.csrf_tokens = ["csrf_token_123"]
                mock_form1.authentication_required = False
                
                # Mock URL relationship
                mock_url = MagicMock()
                mock_url.url = "https://example.com/login"
                mock_form1.discovered_url = mock_url
                
                mock_form2 = MagicMock()
                mock_form2.id = uuid4()
                mock_form2.form_action = "/contact"
                mock_form2.form_method = "POST"
                mock_form2.form_fields = [
                    {"name": "name", "type": "text", "required": True},
                    {"name": "email", "type": "email", "required": True},
                    {"name": "message", "type": "textarea", "required": True}
                ]
                mock_form2.csrf_tokens = []
                mock_form2.authentication_required = False
                
                mock_url2 = MagicMock()
                mock_url2.url = "https://example.com/contact"
                mock_form2.discovered_url = mock_url2
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_form1, mock_form2]))))
                ]
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/forms", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 2
                assert data[0]["form_action"] == "/login"
                assert data[0]["form_method"] == "POST"
                assert len(data[0]["form_fields"]) == 2
                assert data[0]["csrf_tokens"] == ["csrf_token_123"]
    
    @pytest.mark.asyncio
    async def test_get_detected_technologies_empty(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting detected technologies when scan has no technologies."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/technologies", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data == []
    
    @pytest.mark.asyncio
    async def test_get_detected_technologies_with_data(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test getting detected technologies with data."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock technology data
                mock_tech1 = MagicMock()
                mock_tech1.id = uuid4()
                mock_tech1.server_software = "nginx/1.18.0"
                mock_tech1.programming_language = "PHP"
                mock_tech1.framework = "Laravel"
                mock_tech1.cms = None
                mock_tech1.javascript_libraries = ["jQuery", "Bootstrap"]
                mock_tech1.security_headers = {
                    "X-Frame-Options": "DENY",
                    "X-Content-Type-Options": "nosniff",
                    "Strict-Transport-Security": "max-age=31536000"
                }
                mock_tech1.detected_at = datetime.now()
                
                # Mock URL relationship
                mock_url = MagicMock()
                mock_url.url = "https://example.com/"
                mock_tech1.discovered_url = mock_url
                
                mock_tech2 = MagicMock()
                mock_tech2.id = uuid4()
                mock_tech2.server_software = "Apache/2.4.41"
                mock_tech2.programming_language = "Python"
                mock_tech2.framework = "Django"
                mock_tech2.cms = None
                mock_tech2.javascript_libraries = ["React", "Axios"]
                mock_tech2.security_headers = {
                    "Content-Security-Policy": "default-src 'self'",
                    "X-Frame-Options": "SAMEORIGIN"
                }
                mock_tech2.detected_at = datetime.now()
                
                mock_url2 = MagicMock()
                mock_url2.url = "https://example.com/api/"
                mock_tech2.discovered_url = mock_url2
                
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_tech1, mock_tech2]))))
                ]
                
                response = await client.get(f"/api/v1/scans/{sample_scan_id}/technologies", headers=auth_headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data) == 2
                assert data[0]["server_software"] == "nginx/1.18.0"
                assert data[0]["programming_language"] == "PHP"
                assert data[0]["framework"] == "Laravel"
                assert "jQuery" in data[0]["javascript_libraries"]
                assert "X-Frame-Options" in data[0]["security_headers"]
    
    @pytest.mark.asyncio
    async def test_export_scan_results_json(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test exporting scan results in JSON format."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan with results
                mock_scan_with_ownership.stats = {
                    "urls_found": 25,
                    "forms_found": 3,
                    "technologies_found": 5
                }
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership))
                
                # Mock export service
                with patch('services.export_service.generate_scan_export') as mock_export:
                    mock_export.return_value = {
                        "scan_info": {
                            "id": str(sample_scan_id),
                            "status": "completed",
                            "stats": {"urls_found": 25, "forms_found": 3}
                        },
                        "urls": [],
                        "forms": [],
                        "technologies": []
                    }
                    
                    response = await client.get(
                        f"/api/v1/scans/{sample_scan_id}/export?format=json", 
                        headers=auth_headers
                    )
                
                assert response.status_code == status.HTTP_200_OK
                assert response.headers["content-type"] == "application/json"
                data = response.json()
                assert "scan_info" in data
                assert data["scan_info"]["id"] == str(sample_scan_id)
    
    @pytest.mark.asyncio
    async def test_export_scan_results_csv(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test exporting scan results in CSV format."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership))
                
                # Mock export service
                with patch('services.export_service.generate_csv_export') as mock_export:
                    mock_export.return_value = "url,status_code,content_type\nhttps://example.com/,200,text/html"
                    
                    response = await client.get(
                        f"/api/v1/scans/{sample_scan_id}/export?format=csv", 
                        headers=auth_headers
                    )
                
                assert response.status_code == status.HTTP_200_OK
                assert response.headers["content-type"] == "text/csv"
                assert "url,status_code,content_type" in response.text
    
    @pytest.mark.asyncio
    async def test_export_scan_results_pdf(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id, mock_scan_with_ownership):
        """Test exporting scan results in PDF format."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan_with_ownership))
                
                # Mock export service
                with patch('services.export_service.generate_pdf_export') as mock_export:
                    mock_export.return_value = b"PDF_CONTENT_MOCK"
                    
                    response = await client.get(
                        f"/api/v1/scans/{sample_scan_id}/export?format=pdf", 
                        headers=auth_headers
                    )
                
                assert response.status_code == status.HTTP_200_OK
                assert response.headers["content-type"] == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_export_scan_results_invalid_format(self, client: AsyncClient, mock_user, auth_headers, sample_scan_id):
        """Test exporting scan results with invalid format."""
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            response = await client.get(
                f"/api/v1/scans/{sample_scan_id}/export?format=invalid", 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_export_scan_results_unauthorized(self, client: AsyncClient, auth_headers, sample_scan_id):
        """Test exporting results for scan owned by another user."""
        other_user = {
            "id": "987fcdeb-51a2-43d1-b456-426614174999",
            "email": "other@example.com"
        }
        
        with patch('core.auth_deps.get_current_user', return_value=other_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan exists but owned by different user
                mock_scan = MagicMock()
                mock_scan.id = sample_scan_id
                mock_project = MagicMock()
                mock_project.owner_id = "different_user_id"
                mock_scan.project = mock_project
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan))
                
                response = await client.get(
                    f"/api/v1/scans/{sample_scan_id}/export?format=json", 
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_403_FORBIDDEN


class TestScanResultsIntegration:
    """Integration tests for complete scan results workflows."""
    
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
    async def test_complete_results_retrieval_workflow(self, client: AsyncClient, mock_user, auth_headers):
        """Test complete workflow of retrieving all types of scan results."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan with ownership
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.status = "completed"
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                # Step 1: Get discovered URLs
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                urls_response = await client.get(f"/api/v1/scans/{scan_id}/urls", headers=auth_headers)
                assert urls_response.status_code == status.HTTP_200_OK
                
                # Step 2: Get extracted forms
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                forms_response = await client.get(f"/api/v1/scans/{scan_id}/forms", headers=auth_headers)
                assert forms_response.status_code == status.HTTP_200_OK
                
                # Step 3: Get detected technologies
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                tech_response = await client.get(f"/api/v1/scans/{scan_id}/technologies", headers=auth_headers)
                assert tech_response.status_code == status.HTTP_200_OK
                
                # Step 4: Export results
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan))
                
                with patch('services.export_service.generate_scan_export') as mock_export:
                    mock_export.return_value = {"scan_info": {"id": str(scan_id)}}
                    
                    export_response = await client.get(
                        f"/api/v1/scans/{scan_id}/export?format=json", 
                        headers=auth_headers
                    )
                    assert export_response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_results_filtering_and_pagination(self, client: AsyncClient, mock_user, auth_headers):
        """Test filtering and pagination across different result types."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan with ownership
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                # Test URL filtering by status code
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(
                    f"/api/v1/scans/{scan_id}/urls?status_code=404&skip=0&limit=25", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
                
                # Test URL filtering by content type
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(
                    f"/api/v1/scans/{scan_id}/urls?content_type=application/json", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
                
                # Test forms pagination
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(
                    f"/api/v1/scans/{scan_id}/forms?skip=10&limit=20", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
                
                # Test technologies pagination
                mock_db.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan)),
                    MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
                ]
                
                response = await client.get(
                    f"/api/v1/scans/{scan_id}/technologies?skip=5&limit=15", 
                    headers=auth_headers
                )
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_export_formats_comparison(self, client: AsyncClient, mock_user, auth_headers):
        """Test exporting the same scan results in different formats."""
        scan_id = uuid4()
        
        with patch('core.auth_deps.get_current_user', return_value=mock_user):
            with patch('db.session.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db
                
                # Mock scan with ownership
                mock_scan = MagicMock()
                mock_scan.id = scan_id
                mock_scan.status = "completed"
                mock_project = MagicMock()
                mock_project.owner_id = mock_user["id"]
                mock_scan.project = mock_project
                
                mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_scan))
                
                # Test JSON export
                with patch('services.export_service.generate_scan_export') as mock_json_export:
                    mock_json_export.return_value = {"scan_info": {"id": str(scan_id)}}
                    
                    json_response = await client.get(
                        f"/api/v1/scans/{scan_id}/export?format=json", 
                        headers=auth_headers
                    )
                    assert json_response.status_code == status.HTTP_200_OK
                    assert json_response.headers["content-type"] == "application/json"
                
                # Test CSV export
                with patch('services.export_service.generate_csv_export') as mock_csv_export:
                    mock_csv_export.return_value = "url,status\nhttps://example.com,200"
                    
                    csv_response = await client.get(
                        f"/api/v1/scans/{scan_id}/export?format=csv", 
                        headers=auth_headers
                    )
                    assert csv_response.status_code == status.HTTP_200_OK
                    assert csv_response.headers["content-type"] == "text/csv"
                
                # Test PDF export
                with patch('services.export_service.generate_pdf_export') as mock_pdf_export:
                    mock_pdf_export.return_value = b"PDF_CONTENT"
                    
                    pdf_response = await client.get(
                        f"/api/v1/scans/{scan_id}/export?format=pdf", 
                        headers=auth_headers
                    )
                    assert pdf_response.status_code == status.HTTP_200_OK
                    assert pdf_response.headers["content-type"] == "application/pdf"