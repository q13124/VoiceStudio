"""
VoiceStudio Security & Rate Limiting System
Implements security features from the Unified Implementation Map
"""

import time
import hashlib
import hmac
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import ipaddress
import re


@dataclass
class RateLimit:
    """Rate limit configuration"""

    requests_per_minute: int = 100
    clones_per_day_per_user: int = 50
    max_file_size_mb: int = 100
    burst_limit: int = 10  # Allow burst of 10 requests
    window_seconds: int = 60  # 1 minute window


@dataclass
class SecurityConfig:
    """Security configuration"""

    rate_limits: RateLimit = field(default_factory=RateLimit)
    input_validation: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_text_length": 5000,
            "allowed_formats": ["wav", "mp3", "flac"],
            "malware_scan": False,
            "allowed_languages": [
                "en",
                "es",
                "fr",
                "de",
                "it",
                "pt",
                "zh",
                "ja",
                "ru",
                "ar",
            ],
        }
    )
    encryption: Dict[str, bool] = field(
        default_factory=lambda: {"voice_profiles_at_rest": False, "audit_logging": True}
    )
    api_keys: Dict[str, str] = field(default_factory=dict)  # key_id -> secret_hash
    blocked_ips: List[str] = field(default_factory=list)
    allowed_ips: List[str] = field(default_factory=list)


class RateLimiter:
    """Rate limiting implementation"""

    def __init__(self, db_path: str = "voicestudio_rate_limits.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize rate limiting database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    count INTEGER DEFAULT 1,
                    UNIQUE(identifier, endpoint, timestamp)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    clones_count INTEGER DEFAULT 0,
                    requests_count INTEGER DEFAULT 0,
                    UNIQUE(user_id, date)
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rate_limits_timestamp ON rate_limits(timestamp);
                CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier ON rate_limits(identifier);
                CREATE INDEX IF NOT EXISTS idx_daily_usage_date ON daily_usage(date);
            """
            )

    def check_rate_limit(
        self, identifier: str, endpoint: str, limit: int, window_seconds: int = 60
    ) -> Tuple[bool, int, int]:
        """Check if request is within rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)

        with sqlite3.connect(self.db_path) as conn:
            # Count requests in window
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM rate_limits
                WHERE identifier = ? AND endpoint = ? AND timestamp >= ?
            """,
                (identifier, endpoint, window_start),
            )

            current_count = cursor.fetchone()[0]

            if current_count >= limit:
                return False, current_count, limit

            # Record this request
            conn.execute(
                """
                INSERT OR REPLACE INTO rate_limits (identifier, endpoint, timestamp, count)
                VALUES (?, ?, ?, 1)
            """,
                (identifier, endpoint, now),
            )

            return True, current_count + 1, limit

    def check_daily_limit(self, user_id: str, limit: int) -> Tuple[bool, int, int]:
        """Check daily usage limit"""
        today = datetime.now().date()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT clones_count FROM daily_usage
                WHERE user_id = ? AND date = ?
            """,
                (user_id, today),
            )

            row = cursor.fetchone()
            current_count = row[0] if row else 0

            if current_count >= limit:
                return False, current_count, limit

            # Increment count
            conn.execute(
                """
                INSERT OR REPLACE INTO daily_usage (user_id, date, clones_count)
                VALUES (?, ?, ?)
            """,
                (user_id, today, current_count + 1),
            )

            return True, current_count + 1, limit

    def cleanup_old_records(self, days: int = 7):
        """Clean up old rate limit records"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                DELETE FROM rate_limits WHERE timestamp < ?
            """,
                (cutoff,),
            )


