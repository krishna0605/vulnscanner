"""
Unit tests for the session management module.
Tests authentication, CSRF token handling, and session state management.
"""

import pytest
from unittest.mock import Mock
import aiohttp
from aioresponses import aioresponses
from crawler.session import SessionManager


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock(spec=aiohttp.ClientSession)
        self.mock_session.headers = {}
        self.mock_session.cookie_jar = Mock()
        self.session_manager = SessionManager(self.mock_session)
    
    def test_initialization(self):
        """Test SessionManager initialization."""
        assert self.session_manager.session == self.mock_session
        assert not self.session_manager.authenticated
        assert self.session_manager.csrf_tokens == {}
        assert self.session_manager.login_config is None
        assert self.session_manager.base_url == ""
    
    @pytest.mark.asyncio
    async def test_configure_authentication_disabled(self):
        """Test authentication configuration when disabled."""
        auth_config = {'enabled': False}
        base_url = 'https://example.com'
        
        await self.session_manager.configure_authentication(auth_config, base_url)
        
        assert self.session_manager.login_config == auth_config
        assert self.session_manager.base_url == base_url
        assert not self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_configure_authentication_enabled(self):
        """Test authentication configuration when enabled."""
        auth_config = {
            'enabled': True,
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        base_url = 'https://example.com'
        
        with aioresponses() as m:
            # Mock login page response
            login_html = """
            <form action="/login" method="post">
                <input type="hidden" name="csrf_token" value="abc123">
                <input type="text" name="username">
                <input type="password" name="password">
                <input type="submit" value="Login">
            </form>
            """
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=200)
            
            await self.session_manager.configure_authentication(auth_config, base_url)
            
            assert self.session_manager.login_config == auth_config
            assert self.session_manager.base_url == base_url
    
    @pytest.mark.asyncio
    async def test_form_login_success(self):
        """Test successful form-based login."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'testpass',
            'username_field': 'username',
            'password_field': 'password'
        }
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            # Mock login page response
            login_html = """
            <form action="/login" method="post">
                <input type="hidden" name="csrf_token" value="abc123">
                <input type="text" name="username">
                <input type="password" name="password">
                <input type="submit" value="Login">
            </form>
            """
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=200, payload='Login successful')
            
            await self.session_manager._form_login()
            
            assert self.session_manager.authenticated
            assert 'csrf_token' in self.session_manager.csrf_tokens
            assert self.session_manager.csrf_tokens['csrf_token'] == 'abc123'
    
    @pytest.mark.asyncio
    async def test_form_login_with_redirect(self):
        """Test form login with redirect response."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            login_html = '<form><input type="hidden" name="_token" value="xyz789"></form>'
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=302)  # Redirect indicates success
            
            await self.session_manager._form_login()
            
            assert self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_form_login_failure(self):
        """Test failed form-based login."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'wrongpass'
        }
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            login_html = '<form><input type="text" name="username"></form>'
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=401)  # Unauthorized
            
            await self.session_manager._form_login()
            
            assert not self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_form_login_no_form_found(self):
        """Test form login when no form is found on login page."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            login_html = '<html><body><p>No form here</p></body></html>'
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            
            await self.session_manager._form_login()
            
            assert not self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_form_login_missing_parameters(self):
        """Test form login with missing required parameters."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login'
            # Missing username and password
        }
        self.session_manager.base_url = 'https://example.com'
        
        await self.session_manager._form_login()
        
        assert not self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_basic_auth(self):
        """Test HTTP Basic Authentication setup."""
        self.session_manager.login_config = {
            'type': 'basic',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        await self.session_manager._basic_auth()
        
        assert self.session_manager.authenticated
        assert hasattr(self.mock_session, '_default_auth')
        assert isinstance(self.mock_session._default_auth, aiohttp.BasicAuth)
    
    @pytest.mark.asyncio
    async def test_basic_auth_missing_credentials(self):
        """Test basic auth with missing credentials."""
        self.session_manager.login_config = {
            'type': 'basic'
            # Missing username and password
        }
        
        await self.session_manager._basic_auth()
        
        assert not self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_bearer_auth(self):
        """Test Bearer token authentication setup."""
        self.session_manager.login_config = {
            'type': 'bearer',
            'token': 'abc123xyz789'
        }
        
        await self.session_manager._bearer_auth()
        
        assert self.session_manager.authenticated
        assert 'Authorization' in self.mock_session.headers
        assert self.mock_session.headers['Authorization'] == 'Bearer abc123xyz789'
    
    @pytest.mark.asyncio
    async def test_bearer_auth_missing_token(self):
        """Test bearer auth with missing token."""
        self.session_manager.login_config = {
            'type': 'bearer'
            # Missing token
        }
        
        await self.session_manager._bearer_auth()
        
        assert not self.session_manager.authenticated
    
    @pytest.mark.asyncio
    async def test_extract_csrf_tokens_from_inputs(self):
        """Test CSRF token extraction from input fields."""
        html = """
        <html>
        <body>
            <form>
                <input type="hidden" name="csrf_token" value="abc123">
                <input type="hidden" name="authenticity_token" value="def456">
                <input type="hidden" name="_token" value="ghi789">
                <input type="hidden" name="csrfmiddlewaretoken" value="jkl012">
            </form>
        </body>
        </html>
        """
        
        await self.session_manager._extract_csrf_tokens(html)
        
        assert self.session_manager.csrf_tokens['csrf_token'] == 'abc123'
        assert self.session_manager.csrf_tokens['authenticity_token'] == 'def456'
        assert self.session_manager.csrf_tokens['_token'] == 'ghi789'
        assert self.session_manager.csrf_tokens['csrfmiddlewaretoken'] == 'jkl012'
    
    @pytest.mark.asyncio
    async def test_extract_csrf_tokens_from_meta_tags(self):
        """Test CSRF token extraction from meta tags."""
        html = """
        <html>
        <head>
            <meta name="csrf-token" content="meta123">
            <meta name="_token" content="meta456">
        </head>
        <body></body>
        </html>
        """
        
        await self.session_manager._extract_csrf_tokens(html)
        
        assert self.session_manager.csrf_tokens['csrf-token'] == 'meta123'
        assert self.session_manager.csrf_tokens['_token'] == 'meta456'
    
    @pytest.mark.asyncio
    async def test_extract_csrf_tokens_pattern_matching(self):
        """Test CSRF token extraction with pattern matching."""
        html = """
        <html>
        <body>
            <form>
                <input type="hidden" name="custom_csrf_field" value="pattern123">
                <input type="hidden" name="security_token" value="pattern456">
            </form>
        </body>
        </html>
        """
        
        await self.session_manager._extract_csrf_tokens(html)
        
        # Should find tokens with 'csrf' or 'token' in the name
        assert self.session_manager.csrf_tokens['custom_csrf_field'] == 'pattern123'
        assert self.session_manager.csrf_tokens['security_token'] == 'pattern456'
    
    @pytest.mark.asyncio
    async def test_extract_csrf_tokens_malformed_html(self):
        """Test CSRF token extraction with malformed HTML."""
        malformed_html = """
        <html>
        <body>
            <form>
                <input type="hidden" name="csrf_token" value="abc123"
                <input type="hidden" name="other_field" value="def456">
        """
        
        # Should not raise an exception
        await self.session_manager._extract_csrf_tokens(malformed_html)
        
        # Should still extract what it can
        assert 'other_field' in self.session_manager.csrf_tokens
    
    def test_get_stored_csrf_token_exact_match(self):
        """Test getting stored CSRF token with exact URL match."""
        url = 'https://example.com/form'
        token = 'exact_match_token'
        self.session_manager.csrf_tokens[url] = token
        
        result = self.session_manager.get_stored_csrf_token(url)
        
        assert result == token
    
    def test_get_stored_csrf_token_domain_match(self):
        """Test getting stored CSRF token with domain matching."""
        stored_url = 'https://example.com/login'
        token = 'domain_match_token'
        self.session_manager.csrf_tokens[stored_url] = token
        
        test_url = 'https://example.com/form'
        result = self.session_manager.get_stored_csrf_token(test_url)
        
        assert result == token
    
    def test_get_stored_csrf_token_no_match(self):
        """Test getting stored CSRF token with no match."""
        self.session_manager.csrf_tokens['https://other.com/form'] = 'other_token'
        
        result = self.session_manager.get_stored_csrf_token('https://example.com/form')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_csrf_token_from_url(self):
        """Test getting CSRF token by fetching from URL."""
        url = 'https://example.com/form'
        
        with aioresponses() as m:
            html = '<form><input type="hidden" name="csrf_token" value="fetched_token"></form>'
            m.get(url, payload=html, content_type='text/html')
            
            result = await self.session_manager.get_csrf_token(url)
            
            assert result == 'fetched_token'
            assert 'csrf_token' in self.session_manager.csrf_tokens
    
    @pytest.mark.asyncio
    async def test_get_csrf_token_request_failure(self):
        """Test getting CSRF token when request fails."""
        url = 'https://example.com/form'
        
        with aioresponses() as m:
            m.get(url, status=404)
            
            result = await self.session_manager.get_csrf_token(url)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_prepare_request_data_with_csrf(self):
        """Test preparing request data with CSRF tokens."""
        self.session_manager.csrf_tokens = {
            'csrf_token': 'abc123',
            '_token': 'def456'
        }
        
        original_data = {'username': 'testuser', 'password': 'testpass'}
        
        result = await self.session_manager.prepare_request_data('https://example.com', original_data)
        
        assert result['username'] == 'testuser'
        assert result['password'] == 'testpass'
        assert result['csrf_token'] == 'abc123'
        assert result['_token'] == 'def456'
    
    @pytest.mark.asyncio
    async def test_prepare_request_data_no_override(self):
        """Test that existing data is not overridden by CSRF tokens."""
        self.session_manager.csrf_tokens = {'csrf_token': 'abc123'}
        
        original_data = {'csrf_token': 'user_provided', 'username': 'testuser'}
        
        result = await self.session_manager.prepare_request_data('https://example.com', original_data)
        
        # Should not override existing csrf_token
        assert result['csrf_token'] == 'user_provided'
        assert result['username'] == 'testuser'
    
    @pytest.mark.asyncio
    async def test_prepare_request_data_empty_data(self):
        """Test preparing request data with empty original data."""
        self.session_manager.csrf_tokens = {'csrf_token': 'abc123'}
        
        result = await self.session_manager.prepare_request_data('https://example.com')
        
        assert result['csrf_token'] == 'abc123'
    
    def test_is_authenticated(self):
        """Test authentication status check."""
        assert not self.session_manager.is_authenticated()
        
        self.session_manager.authenticated = True
        assert self.session_manager.is_authenticated()
    
    @pytest.mark.asyncio
    async def test_test_authentication_success(self):
        """Test authentication testing with successful result."""
        self.session_manager.authenticated = True
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            # HTML with login indicators (suggesting user is logged in)
            html = '<html><body><a href="/logout">Logout</a><a href="/dashboard">Dashboard</a></body></html>'
            m.get('https://example.com', payload=html, content_type='text/html')
            
            result = await self.session_manager.test_authentication()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_authentication_failure(self):
        """Test authentication testing with failed result."""
        self.session_manager.authenticated = True
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            # HTML with logout indicators (suggesting user is not logged in)
            html = '<html><body><a href="/login">Login</a><a href="/signin">Sign In</a></body></html>'
            m.get('https://example.com', payload=html, content_type='text/html')
            
            result = await self.session_manager.test_authentication()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_test_authentication_unauthorized(self):
        """Test authentication testing with 401 response."""
        self.session_manager.authenticated = True
        
        with aioresponses() as m:
            m.get('https://example.com', status=401)
            
            result = await self.session_manager.test_authentication('https://example.com')
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_test_authentication_not_authenticated(self):
        """Test authentication testing when not authenticated."""
        self.session_manager.authenticated = False
        
        result = await self.session_manager.test_authentication()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_refresh_session_needed(self):
        """Test session refresh when authentication has expired."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        self.session_manager.base_url = 'https://example.com'
        self.session_manager.authenticated = True
        self.session_manager.csrf_tokens = {'old_token': 'old_value'}
        
        with aioresponses() as m:
            # First call to test_authentication returns failure
            html_logout = '<html><body><a href="/login">Login</a></body></html>'
            m.get('https://example.com', payload=html_logout, content_type='text/html')
            
            # Re-authentication calls
            login_html = '<form><input type="hidden" name="csrf_token" value="new_token"></form>'
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=200)
            
            await self.session_manager.refresh_session()
            
            # Should have cleared old tokens and re-authenticated
            assert 'old_token' not in self.session_manager.csrf_tokens
            assert 'csrf_token' in self.session_manager.csrf_tokens
    
    @pytest.mark.asyncio
    async def test_refresh_session_not_needed(self):
        """Test session refresh when authentication is still valid."""
        self.session_manager.authenticated = True
        self.session_manager.base_url = 'https://example.com'
        
        with aioresponses() as m:
            # Authentication test returns success
            html_login = '<html><body><a href="/logout">Logout</a></body></html>'
            m.get('https://example.com', payload=html_login, content_type='text/html')
            
            await self.session_manager.refresh_session()
            
            # Should still be authenticated
            assert self.session_manager.authenticated
    
    def test_get_session_info(self):
        """Test getting session information."""
        self.session_manager.authenticated = True
        self.session_manager.csrf_tokens = {'token1': 'value1', 'token2': 'value2'}
        self.session_manager.login_config = {'type': 'form'}
        
        # Mock cookie jar
        self.mock_session.cookie_jar = [Mock(), Mock(), Mock()]  # 3 cookies
        
        info = self.session_manager.get_session_info()
        
        assert info['authenticated'] is True
        assert info['csrf_tokens_count'] == 2
        assert info['cookies_count'] == 3
        assert info['auth_type'] == 'form'
    
    def test_get_session_info_no_config(self):
        """Test getting session information with no login config."""
        info = self.session_manager.get_session_info()
        
        assert info['authenticated'] is False
        assert info['csrf_tokens_count'] == 0
        assert info['auth_type'] is None
    
    @pytest.mark.asyncio
    async def test_update_csrf_token(self):
        """Test updating CSRF token for a URL."""
        url = 'https://example.com/form'
        token = 'new_token_value'
        
        await self.session_manager.update_csrf_token(url, token)
        
        assert self.session_manager.csrf_tokens[url] == token
    
    @pytest.mark.asyncio
    async def test_logout(self):
        """Test logout functionality."""
        self.session_manager.authenticated = True
        self.session_manager.csrf_tokens = {'token': 'value'}
        
        # Mock cookie jar with clear method
        self.mock_session.cookie_jar.clear = Mock()
        
        await self.session_manager.logout()
        
        assert not self.session_manager.authenticated
        assert self.session_manager.csrf_tokens == {}
        self.mock_session.cookie_jar.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_cookies(self):
        """Test getting session cookies for a URL."""
        url = 'https://example.com/page'
        
        # Mock cookie jar with filter_cookies method
        mock_cookie1 = Mock()
        mock_cookie1.key = 'sessionid'
        mock_cookie1.value = 'abc123'
        
        mock_cookie2 = Mock()
        mock_cookie2.key = 'csrftoken'
        mock_cookie2.value = 'def456'
        
        filtered_cookies = {
            'sessionid': mock_cookie1,
            'csrftoken': mock_cookie2
        }
        
        self.mock_session.cookie_jar.filter_cookies = Mock(return_value=filtered_cookies)
        
        result = await self.session_manager.get_session_cookies(url)
        
        assert result == {'sessionid': 'abc123', 'csrftoken': 'def456'}
        self.mock_session.cookie_jar.filter_cookies.assert_called_once_with(url)
    
    @pytest.mark.asyncio
    async def test_get_session_cookies_fallback(self):
        """Test getting session cookies with fallback method."""
        url = 'https://example.com/page'
        
        # Mock cookie jar without filter_cookies method
        mock_cookie1 = Mock()
        mock_cookie1.key = 'sessionid'
        mock_cookie1.value = 'abc123'
        mock_cookie1.domain = 'example.com'
        
        mock_cookie2 = Mock()
        mock_cookie2.key = 'other'
        mock_cookie2.value = 'xyz789'
        mock_cookie2.domain = 'other.com'
        
        self.mock_session.cookie_jar = [mock_cookie1, mock_cookie2]
        # Remove filter_cookies method to trigger fallback
        if hasattr(self.mock_session.cookie_jar, 'filter_cookies'):
            delattr(self.mock_session.cookie_jar, 'filter_cookies')
        
        result = await self.session_manager.get_session_cookies(url)
        
        assert result == {'sessionid': 'abc123'}  # Only matching domain
    
    @pytest.mark.asyncio
    async def test_get_session_cookies_error(self):
        """Test getting session cookies with error."""
        url = 'https://example.com/page'
        
        # Mock cookie jar that raises an exception
        self.mock_session.cookie_jar.filter_cookies = Mock(side_effect=Exception("Cookie error"))
        
        result = await self.session_manager.get_session_cookies(url)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_custom_headers(self):
        """Test setting custom headers."""
        headers = {
            'User-Agent': 'Custom Bot 1.0',
            'X-Custom-Header': 'custom-value'
        }
        
        await self.session_manager.set_custom_headers(headers)
        
        assert hasattr(self.session_manager, 'custom_headers')
        assert self.session_manager.custom_headers == headers
        
        # Should update session headers
        for key, value in headers.items():
            assert self.mock_session.headers[key] == value
    
    @pytest.mark.asyncio
    async def test_set_custom_headers_update(self):
        """Test updating custom headers."""
        # Set initial headers
        initial_headers = {'Header1': 'value1'}
        await self.session_manager.set_custom_headers(initial_headers)
        
        # Update with new headers
        new_headers = {'Header2': 'value2', 'Header1': 'updated_value1'}
        await self.session_manager.set_custom_headers(new_headers)
        
        assert self.session_manager.custom_headers['Header1'] == 'updated_value1'
        assert self.session_manager.custom_headers['Header2'] == 'value2'
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the session manager."""
        self.session_manager.authenticated = True
        self.session_manager.csrf_tokens = {'token': 'value'}
        
        await self.session_manager.close()
        
        assert not self.session_manager.authenticated
        assert self.session_manager.csrf_tokens == {}


class TestSessionManagerIntegration:
    """Integration tests for SessionManager with realistic scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock(spec=aiohttp.ClientSession)
        self.mock_session.headers = {}
        self.mock_session.cookie_jar = Mock()
        self.session_manager = SessionManager(self.mock_session)
    
    @pytest.mark.asyncio
    async def test_wordpress_login_flow(self):
        """Test complete WordPress login flow."""
        auth_config = {
            'enabled': True,
            'type': 'form',
            'login_url': '/wp-login.php',
            'username': 'admin',
            'password': 'password123',
            'username_field': 'log',
            'password_field': 'pwd'
        }
        base_url = 'https://wordpress.example.com'
        
        with aioresponses() as m:
            # WordPress login page
            wp_login_html = """
            <form name="loginform" action="/wp-login.php" method="post">
                <input type="text" name="log" id="user_login" />
                <input type="password" name="pwd" id="user_pass" />
                <input type="hidden" name="wp-submit" value="Log In" />
                <input type="hidden" name="_wpnonce" value="wp_nonce_123" />
            </form>
            """
            m.get('https://wordpress.example.com/wp-login.php', payload=wp_login_html, content_type='text/html')
            m.post('https://wordpress.example.com/wp-login.php', status=302)  # Redirect after login
            
            await self.session_manager.configure_authentication(auth_config, base_url)
            
            assert self.session_manager.authenticated
            assert '_wpnonce' in self.session_manager.csrf_tokens
            assert self.session_manager.csrf_tokens['_wpnonce'] == 'wp_nonce_123'
    
    @pytest.mark.asyncio
    async def test_django_csrf_handling(self):
        """Test Django CSRF token handling."""
        self.session_manager.base_url = 'https://django.example.com'
        
        with aioresponses() as m:
            # Django form with CSRF token
            django_html = """
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="django_csrf_123">
                <input type="text" name="username">
                <input type="password" name="password">
                <input type="submit" value="Submit">
            </form>
            """
            m.get('https://django.example.com/form', payload=django_html, content_type='text/html')
            
            token = await self.session_manager.get_csrf_token('https://django.example.com/form')
            
            assert token == 'django_csrf_123'
            assert 'csrfmiddlewaretoken' in self.session_manager.csrf_tokens
            
            # Test preparing form data
            form_data = {'username': 'testuser', 'password': 'testpass'}
            prepared_data = await self.session_manager.prepare_request_data(
                'https://django.example.com/form', form_data
            )
            
            assert prepared_data['csrfmiddlewaretoken'] == 'django_csrf_123'
            assert prepared_data['username'] == 'testuser'
    
    @pytest.mark.asyncio
    async def test_laravel_csrf_handling(self):
        """Test Laravel CSRF token handling."""
        with aioresponses() as m:
            # Laravel form with CSRF token
            laravel_html = """
            <html>
            <head>
                <meta name="csrf-token" content="laravel_meta_token">
            </head>
            <body>
                <form method="post">
                    <input type="hidden" name="_token" value="laravel_form_token">
                    <input type="email" name="email">
                    <input type="submit" value="Submit">
                </form>
            </body>
            </html>
            """
            m.get('https://laravel.example.com/form', payload=laravel_html, content_type='text/html')
            
            token = await self.session_manager.get_csrf_token('https://laravel.example.com/form')
            
            # Should return the first available token
            assert token in ['laravel_meta_token', 'laravel_form_token']
            assert 'csrf-token' in self.session_manager.csrf_tokens
            assert '_token' in self.session_manager.csrf_tokens
    
    @pytest.mark.asyncio
    async def test_session_expiry_and_refresh(self):
        """Test session expiry detection and refresh."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        self.session_manager.base_url = 'https://example.com'
        self.session_manager.authenticated = True
        
        with aioresponses() as m:
            # First test shows session expired (login page content)
            expired_html = '<html><body><h1>Please log in</h1><a href="/login">Login</a></body></html>'
            m.get('https://example.com', payload=expired_html, content_type='text/html')
            
            # Re-authentication flow
            login_html = '<form><input type="hidden" name="csrf_token" value="new_session_token"></form>'
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=200)
            
            await self.session_manager.refresh_session()
            
            assert self.session_manager.authenticated
            assert 'csrf_token' in self.session_manager.csrf_tokens
            assert self.session_manager.csrf_tokens['csrf_token'] == 'new_session_token'