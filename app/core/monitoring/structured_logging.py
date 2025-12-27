"""
Structured Logging System

Provides structured logging with JSON format, log aggregation, and enhanced context.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """
    Structured JSON formatter for logs.

    Formats log records as JSON for easy parsing and aggregation.
    """

    def __init__(
        self,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_module: bool = True,
        include_function: bool = True,
        include_line: bool = True,
        include_traceback: bool = True,
        extra_fields: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize structured formatter.

        Args:
            include_timestamp: Include timestamp in log
            include_level: Include log level
            include_module: Include module name
            include_function: Include function name
            include_line: Include line number
            include_traceback: Include traceback for exceptions
            extra_fields: Extra fields to include in all logs
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_module = include_module
        self.include_function = include_function
        self.include_line = include_line
        self.include_traceback = include_traceback
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {}

        # Timestamp
        if self.include_timestamp:
            log_data["timestamp"] = datetime.utcnow().isoformat()

        # Level
        if self.include_level:
            log_data["level"] = record.levelname

        # Message
        log_data["message"] = record.getMessage()

        # Module information
        if self.include_module:
            log_data["module"] = record.module
            log_data["logger"] = record.name

        # Function and line
        if self.include_function:
            log_data["function"] = record.funcName
        if self.include_line:
            log_data["line"] = record.lineno

        # Exception information
        if record.exc_info and self.include_traceback:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": (
                    self.formatException(record.exc_info) if record.exc_info else None
                ),
            }

        # Extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "levelno",
                "levelname",
                "pathname",
                "lineno",
                "exc_info",
                "exc_text",
                "stack_info",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "module",
                "funcName",
                "logger",
            ]:
                log_data[key] = value

        # Add extra fields
        log_data.update(self.extra_fields)

        return json.dumps(log_data, default=str)


class StructuredLogger:
    """
    Structured logger with context support.
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        use_json: bool = True,
        log_file: Optional[Path] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            level: Log level
            use_json: Use JSON formatting
            log_file: Optional log file path
            extra_fields: Extra fields to include in all logs
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        # Remove existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        if use_json:
            formatter = StructuredFormatter(extra_fields=extra_fields)
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.extra_fields = extra_fields or {}

    def _add_context(self, **kwargs) -> Dict[str, Any]:
        """Add context to log record."""
        context = self.extra_fields.copy()
        context.update(kwargs)
        return context

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(message, extra=self._add_context(**kwargs))

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(message, extra=self._add_context(**kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(message, extra=self._add_context(**kwargs))

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.logger.error(message, extra=self._add_context(**kwargs))

    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(message, extra=self._add_context(**kwargs))

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=self._add_context(**kwargs))


def setup_structured_logging(
    level: str = "INFO",
    use_json: bool = True,
    log_file: Optional[Path] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> StructuredLogger:
    """
    Setup structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Use JSON formatting
        log_file: Optional log file path
        extra_fields: Extra fields to include in all logs

    Returns:
        Structured logger instance
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    logger = StructuredLogger(
        name="voicestudio",
        level=log_level,
        use_json=use_json,
        log_file=log_file,
        extra_fields=extra_fields,
    )

    return logger


# Global structured logger instance
_structured_logger: Optional[StructuredLogger] = None


def get_structured_logger() -> StructuredLogger:
    """
    Get or create global structured logger.

    Returns:
        Structured logger instance
    """
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = setup_structured_logging()
    return _structured_logger
