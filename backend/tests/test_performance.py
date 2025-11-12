"""
Performance tests for the Enhanced Vulnerability Scanner.

This module contains performance benchmarks for critical system components
including the crawler engine, API endpoints, database operations, and N+1 query fixes.
"""

import asyncio
import time
import pytest
from typing import Dict, Any
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from models import Project, ScanSession, DiscoveredUrl
from crawler.engine import CrawlerEngine, CrawlConfig
from crawler.spider import WebSpider
from crawler.parser import HTMLParser
from main import app


class QueryCounter:
    """Helper class to count database queries during test execution."""
    
    def __init__(self):
        self.query_count = 0
        self.queries = []
    
    def reset(self):
        self.query_count = 0
        self.queries = []
    
    def log_query(self, query):
        self.query_count += 1
        self.queries.append(str(query))


@pytest.fixture
async def query_counter():
    """Fixture to provide query counting functionality."""
    counter = QueryCounter()
    
    # Patch SQLAlchemy execute method to count queries
    original_execute = AsyncSession.execute
    
    async def counting_execute(self, statement, parameters=None, execution_options=None, bind_arguments=None, _parent_execute_state=None, _add_event=None):
        counter.log_query(statement)
        return await original_execute(self, statement, parameters, execution_options, bind_arguments, _parent_execute_state, _add_event)
    
    with patch.object(AsyncSession, 'execute', counting_execute):
        yield counter


@pytest.fixture
async def test_data(db_session: AsyncSession):
    """Create test data for performance testing."""
    # Create test user
    user_id = "test-user-performance"
    
    # Create test projects
    projects = []
    for i in range(10):
        project = Project(
            id=f"project-{i}",
            name=f"Test Project {i}",
            description=f"Performance test project {i}",
            owner_id=user_id,
            target_domain=f"example{i}.com"
        )
        projects.append(project)
        db_session.add(project)
    
    await db_session.commit()
    
    # Create test scan sessions
    scan_sessions = []
    for i, project in enumerate(projects):
        for j in range(5):  # 5 scans per project
            scan = ScanSession(
                id=f"scan-{i}-{j}",
                project_id=project.id,
                status="completed",
                configuration={"max_depth": 3, "max_pages": 100},
                created_by=user_id
            )
            scan_sessions.append(scan)
            db_session.add(scan)
    
    await db_session.commit()
    
    # Create test URLs for each scan
    for scan in scan_sessions:
        for k in range(20):  # 20 URLs per scan
            url = DiscoveredUrl(
                id=f"url-{scan.id}-{k}",
                session_id=scan.id,
                url=f"https://example.com/page-{k}",
                status_code=200,
                content_type="text/html"
            )
            db_session.add(url)
    
    await db_session.commit()
    
    return {
        "user_id": user_id,
        "projects": projects,
        "scan_sessions": scan_sessions
    }


