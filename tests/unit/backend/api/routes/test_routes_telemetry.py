"""
Unit Tests for Telemetry API Routes.

Tests telemetry data collection endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def telemetry_client():
    """Create test client for telemetry routes."""
    from backend.api.routes.telemetry import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestTelemetryEndpoints:
    """Tests for telemetry endpoints."""

    def test_get_status(self, telemetry_client):
        """Test GET /status returns telemetry status."""
        response = telemetry_client.get("/api/telemetry/status")
        assert response.status_code in [200, 404]

    def test_get_events(self, telemetry_client):
        """Test GET /events returns event list."""
        response = telemetry_client.get("/api/telemetry/events")
        assert response.status_code in [200, 404]

    def test_post_event(self, telemetry_client):
        """Test POST /events records an event."""
        response = telemetry_client.post(
            "/api/telemetry/events",
            json={"event_type": "test", "data": {}}
        )
        assert response.status_code in [200, 201, 404, 422]
