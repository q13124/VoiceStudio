"""
Integration tests for Gateway Endpoint Mappings.

GAP-CRIT-001: Verifies that frontend gateway expected endpoints
match backend route implementations.

These tests ensure:
1. VoiceGateway endpoints are accessible
2. TimelineGateway endpoints are accessible
3. Response models match gateway expectations
"""

import pytest
from fastapi.testclient import TestClient

# Try to import the FastAPI app
try:
    from backend.api.main import app
    HAS_APP = True
except ImportError:
    HAS_APP = False
    app = None


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    if not HAS_APP:
        pytest.skip("FastAPI app not available")
    return TestClient(app)


class TestVoiceGatewayEndpoints:
    """Test endpoints expected by VoiceGateway."""

    def test_get_available_voices_endpoint_exists(self, client):
        """
        VoiceGateway.GetAvailableVoicesAsync expects GET /api/voice/voices.

        This should return a list of available voices.
        """
        response = client.get("/api/voice/voices")

        # Should not be 404 - endpoint must exist
        assert response.status_code != 404, (
            "Endpoint /api/voice/voices not found. "
            "VoiceGateway expects this endpoint to exist."
        )

        # Should be 200 or acceptable error (401 for auth, 503 for service unavailable)
        assert response.status_code in (200, 401, 503), (
            f"Unexpected status {response.status_code} from /api/voice/voices"
        )

    def test_get_voices_with_engine_filter(self, client):
        """
        VoiceGateway passes engine_id query parameter.
        """
        response = client.get("/api/voice/voices?engine_id=xtts")

        assert response.status_code != 404, (
            "Endpoint /api/voice/voices should accept engine_id parameter"
        )

    def test_voices_response_structure(self, client):
        """
        Verify response structure matches VoiceInfo model expectations.
        """
        response = client.get("/api/voice/voices")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Response should be a list of voices"

            # If voices exist, verify structure
            if data:
                voice = data[0]
                assert "id" in voice, "Voice should have 'id' field"
                assert "name" in voice, "Voice should have 'name' field"


class TestTimelineGatewayEndpoints:
    """Test endpoints expected by TimelineGateway."""

    @pytest.fixture
    def test_project_id(self):
        """Provide a test project ID."""
        return "test-project-001"

    def test_get_timeline_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.GetAsync expects GET /api/projects/{projectId}/timeline.

        This should return a TimelineDetail with tracks and markers.
        """
        response = client.get(f"/api/projects/{test_project_id}/timeline")

        assert response.status_code != 404, (
            f"Endpoint /api/projects/{test_project_id}/timeline not found. "
            "TimelineGateway expects this endpoint to exist."
        )

        assert response.status_code in (200, 401, 503), (
            f"Unexpected status {response.status_code} from timeline endpoint"
        )

    def test_timeline_response_structure(self, client, test_project_id):
        """
        Verify timeline response structure matches TimelineDetail expectations.
        """
        response = client.get(f"/api/projects/{test_project_id}/timeline")

        if response.status_code == 200:
            data = response.json()
            assert "project_id" in data, "Timeline should have 'project_id'"
            assert "tracks" in data, "Timeline should have 'tracks' array"
            assert "markers" in data, "Timeline should have 'markers' array"
            assert "duration_seconds" in data, "Timeline should have 'duration_seconds'"

    def test_add_track_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.AddTrackAsync expects POST /api/projects/{projectId}/timeline/tracks.
        """
        response = client.post(
            f"/api/projects/{test_project_id}/timeline/tracks",
            json={"name": "Test Track"}
        )

        assert response.status_code != 404, (
            "Endpoint POST /api/projects/{id}/timeline/tracks not found. "
            "TimelineGateway expects this endpoint to exist."
        )

        # Accept success, validation error, or auth error
        assert response.status_code in (200, 201, 400, 401, 422), (
            f"Unexpected status {response.status_code} from add track endpoint"
        )

    def test_delete_track_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.RemoveTrackAsync expects DELETE /api/projects/{id}/timeline/tracks/{trackId}.
        """
        response = client.delete(
            f"/api/projects/{test_project_id}/timeline/tracks/test-track-id"
        )

        assert response.status_code != 405, (
            "DELETE method not allowed on /api/projects/{id}/timeline/tracks/{trackId}"
        )

        # 404 is acceptable (track not found), but not 405 (method not allowed)
        assert response.status_code in (200, 204, 404, 401), (
            f"Unexpected status {response.status_code} from delete track endpoint"
        )

    def test_add_clip_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.AddClipAsync expects POST /api/projects/{id}/timeline/tracks/{trackId}/clips.
        """
        response = client.post(
            f"/api/projects/{test_project_id}/timeline/tracks/test-track/clips",
            json={
                "name": "Test Clip",
                "profile_id": "test-profile",
                "audio_id": "test-audio",
                "audio_url": "/audio/test.wav",
                "duration_seconds": 1.0,
                "start_time": 0.0
            }
        )

        assert response.status_code != 404, (
            "Endpoint POST /api/projects/{id}/timeline/tracks/{trackId}/clips not found"
        )

    def test_update_clip_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.UpdateClipAsync expects PUT /api/projects/{id}/timeline/tracks/{trackId}/clips/{clipId}.
        """
        response = client.put(
            f"/api/projects/{test_project_id}/timeline/tracks/test-track/clips/test-clip",
            json={"name": "Updated Clip"}
        )

        assert response.status_code != 405, (
            "PUT method not allowed on clips endpoint"
        )

    def test_delete_clip_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.RemoveClipAsync expects DELETE .../clips/{clipId}.
        """
        response = client.delete(
            f"/api/projects/{test_project_id}/timeline/tracks/test-track/clips/test-clip"
        )

        assert response.status_code != 405, (
            "DELETE method not allowed on clips endpoint"
        )

    def test_add_marker_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.AddMarkerAsync expects POST /api/projects/{id}/timeline/markers.
        """
        response = client.post(
            f"/api/projects/{test_project_id}/timeline/markers",
            json={"name": "Test Marker", "time_seconds": 5.0}
        )

        assert response.status_code != 404, (
            "Endpoint POST /api/projects/{id}/timeline/markers not found"
        )

    def test_delete_marker_endpoint_exists(self, client, test_project_id):
        """
        TimelineGateway.RemoveMarkerAsync expects DELETE /api/projects/{id}/timeline/markers/{markerId}.
        """
        response = client.delete(
            f"/api/projects/{test_project_id}/timeline/markers/test-marker-id"
        )

        assert response.status_code != 405, (
            "DELETE method not allowed on markers endpoint"
        )


class TestEndpointCompatibility:
    """Cross-validation tests for endpoint naming consistency."""

    def test_voice_browser_original_endpoint_still_works(self, client):
        """
        Original /api/voice-browser/voices should still work.
        """
        response = client.get("/api/voice-browser/voices")

        # Should not be 404
        assert response.status_code != 404, (
            "Original voice-browser endpoint should still exist"
        )

    def test_tracks_original_endpoint_still_works(self, client):
        """
        Original /api/projects/{id}/tracks should still work.
        """
        response = client.get("/api/projects/test-project/tracks")

        # Should not be 404
        assert response.status_code != 404, (
            "Original tracks endpoint should still exist"
        )