class TestDashboardPerformance:
    """Performance tests for dashboard endpoints."""
    
    @pytest.mark.asyncio
    async def test_projects_summary_query_count(self, query_counter: QueryCounter, test_data: Dict[str, Any]):
        """Test that get_projects_summary uses optimized queries."""
        query_counter.reset()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Mock authentication
            with patch("core.auth_deps.get_user_id", return_value=test_data["user_id"]):
                response = await client.get("/api/v1/dashboard/projects-summary?limit=10")
        
        assert response.status_code == 200
        
        # Should use only 1 query instead of N+1 queries
        # 1 query for the optimized JOIN with subquery
        assert query_counter.query_count <= 2, f"Expected ≤2 queries, got {query_counter.query_count}"
        
        # Verify response structure
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        
        for project_summary in data:
            assert "id" in project_summary
            assert "name" in project_summary
            assert "latest_scan" in project_summary
    
    @pytest.mark.asyncio
    async def test_projects_summary_response_time(self, test_data: Dict[str, Any]):
        """Test response time improvement for projects summary."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Mock authentication
            with patch("core.auth_deps.get_user_id", return_value=test_data["user_id"]):
                start_time = time.time()
                response = await client.get("/api/v1/dashboard/projects-summary?limit=10")
                end_time = time.time()
        
        assert response.status_code == 200
        
        response_time = end_time - start_time
        # Should respond within 200ms for 10 projects with 5 scans each
        assert response_time < 0.2, f"Response time {response_time:.3f}s exceeds 200ms threshold"
    
    @pytest.mark.asyncio
    async def test_recent_activity_query_count(self, query_counter: QueryCounter, test_data: Dict[str, Any]):
        """Test that get_recent_activity uses optimized queries."""
        query_counter.reset()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch("core.auth_deps.get_user_id", return_value=test_data["user_id"]):
                response = await client.get("/api/v1/dashboard/recent-activity?limit=10")
        
        assert response.status_code == 200
        
        # Should use only 1 query with JOIN instead of N+1 queries
        assert query_counter.query_count <= 2, f"Expected ≤2 queries, got {query_counter.query_count}"
    
    @pytest.mark.asyncio
    async def test_dashboard_overview_performance(self, query_counter: QueryCounter, test_data: Dict[str, Any]):
        """Test overall dashboard overview performance."""
        query_counter.reset()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch("core.auth_deps.get_user_id", return_value=test_data["user_id"]):
                start_time = time.time()
                response = await client.get("/api/v1/overview")
                end_time = time.time()
        
        assert response.status_code == 200
        
        response_time = end_time - start_time
        # Dashboard overview should load quickly
        assert response_time < 0.5, f"Dashboard overview response time {response_time:.3f}s exceeds 500ms threshold"
        
        # Should use reasonable number of queries
        assert query_counter.query_count <= 10, f"Expected ≤10 queries, got {query_counter.query_count}"


class TestDashboardServicePerformance:
    """Performance tests for dashboard service methods."""
    
    @pytest.mark.asyncio
    async def test_get_recent_projects_query_count(self, db_session: AsyncSession, query_counter: QueryCounter, test_data: Dict[str, Any]):
        """Test that _get_recent_projects uses optimized queries."""
        from services.dashboard_service import DashboardService
        
        query_counter.reset()
        service = DashboardService()
        
        # Call the optimized method
        result = await service._get_recent_projects(db_session, test_data["user_id"], limit=5)
        
        # Should use only 1 aggregated query instead of N+1 queries
        assert query_counter.query_count <= 2, f"Expected ≤2 queries, got {query_counter.query_count}"
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) <= 5
        
        for project in result:
            assert "scan_count" in project
            assert "url_count" in project
            assert "last_scan_date" in project
    
    @pytest.mark.asyncio
    async def test_get_recent_scans_query_count(self, db_session: AsyncSession, query_counter: QueryCounter, test_data: Dict[str, Any]):
        """Test that _get_recent_scans uses optimized queries."""
        from services.dashboard_service import DashboardService
        
        query_counter.reset()
        service = DashboardService()
        
        # Call the optimized method
        result = await service._get_recent_scans(db_session, test_data["user_id"], limit=10)
        
        # Should use only 1 aggregated query instead of N+1 queries
        assert query_counter.query_count <= 2, f"Expected ≤2 queries, got {query_counter.query_count}"
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) <= 10
        
        for scan in result:
            assert "url_count" in scan


class TestQueryOptimizationBenchmarks:
    """Benchmark tests to measure query optimization improvements."""
    
    @pytest.mark.asyncio
    async def test_query_count_reduction_benchmark(self, db_session: AsyncSession, test_data: Dict[str, Any]):
        """Benchmark query count reduction for various operations."""
        from services.dashboard_service import DashboardService
        
        service = DashboardService()
        user_id = test_data["user_id"]
        
        # Test scenarios with different data sizes
        test_scenarios = [
            {"limit": 5, "expected_max_queries": 2},
            {"limit": 10, "expected_max_queries": 2},
            {"limit": 20, "expected_max_queries": 2},
        ]
        
        for scenario in test_scenarios:
            query_counter = QueryCounter()
            
            with patch.object(AsyncSession, 'execute', query_counter.counting_execute):
                # Test recent projects
                await service._get_recent_projects(db_session, user_id, limit=scenario["limit"])
                projects_queries = query_counter.query_count
                
                query_counter.reset()
                
                # Test recent scans
                await service._get_recent_scans(db_session, user_id, limit=scenario["limit"])
                scans_queries = query_counter.query_count
            
            # Verify query count is independent of data size (O(1) instead of O(n))
            assert projects_queries <= scenario["expected_max_queries"], \
                f"Recent projects: {projects_queries} queries > {scenario['expected_max_queries']} for limit {scenario['limit']}"
            
            assert scans_queries <= scenario["expected_max_queries"], \
                f"Recent scans: {scans_queries} queries > {scenario['expected_max_queries']} for limit {scenario['limit']}"
    
    @pytest.mark.asyncio
    async def test_response_time_benchmark(self, test_data: Dict[str, Any]):
        """Benchmark response times for optimized endpoints."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch("core.auth_deps.get_user_id", return_value=test_data["user_id"]):
                
                # Test multiple endpoints
                endpoints = [
                    "/api/v1/dashboard/projects-summary?limit=10",
                    "/api/v1/dashboard/recent-activity?limit=10",
                    "/api/v1/overview",
                ]
                
                for endpoint in endpoints:
                    # Warm up
                    await client.get(endpoint)
                    
                    # Measure response time
                    start_time = time.time()
                    response = await client.get(endpoint)
                    end_time = time.time()
                    
                    assert response.status_code == 200
                    
                    response_time = end_time - start_time
                    # All optimized endpoints should respond quickly
                    assert response_time < 0.3, \
                        f"Endpoint {endpoint} response time {response_time:.3f}s exceeds 300ms threshold"


