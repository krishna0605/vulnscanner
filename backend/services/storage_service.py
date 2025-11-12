"""
Storage Service for managing file storage operations.
"""
import logging
import os
import json
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
import aiofiles

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage operations."""
    
    def __init__(self, storage_path: str = "./storage"):
        """Initialize the storage service."""
        self.storage_path = storage_path
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure the storage directory exists."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            os.makedirs(os.path.join(self.storage_path, "reports"), exist_ok=True)
            os.makedirs(os.path.join(self.storage_path, "exports"), exist_ok=True)
            os.makedirs(os.path.join(self.storage_path, "logs"), exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create storage directories: {e}")
    
    async def save_scan_report(self, scan_id: str, report_data: Dict[str, Any], format: str = "json") -> Optional[str]:
        """Save a scan report to storage."""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"scan_report_{scan_id}_{timestamp}.{format}"
            filepath = os.path.join(self.storage_path, "reports", filename)
            
            if format.lower() == "json":
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(json.dumps(report_data, indent=2, default=str))
            else:
                # For other formats, save as text for now
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(str(report_data))
            
            logger.info(f"Saved scan report to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save scan report: {e}")
            return None
    
    async def save_export_file(self, scan_id: str, data: Union[str, bytes], format: str = "csv") -> Optional[str]:
        """Save an export file to storage."""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"scan_export_{scan_id}_{timestamp}.{format}"
            filepath = os.path.join(self.storage_path, "exports", filename)
            
            if isinstance(data, bytes):
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(data)
            else:
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(data)
            
            logger.info(f"Saved export file to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save export file: {e}")
            return None
    
    async def save_log_file(self, scan_id: str, log_data: str) -> Optional[str]:
        """Save a log file to storage."""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"scan_log_{scan_id}_{timestamp}.log"
            filepath = os.path.join(self.storage_path, "logs", filename)
            
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(log_data)
            
            logger.info(f"Saved log file to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save log file: {e}")
            return None
    
    async def read_file(self, filepath: str) -> Optional[Union[str, bytes]]:
        """Read a file from storage."""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                return None
            
            # Try to read as text first
            try:
                async with aiofiles.open(filepath, 'r') as f:
                    return await f.read()
            except UnicodeDecodeError:
                # If text reading fails, read as bytes
                async with aiofiles.open(filepath, 'rb') as f:
                    return await f.read()
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            return None
    
    async def delete_file(self, filepath: str) -> bool:
        """Delete a file from storage."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted file: {filepath}")
                return True
            else:
                logger.warning(f"File not found for deletion: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {filepath}: {e}")
            return False
    
    def list_files(self, subdirectory: str = "") -> List[str]:
        """List files in a storage subdirectory."""
        try:
            directory = os.path.join(self.storage_path, subdirectory) if subdirectory else self.storage_path
            if not os.path.exists(directory):
                return []
            
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    files.append(item_path)
            
            return files
        except Exception as e:
            logger.error(f"Failed to list files in {subdirectory}: {e}")
            return []
    
    def get_file_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            if not os.path.exists(filepath):
                return None
            
            stat = os.stat(filepath)
            return {
                "filepath": filepath,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "is_file": os.path.isfile(filepath)
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {filepath}: {e}")
            return None