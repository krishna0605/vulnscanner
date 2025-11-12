"""
Unit tests for the web spider module.
Tests rate limiting, HTTP requests, robots.txt compliance, and error handling.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
import aiohttp
from aioresponses import aioresponses
import time
from urllib.robotparser import RobotFileParser

from crawler.spider import RateLimiter, WebSpider
from schemas.dashboard import ScanConfigurationSchema


class TestRateLimiter:
    """Test cases for RateLimiter class."""
    
    def test_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(10)  # 10 requests per second
        
        assert limiter.requests_per_second == 10
        assert limiter.min_interval == 0.1
        assert limiter.last_request_time == 0
        assert limiter._lock is not None
    
    def test_initialization_zero_rate(self):
        """Test RateLimiter with zero rate (no limiting)."""
        limiter = RateLimiter(0)
        
        assert limiter.requests_per_second == 0
        assert limiter.min_interval == 0
    
    @pytest.mark.asyncio
    async def test_acquire_no_limiting(self):
        """Test acquire with no rate limiting."""
        limiter = RateLimiter(0)  # No limiting
        
        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        end_time = time.time()
        
        # Should complete almost instantly
        assert end_time - start_time < 0.1
    
    @pytest.mark.asyncio
    async def test_acquire_with_limiting(self):
        """Test acquire with rate limiting."""
        limiter = RateLimiter(10)  # 10 requests per second (0.1s interval)
        
        start_time = time.time()
        await limiter.acquire()  # First request - no delay
        await limiter.acquire()  # Second request - should delay
        end_time = time.time()
        
        # Should take at least 0.1 seconds
        assert end_time - start_time >= 0.09  # Allow small margin for timing
    
    @pytest.mark.asyncio
    async def test_acquire_concurrent(self):
        """Test acquire with concurrent requests."""
        limiter = RateLimiter(5)  # 5 requests per second (0.2s interval)
        
        async def make_request():
            await limiter.acquire()
            return time.time()
        
        # Start multiple concurrent requests
        tasks = [make_request() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Requests should be spaced out
        for i in range(1, len(results)):
            time_diff = results[i] - results[i-1]
            assert time_diff >= 0.19  # Allow small margin


class TestWebSpider:
    """Test cases for WebSpider class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = ScanConfigurationSchema(
            max_depth=3,
            max_pages=100,
            requests_per_second=10,
            timeout=30,
            follow_redirects=True,
            respect_robots=True,
            user_agent="Test-Spider/1.0"
        )
        self.spider = WebSpider(self.config)
    
    def test_initialization(self):
        """Test WebSpider initialization."""
        assert self.spider.config == self.config
        assert self.spider.session is None
        assert self.spider.robots_cache == {}
        assert self.spider.failed_domains == set()
        assert self.spider.rate_limiter.requests_per_second == 10
        assert self.spider.timeout.total == 30
        assert self.spider.headers['User-Agent'] == "Test-Spider/1.0"
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test spider initialization."""
        await self.spider.initialize()
        
        assert self.spider.session is not None
        assert isinstance(self.spider.session, aiohttp.ClientSession)
        
        # Clean up
        await self.spider.close()
    
    @pytest.mark.asyncio
    async def test_ensure_session(self):
        """Test session creation."""
        assert self.spider.session is None
        
        await self.spider._ensure_session()
        
        assert self.spider.session is not None
        assert isinstance(self.spider.session, aiohttp.ClientSession)
        
        # Clean up
        await self.spider.close()
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test spider cleanup."""
        await self.spider.initialize()
        assert self.spider.session is not None
        
        await self.spider.close()
        assert self.spider.session is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_success(self):
        """Test successful URL fetching."""
        with aioresponses() as m:
            html_content = """
            <html>
            <head><title>Test Page</title></head>
            <body><h1>Hello World</h1></body>
            </html>
            """
            m.get('https://example.com/test', payload=html_content, 
                  content_type='text/html', status=200,
                  headers={'Content-Length': str(len(html_content))})
            
            result = await self.spider.fetch_url('https://example.com/test')
            
            assert result is not None
            assert result['url'] == 'https://example.com/test'
            assert result['status_code'] == 200
            assert result['content_type'] == 'text/html'
            assert result['title'] == 'Test Page'
            assert result['is_html'] is True
            assert 'Hello World' in result['content']
            assert result['response_time'] > 0
    
    @pytest.mark.asyncio
    async def test_fetch_url_with_custom_headers(self):
        """Test URL fetching with custom headers."""
        custom_headers = {'X-Custom-Header': 'test-value'}
        
        with aioresponses() as m:
            m.get('https://example.com/test', payload='<html><title>Test</title></html>', 
                  content_type='text/html')
            
            result = await self.spider.fetch_url('https://example.com/test', headers=custom_headers)
            
            assert result is not None
            # Verify the request was made (aioresponses doesn't easily let us check headers)
    
    @pytest.mark.asyncio
    async def test_fetch_url_non_html_filtered(self):
        """Test that non-HTML content is filtered out."""
        with aioresponses() as m:
            # JSON response should be filtered
            m.get('https://example.com/api', payload='{"key": "value"}', 
                  content_type='application/json')
            
            result = await self.spider.fetch_url('https://example.com/api')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_image_filtered(self):
        """Test that image content is filtered out."""
        with aioresponses() as m:
            m.get('https://example.com/image.jpg', payload=b'fake_image_data', 
                  content_type='image/jpeg')
            
            result = await self.spider.fetch_url('https://example.com/image.jpg')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_css_filtered(self):
        """Test that CSS content is filtered out."""
        with aioresponses() as m:
            m.get('https://example.com/style.css', payload='body { color: red; }', 
                  content_type='text/css')
            
            result = await self.spider.fetch_url('https://example.com/style.css')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_javascript_filtered(self):
        """Test that JavaScript content is filtered out."""
        with aioresponses() as m:
            m.get('https://example.com/script.js', payload='console.log("test");', 
                  content_type='text/javascript')
            
            result = await self.spider.fetch_url('https://example.com/script.js')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_pdf_filtered(self):
        """Test that PDF content is filtered out."""
        with aioresponses() as m:
            m.get('https://example.com/document.pdf', payload=b'%PDF-1.4 fake pdf', 
                  content_type='application/pdf')
            
            result = await self.spider.fetch_url('https://example.com/document.pdf')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_timeout(self):
        """Test URL fetching with timeout."""
        with aioresponses() as m:
            m.get('https://example.com/slow', exception=asyncio.TimeoutError())
            
            result = await self.spider.fetch_url('https://example.com/slow')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_connection_error(self):
        """Test URL fetching with connection error."""
        with aioresponses() as m:
            m.get('https://example.com/error', exception=aiohttp.ClientConnectorError(
                connection_key=None, os_error=None))
            
            result = await self.spider.fetch_url('https://example.com/error')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_client_error(self):
        """Test URL fetching with client error."""
        with aioresponses() as m:
            m.get('https://example.com/notfound', status=404)
            
            result = await self.spider.fetch_url('https://example.com/notfound')
            
            assert result is not None
            assert result['status_code'] == 404
    
    @pytest.mark.asyncio
    async def test_fetch_url_server_error_no_retry(self):
        """Test URL fetching with server error (no retry)."""
        with aioresponses() as m:
            m.get('https://example.com/server_error', status=500)
            
            result = await self.spider.fetch_url('https://example.com/server_error')
            
            assert result is not None
            assert result['status_code'] == 500
    
    @pytest.mark.asyncio
    async def test_fetch_url_server_error_with_retry(self):
        """Test URL fetching with server error and retry."""
        with aioresponses() as m:
            # First attempt fails, second succeeds
            m.get('https://example.com/retry', status=500)
            m.get('https://example.com/retry', payload='<html><title>Success</title></html>', 
                  content_type='text/html', status=200)
            
            result = await self.spider.fetch_url('https://example.com/retry', max_retries=1)
            
            assert result is not None
            assert result['status_code'] == 200
            assert result['title'] == 'Success'
    
    @pytest.mark.asyncio
    async def test_fetch_url_redirect(self):
        """Test URL fetching with redirects."""
        with aioresponses() as m:
            # Mock redirect behavior
            m.get('https://example.com/redirect', status=302, 
                  headers={'Location': 'https://example.com/final'})
            m.get('https://example.com/final', payload='<html><title>Final</title></html>', 
                  content_type='text/html')
            
            result = await self.spider.fetch_url('https://example.com/redirect')
            
            assert result is not None
            # Note: aioresponses doesn't fully simulate redirects, so we test what we can
    
    @pytest.mark.asyncio
    async def test_fetch_url_robots_blocked(self):
        """Test URL fetching blocked by robots.txt."""
        # Mock robots.txt that disallows the path
        robots_content = """
        User-agent: *
        Disallow: /blocked/
        """
        
        with aioresponses() as m:
            m.get('https://example.com/robots.txt', payload=robots_content, 
                  content_type='text/plain')
            
            result = await self.spider.fetch_url('https://example.com/blocked/page')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_url_robots_allowed(self):
        """Test URL fetching allowed by robots.txt."""
        robots_content = """
        User-agent: *
        Disallow: /admin/
        Allow: /public/
        """
        
        with aioresponses() as m:
            m.get('https://example.com/robots.txt', payload=robots_content, 
                  content_type='text/plain')
            m.get('https://example.com/public/page', payload='<html><title>Public</title></html>', 
                  content_type='text/html')
            
            result = await self.spider.fetch_url('https://example.com/public/page')
            
            assert result is not None
            assert result['title'] == 'Public'
    
    @pytest.mark.asyncio
    async def test_fetch_url_robots_disabled(self):
        """Test URL fetching with robots.txt checking disabled."""
        self.spider.config.respect_robots = False
        
        with aioresponses() as m:
            # Don't mock robots.txt - it shouldn't be fetched
            m.get('https://example.com/admin/secret', payload='<html><title>Secret</title></html>', 
                  content_type='text/html')
            
            result = await self.spider.fetch_url('https://example.com/admin/secret')
            
            assert result is not None
            assert result['title'] == 'Secret'
    
    @pytest.mark.asyncio
    async def test_read_content_safely_normal(self):
        """Test safe content reading with normal content."""
        mock_response = Mock()
        mock_response.headers = {}
        mock_response.read = AsyncMock(return_value=b'<html><title>Test</title></html>')
        mock_response.url = 'https://example.com'
        
        content = await self.spider._read_content_safely(mock_response)
        
        assert content == '<html><title>Test</title></html>'
    
    @pytest.mark.asyncio
    async def test_read_content_safely_large_content_header(self):
        """Test safe content reading with large content length in header."""
        mock_response = Mock()
        mock_response.headers = {'Content-Length': str(20 * 1024 * 1024)}  # 20MB
        mock_response.url = 'https://example.com'
        
        content = await self.spider._read_content_safely(mock_response)
        
        assert content is None
    
    @pytest.mark.asyncio
    async def test_read_content_safely_large_content_actual(self):
        """Test safe content reading with large actual content."""
        mock_response = Mock()
        mock_response.headers = {}
        # Mock large content (11MB)
        large_content = b'x' * (11 * 1024 * 1024)
        mock_response.read = AsyncMock(return_value=large_content)
        mock_response.url = 'https://example.com'
        
        content = await self.spider._read_content_safely(mock_response)
        
        assert content is None
    
    @pytest.mark.asyncio
    async def test_read_content_safely_encoding_fallback(self):
        """Test safe content reading with encoding fallback."""
        mock_response = Mock()
        mock_response.headers = {}
        # Content with non-UTF-8 bytes
        mock_response.read = AsyncMock(return_value=b'\\xff\\xfe<html></html>')
        mock_response.url = 'https://example.com'
        
        content = await self.spider._read_content_safely(mock_response)
        
        # Should fallback to latin1 or other encoding
        assert content is not None
        assert '<html>' in content
    
    @pytest.mark.asyncio
    async def test_read_content_safely_error(self):
        """Test safe content reading with error."""
        mock_response = Mock()
        mock_response.headers = {}
        mock_response.read = AsyncMock(side_effect=Exception("Read error"))
        mock_response.url = 'https://example.com'
        
        content = await self.spider._read_content_safely(mock_response)
        
        assert content is None
    
    def test_extract_title_success(self):
        """Test title extraction from HTML."""
        html = '<html><head><title>Test Page Title</title></head><body></body></html>'
        
        title = self.spider._extract_title(html)
        
        assert title == 'Test Page Title'
    
    def test_extract_title_with_whitespace(self):
        """Test title extraction with whitespace cleanup."""
        html = '<html><head><title>   Test   Page   Title   </title></head></html>'
        
        title = self.spider._extract_title(html)
        
        assert title == 'Test   Page   Title'  # Internal whitespace preserved, edges trimmed
    
    def test_extract_title_case_insensitive(self):
        """Test title extraction is case insensitive."""
        html = '<HTML><HEAD><TITLE>Uppercase Title</TITLE></HEAD></HTML>'
        
        title = self.spider._extract_title(html)
        
        assert title == 'Uppercase Title'
    
    def test_extract_title_no_title(self):
        """Test title extraction with no title tag."""
        html = '<html><head></head><body><h1>No Title</h1></body></html>'
        
        title = self.spider._extract_title(html)
        
        assert title is None
    
    def test_extract_title_empty_title(self):
        """Test title extraction with empty title."""
        html = '<html><head><title></title></head><body></body></html>'
        
        title = self.spider._extract_title(html)
        
        assert title == ''
    
    def test_extract_title_long_title(self):
        """Test title extraction with very long title."""
        long_title = 'A' * 600  # Longer than 500 char limit
        html = f'<html><head><title>{long_title}</title></head></html>'
        
        title = self.spider._extract_title(html)
        
        assert len(title) == 500
        assert title == 'A' * 500
    
    def test_extract_title_malformed_html(self):
        """Test title extraction with malformed HTML."""
        html = '<html><head><title>Broken Title</head></html>'  # Missing closing title tag
        
        title = self.spider._extract_title(html)
        
        assert title is None
    
    def test_extract_title_error(self):
        """Test title extraction with error."""
        # Pass non-string to trigger error
        title = self.spider._extract_title(None)
        
        assert title is None
    
    @pytest.mark.asyncio
    async def test_can_fetch_cached_robots(self):
        """Test robots.txt checking with cached parser."""
        # Pre-populate cache
        rp = RobotFileParser()
        rp.set_url('https://example.com/robots.txt')
        rp.parse(['User-agent: *', 'Disallow: /admin/'])
        self.spider.robots_cache['example.com'] = rp
        
        # Initialize session
        await self.spider.initialize()
        
        # Test allowed URL
        can_fetch = await self.spider._can_fetch('https://example.com/public')
        assert can_fetch is True
        
        # Test disallowed URL
        can_fetch = await self.spider._can_fetch('https://example.com/admin/secret')
        assert can_fetch is False
        
        await self.spider.close()
    
    @pytest.mark.asyncio
    async def test_can_fetch_fetch_robots(self):
        """Test robots.txt checking by fetching robots.txt."""
        robots_content = """
        User-agent: *
        Disallow: /private/
        """
        
        with aioresponses() as m:
            m.get('https://example.com/robots.txt', payload=robots_content, 
                  content_type='text/plain')
            
            await self.spider.initialize()
            
            can_fetch = await self.spider._can_fetch('https://example.com/public')
            assert can_fetch is True
            
            can_fetch = await self.spider._can_fetch('https://example.com/private/data')
            assert can_fetch is False
            
            # Check that robots.txt was cached
            assert 'example.com' in self.spider.robots_cache
            
            await self.spider.close()
    
    @pytest.mark.asyncio
    async def test_can_fetch_robots_not_found(self):
        """Test robots.txt checking when robots.txt is not found."""
        with aioresponses() as m:
            m.get('https://example.com/robots.txt', status=404)
            
            await self.spider.initialize()
            
            # Should allow fetching when robots.txt is not found
            can_fetch = await self.spider._can_fetch('https://example.com/anything')
            assert can_fetch is True
            
            await self.spider.close()
    
    @pytest.mark.asyncio
    async def test_can_fetch_robots_error(self):
        """Test robots.txt checking with fetch error."""
        with aioresponses() as m:
            m.get('https://example.com/robots.txt', exception=aiohttp.ClientError())
            
            await self.spider.initialize()
            
            # Should allow fetching when robots.txt fetch fails
            can_fetch = await self.spider._can_fetch('https://example.com/anything')
            assert can_fetch is True
            
            await self.spider.close()
    
    def test_handle_domain_failure(self):
        """Test domain failure handling."""
        domain = 'problematic.com'
        
        # Should not raise an exception
        self.spider._handle_domain_failure(domain)
        
        # Currently just logs, but could be extended to track failures
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_urls(self):
        """Test fetching multiple URLs concurrently."""
        urls = [
            'https://example.com/page1',
            'https://example.com/page2',
            'https://example.com/page3'
        ]
        
        with aioresponses() as m:
            for i, url in enumerate(urls, 1):
                m.get(url, payload=f'<html><title>Page {i}</title></html>', 
                      content_type='text/html')
            
            results = await self.spider.fetch_multiple_urls(urls, max_concurrent=2)
            
            assert len(results) == 3
            for url in urls:
                assert url in results
                assert results[url] is not None
                assert results[url]['status_code'] == 200
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_urls_with_failures(self):
        """Test fetching multiple URLs with some failures."""
        urls = [
            'https://example.com/success',
            'https://example.com/failure',
            'https://example.com/timeout'
        ]
        
        with aioresponses() as m:
            m.get('https://example.com/success', payload='<html><title>Success</title></html>', 
                  content_type='text/html')
            m.get('https://example.com/failure', status=500)
            m.get('https://example.com/timeout', exception=asyncio.TimeoutError())
            
            results = await self.spider.fetch_multiple_urls(urls)
            
            assert len(results) == 3
            assert results['https://example.com/success'] is not None
            assert results['https://example.com/failure'] is not None  # 500 still returns data
            assert results['https://example.com/timeout'] is None
    
    @pytest.mark.asyncio
    async def test_head_request_success(self):
        """Test successful HEAD request."""
        with aioresponses() as m:
            m.head('https://example.com/check', status=200, 
                   headers={'Content-Type': 'text/html', 'Content-Length': '1234'})
            
            result = await self.spider.head_request('https://example.com/check')
            
            assert result is not None
            assert result['status_code'] == 200
            assert result['content_type'] == 'text/html'
            assert result['content_length'] == '1234'
    
    @pytest.mark.asyncio
    async def test_head_request_failure(self):
        """Test HEAD request failure."""
        with aioresponses() as m:
            m.head('https://example.com/error', exception=aiohttp.ClientError())
            
            result = await self.spider.head_request('https://example.com/error')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_robots_txt_success(self):
        """Test successful robots.txt fetching."""
        robots_content = """
        User-agent: *
        Disallow: /admin/
        Allow: /public/
        """
        
        with aioresponses() as m:
            m.get('http://example.com/robots.txt', payload=robots_content, 
                  content_type='text/plain')
            
            rp = await self.spider._get_robots_txt('example.com')
            
            assert rp is not None
            assert isinstance(rp, RobotFileParser)
            assert 'example.com' in self.spider.robots_cache
    
    @pytest.mark.asyncio
    async def test_get_robots_txt_cached(self):
        """Test robots.txt fetching from cache."""
        # Pre-populate cache
        rp = RobotFileParser()
        self.spider.robots_cache['example.com'] = rp
        
        result = await self.spider._get_robots_txt('example.com')
        
        assert result is rp  # Should return the cached instance
    
    @pytest.mark.asyncio
    async def test_get_robots_txt_not_found(self):
        """Test robots.txt fetching when not found."""
        with aioresponses() as m:
            m.get('http://example.com/robots.txt', status=404)
            
            rp = await self.spider._get_robots_txt('example.com')
            
            assert rp is None
    
    @pytest.mark.asyncio
    async def test_get_robots_txt_error(self):
        """Test robots.txt fetching with error."""
        with aioresponses() as m:
            m.get('http://example.com/robots.txt', exception=aiohttp.ClientError())
            
            rp = await self.spider._get_robots_txt('example.com')
            
            assert rp is None


