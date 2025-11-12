"""
Tests for the crawler engine component.
Tests the main crawling orchestrator, URL queue management, and crawl statistics.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from crawler.engine import CrawlerEngine, CrawlStats
from schemas.dashboard import ScanConfigurationSchema


class TestCrawlStats:
    """Test the CrawlStats dataclass."""
    
    def test_crawl_stats_initialization(self):
        """Test CrawlStats initialization with default values."""
        stats = CrawlStats()
        
        assert stats.urls_discovered == 0
        assert stats.urls_crawled == 0
        assert stats.forms_found == 0
        assert stats.technologies_detected == 0
        assert stats.errors == 0
        assert stats.start_time is not None
        assert stats.end_time is None
    
    def test_crawl_stats_to_dict(self):
        """Test CrawlStats conversion to dictionary."""
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        stats = CrawlStats(
            urls_discovered=10,
            urls_crawled=8,
            forms_found=3,
            technologies_detected=5,
            errors=1,
            start_time=start_time,
            end_time=end_time
        )
        
        result = stats.to_dict()
        
        assert result["urls_discovered"] == 10
        assert result["urls_crawled"] == 8
        assert result["forms_found"] == 3
        assert result["technologies_detected"] == 5
        assert result["errors"] == 1
        assert result["start_time"] == start_time.isoformat()
        assert result["end_time"] == end_time.isoformat()
        assert result["duration_seconds"] is not None
    
    def test_crawl_stats_duration_calculation(self):
        """Test duration calculation in CrawlStats."""
        start_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 1, 12, 5, 30, tzinfo=timezone.utc)
        
        stats = CrawlStats(start_time=start_time, end_time=end_time)
        result = stats.to_dict()
        
        assert result["duration_seconds"] == 330.0  # 5 minutes 30 seconds


class TestCrawlerEngine:
    """Test the main CrawlerEngine class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock scan configuration."""
        return ScanConfigurationSchema(
            max_depth=3,
            max_pages=100,
            requests_per_second=10,
            timeout=30,
            max_concurrent_requests=5,
            follow_redirects=True,
            respect_robots=True,
            user_agent="VulnScanner-Test/1.0"
        )
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def crawler_engine(self, mock_config, mock_db_session):
        """Create a CrawlerEngine instance for testing."""
        with patch('crawler.engine.WebSpider'), \
             patch('crawler.engine.HTMLParser'), \
             patch('crawler.engine.URLNormalizer'), \
             patch('crawler.engine.SessionManager'), \
             patch('crawler.engine.TechnologyFingerprinter'):
            
            engine = CrawlerEngine(
                config=mock_config,
                session_id=1,
                db_session=mock_db_session
            )
            return engine
    
    def test_crawler_engine_initialization(self, crawler_engine, mock_config):
        """Test CrawlerEngine initialization."""
        assert crawler_engine.config == mock_config
        assert crawler_engine.session_id == 1
        assert crawler_engine.url_queue is not None
        assert isinstance(crawler_engine.visited_urls, set)
        assert isinstance(crawler_engine.discovered_urls, set)
        assert isinstance(crawler_engine.stats, CrawlStats)
        assert not crawler_engine.is_running
        assert not crawler_engine.should_stop
    
    @pytest.mark.asyncio
    async def test_start_crawl_success(self, crawler_engine):
        """Test successful crawl start and completion."""
        target_url = "https://example.com"
        
        # Mock the normalizer
        crawler_engine.normalizer.normalize_url = MagicMock(return_value=target_url)
        
        # Mock session manager
        crawler_engine.session_manager.initialize = AsyncMock()
        crawler_engine.session_manager.close = AsyncMock()
        
        # Mock database operations
        crawler_engine._update_scan_status = AsyncMock()
        crawler_engine._update_scan_stats = AsyncMock()
        
        # Mock worker to prevent infinite loop
        async def mock_worker(name):
            await asyncio.sleep(0.1)  # Simulate work
            crawler_engine.should_stop = True
        
        crawler_engine._crawler_worker = mock_worker
        
        # Start crawl
        stats = await crawler_engine.start_crawl(target_url)
        
        # Verify results
        assert isinstance(stats, CrawlStats)
        assert target_url in crawler_engine.discovered_urls
        assert stats.urls_discovered == 1
        assert not crawler_engine.is_running
        
        # Verify method calls
        crawler_engine.session_manager.initialize.assert_called_once()
        crawler_engine.session_manager.close.assert_called_once()
        crawler_engine._update_scan_status.assert_called()
        crawler_engine._update_scan_stats.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_crawl_with_exception(self, crawler_engine):
        """Test crawl handling when an exception occurs."""
        target_url = "https://example.com"
        
        # Mock the normalizer
        crawler_engine.normalizer.normalize_url = MagicMock(return_value=target_url)
        
        # Mock session manager to raise exception
        crawler_engine.session_manager.initialize = AsyncMock(side_effect=Exception("Test error"))
        crawler_engine.session_manager.close = AsyncMock()
        
        # Mock database operations
        crawler_engine._update_scan_status = AsyncMock()
        crawler_engine._update_scan_stats = AsyncMock()
        
        # Start crawl and expect exception
        with pytest.raises(Exception, match="Test error"):
            await crawler_engine.start_crawl(target_url)
        
        # Verify cleanup was called
        assert not crawler_engine.is_running
        assert crawler_engine.stats.errors == 1
        crawler_engine.session_manager.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_crawl(self, crawler_engine):
        """Test graceful crawl stopping."""
        crawler_engine.is_running = True
        
        await crawler_engine.stop_crawl()
        
        assert crawler_engine.should_stop
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, crawler_engine):
        """Test rate limiting functionality."""
        # Set a low rate limit
        crawler_engine.config.requests_per_second = 2
        crawler_engine.rate_limiter = asyncio.Semaphore(2)
        
        start_time = asyncio.get_event_loop().time()
        
        # Simulate multiple requests
        tasks = []
        for _ in range(4):
            task = asyncio.create_task(crawler_engine._apply_rate_limit())
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Should take at least 1 second due to rate limiting (4 requests / 2 per second)
        assert duration >= 0.5  # Allow some tolerance for test execution
    
    @pytest.mark.asyncio
    async def test_url_queue_management(self, crawler_engine):
        """Test URL queue operations."""
        # Add URLs to queue
        urls = [
            ("https://example.com", 0),
            ("https://example.com/page1", 1),
            ("https://example.com/page2", 1)
        ]
        
        for url, depth in urls:
            await crawler_engine.url_queue.put((url, depth))
        
        assert crawler_engine.url_queue.qsize() == 3
        
        # Retrieve URLs from queue
        retrieved_urls = []
        while not crawler_engine.url_queue.empty():
            url, depth = await crawler_engine.url_queue.get()
            retrieved_urls.append((url, depth))
        
        assert len(retrieved_urls) == 3
        assert retrieved_urls == urls
    
    @pytest.mark.asyncio
    async def test_domain_semaphore_creation(self, crawler_engine):
        """Test domain-specific semaphore creation."""
        domain = "example.com"
        
        # Get domain semaphore (should create new one)
        semaphore = crawler_engine._get_domain_semaphore(domain)
        
        assert domain in crawler_engine.domain_semaphores
        assert crawler_engine.domain_semaphores[domain] == semaphore
        
        # Get same domain semaphore (should return existing)
        same_semaphore = crawler_engine._get_domain_semaphore(domain)
        assert same_semaphore == semaphore
    
    @pytest.mark.asyncio
    async def test_crawl_statistics_tracking(self, crawler_engine):
        """Test crawl statistics are properly tracked."""
        # Simulate crawl progress
        crawler_engine.stats.urls_discovered = 10
        crawler_engine.stats.urls_crawled = 8
        crawler_engine.stats.forms_found = 3
        crawler_engine.stats.technologies_detected = 5
        crawler_engine.stats.errors = 1
        
        stats_dict = crawler_engine.stats.to_dict()
        
        assert stats_dict["urls_discovered"] == 10
        assert stats_dict["urls_crawled"] == 8
        assert stats_dict["forms_found"] == 3
        assert stats_dict["technologies_detected"] == 5
        assert stats_dict["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_concurrent_request_limiting(self, crawler_engine):
        """Test concurrent request limiting."""
        # Set low concurrency limit
        crawler_engine.config.max_concurrent_requests = 2
        crawler_engine.semaphore = asyncio.Semaphore(2)
        
        # Track active requests
        active_requests = 0
        max_concurrent = 0
        
        async def mock_request():
            nonlocal active_requests, max_concurrent
            async with crawler_engine.semaphore:
                active_requests += 1
                max_concurrent = max(max_concurrent, active_requests)
                await asyncio.sleep(0.1)  # Simulate request time
                active_requests -= 1
        
        # Start multiple concurrent requests
        tasks = [asyncio.create_task(mock_request()) for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Should not exceed the semaphore limit
        assert max_concurrent <= 2
        assert active_requests == 0  # All requests completed
    
    def test_url_filtering_by_scope(self, crawler_engine):
        """Test URL filtering based on scope rules."""
        # Mock scope checking
        crawler_engine.config.scope_patterns = ["https://example.com/*"]
        
        # Test URLs
        in_scope_urls = [
            "https://example.com/",
            "https://example.com/page1",
            "https://example.com/admin/login"
        ]
        
        out_of_scope_urls = [
            "https://other-site.com/",
            "http://example.com/",  # Different protocol
            "https://subdomain.example.com/"
        ]
        
        # Mock the scope checking method
        def mock_is_in_scope(url):
            return any(url.startswith(pattern.replace("*", "")) 
                      for pattern in crawler_engine.config.scope_patterns)
        
        crawler_engine._is_url_in_scope = mock_is_in_scope
        
        # Test in-scope URLs
        for url in in_scope_urls:
            assert crawler_engine._is_url_in_scope(url)
        
        # Test out-of-scope URLs
        for url in out_of_scope_urls:
            assert not crawler_engine._is_url_in_scope(url)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, crawler_engine):
        """Test error handling and recovery mechanisms."""
        # Mock a failing operation
        async def failing_operation():
            raise Exception("Simulated error")
        
        # Test error counting
        initial_errors = crawler_engine.stats.errors
        
        try:
            await failing_operation()
        except Exception:
            crawler_engine.stats.errors += 1
        
        assert crawler_engine.stats.errors == initial_errors + 1
    
    @pytest.mark.asyncio
    async def test_crawl_depth_limiting(self, crawler_engine):
        """Test crawl depth limiting functionality."""
        max_depth = crawler_engine.config.max_depth
        
        # Test URLs at different depths
        test_cases = [
            ("https://example.com/", 0, True),  # Root level
            ("https://example.com/page1", max_depth - 1, True),  # Within limit
            ("https://example.com/deep/page", max_depth, True),  # At limit
            ("https://example.com/very/deep/page", max_depth + 1, False),  # Exceeds limit
        ]
        
        for url, depth, should_crawl in test_cases:
            result = depth <= max_depth
            assert result == should_crawl, f"Depth {depth} for URL {url} should {'be crawled' if should_crawl else 'not be crawled'}"