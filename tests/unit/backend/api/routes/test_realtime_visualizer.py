"""
Unit Tests for Real-Time Visualizer API Routes.

Tests real-time audio visualization session management.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_visualizer_state():
    """Reset visualizer state before each test."""
    from backend.api.routes import realtime_visualizer
    realtime_visualizer._visualizer_sessions = {}
    yield
    realtime_visualizer._visualizer_sessions = {}


@pytest.fixture
def visualizer_client():
    """Create test client for realtime visualizer routes."""
    from backend.api.routes.realtime_visualizer import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_start_request():
    """Sample visualizer start request data."""
    return {
        "visualization_type": "both",
        "update_rate": 30.0,
        "fft_size": 2048,
        "window_type": "hann",
        "show_phase": False,
        "color_scheme": "default",
    }


# =============================================================================
# Session Management Tests
# =============================================================================


class TestSessionManagement:
    """Tests for visualizer session CRUD operations."""

    def test_start_session(self, visualizer_client, sample_start_request):
        """Test POST /start creates a new visualizer session."""
        response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json=sample_start_request,
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"].startswith("viz-")
        assert "message" in data

    def test_start_session_minimal(self, visualizer_client):
        """Test POST /start works with minimal data (defaults)."""
        response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data

    def test_get_session(self, visualizer_client, sample_start_request):
        """Test GET /{session_id} returns session config."""
        # Start a session
        start_response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Get session
        response = visualizer_client.get(f"/api/realtime-visualizer/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["visualization_type"] == sample_start_request["visualization_type"]
        assert data["fft_size"] == sample_start_request["fft_size"]

    def test_get_session_not_found(self, visualizer_client):
        """Test GET /{session_id} returns 404 for missing session."""
        response = visualizer_client.get("/api/realtime-visualizer/nonexistent-session")
        assert response.status_code == 404

    def test_stop_session(self, visualizer_client, sample_start_request):
        """Test POST /{session_id}/stop stops visualizer session."""
        # Start a session
        start_response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Stop session
        stop_response = visualizer_client.post(f"/api/realtime-visualizer/{session_id}/stop")
        assert stop_response.status_code == 200

    def test_stop_session_not_found(self, visualizer_client):
        """Test POST /{session_id}/stop returns 404 for missing session."""
        response = visualizer_client.post("/api/realtime-visualizer/nonexistent/stop")
        assert response.status_code == 404

    def test_delete_session(self, visualizer_client, sample_start_request):
        """Test DELETE /{session_id} removes session."""
        # Start a session
        start_response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json=sample_start_request,
        )
        session_id = start_response.json()["session_id"]

        # Delete session
        delete_response = visualizer_client.delete(f"/api/realtime-visualizer/{session_id}")
        assert delete_response.status_code == 200

        # Verify it's gone
        get_response = visualizer_client.get(f"/api/realtime-visualizer/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, visualizer_client):
        """Test DELETE /{session_id} returns 404 for missing session."""
        response = visualizer_client.delete("/api/realtime-visualizer/nonexistent")
        assert response.status_code == 404


# =============================================================================
# Configuration Tests
# =============================================================================


class TestVisualizerConfig:
    """Tests for visualizer configuration options."""

    def test_waveform_visualization(self, visualizer_client):
        """Test starting waveform-only visualization."""
        response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json={"visualization_type": "waveform"},
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        config = visualizer_client.get(f"/api/realtime-visualizer/{session_id}")
        assert config.json()["visualization_type"] == "waveform"

    def test_spectrogram_visualization(self, visualizer_client):
        """Test starting spectrogram visualization."""
        response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json={"visualization_type": "spectrogram"},
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        config = visualizer_client.get(f"/api/realtime-visualizer/{session_id}")
        assert config.json()["visualization_type"] == "spectrogram"

    def test_custom_fft_size(self, visualizer_client):
        """Test custom FFT size configuration."""
        response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json={"fft_size": 4096},
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        config = visualizer_client.get(f"/api/realtime-visualizer/{session_id}")
        assert config.json()["fft_size"] == 4096

    def test_custom_update_rate(self, visualizer_client):
        """Test custom update rate configuration."""
        response = visualizer_client.post(
            "/api/realtime-visualizer/start",
            json={"update_rate": 60.0},
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        config = visualizer_client.get(f"/api/realtime-visualizer/{session_id}")
        assert config.json()["update_rate"] == 60.0
