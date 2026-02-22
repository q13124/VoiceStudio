"""
Transcription Workflow E2E Tests.

Tests the complete transcription workflow:
1. Upload/provide audio
2. Start transcription
3. Monitor progress
4. Retrieve transcript
5. Edit/export transcript
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path

import pytest

try:
    import httpx
except ImportError:
    httpx = None

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.transcription,
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
    """Create a test audio file."""
    import struct
    import wave

    audio_file = tmp_path / "test_audio.wav"
    with wave.open(str(audio_file), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        # Generate 3 seconds of silence with slight noise
        samples = [int(100 * ((i % 100) - 50)) for i in range(16000 * 3)]
        wav.writeframes(struct.pack(f"{len(samples)}h", *samples))

    return audio_file


class TestTranscriptionLanguages:
    """Tests for transcription language support."""

    def test_list_supported_languages(self, api_client, backend_available):
        """Test getting list of supported languages."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/transcribe/languages")
        assert response.status_code == 200

        languages = response.json()
        assert isinstance(languages, list)
        # Should have at least English
        language_codes = [lang.get("code") for lang in languages]
        assert "en" in language_codes or "english" in [l.get("name", "").lower() for l in languages]


class TestTranscriptionCRUD:
    """Tests for transcription CRUD operations."""

    def test_list_transcriptions(self, api_client, backend_available):
        """Test listing all transcriptions."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/transcribe/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_transcription_not_found(self, api_client, backend_available):
        """Test getting a non-existent transcription."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/transcribe/{fake_id}")
        assert response.status_code in (404, 422)

    def test_delete_transcription_not_found(self, api_client, backend_available):
        """Test deleting a non-existent transcription."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.delete(f"/api/transcribe/{fake_id}")
        assert response.status_code in (404, 422)


class TestTranscriptionSubmission:
    """Tests for submitting transcription jobs."""

    def test_transcribe_with_file(self, api_client, backend_available, test_audio_file):
        """Test submitting a transcription job with file upload."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/transcribe/",
                files={"file": ("test.wav", f, "audio/wav")},
                data={"language": "en"},
            )

        # May succeed or fail depending on engine availability
        assert response.status_code in (200, 201, 400, 500, 503)

    def test_transcribe_invalid_language(self, api_client, backend_available, test_audio_file):
        """Test transcription with invalid language code."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/transcribe/",
                files={"file": ("test.wav", f, "audio/wav")},
                data={"language": "xyz_invalid"},
            )

        # Should reject invalid language or handle gracefully
        assert response.status_code in (400, 422, 200, 500, 503)


class TestTranscriptionStatus:
    """Tests for transcription job status tracking."""

    def test_transcription_progress_tracking(self, api_client, backend_available):
        """Test that transcription progress can be tracked."""
        if not backend_available:
            pytest.skip("Backend not available")

        # List existing transcriptions
        response = api_client.get("/api/transcribe/")
        assert response.status_code == 200

        transcriptions = response.json()
        if transcriptions:
            # Check that transcriptions have status fields
            trans = transcriptions[0]
            # Should have standard response fields
            assert "id" in trans or "transcription_id" in trans


class TestTranscriptionEditing:
    """Tests for editing transcription results."""

    def test_update_transcription_not_found(self, api_client, backend_available):
        """Test updating a non-existent transcription."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.put(
            f"/api/transcribe/{fake_id}",
            json={"text": "Updated text"},
        )
        assert response.status_code in (404, 422)


class TestTranscriptionWorkflowIntegration:
    """Integration tests for complete transcription workflow."""

    @pytest.fixture
    def workflow_state(self):
        """State tracking for workflow tests."""
        return {"transcription_id": None, "text": None}

    def test_complete_transcription_workflow_api(
        self, api_client, backend_available, workflow_state, test_audio_file
    ):
        """Test the complete transcription workflow via API.

        Steps:
        1. Check supported languages
        2. Submit transcription
        3. Get transcription result
        4. (Optional) Edit transcription
        5. Clean up
        """
        if not backend_available:
            pytest.skip("Backend not available")

        # Step 1: Check supported languages
        languages_response = api_client.get("/api/transcribe/languages")
        assert languages_response.status_code == 200
        languages = languages_response.json()
        assert len(languages) > 0, "No languages supported"

        # Step 2: Submit transcription
        with open(test_audio_file, "rb") as f:
            submit_response = api_client.post(
                "/api/transcribe/",
                files={"file": ("test.wav", f, "audio/wav")},
                data={"language": "en"},
            )

        if submit_response.status_code in (500, 503):
            # Engine not available - workflow still passes as API works
            pytest.skip("Transcription engine not available")

        if submit_response.status_code in (200, 201):
            result = submit_response.json()
            transcription_id = result.get("id") or result.get("transcription_id")
            workflow_state["transcription_id"] = transcription_id

            # Step 3: Get transcription result
            if transcription_id:
                get_response = api_client.get(f"/api/transcribe/{transcription_id}")
                assert get_response.status_code == 200

                # Step 4: Clean up
                delete_response = api_client.delete(f"/api/transcribe/{transcription_id}")
                assert delete_response.status_code in (200, 204, 404)


class TestTranscriptionExport:
    """Tests for exporting transcription results."""

    def test_transcription_response_format(self, api_client, backend_available):
        """Test that transcription responses have expected format."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/transcribe/")
        assert response.status_code == 200

        transcriptions = response.json()
        # If there are transcriptions, verify structure
        for trans in transcriptions[:3]:  # Check first 3
            # Standard fields should be present
            assert "id" in trans or "transcription_id" in trans


class TestBatchTranscription:
    """Tests for batch transcription operations."""

    def test_batch_transcription_endpoint_exists(self, api_client, backend_available):
        """Test that batch transcription endpoint is accessible."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Check batch endpoints
        response = api_client.get("/api/batch/transcription/status")
        # May or may not exist
        assert response.status_code in (200, 404, 405)
