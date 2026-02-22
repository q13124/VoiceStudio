"""
Unit Tests for Face Swap API Routes (Arch Review 1.4).

Tests face swap creation jobs and engine management.
Replaces test_deepfake_creator.py.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def enable_face_swap(monkeypatch):
    """Enable face swap feature flag for tests."""
    monkeypatch.setattr("backend.api.routes.face_swap.is_enabled", lambda flag: True)


@pytest.fixture(autouse=True)
def reset_face_swap_state():
    """Reset face swap state before each test."""
    from backend.api.routes import face_swap

    face_swap._jobs.clear()
    face_swap._job_queue.clear()
    face_swap._processing_jobs.clear()
    yield
    face_swap._jobs.clear()
    face_swap._job_queue.clear()
    face_swap._processing_jobs.clear()


@pytest.fixture
def face_swap_client():
    """Create test client for face swap routes."""
    from backend.api.routes.face_swap import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def deepfake_alias_client():
    """Create test client for backward-compat deepfake-creator alias."""
    from backend.api.routes.face_swap import deepfake_alias_router

    app = FastAPI()
    app.include_router(deepfake_alias_router)
    return TestClient(app)


class TestFaceSwapCRUD:
    """Tests for face swap job management."""

    def test_get_engines(self, face_swap_client):
        """Test GET /engines returns available engines."""
        response = face_swap_client.get("/api/face-swap/engines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_queue_status(self, face_swap_client):
        """Test GET /queue/status returns queue state."""
        response = face_swap_client.get("/api/face-swap/queue/status")
        assert response.status_code == 200
        data = response.json()
        assert data is not None

    def test_list_jobs_empty(self, face_swap_client):
        """Test GET /jobs returns empty list initially."""
        response = face_swap_client.get("/api/face-swap/jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_job_not_found(self, face_swap_client):
        """Test GET /jobs/{job_id} returns 404 for missing job."""
        response = face_swap_client.get("/api/face-swap/jobs/nonexistent")
        assert response.status_code == 404

    def test_delete_job_not_found(self, face_swap_client):
        """Test DELETE /jobs/{job_id} returns 404 for missing job."""
        response = face_swap_client.delete("/api/face-swap/jobs/nonexistent")
        assert response.status_code == 404

    def test_create_validation(self, face_swap_client):
        """Test POST /create validates required fields."""
        response = face_swap_client.post("/api/face-swap/create", json={})
        assert response.status_code == 422


class TestDeepfakeAlias:
    """Tests for backward-compat /api/deepfake-creator alias."""

    def test_get_engines(self, deepfake_alias_client):
        """Test GET /engines via alias."""
        response = deepfake_alias_client.get("/api/deepfake-creator/engines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_jobs_empty(self, deepfake_alias_client):
        """Test GET /jobs via alias."""
        response = deepfake_alias_client.get("/api/deepfake-creator/jobs")
        assert response.status_code == 200
        assert response.json() == []
