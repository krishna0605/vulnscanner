"""
Integration tests for authentication API endpoints.
Tests user registration, login, token validation, and auth flows.
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch

from main import app


class TestAuthAPI:
    """Integration tests for authentication endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_dev_test_endpoint(self, client: AsyncClient):
        """Test development test endpoint."""
        response = await client.get("/api/auth/dev-test")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "development_mode" in data
        assert "skip_supabase" in data
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        with patch('services.auth_service.auth_service.register_user') as mock_register:
            # Mock successful registration
            mock_user = {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "test@example.com",
                "full_name": "Test User",
                "created_at": "2024-01-01T00:00:00Z"
            }
            mock_token = "mock_access_token"
            mock_register.return_value = (mock_user, mock_token)
            
            response = await client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["full_name"] == "Test User"
            assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email."""
        user_data = {
            "email": "existing@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        with patch('services.auth_service.auth_service.register_user') as mock_register:
            # Mock duplicate email error
            mock_register.side_effect = Exception("Email already registered")
            
            response = await client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "already registered" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        user_data = {
            "email": "test@example.com",
            "password": "weak",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        user_data = {
            "email": "test@example.com"
            # Missing password and full_name
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful user login."""
        login_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        with patch('services.auth_service.auth_service.login_user') as mock_login:
            # Mock successful login
            mock_response = {
                "access_token": "mock_access_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "test@example.com",
                    "full_name": "Test User"
                }
            }
            mock_login.return_value = mock_response
            
            response = await client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "mock_access_token"
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "test@example.com",
            "password": "WrongPassword"
        }
        
        with patch('services.auth_service.auth_service.login_user') as mock_login:
            # Mock invalid credentials
            from fastapi import HTTPException
            mock_login.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
            response = await client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "invalid" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        
        with patch('services.auth_service.auth_service.login_user') as mock_login:
            # Mock user not found
            from fastapi import HTTPException
            mock_login.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
            response = await client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient):
        """Test getting current user with valid token."""
        with patch('core.auth_deps.get_current_user') as mock_get_user:
            # Mock authenticated user
            mock_user = {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "test@example.com",
                "full_name": "Test User"
            }
            mock_get_user.return_value = mock_user
            
            headers = {"Authorization": "Bearer mock_token"}
            response = await client.get("/api/auth/me", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/auth/me", headers=headers)
        
        # Should return 401 for invalid token
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/api/auth/me")
        
        # Should return 401 for missing token
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient):
        """Test token refresh with valid refresh token."""
        refresh_data = {
            "refresh_token": "valid_refresh_token"
        }
        
        with patch('services.auth_service.auth_service.refresh_token') as mock_refresh:
            # Mock successful refresh
            mock_response = {
                "access_token": "new_access_token",
                "token_type": "bearer",
                "expires_in": 3600
            }
            mock_refresh.return_value = mock_response
            
            response = await client.post("/api/auth/refresh", json=refresh_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "new_access_token"
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid refresh token."""
        refresh_data = {
            "refresh_token": "invalid_refresh_token"
        }
        
        with patch('services.auth_service.auth_service.refresh_token') as mock_refresh:
            # Mock invalid refresh token
            from fastapi import HTTPException
            mock_refresh.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
            response = await client.post("/api/auth/refresh", json=refresh_data)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient):
        """Test successful logout."""
        with patch('core.auth_deps.get_current_user') as mock_get_user:
            mock_user = {"id": "123e4567-e89b-12d3-a456-426614174000"}
            mock_get_user.return_value = mock_user
            
            with patch('services.auth_service.auth_service.logout_user') as mock_logout:
                mock_logout.return_value = {"message": "Logged out successfully"}
                
                headers = {"Authorization": "Bearer valid_token"}
                response = await client.post("/api/auth/logout", headers=headers)
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "message" in data
    
    @pytest.mark.asyncio
    async def test_logout_no_token(self, client: AsyncClient):
        """Test logout without authentication token."""
        response = await client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_password_reset_request(self, client: AsyncClient):
        """Test password reset request."""
        reset_data = {
            "email": "test@example.com"
        }
        
        with patch('services.auth_service.auth_service.request_password_reset') as mock_reset:
            mock_reset.return_value = {"message": "Password reset email sent"}
            
            response = await client.post("/api/auth/password-reset", json=reset_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_password_reset_invalid_email(self, client: AsyncClient):
        """Test password reset with invalid email format."""
        reset_data = {
            "email": "invalid-email"
        }
        
        response = await client.post("/api/auth/password-reset", json=reset_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_email_verification(self, client: AsyncClient):
        """Test email verification."""
        verify_data = {
            "token": "verification_token"
        }
        
        with patch('services.auth_service.auth_service.verify_email') as mock_verify:
            mock_verify.return_value = {"message": "Email verified successfully"}
            
            response = await client.post("/api/auth/verify-email", json=verify_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_email_verification_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token."""
        verify_data = {
            "token": "invalid_token"
        }
        
        with patch('services.auth_service.auth_service.verify_email') as mock_verify:
            from fastapi import HTTPException
            mock_verify.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
            
            response = await client.post("/api/auth/verify-email", json=verify_data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthIntegration:
    """Integration tests for complete authentication flows."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_complete_registration_login_flow(self, client: AsyncClient):
        """Test complete user registration and login flow."""
        # Step 1: Register user
        user_data = {
            "email": "integration@example.com",
            "password": "SecurePassword123!",
            "full_name": "Integration Test User"
        }
        
        with patch('services.auth_service.auth_service.register_user') as mock_register:
            mock_user = {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "integration@example.com",
                "full_name": "Integration Test User",
                "created_at": "2024-01-01T00:00:00Z"
            }
            mock_token = "registration_token"
            mock_register.return_value = (mock_user, mock_token)
            
            register_response = await client.post("/api/auth/register", json=user_data)
            assert register_response.status_code == status.HTTP_200_OK
        
        # Step 2: Login with registered user
        login_data = {
            "email": "integration@example.com",
            "password": "SecurePassword123!"
        }
        
        with patch('services.auth_service.auth_service.login_user') as mock_login:
            mock_login_response = {
                "access_token": "login_access_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": mock_user
            }
            mock_login.return_value = mock_login_response
            
            login_response = await client.post("/api/auth/login", json=login_data)
            assert login_response.status_code == status.HTTP_200_OK
            
            login_data = login_response.json()
            access_token = login_data["access_token"]
        
        # Step 3: Access protected endpoint
        with patch('core.auth_deps.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_user
            
            headers = {"Authorization": f"Bearer {access_token}"}
            me_response = await client.get("/api/auth/me", headers=headers)
            assert me_response.status_code == status.HTTP_200_OK
            
            user_data = me_response.json()
            assert user_data["email"] == "integration@example.com"
    
    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, client: AsyncClient):
        """Test token refresh flow."""
        # Step 1: Login to get tokens
        login_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        with patch('services.auth_service.auth_service.login_user') as mock_login:
            mock_response = {
                "access_token": "initial_access_token",
                "refresh_token": "valid_refresh_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "test@example.com"
                }
            }
            mock_login.return_value = mock_response
            
            login_response = await client.post("/api/auth/login", json=login_data)
            assert login_response.status_code == status.HTTP_200_OK
            
            tokens = login_response.json()
            refresh_token = tokens.get("refresh_token")
        
        # Step 2: Refresh token
        if refresh_token:
            refresh_data = {"refresh_token": refresh_token}
            
            with patch('services.auth_service.auth_service.refresh_token') as mock_refresh:
                mock_refresh_response = {
                    "access_token": "new_access_token",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
                mock_refresh.return_value = mock_refresh_response
                
                refresh_response = await client.post("/api/auth/refresh", json=refresh_data)
                assert refresh_response.status_code == status.HTTP_200_OK
                
                new_tokens = refresh_response.json()
                assert new_tokens["access_token"] == "new_access_token"
    
    @pytest.mark.asyncio
    async def test_authentication_middleware_integration(self, client: AsyncClient):
        """Test authentication middleware with various scenarios."""
        # Test 1: No token
        response = await client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test 2: Invalid token format
        headers = {"Authorization": "InvalidFormat token"}
        response = await client.get("/api/v1/projects/", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test 3: Valid token format but invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/projects/", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test 4: Valid token
        with patch('core.auth_deps.get_current_user') as mock_get_user:
            mock_user = {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "test@example.com"
            }
            mock_get_user.return_value = mock_user
            
            headers = {"Authorization": "Bearer valid_token"}
            
            # Mock the database query for projects
            with patch('db.session.get_db'):
                response = await client.get("/api/v1/projects/", headers=headers)
                # Should not be 401 (might be other status based on implementation)
                assert response.status_code != status.HTTP_401_UNAUTHORIZED