class InputValidator:
    """Input validation system"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self._init_patterns()

    def _init_patterns(self):
        """Initialize validation patterns"""
        self.text_patterns = {
            "max_length": self.config.input_validation["max_text_length"],
            "allowed_chars": re.compile(r"^[a-zA-Z0-9\s\.,!?;:\-\'\"()]+$"),
            "suspicious_patterns": [
                re.compile(r"<script", re.IGNORECASE),
                re.compile(r"javascript:", re.IGNORECASE),
                re.compile(r"data:text/html", re.IGNORECASE),
                re.compile(r"vbscript:", re.IGNORECASE),
            ],
        }

        self.file_patterns = {
            "allowed_extensions": set(self.config.input_validation["allowed_formats"]),
            "max_size_mb": self.config.input_validation.get("max_file_size_mb", 100),
            "suspicious_extensions": {".exe", ".bat", ".cmd", ".scr", ".pif", ".com"},
        }

    def validate_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """Validate text input"""
        if not text or not isinstance(text, str):
            return False, "Text is required and must be a string"

        if len(text) > self.text_patterns["max_length"]:
            return (
                False,
                f"Text too long (max {self.text_patterns['max_length']} characters)",
            )

        if not self.text_patterns["allowed_chars"].match(text):
            return False, "Text contains invalid characters"

        # Check for suspicious patterns
        for pattern in self.text_patterns["suspicious_patterns"]:
            if pattern.search(text):
                return False, "Text contains potentially malicious content"

        return True, None

    def validate_language(self, language: str) -> Tuple[bool, Optional[str]]:
        """Validate language code"""
        allowed_languages = self.config.input_validation.get(
            "allowed_languages", ["en"]
        )

        if language not in allowed_languages:
            return False, f"Language '{language}' not supported"

        return True, None

    def validate_file(
        self, filename: str, file_size_bytes: int
    ) -> Tuple[bool, Optional[str]]:
        """Validate file upload"""
        if not filename:
            return False, "Filename is required"

        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext in self.file_patterns["suspicious_extensions"]:
            return False, "File type not allowed"

        if file_ext not in self.file_patterns["allowed_extensions"]:
            return False, f"File type '{file_ext}' not supported"

        # Check file size
        max_size_bytes = self.file_patterns["max_size_mb"] * 1024 * 1024
        if file_size_bytes > max_size_bytes:
            return False, f"File too large (max {self.file_patterns['max_size_mb']}MB)"

        return True, None

    def validate_voice_profile(
        self, profile: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validate voice profile data"""
        if not isinstance(profile, dict):
            return False, "Voice profile must be a dictionary"

        # Check for required fields
        required_fields = ["voice_id"]
        for field in required_fields:
            if field not in profile:
                return False, f"Missing required field: {field}"

        # Validate voice_id format
        voice_id = profile.get("voice_id", "")
        if not isinstance(voice_id, str) or len(voice_id) < 3:
            return False, "Invalid voice_id format"

        # Check for suspicious data
        for key, value in profile.items():
            if isinstance(value, str) and len(value) > 1000:
                return False, f"Field '{key}' too long"

        return True, None


class IPFilter:
    """IP address filtering system"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self._init_ip_ranges()

    def _init_ip_ranges(self):
        """Initialize IP address ranges"""
        self.blocked_ranges = []
        self.allowed_ranges = []

        for ip_str in self.config.blocked_ips:
            try:
                self.blocked_ranges.append(ipaddress.ip_network(ip_str, strict=False))
            except ValueError:
                print(f"Warning: Invalid blocked IP range: {ip_str}")

        for ip_str in self.config.allowed_ips:
            try:
                self.allowed_ranges.append(ipaddress.ip_network(ip_str, strict=False))
            except ValueError:
                print(f"Warning: Invalid allowed IP range: {ip_str}")

    def is_allowed(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check if IP address is allowed"""
        try:
            ip = ipaddress.ip_address(ip_address)
        except ValueError:
            return False, "Invalid IP address format"

        # Check blocked ranges first
        for blocked_range in self.blocked_ranges:
            if ip in blocked_range:
                return False, f"IP {ip_address} is blocked"

        # If allowed ranges are specified, check them
        if self.allowed_ranges:
            for allowed_range in self.allowed_ranges:
                if ip in allowed_range:
                    return True, None
            return False, f"IP {ip_address} not in allowed ranges"

        # If no allowed ranges specified, allow all non-blocked IPs
        return True, None


