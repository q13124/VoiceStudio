"""
Log Sanitizer.

Task 2.2.5: XSS prevention for logs.
Sanitizes user input before logging.
"""

from __future__ import annotations

import html
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SanitizerConfig:
    """Configuration for log sanitizer."""

    # Fields to redact completely
    redact_fields: set[str] = field(
        default_factory=lambda: {
            "password",
            "secret",
            "token",
            "api_key",
            "apikey",
            "authorization",
            "auth",
            "credential",
            "credit_card",
            "ssn",
            "social_security",
        }
    )

    # Maximum string length in logs
    max_string_length: int = 1000

    # Truncation suffix
    truncation_suffix: str = "...[TRUNCATED]"

    # Enable HTML escaping
    escape_html: bool = True

    # Patterns to sanitize
    sanitize_patterns: list[str] = field(
        default_factory=lambda: [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"on\w+\s*=",  # Event handlers
            r"<iframe[^>]*>",  # iframes
        ]
    )


class LogSanitizer:
    """
    Sanitizes data before logging.

    Features:
    - Sensitive field redaction
    - HTML/XSS prevention
    - Length limiting
    - Pattern removal
    """

    def __init__(self, config: SanitizerConfig | None = None):
        self.config = config or SanitizerConfig()

        self._patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.config.sanitize_patterns
        ]

    def sanitize(self, value: Any) -> Any:
        """
        Sanitize a value for logging.

        Handles strings, dicts, and lists recursively.
        """
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, dict):
            return self._sanitize_dict(value)
        elif isinstance(value, list):
            return [self.sanitize(item) for item in value]
        elif isinstance(value, (int, float, bool, type(None))):
            return value
        else:
            # Convert to string and sanitize
            return self._sanitize_string(str(value))

    def _sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        result = value

        # Remove dangerous patterns
        for pattern in self._patterns:
            result = pattern.sub("[SANITIZED]", result)

        # Escape HTML
        if self.config.escape_html:
            result = html.escape(result)

        # Truncate if too long
        if len(result) > self.config.max_string_length:
            result = result[: self.config.max_string_length] + self.config.truncation_suffix

        return result

    def _sanitize_dict(self, value: dict) -> dict:
        """Sanitize a dictionary."""
        result = {}

        for key, val in value.items():
            # Check if key should be redacted
            key_lower = str(key).lower()

            should_redact = any(redact_key in key_lower for redact_key in self.config.redact_fields)

            if should_redact:
                result[key] = "[REDACTED]"
            else:
                result[key] = self.sanitize(val)

        return result

    def redact_sensitive(self, text: str) -> str:
        """
        Redact sensitive patterns from text.

        Useful for log messages that may contain secrets.
        """
        result = text

        # Common secret patterns
        patterns = [
            (
                r'(?i)(api[_-]?key|token|secret|password|auth)["\'\s:=]+["\']?([^\s"\']+)',
                r"\1=[REDACTED]",
            ),
            (r"(?i)(bearer\s+)([A-Za-z0-9_\-\.]+)", r"\1[REDACTED]"),
            (r"(?i)(basic\s+)([A-Za-z0-9+/=]+)", r"\1[REDACTED]"),
        ]

        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)

        return result


# Global sanitizer instance
_sanitizer: LogSanitizer | None = None


def get_log_sanitizer() -> LogSanitizer:
    """Get or create the global log sanitizer."""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = LogSanitizer()
    return _sanitizer


def sanitize_for_logging(value: Any) -> Any:
    """Convenience function to sanitize any value for logging."""
    return get_log_sanitizer().sanitize(value)


class SanitizingLogFilter(logging.Filter):
    """
    Logging filter that sanitizes log records.

    Usage:
        handler = logging.StreamHandler()
        handler.addFilter(SanitizingLogFilter())
    """

    def __init__(self, sanitizer: LogSanitizer | None = None):
        super().__init__()
        self.sanitizer = sanitizer or get_log_sanitizer()

    def filter(self, record: logging.LogRecord) -> bool:
        # Sanitize the message
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = self.sanitizer.redact_sensitive(record.msg)

        # Sanitize args
        if record.args:
            if isinstance(record.args, dict):
                record.args = self.sanitizer._sanitize_dict(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(self.sanitizer.sanitize(arg) for arg in record.args)

        return True
