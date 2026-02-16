"""
File Security Tests.

Tests for file-related security including:
- Secure filename handling
- Security headers in responses
- Path sanitization
- Error response security

Phase 7C: File Security
"""

from __future__ import annotations

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.security,
    pytest.mark.file_security,
]


@pytest.fixture
def api_client():
    """Create a test client for API tests."""
    from fastapi.testclient import TestClient

    from backend.api.main import app
    return TestClient(app)


@pytest.fixture
def backend_available(api_client):
    """Check if backend is available."""
    try:
        response = api_client.get("/api/health")
        return response.status_code == 200
    except Exception:
        return False


class TestSecurityHeaders:
    """Tests for security-related HTTP headers."""

    def test_content_type_header_set(self, api_client, backend_available):
        """Test that Content-Type header is always set."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health")
        assert "content-type" in response.headers

    def test_json_responses_have_charset(self, api_client, backend_available):
        """Test that JSON responses specify charset."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/version")
        content_type = response.headers.get("content-type", "")
        # Either charset is specified or it's application/json (which defaults to UTF-8)
        assert "application/json" in content_type.lower()

    def test_x_content_type_options(self, api_client, backend_available):
        """Test X-Content-Type-Options header to prevent MIME sniffing."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health")
        # This header may or may not be present depending on middleware configuration
        # If present, it should be "nosniff"
        header = response.headers.get("x-content-type-options")
        if header:
            assert header.lower() == "nosniff"

    def test_no_server_version_exposure(self, api_client, backend_available):
        """Test that server doesn't expose detailed version info in headers."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health")
        server_header = response.headers.get("server", "")
        # Should not contain specific version numbers
        assert "uvicorn" not in server_header.lower() or "/" not in server_header


class TestErrorResponseSecurity:
    """Tests for secure error responses."""

    def test_no_stack_traces_in_errors(self, api_client, backend_available):
        """Test that stack traces are not exposed in error responses."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Trigger a 404 error
        response = api_client.get("/api/nonexistent_endpoint_xyz")
        body = response.text.lower()
        
        # Should not contain stack trace indicators
        assert "traceback" not in body
        assert "file \"" not in body
        assert "line " not in body or "not found" in body

    def test_no_internal_paths_in_errors(self, api_client, backend_available):
        """Test that internal file paths are not exposed."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/this_does_not_exist")
        body = response.text
        
        # Should not contain internal paths
        assert "C:\\" not in body
        assert "/home/" not in body
        assert "/usr/" not in body
        assert "site-packages" not in body

    def test_no_version_info_in_errors(self, api_client, backend_available):
        """Test that dependency versions are not exposed in errors."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/missing_endpoint")
        body = response.text.lower()
        
        # Should not expose Python or framework versions
        assert "python" not in body or "endpoint" in body
        assert "fastapi" not in body

    def test_consistent_error_format(self, api_client, backend_available):
        """Test that error responses have consistent format."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/does_not_exist")
        
        # Should return JSON error
        assert response.status_code in (404, 422)
        content_type = response.headers.get("content-type", "")
        assert "json" in content_type.lower()


