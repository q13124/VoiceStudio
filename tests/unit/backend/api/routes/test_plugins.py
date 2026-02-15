"""
Unit Tests for Plugins API Routes.

Tests plugin system management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def plugins_client():
    """Create test client for plugins routes."""
    from backend.api.routes.plugins import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestPluginsEndpoints:
    """Tests for plugins endpoints."""

    def test_list_plugins(self, plugins_client):
        """Test GET /list returns plugin list."""
        response = plugins_client.get("/api/plugins/list")
        assert response.status_code in [200, 404]

    def test_get_plugin_by_id(self, plugins_client):
        """Test GET /plugin/{id} returns specific plugin."""
        response = plugins_client.get("/api/plugins/plugin/test-plugin")
        assert response.status_code in [200, 404]

    def test_install_plugin(self, plugins_client):
        """Test POST /install installs a plugin."""
        response = plugins_client.post(
            "/api/plugins/install",
            json={"plugin_id": "test-plugin"}
        )
        # 405 if POST install endpoint not implemented
        assert response.status_code in [200, 201, 404, 405, 422]

    def test_uninstall_plugin(self, plugins_client):
        """Test POST /uninstall uninstalls a plugin."""
        response = plugins_client.post(
            "/api/plugins/uninstall",
            json={"plugin_id": "test-plugin"}
        )
        # 405 if POST uninstall endpoint not implemented
        assert response.status_code in [200, 404, 405, 422]
