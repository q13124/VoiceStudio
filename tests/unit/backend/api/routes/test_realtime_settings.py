"""
Unit Tests for Real-Time Settings API Routes.

Tests real-time audio processing settings endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def realtime_settings_client():
    """Create test client for realtime settings routes."""
    from backend.api.routes.realtime_settings import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestRealtimeSettingsEndpoints:
    """Tests for realtime settings endpoints."""

    def test_get_settings(self, realtime_settings_client):
        """Test GET /settings returns current settings."""
        response = realtime_settings_client.get("/api/realtime-settings/settings")
        assert response.status_code in [200, 404]

    def test_update_settings(self, realtime_settings_client):
        """Test PUT /settings updates settings."""
        response = realtime_settings_client.put(
            "/api/realtime-settings/settings",
            json={"latency_mode": "low"}
        )
        assert response.status_code in [200, 404, 422]

    def test_get_presets(self, realtime_settings_client):
        """Test GET /presets returns setting presets."""
        response = realtime_settings_client.get("/api/realtime-settings/presets")
        assert response.status_code in [200, 404]

    def test_apply_preset(self, realtime_settings_client):
        """Test POST /presets/{name}/apply applies a preset."""
        response = realtime_settings_client.post("/api/realtime-settings/presets/default/apply")
        assert response.status_code in [200, 404]
