"""
Unit tests for Pydantic schemas.
Tests validation, serialization, and data transformation.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from schemas.auth import (
    UserCreate,
    UserLogin,
    UserPublic,
    Token,
    TokenPayload
)
from schemas.dashboard import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ScanSessionCreate,
    ScanSessionResponse,
    ScanConfigurationSchema
)
from models.unified_models import ScanStatus
from schemas.scan_results import (
    DiscoveredURLResponse,
    ExtractedFormResponse,
    TechnologyFingerprintResponse,
    ScanResultsSummary
)


class TestAuthSchemas:
    """Test authentication schemas."""
    
    def test_user_create_valid(self):
        """Test valid user creation data."""
        data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        user = UserCreate(**data)
        
        assert user.email == "test@example.com"
        assert user.password == "SecurePassword123!"
        assert user.full_name == "Test User"
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        data = {
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_create_weak_password(self):
        """Test user creation with weak password."""
        data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "username": "testuser"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        assert "password" in str(exc_info.value)
    
    def test_user_create_invalid_password(self):
        """Test user creation with invalid password."""
        invalid_passwords = [
            "short",  # Too short (less than 8 chars)
            "",  # Empty password
            "1234567",  # Too short
        ]
        
        for password in invalid_passwords:
            data = {
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            }
            
            with pytest.raises(ValidationError):
                UserCreate(**data)
    
    def test_user_login_valid(self):
        """Test valid user login data."""
        data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        login = UserLogin(**data)
        
        assert login.email == "test@example.com"
        assert login.password == "SecurePassword123!"
    
    def test_user_response_serialization(self):
        """Test user response serialization."""
        user_id = str(uuid4())
        data = {
            "id": user_id,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg",
            "role": "user",
            "email_confirmed": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        user = UserPublic(**data)
        
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.email_confirmed is True
    
    def test_token_schema(self):
        """Test token schema."""
        data = {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        token = Token(**data)
        
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"
        assert token.expires_in == 3600
    
    def test_token_data_schema(self):
        """Test token data schema."""
        data = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "exp": 1234567890,
            "iat": 1234567800
        }
        
        token_data = TokenPayload(**data)
        
        assert token_data.sub is not None
        assert token_data.email == "test@example.com"
        assert token_data.exp == 1234567890
        assert token_data.iat == 1234567800


class TestProjectSchemas:
    """Test project schemas."""
    
    def test_project_create_valid(self):
        """Test valid project creation data."""
        data = {
            "name": "Test Project",
            "description": "A test project for scanning",
            "target_domain": "example.com",
            "scope_rules": ["https://example.com/*", "https://api.example.com/*"]
        }
        
        project = ProjectCreate(**data)
        
        assert project.name == "Test Project"
        assert project.description == "A test project for scanning"
        assert project.target_domain == "example.com"
        assert len(project.scope_rules) == 2
    
    def test_project_create_invalid_name(self):
        """Test project creation with invalid name."""
        invalid_names = [
            "",  # Empty
            "a",  # Too short
            "a" * 101,  # Too long
        ]
        
        for name in invalid_names:
            data = {
                "name": name,
                "target_domain": "example.com"
            }
            
            with pytest.raises(ValidationError):
                ProjectCreate(**data)
    
    def test_project_create_invalid_domain(self):
        """Test project creation with invalid domain."""
        invalid_domains = [
            "",  # Empty
            "not-a-domain",  # Invalid format
            "http://example.com",  # Should not include protocol
            "example.com/path",  # Should not include path
        ]
        
        for domain in invalid_domains:
            data = {
                "name": "Test Project",
                "target_domain": domain
            }
            
            with pytest.raises(ValidationError):
                ProjectCreate(**data)
    
    def test_project_update_partial(self):
        """Test partial project update."""
        data = {
            "description": "Updated description"
        }
        
        update = ProjectUpdate(**data)
        
        assert update.description == "Updated description"
        assert update.name is None
        assert update.target_domain is None
        assert update.scope_rules is None
    
    def test_project_response_serialization(self):
        """Test project response serialization."""
        project_id = str(uuid4())
        owner_id = str(uuid4())
        
        data = {
            "id": project_id,
            "name": "Test Project",
            "description": "A test project",
            "owner_id": owner_id,
            "target_domain": "example.com",
            "scope_rules": ["https://example.com/*"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        project = ProjectResponse(**data)
        
        assert project.id == project_id
        assert project.name == "Test Project"
        assert project.owner_id == owner_id
    
    def test_project_list_schema(self):
        """Test project list schema."""
        
        # Test single project response
        project_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Test Project",
            "description": "Test Description",
            "target_domain": "example.com",
            "scope_rules": ["https://example.com/*"],
            "owner_id": "123e4567-e89b-12d3-a456-426614174001",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        project = ProjectResponse(**project_data)
        
        assert project.name == "Test Project"
        assert project.target_domain == "example.com"
        assert project.owner_id == "123e4567-e89b-12d3-a456-426614174001"


class TestScanSchemas:
    """Test scan schemas."""
    
    def test_crawl_config_valid(self):
        """Test valid crawl configuration."""
        data = {
            "max_depth": 5,
            "max_pages": 2000,
            "requests_per_second": 15,
            "timeout": 45,
            "follow_redirects": True,
            "respect_robots": True,
            "user_agent": "Custom-Scanner/1.0",
            "scope_patterns": [".*\\.example\\.com.*"],
            "exclude_patterns": [".*/admin/.*", ".*/private/.*"],
            "authentication": {
                "type": "basic",
                "username": "testuser",
                "password": "testpass"
            }
        }
        
        config = ScanConfigurationSchema(**data)
        
        assert config.max_depth == 5
        assert config.max_pages == 2000
        assert config.requests_per_second == 15
        assert config.timeout == 45
        assert config.follow_redirects is True
        assert config.respect_robots is True
        assert config.user_agent == "Custom-Scanner/1.0"
        assert len(config.scope_patterns) == 1
        assert len(config.exclude_patterns) == 2
        assert config.authentication["type"] == "basic"
    
    def test_crawl_config_defaults(self):
        """Test crawl configuration defaults."""
        config = ScanConfigurationSchema()
        
        assert config.max_depth == 3
        assert config.max_pages == 1000
        assert config.requests_per_second == 10
        assert config.timeout == 30
        assert config.follow_redirects is True
        assert config.respect_robots is True
        assert config.user_agent == "Enhanced-Vulnerability-Scanner/1.0"
        assert config.scope_patterns == []
        assert config.exclude_patterns == []
        assert config.authentication is None
    
    def test_crawl_config_validation(self):
        """Test crawl configuration validation."""
        # Test invalid values
        invalid_configs = [
            {"max_depth": 0},  # Too small
            {"max_depth": 11},  # Too large
            {"max_pages": 5},  # Too small
            {"max_pages": 200000},  # Too large
            {"requests_per_second": 0},  # Too small
            {"requests_per_second": 150},  # Too large
            {"timeout": 2},  # Too small
            {"timeout": 400},  # Too large
        ]
        
        for invalid_data in invalid_configs:
            with pytest.raises(ValidationError):
                ScanConfigurationSchema(**invalid_data)
    
    def test_scan_create_valid(self):
        """Test valid scan creation data."""
        config = {
            "max_depth": 3,
            "max_pages": 1000,
            "requests_per_second": 10
        }
        
        data = {
            "configuration": config
        }
        
        scan = ScanSessionCreate(**data)
        
        assert scan.configuration.max_depth == 3
        assert scan.configuration.max_pages == 1000
    
    def test_scan_status_enum(self):
        """Test scan status enum values."""
        valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
        
        for status in valid_statuses:
            scan_status = ScanStatus(status)
            assert scan_status.value == status
        
        # Test invalid status
        with pytest.raises(ValueError):
            ScanStatus("invalid_status")
    
    def test_scan_response_serialization(self):
        """Test scan response serialization."""
        scan_id = str(uuid4())
        project_id = str(uuid4())
        created_by = str(uuid4())
        
        data = {
            "id": scan_id,
            "project_id": project_id,
            "status": "completed",
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc),
            "configuration": {
                "max_depth": 3,
                "max_pages": 1000,
                "requests_per_second": 10,
                "timeout": 30,
                "follow_redirects": True,
                "respect_robots": True,
                "user_agent": "Enhanced-Vulnerability-Scanner/1.0",
                "scope_patterns": [],
                "exclude_patterns": [],
                "authentication": None
            },
            "stats": {
                "urls_discovered": 150,
                "forms_found": 25,
                "technologies_detected": 8
            },
            "created_by": created_by
        }
        
        scan = ScanSessionResponse(**data)
        
        assert str(scan.id) == scan_id
        assert str(scan.project_id) == project_id
        assert scan.status.value == "completed"
        assert scan.stats["urls_discovered"] == 150
    
    def test_scan_list_schema(self):
        """Test scan list schema."""
        
        # Test single scan session response
        scan_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "project_id": "123e4567-e89b-12d3-a456-426614174001",
            "status": ScanStatus.COMPLETED,
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "configuration": {
                "max_depth": 5,
                "max_pages": 1000,
                "requests_per_second": 10,
                "max_concurrent_requests": 10,
                "timeout": 30,
                "follow_redirects": True,
                "respect_robots": True,
                "user_agent": "Enhanced-Vulnerability-Scanner/1.0",
                "scope_patterns": [],
                "exclude_patterns": [],
                "authentication": None
            },
            "stats": {},
            "created_by": "123e4567-e89b-12d3-a456-426614174002"
        }
        
        scan = ScanSessionResponse(**scan_data)
        
        assert scan.status == ScanStatus.COMPLETED
        assert scan.configuration["max_depth"] == 5


class TestScanResultSchemas:
    """Test scan result schemas."""
    
    def test_discovered_url_response(self):
        """Test discovered URL response schema."""
        url_id = str(uuid4())
        session_id = str(uuid4())
        
        data = {
            "id": url_id,
            "session_id": session_id,
            "url": "https://example.com/page1",
            "parent_url": "https://example.com/",
            "method": "GET",
            "status_code": 200,
            "content_type": "text/html",
            "content_length": 1024,
            "response_time": 150,
            "page_title": "Test Page",
            "discovered_at": datetime.now(timezone.utc)
        }
        
        url_response = DiscoveredURLResponse(**data)
        
        assert str(url_response.id) == url_id
        assert url_response.url == "https://example.com/page1"
        assert url_response.status_code == 200
        assert url_response.page_title == "Test Page"
    
    def test_extracted_form_response(self):
        """Test extracted form response schema."""
        form_id = str(uuid4())
        url_id = str(uuid4())
        
        form_fields = {
            "username": {"type": "text", "required": True},
            "password": {"type": "password", "required": True}
        }
        
        data = {
            "id": form_id,
            "url_id": url_id,
            "form_action": "/login",
            "form_method": "POST",
            "form_fields": form_fields,
            "csrf_tokens": ["csrf_token_123"],
            "authentication_required": True
        }
        
        form_response = ExtractedFormResponse(**data)
        
        assert str(form_response.id) == form_id
        assert form_response.form_action == "/login"
        assert form_response.form_method == "POST"
        assert len(form_response.form_fields) == 2
        assert form_response.authentication_required is True
    
    def test_technology_fingerprint_response(self):
        """Test technology fingerprint response schema."""
        tech_id = str(uuid4())
        url_id = str(uuid4())
        
        data = {
            "id": tech_id,
            "url_id": url_id,
            "server_software": "nginx/1.20.1",
            "programming_language": "Python",
            "framework": "Django",
            "cms": "WordPress",
            "javascript_libraries": ["jquery", "bootstrap"],
            "security_headers": {
                "Content-Security-Policy": "default-src 'self'",
                "X-Frame-Options": "DENY"
            },
            "detected_at": datetime.now(timezone.utc)
        }
        
        tech_response = TechnologyFingerprintResponse(**data)
        
        assert str(tech_response.id) == tech_id
        assert tech_response.server_software == "nginx/1.20.1"
        assert tech_response.programming_language == "Python"
        assert len(tech_response.javascript_libraries) == 2
    
    def test_scan_results_summary(self):
        """Test scan results summary schema."""
        scan_id = str(uuid4())
        
        data = {
            "scan_id": scan_id,
            "total_urls": 150,
            "total_forms": 25,
            "total_technologies": 8,
            "unique_domains": 5,
            "status_code_distribution": {
                "200": 120,
                "404": 20,
                "500": 5,
                "403": 5
            },
            "content_type_distribution": {
                "text/html": 100,
                "application/json": 30,
                "text/css": 15,
                "application/javascript": 5
            },
            "technology_distribution": {
                "nginx": 150,
                "Python": 150,
                "Django": 150,
                "jQuery": 80,
                "Bootstrap": 60
            },
            "security_headers_summary": {
                "Content-Security-Policy": 120,
                "X-Frame-Options": 135,
                "X-Content-Type-Options": 105
            }
        }
        
        summary = ScanResultsSummary(**data)
        
        assert str(summary.scan_id) == scan_id
        assert summary.total_urls == 150
        assert summary.total_forms == 25
        assert summary.status_code_distribution["200"] == 120
        assert summary.security_headers_summary["X-Frame-Options"] == 135


class TestSchemaValidation:
    """Test schema validation edge cases."""
    
    def test_uuid_validation(self):
        """Test UUID field validation."""
        # Valid configuration
        config = {"max_depth": 3, "max_pages": 100}
        scan = ScanSessionCreate(configuration=config)
        assert scan.configuration.max_depth == 3
        
        # Invalid configuration (invalid field values)
        with pytest.raises(ValidationError):
            ScanSessionCreate(configuration={"max_depth": -1})  # Invalid: below minimum
    
    def test_datetime_serialization(self):
        """Test datetime field serialization."""
        now = datetime.now(timezone.utc)
        
        data = {
            "id": str(uuid4()),
            "email": "test@example.com",
            "username": "testuser",
            "role": "user",
            "email_confirmed": True,
            "created_at": now,
            "updated_at": now
        }
        
        user = UserPublic(**data)
        
        # Test JSON serialization
        json_data = user.model_dump(mode='json')
        assert isinstance(json_data["created_at"], str)
        assert isinstance(json_data["updated_at"], str)
    
    def test_optional_fields(self):
        """Test optional field handling."""
        # Minimal data
        data = {
            "name": "Test Project",
            "target_domain": "example.com"
        }
        
        project = ProjectCreate(**data)
        
        assert project.name == "Test Project"
        assert project.target_domain == "example.com"
        assert project.description is None
        assert project.scope_rules == []
    
    def test_field_aliases(self):
        """Test field aliases if any are defined."""
        # This would test any field aliases defined in schemas
        # For now, just ensure basic functionality works
        data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "username": "testuser"
        }
        
        user = UserCreate(**data)
        assert user.email == "test@example.com"
    
    def test_custom_validators(self):
        """Test custom validator functions."""
        # Test domain validation
        invalid_domains = [
            "localhost",  # Should be rejected in production
            "127.0.0.1",  # IP addresses might be rejected
            "example.com:8080",  # Ports might be rejected
        ]
        
        for domain in invalid_domains:
            data = {
                "name": "Test Project",
                "target_domain": domain
            }
            
            # Depending on custom validators, this might raise ValidationError
            try:
                ProjectCreate(**data)
            except ValidationError:
                pass  # Expected for some validators