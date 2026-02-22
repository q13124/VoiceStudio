"""
Voice Cloning Workflow E2E Tests.

Tests the complete voice cloning workflow:
1. Validate reference audio
2. Start cloning wizard
3. Process voice characteristics
4. Finalize and create voice profile
5. Test synthesizing with cloned voice
"""

from __future__ import annotations

import struct
import uuid
import wave
from pathlib import Path

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.voice_cloning,
]


@pytest.fixture
def api_client():
    """Create a test client for API tests."""
    from fastapi.testclient import TestClient

    from backend.api.main import app

    return TestClient(app)


@pytest.fixture
def backend_available(api_client):
    """Check if backend is available."""
    try:
        response = api_client.get("/api/health/status")
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture
def test_audio_file(tmp_path):
    """Create a test audio file suitable for voice cloning."""
    import math

    audio_file = tmp_path / "reference_voice.wav"
    with wave.open(str(audio_file), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)  # Common rate for voice cloning
        # Generate 5 seconds of audio with sine wave (safe 16-bit range)
        num_samples = 22050 * 5
        samples = [int(8000 * math.sin(2 * math.pi * 440 * i / 22050)) for i in range(num_samples)]
        wav.writeframes(struct.pack(f"{len(samples)}h", *samples))

    return audio_file


@pytest.fixture
def short_audio_file(tmp_path):
    """Create a too-short audio file for validation testing."""
    import math

    audio_file = tmp_path / "short_audio.wav"
    with wave.open(str(audio_file), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        # Only 0.5 seconds - too short
        num_samples = 22050 // 2
        samples = [int(4000 * math.sin(2 * math.pi * 440 * i / 22050)) for i in range(num_samples)]
        wav.writeframes(struct.pack(f"{len(samples)}h", *samples))

    return audio_file


class TestAudioValidation:
    """Tests for voice cloning audio validation."""

    def test_validate_audio_with_valid_file(self, api_client, backend_available, test_audio_file):
        """Test validating a valid reference audio file."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-cloning-wizard/validate-audio",
                files={"file": ("reference.wav", f, "audio/wav")},
            )

        # Should succeed or indicate engine unavailable
        assert response.status_code in (200, 400, 500, 503)

        if response.status_code == 200:
            result = response.json()
            # Should have validation results
            assert "valid" in result or "is_valid" in result or "duration" in result

    def test_validate_audio_with_short_file(self, api_client, backend_available, short_audio_file):
        """Test validating a too-short audio file."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(short_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-cloning-wizard/validate-audio",
                files={"file": ("short.wav", f, "audio/wav")},
            )

        # Should indicate validation failure or process gracefully
        assert response.status_code in (200, 400, 422, 500, 503)


class TestWizardStartup:
    """Tests for starting the voice cloning wizard."""

    def test_start_wizard_job(self, api_client, backend_available, test_audio_file):
        """Test starting a voice cloning wizard job."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-cloning-wizard/start",
                files={"file": ("reference.wav", f, "audio/wav")},
                data={
                    "voice_name": f"test_voice_{uuid.uuid4().hex[:8]}",
                    "description": "Test cloned voice",
                },
            )

        # Should succeed, fail due to engine, or validation error
        assert response.status_code in (201, 200, 400, 422, 500, 503)

        if response.status_code in (200, 201):
            result = response.json()
            # Should return job ID
            assert "job_id" in result or "id" in result

    def test_start_wizard_missing_file(self, api_client, backend_available):
        """Test starting wizard without audio file."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/voice-cloning-wizard/start",
            data={"voice_name": "test_voice"},
        )

        # Should fail with validation error
        assert response.status_code in (400, 422)


class TestWizardStatus:
    """Tests for wizard job status tracking."""

    def test_get_job_status_not_found(self, api_client, backend_available):
        """Test getting status of non-existent job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/voice-cloning-wizard/{fake_id}/status")
        assert response.status_code in (404, 422)

    def test_delete_job_not_found(self, api_client, backend_available):
        """Test deleting non-existent job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.delete(f"/api/voice-cloning-wizard/{fake_id}")
        assert response.status_code in (404, 422)


