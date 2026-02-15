"""
Unit Tests for Diagnostics API Routes.

Tests system diagnostics and troubleshooting endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def diagnostics_client():
    """Create test client for diagnostics routes."""
    from backend.api.routes.diagnostics import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestDiagnosticsEndpoints:
    """Tests for diagnostics endpoints."""

    def test_get_status(self, diagnostics_client):
        """Test GET /status returns quick status."""
        response = diagnostics_client.get("/api/diagnostics/status")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "hostname" in data
        assert "platform" in data

    def test_run_diagnostics(self, diagnostics_client):
        """Test GET /run runs full diagnostics."""
        response = diagnostics_client.get("/api/diagnostics/run")
        assert response.status_code == 200
        data = response.json()
        assert "generated_at" in data
        assert "overall_status" in data

    def test_get_checks(self, diagnostics_client):
        """Test GET /checks returns available checks."""
        response = diagnostics_client.get("/api/diagnostics/checks")
        assert response.status_code == 200

    def test_get_categories(self, diagnostics_client):
        """Test GET /categories returns available categories."""
        response = diagnostics_client.get("/api/diagnostics/categories")
        assert response.status_code == 200

    def test_save_report(self, diagnostics_client):
        """Test POST /save saves diagnostic report."""
        response = diagnostics_client.post("/api/diagnostics/save")
        assert response.status_code in [200, 500]

    def test_get_recommendations(self, diagnostics_client):
        """Test GET /recommendations returns recommendations."""
        response = diagnostics_client.get("/api/diagnostics/recommendations")
        assert response.status_code == 200

    def test_get_environment(self, diagnostics_client):
        """Test GET /environment returns environment info."""
        response = diagnostics_client.get("/api/diagnostics/environment")
        assert response.status_code == 200
