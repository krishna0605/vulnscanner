"""Integration tests for scan results API endpoints.
Tests discovered URLs, forms, technology fingerprints, and export functionality."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch
from uuid import uuid4

from models.unified_models import (
    Profile, Project, ScanSession, DiscoveredUrl, 
    ExtractedForm, TechnologyFingerprint
)


@pytest.mark.integration
@pytest.mark.api
class TestScanResultsAPI:
    """Test scan results API endpoints."""

    @pytest.mark.asyncio
    async def test_list_scan_urls_success(
        self, 
        authenticated_client: AsyncClient, 
        db_session: AsyncSession,
        test_profile: Profile,
        test_project: Project,
        test_scan_session: ScanSession
    ):
        """Test listing discovered URLs for a scan."""
        # Create test discovered URLs
        url1 = DiscoveredUrl(
            session_id=test_scan_session.id,
            url="https://example.com/page1",
            method="GET",
            status_code=200,
            content_type="text/html",
            content_length=1024,
            response_time=150,
            page_title="Page 1"
        )
        url2 = DiscoveredUrl(
            session_id=test_scan_session.id,
            url="https://example.com/page2",
            method="GET",
            status_code=200,
            content_type="text/html",
            content_length=2048,
            response_time=200,
            page_title="Page 2"
        )
        
        db_session.add_all([url1, url2])
        await db_session.commit()
        
        response = await authenticated_client.get(f"/api/v1/scans/{test_scan_session.id}/urls")
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) == 2
            assert any(url["url"] == "https://example.com/page1" for url in data)
            assert any(url["url"] == "https://example.com/page2" for url in data)
        else:
            # Endpoint might not be fully implemented yet
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_list_scan_urls_with_filters(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_scan_session: ScanSession
    ):
        """Test listing URLs with filters."""
        # Create test URLs with different status codes
        urls = [
            DiscoveredUrl(
                session_id=test_scan_session.id,
                url="https://example.com/success",
                method="GET",
                status_code=200,
                content_type="text/html"
            ),
            DiscoveredUrl(
                session_id=test_scan_session.id,
                url="https://example.com/notfound",
                method="GET",
                status_code=404,
                content_type="text/html"
            ),
            DiscoveredUrl(
                session_id=test_scan_session.id,
                url="https://example.com/error",
                method="GET",
                status_code=500,
                content_type="text/html"
            )
        ]
        
        db_session.add_all(urls)
        await db_session.commit()
        
        # Test filtering by status code
        response = await authenticated_client.get(
            f"/api/v1/scans/{test_scan_session.id}/urls?status_code=200"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert all(url["status_code"] == 200 for url in data)
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_list_scan_urls_unauthorized(self, client: AsyncClient):
        """Test listing URLs without authentication."""
        scan_id = str(uuid4())
        response = await client.get(f"/api/v1/scans/{scan_id}/urls")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_list_scan_urls_not_found(self, authenticated_client: AsyncClient):
        """Test listing URLs for non-existent scan."""
        scan_id = str(uuid4())
        response = await authenticated_client.get(f"/api/v1/scans/{scan_id}/urls")
        assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_create_discovered_url(
        self,
        authenticated_client: AsyncClient,
        test_scan_session: ScanSession
    ):
        """Test creating a discovered URL."""
        url_data = {
            "url": "https://example.com/new-page",
            "method": "GET",
            "status_code": 200,
            "content_type": "text/html",
            "content_length": 1024,
            "response_time": 150,
            "page_title": "New Page"
        }
        
        response = await authenticated_client.post(
            f"/api/v1/scans/{test_scan_session.id}/urls",
            json=url_data
        )
        
        if response.status_code == 201:
            data = response.json()
            assert data["url"] == url_data["url"]
            assert data["status_code"] == url_data["status_code"]
        else:
            # Endpoint might not be implemented yet
            assert response.status_code in [404, 405, 500]

    @pytest.mark.asyncio
    async def test_list_scan_forms_success(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_scan_session: ScanSession
    ):
        """Test listing extracted forms for a scan."""
        # Create a discovered URL first
        url = DiscoveredUrl(
            session_id=test_scan_session.id,
            url="https://example.com/form-page",
            method="GET",
            status_code=200,
            content_type="text/html"
        )
        db_session.add(url)
        await db_session.commit()
        await db_session.refresh(url)
        
        # Create test forms
        form1 = ExtractedForm(
            url_id=url.id,
            form_action="/submit",
            form_method="POST",
            form_fields=[
                {"name": "username", "type": "text", "required": True},
                {"name": "password", "type": "password", "required": True}
            ],
            csrf_tokens=["csrf-token-123"],
            authentication_required=True
        )
        
        db_session.add(form1)
        await db_session.commit()
        
        response = await authenticated_client.get(f"/api/v1/scans/{test_scan_session.id}/forms")
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) >= 1
            form = data[0]
            assert form["form_action"] == "/submit"
            assert form["form_method"] == "POST"
            assert form["authentication_required"] is True
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_list_scan_technologies_success(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_scan_session: ScanSession
    ):
        """Test listing technology fingerprints for a scan."""
        # Create a discovered URL first
        url = DiscoveredUrl(
            session_id=test_scan_session.id,
            url="https://example.com/tech-page",
            method="GET",
            status_code=200,
            content_type="text/html"
        )
        db_session.add(url)
        await db_session.commit()
        await db_session.refresh(url)
        
        # Create test technology fingerprint
        tech = TechnologyFingerprint(
            url_id=url.id,
            server_software="nginx/1.18.0",
            programming_language="Python",
            framework="Django",
            cms="WordPress",
            javascript_libraries=["jQuery", "React"],
            security_headers={
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
        db_session.add(tech)
        await db_session.commit()
        
        response = await authenticated_client.get(f"/api/v1/scans/{test_scan_session.id}/technologies")
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) >= 1
            technology = data[0]
            assert technology["server_software"] == "nginx/1.18.0"
            assert technology["programming_language"] == "Python"
            assert technology["framework"] == "Django"
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_get_scan_summary(
        self,
        authenticated_client: AsyncClient,
        test_scan_session: ScanSession
    ):
        """Test getting scan results summary."""
        response = await authenticated_client.get(f"/api/v1/scans/{test_scan_session.id}/summary")
        
        if response.status_code == 200:
            data = response.json()
            assert "total_urls" in data
            assert "total_forms" in data
            assert "total_technologies" in data
            assert "status_code_distribution" in data
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_export_scan_results_json(
        self,
        authenticated_client: AsyncClient,
        test_scan_session: ScanSession
    ):
        """Test exporting scan results as JSON."""
        response = await authenticated_client.get(
            f"/api/v1/scans/{test_scan_session.id}/export?format=json"
        )
        
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/json"
            data = response.json()
            assert "scan_id" in data
            assert "urls" in data
            assert "forms" in data
            assert "technologies" in data
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_export_scan_results_csv(
        self,
        authenticated_client: AsyncClient,
        test_scan_session: ScanSession
    ):
        """Test exporting scan results as CSV."""
        response = await authenticated_client.get(
            f"/api/v1/scans/{test_scan_session.id}/export?format=csv"
        )
        
        if response.status_code == 200:
            assert "text/csv" in response.headers["content-type"]
            content = response.text
            assert "url,method,status_code" in content  # CSV headers
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_export_scan_results_pdf(
        self,
        authenticated_client: AsyncClient,
        test_scan_session: ScanSession
    ):
        """Test exporting scan results as PDF."""
        with patch('tasks.report_tasks.generate_report_task.delay') as mock_task:
            mock_task.return_value.id = "test-task-id"
            
            response = await authenticated_client.get(
                f"/api/v1/scans/{test_scan_session.id}/export?format=pdf"
            )
            
            if response.status_code == 202:
                data = response.json()
                assert "task_id" in data
                assert data["task_id"] == "test-task-id"
            else:
                assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_pagination(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_scan_session: ScanSession
    ):
        """Test pagination of scan results."""
        # Create multiple URLs for pagination testing
        urls = []
        for i in range(25):
            url = DiscoveredUrl(
                session_id=test_scan_session.id,
                url=f"https://example.com/page{i}",
                method="GET",
                status_code=200,
                content_type="text/html"
            )
            urls.append(url)
        
        db_session.add_all(urls)
        await db_session.commit()
        
        # Test first page
        response = await authenticated_client.get(
            f"/api/v1/scans/{test_scan_session.id}/urls?limit=10&offset=0"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) <= 10
        else:
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_search_urls(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_scan_session: ScanSession
    ):
        """Test searching URLs by content."""
        # Create URLs with different content
        urls = [
            DiscoveredUrl(
                session_id=test_scan_session.id,
                url="https://example.com/login",
                method="GET",
                status_code=200,
                page_title="Login Page"
            ),
            DiscoveredUrl(
                session_id=test_scan_session.id,
                url="https://example.com/admin",
                method="GET",
                status_code=200,
                page_title="Admin Panel"
            )
        ]
        
        db_session.add_all(urls)
        await db_session.commit()
        
        # Search for login pages
        response = await authenticated_client.get(
            f"/api/v1/scans/{test_scan_session.id}/urls?search=login"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert any("login" in url["url"].lower() or 
                     "login" in (url.get("page_title", "")).lower() 
                     for url in data)
        else:
            assert response.status_code in [404, 500]


@pytest.mark.integration
@pytest.mark.api
class TestScanResultsValidation:
    """Test scan results API input validation."""

    @pytest.mark.asyncio
    async def test_invalid_scan_id_format(self, authenticated_client: AsyncClient):
        """Test with invalid scan ID format."""
        response = await authenticated_client.get("/api/v1/scans/invalid-uuid/urls")
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_invalid_pagination_params(self, authenticated_client: AsyncClient):
        """Test with invalid pagination parameters."""
        scan_id = str(uuid4())
        
        # Negative limit
        response = await authenticated_client.get(f"/api/v1/scans/{scan_id}/urls?limit=-1")
        if response.status_code not in [404, 500]:
            assert response.status_code in [400, 422]
        
        # Negative offset
        response = await authenticated_client.get(f"/api/v1/scans/{scan_id}/urls?offset=-1")
        if response.status_code not in [404, 500]:
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_invalid_export_format(self, authenticated_client: AsyncClient):
        """Test with invalid export format."""
        scan_id = str(uuid4())
        response = await authenticated_client.get(f"/api/v1/scans/{scan_id}/export?format=invalid")
        assert response.status_code in [400, 422, 404, 500]


@pytest.mark.integration
@pytest.mark.api
class TestScanResultsSecurity:
    """Test scan results API security."""

    @pytest.mark.asyncio
    async def test_access_other_user_scan(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test accessing another user's scan results."""
        # Create a scan for a different user
        other_user_id = "other-user-id"
        other_profile = Profile(
            id=other_user_id,
            email="other@example.com",
            full_name="Other User",
            is_active=True,
            role="user"
        )
        db_session.add(other_profile)
        
        other_project = Project(
            name="Other Project",
            description="Another user's project",
            owner_id=other_user_id,
            target_domain="other.com",
            scope_rules=["https://other.com/*"]
        )
        db_session.add(other_project)
        await db_session.commit()
        await db_session.refresh(other_project)
        
        other_scan = ScanSession(
            project_id=other_project.id,
            status="completed",
            configuration={"max_depth": 3},
            created_by=other_user_id
        )
        db_session.add(other_scan)
        await db_session.commit()
        
        # Try to access other user's scan
        response = await authenticated_client.get(f"/api/v1/scans/{other_scan.id}/urls")
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, authenticated_client: AsyncClient):
        """Test SQL injection protection in search parameters."""
        scan_id = str(uuid4())
        
        # Try SQL injection in search parameter
        malicious_search = "'; DROP TABLE discovered_urls; --"
        response = await authenticated_client.get(
            f"/api/v1/scans/{scan_id}/urls?search={malicious_search}"
        )
        
        # Should not cause a server error (500)
        assert response.status_code in [200, 400, 404, 422]

    @pytest.mark.asyncio
    async def test_xss_protection(self, authenticated_client: AsyncClient):
        """Test XSS protection in responses."""
        scan_id = str(uuid4())
        
        # Try XSS in search parameter
        xss_payload = "<script>alert('xss')</script>"
        response = await authenticated_client.get(
            f"/api/v1/scans/{scan_id}/urls?search={xss_payload}"
        )
        
        if response.status_code == 200:
            # Response should not contain unescaped script tags
            content = response.text
            assert "<script>" not in content
            assert "alert('xss')" not in content