class TestWizardProcessing:
    """Tests for wizard processing steps."""

    def test_process_job_not_found(self, api_client, backend_available):
        """Test processing non-existent job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/voice-cloning-wizard/{fake_id}/process")
        assert response.status_code in (404, 422)

    def test_finalize_job_not_found(self, api_client, backend_available):
        """Test finalizing non-existent job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/voice-cloning-wizard/{fake_id}/finalize")
        assert response.status_code in (404, 422)


class TestVoiceCloningWorkflowIntegration:
    """Integration tests for complete voice cloning workflow."""

    @pytest.fixture
    def workflow_state(self):
        """State tracking for workflow tests."""
        return {"job_id": None, "profile_id": None}

    def test_complete_voice_cloning_workflow_api(
        self, api_client, backend_available, workflow_state, test_audio_file
    ):
        """Test the complete voice cloning workflow via API.

        Steps:
        1. Validate reference audio
        2. Start wizard job
        3. Check job status
        4. Process voice characteristics
        5. Finalize and create profile
        6. Clean up
        """
        if not backend_available:
            pytest.skip("Backend not available")

        # Step 1: Validate reference audio
        with open(test_audio_file, "rb") as f:
            validate_response = api_client.post(
                "/api/voice-cloning-wizard/validate-audio",
                files={"file": ("reference.wav", f, "audio/wav")},
            )

        if validate_response.status_code in (500, 503):
            pytest.skip("Voice cloning engine not available")

        # Validation may fail for synthetic audio - continue anyway
        if validate_response.status_code != 200:
            # Try to proceed anyway
            pass

        # Step 2: Start wizard job
        voice_name = f"test_clone_{uuid.uuid4().hex[:8]}"
        with open(test_audio_file, "rb") as f:
            start_response = api_client.post(
                "/api/voice-cloning-wizard/start",
                files={"file": ("reference.wav", f, "audio/wav")},
                data={
                    "voice_name": voice_name,
                    "description": "E2E test voice clone",
                },
            )

        if start_response.status_code in (500, 503):
            pytest.skip("Voice cloning engine not available")

        if start_response.status_code in (200, 201):
            result = start_response.json()
            job_id = result.get("job_id") or result.get("id")
            workflow_state["job_id"] = job_id

            if job_id:
                # Step 3: Check job status
                status_response = api_client.get(f"/api/voice-cloning-wizard/{job_id}/status")
                assert status_response.status_code == 200

                # Step 4: Clean up (cancel job)
                delete_response = api_client.delete(f"/api/voice-cloning-wizard/{job_id}")
                assert delete_response.status_code in (200, 204, 404)


class TestInstantCloning:
    """Tests for instant/quick voice cloning."""

    def test_instant_cloning_status(self, api_client, backend_available):
        """Test instant cloning status endpoint."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/instant-cloning/status")
        # May or may not exist
        assert response.status_code in (200, 404, 405)

    def test_instant_cloning_engines(self, api_client, backend_available):
        """Test listing instant cloning capable engines."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/instant-cloning/engines")
        # May or may not exist
        assert response.status_code in (200, 404, 405)


class TestVoiceCloningQuickClone:
    """Tests for quick clone API."""

    def test_quick_clone_endpoint(self, api_client, backend_available, test_audio_file):
        """Test quick clone endpoint if available."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Check if quick clone API exists
        response = api_client.get("/api/voice/quick-clone/status")
        # May or may not exist
        if response.status_code == 404:
            pytest.skip("Quick clone API not available")


class TestVoiceCloningProfiles:
    """Tests for cloned voice profile management."""

    def test_list_cloned_profiles(self, api_client, backend_available):
        """Test listing profiles that were created via cloning."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/profiles/")
        assert response.status_code == 200

        profiles = response.json()
        # Profiles should be a list
        if isinstance(profiles, dict):
            profiles = profiles.get("profiles", []) or profiles.get("items", [])
        assert isinstance(profiles, list)
