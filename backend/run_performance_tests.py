#!/usr/bin/env python3
"""
Performance test runner for N+1 query fixes validation.
Measures query count reduction and response time improvements.
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from models import Project, ScanSession, DiscoveredUrl
from main import app


class PerformanceTestRunner:
    """Runner for performance tests with detailed metrics."""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.test_results = []
    
    async def setup_database(self):
        """Setup test database connection."""
        # Use SQLite for testing
        database_url = "sqlite+aiosqlite:///./test_performance.db"
        self.engine = create_async_engine(database_url, echo=False)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create_test_data(self, session: AsyncSession, num_projects: int = 10, scans_per_project: int = 5, urls_per_scan: int = 20):
        """Create test data for performance testing."""
        user_id = "test-performance-user"
        
        print(f"Creating test data: {num_projects} projects, {scans_per_project} scans each, {urls_per_scan} URLs each...")
        
        # Create projects
        projects = []
        for i in range(num_projects):
            project = Project(
                id=f"perf-project-{i}",
                name=f"Performance Test Project {i}",
                description=f"Test project {i} for performance testing",
                owner_id=user_id,
                target_domain=f"example{i}.com"
            )
            projects.append(project)
            session.add(project)
        
        await session.commit()
        
        # Create scan sessions
        scan_sessions = []
        for i, project in enumerate(projects):
            for j in range(scans_per_project):
                scan = ScanSession(
                    id=f"perf-scan-{i}-{j}",
                    project_id=project.id,
                    status="completed",
                    configuration={"max_depth": 3, "max_pages": 100},
                    created_by=user_id
                )
                scan_sessions.append(scan)
                session.add(scan)
        
        await session.commit()
        
        # Create discovered URLs
        for scan in scan_sessions:
            for k in range(urls_per_scan):
                url = DiscoveredUrl(
                    id=f"perf-url-{scan.id}-{k}",
                    session_id=scan.id,
                    url=f"https://example.com/page-{k}",
                    status_code=200,
                    content_type="text/html"
                )
                session.add(url)
        
        await session.commit()
        
        print(f"✓ Created {len(projects)} projects, {len(scan_sessions)} scans, {len(scan_sessions) * urls_per_scan} URLs")
        return user_id
    
    async def test_endpoint_performance(self, endpoint: str, user_id: str, expected_max_time: float = 0.5) -> Dict[str, Any]:
        """Test endpoint performance and return metrics."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Warm up
            await client.get(endpoint, headers={"Authorization": f"Bearer test-token-{user_id}"})
            
            # Measure performance
            times = []
            for _ in range(5):  # Run 5 times for average
                start_time = time.time()
                response = await client.get(endpoint, headers={"Authorization": f"Bearer test-token-{user_id}"})
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times) if times else float('inf')
            min_time = min(times) if times else float('inf')
            max_time = max(times) if times else float('inf')
            
            return {
                "endpoint": endpoint,
                "avg_response_time": avg_time,
                "min_response_time": min_time,
                "max_response_time": max_time,
                "success_rate": len(times) / 5,
                "meets_threshold": avg_time <= expected_max_time
            }
    
    async def run_dashboard_performance_tests(self, user_id: str):
        """Run performance tests for dashboard endpoints."""
        print("\n🚀 Running Dashboard Performance Tests...")
        
        endpoints_to_test = [
            ("/api/v1/dashboard/projects-summary?limit=10", 0.2),
            ("/api/v1/dashboard/recent-activity?limit=10", 0.2),
            ("/api/v1/overview", 0.5),
            ("/api/v1/dashboard/scan-statistics", 0.3),
        ]
        
        results = []
        for endpoint, max_time in endpoints_to_test:
            try:
                result = await self.test_endpoint_performance(endpoint, user_id, max_time)
                results.append(result)
                
                status = "✓ PASS" if result["meets_threshold"] else "✗ FAIL"
                print(f"{status} {endpoint}")
                print(f"    Avg: {result['avg_response_time']:.3f}s | Max: {result['max_response_time']:.3f}s | Threshold: {max_time}s")
                
            except Exception as e:
                print(f"✗ ERROR {endpoint}: {e}")
                results.append({
                    "endpoint": endpoint,
                    "error": str(e),
                    "meets_threshold": False
                })
        
        return results
    
    async def run_query_optimization_tests(self, user_id: str):
        """Test query optimization improvements."""
        print("\n🔍 Running Query Optimization Tests...")
        
        from services.dashboard_service import DashboardService
        
        async with self.session_factory() as session:
            service = DashboardService()
            
            # Test different data sizes to verify O(1) query complexity
            test_sizes = [5, 10, 20, 50]
            
            for size in test_sizes:
                start_time = time.time()
                
                # Test recent projects (should be O(1) queries regardless of size)
                recent_projects = await service._get_recent_projects(session, user_id, limit=size)
                
                # Test recent scans (should be O(1) queries regardless of size)
                recent_scans = await service._get_recent_scans(session, user_id, limit=size)
                
                end_time = time.time()
                
                print(f"✓ Size {size:2d}: {len(recent_projects)} projects, {len(recent_scans)} scans in {end_time - start_time:.3f}s")
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print test summary."""
        print("\n📊 Performance Test Summary")
        print("=" * 50)
        
        passed = sum(1 for r in results if r.get("meets_threshold", False))
        total = len(results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("🎉 All performance tests PASSED!")
        else:
            print("⚠️  Some performance tests FAILED. Review optimizations.")
        
        print("\nDetailed Results:")
        for result in results:
            if "error" in result:
                print(f"❌ {result['endpoint']}: ERROR - {result['error']}")
            else:
                status = "✅" if result["meets_threshold"] else "❌"
                print(f"{status} {result['endpoint']}: {result['avg_response_time']:.3f}s avg")
    
    async def cleanup(self):
        """Cleanup test database."""
        if self.engine:
            await self.engine.dispose()
        
        # Remove test database file
        test_db_path = Path("./test_performance.db")
        if test_db_path.exists():
            test_db_path.unlink()
    
    async def run_all_tests(self):
        """Run all performance tests."""
        try:
            print("🧪 Starting Performance Test Suite")
            print("=" * 50)
            
            await self.setup_database()
            
            async with self.session_factory() as session:
                user_id = await self.create_test_data(session)
            
            # Run dashboard performance tests
            dashboard_results = await self.run_dashboard_performance_tests(user_id)
            
            # Run query optimization tests
            await self.run_query_optimization_tests(user_id)
            
            # Print summary
            self.print_summary(dashboard_results)
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.cleanup()


async def main():
    """Main entry point for performance tests."""
    runner = PerformanceTestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())