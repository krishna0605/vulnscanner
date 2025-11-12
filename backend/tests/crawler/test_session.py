"""
Tests for session management functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import aiohttp
from aioresponses import aioresponses

from crawler.session import SessionManager


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock(spec=aiohttp.ClientSession)
        self.session_manager = SessionManager(self.mock_session)
    
    def test_session_manager_initialization(self):
        """Test session manager initialization."""
        assert self.session_manager.session == self.mock_session
        assert self.session_manager.authenticated is False
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
        assert self.session_manager.authenticated is False
    
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
            # Mock login page
            login_html = '''
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
            '''
            m.get('https://example.com/login', payload=login_html, content_type='text/html')
            m.post('https://example.com/login', status=200)
            
            # Mock session methods
            self.mock_session.get = AsyncMock()
            self.mock_session.post = AsyncMock()
            
            # Create mock response for GET
            mock_get_response = AsyncMock()
            mock_get_response.status = 200
            mock_get_response.text = AsyncMock(return_value=login_html)
            mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
            mock_get_response.__aexit__ = AsyncMock(return_value=None)
            self.mock_session.get.return_value = mock_get_response
            
            # Create mock response for POST
            mock_post_response = AsyncMock()
            mock_post_response.status = 200
            mock_post_response.text = AsyncMock(return_value='<html>Login successful</html>')
            mock_post_response.__aenter__ = AsyncMock(return_value=mock_post_response)
            mock_post_response.__aexit__ = AsyncMock(return_value=None)
            self.mock_session.post.return_value = mock_post_response
            
            await self.session_manager.configure_authentication(auth_config, base_url)
            
            assert self.session_manager.login_config == auth_config
            assert self.session_manager.base_url == base_url
    
    @pytest.mark.asyncio
    async def test_form_login_success(self):
        """Test successful form-based login."""
        login_html = '''
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
        '''
        
        with aioresponses() as m:
            # Mock the GET request to login page
            m.get('https://example.com/login', body=login_html, content_type='text/html')
            # Mock the POST request for login
            m.post('https://example.com/login', body='<html>Login successful</html>', content_type='text/html')
            
            async with aiohttp.ClientSession() as session:
                session_manager = SessionManager(session)
                session_manager.login_config = {
                    'type': 'form',
                    'login_url': 'https://example.com/login',
                    'username': 'testuser',
                    'password': 'testpass',
                    'username_field': 'username',
                    'password_field': 'password'
                }
                session_manager.base_url = 'https://example.com'
                
                await session_manager._form_login()
                
                assert session_manager.authenticated is True
    
    @pytest.mark.asyncio
    async def test_form_login_missing_parameters(self):
        """Test form login with missing parameters."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': 'https://example.com/login'
            # Missing username and password
        }
        
        await self.session_manager._form_login()
        
        assert self.session_manager.authenticated is False
        self.mock_session.get.assert_not_called()
        self.mock_session.post.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_form_login_relative_url(self):
        """Test form login with relative URL."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': '/login',  # Relative URL
            'username': 'testuser',
            'password': 'testpass'
        }
        self.session_manager.base_url = 'https://example.com'
        
        login_html = '<html><body><form><input type="hidden" name="csrf" value="123"></form></body></html>'
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.text = AsyncMock(return_value=login_html)
        mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
        mock_get_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.text = AsyncMock(return_value='<html>Success</html>')
        mock_post_response.__aenter__ = AsyncMock(return_value=mock_post_response)
        mock_post_response.__aexit__ = AsyncMock(return_value=None)
        
        self.mock_session.get = AsyncMock(return_value=mock_get_response)
        self.mock_session.post = AsyncMock(return_value=mock_post_response)
        
        await self.session_manager._form_login()
        
        # Should call with absolute URL
        self.mock_session.get.assert_called_once_with('https://example.com/login')
    
    @pytest.mark.asyncio
    async def test_form_login_no_form_found(self):
        """Test form login when no form is found on page."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': 'https://example.com/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        login_html = '<html><body><p>No form here</p></body></html>'
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.text = AsyncMock(return_value=login_html)
        mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
        mock_get_response.__aexit__ = AsyncMock(return_value=None)
        
        self.mock_session.get = AsyncMock(return_value=mock_get_response)
        self.mock_session.post = AsyncMock()
        
        await self.session_manager._form_login()
        
        assert self.session_manager.authenticated is False
        self.mock_session.post.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_form_login_failed_status(self):
        """Test form login with failed HTTP status."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': 'https://example.com/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        mock_get_response = AsyncMock()
        mock_get_response.status = 404  # Failed status
        mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
        mock_get_response.__aexit__ = AsyncMock(return_value=None)
        
        self.mock_session.get = AsyncMock(return_value=mock_get_response)
        
        await self.session_manager._form_login()
        
        assert self.session_manager.authenticated is False
    
    @pytest.mark.asyncio
    async def test_basic_auth_setup(self):
        """Test HTTP Basic Authentication setup."""
        self.session_manager.login_config = {
            'type': 'basic',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        await self.session_manager._basic_auth()
        
        assert self.session_manager.authenticated is True
        assert hasattr(self.mock_session, '_default_auth')
    
    @pytest.mark.asyncio
    async def test_basic_auth_missing_credentials(self):
        """Test Basic Auth with missing credentials."""
        self.session_manager.login_config = {
            'type': 'basic'
            # Missing username and password
        }
        
        await self.session_manager._basic_auth()
        
        assert self.session_manager.authenticated is False
    
    @pytest.mark.asyncio
    async def test_bearer_auth_setup(self):
        """Test Bearer token authentication setup."""
        self.session_manager.login_config = {
            'type': 'bearer',
            'token': 'abc123token'
        }
        
        await self.session_manager._bearer_auth()
        
        assert self.session_manager.authenticated is True
    
    @pytest.mark.asyncio
    async def test_bearer_auth_missing_token(self):
        """Test Bearer Auth with missing token."""
        self.session_manager.login_config = {
            'type': 'bearer'
            # Missing token
        }
        
        await self.session_manager._bearer_auth()
        
        assert self.session_manager.authenticated is False
    
    @pytest.mark.asyncio
    async def test_csrf_token_extraction(self):
        """Test CSRF token extraction from HTML."""
        html_content = '''
        <html>
            <body>
                <form>
                    <input type="hidden" name="csrf_token" value="abc123">
                    <input type="hidden" name="_token" value="def456">
                    <meta name="csrf-token" content="ghi789">
                </form>
            </body>
        </html>
        '''
        
        await self.session_manager._extract_csrf_tokens(html_content)
        
        # Should extract CSRF tokens
        assert len(self.session_manager.csrf_tokens) > 0
    
    def test_get_stored_csrf_token(self):
        """Test getting stored CSRF token for a URL."""
        self.session_manager.csrf_tokens = {
            'https://example.com': 'token123',
            'https://example.com/page': 'token456'
        }
        
        # Test exact match
        token = self.session_manager.get_stored_csrf_token('https://example.com')
        assert token == 'token123'
        
        # Test domain match
        token = self.session_manager.get_stored_csrf_token('https://example.com/other')
        assert token == 'token123'
        
        # Test no match
        token = self.session_manager.get_stored_csrf_token('https://other.com')
        assert token is None
    
    @pytest.mark.asyncio
    async def test_update_csrf_token(self):
        """Test updating CSRF token for a URL."""
        url = 'https://example.com/page'
        token = 'newtoken123'
        
        await self.session_manager.update_csrf_token(url, token)
        
        assert self.session_manager.csrf_tokens[url] == token
    
    @pytest.mark.asyncio
    async def test_is_authenticated(self):
        """Test authentication status check."""
        # Initially not authenticated
        assert not self.session_manager.is_authenticated()
        
        # Set as authenticated
        self.session_manager.authenticated = True
        assert self.session_manager.is_authenticated()
    
    @pytest.mark.asyncio
    async def test_logout(self):
        """Test logout functionality."""
        # Set up authenticated state
        self.session_manager.authenticated = True
        self.session_manager.csrf_tokens = {'url': 'token'}
        
        await self.session_manager.logout()
        
        assert self.session_manager.authenticated is False
        assert len(self.session_manager.csrf_tokens) == 0
    
    @pytest.mark.asyncio
    async def test_session_persistence(self):
        """Test session cookie persistence."""
        # Mock session with cookies
        self.mock_session.cookie_jar = MagicMock()
        
        # Create mock cookie objects
        mock_cookie1 = MagicMock()
        mock_cookie1.key = 'sessionid'
        mock_cookie1.value = 'abc123'
        
        mock_cookie2 = MagicMock()
        mock_cookie2.key = 'csrftoken'
        mock_cookie2.value = 'def456'
        
        # Mock filter_cookies to return a dict-like object with values() method
        mock_filtered = MagicMock()
        mock_filtered.values.return_value = [mock_cookie1, mock_cookie2]
        self.mock_session.cookie_jar.filter_cookies.return_value = mock_filtered
        
        cookies = await self.session_manager.get_session_cookies('https://example.com')
        
        assert cookies is not None
        assert 'sessionid' in cookies
        assert cookies['sessionid'] == 'abc123'
    
    @pytest.mark.asyncio
    async def test_custom_headers(self):
        """Test custom header management."""
        headers = {
            'User-Agent': 'Custom Scanner',
            'X-Custom-Header': 'test-value'
        }
        
        await self.session_manager.set_custom_headers(headers)
        
        # Should store custom headers
        assert hasattr(self.session_manager, 'custom_headers')
    
    @pytest.mark.asyncio
    async def test_form_with_multiple_hidden_fields(self):
        """Test form login with multiple hidden fields."""
        login_html = '''
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="hidden" name="csrf_token" value="abc123">
                    <input type="hidden" name="form_id" value="login_form">
                    <input type="hidden" name="redirect_url" value="/dashboard">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
        '''
        
        with aioresponses() as m:
            # Mock the GET request to login page
            m.get('https://example.com/login', body=login_html, content_type='text/html')
            # Mock the POST request for login (302 redirect after successful login)
            m.post('https://example.com/login', status=302, body='', content_type='text/html')
            
            async with aiohttp.ClientSession() as session:
                session_manager = SessionManager(session)
                session_manager.login_config = {
                    'type': 'form',
                    'login_url': 'https://example.com/login',
                    'username': 'testuser',
                    'password': 'testpass'
                }
                session_manager.base_url = 'https://example.com'
                
                await session_manager._form_login()
                
                assert session_manager.authenticated is True
                
                # Check that the requests were made
                assert len(m.requests) == 2  # GET and POST
                
                # Note: aioresponses doesn't easily expose form data, 
                # but we can verify the request was made successfully
    
    @pytest.mark.asyncio
    async def test_login_error_handling(self):
        """Test error handling during login process."""
        self.session_manager.login_config = {
            'type': 'form',
            'login_url': 'https://example.com/login',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        # Mock session to raise an exception
        self.mock_session.get = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))
        
        # Should not raise exception, but handle gracefully
        await self.session_manager._form_login()
        
        assert self.session_manager.authenticated is False