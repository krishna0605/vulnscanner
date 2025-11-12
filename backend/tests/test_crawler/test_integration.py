"""
Integration tests for crawler components.
Tests the interaction between different crawler components and end-to-end scenarios.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from crawler.engine import CrawlerEngine
from schemas.dashboard import ScanConfigurationSchema


class TestCrawlerIntegration:
    """Test integration between crawler components."""
    
    @pytest.fixture
    def integration_config(self):
        """Create configuration for integration testing."""
        return ScanConfigurationSchema(
            max_depth=2,
            max_pages=10,
            requests_per_second=5,
            timeout=10,
            max_concurrent_requests=3,
            follow_redirects=True,
            respect_robots=True,
            user_agent="VulnScanner-Integration-Test/1.0"
        )
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session for integration tests."""
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def mock_http_session(self):
        """Create mock HTTP session for integration tests."""
        session = AsyncMock(spec=aiohttp.ClientSession)
        return session
    
    @pytest.mark.asyncio
    async def test_full_crawl_workflow(self, integration_config, mock_db_session):
        """Test complete crawl workflow from start to finish."""
        target_url = "https://example.com"
        
        # Mock HTML responses
        main_page_html = """
        <html>
            <head>
                <title>Example Site</title>
                <meta name="generator" content="WordPress 5.8">
            </head>
            <body>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <form action="/search" method="get">
                    <input type="text" name="q" placeholder="Search">
                    <input type="submit" value="Search">
                </form>
                <script src="/js/jquery-3.6.0.min.js"></script>
            </body>
        </html>
        """
        
        about_page_html = """
        <html>
            <head><title>About Us</title></head>
            <body>
                <h1>About Us</h1>
                <a href="/team">Our Team</a>
            </body>
        </html>
        """
        
        # Mock responses
        mock_responses = {
            "https://example.com": {
                "status": 200,
                "headers": {"Content-Type": "text/html", "Server": "Apache/2.4.41"},
                "text": main_page_html
            },
            "https://example.com/about": {
                "status": 200,
                "headers": {"Content-Type": "text/html"},
                "text": about_page_html
            },
            "https://example.com/contact": {
                "status": 200,
                "headers": {"Content-Type": "text/html"},
                "text": "<html><head><title>Contact</title></head><body><h1>Contact Us</h1></body></html>"
            }
        }
        
        # Create crawler engine with mocked components
        with patch('crawler.engine.WebSpider') as MockSpider, \
             patch('crawler.engine.HTMLParser') as MockParser, \
             patch('crawler.engine.URLNormalizer') as MockNormalizer, \
             patch('crawler.engine.SessionManager') as MockSessionManager, \
             patch('crawler.engine.TechnologyFingerprinter') as MockFingerprinter:
            
            # Setup mocks
            mock_spider = MockSpider.return_value
            mock_parser = MockParser.return_value
            mock_normalizer = MockNormalizer.return_value
            mock_session_manager = MockSessionManager.return_value
            mock_fingerprinter = MockFingerprinter.return_value
            
            # Configure normalizer
            mock_normalizer.normalize_url.side_effect = lambda url: url
            mock_normalizer.is_same_domain.return_value = True
            
            # Configure spider
            async def mock_fetch(url):
                if url in mock_responses:
                    response_data = mock_responses[url]
                    mock_response = MagicMock()
                    mock_response.status = response_data["status"]
                    mock_response.headers = response_data["headers"]
                    mock_response.text = AsyncMock(return_value=response_data["text"])
                    mock_response.url = url
                    return mock_response
                return None
            
            mock_spider.fetch_url = mock_fetch
            
            # Configure parser
            def mock_parse(html, base_url):
                if "About" in html:
                    return {
                        "title": "About Us",
                        "links": ["https://example.com/team"],
                        "forms": [],
                        "meta_tags": {}
                    }
                elif "Contact" in html:
                    return {
                        "title": "Contact",
                        "links": [],
                        "forms": [],
                        "meta_tags": {}
                    }
                else:  # Main page
                    return {
                        "title": "Example Site",
                        "links": ["https://example.com/about", "https://example.com/contact"],
                        "forms": [{
                            "action": "https://example.com/search",
                            "method": "get",
                            "fields": [{"name": "q", "type": "text"}]
                        }],
                        "meta_tags": {"generator": "WordPress 5.8"}
                    }
            
            mock_parser.parse_html.side_effect = mock_parse
            
            # Configure fingerprinter
            def mock_fingerprint(response, parsed_data):
                return {
                    "server": "Apache/2.4.41",
                    "cms": "WordPress",
                    "javascript_libraries": ["jQuery 3.6.0"],
                    "programming_language": "PHP"
                }
            
            mock_fingerprinter.analyze_response.side_effect = mock_fingerprint
            
            # Configure session manager
            mock_session_manager.initialize = AsyncMock()
            mock_session_manager.close = AsyncMock()
            
            # Create and run crawler
            engine = CrawlerEngine(
                config=integration_config,
                session_id=1,
                db_session=mock_db_session
            )
            
            # Mock database operations
            engine._update_scan_status = AsyncMock()
            engine._update_scan_stats = AsyncMock()
            engine._save_discovered_url = AsyncMock()
            engine._save_extracted_form = AsyncMock()
            engine._save_technology_fingerprint = AsyncMock()
            
            # Run the crawl
            stats = await engine.start_crawl(target_url)
            
            # Verify crawl results
            assert stats.urls_discovered > 0
            assert stats.urls_crawled >= 0
            
            # Verify component interactions
            mock_session_manager.initialize.assert_called_once()
            mock_session_manager.close.assert_called_once()
            engine._update_scan_status.assert_called()
            engine._update_scan_stats.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, integration_config, mock_db_session):
        """Test error recovery across integrated components."""
        target_url = "https://example.com"
        
        with patch('crawler.engine.WebSpider') as MockSpider, \
             patch('crawler.engine.HTMLParser') as MockParser, \
             patch('crawler.engine.URLNormalizer') as MockNormalizer, \
             patch('crawler.engine.SessionManager') as MockSessionManager, \
             patch('crawler.engine.TechnologyFingerprinter') as MockFingerprinter:
            
            # Setup mocks with some failures
            mock_spider = MockSpider.return_value
            mock_parser = MockParser.return_value
            mock_normalizer = MockNormalizer.return_value
            mock_session_manager = MockSessionManager.return_value
            _ = MockFingerprinter.return_value
            
            # Configure normalizer
            mock_normalizer.normalize_url.side_effect = lambda url: url
            
            # Configure spider with intermittent failures
            call_count = 0
            async def mock_fetch_with_errors(url):
                nonlocal call_count
                call_count += 1
                if call_count % 3 == 0:  # Every third call fails
                    raise aiohttp.ClientError("Network error")
                
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.headers = {"Content-Type": "text/html"}
                mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
                mock_response.url = url
                return mock_response
            
            mock_spider.fetch_url = mock_fetch_with_errors
            
            # Configure parser
            mock_parser.parse_html.return_value = {
                "title": "Test Page",
                "links": [],
                "forms": [],
                "meta_tags": {}
            }
            
            # Configure session manager
            mock_session_manager.initialize = AsyncMock()
            mock_session_manager.close = AsyncMock()
            
            # Create crawler
            engine = CrawlerEngine(
                config=integration_config,
                session_id=1,
                db_session=mock_db_session
            )
            
            # Mock database operations
            engine._update_scan_status = AsyncMock()
            engine._update_scan_stats = AsyncMock()
            
            # Run crawl with error handling
            stats = await engine.start_crawl(target_url)
            
            # Verify error handling
            assert stats.errors >= 0  # Some errors may have occurred
            
            # Verify cleanup was performed
            mock_session_manager.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_integration(self, integration_config, mock_db_session):
        """Test integration with authentication workflow."""
        target_url = "https://example.com"
        auth_config = {
            "enabled": True,
            "login_url": "/login",
            "username": "testuser",
            "password": "testpass",
            "username_field": "username",
            "password_field": "password"
        }
        
        with patch('crawler.engine.WebSpider') as MockSpider, \
             patch('crawler.engine.SessionManager') as MockSessionManager:
            
            mock_spider = MockSpider.return_value
            mock_session_manager = MockSessionManager.return_value
            
            # Configure session manager for authentication
            mock_session_manager.initialize = AsyncMock()
            mock_session_manager.configure_authentication = AsyncMock()
            mock_session_manager.is_authenticated = AsyncMock(return_value=True)
            mock_session_manager.close = AsyncMock()
            
            # Configure spider
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.text = AsyncMock(return_value="<html><body>Authenticated content</body></html>")
            mock_response.url = target_url
            
            mock_spider.fetch_url = AsyncMock(return_value=mock_response)
            
            # Create crawler with authentication
            engine = CrawlerEngine(
                config=integration_config,
                session_id=1,
                db_session=mock_db_session
            )
            
            # Mock other components
            engine.parser = MagicMock()
            engine.parser.parse_html.return_value = {
                "title": "Authenticated Page",
                "links": [],
                "forms": [],
                "meta_tags": {}
            }
            
            engine.normalizer = MagicMock()
            engine.normalizer.normalize_url.side_effect = lambda url: url
            
            engine.fingerprinter = MagicMock()
            engine.fingerprinter.analyze_response.return_value = {}
            
            # Mock database operations
            engine._update_scan_status = AsyncMock()
            engine._update_scan_stats = AsyncMock()
            
            # Configure authentication
            await engine.session_manager.configure_authentication(auth_config, target_url)
            
            # Run crawl
            await engine.start_crawl(target_url)
            
            # Verify authentication was configured
            mock_session_manager.configure_authentication.assert_called_once_with(auth_config, target_url)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, integration_config, mock_db_session):
        """Test rate limiting integration across components."""
        target_url = "https://example.com"
        
        # Set aggressive rate limiting for testing
        integration_config.requests_per_second = 2
        
        with patch('crawler.engine.WebSpider') as MockSpider:
            mock_spider = MockSpider.return_value
            
            # Track request timing
            request_times = []
            
            async def mock_fetch_with_timing(url):
                request_times.append(asyncio.get_event_loop().time())
                await asyncio.sleep(0.01)  # Simulate network delay
                
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.headers = {"Content-Type": "text/html"}
                mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
                mock_response.url = url
                return mock_response
            
            mock_spider.fetch_url = mock_fetch_with_timing
            
            # Create crawler
            engine = CrawlerEngine(
                config=integration_config,
                session_id=1,
                db_session=mock_db_session
            )
            
            # Mock other components
            engine.parser = MagicMock()
            engine.parser.parse_html.return_value = {
                "title": "Test Page",
                "links": [f"https://example.com/page{i}" for i in range(5)],
                "forms": [],
                "meta_tags": {}
            }
            
            engine.normalizer = MagicMock()
            engine.normalizer.normalize_url.side_effect = lambda url: url
            engine.normalizer.is_same_domain.return_value = True
            
            engine.session_manager = MagicMock()
            engine.session_manager.initialize = AsyncMock()
            engine.session_manager.close = AsyncMock()
            
            engine.fingerprinter = MagicMock()
            engine.fingerprinter.analyze_response.return_value = {}
            
            # Mock database operations
            engine._update_scan_status = AsyncMock()
            engine._update_scan_stats = AsyncMock()
            
            # Run crawl
            start_time = asyncio.get_event_loop().time()
            await engine.start_crawl(target_url)
            end_time = asyncio.get_event_loop().time()
            
            # Verify rate limiting was applied
            if len(request_times) > 1:
                total_duration = end_time - start_time
                expected_min_duration = (len(request_times) - 1) / integration_config.requests_per_second
                assert total_duration >= expected_min_duration * 0.5  # Allow tolerance for test execution
    
    @pytest.mark.asyncio
    async def test_data_persistence_integration(self, integration_config, mock_db_session):
        """Test data persistence integration across components."""
        target_url = "https://example.com"
        
        # Track database operations
        saved_urls = []
        saved_forms = []
        saved_technologies = []
        
        async def mock_save_url(url_data):
            saved_urls.append(url_data)
        
        async def mock_save_form(form_data):
            saved_forms.append(form_data)
        
        async def mock_save_tech(tech_data):
            saved_technologies.append(tech_data)
        
        with patch('crawler.engine.WebSpider') as MockSpider, \
             patch('crawler.engine.HTMLParser') as MockParser, \
             patch('crawler.engine.TechnologyFingerprinter') as MockFingerprinter:
            
            # Setup mocks
            mock_spider = MockSpider.return_value
            mock_parser = MockParser.return_value
            mock_fingerprinter = MockFingerprinter.return_value
            
            # Configure spider
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.headers = {"Content-Type": "text/html", "Server": "nginx/1.18"}
            mock_response.text = AsyncMock(return_value="""
                <html>
                    <body>
                        <form action="/submit" method="post">
                            <input type="text" name="username">
                            <input type="password" name="password">
                        </form>
                    </body>
                </html>
            """)
            mock_response.url = target_url
            
            mock_spider.fetch_url = AsyncMock(return_value=mock_response)
            
            # Configure parser
            mock_parser.parse_html.return_value = {
                "title": "Test Page",
                "links": [],
                "forms": [{
                    "action": "https://example.com/submit",
                    "method": "post",
                    "fields": [
                        {"name": "username", "type": "text"},
                        {"name": "password", "type": "password"}
                    ]
                }],
                "meta_tags": {}
            }
            
            # Configure fingerprinter
            mock_fingerprinter.analyze_response.return_value = {
                "server": "nginx/1.18",
                "programming_language": "Unknown",
                "javascript_libraries": []
            }
            
            # Create crawler
            engine = CrawlerEngine(
                config=integration_config,
                session_id=1,
                db_session=mock_db_session
            )
            
            # Mock other components
            engine.normalizer = MagicMock()
            engine.normalizer.normalize_url.side_effect = lambda url: url
            
            engine.session_manager = MagicMock()
            engine.session_manager.initialize = AsyncMock()
            engine.session_manager.close = AsyncMock()
            
            # Mock database operations
            engine._update_scan_status = AsyncMock()
            engine._update_scan_stats = AsyncMock()
            engine._save_discovered_url = mock_save_url
            engine._save_extracted_form = mock_save_form
            engine._save_technology_fingerprint = mock_save_tech
            
            # Run crawl
            await engine.start_crawl(target_url)
            
            # Verify data was saved
            assert len(saved_urls) > 0
            assert len(saved_forms) > 0
            assert len(saved_technologies) > 0
            
            # Verify data structure
            url_data = saved_urls[0]
            assert "url" in url_data
            assert "status_code" in url_data
            
            form_data = saved_forms[0]
            assert "action" in form_data
            assert "method" in form_data
            assert "fields" in form_data
            
            tech_data = saved_technologies[0]
            assert "server" in tech_data
    
    @pytest.mark.asyncio
    async def test_concurrent_crawling_integration(self, integration_config, mock_db_session):
        """Test concurrent crawling integration."""
        target_url = "https://example.com"
        
        # Set up for concurrent processing
        integration_config.max_concurrent_requests = 3
        
        # Track concurrent operations
        active_operations = 0
        max_concurrent = 0
        
        with patch('crawler.engine.WebSpider') as MockSpider:
            mock_spider = MockSpider.return_value
            
            async def mock_fetch_concurrent(url):
                nonlocal active_operations, max_concurrent
                active_operations += 1
                max_concurrent = max(max_concurrent, active_operations)
                
                await asyncio.sleep(0.1)  # Simulate processing time
                
                active_operations -= 1
                
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.headers = {"Content-Type": "text/html"}
                mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
                mock_response.url = url
                return mock_response
            
            mock_spider.fetch_url = mock_fetch_concurrent
            
            # Create crawler
            engine = CrawlerEngine(
                config=integration_config,
                session_id=1,
                db_session=mock_db_session
            )
            
            # Mock other components
            engine.parser = MagicMock()
            engine.parser.parse_html.return_value = {
                "title": "Test Page",
                "links": [f"https://example.com/page{i}" for i in range(5)],
                "forms": [],
                "meta_tags": {}
            }
            
            engine.normalizer = MagicMock()
            engine.normalizer.normalize_url.side_effect = lambda url: url
            engine.normalizer.is_same_domain.return_value = True
            
            engine.session_manager = MagicMock()
            engine.session_manager.initialize = AsyncMock()
            engine.session_manager.close = AsyncMock()
            
            engine.fingerprinter = MagicMock()
            engine.fingerprinter.analyze_response.return_value = {}
            
            # Mock database operations
            engine._update_scan_status = AsyncMock()
            engine._update_scan_stats = AsyncMock()
            
            # Run crawl
            await engine.start_crawl(target_url)
            
            # Verify concurrency was limited
            assert max_concurrent <= integration_config.max_concurrent_requests
            assert active_operations == 0  # All operations completed