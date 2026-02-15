"""
Security Audit and Hardening Module

Comprehensive security utilities for:
- Input validation and sanitization
- Output sanitization
- Secure file operations
- Path traversal prevention
- Security logging
- Vulnerability scanning
"""

from __future__ import annotations

import logging
import os
import re
import secrets
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try importing cryptography for encryption
try:
    import base64

    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    logger.warning("cryptography not available. Encryption features will be limited.")


class SecurityAuditor:
    """
    Security auditor for vulnerability scanning and security checks.
    """

    def __init__(self):
        """Initialize security auditor."""
        self.vulnerabilities: list[dict[str, Any]] = []
        self.security_log: list[dict[str, Any]] = []

    def audit_file_operations(
        self, file_path: str, base_path: str
    ) -> tuple[bool, str | None]:
        """
        Audit file operation for path traversal vulnerabilities.

        Args:
            file_path: File path to check
            base_path: Base directory path

        Returns:
            (is_safe, error_message)
        """
        try:
            # Normalize paths
            base = Path(base_path).resolve()
            path = Path(file_path).resolve()

            # Check for path traversal
            try:
                path.relative_to(base)
            except ValueError:
                return False, f"Path traversal detected: {file_path}"

            # Check for dangerous patterns
            path_str = str(path)
            dangerous_patterns = [
                "..",
                "~",
                "//",
                "\\\\",
            ]

            # Check resolved path (after normalization)
            if any(pattern in path_str for pattern in dangerous_patterns):
                # Check if it's actually outside base after resolution
                if not str(path).startswith(str(base)):
                    return False, f"Path outside base directory: {file_path}"

            return True, None

        except Exception as e:
            logger.error(f"Error auditing file operation: {e}")
            return False, f"Error validating path: {e!s}"

    def audit_input(
        self, value: Any, field_name: str, max_length: int | None = None
    ) -> tuple[bool, str | None]:
        """
        Audit input value for security issues.

        Args:
            value: Input value to audit
            field_name: Field name for context
            max_length: Maximum allowed length

        Returns:
            (is_safe, error_message)
        """
        if value is None:
            return True, None

        # Convert to string for checking
        str_value = str(value)

        # Check length
        if max_length and len(str_value) > max_length:
            return False, f"{field_name} exceeds maximum length of {max_length}"

        # Check for SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|/\*|\*/|;|')",
        ]
        for pattern in sql_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                return False, f"{field_name} contains potential SQL injection pattern"

        # Check for command injection patterns
        command_patterns = [
            r"[;&|`$(){}]",
            r"(\b(cmd|sh|bash|powershell|python|perl)\b)",
        ]
        for pattern in command_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                return (
                    False,
                    f"{field_name} contains potential command injection pattern",
                )

        # Check for XSS patterns
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onerror=",
            r"onload=",
        ]
        for pattern in xss_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                return False, f"{field_name} contains potential XSS pattern"

        return True, None

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """
        Log security event.

        Args:
            event_type: Type of event (e.g., "path_traversal", "sql_injection")
            severity: Severity level (info, warning, error, critical)
            message: Event message
            details: Additional details
        """
        import datetime

        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": event_type,
            "severity": severity,
            "message": message,
            "details": details or {},
        }

        self.security_log.append(event)

        # Log based on severity
        if severity == "critical":
            logger.critical(f"SECURITY: {message} | Type: {event_type}")
        elif severity == "error":
            logger.error(f"SECURITY: {message} | Type: {event_type}")
        elif severity == "warning":
            logger.warning(f"SECURITY: {message} | Type: {event_type}")
        else:
            logger.info(f"SECURITY: {message} | Type: {event_type}")

        # Keep only recent events (last 1000)
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]