class TestCrawlerPerformance:
    """Performance tests for the crawler engine."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="crawler")
    async def test_url_processing_speed(self, benchmark):
        """Test URL processing speed under load."""
        
        async def process_urls():
            config = CrawlConfig(
                max_depth=2,
                max_pages=100,
                requests_per_second=50
            )
            
            engine = CrawlerEngine(config)
            
            # Mock the HTTP responses
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text.return_value = """
                <html>
                    <head><title>Test Page</title></head>
                    <body>
                        <a href="/page1">Page 1</a>
                        <a href="/page2">Page 2</a>
                        <a href="/page3">Page 3</a>
                    </body>
                </html>
                """
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                # Process URLs and measure time
                start_time = time.time()
                await engine._process_url("https://example.com", 1)
                end_time = time.time()
                
                return end_time - start_time
        
        # Benchmark the URL processing
        result = benchmark(lambda: asyncio.run(process_urls()))
        
        # Assert performance requirements
        assert result < 0.5, "URL processing should complete within 500ms"

    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="crawler")
    async def test_concurrent_crawling_performance(self, benchmark):
        """Test performance of concurrent crawling operations."""
        
        async def concurrent_crawl():
            config = CrawlConfig(
                max_depth=1,
                max_pages=50,
                requests_per_second=20,
                max_concurrent_requests=10
            )
            
            engine = CrawlerEngine(config)
            
            # Mock HTTP responses
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text.return_value = "<html><body>Test</body></html>"
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                # Simulate concurrent crawling
                tasks = []
                for i in range(10):
                    task = engine._process_url(f"https://example.com/page{i}", 1)
                    tasks.append(task)
                
                start_time = time.time()
                await asyncio.gather(*tasks)
                end_time = time.time()
                
                return end_time - start_time
        
        result = benchmark(lambda: asyncio.run(concurrent_crawl()))
        
        # Should handle 10 concurrent requests efficiently
        assert result < 2.0, "Concurrent crawling should complete within 2 seconds"

    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="parser")
    async def test_html_parsing_performance(self, benchmark):
        """Test HTML parsing performance with large documents."""
        
        # Generate large HTML document
        large_html = """
        <html>
            <head>
                <title>Large Test Page</title>
                <meta name="description" content="Test page for performance testing">
            </head>
            <body>
        """
        
        # Add many links and forms
        for i in range(1000):
            large_html += f'<a href="/page{i}">Page {i}</a>\n'
        
        for i in range(100):
            large_html += f"""
            <form action="/form{i}" method="post">
                <input type="text" name="field{i}" value="value{i}">
                <input type="submit" value="Submit {i}">
            </form>
            """
        
        large_html += """
            </body>
        </html>
        """
        
        def parse_html():
            parser = HTMLParser()
            return parser.parse_html(large_html, "https://example.com")
        
        result = benchmark(parse_html)
        
        # Verify parsing results
        assert len(result.links) == 1000
        assert len(result.forms) == 100
        
        # Performance assertion
        assert benchmark.stats.stats.mean < 0.1, "HTML parsing should complete within 100ms on average"


class TestAPIPerformanceBenchmarks:
    """Additional API performance benchmarks."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="api")
    async def test_health_endpoint_performance(self, benchmark):
        """Test health endpoint response time."""
        
        async def call_health_endpoint():
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/health")
                return response.status_code
        
        status_code = benchmark(lambda: asyncio.run(call_health_endpoint()))
        
        assert status_code == 200
        assert benchmark.stats.stats.mean < 0.05, "Health endpoint should respond within 50ms on average"

    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="api")
    async def test_concurrent_api_requests(self, benchmark):
        """Test API performance under concurrent load."""
        
        async def concurrent_requests():
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Create multiple concurrent requests
                tasks = []
                for i in range(50):
                    task = client.get("/api/v1/health")
                    tasks.append(task)
                
                start_time = time.time()
                responses = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Verify all requests succeeded
                for response in responses:
                    assert response.status_code == 200
                
                return end_time - start_time
        
        duration = benchmark(lambda: asyncio.run(concurrent_requests()))
        
        # 50 concurrent requests should complete within reasonable time
        assert duration < 5.0, "50 concurrent requests should complete within 5 seconds"


