"""
Tests for request signing middleware.

Tests HMAC-based request signature verification for IPC security.
"""

import base64
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.middleware.request_signing import (
    MAX_TIMESTAMP_AGE_SECONDS,
    SIGNATURE_HEADER,
    TIMESTAMP_HEADER,
    VERSION_HEADER,
    RequestSigningMiddleware,
    compute_signature,
    get_secret_key,
    is_signing_enabled,
    validate_timestamp,
    verify_signature,
)

# Test secret key (32 bytes, Base64 encoded)
TEST_SECRET_B64 = base64.b64encode(b"test_secret_key_32_bytes_long!!").decode()
TEST_SECRET = base64.b64decode(TEST_SECRET_B64)


class TestComputeSignature:
    """Tests for compute_signature function."""

    def test_basic_signature(self):
        """Compute signature for basic request."""
        signature = compute_signature(
            TEST_SECRET,
            "GET",
            "/api/v1/test",
            "2026-02-05T12:00:00Z",
            "",
        )

        assert signature is not None
        assert len(signature) > 0
        # Base64 encoded SHA-256 should be 44 characters
        assert len(signature) == 44

    def test_signature_with_body(self):
        """Compute signature for request with body."""
        signature = compute_signature(
            TEST_SECRET,
            "POST",
            "/api/v1/data",
            "2026-02-05T12:00:00Z",
            '{"key": "value"}',
        )

        assert signature is not None
        assert len(signature) == 44

    def test_different_methods_different_signatures(self):
        """Different HTTP methods produce different signatures."""
        sig_get = compute_signature(TEST_SECRET, "GET", "/path", "ts", "")
        sig_post = compute_signature(TEST_SECRET, "POST", "/path", "ts", "")

        assert sig_get != sig_post

    def test_different_paths_different_signatures(self):
        """Different paths produce different signatures."""
        sig1 = compute_signature(TEST_SECRET, "GET", "/path1", "ts", "")
        sig2 = compute_signature(TEST_SECRET, "GET", "/path2", "ts", "")

        assert sig1 != sig2

    def test_different_timestamps_different_signatures(self):
        """Different timestamps produce different signatures."""
        sig1 = compute_signature(TEST_SECRET, "GET", "/path", "ts1", "")
        sig2 = compute_signature(TEST_SECRET, "GET", "/path", "ts2", "")

        assert sig1 != sig2

    def test_different_bodies_different_signatures(self):
        """Different bodies produce different signatures."""
        sig1 = compute_signature(TEST_SECRET, "POST", "/path", "ts", '{"a": 1}')
        sig2 = compute_signature(TEST_SECRET, "POST", "/path", "ts", '{"a": 2}')

        assert sig1 != sig2

    def test_different_keys_different_signatures(self):
        """Different secret keys produce different signatures."""
        key1 = b"key1_32_bytes_long!!!!!!!!!!!!!!!"
        key2 = b"key2_32_bytes_long!!!!!!!!!!!!!!!"

        sig1 = compute_signature(key1, "GET", "/path", "ts", "")
        sig2 = compute_signature(key2, "GET", "/path", "ts", "")

        assert sig1 != sig2


class TestVerifySignature:
    """Tests for verify_signature function."""

    def test_valid_signature(self):
        """Verify valid signature."""
        signature = compute_signature(
            TEST_SECRET,
            "POST",
            "/api/v1/test",
            "2026-02-05T12:00:00Z",
            '{"data": "test"}',
        )

        result = verify_signature(
            TEST_SECRET,
            signature,
            "POST",
            "/api/v1/test",
            "2026-02-05T12:00:00Z",
            '{"data": "test"}',
        )

        assert result is True

    def test_invalid_signature(self):
        """Reject invalid signature."""
        result = verify_signature(
            TEST_SECRET,
            "invalid_signature",
            "GET",
            "/path",
            "ts",
            "",
        )

        assert result is False

    def test_tampered_body(self):
        """Reject signature with tampered body."""
        signature = compute_signature(
            TEST_SECRET,
            "POST",
            "/path",
            "ts",
            '{"original": "data"}',
        )

        result = verify_signature(
            TEST_SECRET,
            signature,
            "POST",
            "/path",
            "ts",
            '{"tampered": "data"}',
        )

        assert result is False

    def test_tampered_method(self):
        """Reject signature with changed method."""
        signature = compute_signature(
            TEST_SECRET,
            "GET",
            "/path",
            "ts",
            "",
        )

        result = verify_signature(
            TEST_SECRET,
            signature,
            "POST",  # Changed method
            "/path",
            "ts",
            "",
        )

        assert result is False

    def test_wrong_key(self):
        """Reject signature verified with wrong key."""
        key1 = b"key1_32_bytes_long!!!!!!!!!!!!!!!"
        key2 = b"key2_32_bytes_long!!!!!!!!!!!!!!!"

        signature = compute_signature(key1, "GET", "/path", "ts", "")

        result = verify_signature(key2, signature, "GET", "/path", "ts", "")

        assert result is False


