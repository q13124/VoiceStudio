"""
Overseer Issue Sanitizer.

Scans and redacts secrets and PII from issue messages and context
before persistence. Prevents credential exposure and supports privacy compliance.
"""

from __future__ import annotations

import re
from typing import Any

# Patterns that indicate secrets (match group or full match is redacted)
_SECRET_PATTERNS = [
    # Bearer / API key style
    (re.compile(r"\bBearer\s+[A-Za-z0-9\-_.~+/]+=*", re.I), "Bearer <REDACTED>"),
    (re.compile(r"\b(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9\-_.~+/]+=*['\"]?", re.I), "api_key=<REDACTED>"),
    (re.compile(r"\b(?:token|auth)\s*[:=]\s*['\"]?[A-Za-z0-9\-_.~+/]+=*['\"]?", re.I), "token=<REDACTED>"),
    (re.compile(r"\b(?:password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]+['\"]?", re.I), "password=<REDACTED>"),
    (re.compile(r"\b(?:secret|credentials)\s*[:=]\s*['\"]?[^\s'\"]+['\"]?", re.I), "secret=<REDACTED>"),
    # Long hex tokens often used as API keys (32+ hex chars)
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "<REDACTED>"),
    # AWS / cloud style
    (re.compile(r"AKIA[0-9A-Z]{16}"), "<REDACTED>"),
    (re.compile(r"\b(?:aws_)?(?:access_?key|secret_?key)\s*[:=]\s*[^\s,}\]]+", re.I), "aws_key=<REDACTED>"),
]

# PII patterns (redact or generalize)
_PII_PATTERNS = [
    # Email
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b"), "<EMAIL>"),
    # IPv4
    (re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"), "<IP>"),
    # Long numeric IDs that might be SSN/credit (optional: only if looks like SSN pattern)
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "<REDACTED>"),
]


def _redact_text(text: str, patterns: list[tuple[re.Pattern, str]]) -> str:
    """Apply redaction patterns to a string. Returns redacted copy."""
    if not text or not isinstance(text, str):
        return text
    out = text
    for pattern, replacement in patterns:
        out = pattern.sub(replacement, out)
    return out


def sanitize_message(message: str) -> str:
    """
    Redact secrets and PII from an issue message.

    Args:
        message: Raw message string.

    Returns:
        Sanitized message safe for logging.
    """
    if not message:
        return message
    out = _redact_text(message, _SECRET_PATTERNS)
    out = _redact_text(out, _PII_PATTERNS)
    return out


def sanitize_value(value: Any) -> Any:
    """
    Recursively sanitize a value (string, dict, list).

    Strings are redacted; dicts/lists are traversed; other types returned as-is.
    """
    if isinstance(value, str):
        return sanitize_message(value)
    if isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_value(item) for item in value]
    return value


def sanitize_context(context: dict[str, Any] | None) -> dict[str, Any]:
    """
    Sanitize a context dict (message, stack, traceback, etc.) in place or copy.

    Args:
        context: Raw context from issue recording.

    Returns:
        New dict with secrets and PII redacted. Keys such as 'traceback',
        'stack', 'error_stack', and string values elsewhere are sanitized.
    """
    if context is None:
        return {}
    return sanitize_value(dict(context))


def scan_for_secrets(text: str) -> bool:
    """
    Quick check whether text appears to contain secret-like content.

    Used to decide whether to run full sanitization or to warn.

    Returns:
        True if any secret pattern matches.
    """
    if not text or not isinstance(text, str):
        return False
    return any(pattern.search(text) for pattern, _ in _SECRET_PATTERNS)
