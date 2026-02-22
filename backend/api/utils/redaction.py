"""
PII and Secret Redaction Helper
Redacts PII and secrets from logs and test data.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Common PII patterns
PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),  # SSN
    (r"\b\d{3}\.\d{2}\.\d{4}\b", "[SSN]"),  # SSN with dots
    (r"\b\d{16}\b", "[CARD]"),  # Credit card
    (
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "[CARD]",
    ),  # Credit card with spaces/dashes
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),  # Email
    (r"\b\d{3}-\d{3}-\d{4}\b", "[PHONE]"),  # Phone
    (r"\b\(\d{3}\)\s?\d{3}-\d{4}\b", "[PHONE]"),  # Phone with parentheses
]

# Common secret patterns
SECRET_PATTERNS: list[tuple[str, str, int]] = [
    (
        r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'password["\']?\s*[:=]\s*["\']?[REDACTED]',
        0,
    ),
    (
        r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'api[_-]?key["\']?\s*[:=]\s*["\']?[REDACTED]',
        0,
    ),
    (
        r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'secret["\']?\s*[:=]\s*["\']?[REDACTED]',
        0,
    ),
    (
        r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'token["\']?\s*[:=]\s*["\']?[REDACTED]',
        0,
    ),
    (
        r'authorization["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'authorization["\']?\s*[:=]\s*["\']?[REDACTED]',
        0,
    ),
    (r"bearer\s+([A-Za-z0-9._-]+)", r"bearer [REDACTED]", re.IGNORECASE),
    (
        r'aws[_-]?access[_-]?key[_-]?id["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'aws_access_key_id["\']?\s*[:=]\s*["\']?[REDACTED]',
        re.IGNORECASE,
    ),
    (
        r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'aws_secret_access_key["\']?\s*[:=]\s*["\']?[REDACTED]',
        re.IGNORECASE,
    ),
]


class Redactor:
    """Redacts PII and secrets from text and data structures."""

    def __init__(self, redact_pii: bool = True, redact_secrets: bool = True):
        """
        Initialize redactor.

        Args:
            redact_pii: Whether to redact PII
            redact_secrets: Whether to redact secrets
        """
        self.redact_pii = redact_pii
        self.redact_secrets = redact_secrets

    def redact_text(self, text: str) -> str:
        """
        Redact PII and secrets from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        if not isinstance(text, str):
            return text

        result = text

        # Redact PII
        if self.redact_pii:
            for pattern, replacement in PII_PATTERNS:
                result = re.sub(pattern, replacement, result)

        # Redact secrets
        if self.redact_secrets:
            for pat, repl, flags in SECRET_PATTERNS:
                result = re.sub(pat, repl, result, flags=flags)

        return result

    def redact_dict(
        self, data: dict[str, Any], keys_to_redact: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Redact PII and secrets from dictionary.

        Args:
            data: Dictionary to redact
            keys_to_redact: Optional list of keys to always redact

        Returns:
            Redacted dictionary
        """
        if not isinstance(data, dict):
            return data

        default_keys = [
            "password",
            "api_key",
            "secret",
            "token",
            "authorization",
            "access_key",
            "secret_key",
        ]
        keys_to_redact = keys_to_redact or []
        keys_to_redact = list(set(default_keys + keys_to_redact))

        result: dict[str, Any] = {}
        for key, value in data.items():
            # Always redact specific keys
            if any(redact_key.lower() in key.lower() for redact_key in keys_to_redact):
                result[key] = "[REDACTED]"
            elif isinstance(value, str):
                result[key] = self.redact_text(value)
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value, keys_to_redact)
            elif isinstance(value, list):
                result[key] = [
                    (
                        self.redact_dict(item, keys_to_redact)
                        if isinstance(item, dict)
                        else self.redact_text(item) if isinstance(item, str) else item
                    )
                    for item in value
                ]
            else:
                result[key] = value

        return result

    def redact(
        self,
        data: str | dict[str, Any] | list[Any],
        keys_to_redact: list[str] | None = None,
    ) -> str | dict[str, Any] | list[Any]:
        """
        Redact PII and secrets from data.

        Args:
            data: Data to redact (string, dict, or list)
            keys_to_redact: Optional list of keys to always redact

        Returns:
            Redacted data
        """
        if isinstance(data, str):
            return self.redact_text(data)
        elif isinstance(data, dict):
            return self.redact_dict(data, keys_to_redact)
        elif isinstance(data, list):
            return [self.redact(item, keys_to_redact) for item in data]
        else:
            return data


# Global redactor instance
_redactor = Redactor()


def redact(
    data: str | dict[str, Any] | list[Any],
    keys_to_redact: list[str] | None = None,
    redact_pii: bool = True,
    redact_secrets: bool = True,
) -> str | dict[str, Any] | list[Any]:
    """
    Redact PII and secrets from data.

    Args:
        data: Data to redact
        keys_to_redact: Optional list of keys to always redact
        redact_pii: Whether to redact PII
        redact_secrets: Whether to redact secrets

    Returns:
        Redacted data
    """
    redactor = Redactor(redact_pii=redact_pii, redact_secrets=redact_secrets)
    return redactor.redact(data, keys_to_redact)
