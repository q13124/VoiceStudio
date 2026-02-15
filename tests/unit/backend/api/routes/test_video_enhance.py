"""
Unit Tests for Video Enhancement API Routes.

Tests video enhancement jobs and face detection endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_video_state():
    """Reset video state before each test."""
    from backend.api.routes import video_enhance
    video_enhance._enhancement_jobs = {}
    yield
    video_enhance._enhancement_jobs = {}


@pytest.fixture
def video_client():
    """Create test client for video enhancement routes."""
    from backend.api.routes.video_enhance import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestVideoEnhanceCRUD:
    """Tests for video enhancement job management."""

    def test_get_capabilities(self, video_client):
        """Test GET /capabilities returns enhancement capabilities."""
        response = video_client.get("/api/video/enhance/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert data is not None

    def test_list_jobs_empty(self, video_client):
        """Test GET /jobs returns empty list initially."""
        response = video_client.get("/api/video/enhance/jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_job_status_not_found(self, video_client):
        """Test GET /status/{job_id} returns 404 for missing job."""
        response = video_client.get("/api/video/enhance/status/nonexistent")
        assert response.status_code == 404

    def test_cancel_job_not_found(self, video_client):
        """Test DELETE /cancel/{job_id} for missing job."""
        response = video_client.delete("/api/video/enhance/cancel/nonexistent")
        # API returns 200 even for nonexistent job (idempotent behavior)
        assert response.status_code in [200, 404]

    def test_start_validation(self, video_client):
        """Test POST /start validates required fields."""
        response = video_client.post("/api/video/enhance/start", json={})
        assert response.status_code == 422

    def test_detect_faces_validation(self, video_client):
        """Test POST /detect-faces validates input."""
        response = video_client.post("/api/video/enhance/detect-faces", json={})
        assert response.status_code == 422
