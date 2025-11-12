"""
Logging configuration for the Enhanced Vulnerability Scanner.

This module provides structured JSON logging with correlation IDs,
performance metrics, and security-focused log filtering.
"""

import logging
import logging.config
import json
import time
import uuid
from typing import Optional
from contextvars import ContextVar
from datetime import datetime

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
scan_id_var: ContextVar[Optional[str]] = ContextVar('scan_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs with context.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = self._get_hostname()
    
    def _get_hostname(self) -> str:
        """Get the hostname for log identification."""
        import socket
        try:
            return socket.gethostname()
        except Exception:
            return "unknown"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "hostname": self.hostname,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add context variables if available
        if request_id := request_id_var.get():
            log_entry["request_id"] = request_id
        
        if user_id := user_id_var.get():
            log_entry["user_id"] = user_id
        
        if scan_id := scan_id_var.get():
            log_entry["scan_id"] = scan_id
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields from the log record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        # Add source location for debug logs
        if record.levelno <= logging.DEBUG:
            log_entry["source"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class SecurityFilter(logging.Filter):
    """
    Filter to prevent logging of sensitive information.
    """
    
    SENSITIVE_PATTERNS = [
        'password', 'passwd', 'secret', 'token', 'key', 'auth',
        'credential', 'session', 'cookie', 'authorization'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out logs containing sensitive information."""
        
        # Check message for sensitive patterns
        message = record.getMessage().lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                # Replace sensitive data with placeholder
                record.msg = "[REDACTED - SENSITIVE DATA]"
                record.args = ()
                break
        
        # Check extra fields for sensitive data
        if hasattr(record, 'extra'):
            for key, value in record.extra.items():
                if any(pattern in key.lower() for pattern in self.SENSITIVE_PATTERNS):
                    record.extra[key] = "[REDACTED]"
        
        return True


class PerformanceFilter(logging.Filter):
    """
    Filter to add performance metrics to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance context to log records."""
        
        # Add memory usage for performance-critical logs
        if record.levelno >= logging.WARNING:
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                record.memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
                record.cpu_percent = process.cpu_percent()
            except Exception:
                pass
        
        return True


def setup_logging(
    level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    log_file: str = "logs/app.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up structured logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        log_file: Path to log file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "filters": {
            "security": {
                "()": SecurityFilter,
            },
            "performance": {
                "()": PerformanceFilter,
            }
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "level": level,
                "handlers": [],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": [],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": [],
                "propagate": False
            },
            "aiohttp": {
                "level": "INFO",
                "handlers": [],
                "propagate": False
            }
        }
    }
    
    # Add console handler if enabled
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "structured",
            "filters": ["security", "performance"],
            "stream": "ext://sys.stdout"
        }
        config["loggers"][""]["handlers"].append("console")
        config["loggers"]["uvicorn"]["handlers"].append("console")
        config["loggers"]["sqlalchemy"]["handlers"].append("console")
        config["loggers"]["aiohttp"]["handlers"].append("console")
    
    # Add file handler if enabled
    if enable_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "structured",
            "filters": ["security", "performance"],
            "filename": log_file,
            "maxBytes": max_bytes,
            "backupCount": backup_count,
            "encoding": "utf-8"
        }
        config["loggers"][""]["handlers"].append("file")
        config["loggers"]["uvicorn"]["handlers"].append("file")
        config["loggers"]["sqlalchemy"]["handlers"].append("file")
        config["loggers"]["aiohttp"]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    scan_id: Optional[str] = None
) -> None:
    """
    Set context variables for request tracking.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        scan_id: Scan session identifier
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if scan_id:
        scan_id_var.set(scan_id)


def clear_request_context() -> None:
    """Clear all request context variables."""
    request_id_var.set(None)
    user_id_var.set(None)
    scan_id_var.set(None)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


class LoggerMixin:
    """
    Mixin class to add logging capabilities to other classes.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


# Performance logging decorators
def log_performance(func):
    """
    Decorator to log function performance metrics.
    """
    import functools
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"Function {func.__name__} completed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "status": "success"
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "status": "error",
                    "error": str(e)
                }
            )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"Function {func.__name__} completed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "status": "success"
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "status": "error",
                    "error": str(e)
                }
            )
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    setup_logging(level="DEBUG")
    
    # Get logger
    logger = get_logger(__name__)
    
    # Set request context
    set_request_context(
        request_id=generate_request_id(),
        user_id="user123",
        scan_id="scan456"
    )
    
    # Test logging
    logger.info("Application started")
    logger.debug("Debug information", extra={"component": "test"})
    logger.warning("Warning message", extra={"memory_mb": 150.5})
    logger.error("Error occurred", extra={"error_code": "E001"})
    
    # Test sensitive data filtering
    logger.info("User login with password: secret123")  # Should be redacted
    
    # Clear context
    clear_request_context()
    
    logger.info("Context cleared")