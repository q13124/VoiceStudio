"""
Unit Tests for Deepfake Creator API Routes.

Tests deepfake creation jobs and engine management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_deepfake_state():
    """Reset deepfake state before each test."""
    from backend.api.routes import deepfake_creator

    deepfake_creator._deepfake_jobs = {}
    yield
    deepfake_creator._deepfake_jobs = {}


@pytest.fixture
def deepfake_client():
    """Create test client for deepfake creator routes."""
    from backend.api.routes.deepfake_creator import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestDeepfakeCRUD:
    """Tests for deepfake job management."""

    def test_get_engines(self, deepfake_client):
        """Test GET /engines returns available engines."""
        response = deepfake_client.get("/api/deepfake-creator/engines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_queue_status(self, deepfake_client):
        """Test GET /queue/status returns queue state."""
        response = deepfake_client.get("/api/deepfake-creator/queue/status")
        assert response.status_code == 200
        data = response.json()
        assert data is not None

    def test_list_jobs_empty(self, deepfake_client):
        """Test GET /jobs returns empty list initially."""
        response = deepfake_client.get("/api/deepfake-creator/jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_job_not_found(self, deepfake_client):
        """Test GET /jobs/{job_id} returns 404 for missing job."""
        response = deepfake_client.get("/api/deepfake-creator/jobs/nonexistent")
        assert response.status_code == 404

    def test_delete_job_not_found(self, deepfake_client):
        """Test DELETE /jobs/{job_id} returns 404 for missing job."""
        response = deepfake_client.delete("/api/deepfake-creator/jobs/nonexistent")
        assert response.status_code == 404

    def test_create_validation(self, deepfake_client):
        """Test POST /create validates required fields."""
        response = deepfake_client.post("/api/deepfake-creator/create", json={})
        assert response.status_code == 422
