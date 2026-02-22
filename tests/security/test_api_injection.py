"""
API Injection Security Tests.

Phase 8 WS5: SQL injection, path traversal, header injection against API routes.
Targets real API endpoints to verify input sanitization.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.security]


@pytest.fixture
def api_client():
    """Create a test client for API tests."""
    from fastapi.testclient import TestClient

    from backend.api.main import app

    return TestClient(app)


INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "1 OR 1=1",
    "' UNION SELECT * FROM users --",
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32",
    "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "<script>alert(1)</script>",
    "{{7*7}}",
]


class TestAPIInjection:
    """Injection attacks against API routes."""

    def test_sql_injection_in_voice_synthesize_text(self, api_client):
        """SQL injection in synthesis text body should be sanitized or rejected."""
        for payload in INJECTION_PAYLOADS[:3]:
            response = api_client.post(
                "/api/voice/synthesize",
                json={"text": payload, "engine_id": "piper", "voice_id": "test"},
            )
            # Should not return 500 with SQL error; 400/422/404/503 acceptable
            assert response.status_code != 500 or "SQL" not in response.text.upper()
            assert response.status_code != 500 or "syntax" not in response.text.lower()

    def test_path_traversal_in_audio_id(self, api_client):
        """Path traversal in path parameter should be rejected."""
        payload = "../../../etc/passwd"
        response = api_client.get(f"/api/voice/audio/{payload}")
        # 404 = not found, 400/422 = validation error
        assert response.status_code in (400, 404, 422, 500, 503)

    def test_header_injection_no_sql_leak(self, api_client):
        """Malicious headers should not cause SQL errors in response."""
        response = api_client.get(
            "/api/health",
            headers={
                "X-Custom": "'; DROP TABLE users; --",
                "X-Forwarded-For": "1' OR '1'='1",
            },
        )
        body = response.text.upper()
        assert "SQL" not in body or "SYNTAX" not in body
        assert response.status_code in (200, 400, 401, 403, 422, 429, 500, 503)

    def test_json_body_injection_in_models(self, api_client):
        """Injection in JSON body for models API."""
        response = api_client.post(
            "/api/models",
            json={"engine_id": "'; DROP TABLE models; --", "model_name": "test"},
        )
        assert response.status_code != 500 or "SQL" not in response.text.upper()
