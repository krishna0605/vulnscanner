import pytest
from unittest.mock import patch, MagicMock
from backend.tasks.report_tasks import (
    generate_report_task, generate_json_report, generate_csv_report, generate_pdf_report
)

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_report_task_success(mock_logger):
    with patch("backend.tasks.report_tasks.upload_report_to_storage") as mock_upload:
        mock_upload.return_value = "mock_url"
        result = await generate_report_task.apply_async(("scan_id", "json"))
        assert result.successful()
        mock_logger.info.assert_called_with("Report generated for scan scan_id: mock_url")

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_report_task_failure(mock_logger):
    with patch("backend.tasks.report_tasks.upload_report_to_storage") as mock_upload:
        mock_upload.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await generate_report_task.apply_async(("scan_id", "json"))
        mock_logger.error.assert_called_with(
            "Report generation failed for scan scan_id in format json: %s", "Test Exception", exc_info=True
        )

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_json_report_success(mock_logger):
    with patch("backend.tasks.report_tasks.fetch_scan_data") as mock_fetch:
        mock_fetch.return_value = {"key": "value"}
        result = await generate_json_report.apply_async(("scan_id",))
        assert result.successful()
        assert result.result == '{\n    "key": "value"\n}'

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_json_report_failure(mock_logger):
    with patch("backend.tasks.report_tasks.fetch_scan_data") as mock_fetch:
        mock_fetch.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await generate_json_report.apply_async(("scan_id",))
        mock_logger.error.assert_called_with(
            "Failed to generate JSON report for scan scan_id: %s", "Test Exception", exc_info=True
        )

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_csv_report_success(mock_logger):
    with patch("backend.tasks.report_tasks.fetch_scan_data") as mock_fetch:
        mock_fetch.return_value = {"headers": ["col1", "col2"], "rows": [["val1", "val2"]]}
        result = await generate_csv_report.apply_async(("scan_id",))
        assert result.successful()
        assert result.result == "col1,col2\r\nval1,val2\r\n"

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_csv_report_failure(mock_logger):
    with patch("backend.tasks.report_tasks.fetch_scan_data") as mock_fetch:
        mock_fetch.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await generate_csv_report.apply_async(("scan_id",))
        mock_logger.error.assert_called_with(
            "Failed to generate CSV report for scan scan_id: %s", "Test Exception", exc_info=True
        )

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_pdf_report_success(mock_logger):
    with patch("backend.tasks.report_tasks.fetch_scan_data") as mock_fetch:
        mock_fetch.return_value = {"key": "value"}
        with patch("backend.tasks.report_tasks.create_pdf") as mock_create_pdf:
            mock_create_pdf.return_value = b"mock_pdf_content"
            result = await generate_pdf_report.apply_async(("scan_id",))
            assert result.successful()
            assert result.result == b"mock_pdf_content"

@pytest.mark.asyncio
@patch("backend.tasks.report_tasks.logger")
async def test_generate_pdf_report_failure(mock_logger):
    with patch("backend.tasks.report_tasks.fetch_scan_data") as mock_fetch:
        mock_fetch.side_effect = Exception("Test Exception")
        with pytest.raises(Exception):
            await generate_pdf_report.apply_async(("scan_id",))
        mock_logger.error.assert_called_with(
            "Failed to generate PDF report for scan scan_id: %s", "Test Exception", exc_info=True
        )