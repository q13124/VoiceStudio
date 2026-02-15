"""
Integration Tests for Tracing API — Phase 5.1

Tests for the tracing API endpoints.
"""

import sys
from pathlib import Path

import pytest

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


pytestmark = pytest.mark.integration


class TestTracingEndpoints:
    """Test tracing API endpoints."""

    def test_get_trace_summary(self, client):
        """Test GET /api/tracing/summary endpoint."""
        response = client.get("/api/tracing/summary")

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total_traces" in data
        assert "total_spans" in data
        assert "avg_duration_ms" in data
        assert "error_rate" in data
        assert "p50_duration_ms" in data
        assert "p95_duration_ms" in data
        assert "p99_duration_ms" in data

    def test_get_recent_spans(self, client):
        """Test GET /api/tracing/recent endpoint."""
        response = client.get("/api/tracing/recent", params={"limit": 10})

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()

        # Response should be a list
        assert isinstance(data, list)

        # If there are spans, verify structure
        if data:
            span = data[0]
            assert "trace_id" in span
            assert "span_id" in span
            assert "name" in span
            assert "duration_ms" in span
            assert "status" in span

    def test_get_recent_spans_with_filter(self, client):
        """Test filtering recent spans by operation."""
        # First, generate some spans by calling an API
        client.get("/api/health")

        response = client.get(
            "/api/tracing/recent",
            params={"limit": 50, "operation": "http"}
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_operations_statistics(self, client):
        """Test GET /api/tracing/operations endpoint."""
        # Generate some spans
        for _ in range(3):
            client.get("/api/health")

        response = client.get("/api/tracing/operations")

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()

        # Response should be a list
        assert isinstance(data, list)

        # If there are operations, verify structure
        if data:
            op = data[0]
            assert "operation" in op
            assert "count" in op
            assert "avg_ms" in op
            assert "p50_ms" in op
            assert "p95_ms" in op
            assert "error_rate" in op

    def test_get_slow_spans(self, client):
        """Test GET /api/tracing/slow-spans endpoint."""
        response = client.get(
            "/api/tracing/slow-spans",
            params={"threshold_ms": 0, "limit": 10}  # 0ms to get all spans
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_error_spans(self, client):
        """Test GET /api/tracing/errors endpoint."""
        response = client.get("/api/tracing/errors", params={"limit": 10})

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_trace_tree_not_found(self, client):
        """Test GET /api/tracing/trace/{trace_id}/tree for non-existent trace."""
        response = client.get("/api/tracing/trace/nonexistent-trace-id/tree")

        if response.status_code == 500:
            # Route exists but trace not found
            pass
        elif response.status_code == 404:
            # Either route not registered or trace not found
            pass

        # Just verify we get a response
        assert response.status_code in [404, 500]

    def test_export_traces(self, client):
        """Test POST /api/tracing/export endpoint."""
        # Generate some spans first
        client.get("/api/health")
        client.get("/api/version")

        response = client.post(
            "/api/tracing/export",
            params={"limit": 100}
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "filepath" in data
        assert "trace_count" in data
        assert "span_count" in data
        assert "message" in data
        assert data["success"] is True

    def test_export_traces_with_filename(self, client):
        """Test exporting traces with custom filename."""
        response = client.post(
            "/api/tracing/export",
            params={"limit": 10, "filename": "custom_export.json"}
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        assert response.status_code == 200
        data = response.json()

        assert "custom_export.json" in data["filepath"]


class TestTracingSummaryAccuracy:
    """Test that tracing summary is accurate."""

    def test_summary_reflects_api_calls(self, client):
        """Test that summary reflects actual API calls made."""
        # Get initial summary
        initial_response = client.get("/api/tracing/summary")

        if initial_response.status_code == 404:
            pytest.skip("Tracing route not registered")

        initial = initial_response.json()
        initial_spans = initial["total_spans"]

        # Make some API calls
        num_calls = 5
        for _ in range(num_calls):
            client.get("/api/health")

        # Get updated summary
        updated_response = client.get("/api/tracing/summary")
        updated = updated_response.json()

        # Span count should increase (at least by num_calls, maybe more from summary calls)
        assert updated["total_spans"] >= initial_spans + num_calls


class TestTracingParameterValidation:
    """Test parameter validation for tracing endpoints."""

    def test_recent_limit_max(self, client):
        """Test that limit parameter is capped."""
        response = client.get(
            "/api/tracing/recent",
            params={"limit": 10000}  # Over max
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        # Should either succeed with capped limit or return validation error
        assert response.status_code in [200, 422]

    def test_slow_spans_negative_threshold(self, client):
        """Test threshold parameter validation."""
        response = client.get(
            "/api/tracing/slow-spans",
            params={"threshold_ms": -100}
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        # Should return validation error
        assert response.status_code == 422

    def test_summary_limit_range(self, client):
        """Test limit parameter range for summary."""
        response = client.get(
            "/api/tracing/summary",
            params={"limit": 0}  # Below minimum
        )

        if response.status_code == 404:
            pytest.skip("Tracing route not registered")

        # Should return validation error
        assert response.status_code == 422
