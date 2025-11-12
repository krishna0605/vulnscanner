import asyncio
import pytest
from unittest.mock import patch, MagicMock
from backend.tasks.crawler_tasks import start_crawl_task


def test_start_crawl_task_thread_execution():
    """Test that start_crawl_task executes properly and indirectly validates _run_in_thread."""
    async def mock_crawl():
        return {"status": "completed"}

    with patch("backend.tasks.crawler_tasks._run_in_thread", return_value={"status": "completed"}) as mock_thread:
        result = start_crawl_task("project_id", "https://example.com")
        mock_thread.assert_called_once()
        assert result == {"status": "completed"}


@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_start_crawl_task_error_handling(mock_logger):
    """Test error handling in start_crawl_task."""
    async def mock_crawl():
        raise Exception("Test Exception")

    with patch("backend.tasks.crawler_tasks._run_in_thread", side_effect=Exception("Test Exception")) as mock_thread:
        with pytest.raises(Exception, match="Test Exception"):
            await start_crawl_task("project_id", "https://example.com")
        mock_thread.assert_called_once()
        mock_logger.error.assert_called_with(
            "Crawl task error for project %s (scan %s): %s", "project_id", "N/A", "Test Exception"
        )


@patch("backend.tasks.crawler_tasks.logger")
def test_run_in_thread_event_loop_cleanup(mock_logger):
    """Test that _run_in_thread cleans up the event loop properly."""
    async def mock_coroutine():
        return {"result": "success"}

    with patch("asyncio.new_event_loop") as mock_new_event_loop:
        mock_loop = MagicMock()
        mock_new_event_loop.return_value = mock_loop

        _run_in_thread(mock_coroutine())

        mock_loop.stop.assert_called_once()
        mock_loop.close.assert_called_once()

        # Ensure no errors were logged during cleanup
        mock_logger.error.assert_not_called()

@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_start_crawl_task_success(mock_logger):
    with patch("backend.tasks.crawler_tasks.start_crawl") as mock_start_crawl:
        mock_start_crawl.return_value = None
        result = await start_crawl_task.apply_async(("scan_id", {"config": "test_config"}))
        assert result.successful()
        mock_logger.info.assert_called_with("Crawl task completed successfully for scan scan_id")

@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_start_crawl_task_failure(mock_logger):
    with patch("backend.tasks.crawler_tasks.start_crawl") as mock_start_crawl:
        mock_start_crawl.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await start_crawl_task.apply_async(("scan_id", {"config": "test_config"}))
        mock_logger.error.assert_called_with(
            "Crawl task failed for scan scan_id: %s", "Test Exception", exc_info=True
        )

@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_stop_crawl_task_success(mock_logger):
    with patch("backend.tasks.crawler_tasks.stop_crawl") as mock_stop_crawl:
        mock_stop_crawl.return_value = None
        result = await stop_crawl_task.apply_async(("scan_id",))
        assert result.successful()
        mock_logger.info.assert_called_with("Successfully stopped crawl for scan scan_id")

@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_stop_crawl_task_failure(mock_logger):
    with patch("backend.tasks.crawler_tasks.stop_crawl") as mock_stop_crawl:
        mock_stop_crawl.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await stop_crawl_task.apply_async(("scan_id",))
        mock_logger.error.assert_called_with(
            "Failed to stop crawl for scan scan_id: %s", "Test Exception", exc_info=True
        )

@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_cleanup_expired_scans_success(mock_logger):
    with patch("backend.tasks.crawler_tasks.cleanup_scans") as mock_cleanup_scans:
        mock_cleanup_scans.return_value = 5
        result = await cleanup_expired_scans.apply_async()
        assert result.successful()
        mock_logger.info.assert_called_with("Successfully cleaned up 5 expired scans")

@pytest.mark.asyncio
@patch("backend.tasks.crawler_tasks.logger")
async def test_cleanup_expired_scans_failure(mock_logger):
    with patch("backend.tasks.crawler_tasks.cleanup_scans") as mock_cleanup_scans:
        mock_cleanup_scans.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await cleanup_expired_scans.apply_async()
        mock_logger.error.assert_called_with(
            "Failed to clean up expired scans: %s", "Test Exception", exc_info=True
        )