class TestValidateTimestamp:
    """Tests for validate_timestamp function."""

    def test_valid_recent_timestamp(self):
        """Accept recent timestamp."""
        now = datetime.now(timezone.utc)
        timestamp = now.isoformat()

        assert validate_timestamp(timestamp) is True

    def test_valid_timestamp_with_z_suffix(self):
        """Accept timestamp with Z suffix."""
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        assert validate_timestamp(timestamp) is True

    def test_expired_timestamp(self):
        """Reject expired timestamp."""
        old = datetime.now(timezone.utc) - timedelta(seconds=MAX_TIMESTAMP_AGE_SECONDS + 60)
        timestamp = old.isoformat()

        assert validate_timestamp(timestamp) is False

    def test_future_timestamp_within_window(self):
        """Accept timestamp slightly in the future (clock skew)."""
        future = datetime.now(timezone.utc) + timedelta(seconds=30)
        timestamp = future.isoformat()

        assert validate_timestamp(timestamp) is True

    def test_far_future_timestamp(self):
        """Reject timestamp too far in the future."""
        future = datetime.now(timezone.utc) + timedelta(seconds=MAX_TIMESTAMP_AGE_SECONDS + 60)
        timestamp = future.isoformat()

        assert validate_timestamp(timestamp) is False

    def test_invalid_timestamp_format(self):
        """Reject invalid timestamp format."""
        assert validate_timestamp("not-a-timestamp") is False
        assert validate_timestamp("") is False
        assert validate_timestamp("12345") is False

    def test_custom_max_age(self):
        """Use custom max age."""
        old = datetime.now(timezone.utc) - timedelta(seconds=120)
        timestamp = old.isoformat()

        # Should fail with default (5 min is plenty)
        assert validate_timestamp(timestamp) is True

        # Should fail with very short max age
        assert validate_timestamp(timestamp, max_age_seconds=60) is False


