"""
Session management component for handling authentication and cookies.
Manages login sessions, CSRF tokens, and cookie persistence during crawling.
"""

import logging
import asyncio
from typing import Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages HTTP sessions, authentication, and cookie persistence.
    Handles login flows, CSRF tokens, and session state.
    """
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.authenticated = False
        self.csrf_tokens: Dict[str, str] = {}
        self.login_config: Optional[Dict[str, Any]] = None
        self.base_url = ""
    
    async def configure_authentication(self, auth_config: Dict[str, Any], base_url: str):
        """
        Configure authentication settings.
        
        Args:
            auth_config: Authentication configuration
            base_url: Base URL for the target site
        """
        self.login_config = auth_config
        self.base_url = base_url
        
        if auth_config and auth_config.get('enabled', False):
            await self._perform_login()
    
    async def _perform_login(self):
        """
        Perform login using configured credentials.
        """
        if not self.login_config:
            return
        
        try:
            login_type = self.login_config.get('type', 'form')
            
            if login_type == 'form':
                await self._form_login()
            elif login_type == 'basic':
                await self._basic_auth()
            elif login_type == 'bearer':
                await self._bearer_auth()
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
    
    async def _form_login(self):
        """
        Perform form-based login.
        """
        login_url = self.login_config.get('login_url')
        username = self.login_config.get('username')
        password = self.login_config.get('password')
        
        if not all([login_url, username, password]):
            logger.error("Missing required form login parameters")
            return
        
        # Make login_url absolute
        if not login_url.startswith('http'):
            login_url = urljoin(self.base_url, login_url)
        
        try:
            # First, get the login page to extract CSRF tokens
            async with self.session.get(login_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to access login page: {response.status}")
                    return
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find login form
                form = soup.find('form')
                if not form:
                    logger.error("No form found on login page")
                    return
                
                # Extract form action
                action = form.get('action', '')
                if action and not action.startswith('http'):
                    action = urljoin(login_url, action)
                else:
                    action = login_url
                
                # Prepare form data
                form_data = {}
                
                # Add all hidden inputs
                for hidden_input in form.find_all('input', type='hidden'):
                    name = hidden_input.get('name')
                    value = hidden_input.get('value', '')
                    if name:
                        form_data[name] = value
                
                # Add username and password
                username_field = self.login_config.get('username_field', 'username')
                password_field = self.login_config.get('password_field', 'password')
                
                form_data[username_field] = username
                form_data[password_field] = password
                
                # Submit login form
                async with self.session.post(action, data=form_data) as login_response:
                    if login_response.status in [200, 302, 303]:
                        self.authenticated = True
                        logger.info("Form login successful")
                        
                        # Store any new CSRF tokens
                        await self._extract_csrf_tokens(await login_response.text())
                    else:
                        logger.error(f"Login failed with status: {login_response.status}")
        
        except Exception as e:
            logger.error(f"Form login error: {e}")
    
    async def _basic_auth(self):
        """
        Set up HTTP Basic Authentication.
        """
        username = self.login_config.get('username')
        password = self.login_config.get('password')
        
        if username and password:
            auth = aiohttp.BasicAuth(username, password)
            # Update session with basic auth
            self.session._default_auth = auth
            self.authenticated = True
            logger.info("Basic auth configured")
    
    async def _bearer_auth(self):
        """
        Set up Bearer token authentication.
        """
        token = self.login_config.get('token')
        
        if token:
            # Add Authorization header to all requests
            self.session.headers.update({'Authorization': f'Bearer {token}'})
            self.authenticated = True
            logger.info("Bearer auth configured")
    
    async def _extract_csrf_tokens(self, html: str):
        """
        Extract CSRF tokens from HTML content.
        
        Args:
            html: HTML content to parse
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Common CSRF token patterns
            csrf_patterns = [
                {'name': 'csrf_token'},
                {'name': 'authenticity_token'},
                {'name': '_token'},
                {'name': 'csrfmiddlewaretoken'},
                {'attrs': {'name': lambda x: x and 'csrf' in x.lower()}},
                {'attrs': {'name': lambda x: x and 'token' in x.lower()}}
            ]
            
            for pattern in csrf_patterns:
                inputs = soup.find_all('input', pattern)
                for input_tag in inputs:
                    name = input_tag.get('name')
                    value = input_tag.get('value')
                    if name and value:
                        self.csrf_tokens[name] = value
                        logger.debug(f"Found CSRF token: {name}")
            
            # Also check meta tags
            meta_patterns = [
                {'name': 'csrf-token'},
                {'name': '_token'},
                {'attrs': {'name': lambda x: x and 'csrf' in x.lower()}}
            ]
            
            for pattern in meta_patterns:
                metas = soup.find_all('meta', pattern)
                for meta_tag in metas:
                    name = meta_tag.get('name')
                    content = meta_tag.get('content')
                    if name and content:
                        self.csrf_tokens[name] = content
                        logger.debug(f"Found CSRF meta token: {name}")
        
        except Exception as e:
            logger.error(f"Error extracting CSRF tokens: {e}")
    
    async def get_csrf_token(self, url: str) -> Optional[str]:
        """
        Get CSRF token for a specific URL.
        
        Args:
            url: URL to get CSRF token for
            
        Returns:
            CSRF token if found
        """
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    await self._extract_csrf_tokens(html)
                    
                    # Return the first available token
                    if self.csrf_tokens:
                        return list(self.csrf_tokens.values())[0]
        
        except Exception as e:
            logger.error(f"Error getting CSRF token from {url}: {e}")
        
        return None
    
    async def prepare_request_data(self, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare request data with CSRF tokens if needed.
        
        Args:
            url: Target URL
            data: Original form data
            
        Returns:
            Enhanced form data with CSRF tokens
        """
        if data is None:
            data = {}
        
        # Add CSRF tokens to form data
        for token_name, token_value in self.csrf_tokens.items():
            if token_name not in data:
                data[token_name] = token_value
        
        return data
    
    async def is_authenticated(self) -> bool:
        """
        Check if session is authenticated.
        
        Returns:
            True if authenticated
        """
        return self.authenticated
    
    async def test_authentication(self, test_url: str = None) -> bool:
        """
        Test if authentication is working by accessing a protected resource.
        
        Args:
            test_url: URL to test authentication against
            
        Returns:
            True if authentication is working
        """
        if not self.authenticated:
            return False
        
        if not test_url:
            test_url = self.base_url
        
        try:
            async with self.session.get(test_url) as response:
                # Check for common authentication indicators
                if response.status == 200:
                    html = await response.text()
                    
                    # Look for signs of being logged in
                    login_indicators = ['logout', 'dashboard', 'profile', 'account']
                    logout_indicators = ['login', 'sign in', 'authenticate']
                    
                    html_lower = html.lower()
                    
                    # Count positive and negative indicators
                    login_score = sum(1 for indicator in login_indicators if indicator in html_lower)
                    logout_score = sum(1 for indicator in logout_indicators if indicator in html_lower)
                    
                    # Simple heuristic: more login indicators than logout indicators
                    return login_score > logout_score
                
                elif response.status == 401:
                    return False
        
        except Exception as e:
            logger.error(f"Error testing authentication: {e}")
        
        return self.authenticated
    
    async def refresh_session(self):
        """
        Refresh the session by re-authenticating if needed.
        """
        if self.login_config and not await self.test_authentication():
            logger.info("Session expired, re-authenticating...")
            self.authenticated = False
            self.csrf_tokens.clear()
            await self._perform_login()
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Session information dictionary
        """
        return {
            'authenticated': self.authenticated,
            'csrf_tokens_count': len(self.csrf_tokens),
            'cookies_count': len(self.session.cookie_jar),
            'auth_type': self.login_config.get('type') if self.login_config else None
        }