class TestRateLimitingPerformance:
    """Performance tests for rate limiting mechanisms."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="rate_limiting")
    async def test_rate_limiter_performance(self, benchmark):
        """Test rate limiter performance under load."""
        
        async def test_rate_limiting():
            config = CrawlConfig(requests_per_second=10)
            spider = WebSpider(config)
            
            # Test rate limiting with many requests
            start_time = time.time()
            
            tasks = []
            for i in range(20):  # 20 requests with 10 req/s limit
                task = spider._wait_for_rate_limit()
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            end_time = time.time()
            
            return end_time - start_time
        
        duration = benchmark(lambda: asyncio.run(test_rate_limiting()))
        
        # Rate limiting should work efficiently
        # 20 requests at 10 req/s should take approximately 2 seconds
        assert 1.8 <= duration <= 2.5, f"Rate limiting timing incorrect: {duration}s"


@pytest.mark.benchmark(group="system")
def test_system_startup_time(benchmark):
    """Test system startup time."""
    
    def startup_system():
        # Simulate system initialization
        config = CrawlConfig()
        _ = CrawlerEngine(config)
        _ = HTMLParser()
        
        # Simulate initialization time
        time.sleep(0.1)
        
        return True
    
    result = benchmark(startup_system)
    
    assert result is True
    assert benchmark.stats.stats.mean < 0.2, "System startup should complete within 200ms on average"


@pytest.mark.benchmark(group="memory")
def test_memory_efficiency():
    """Test memory efficiency of core components."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create multiple instances to test memory usage
    engines = []
    for i in range(10):
        config = CrawlConfig(max_pages=100)
        engine = CrawlerEngine(config)
        engines.append(engine)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_per_engine = (final_memory - initial_memory) / 10
    
    # Each engine instance should use reasonable memory
    assert memory_per_engine < 10, f"Each engine instance uses too much memory: {memory_per_engine}MB"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__,
        "-v",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-json=benchmark-results.json"
    ])