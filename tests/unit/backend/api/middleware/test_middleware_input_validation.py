"""
Unit tests for the Input Validation Middleware.

Tests cover:
- Path traversal detection
- Command injection detection
- XSS detection
- SQL injection detection
- String length validation
- Query parameter validation
- Path parameter validation
"""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from backend.api.middleware.input_validation import (
    INJECTION_PATTERNS,
    MAX_STRING_LENGTH,
    PATH_TRAVERSAL_PATTERNS,
    SQL_INJECTION_PATTERNS,
    InputValidationMiddleware,
)


class TestPathTraversalDetection:
    """Tests for path traversal detection."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return InputValidationMiddleware(MagicMock())

    def test_detects_unix_path_traversal(self, middleware):
        """Test detection of Unix path traversal."""
        assert middleware._check_path_traversal("../etc/passwd") is True
        assert middleware._check_path_traversal("../../secret") is True

    def test_detects_windows_path_traversal(self, middleware):
        """Test detection of Windows path traversal."""
        assert middleware._check_path_traversal("..\\windows\\system32") is True
        assert middleware._check_path_traversal("..\\..\\config") is True

    def test_detects_double_dot(self, middleware):
        """Test detection of double dot sequences."""
        assert middleware._check_path_traversal("..") is True

    def test_detects_double_slash(self, middleware):
        """Test detection of double slashes."""
        assert middleware._check_path_traversal("//etc/passwd") is True

    def test_detects_unc_path(self, middleware):
        """Test detection of Windows UNC paths."""
        assert middleware._check_path_traversal("\\\\server\\share") is True

    def test_allows_safe_paths(self, middleware):
        """Test that safe paths are allowed."""
        assert middleware._check_path_traversal("/api/voice") is False
        assert middleware._check_path_traversal("voice_profile") is False
        assert middleware._check_path_traversal("my-project.wav") is False


class TestInjectionDetection:
    """Tests for command injection detection."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return InputValidationMiddleware(MagicMock())

    def test_detects_command_chaining(self, middleware):
        """Test detection of command chaining characters."""
        assert middleware._check_injection("test; rm -rf /") is True
        assert middleware._check_injection("test && malicious") is True
        assert middleware._check_injection("test | cat /etc/passwd") is True

    def test_detects_shell_command_substitution(self, middleware):
        """Test detection of shell command substitution."""
        assert middleware._check_injection("$(whoami)") is True
        assert middleware._check_injection("`id`") is True

    def test_detects_xss_script_tags(self, middleware):
        """Test detection of XSS script tags."""
        assert middleware._check_injection("<script>alert(1)</script>") is True
        assert middleware._check_injection("<SCRIPT>malicious</SCRIPT>") is True

    def test_detects_javascript_protocol(self, middleware):
        """Test detection of JavaScript protocol."""
        assert middleware._check_injection("javascript:alert(1)") is True

    def test_detects_event_handlers(self, middleware):
        """Test detection of event handlers."""
        assert middleware._check_injection("onerror=alert(1)") is True
        assert middleware._check_injection("onclick=malicious()") is True

    def test_detects_data_uri(self, middleware):
        """Test detection of data URIs with HTML."""
        assert middleware._check_injection("data:text/html,<script>") is True

    def test_allows_safe_input(self, middleware):
        """Test that safe input is allowed."""
        assert middleware._check_injection("Hello World") is False
        assert middleware._check_injection("voice_profile_001") is False
        assert middleware._check_injection("This is a normal sentence.") is False


class TestSqlInjectionDetection:
    """Tests for SQL injection detection."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return InputValidationMiddleware(MagicMock(), strict_mode=True)

    def test_detects_sql_keywords(self, middleware):
        """Test detection of SQL keywords."""
        assert middleware._check_sql_injection("SELECT * FROM users") is True
        assert middleware._check_sql_injection("DROP TABLE data") is True
        assert middleware._check_sql_injection("INSERT INTO logs") is True

    def test_detects_sql_comments(self, middleware):
        """Test detection of SQL comments."""
        assert middleware._check_sql_injection("admin'--") is True
        assert middleware._check_sql_injection("password'#") is True
        assert middleware._check_sql_injection("/* comment */") is True

    def test_detects_union_based(self, middleware):
        """Test detection of UNION-based injection."""
        assert middleware._check_sql_injection("UNION SELECT password") is True

    def test_allows_safe_input(self, middleware):
        """Test that safe input is allowed."""
        assert middleware._check_sql_injection("normal text") is False
        assert middleware._check_sql_injection("user@example.com") is False


class TestStringLengthValidation:
    """Tests for string length validation."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return InputValidationMiddleware(MagicMock())

    def test_allows_short_strings(self, middleware):
        """Test that short strings are allowed."""
        assert middleware._check_length("short") is False
        assert middleware._check_length("a" * 100) is False

    def test_blocks_long_strings(self, middleware):
        """Test that very long strings are blocked."""
        long_string = "a" * (MAX_STRING_LENGTH + 1)
        assert middleware._check_length(long_string) is True

    def test_custom_max_length(self, middleware):
        """Test custom max length."""
        assert middleware._check_length("123456", max_length=5) is True
        assert middleware._check_length("12345", max_length=5) is False


