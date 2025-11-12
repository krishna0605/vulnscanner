"""
Tests for web spider HTTP client functionality.
"""

import asyncio
import pytest
import aiohttp
from aioresponses import aioresponses

from crawler.spider import WebSpider
from schemas.dashboard import ScanConfigurationSchema


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
    
    @pytest.mark.asyncio
    async def test_spider_initialization(self):
        """Test spider initialization with configuration."""
        assert self.spider.config == self.config
        assert self.spider.session is None
        assert self.spider.rate_limiter is not None
        assert self.spider.robots_cache == {}
    
    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test HTTP session creation and configuration."""
        await self.spider._ensure_session()
        
        assert self.spider.session is not None
        assert isinstance(self.spider.session, aiohttp.ClientSession)
        
        # Check timeout configuration
        timeout = self.spider.session.timeout
        assert timeout.total == 30
        
        # Check headers
        headers = self.spider.session.headers
        assert headers.get('User-Agent') == "Test-Spider/1.0"
        
        await self.spider.close()
    
    @pytest.mark.asyncio
    async def test_successful_request(self):
        """Test successful HTTP request."""
        url = "http://example.com/page"
        html_content = "<html><body><h1>Test Page</h1></body></html>"
        
        with aioresponses() as m:
            m.get(url, status=200, body=html_content, headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(url)
            
            assert response is not None
            assert response['status_code'] == 200
            assert response['content'] == html_content
            assert response['content_type'] == 'text/html'
            assert response['url'] == url
            assert 'response_time' in response
            assert response['response_time'] > 0
    
    @pytest.mark.asyncio
    async def test_404_response(self):
        """Test handling of 404 responses."""
        url = "http://example.com/notfound"
        
        with aioresponses() as m:
            m.get(url, status=404, body="Not Found", headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(url)
            
            assert response is not None
            assert response['status_code'] == 404
            assert response['content'] == "Not Found"
    
    @pytest.mark.asyncio
    async def test_server_error_response(self):
        """Test handling of server error responses."""
        url = "http://example.com/error"
        
        with aioresponses() as m:
            m.get(url, status=500, body="Internal Server Error", headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(url)
            
            assert response is not None
            assert response['status_code'] == 500
            assert response['content'] == "Internal Server Error"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test request timeout handling."""
        url = "http://example.com/slow"
        
        with aioresponses() as m:
            # Simulate timeout by not responding
            m.get(url, exception=aiohttp.ServerTimeoutError())
            
            response = await self.spider.fetch_url(url)
            
            # Should return None or error response for timeout
            assert response is None or response.get('error') is not None
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        url = "http://nonexistent.example.com"
        
        with aioresponses() as m:
            # Use a simple connection error
            m.get(url, exception=OSError("Connection failed"))
            
            response = await self.spider.fetch_url(url)
            
            # Should return None or error response for connection error
            assert response is None or response.get('error') is not None
    
    @pytest.mark.asyncio
    async def test_redirect_following(self):
        """Test redirect following functionality."""
        original_url = "http://example.com/redirect"
        final_url = "http://example.com/final"
        final_content = "<html><body>Final page</body></html>"
        
        with aioresponses() as m:
            # Set up redirect chain
            m.get(original_url, status=302, headers={'Location': final_url})
            m.get(final_url, status=200, body=final_content, headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(original_url)
            
            assert response is not None
            assert response['status_code'] == 200
            assert response['content'] == final_content
            assert response['url'] == final_url  # Should be final URL after redirect
    
    @pytest.mark.asyncio
    async def test_robots_txt_parsing(self):
        """Test robots.txt parsing and caching."""
        domain = "example.com"
        robots_content = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/

User-agent: Test-Spider
Disallow: /restricted/
Crawl-delay: 1
        """
        
        with aioresponses() as m:
            m.get(f"http://{domain}/robots.txt", status=200, body=robots_content)
            
            robots = await self.spider._get_robots_txt(domain)
            
            assert robots is not None
            assert domain in self.spider.robots_cache
            
            # Test disallowed paths
            assert not robots.can_fetch("Test-Spider", f"http://{domain}/restricted/page")
            assert not robots.can_fetch("*", f"http://{domain}/admin/panel")
            
            # Test allowed paths
            assert robots.can_fetch("Test-Spider", f"http://{domain}/public/page")
            assert robots.can_fetch("*", f"http://{domain}/allowed/page")
    
    @pytest.mark.asyncio
    async def test_robots_txt_respect(self):
        """Test respecting robots.txt rules."""
        url = "http://example.com/admin/secret"
        robots_content = """
User-agent: *
Disallow: /admin/
        """
        
        with aioresponses() as m:
            m.get("http://example.com/robots.txt", status=200, body=robots_content)
            
            # Should not fetch disallowed URL
            response = await self.spider.fetch_url(url)
            
            # Should return None or indicate robots.txt blocked
            assert response is None or response.get('robots_blocked')
    
    @pytest.mark.asyncio
    async def test_robots_txt_disabled(self):
        """Test bypassing robots.txt when disabled."""
        # Create spider with robots.txt disabled
        config = ScanConfigurationSchema(
            max_depth=3,
            max_pages=100,
            requests_per_second=10,
            timeout=30,
            respect_robots=False,
            user_agent="Test-Spider/1.0"
        )
        spider = WebSpider(config)
        
        url = "http://example.com/admin/secret"
        content = "<html><body>Secret admin page</body></html>"
        robots_content = """
User-agent: *
Disallow: /admin/
        """
        
        with aioresponses() as m:
            m.get("http://example.com/robots.txt", status=200, body=robots_content)
            m.get(url, status=200, body=content, headers={'Content-Type': 'text/html'})
            
            response = await spider.fetch_url(url)
            
            # Should fetch despite robots.txt disallow
            assert response is not None
            assert response['status_code'] == 200
            assert response['content'] == content
        
        await spider.close()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        import time
        
        urls = [f"http://example.com/page{i}" for i in range(5)]
        
        with aioresponses() as m:
            for url in urls:
                m.get(url, status=200, body=f"<html>Content for {url}</html>", headers={'Content-Type': 'text/html'})
            
            start_time = time.time()
            
            # Fetch multiple URLs
            tasks = []
            for url in urls:
                tasks.append(self.spider.fetch_url(url))
            
            responses = await asyncio.gather(*tasks)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # With 10 req/s limit, 5 requests should take at least 0.4 seconds
            assert elapsed >= 0.4
            assert all(r is not None for r in responses)
    
    @pytest.mark.asyncio
    async def test_content_type_filtering(self):
        """Test filtering of non-HTML content types."""
        urls_and_types = [
            ("http://example.com/page.html", "text/html", True),
            ("http://example.com/api/data", "application/json", False),
            ("http://example.com/image.jpg", "image/jpeg", False),
            ("http://example.com/document.pdf", "application/pdf", False),
            ("http://example.com/style.css", "text/css", False),
        ]
        
        with aioresponses() as m:
            for url, content_type, should_process in urls_and_types:
                m.get(url, status=200, body="content", headers={'Content-Type': content_type})
                
                response = await self.spider.fetch_url(url)
                
                if should_process:
                    assert response is not None
                    assert response['content_type'] == content_type
                else:
                    # Should either return None or mark as non-HTML
                    assert response is None or not response.get('is_html')
    
    @pytest.mark.asyncio
    async def test_large_response_handling(self):
        """Test handling of large responses."""
        url = "http://example.com/large"
        large_content = "x" * (10 * 1024 * 1024)  # 10MB content
        
        with aioresponses() as m:
            m.get(url, status=200, body=large_content, headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(url)
            
            # Should handle large content or limit it
            assert response is not None
            # Content might be truncated for large responses
            assert len(response['content']) <= len(large_content)
    
    @pytest.mark.asyncio
    async def test_custom_headers(self):
        """Test custom headers in requests."""
        url = "http://example.com/api"
        custom_headers = {
            'Authorization': 'Bearer token123',
            'X-Custom-Header': 'custom-value'
        }
        
        with aioresponses() as m:
            m.get(url, status=200, body='<html><body>Success</body></html>', headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(url, headers=custom_headers)
            
            assert response is not None
            assert response['status_code'] == 200
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self):
        """Test proper session cleanup."""
        await self.spider._ensure_session()
        session = self.spider.session
        
        assert not session.closed
        
        await self.spider.close()
        
        assert session.closed
        assert self.spider.session is None
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import asyncio
        
        urls = [f"http://example.com/page{i}" for i in range(20)]
        
        with aioresponses() as m:
            for url in urls:
                m.get(url, status=200, body=f"<html>Content for {url}</html>", headers={'Content-Type': 'text/html'})
            
            # Create tasks for concurrent execution
            tasks = [self.spider.fetch_url(url) for url in urls]
            
            # Execute concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All requests should complete successfully
            successful_responses = [r for r in responses if isinstance(r, dict) and r.get('status_code') == 200]
            assert len(successful_responses) == len(urls)
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """Test retry mechanism for failed requests."""
        url = "http://example.com/flaky"
        
        with aioresponses() as m:
            # First request fails, second succeeds
            m.get(url, status=500, body="Server Error", headers={'Content-Type': 'text/html'})
            m.get(url, status=200, body="<html>Success</html>", headers={'Content-Type': 'text/html'})
            
            response = await self.spider.fetch_url(url, max_retries=1)
            
            # Should eventually succeed after retry
            assert response is not None
            assert response['status_code'] == 200
            assert response['content'] == "<html>Success</html>"