class TestGetSecretKey:
    """Tests for get_secret_key function."""

    def test_returns_none_when_not_set(self):
        """Return None when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_secret_key() is None

    def test_returns_decoded_key(self):
        """Return decoded key from env var."""
        with patch.dict(os.environ, {"VOICESTUDIO_IPC_SECRET": TEST_SECRET_B64}):
            key = get_secret_key()
            assert key == TEST_SECRET

    def test_returns_none_for_invalid_base64(self):
        """Return None for invalid Base64."""
        with patch.dict(os.environ, {"VOICESTUDIO_IPC_SECRET": "not-valid-base64!!!"}):
            assert get_secret_key() is None


class TestIsSigningEnabled:
    """Tests for is_signing_enabled function."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("", False),
        ],
    )
    def test_various_values(self, value, expected):
        """Test various env var values."""
        with patch.dict(os.environ, {"VOICESTUDIO_IPC_SIGNING_ENABLED": value}):
            assert is_signing_enabled() is expected

    def test_defaults_to_false(self):
        """Default to false when not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_signing_enabled() is False


class TestRequestSigningMiddleware:
    """Integration tests for RequestSigningMiddleware."""

    @pytest.fixture
    def app_with_middleware(self):
        """Create test app with signing middleware."""
        app = FastAPI()

        # Reset middleware cache
        middleware = RequestSigningMiddleware(app)
        middleware._secret_key = TEST_SECRET
        middleware._enabled = True

        @app.get("/api/v1/test")
        async def test_endpoint():
            return {"message": "success"}

        @app.post("/api/v1/data")
        async def data_endpoint():
            return {"message": "data received"}

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        # Apply middleware
        app.add_middleware(
            RequestSigningMiddleware,
            exclude_paths={"/health"},
        )

        return app

    def test_excluded_path_no_signature_required(self, app_with_middleware):
        """Excluded paths don't require signature."""
        # Patch the middleware to be enabled
        with patch.dict(
            os.environ,
            {
                "VOICESTUDIO_IPC_SIGNING_ENABLED": "true",
                "VOICESTUDIO_IPC_SECRET": TEST_SECRET_B64,
            },
        ):
            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get("/health")

            assert response.status_code == 200

    def test_missing_signature_rejected(self, app_with_middleware):
        """Requests without signature are rejected when enabled."""
        with patch.dict(
            os.environ,
            {
                "VOICESTUDIO_IPC_SIGNING_ENABLED": "true",
                "VOICESTUDIO_IPC_SECRET": TEST_SECRET_B64,
            },
        ):
            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get("/api/v1/test")

            assert response.status_code == 401

    def test_valid_signature_accepted(self, app_with_middleware):
        """Requests with valid signature are accepted."""
        with patch.dict(
            os.environ,
            {
                "VOICESTUDIO_IPC_SIGNING_ENABLED": "true",
                "VOICESTUDIO_IPC_SECRET": TEST_SECRET_B64,
            },
        ):
            timestamp = datetime.now(timezone.utc).isoformat()
            signature = compute_signature(
                TEST_SECRET,
                "GET",
                "/api/v1/test",
                timestamp,
                "",
            )

            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get(
                "/api/v1/test",
                headers={
                    SIGNATURE_HEADER: signature,
                    TIMESTAMP_HEADER: timestamp,
                    VERSION_HEADER: "1",
                },
            )

            assert response.status_code == 200

    def test_invalid_signature_rejected(self, app_with_middleware):
        """Requests with invalid signature are rejected."""
        with patch.dict(
            os.environ,
            {
                "VOICESTUDIO_IPC_SIGNING_ENABLED": "true",
                "VOICESTUDIO_IPC_SECRET": TEST_SECRET_B64,
            },
        ):
            timestamp = datetime.now(timezone.utc).isoformat()

            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get(
                "/api/v1/test",
                headers={
                    SIGNATURE_HEADER: "invalid_signature",
                    TIMESTAMP_HEADER: timestamp,
                    VERSION_HEADER: "1",
                },
            )

            assert response.status_code == 401

    def test_expired_timestamp_rejected(self, app_with_middleware):
        """Requests with expired timestamp are rejected."""
        with patch.dict(
            os.environ,
            {
                "VOICESTUDIO_IPC_SIGNING_ENABLED": "true",
                "VOICESTUDIO_IPC_SECRET": TEST_SECRET_B64,
            },
        ):
            # Use old timestamp
            old = datetime.now(timezone.utc) - timedelta(seconds=600)
            timestamp = old.isoformat()
            signature = compute_signature(
                TEST_SECRET,
                "GET",
                "/api/v1/test",
                timestamp,
                "",
            )

            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get(
                "/api/v1/test",
                headers={
                    SIGNATURE_HEADER: signature,
                    TIMESTAMP_HEADER: timestamp,
                    VERSION_HEADER: "1",
                },
            )

            assert response.status_code == 401

    def test_signing_disabled_no_verification(self, app_with_middleware):
        """No verification when signing is disabled."""
        with patch.dict(
            os.environ,
            {
                "VOICESTUDIO_IPC_SIGNING_ENABLED": "false",
            },
        ):
            client = TestClient(app_with_middleware, raise_server_exceptions=False)
            response = client.get("/api/v1/test")

            assert response.status_code == 200


class TestReplayAttackPrevention:
    """Tests for replay attack prevention."""

    def test_same_signature_different_time(self):
        """Signature replay fails after timestamp expires."""
        # Create a signature with a valid timestamp
        timestamp = datetime.now(timezone.utc).isoformat()
        signature = compute_signature(
            TEST_SECRET,
            "GET",
            "/api/v1/test",
            timestamp,
            "",
        )

        # Verify immediately - should pass
        assert (
            verify_signature(
                TEST_SECRET,
                signature,
                "GET",
                "/api/v1/test",
                timestamp,
                "",
            )
            is True
        )

        # Timestamp validation should fail for old timestamps
        old_timestamp = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        old_signature = compute_signature(
            TEST_SECRET,
            "GET",
            "/api/v1/test",
            old_timestamp,
            "",
        )

        # Signature itself is valid but timestamp is expired
        assert (
            verify_signature(
                TEST_SECRET,
                old_signature,
                "GET",
                "/api/v1/test",
                old_timestamp,
                "",
            )
            is True
        )  # Signature is technically valid

        assert validate_timestamp(old_timestamp) is False  # But timestamp is expired