class TestWebSpiderIntegration:
    """Integration tests for WebSpider with realistic scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = ScanConfigurationSchema(
            max_depth=2,
            max_pages=50,
            requests_per_second=5,
            timeout=10,
            follow_redirects=True,
            respect_robots=True,
            user_agent="Integration-Test-Spider/1.0"
        )
        self.spider = WebSpider(self.config)
    
    @pytest.mark.asyncio
    async def test_wordpress_site_crawling(self):
        """Test crawling a WordPress-like site."""
        robots_content = """
        User-agent: *
        Disallow: /wp-admin/
        Disallow: /wp-includes/
        Allow: /wp-content/uploads/
        """
        
        with aioresponses() as m:
            # Robots.txt
            m.get('https://wordpress.example.com/robots.txt', payload=robots_content)
            
            # Allowed pages
            m.get('https://wordpress.example.com/', 
                  payload='<html><title>WordPress Site</title><body>Welcome</body></html>', 
                  content_type='text/html')
            m.get('https://wordpress.example.com/about/', 
                  payload='<html><title>About Us</title><body>About page</body></html>', 
                  content_type='text/html')
            
            # Test allowed URLs
            result = await self.spider.fetch_url('https://wordpress.example.com/')
            assert result is not None
            assert result['title'] == 'WordPress Site'
            
            result = await self.spider.fetch_url('https://wordpress.example.com/about/')
            assert result is not None
            assert result['title'] == 'About Us'
            
            # Test blocked URL
            result = await self.spider.fetch_url('https://wordpress.example.com/wp-admin/admin.php')
            assert result is None  # Should be blocked by robots.txt
    
    @pytest.mark.asyncio
    async def test_ecommerce_site_crawling(self):
        """Test crawling an e-commerce site with various content types."""
        with aioresponses() as m:
            # Allow all in robots.txt
            m.get('https://shop.example.com/robots.txt', payload='User-agent: *\\nAllow: /')
            
            # Product page (HTML)
            m.get('https://shop.example.com/product/123', 
                  payload='<html><title>Product 123</title><body>Product details</body></html>', 
                  content_type='text/html')
            
            # API endpoint (JSON - should be filtered)
            m.get('https://shop.example.com/api/products', 
                  payload='{"products": []}', content_type='application/json')
            
            # Product image (should be filtered)
            m.get('https://shop.example.com/images/product.jpg', 
                  payload=b'fake_image_data', content_type='image/jpeg')
            
            # CSS file (should be filtered)
            m.get('https://shop.example.com/css/style.css', 
                  payload='body { color: red; }', content_type='text/css')
            
            # Test HTML page
            result = await self.spider.fetch_url('https://shop.example.com/product/123')
            assert result is not None
            assert result['title'] == 'Product 123'
            assert result['is_html'] is True
            
            # Test filtered content types
            result = await self.spider.fetch_url('https://shop.example.com/api/products')
            assert result is None
            
            result = await self.spider.fetch_url('https://shop.example.com/images/product.jpg')
            assert result is None
            
            result = await self.spider.fetch_url('https://shop.example.com/css/style.css')
            assert result is None
    
    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self):
        """Test that rate limiting works correctly."""
        # Set aggressive rate limiting
        self.spider.config.requests_per_second = 2  # 2 requests per second
        self.spider.rate_limiter = RateLimiter(2)
        
        urls = [
            'https://example.com/page1',
            'https://example.com/page2',
            'https://example.com/page3'
        ]
        
        with aioresponses() as m:
            for url in urls:
                m.get(url, payload='<html><title>Test</title></html>', content_type='text/html')
            
            start_time = time.time()
            
            # Fetch URLs sequentially
            for url in urls:
                await self.spider.fetch_url(url)
            
            end_time = time.time()
            
            # Should take at least 1 second (2 intervals of 0.5s each)
            assert end_time - start_time >= 0.9  # Allow small margin
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_retry(self):
        """Test error recovery and retry mechanisms."""
        with aioresponses() as m:
            # First attempt fails with 500, second succeeds
            m.get('https://example.com/unstable', status=500)
            m.get('https://example.com/unstable', 
                  payload='<html><title>Success After Retry</title></html>', 
                  content_type='text/html', status=200)
            
            result = await self.spider.fetch_url('https://example.com/unstable', max_retries=1)
            
            assert result is not None
            assert result['status_code'] == 200
            assert result['title'] == 'Success After Retry'
    
    @pytest.mark.asyncio
    async def test_concurrent_fetching_with_rate_limiting(self):
        """Test concurrent fetching respects rate limiting."""
        urls = [f'https://example.com/page{i}' for i in range(5)]
        
        with aioresponses() as m:
            for url in urls:
                m.get(url, payload='<html><title>Test</title></html>', content_type='text/html')
            
            start_time = time.time()
            results = await self.spider.fetch_multiple_urls(urls, max_concurrent=3)
            end_time = time.time()
            
            # All requests should succeed
            assert len(results) == 5
            for url in urls:
                assert results[url] is not None
            
            # Should take some time due to rate limiting
            assert end_time - start_time >= 0.4  # At least some delay from rate limiting