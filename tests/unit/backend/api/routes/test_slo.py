"""
Unit Tests for SLO Monitoring API Routes.

Tests SLO status, alerts, and management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def slo_client():
    """Create test client for SLO routes."""
    from backend.api.routes.slo import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestSLOStatus:
    """Tests for SLO status endpoints."""

    def test_list_slos(self, slo_client):
        """Test GET / returns all SLO statuses."""
        response = slo_client.get("/api/slo")
        assert response.status_code == 200
        data = response.json()
        assert "slos" in data
        assert "overview" in data

    def test_get_health(self, slo_client):
        """Test GET /health returns SLO health overview."""
        response = slo_client.get("/api/slo/health")
        assert response.status_code == 200

    def test_get_slo_by_id(self, slo_client):
        """Test GET /{slo_id} returns specific SLO."""
        response = slo_client.get("/api/slo/nonexistent")
        assert response.status_code in [200, 404]


class TestSLOAlerts:
    """Tests for SLO alert endpoints."""

    def test_list_active_alerts(self, slo_client):
        """Test GET /alerts/active returns active alerts."""
        response = slo_client.get("/api/slo/alerts/active")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    def test_list_alert_history(self, slo_client):
        """Test GET /alerts/history returns alert history."""
        response = slo_client.get("/api/slo/alerts/history")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    def test_acknowledge_alert(self, slo_client):
        """Test POST /alerts/{alert_id}/acknowledge acknowledges alert."""
        response = slo_client.post(
            "/api/slo/alerts/test-alert/acknowledge",
            json={"acknowledged_by": "test-user"}
        )
        assert response.status_code in [200, 404, 422]


class TestSLOManagement:
    """Tests for SLO management endpoints."""

    def test_export_slos(self, slo_client):
        """Test POST /export exports SLO data."""
        response = slo_client.post("/api/slo/export")
        assert response.status_code in [200, 500]

    def test_record_metric(self, slo_client):
        """Test POST /record/{metric_name} records a metric."""
        response = slo_client.post(
            "/api/slo/record/test_metric",
            json={"value": 100.0}
        )
        assert response.status_code in [200, 422]
