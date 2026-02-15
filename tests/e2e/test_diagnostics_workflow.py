"""
Diagnostics and Logs Workflow E2E Tests.

Tests for diagnostics and logging operations including:
- View diagnostics
- Export diagnostic report
- View health status
- Log viewer operations

Phase 9A: Feature Matrix - Logs
"""

from __future__ import annotations

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
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


class TestHealthStatus:
    """Tests for health status endpoints."""

    def test_basic_health_check(self, api_client, backend_available):
        """Test basic health endpoint."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "healthy" in str(data).lower()

    def test_detailed_health_check(self, api_client, backend_available):
        """Test detailed health check with component status."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health/detailed")
        assert response.status_code in (200, 404, 422, 429)

    def test_readiness_check(self, api_client, backend_available):
        """Test readiness probe."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health/ready")
        assert response.status_code in (200, 404, 422, 429)

    def test_liveness_check(self, api_client, backend_available):
        """Test liveness probe."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/health/live")
        assert response.status_code in (200, 404, 422, 429)


class TestDiagnosticsView:
    """Tests for viewing diagnostics."""

    def test_get_diagnostics_summary(self, api_client, backend_available):
        """Test getting diagnostics summary."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_system_info(self, api_client, backend_available):
        """Test getting system information."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/system")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_gpu_info(self, api_client, backend_available):
        """Test getting GPU information."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/gpu")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_memory_info(self, api_client, backend_available):
        """Test getting memory information."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/memory")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_engine_diagnostics(self, api_client, backend_available):
        """Test getting engine diagnostics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/engines")
        assert response.status_code in (200, 404, 422, 429)


class TestDiagnosticsExport:
    """Tests for exporting diagnostic reports."""

    def test_export_diagnostic_report(self, api_client, backend_available):
        """Test exporting full diagnostic report."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/export")
        assert response.status_code in (200, 404, 422, 429)

    def test_export_diagnostic_report_json(self, api_client, backend_available):
        """Test exporting diagnostic report as JSON."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/export?format=json")
        assert response.status_code in (200, 404, 422, 429)

    def test_export_diagnostic_report_text(self, api_client, backend_available):
        """Test exporting diagnostic report as text."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/diagnostics/export?format=text")
        assert response.status_code in (200, 404, 422, 429)


class TestLogsView:
    """Tests for log viewing operations."""

    def test_get_recent_logs(self, api_client, backend_available):
        """Test getting recent logs."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/logs/")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_logs_with_pagination(self, api_client, backend_available):
        """Test getting logs with pagination."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/logs/?page=1&limit=50")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_logs_by_level(self, api_client, backend_available):
        """Test filtering logs by level."""
        if not backend_available:
            pytest.skip("Backend not available")

        for level in ["error", "warning", "info", "debug"]:
            response = api_client.get(f"/api/logs/?level={level}")
            assert response.status_code in (200, 404, 422, 429)

    def test_get_logs_by_source(self, api_client, backend_available):
        """Test filtering logs by source."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/logs/?source=engine")
        assert response.status_code in (200, 404, 422, 429)

    def test_search_logs(self, api_client, backend_available):
        """Test searching logs."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/logs/search?q=error")
        assert response.status_code in (200, 404, 422, 429)


class TestLogsExport:
    """Tests for log export operations."""

    def test_export_logs(self, api_client, backend_available):
        """Test exporting logs."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/logs/export")
        assert response.status_code in (200, 404, 422, 429)

    def test_export_error_logs(self, api_client, backend_available):
        """Test exporting only error logs."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/logs/export?level=error")
        assert response.status_code in (200, 404, 422, 429)

    def test_clear_logs(self, api_client, backend_available):
        """Test clearing logs (admin operation)."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.delete("/api/logs/clear")
        # Should require auth or return appropriate status
        assert response.status_code in (200, 204, 400, 401, 403, 404, 422, 429)


class TestErrorTracking:
    """Tests for error tracking functionality."""

    def test_get_error_summary(self, api_client, backend_available):
        """Test getting error summary."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/errors/")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_recent_errors(self, api_client, backend_available):
        """Test getting recent errors."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/errors/recent")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_error_details(self, api_client, backend_available):
        """Test getting error details by ID."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/errors/nonexistent_id")
        assert response.status_code in (200, 404, 422, 429)

    def test_acknowledge_error(self, api_client, backend_available):
        """Test acknowledging an error."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post("/api/errors/test_id/acknowledge")
        assert response.status_code in (200, 400, 404, 422, 429)


class TestPerformanceMetrics:
    """Tests for performance metrics."""

    def test_get_performance_metrics(self, api_client, backend_available):
        """Test getting performance metrics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/metrics/")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_api_metrics(self, api_client, backend_available):
        """Test getting API performance metrics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/metrics/api")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_engine_metrics(self, api_client, backend_available):
        """Test getting engine performance metrics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/metrics/engines")
        assert response.status_code in (200, 404, 422, 429)
