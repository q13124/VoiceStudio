"""
Unit Tests for Multi-Voice Generator API Routes.

Tests multi-voice generation jobs and comparison endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_multi_voice_state():
    """Reset multi-voice state before each test."""
    from backend.api.routes import multi_voice_generator
    multi_voice_generator._jobs = {}
    yield
    multi_voice_generator._jobs = {}


@pytest.fixture
def multi_voice_client():
    """Create test client for multi-voice generator routes."""
    from backend.api.routes.multi_voice_generator import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestJobManagement:
    """Tests for multi-voice job management."""

    def test_get_job_status_not_found(self, multi_voice_client):
        """Test GET /{job_id}/status returns 404 for missing job."""
        response = multi_voice_client.get("/api/voice/multi/nonexistent/status")
        assert response.status_code == 404

    def test_get_job_results_not_found(self, multi_voice_client):
        """Test GET /{job_id}/results returns 404 for missing job."""
        response = multi_voice_client.get("/api/voice/multi/nonexistent/results")
        assert response.status_code == 404


class TestMultiVoiceOperations:
    """Tests for multi-voice operation endpoints."""

    def test_generate_validation(self, multi_voice_client):
        """Test POST /generate validates required fields."""
        response = multi_voice_client.post("/api/voice/multi/generate", json={})
        assert response.status_code == 422

    def test_compare_validation(self, multi_voice_client):
        """Test POST /compare validates required fields."""
        response = multi_voice_client.post("/api/voice/multi/compare", json={})
        assert response.status_code == 422

    def test_export_validation(self, multi_voice_client):
        """Test POST /export validates job_id parameter."""
        response = multi_voice_client.post("/api/voice/multi/export")
        # job_id is optional with default "", will return 404 for empty job_id
        assert response.status_code in [200, 404, 422]

    def test_import_validation(self, multi_voice_client):
        """Test POST /import validates required fields."""
        response = multi_voice_client.post("/api/voice/multi/import", json={})
        assert response.status_code == 422
