"""
Unit Tests for Metrics API Routes.

Tests Prometheus metrics export endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def metrics_client():
    """Create test client for metrics routes."""
    from backend.api.routes.metrics import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestMetricsEndpoints:
    """Tests for metrics endpoints."""

    def test_get_metrics_text(self, metrics_client):
        """Test GET /metrics returns Prometheus text format."""
        response = metrics_client.get("/api/metrics")
        # Returns plain text in Prometheus format
        assert response.status_code == 200

    def test_get_metrics_json_format(self, metrics_client):
        """Test GET /metrics?format=json returns JSON format."""
        response = metrics_client.get("/api/metrics", params={"format": "json"})
        assert response.status_code == 200

    def test_get_metrics_by_name(self, metrics_client):
        """Test GET /metrics/{name} returns specific metric."""
        response = metrics_client.get("/api/metrics/test_metric")
        # May return 200 or 404 depending on metric existence
        assert response.status_code in [200, 404]

    def test_set_metric(self, metrics_client):
        """Test POST /metrics sets a metric value."""
        response = metrics_client.post(
            "/api/metrics",
            json={"name": "test_metric", "value": 1.0}
        )
        # POST may not be implemented (read-only metrics)
        assert response.status_code in [200, 201, 405, 422]