class APIKeyManager:
    """API key management system"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self._init_keys()

    def _init_keys(self):
        """Initialize API keys"""
        # Generate default API key if none exist
        if not self.config.api_keys:
            default_key = self._generate_key()
            default_secret = self._generate_secret()
            self.config.api_keys[default_key] = self._hash_secret(default_secret)
            print(f"Generated default API key: {default_key}")
            print(f"Generated default secret: {default_secret}")

    def _generate_key(self) -> str:
        """Generate API key"""
        import secrets

        return f"vs_{secrets.token_urlsafe(16)}"

    def _generate_secret(self) -> str:
        """Generate API secret"""
        import secrets

        return secrets.token_urlsafe(32)

    def _hash_secret(self, secret: str) -> str:
        """Hash API secret"""
        return hashlib.sha256(secret.encode()).hexdigest()

    def validate_key(self, key: str, secret: str) -> Tuple[bool, Optional[str]]:
        """Validate API key and secret"""
        if key not in self.config.api_keys:
            return False, "Invalid API key"

        expected_hash = self.config.api_keys[key]
        actual_hash = self._hash_secret(secret)

        if not hmac.compare_digest(expected_hash, actual_hash):
            return False, "Invalid API secret"

        return True, None

    def create_key(self, name: str) -> Tuple[str, str]:
        """Create new API key"""
        key = self._generate_key()
        secret = self._generate_secret()
        self.config.api_keys[key] = self._hash_secret(secret)
        return key, secret

    def revoke_key(self, key: str) -> bool:
        """Revoke API key"""
        if key in self.config.api_keys:
            del self.config.api_keys[key]
            return True
        return False


class AuditLogger:
    """Audit logging system"""

    def __init__(self, db_path: str = "voicestudio_audit.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize audit database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    ip_address TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    success BOOLEAN NOT NULL,
                    details TEXT,
                    error_message TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
                CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
            """
            )

    def log_event(
        self,
        user_id: Optional[str],
        ip_address: str,
        action: str,
        resource: Optional[str],
        success: bool,
        details: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Log audit event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_log (user_id, ip_address, action, resource, success, details, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    ip_address,
                    action,
                    resource,
                    success,
                    details,
                    error_message,
                ),
            )

    def get_events(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Get audit events"""
        cutoff = datetime.now() - timedelta(hours=hours)

        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM audit_log WHERE timestamp >= ?"
            params = [cutoff]

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if action:
                query += " AND action = ?"
                params.append(action)

            query += " ORDER BY timestamp DESC"

            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]

            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class SecurityManager:
    """Main security manager"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rate_limiter = RateLimiter()
        self.input_validator = InputValidator(config)
        self.ip_filter = IPFilter(config)
        self.api_key_manager = APIKeyManager(config)
        self.audit_logger = AuditLogger()

    def check_request(
        self,
        ip_address: str,
        user_id: Optional[str],
        endpoint: str,
        api_key: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Comprehensive request security check"""

        # Check IP filtering
        ip_allowed, ip_error = self.ip_filter.is_allowed(ip_address)
        if not ip_allowed:
            self.audit_logger.log_event(
                user_id,
                ip_address,
                "ip_blocked",
                endpoint,
                False,
                error_message=ip_error,
            )
            return False, ip_error

        # Check API key if required
        if api_key:
            key_parts = api_key.split(":")
            if len(key_parts) != 2:
                self.audit_logger.log_event(
                    user_id,
                    ip_address,
                    "invalid_api_key",
                    endpoint,
                    False,
                    error_message="Invalid API key format",
                )
                return False, "Invalid API key format"

            key, secret = key_parts
            key_valid, key_error = self.api_key_manager.validate_key(key, secret)
            if not key_valid:
                self.audit_logger.log_event(
                    user_id,
                    ip_address,
                    "invalid_api_key",
                    endpoint,
                    False,
                    error_message=key_error,
                )
                return False, key_error

        # Check rate limits
        identifier = user_id or ip_address
        rate_ok, current_count, limit = self.rate_limiter.check_rate_limit(
            identifier, endpoint, self.config.rate_limits.requests_per_minute
        )

        if not rate_ok:
            self.audit_logger.log_event(
                user_id,
                ip_address,
                "rate_limit_exceeded",
                endpoint,
                False,
                error_message=f"Rate limit exceeded: {current_count}/{limit}",
            )
            return (
                False,
                f"Rate limit exceeded: {current_count}/{limit} requests per minute",
            )

        # Log successful check
        self.audit_logger.log_event(
            user_id, ip_address, "request_allowed", endpoint, True
        )

        return True, None

    def check_daily_limit(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check daily usage limit"""
        daily_ok, current_count, limit = self.rate_limiter.check_daily_limit(
            user_id, self.config.rate_limits.clones_per_day_per_user
        )

        if not daily_ok:
            return (
                False,
                f"Daily limit exceeded: {current_count}/{limit} clones per day",
            )

        return True, None

    def validate_tts_request(
        self, text: str, language: str, voice_profile: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validate TTS request"""

        # Validate text
        text_valid, text_error = self.input_validator.validate_text(text)
        if not text_valid:
            return False, text_error

        # Validate language
        lang_valid, lang_error = self.input_validator.validate_language(language)
        if not lang_valid:
            return False, lang_error

        # Validate voice profile
        profile_valid, profile_error = self.input_validator.validate_voice_profile(
            voice_profile
        )
        if not profile_valid:
            return False, profile_error

        return True, None

    def cleanup(self):
        """Cleanup old records"""
        self.rate_limiter.cleanup_old_records()


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager

    if _security_manager is None:
        from config.config_loader import get_security_config

        security_config = get_security_config()
        _security_manager = SecurityManager(security_config)

    return _security_manager


def check_request_security(
    ip_address: str,
    user_id: Optional[str],
    endpoint: str,
    api_key: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Check request security"""
    return get_security_manager().check_request(ip_address, user_id, endpoint, api_key)


def validate_tts_request(
    text: str, language: str, voice_profile: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """Validate TTS request"""
    return get_security_manager().validate_tts_request(text, language, voice_profile)


def check_daily_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    """Check daily usage limit"""
    return get_security_manager().check_daily_limit(user_id)


if __name__ == "__main__":
    # Test security system
    config = SecurityConfig()
    security = SecurityManager(config)

    # Test rate limiting
    ip = "192.168.1.1"
    user_id = "test_user"
    endpoint = "/tts"

    for i in range(5):
        allowed, error = security.check_request(ip, user_id, endpoint)
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'} - {error}")

    # Test input validation
    text_valid, text_error = security.validate_tts_request(
        "Hello world", "en", {"voice_id": "test"}
    )
    print(f"Text validation: {'Valid' if text_valid else 'Invalid'} - {text_error}")

    # Test daily limit
    daily_ok, daily_error = security.check_daily_limit(user_id)
    print(f"Daily limit: {'OK' if daily_ok else 'Exceeded'} - {daily_error}")
