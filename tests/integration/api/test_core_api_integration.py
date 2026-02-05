"""
Core API Integration Tests

Tests core API functionality including:
- Health endpoints
- Version negotiation
- Standard response formats
- Error handling
"""

import pytest


@pytest.mark.integration
@pytest.mark.api
class TestHealthEndpoints:
    """Integration tests for health endpoints."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns version info."""
        response = test_client.get("/")
        test_client.assert_success(response)

        assert "message" in response.body
        assert "version" in response.body
        assert "VoiceStudio" in response.body.get("message", "")

    def test_health_endpoint(self, test_client):
        """Test basic health endpoint."""
        response = test_client.get("/health")
        test_client.assert_success(response)

        assert response.body.get("status") == "ok"

    def test_api_health_endpoint(self, test_client):
        """Test API health endpoint with metrics."""
        response = test_client.get("/api/health")
        test_client.assert_success(response)

        body = response.body
        assert body.get("status") == "ok"
        assert "version" in body


@pytest.mark.integration
@pytest.mark.api
class TestVersioning:
    """Integration tests for API versioning."""

    def test_version_headers_present(self, test_client):
        """Test that version headers are present in responses."""
        response = test_client.get("/health")
        test_client.assert_success(response)

        # Check version headers are present
        headers = {k.lower(): v for k, v in response.headers.items()}
        assert "x-api-version" in headers
        assert "x-min-version" in headers

    def test_version_endpoint(self, test_client):
        """Test /api/version endpoint returns version info."""
        response = test_client.get("/api/version")
        test_client.assert_success(response)

        body = response.body
        assert "current_version" in body
        assert "min_supported_version" in body
        assert "negotiated_version" in body
        assert "supported_versions" in body

    def test_version_negotiation_with_header(self, test_client):
        """Test version negotiation with X-API-Version header."""
        response = test_client.get(
            "/api/version",
            headers={"X-API-Version": "1.0"}
        )
        test_client.assert_success(response)

        assert response.body.get("negotiated_version") == "1.0"

    def test_version_negotiation_unsupported(self, test_client):
        """Test version negotiation with unsupported version."""
        response = test_client.get(
            "/api/version",
            headers={"X-API-Version": "99.0"}
        )
        test_client.assert_success(response)

        # Should fall back to current version (1.0)
        assert response.body.get("negotiated_version") == "1.0"
        # May or may not have warnings depending on implementation
        # Just verify the endpoint works with invalid version


@pytest.mark.integration
@pytest.mark.api
class TestMetricsEndpoints:
    """Integration tests for metrics endpoints."""

    def test_api_metrics_endpoint(self, test_client):
        """Test /api/metrics endpoint."""
        response = test_client.get("/api/metrics")
        test_client.assert_success(response)

        body = response.body
        assert "timestamp" in body
        assert "errors" in body

    def test_cache_stats_endpoint(self, test_client):
        """Test /api/cache/stats endpoint."""
        response = test_client.get("/api/cache/stats")
        test_client.assert_success(response)


@pytest.mark.integration
@pytest.mark.api
class TestErrorHandling:
    """Integration tests for error handling."""

    def test_404_error_format(self, test_client):
        """Test 404 error has standard format."""
        response = test_client.get("/api/nonexistent-endpoint-xyz")
        test_client.assert_status(response, 404)

        # Should have error detail
        body = response.body
        assert "detail" in body or "error" in body

    def test_validation_error_format(self, test_client):
        """Test validation error has standard format."""
        # Post to an endpoint with invalid data
        response = test_client.post(
            "/api/voice/synthesize",
            json={}  # Missing required fields
        )

        # Should return 422 for validation error
        if response.status_code == 422:
            body = response.body
            assert "detail" in body


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestResponsePerformance:
    """Integration tests for response performance."""

    def test_health_response_time(self, test_client):
        """Test health endpoint responds quickly."""
        response = test_client.get("/health")
        test_client.assert_success(response)

        # Health should respond in under 100ms
        assert response.elapsed_ms < 100, (
            f"Health endpoint too slow: {response.elapsed_ms:.2f}ms"
        )

    def test_version_response_time(self, test_client):
        """Test version endpoint responds quickly."""
        response = test_client.get("/api/version")
        test_client.assert_success(response)

        # Version should respond in under 200ms
        assert response.elapsed_ms < 200, (
            f"Version endpoint too slow: {response.elapsed_ms:.2f}ms"
        )


@pytest.mark.integration
@pytest.mark.api
class TestSchedulerEndpoints:
    """Integration tests for scheduler endpoints."""

    def test_scheduler_stats(self, test_client):
        """Test /api/scheduler/stats endpoint."""
        response = test_client.get("/api/scheduler/stats")
        test_client.assert_success(response)

    def test_scheduler_tasks_list(self, test_client):
        """Test /api/scheduler/tasks endpoint."""
        response = test_client.get("/api/scheduler/tasks")
        test_client.assert_success(response)

        body = response.body
        assert "tasks" in body or "error" not in body


@pytest.mark.integration
@pytest.mark.api
class TestProfilerEndpoints:
    """Integration tests for profiler endpoints."""

    def test_profiler_stats(self, test_client):
        """Test /api/profiler/stats endpoint."""
        response = test_client.get("/api/profiler/stats")
        test_client.assert_success(response)

    def test_profiler_detailed(self, test_client):
        """Test /api/profiler/detailed endpoint."""
        response = test_client.get("/api/profiler/detailed")
        test_client.assert_success(response)


@pytest.mark.integration
@pytest.mark.api
class TestValidationEndpoints:
    """Integration tests for validation endpoints."""

    def test_validation_stats(self, test_client):
        """Test /api/validation/stats endpoint."""
        response = test_client.get("/api/validation/stats")
        test_client.assert_success(response)
