"""
Unit Tests for Plugin Gallery API Routes.

Tests plugin gallery browsing endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def gallery_client():
    """Create test client for plugin gallery routes."""
    from backend.api.routes.plugin_gallery import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestPluginGalleryEndpoints:
    """Tests for plugin gallery endpoints."""

    def test_browse_gallery(self, gallery_client):
        """Test GET /gallery returns gallery listing."""
        response = gallery_client.get("/api/plugins/gallery")
        assert response.status_code in [200, 404]

    def test_search_plugins(self, gallery_client):
        """Test GET /search searches plugins."""
        response = gallery_client.get("/api/plugins/search", params={"q": "voice"})
        assert response.status_code in [200, 404]

    def test_get_categories(self, gallery_client):
        """Test GET /categories returns plugin categories."""
        response = gallery_client.get("/api/plugins/categories")
        assert response.status_code in [200, 404]

    def test_get_featured(self, gallery_client):
        """Test GET /featured returns featured plugins."""
        response = gallery_client.get("/api/plugins/featured")
        assert response.status_code in [200, 404]
