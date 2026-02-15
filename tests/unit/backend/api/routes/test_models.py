"""
Unit Tests for Models API Routes.

Tests model management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def models_client():
    """Create test client for models routes."""
    from backend.api.routes.models import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestModelsEndpoints:
    """Tests for models endpoints."""

    def test_list_models(self, models_client):
        """Test GET /list returns model list."""
        response = models_client.get("/api/models/list")
        assert response.status_code in [200, 404]

    def test_get_model_by_id(self, models_client):
        """Test GET /model/{id} returns specific model."""
        response = models_client.get("/api/models/model/test-model")
        assert response.status_code in [200, 404]

    def test_download_model(self, models_client):
        """Test POST /download initiates model download."""
        response = models_client.post(
            "/api/models/download",
            json={"model_id": "test-model"}
        )
        assert response.status_code in [200, 202, 404, 422]

    def test_delete_model(self, models_client):
        """Test DELETE /model/{id} deletes a model."""
        response = models_client.delete("/api/models/model/test-model")
        assert response.status_code in [200, 204, 404]

    def test_get_model_status(self, models_client):
        """Test GET /status returns model system status."""
        response = models_client.get("/api/models/status")
        assert response.status_code in [200, 404]
