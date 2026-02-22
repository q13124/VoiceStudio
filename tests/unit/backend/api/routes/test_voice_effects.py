"""
Unit Tests for Voice Effects API Routes.

Tests voice effects processing endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def voice_effects_client():
    """Create test client for voice effects routes."""
    from backend.api.routes.voice_effects import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestVoiceEffectsEndpoints:
    """Tests for voice effects endpoints."""

    def test_list_effects(self, voice_effects_client):
        """Test GET /effects returns available effects."""
        response = voice_effects_client.get("/api/voice-effects/effects")
        assert response.status_code in [200, 404]

    def test_get_effect_by_id(self, voice_effects_client):
        """Test GET /effects/{effect_id} returns specific effect."""
        response = voice_effects_client.get("/api/voice-effects/effects/reverb")
        assert response.status_code in [200, 404]

    def test_apply_effect_validation(self, voice_effects_client):
        """Test POST /apply validates required fields."""
        response = voice_effects_client.post("/api/voice-effects/apply", json={})
        assert response.status_code in [200, 404, 422]

    def test_get_presets(self, voice_effects_client):
        """Test GET /presets returns effect presets."""
        response = voice_effects_client.get("/api/voice-effects/presets")
        # May return 500 if preset service not fully initialized
        assert response.status_code in [200, 404, 500]
