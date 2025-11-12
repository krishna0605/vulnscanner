"""
Tests for the session manager component.
Tests authentication, cookie management, and session persistence.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock
from bs4 import BeautifulSoup

from crawler.session import SessionManager


class TestSessionManager:
    """Test the SessionManager class."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock aiohttp ClientSession."""
        session = AsyncMock(spec=aiohttp.ClientSession)
        return session
    
    @pytest.fixture
    def session_manager(self, mock_session):
        """Create a SessionManager instance for testing."""
        return SessionManager(session=mock_session)
    
    def test_session_manager_initialization(self, session_manager, mock_session):
        """Test SessionManager initialization."""
        assert session_manager.session == mock_session
        assert not session_manager.authenticated
        assert session_manager.csrf_tokens == {}
        assert session_manager.login_config is None
        assert session_manager.base_url == ""
    
    @pytest.mark.asyncio
    async def test_configure_authentication_disabled(self, session_manager):
        """Test authentication configuration when disabled."""
        auth_config = {"enabled": False}
        base_url = "https://example.com"
        
        await session_manager.configure_authentication(auth_config, base_url)
        
        assert session_manager.login_config == auth_config
        assert session_manager.base_url == base_url
        assert not session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_configure_authentication_enabled(self, session_manager):
        """Test authentication configuration when enabled."""
        auth_config = {
            "enabled": True,
            "login_url": "/login",
            "username": "testuser",
            "password": "testpass",
            "username_field": "username",
            "password_field": "password"
        }
        base_url = "https://example.com"
        
        # Mock the login process
        session_manager._perform_login = AsyncMock()
        
        await session_manager.configure_authentication(auth_config, base_url)
        
        assert session_manager.login_config == auth_config
        assert session_manager.base_url == base_url
        session_manager._perform_login.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_login_success(self, session_manager, mock_session):
        """Test successful login process."""
        # Setup login configuration
        session_manager.login_config = {
            "login_url": "/login",
            "username": "testuser",
            "password": "testpass",
            "username_field": "username",
            "password_field": "password"
        }
        session_manager.base_url = "https://example.com"
        
        # Mock login form response
        login_form_html = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="hidden" name="csrf_token" value="abc123">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
        """
        
        # Mock responses
        form_response = AsyncMock()
        form_response.text.return_value = login_form_html
        form_response.status = 200
        
        login_response = AsyncMock()
        login_response.status = 200
        login_response.url = "https://example.com/dashboard"  # Redirect indicates success
        
        mock_session.get.return_value.__aenter__.return_value = form_response
        mock_session.post.return_value.__aenter__.return_value = login_response
        
        # Mock CSRF token extraction
        session_manager._extract_csrf_token = MagicMock(return_value="abc123")
        
        # Perform login
        await session_manager._perform_login()
        
        # Verify login was attempted
        mock_session.get.assert_called_once()
        mock_session.post.assert_called_once()
        assert session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_perform_login_failure(self, session_manager, mock_session):
        """Test failed login process."""
        # Setup login configuration
        session_manager.login_config = {
            "login_url": "/login",
            "username": "testuser",
            "password": "wrongpass",
            "username_field": "username",
            "password_field": "password"
        }
        session_manager.base_url = "https://example.com"
        
        # Mock login form response
        login_form_html = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
        """
        
        # Mock responses
        form_response = AsyncMock()
        form_response.text.return_value = login_form_html
        form_response.status = 200
        
        login_response = AsyncMock()
        login_response.status = 401  # Unauthorized
        login_response.url = "https://example.com/login"  # No redirect
        
        mock_session.get.return_value.__aenter__.return_value = form_response
        mock_session.post.return_value.__aenter__.return_value = login_response
        
        # Perform login
        await session_manager._perform_login()
        
        # Verify login failed
        assert not session_manager.authenticated
    
    def test_extract_csrf_token_success(self, session_manager):
        """Test successful CSRF token extraction."""
        html_content = """
        <html>
            <body>
                <form>
                    <input type="hidden" name="csrf_token" value="abc123">
                    <input type="hidden" name="_token" value="def456">
                </form>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        token = session_manager._extract_csrf_token(soup)
        
        # Should find the first CSRF token
        assert token in ["abc123", "def456"]
    
    def test_extract_csrf_token_not_found(self, session_manager):
        """Test CSRF token extraction when no token is present."""
        html_content = """
        <html>
            <body>
                <form>
                    <input type="text" name="username">
                    <input type="password" name="password">
                </form>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        token = session_manager._extract_csrf_token(soup)
        
        assert token is None
    
    def test_extract_csrf_token_meta_tag(self, session_manager):
        """Test CSRF token extraction from meta tag."""
        html_content = """
        <html>
            <head>
                <meta name="csrf-token" content="meta123">
            </head>
            <body>
                <form>
                    <input type="text" name="username">
                </form>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        token = session_manager._extract_csrf_token(soup)
        
        assert token == "meta123"
    
    @pytest.mark.asyncio
    async def test_get_csrf_token_cached(self, session_manager):
        """Test CSRF token retrieval from cache."""
        url = "https://example.com/form"
        cached_token = "cached123"
        
        # Add token to cache
        session_manager.csrf_tokens[url] = cached_token
        
        token = await session_manager.get_csrf_token(url)
        
        assert token == cached_token
    
    @pytest.mark.asyncio
    async def test_get_csrf_token_fetch_new(self, session_manager, mock_session):
        """Test CSRF token fetching when not cached."""
        url = "https://example.com/form"
        
        # Mock response with CSRF token
        html_content = """
        <html>
            <body>
                <form>
                    <input type="hidden" name="csrf_token" value="new123">
                </form>
            </body>
        </html>
        """
        
        response = AsyncMock()
        response.text.return_value = html_content
        response.status = 200
        
        mock_session.get.return_value.__aenter__.return_value = response
        
        # Mock CSRF token extraction
        session_manager._extract_csrf_token = MagicMock(return_value="new123")
        
        token = await session_manager.get_csrf_token(url)
        
        assert token == "new123"
        assert session_manager.csrf_tokens[url] == "new123"
        mock_session.get.assert_called_once_with(url)
    
    @pytest.mark.asyncio
    async def test_is_authenticated_check(self, session_manager, mock_session):
        """Test authentication status checking."""
        # Mock response for authentication check
        response = AsyncMock()
        response.status = 200
        response.url = "https://example.com/dashboard"
        
        mock_session.get.return_value.__aenter__.return_value = response
        
        # Test when authenticated
        session_manager.authenticated = True
        is_auth = await session_manager.is_authenticated()
        assert is_auth
        
        # Test when not authenticated
        session_manager.authenticated = False
        is_auth = await session_manager.is_authenticated()
        assert not is_auth
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, session_manager, mock_session):
        """Test session cookie persistence."""
        # Mock cookie jar
        mock_session.cookie_jar = MagicMock()
        mock_session.cookie_jar.filter_cookies.return_value = {
            "sessionid": "session123",
            "csrftoken": "csrf456"
        }
        
        cookies = session_manager.get_session_cookies("https://example.com")
        
        # Verify cookies are retrieved
        mock_session.cookie_jar.filter_cookies.assert_called_once()
        assert cookies == {
            "sessionid": "session123",
            "csrftoken": "csrf456"
        }
    
    def test_build_login_data(self, session_manager):
        """Test login data building."""
        session_manager.login_config = {
            "username": "testuser",
            "password": "testpass",
            "username_field": "email",
            "password_field": "pwd"
        }
        
        csrf_token = "token123"
        
        login_data = session_manager._build_login_data(csrf_token)
        
        expected_data = {
            "email": "testuser",
            "pwd": "testpass",
            "csrf_token": "token123"
        }
        
        assert login_data == expected_data
    
    def test_build_login_data_no_csrf(self, session_manager):
        """Test login data building without CSRF token."""
        session_manager.login_config = {
            "username": "testuser",
            "password": "testpass",
            "username_field": "username",
            "password_field": "password"
        }
        
        login_data = session_manager._build_login_data(None)
        
        expected_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        assert login_data == expected_data
    
    @pytest.mark.asyncio
    async def test_logout_functionality(self, session_manager, mock_session):
        """Test logout functionality."""
        session_manager.authenticated = True
        session_manager.csrf_tokens = {"url1": "token1", "url2": "token2"}
        
        # Mock logout response
        response = AsyncMock()
        response.status = 200
        
        mock_session.post.return_value.__aenter__.return_value = response
        
        await session_manager.logout("/logout")
        
        # Verify logout was called and state was reset
        mock_session.post.assert_called_once()
        assert not session_manager.authenticated
        assert session_manager.csrf_tokens == {}
    
    @pytest.mark.asyncio
    async def test_session_timeout_handling(self, session_manager, mock_session):
        """Test handling of session timeouts."""
        session_manager.authenticated = True
        
        # Mock timeout response (401 or redirect to login)
        response = AsyncMock()
        response.status = 401
        
        mock_session.get.return_value.__aenter__.return_value = response
        
        # Mock re-authentication
        session_manager._perform_login = AsyncMock()
        
        # Simulate session timeout detection and re-authentication
        await session_manager._handle_session_timeout()
        
        session_manager._perform_login.assert_called_once()
    
    def test_cookie_domain_handling(self, session_manager):
        """Test proper cookie domain handling."""
        test_cases = [
            ("https://example.com/path", "example.com"),
            ("https://subdomain.example.com/", "subdomain.example.com"),
            ("http://localhost:8080/", "localhost"),
        ]
        
        for url, expected_domain in test_cases:
            domain = session_manager._extract_domain(url)
            assert domain == expected_domain
    
    @pytest.mark.asyncio
    async def test_concurrent_csrf_token_requests(self, session_manager, mock_session):
        """Test handling of concurrent CSRF token requests."""
        url = "https://example.com/form"
        
        # Mock response
        html_content = """
        <form>
            <input type="hidden" name="csrf_token" value="concurrent123">
        </form>
        """
        
        response = AsyncMock()
        response.text.return_value = html_content
        response.status = 200
        
        mock_session.get.return_value.__aenter__.return_value = response
        session_manager._extract_csrf_token = MagicMock(return_value="concurrent123")
        
        # Make concurrent requests
        tasks = [
            session_manager.get_csrf_token(url),
            session_manager.get_csrf_token(url),
            session_manager.get_csrf_token(url)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should return the same token
        assert all(token == "concurrent123" for token in results)
        
        # Should only make one HTTP request due to caching
        assert mock_session.get.call_count <= 1