class InputValidator:
    """Input validation utilities."""

    @staticmethod
    def sanitize_path(file_path: str, base_path: str) -> str | None:
        """
        Sanitize file path to prevent path traversal.

        Args:
            file_path: File path to sanitize
            base_path: Base directory path

        Returns:
            Sanitized path or None if invalid
        """
        try:
            # Remove any path traversal attempts
            normalized = os.path.normpath(file_path)

            # Remove leading separators
            normalized = normalized.lstrip(os.sep).lstrip(os.altsep)

            # Join with base path
            base = Path(base_path).resolve()
            full_path = base / normalized

            # Resolve to absolute path
            resolved = full_path.resolve()

            # Verify it's still within base
            try:
                resolved.relative_to(base)
                return str(resolved)
            except ValueError:
                return None

        except Exception as e:
            logger.error(f"Error sanitizing path: {e}")
            return None

    @staticmethod
    def sanitize_string(value: str, max_length: int | None = None) -> str:
        """
        Sanitize string input.

        Args:
            value: String to sanitize
            max_length: Maximum length

        Returns:
            Sanitized string
        """
        # Remove null bytes
        sanitized = value.replace("\x00", "")

        # Truncate if needed
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate filename for security.

        Args:
            filename: Filename to validate

        Returns:
            True if valid, False otherwise
        """
        # Check for invalid characters
        invalid_chars = set('<>:"/\\|?*')
        if any(c in invalid_chars for c in filename):
            return False

        # Check for reserved names (Windows)
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        if filename.upper() in reserved_names:
            return False

        # Check length
        return not len(filename) > 255


class OutputSanitizer:
    """Output sanitization utilities."""

    @staticmethod
    def sanitize_for_json(value: Any) -> Any:
        """
        Sanitize value for JSON output.

        Args:
            value: Value to sanitize

        Returns:
            Sanitized value
        """
        if isinstance(value, str):
            # Remove control characters
            sanitized = "".join(c for c in value if ord(c) >= 32 or c in "\n\r\t")
            return sanitized
        elif isinstance(value, dict):
            return {k: OutputSanitizer.sanitize_for_json(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [OutputSanitizer.sanitize_for_json(item) for item in value]
        else:
            return value

    @staticmethod
    def sanitize_error_message(message: str, include_details: bool = False) -> str:
        """
        Sanitize error message for user display.

        Args:
            message: Error message
            include_details: Whether to include detailed error info

        Returns:
            Sanitized error message
        """
        # Remove sensitive information patterns
        patterns = [
            (r"password['\"]?\s*[:=]\s*['\"]?[^'\"]+", "password=***"),
            (r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[^'\"]+", "api_key=***"),
            (r"token['\"]?\s*[:=]\s*['\"]?[^'\"]+", "token=***"),
            (r"secret['\"]?\s*[:=]\s*['\"]?[^'\"]+", "secret=***"),
        ]

        sanitized = message
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Remove file paths if not including details
        if not include_details:
            sanitized = re.sub(r"[A-Z]:\\[^\s]+", "[PATH]", sanitized)
            sanitized = re.sub(r"/[^\s]+", "[PATH]", sanitized)

        return sanitized


class SecureFileOperations:
    """Secure file operation utilities."""

    def __init__(self, base_path: str):
        """
        Initialize secure file operations.

        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def safe_open(self, file_path: str, mode: str = "r") -> Any | None:
        """
        Safely open a file with path validation.

        Args:
            file_path: Relative file path
            mode: File open mode

        Returns:
            File handle or None if invalid
        """
        # Sanitize path
        sanitized = InputValidator.sanitize_path(file_path, str(self.base_path))
        if not sanitized:
            logger.warning(f"Invalid file path: {file_path}")
            return None

        try:
            path = Path(sanitized)
            if not path.exists() and "r" in mode:
                return None

            return open(path, mode)
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return None

    def safe_write(self, file_path: str, content: bytes) -> bool:
        """
        Safely write to a file.

        Args:
            file_path: Relative file path
            content: Content to write

        Returns:
            True if successful, False otherwise
        """
        # Sanitize path
        sanitized = InputValidator.sanitize_path(file_path, str(self.base_path))
        if not sanitized:
            logger.warning(f"Invalid file path: {file_path}")
            return False

        try:
            path = Path(sanitized)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False


class SecureStorage:
    """Secure storage for sensitive data (API keys, tokens, etc.)."""

    def __init__(self, master_key: bytes | None = None):
        """
        Initialize secure storage.

        Args:
            master_key: Master encryption key (generated if None)
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography library required for secure storage")

        if master_key is None:
            # Generate master key from environment or create new
            key_str = os.getenv("VOICESTUDIO_MASTER_KEY")
            if key_str:
                master_key = key_str.encode()
            else:
                # Generate random key (should be stored securely in production)
                master_key = secrets.token_bytes(32)

        # Derive encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"voicestudio_salt",  # Should be unique per installation
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt sensitive data.

        Args:
            plaintext: Plain text to encrypt

        Returns:
            Encrypted string (base64)
        """
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt sensitive data.

        Args:
            ciphertext: Encrypted string

        Returns:
            Decrypted plain text
        """
        return self.cipher.decrypt(ciphertext.encode()).decode()


# Global security auditor instance
_security_auditor: SecurityAuditor | None = None


def get_security_auditor() -> SecurityAuditor:
    """Get global security auditor instance."""
    global _security_auditor
    if _security_auditor is None:
        _security_auditor = SecurityAuditor()
    return _security_auditor


# Export
__all__ = [
    "InputValidator",
    "OutputSanitizer",
    "SecureFileOperations",
    "SecureStorage",
    "SecurityAuditor",
    "get_security_auditor",
]
