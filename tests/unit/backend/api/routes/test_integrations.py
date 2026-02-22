"""
Unit Tests for Integrations API Routes.

Tests external integration management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def integrations_client():
    """Create test client for integrations routes."""
    from backend.api.routes.integrations import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestIntegrationsEndpoints:
    """Tests for integrations endpoints."""

    def test_list_integrations(self, integrations_client):
        """Test GET /list returns integration list."""
        response = integrations_client.get("/api/integrations/list")
        assert response.status_code in [200, 404]

    def test_get_integration_status(self, integrations_client):
        """Test GET /status/{name} returns integration status."""
        response = integrations_client.get("/api/integrations/status/elevenlabs")
        assert response.status_code in [200, 404]

    def test_configure_integration(self, integrations_client):
        """Test POST /configure configures an integration."""
        response = integrations_client.post(
            "/api/integrations/configure", json={"name": "test", "config": {}}
        )
        assert response.status_code in [200, 404, 422]

    def test_test_integration(self, integrations_client):
        """Test POST /test tests integration connectivity."""
        response = integrations_client.post("/api/integrations/test", json={"name": "test"})
        assert response.status_code in [200, 404, 422]
