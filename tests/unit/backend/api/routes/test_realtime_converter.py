"""
Unit Tests for Real-Time Converter API Routes.

Tests real-time voice conversion sessions and streaming endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_converter_state():
    """Reset converter state and cache before each test."""
    from backend.api.routes import realtime_converter
    from backend.api import optimization
    
    realtime_converter._converter_sessions = {}
    optimization._RESPONSE_CACHE.clear()  # Clear module-level cache
    yield
    realtime_converter._converter_sessions = {}
    optimization._RESPONSE_CACHE.clear()


@pytest.fixture
def converter_client():
    """Create test client for realtime converter routes."""
    from backend.api.routes.realtime_converter import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_start_request():
    """Sample converter start request data."""
    return {
        "source_profile_id": "profile-source-123",
        "target_profile_id": "profile-target-456",
    }


# =============================================================================
# Session Management Tests
# =============================================================================


class TestSessionManagement:
    """Tests for converter session CRUD operations."""

    def test_start_session(self, converter_client, sample_start_request):
        """Test POST /start creates a new session."""
        response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"].startswith("session-")
        assert "message" in data

    def test_list_sessions_empty(self, converter_client):
        """Test GET / returns empty list initially."""
        response = converter_client.get("/api/realtime-converter")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert data["sessions"] == []

    def test_session_retrievable_after_start(self, converter_client, sample_start_request):
        """Test session is retrievable via GET /{id} after creation."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]

        # Verify session is retrievable via direct GET (avoids cache issues with list)
        get_response = converter_client.get(f"/api/realtime-converter/{session_id}")
        assert get_response.status_code == 200
        assert get_response.json()["session_id"] == session_id
        assert get_response.json()["source_profile_id"] == sample_start_request["source_profile_id"]

    def test_get_session(self, converter_client, sample_start_request):
        """Test GET /{session_id} returns session details."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Get session
        response = converter_client.get(f"/api/realtime-converter/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["source_profile_id"] == sample_start_request["source_profile_id"]
        assert data["target_profile_id"] == sample_start_request["target_profile_id"]
        assert data["status"] == "active"

    def test_get_session_not_found(self, converter_client):
        """Test GET /{session_id} returns 404 for missing session."""
        response = converter_client.get("/api/realtime-converter/nonexistent-session")
        assert response.status_code == 404

    def test_delete_session(self, converter_client, sample_start_request):
        """Test DELETE /{session_id} removes session."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Delete session
        delete_response = converter_client.delete(f"/api/realtime-converter/{session_id}")
        assert delete_response.status_code == 200

        # Verify it's gone
        get_response = converter_client.get(f"/api/realtime-converter/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, converter_client):
        """Test DELETE /{session_id} returns 404 for missing session."""
        response = converter_client.delete("/api/realtime-converter/nonexistent-session")
        assert response.status_code == 404


# =============================================================================
# Session Control Tests
# =============================================================================


class TestSessionControl:
    """Tests for session pause/resume/stop operations."""

    def test_pause_session(self, converter_client, sample_start_request):
        """Test POST /{session_id}/pause pauses session."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Pause session
        pause_response = converter_client.post(f"/api/realtime-converter/{session_id}/pause")
        assert pause_response.status_code == 200

        # Verify status
        get_response = converter_client.get(f"/api/realtime-converter/{session_id}")
        assert get_response.json()["status"] == "paused"

    def test_resume_session(self, converter_client, sample_start_request):
        """Test POST /{session_id}/resume resumes paused session."""
        # Start and pause a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]
        converter_client.post(f"/api/realtime-converter/{session_id}/pause")

        # Resume session
        resume_response = converter_client.post(f"/api/realtime-converter/{session_id}/resume")
        assert resume_response.status_code == 200

        # Verify status
        get_response = converter_client.get(f"/api/realtime-converter/{session_id}")
        assert get_response.json()["status"] == "active"

    def test_stop_session(self, converter_client, sample_start_request):
        """Test POST /{session_id}/stop stops session."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Stop session
        stop_response = converter_client.post(f"/api/realtime-converter/{session_id}/stop")
        assert stop_response.status_code == 200

        # Verify status
        get_response = converter_client.get(f"/api/realtime-converter/{session_id}")
        assert get_response.json()["status"] == "stopped"

    def test_pause_nonexistent_session(self, converter_client):
        """Test POST /{session_id}/pause returns 404 for missing session."""
        response = converter_client.post("/api/realtime-converter/nonexistent/pause")
        assert response.status_code == 404

    def test_resume_nonexistent_session(self, converter_client):
        """Test POST /{session_id}/resume returns 404 for missing session."""
        response = converter_client.post("/api/realtime-converter/nonexistent/resume")
        assert response.status_code == 404

    def test_stop_nonexistent_session(self, converter_client):
        """Test POST /{session_id}/stop returns 404 for missing session."""
        response = converter_client.post("/api/realtime-converter/nonexistent/stop")
        assert response.status_code == 404


# =============================================================================
# Metrics Tests
# =============================================================================


class TestSessionMetrics:
    """Tests for session metrics endpoints."""

    def test_get_latency(self, converter_client, sample_start_request):
        """Test GET /{session_id}/latency returns latency info."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Get latency
        response = converter_client.get(f"/api/realtime-converter/{session_id}/latency")
        assert response.status_code == 200
        data = response.json()
        assert "latency_ms" in data or "session_id" in data

    def test_get_latency_for_any_session_id(self, converter_client):
        """Test GET /{session_id}/latency returns stub data for any session_id."""
        # Note: Endpoint returns stub data without validating session existence
        response = converter_client.get("/api/realtime-converter/any-session-id/latency")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "any-session-id"
        assert "latency_ms" in data

    def test_get_quality(self, converter_client, sample_start_request):
        """Test GET /{session_id}/quality returns quality metrics."""
        # Start a session
        start_response = converter_client.post(
            "/api/realtime-converter/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Get quality
        response = converter_client.get(f"/api/realtime-converter/{session_id}/quality")
        assert response.status_code == 200
        data = response.json()
        assert data is not None

    def test_get_quality_for_any_session_id(self, converter_client):
        """Test GET /{session_id}/quality returns stub data for any session_id."""
        # Note: Endpoint returns stub data without validating session existence
        response = converter_client.get("/api/realtime-converter/any-session-id/quality")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "any-session-id"
        assert "overall_score" in data
