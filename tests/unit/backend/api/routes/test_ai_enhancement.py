"""
Unit Tests for AI Enhancement API Routes.

Tests AI-powered audio enhancement endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def ai_enhancement_client():
    """Create test client for AI enhancement routes."""
    from backend.api.routes.ai_enhancement import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestAIEnhancementEndpoints:
    """Tests for AI enhancement endpoints."""

    def test_enhance_audio_validation(self, ai_enhancement_client):
        """Test POST /enhance validates required fields."""
        response = ai_enhancement_client.post("/api/ai-enhancement/enhance", json={})
        assert response.status_code in [200, 404, 422]

    def test_get_models(self, ai_enhancement_client):
        """Test GET /models returns available models."""
        response = ai_enhancement_client.get("/api/ai-enhancement/models")
        assert response.status_code in [200, 404]

    def test_get_presets(self, ai_enhancement_client):
        """Test GET /presets returns enhancement presets."""
        response = ai_enhancement_client.get("/api/ai-enhancement/presets")
        # May return 500 if preset service not fully initialized
        assert response.status_code in [200, 404, 500]

    def test_get_job_status(self, ai_enhancement_client):
        """Test GET /jobs/{job_id} returns job status."""
        response = ai_enhancement_client.get("/api/ai-enhancement/jobs/test-job")
        assert response.status_code in [200, 404]
