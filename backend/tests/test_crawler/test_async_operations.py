"""
Tests for async operations and crawler coordination.
Tests concurrent crawling, rate limiting, and async task management.
"""

import pytest
import asyncio

from schemas.dashboard import ScanConfigurationSchema


class TestAsyncOperations:
    """Test async operations in the crawler system."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock scan configuration for async testing."""
        return ScanConfigurationSchema(
            max_depth=2,
            max_pages=50,
            requests_per_second=5,
            timeout=10,
            max_concurrent_requests=3,
            follow_redirects=True,
            respect_robots=True
        )
    
    @pytest.mark.asyncio
    async def test_concurrent_url_processing(self, mock_config):
        """Test concurrent processing of multiple URLs."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
            "https://example.com/page4",
            "https://example.com/page5"
        ]
        
        # Track processing order and concurrency
        processing_order = []
        active_tasks = 0
        max_concurrent = 0
        
        async def mock_process_url(url):
            nonlocal active_tasks, max_concurrent
            active_tasks += 1
            max_concurrent = max(max_concurrent, active_tasks)
            
            processing_order.append(f"start_{url}")
            await asyncio.sleep(0.1)  # Simulate processing time
            processing_order.append(f"end_{url}")
            
            active_tasks -= 1
            return f"processed_{url}"
        
        # Process URLs concurrently with semaphore
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
        
        async def limited_process(url):
            async with semaphore:
                return await mock_process_url(url)
        
        # Execute concurrent processing
        tasks = [limited_process(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # Verify results
        assert len(results) == 5
        assert all(result.startswith("processed_") for result in results)
        assert max_concurrent <= 3  # Respects concurrency limit
        
        # Verify all URLs were processed
        start_events = [event for event in processing_order if event.startswith("start_")]
        end_events = [event for event in processing_order if event.startswith("end_")]
        assert len(start_events) == 5
        assert len(end_events) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiting_with_timing(self):
        """Test rate limiting with actual timing verification."""
        requests_per_second = 2
        num_requests = 4
        
        # Track request timestamps
        request_times = []
        
        async def mock_request():
            request_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.01)  # Minimal processing time
        
        # Rate limiter implementation
        class RateLimiter:
            def __init__(self, rate):
                self.rate = rate
                self.tokens = rate
                self.last_update = asyncio.get_event_loop().time()
            
            async def acquire(self):
                now = asyncio.get_event_loop().time()
                elapsed = now - self.last_update
                self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
        
        rate_limiter = RateLimiter(requests_per_second)
        
        # Execute rate-limited requests
        start_time = asyncio.get_event_loop().time()
        
        async def rate_limited_request():
            await rate_limiter.acquire()
            await mock_request()
        
        tasks = [rate_limited_request() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        total_duration = end_time - start_time
        
        # Verify timing constraints
        expected_min_duration = (num_requests - 1) / requests_per_second
        assert total_duration >= expected_min_duration * 0.8  # Allow some tolerance
        
        # Verify request spacing
        if len(request_times) > 1:
            intervals = [request_times[i] - request_times[i-1] 
                        for i in range(1, len(request_times))]
            # Most intervals should respect rate limit
            valid_intervals = sum(1 for interval in intervals if interval >= (1/requests_per_second) * 0.8)
            assert valid_intervals >= len(intervals) * 0.7  # Allow some variance
    
    @pytest.mark.asyncio
    async def test_async_queue_operations(self):
        """Test async queue operations for URL management."""
        queue = asyncio.Queue(maxsize=5)
        
        # Producer task
        async def producer():
            for i in range(10):
                url = f"https://example.com/page{i}"
                await queue.put((url, i % 3))  # (url, depth)
                await asyncio.sleep(0.01)  # Simulate discovery delay
        
        # Consumer task
        async def consumer(consumer_id):
            processed = []
            while True:
                try:
                    url, depth = await asyncio.wait_for(queue.get(), timeout=0.5)
                    processed.append((url, depth, consumer_id))
                    queue.task_done()
                    await asyncio.sleep(0.02)  # Simulate processing time
                except asyncio.TimeoutError:
                    break
            return processed
        
        # Run producer and multiple consumers
        producer_task = asyncio.create_task(producer())
        consumer_tasks = [
            asyncio.create_task(consumer(f"consumer_{i}"))
            for i in range(3)
        ]
        
        # Wait for producer to finish
        await producer_task
        
        # Wait for queue to be processed
        await queue.join()
        
        # Collect results from consumers
        consumer_results = await asyncio.gather(*consumer_tasks)
        
        # Verify all URLs were processed
        all_processed = []
        for result in consumer_results:
            all_processed.extend(result)
        
        assert len(all_processed) == 10
        processed_urls = [item[0] for item in all_processed]
        expected_urls = [f"https://example.com/page{i}" for i in range(10)]
        
        for expected_url in expected_urls:
            assert expected_url in processed_urls
    
    @pytest.mark.asyncio
    async def test_error_handling_in_async_operations(self):
        """Test error handling in async operations."""
        # Simulate operations that may fail
        async def unreliable_operation(item_id, fail_probability=0.3):
            await asyncio.sleep(0.01)
            if item_id % 3 == 0:  # Simulate failures
                raise Exception(f"Operation failed for item {item_id}")
            return f"success_{item_id}"
        
        # Process items with error handling
        items = list(range(10))
        results = []
        errors = []
        
        async def safe_operation(item_id):
            try:
                result = await unreliable_operation(item_id)
                results.append(result)
                return result
            except Exception as e:
                errors.append((item_id, str(e)))
                return None
        
        # Execute operations concurrently
        tasks = [safe_operation(item_id) for item_id in items]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify error handling
        assert len(errors) > 0  # Some operations should have failed
        assert len(results) > 0  # Some operations should have succeeded
        assert len(errors) + len(results) == len(items)
        
        # Verify specific failures
        failed_items = [item_id for item_id, _ in errors]
        expected_failures = [i for i in range(10) if i % 3 == 0]
        assert failed_items == expected_failures
    
    @pytest.mark.asyncio
    async def test_async_context_manager_usage(self):
        """Test proper async context manager usage."""
        # Mock async context manager
        class MockAsyncResource:
            def __init__(self, resource_id):
                self.resource_id = resource_id
                self.is_open = False
                self.operations = []
            
            async def __aenter__(self):
                self.is_open = True
                self.operations.append("opened")
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.is_open = False
                self.operations.append("closed")
                return False
            
            async def do_work(self):
                if not self.is_open:
                    raise RuntimeError("Resource not open")
                self.operations.append("work_done")
                await asyncio.sleep(0.01)
        
        # Test proper resource management
        resource = MockAsyncResource("test_resource")
        
        async with resource:
            assert resource.is_open
            await resource.do_work()
        
        assert not resource.is_open
        assert resource.operations == ["opened", "work_done", "closed"]
    
    @pytest.mark.asyncio
    async def test_async_timeout_handling(self):
        """Test timeout handling in async operations."""
        # Simulate operations with different durations
        async def slow_operation(duration):
            await asyncio.sleep(duration)
            return f"completed_after_{duration}s"
        
        # Test successful operation within timeout
        try:
            result = await asyncio.wait_for(slow_operation(0.1), timeout=0.2)
            assert result == "completed_after_0.1s"
        except asyncio.TimeoutError:
            pytest.fail("Operation should not have timed out")
        
        # Test timeout handling
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(0.3), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_async_semaphore_fairness(self):
        """Test fairness in async semaphore usage."""
        semaphore = asyncio.Semaphore(2)
        execution_order = []
        
        async def worker(worker_id, work_duration):
            async with semaphore:
                execution_order.append(f"start_{worker_id}")
                await asyncio.sleep(work_duration)
                execution_order.append(f"end_{worker_id}")
        
        # Create workers with different work durations
        workers = [
            worker("fast_1", 0.05),
            worker("slow_1", 0.15),
            worker("fast_2", 0.05),
            worker("slow_2", 0.15),
            worker("fast_3", 0.05),
        ]
        
        # Execute workers
        await asyncio.gather(*workers)
        
        # Verify execution order makes sense
        assert len(execution_order) == 10  # 5 starts + 5 ends
        
        # Count concurrent executions
        active_workers = 0
        max_concurrent = 0
        
        for event in execution_order:
            if event.startswith("start_"):
                active_workers += 1
                max_concurrent = max(max_concurrent, active_workers)
            elif event.startswith("end_"):
                active_workers -= 1
        
        assert max_concurrent <= 2  # Semaphore limit
        assert active_workers == 0  # All workers completed
    
    @pytest.mark.asyncio
    async def test_async_cancellation_handling(self):
        """Test proper handling of task cancellation."""
        cancelled_tasks = []
        completed_tasks = []
        
        async def cancellable_task(task_id, duration):
            try:
                await asyncio.sleep(duration)
                completed_tasks.append(task_id)
                return f"completed_{task_id}"
            except asyncio.CancelledError:
                cancelled_tasks.append(task_id)
                raise
        
        # Create tasks with different durations
        tasks = [
            asyncio.create_task(cancellable_task(f"task_{i}", 0.1 * (i + 1)))
            for i in range(5)
        ]
        
        # Let some tasks start, then cancel them
        await asyncio.sleep(0.15)  # Let first task complete
        
        # Cancel remaining tasks
        for task in tasks[1:]:
            task.cancel()
        
        # Wait for all tasks to finish (completed or cancelled)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify cancellation handling
        assert len(completed_tasks) >= 1  # At least first task completed
        assert len(cancelled_tasks) >= 1  # Some tasks were cancelled
        
        # Verify results contain both completed and cancelled tasks
        successful_results = [r for r in results if isinstance(r, str)]
        cancelled_results = [r for r in results if isinstance(r, asyncio.CancelledError)]
        
        assert len(successful_results) >= 1
        assert len(cancelled_results) >= 1
    
    @pytest.mark.asyncio
    async def test_async_batch_processing(self):
        """Test batch processing of async operations."""
        # Simulate processing items in batches
        items = list(range(20))
        batch_size = 5
        processed_batches = []
        
        async def process_batch(batch):
            batch_results = []
            for item in batch:
                await asyncio.sleep(0.01)  # Simulate processing
                batch_results.append(f"processed_{item}")
            processed_batches.append(batch_results)
            return batch_results
        
        # Create batches
        batches = [
            items[i:i + batch_size]
            for i in range(0, len(items), batch_size)
        ]
        
        # Process batches concurrently
        batch_tasks = [process_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*batch_tasks)
        
        # Verify batch processing
        assert len(batch_results) == 4  # 20 items / 5 per batch
        assert len(processed_batches) == 4
        
        # Verify all items were processed
        all_processed = []
        for batch_result in batch_results:
            all_processed.extend(batch_result)
        
        assert len(all_processed) == 20
        expected_results = [f"processed_{i}" for i in range(20)]
        assert sorted(all_processed) == sorted(expected_results)