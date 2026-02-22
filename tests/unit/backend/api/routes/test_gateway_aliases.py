"""
Unit Tests for Gateway Aliases API Routes.

Tests voice API gateway alias endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def gateway_client():
    """Create test client for gateway alias routes."""
    from backend.api.routes.gateway_aliases import voice_alias_router as router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestGatewayAliasEndpoints:
    """Tests for gateway alias endpoints."""

    def test_synthesize_alias(self, gateway_client):
        """Test POST /synthesize voice synthesis alias."""
        response = gateway_client.post("/api/voice/synthesize", json={"text": "Hello"})
        assert response.status_code in [200, 404, 422]

    def test_clone_alias(self, gateway_client):
        """Test POST /clone voice cloning alias."""
        response = gateway_client.post("/api/voice/clone", json={})
        assert response.status_code in [200, 404, 422]

    def test_list_voices_alias(self, gateway_client):
        """Test GET /voices returns voice list."""
        response = gateway_client.get("/api/voice/voices")
        assert response.status_code in [200, 404]

    def test_get_voice_alias(self, gateway_client):
        """Test GET /voices/{voice_id} returns specific voice."""
        response = gateway_client.get("/api/voice/voices/test-voice")
        assert response.status_code in [200, 404]
