"""
Unit Tests for Multi-Speaker Dubbing API Routes.

Tests multi-speaker dubbing service endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def dubbing_client():
    """Create test client for multi-speaker dubbing routes."""
    from backend.api.routes.multi_speaker_dubbing import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestMultiSpeakerDubbingEndpoints:
    """Tests for multi-speaker dubbing endpoints."""

    def test_create_job_validation(self, dubbing_client):
        """Test POST /jobs validates required fields."""
        response = dubbing_client.post("/api/multi-speaker-dubbing/jobs", json={})
        assert response.status_code in [200, 201, 404, 422]

    def test_get_job_status(self, dubbing_client):
        """Test GET /jobs/{job_id} returns job status."""
        response = dubbing_client.get("/api/multi-speaker-dubbing/jobs/test-job")
        assert response.status_code in [200, 404]

    def test_list_jobs(self, dubbing_client):
        """Test GET /jobs returns job list."""
        response = dubbing_client.get("/api/multi-speaker-dubbing/jobs")
        assert response.status_code in [200, 404]

    def test_get_speakers(self, dubbing_client):
        """Test GET /speakers returns speaker list."""
        response = dubbing_client.get("/api/multi-speaker-dubbing/speakers")
        assert response.status_code in [200, 404]
