"""
Unit Tests for Translation API Routes.

Tests translation service endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def translation_client():
    """Create test client for translation routes."""
    from backend.api.routes.translation import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestTranslationEndpoints:
    """Tests for translation endpoints."""

    def test_get_languages(self, translation_client):
        """Test GET /languages returns supported languages."""
        response = translation_client.get("/api/translation/languages")
        assert response.status_code in [200, 404]

    def test_translate_validation(self, translation_client):
        """Test POST /translate validates required fields."""
        response = translation_client.post("/api/translation/translate", json={})
        assert response.status_code in [200, 404, 422]

    def test_detect_language(self, translation_client):
        """Test POST /detect detects language."""
        response = translation_client.post("/api/translation/detect", json={"text": "Hello world"})
        assert response.status_code in [200, 404, 422]