class TestValidateString:
    """Tests for full string validation."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return InputValidationMiddleware(MagicMock())

    def test_raises_on_path_traversal(self, middleware):
        """Test that path traversal raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            middleware._validate_string("../../../etc/passwd", "path")

        assert exc_info.value.status_code == 400
        assert "Path traversal" in exc_info.value.detail

    def test_raises_on_injection(self, middleware):
        """Test that injection raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            middleware._validate_string("<script>alert(1)</script>", "input")

        assert exc_info.value.status_code == 400
        assert "malicious content" in exc_info.value.detail

    def test_raises_on_long_string(self, middleware):
        """Test that long strings raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            middleware._validate_string("a" * (MAX_STRING_LENGTH + 1), "field")

        assert exc_info.value.status_code == 400
        assert "maximum length" in exc_info.value.detail

    def test_allows_safe_strings(self, middleware):
        """Test that safe strings pass validation."""
        # Should not raise
        middleware._validate_string("Hello, World!", "greeting")
        middleware._validate_string("voice_profile_001", "profile_id")


class TestValidateDict:
    """Tests for dictionary validation."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return InputValidationMiddleware(MagicMock())

    def test_validates_nested_strings(self, middleware):
        """Test validation of nested strings."""
        with pytest.raises(HTTPException):
            middleware._validate_dict({
                "name": "safe",
                "nested": {
                    "evil": "<script>alert(1)</script>"
                }
            })

    def test_validates_list_items(self, middleware):
        """Test validation of list items."""
        with pytest.raises(HTTPException):
            middleware._validate_dict({
                "items": ["safe", "../traversal", "normal"]
            })

    def test_allows_safe_dicts(self, middleware):
        """Test that safe dictionaries pass validation."""
        # Should not raise
        middleware._validate_dict({
            "name": "John",
            "tags": ["audio", "voice"],
            "config": {"quality": "high"}
        })


class TestMiddlewareIntegration:
    """Integration tests for the middleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        mock_app = MagicMock()
        return InputValidationMiddleware(mock_app, enabled=True)

    def test_skips_health_endpoints(self, middleware):
        """Test that health endpoints are skipped."""
        assert "/health" in middleware.skip_paths
        assert "/api/health" in middleware.skip_paths

    def test_skips_docs_endpoints(self, middleware):
        """Test that documentation endpoints are skipped."""
        assert "/docs" in middleware.skip_paths
        assert "/openapi.json" in middleware.skip_paths

    def test_disabled_middleware_skips_validation(self):
        """Test that disabled middleware skips validation."""
        middleware = InputValidationMiddleware(MagicMock(), enabled=False)
        assert middleware.enabled is False

    def test_validates_query_params_logs_warning(self, middleware, caplog):
        """Test query parameter validation logs warnings for malicious input."""
        import logging

        mock_request = MagicMock()
        mock_request.url.path = "/api/voice"
        mock_request.query_params = {"path": "../../../etc/passwd"}
        mock_request.path_params = {}
        mock_request.method = "GET"

        # The middleware catches exceptions and logs warnings
        with caplog.at_level(logging.WARNING):
            middleware._validate_query_params(mock_request)

        # Verify warning was logged for path traversal attempt
        assert "Path traversal" in caplog.text


class TestStrictMode:
    """Tests for strict mode."""

    def test_strict_mode_enables_sql_check(self):
        """Test that strict mode enables SQL injection checking."""
        middleware = InputValidationMiddleware(MagicMock(), strict_mode=True)

        with pytest.raises(HTTPException):
            middleware._validate_string("SELECT * FROM users", "query")

    def test_non_strict_allows_sql_in_regular_fields(self):
        """Test that non-strict mode allows SQL-like text in regular fields."""
        middleware = InputValidationMiddleware(MagicMock(), strict_mode=False)

        # Should not raise for regular fields
        middleware._validate_string("SELECT sounds great!", "comment")

    def test_non_strict_checks_sql_sensitive_fields(self):
        """Test that non-strict mode still checks SQL in sensitive fields."""
        middleware = InputValidationMiddleware(MagicMock(), strict_mode=False)

        with pytest.raises(HTTPException):
            middleware._validate_string("SELECT * FROM users", "query")


class TestModuleExports:
    """Tests for module exports."""

    def test_patterns_exported(self):
        """Test that patterns are exported."""
        assert len(PATH_TRAVERSAL_PATTERNS) > 0
        assert len(INJECTION_PATTERNS) > 0
        assert len(SQL_INJECTION_PATTERNS) > 0

    def test_max_length_exported(self):
        """Test that max length constant is exported."""
        assert MAX_STRING_LENGTH == 10000
