"""
Tests for crawler engine orchestration functionality.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

from crawler.engine import CrawlerEngine, CrawlStats
from schemas.dashboard import ScanConfigurationSchema


class TestCrawlerEngine:
    """Test cases for CrawlerEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scan_id = str(uuid4())
        self.config = ScanConfigurationSchema(
            max_depth=3,
            max_pages=100,
            requests_per_second=10,
            timeout=30,
            follow_redirects=True,
            respect_robots=True,
            user_agent="Test-Crawler/1.0",
            scope_patterns=["example.com"],
            exclude_patterns=["logout", "admin"]
        )
        self.start_url = "http://example.com"
        
        # Mock dependencies
        self.mock_db_session = MagicMock()
        
        # Create mocks for components
        self.mock_spider = MagicMock()
        self.mock_parser = MagicMock()
        self.mock_normalizer = MagicMock()
        self.mock_fingerprinter = MagicMock()
        self.mock_session_manager = AsyncMock()
        self.mock_storage = MagicMock()
        
        # Configure async methods
        self.mock_session_manager.initialize = AsyncMock()
        self.mock_session_manager.close = AsyncMock()
        self.mock_spider.fetch_url = AsyncMock()
        self.mock_parser.parse_html = AsyncMock()
        
        # Patch the component classes
        self.spider_patcher = patch('crawler.engine.WebSpider', return_value=self.mock_spider)
        self.parser_patcher = patch('crawler.engine.HTMLParser', return_value=self.mock_parser)
        self.normalizer_patcher = patch('crawler.engine.URLNormalizer', return_value=self.mock_normalizer)
        self.fingerprinter_patcher = patch('crawler.engine.TechnologyFingerprinter', return_value=self.mock_fingerprinter)
        self.session_manager_patcher = patch('crawler.engine.SessionManager', return_value=self.mock_session_manager)
        
        # Start patches
        self.spider_patcher.start()
        self.parser_patcher.start()
        self.normalizer_patcher.start()
        self.fingerprinter_patcher.start()
        self.session_manager_patcher.start()
        
        self.engine = CrawlerEngine(
            config=self.config,
            session_id=1,
            db_session=self.mock_db_session
        )
        
        # Mock internal async methods
        self.engine._update_scan_status = AsyncMock()
        self.engine._update_scan_stats = AsyncMock()
        self.engine._store_discovered_url = AsyncMock()
        self.engine._store_forms = AsyncMock()
        self.engine._apply_rate_limit = AsyncMock()
    
    def teardown_method(self):
        """Clean up patches."""
        self.spider_patcher.stop()
        self.parser_patcher.stop()
        self.normalizer_patcher.stop()
        self.fingerprinter_patcher.stop()
        self.session_manager_patcher.stop()
    
    def test_engine_initialization(self):
        """Test crawler engine initialization."""
        assert self.engine.session_id == 1
        assert self.engine.config == self.config
        assert self.engine.spider is not None
        assert self.engine.parser is not None
        assert self.engine.normalizer is not None
        assert self.engine.fingerprinter is not None
        assert self.engine.db_session == self.mock_db_session
        
        # Check initial state
        assert self.engine.stats.urls_crawled == 0
        assert self.engine.stats.urls_discovered == 0
        assert self.engine.stats.forms_found == 0
        assert self.engine.stats.errors == 0
        assert not self.engine.is_running
        assert not self.engine.should_stop
    
    @pytest.mark.asyncio
    async def test_start_crawl_basic(self):
        """Test basic crawl execution."""
        # Mock spider response
        self.mock_spider.fetch_url.return_value = {
            'status_code': 200,
            'content': '<html><body><a href="/page2">Link</a></body></html>',
            'content_type': 'text/html',
            'url': self.start_url,
            'response_time': 100
        }
        
        # Mock parser response
        self.mock_parser.parse_html.return_value = {
            'links': [{'url': 'http://example.com/page2', 'text': 'Link'}],
            'forms': [],
            'scripts': [],
            'meta': [],
            'title': 'Test Page',
            'comments': [],
            'images': []
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 1
        
        # Mock fingerprinter
        self.mock_fingerprinter.analyze_response.return_value = {
            'server': 'nginx',
            'technologies': ['HTML'],
            'security_headers': {}
        }
        
        # Start crawl
        stats = await self.engine.start_crawl(self.start_url)
        
        # Verify crawl completed
        assert isinstance(stats, CrawlStats)
        assert stats.urls_crawled >= 1
        assert stats.urls_discovered >= 1
        
        # Verify spider was called
        self.mock_spider.fetch_url.assert_called()
        
        # Verify parser was called
        self.mock_parser.parse_html.assert_called()
        
        # Verify database operations were called
        self.engine._store_discovered_url.assert_called()
    
    @pytest.mark.asyncio
    async def test_crawl_depth_limiting(self):
        """Test crawl depth limiting functionality."""
        # Set max depth to 1
        self.config.max_depth = 1
        
        # Mock responses for different depths
        def mock_fetch_url(url):
            if url == self.start_url:
                return {
                    'status_code': 200,
                    'content': '<html><body><a href="/level1">Level 1</a></body></html>',
                    'content_type': 'text/html',
                    'url': url,
                    'response_time': 100
                }
            elif url == 'http://example.com/level1':
                return {
                    'status_code': 200,
                    'content': '<html><body><a href="/level2">Level 2</a></body></html>',
                    'content_type': 'text/html',
                    'url': url,
                    'response_time': 100
                }
            return None
        
        self.mock_spider.fetch_url.side_effect = mock_fetch_url
        
        # Mock parser to return links
        def mock_parse_html(content, base_url):
            if 'Level 1' in content:
                return {
                    'links': [{'url': 'http://example.com/level1', 'text': 'Level 1'}],
                    'forms': [], 'scripts': [], 'meta': [], 'title': 'Page',
                    'comments': [], 'images': []
                }
            elif 'Level 2' in content:
                return {
                    'links': [{'url': 'http://example.com/level2', 'text': 'Level 2'}],
                    'forms': [], 'scripts': [], 'meta': [], 'title': 'Page',
                    'comments': [], 'images': []
                }
            return {'links': [], 'forms': [], 'scripts': [], 'meta': [], 'title': '', 'comments': [], 'images': []}
        
        self.mock_parser.parse_html.side_effect = mock_parse_html
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        
        def mock_get_depth(url):
            if url == self.start_url:
                return 0
            elif 'level1' in url:
                return 1
            elif 'level2' in url:
                return 2
            return 0
        
        self.mock_normalizer.get_url_depth.side_effect = mock_get_depth
        
        # Start crawl
        stats = await self.engine.start_crawl(self.start_url)
        
        # Should not crawl level2 due to depth limit
        fetch_calls = [call[0][0] for call in self.mock_spider.fetch_url.call_args_list]
        assert 'http://example.com/level2' not in fetch_calls
        assert stats.urls_crawled <= 2  # start_url + level1
    
    @pytest.mark.asyncio
    async def test_crawl_page_limiting(self):
        """Test crawl page count limiting."""
        # Set max pages to 3
        self.config.max_pages = 3
        
        # Mock spider to return many links
        self.mock_spider.fetch_url.return_value = {
            'status_code': 200,
            'content': '<html><body>' + ''.join([f'<a href="/page{i}">Page {i}</a>' for i in range(10)]) + '</body></html>',
            'content_type': 'text/html',
            'url': self.start_url,
            'response_time': 100
        }
        
        # Mock parser to return many links
        self.mock_parser.parse_html.return_value = {
            'links': [{'url': f'http://example.com/page{i}', 'text': f'Page {i}'} for i in range(10)],
            'forms': [], 'scripts': [], 'meta': [], 'title': 'Page',
            'comments': [], 'images': []
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 1
        
        # Start crawl
        stats = await self.engine.start_crawl(self.start_url)
        
        # Should stop at max_pages limit
        assert stats.urls_crawled <= self.config.max_pages
    
    @pytest.mark.asyncio
    async def test_scope_pattern_filtering(self):
        """Test URL scope pattern filtering."""
        # Mock spider response with mixed URLs
        self.mock_spider.fetch_url.return_value = {
            'status_code': 200,
            'content': '''<html><body>
                <a href="http://example.com/allowed">Allowed</a>
                <a href="http://other.com/external">External</a>
                <a href="http://example.com/admin">Admin</a>
            </body></html>''',
            'content_type': 'text/html',
            'url': self.start_url,
            'response_time': 100
        }
        
        # Mock parser
        self.mock_parser.parse_html.return_value = {
            'links': [
                {'url': 'http://example.com/allowed', 'text': 'Allowed'},
                {'url': 'http://other.com/external', 'text': 'External'},
                {'url': 'http://example.com/admin', 'text': 'Admin'}
            ],
            'forms': [], 'scripts': [], 'meta': [], 'title': 'Page',
            'comments': [], 'images': []
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 1
        
        # Start crawl
        await self.engine.start_crawl(self.start_url)
        
        # Check that only in-scope URLs were processed
        fetch_calls = [call[0][0] for call in self.mock_spider.fetch_url.call_args_list]
        
        # Should include example.com URLs
        assert any('example.com' in url for url in fetch_calls)
        
        # Should exclude other.com URLs (out of scope)
        assert not any('other.com' in url for url in fetch_calls)
    
    @pytest.mark.asyncio
    async def test_exclude_pattern_filtering(self):
        """Test URL exclude pattern filtering."""
        # Mock spider response with various file types
        self.mock_spider.fetch_url.return_value = {
            'status_code': 200,
            'content': '''<html><body>
                <a href="/page.html">HTML Page</a>
                <a href="/image.jpg">Image</a>
                <a href="/document.pdf">PDF</a>
                <a href="/style.css">CSS</a>
            </body></html>''',
            'content_type': 'text/html',
            'url': self.start_url,
            'response_time': 100
        }
        
        # Mock parser
        self.mock_parser.parse_html.return_value = {
            'links': [
                {'url': 'http://example.com/page.html', 'text': 'HTML Page'},
                {'url': 'http://example.com/image.jpg', 'text': 'Image'},
                {'url': 'http://example.com/document.pdf', 'text': 'PDF'},
                {'url': 'http://example.com/style.css', 'text': 'CSS'}
            ],
            'forms': [], 'scripts': [], 'meta': [], 'title': 'Page',
            'comments': [], 'images': []
        }
        
        # Mock normalizer to exclude certain patterns
        def mock_is_valid_url(url):
            return not any(ext in url for ext in ['.jpg', '.pdf'])
        
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.is_valid_url.side_effect = mock_is_valid_url
        self.mock_normalizer.get_url_depth.return_value = 1
        
        # Start crawl
        await self.engine.start_crawl(self.start_url)
        
        # Check that excluded URLs were not fetched
        fetch_calls = [call[0][0] for call in self.mock_spider.fetch_url.call_args_list]
        
        # Should exclude .jpg and .pdf files
        assert not any('.jpg' in url for url in fetch_calls)
        assert not any('.pdf' in url for url in fetch_calls)
        
        # Should include .html and .css files
        assert any('.html' in url for url in fetch_calls) or any('page.html' in url for url in fetch_calls)
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling during crawl."""
        # Mock spider to raise exception
        self.mock_spider.fetch_url.side_effect = Exception("Network error")
        
        # Start crawl - should not crash
        stats = await self.engine.start_crawl(self.start_url)
        
        # Should record error
        assert stats.errors > 0
        assert stats.urls_crawled == 0
    
    @pytest.mark.asyncio
    async def test_form_extraction_and_storage(self):
        """Test form extraction and storage."""
        # Mock spider response with forms
        self.mock_spider.fetch_url.return_value = {
            'status_code': 200,
            'content': '''<html><body>
                <form action="/login" method="post">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit" value="Login">
                </form>
            </body></html>''',
            'content_type': 'text/html',
            'url': self.start_url,
            'response_time': 100
        }
        
        # Mock parser to return forms
        self.mock_parser.parse_html.return_value = {
            'links': [],
            'forms': [{
                'action': 'http://example.com/login',
                'method': 'post',
                'fields': [
                    {'name': 'username', 'type': 'text'},
                    {'name': 'password', 'type': 'password'},
                    {'name': 'submit', 'type': 'submit', 'value': 'Login'}
                ]
            }],
            'scripts': [], 'meta': [], 'title': 'Login Page',
            'comments': [], 'images': []
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 0
        
        # Start crawl
        stats = await self.engine.start_crawl(self.start_url)
        
        # Verify form was stored
        self.engine._store_forms.assert_called()
        assert stats.forms_found >= 1
    
    @pytest.mark.asyncio
    async def test_technology_fingerprinting(self):
        """Test technology fingerprinting."""
        # Mock spider response
        self.mock_spider.fetch_url.return_value = {
            'status_code': 200,
            'content': '<html><body>Test</body></html>',
            'content_type': 'text/html',
            'url': self.start_url,
            'response_time': 100,
            'headers': {'Server': 'nginx/1.18.0', 'X-Powered-By': 'PHP/7.4'}
        }
        
        # Mock parser
        self.mock_parser.parse_html.return_value = {
            'links': [], 'forms': [], 'scripts': [], 'meta': [], 'title': 'Test',
            'comments': [], 'images': []
        }
        
        # Mock fingerprinter
        self.mock_fingerprinter.analyze_response.return_value = {
            'server': 'nginx/1.18.0',
            'programming_language': 'PHP',
            'framework': None,
            'cms': None,
            'javascript_libraries': [],
            'security_headers': {}
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 0
        
        # Start crawl
        await self.engine.start_crawl(self.start_url)
        
        # Verify fingerprinting was performed
        self.mock_fingerprinter.analyze_response.assert_called()
    
    @pytest.mark.asyncio
    async def test_crawl_stop_functionality(self):
        """Test crawl stop functionality."""
        # Mock long-running spider
        async def slow_fetch(url):
            await asyncio.sleep(0.1)
            return {
                'status_code': 200,
                'content': '<html><body>Test</body></html>',
                'content_type': 'text/html',
                'url': url,
                'response_time': 100
            }
        
        self.mock_spider.fetch_url.side_effect = slow_fetch
        
        # Mock parser
        self.mock_parser.parse_html.return_value = {
            'links': [{'url': f'http://example.com/page{i}', 'text': f'Page {i}'} for i in range(100)],
            'forms': [], 'scripts': [], 'meta': [], 'title': 'Test',
            'comments': [], 'images': []
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 1
        
        # Start crawl in background
        crawl_task = asyncio.create_task(self.engine.start_crawl(self.start_url))
        
        # Wait a bit then stop
        await asyncio.sleep(0.05)
        await self.engine.stop_crawl()
        
        # Wait for crawl to complete
        await crawl_task
        
        # Should have stopped early
        assert self.engine.should_stop
        assert not self.engine.is_running
    
    @pytest.mark.asyncio
    async def test_concurrent_worker_management(self):
        """Test concurrent worker management."""
        # Set high concurrency
        self.config.max_concurrent_requests = 5
        
        # Mock spider with delay
        async def delayed_fetch(url):
            await asyncio.sleep(0.01)
            return {
                'status_code': 200,
                'content': f'<html><body><a href="/next{hash(url) % 10}">Next</a></body></html>',
                'content_type': 'text/html',
                'url': url,
                'response_time': 10
            }
        
        self.mock_spider.fetch_url.side_effect = delayed_fetch
        
        # Mock parser
        self.mock_parser.parse_html.return_value = {
            'links': [{'url': f'http://example.com/next{i}', 'text': f'Next {i}'} for i in range(3)],
            'forms': [], 'scripts': [], 'meta': [], 'title': 'Test',
            'comments': [], 'images': []
        }
        
        # Mock normalizer
        self.mock_normalizer.normalize_url.side_effect = lambda url: url
        self.mock_normalizer.should_exclude_url.return_value = False
        self.mock_normalizer.get_url_depth.return_value = 1
        
        # Start crawl
        stats = await self.engine.start_crawl(self.start_url)
        
        # Should have processed multiple pages concurrently
        assert stats.urls_crawled > 1
        assert stats.urls_discovered > 1
    
    def test_stats_tracking(self):
        """Test crawl statistics tracking."""
        stats = CrawlStats()
        
        # Test initial state
        assert stats.urls_crawled == 0
        assert stats.urls_discovered == 0
        assert stats.forms_found == 0
        assert stats.errors == 0
        assert stats.start_time is not None  # start_time is set by default factory
        assert stats.end_time is None
        
        # Test stats updates
        stats.urls_crawled = 5
        stats.urls_discovered = 10
        stats.forms_found = 2
        stats.errors = 1
        
        assert stats.urls_crawled == 5
        assert stats.urls_discovered == 10
        assert stats.forms_found == 2
        assert stats.errors == 1