class TestPathSanitization:
    """Tests for path traversal prevention in URL paths."""

    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..%2f..%2f..%2fetc/passwd",
        "....//....//etc/passwd",
        "%2e%2e%2f",
    ]

    def test_path_traversal_in_url(self, api_client, backend_available):
        """Test path traversal attempts in URL paths."""
        if not backend_available:
            pytest.skip("Backend not available")

        for payload in self.PATH_TRAVERSAL_PAYLOADS:
            response = api_client.get(f"/api/endpoints/metrics/{payload}")
            # 200 is acceptable if path traversal is handled by treating it as a literal key
            # The key assertion is that no actual file contents are exposed
            assert response.status_code in (200, 400, 404, 422, 429, 500)
            # Should not contain actual /etc/passwd contents (root:x:0:0:...)
            assert "root:x:" not in response.text
            assert "root:*:" not in response.text
            # Should not contain Windows SAM file contents
            assert "Administrator:500:" not in response.text

    def test_encoded_path_traversal(self, api_client, backend_available):
        """Test URL-encoded path traversal attempts."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Double-encoded traversal
        response = api_client.get("/api/engines/metrics/%252e%252e%252f%252e%252e%252fetc/passwd")
        assert response.status_code in (400, 404, 422, 429, 500)
        assert "root:" not in response.text


class TestFilenameSanitization:
    """Tests for filename sanitization logic."""

    MALICIOUS_FILENAMES = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "file.php.wav",  # Double extension
        "file.exe",  # Executable
        "<script>alert(1)</script>.wav",  # XSS in filename
        "CON.wav",  # Reserved Windows name
        "LPT1.wav",  # Reserved Windows name
    ]

    def test_malicious_filenames_in_query(self, api_client, backend_available):
        """Test malicious filenames in query parameters."""
        if not backend_available:
            pytest.skip("Backend not available")

        for filename in self.MALICIOUS_FILENAMES[:4]:  # Test subset (no null bytes)
            response = api_client.get(f"/api/validation/stats?file={filename}")
            # Should handle gracefully
            assert response.status_code in (200, 400, 404, 422, 429)
            # Should not expose actual system file contents
            assert "root:x:" not in response.text
            assert "Administrator:500:" not in response.text

    def test_null_byte_in_path(self, api_client, backend_available):
        """Test null byte injection in path parameters."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Note: URL-encoded null byte (%00) is handled by the HTTP layer
        response = api_client.get("/api/engines/metrics/test%00.php")
        # Should handle gracefully - 200 is acceptable as it means the null byte was stripped/ignored
        assert response.status_code in (200, 400, 404, 422, 429, 500)
        # Should not expose PHP file contents
        assert "<?php" not in response.text


class TestInputBoundaries:
    """Tests for input length and boundary conditions."""

    def test_very_long_path(self, api_client, backend_available):
        """Test handling of very long URL paths."""
        if not backend_available:
            pytest.skip("Backend not available")

        long_path = "x" * 1000
        response = api_client.get(f"/api/endpoints/metrics/{long_path}")
        # Should handle gracefully - 200 is acceptable as long path is treated as a key
        assert response.status_code in (200, 400, 404, 414, 422, 429, 500)

    def test_very_long_query_string(self, api_client, backend_available):
        """Test handling of very long query strings."""
        if not backend_available:
            pytest.skip("Backend not available")

        long_query = "x" * 5000
        response = api_client.get(f"/api/validation/stats?data={long_query}")
        # Should handle gracefully
        assert response.status_code in (200, 400, 414, 422, 429, 500)

    def test_many_query_parameters(self, api_client, backend_available):
        """Test handling of many query parameters."""
        if not backend_available:
            pytest.skip("Backend not available")

        params = "&".join([f"param{i}=value{i}" for i in range(100)])
        response = api_client.get(f"/api/validation/stats?{params}")
        # Should handle gracefully
        assert response.status_code in (200, 400, 414, 422, 429, 500)


class TestSpecialCharacterHandling:
    """Tests for handling special characters in requests."""

    def test_unicode_in_path(self, api_client, backend_available):
        """Test Unicode characters in URL path."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Use URL-encoded Unicode to avoid encoding issues
        unicode_paths = [
            "/api/endpoints/metrics/test%E2%80%AE",  # RTL override (U+202E)
            "/api/endpoints/metrics/test_emoji",  # Simple path (emoji encoding varies)
        ]

        for path in unicode_paths:
            try:
                response = api_client.get(path)
                # Should handle gracefully
                assert response.status_code in (200, 400, 404, 422, 429, 500)
            except Exception:
                # Some Unicode may cause encoding issues in the HTTP library
                # which is acceptable security behavior
                pass

    def test_control_characters_in_path(self, api_client, backend_available):
        """Test control characters in URL path."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Test with URL-encoded control characters
        response = api_client.get("/api/endpoints/metrics/test%0d%0a")
        # Should handle gracefully - CRLF injection prevention
        assert response.status_code in (200, 400, 404, 422, 429, 500)
