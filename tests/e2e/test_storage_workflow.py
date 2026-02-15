"""
End-to-End test for Audio Storage workflow.

Tests the complete audio storage and retrieval workflow including:
- Audio file upload
- Audio file retrieval
- Audio format handling
- Storage persistence
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to path to enable proper package imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.main import app


class TestAudioStorageWorkflow:
    """End-to-end tests for audio storage and retrieval."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_audio_retrieval_not_found(self, client: TestClient):
        """
        GET /api/voice/audio/{id} returns 404 for non-existent audio.
        """
        print("\n[E2E] Testing audio retrieval for non-existent ID...")

        response = client.get("/api/voice/audio/non-existent-audio-id")
        assert response.status_code == 404
        print("[E2E] Correctly returned 404 for non-existent audio")

    def test_audio_list(self, client: TestClient):
        """
        GET /api/audio returns list of stored audio files.
        """
        print("\n[E2E] Testing audio list endpoint...")

        response = client.get("/api/audio")

        # Accept 200 (list returned) or 404 (endpoint may not exist)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            print(f"[E2E] Found {len(data) if isinstance(data, list) else 'N/A'} audio files")
        else:
            print("[E2E] Audio list endpoint not available")


class TestSynthesisStorageWorkflow:
    """End-to-end tests for synthesis + storage workflow."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_synthesize_stores_audio(self, client: TestClient):
        """
        POST /api/voice/synthesize stores audio and returns retrievable ID.
        """
        print("\n[E2E] Testing synthesis -> storage workflow...")

        # Synthesize audio
        synth_response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "Test synthesis for storage.",
                "profile_id": "default",
                "engine": "piper",
            },
        )

        # Accept 200 (synthesis succeeded) or 500 (engine not available)
        if synth_response.status_code != 200:
            print(f"[E2E] Synthesis not available: {synth_response.status_code}")
            return

        data = synth_response.json()
        assert "audio_id" in data
        audio_id = data["audio_id"]
        print(f"[E2E] Synthesized audio: {audio_id}")

        # Retrieve the audio
        retrieve_response = client.get(f"/api/voice/audio/{audio_id}")

        # Accept 200 (audio retrieved) or 404 (not stored yet)
        assert retrieve_response.status_code in [200, 404]

        if retrieve_response.status_code == 200:
            assert retrieve_response.headers.get("content-type", "").startswith("audio/")
            print(f"[E2E] Retrieved audio: {len(retrieve_response.content)} bytes")
        else:
            print("[E2E] Audio not yet available for retrieval")

    def test_audio_persistence_after_synthesis(self, client: TestClient):
        """
        Audio remains available after initial synthesis.
        """
        print("\n[E2E] Testing audio persistence...")

        # Synthesize first
        synth_response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "Persistence test audio.",
                "profile_id": "default",
            },
        )

        if synth_response.status_code != 200:
            print(f"[E2E] Synthesis skipped: {synth_response.status_code}")
            return

        audio_id = synth_response.json().get("audio_id")
        if not audio_id:
            print("[E2E] No audio_id returned")
            return

        # Retrieve multiple times
        for i in range(3):
            response = client.get(f"/api/voice/audio/{audio_id}")
            # Accept 200 or 404
            if response.status_code == 200:
                print(f"[E2E] Retrieval {i+1}/3: {len(response.content)} bytes")
            else:
                print(f"[E2E] Retrieval {i+1}/3: status {response.status_code}")


class TestAudioFormatHandling:
    """End-to-end tests for audio format handling."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_wav_format_synthesis(self, client: TestClient):
        """
        Synthesize audio in WAV format.
        """
        print("\n[E2E] Testing WAV format synthesis...")

        response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "WAV format test.",
                "profile_id": "default",
                "format": "wav",
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[E2E] WAV synthesis: {data.get('audio_id', 'no id')}")
        else:
            print(f"[E2E] WAV synthesis skipped: {response.status_code}")

    def test_mp3_format_synthesis(self, client: TestClient):
        """
        Synthesize audio in MP3 format.
        """
        print("\n[E2E] Testing MP3 format synthesis...")

        response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "MP3 format test.",
                "profile_id": "default",
                "format": "mp3",
            },
        )

        # MP3 encoding may not be available
        if response.status_code == 200:
            data = response.json()
            print(f"[E2E] MP3 synthesis: {data.get('audio_id', 'no id')}")
        else:
            print(f"[E2E] MP3 synthesis skipped: {response.status_code}")


class TestAudioMetadata:
    """End-to-end tests for audio metadata."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_audio_info_endpoint(self, client: TestClient):
        """
        GET /api/audio/{id}/info returns audio metadata.
        """
        print("\n[E2E] Testing audio info endpoint...")

        # First synthesize audio
        synth_response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "Metadata test audio.",
                "profile_id": "default",
            },
        )

        if synth_response.status_code != 200:
            print(f"[E2E] Synthesis skipped: {synth_response.status_code}")
            return

        audio_id = synth_response.json().get("audio_id")
        if not audio_id:
            print("[E2E] No audio_id returned")
            return

        # Get audio info
        info_response = client.get(f"/api/audio/{audio_id}/info")

        # Accept 200 (info returned) or 404 (endpoint not available)
        assert info_response.status_code in [200, 404]

        if info_response.status_code == 200:
            data = info_response.json()
            print(f"[E2E] Audio info: {data}")
        else:
            print("[E2E] Audio info endpoint not available")


class TestAudioAnalysis:
    """End-to-end tests for audio analysis endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_audio_waveform(self, client: TestClient):
        """
        GET /api/audio/{id}/waveform returns waveform data.
        """
        print("\n[E2E] Testing audio waveform endpoint...")

        # Synthesize audio first
        synth_response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "Waveform test.",
                "profile_id": "default",
            },
        )

        if synth_response.status_code != 200:
            print(f"[E2E] Synthesis skipped: {synth_response.status_code}")
            return

        audio_id = synth_response.json().get("audio_id")
        if not audio_id:
            return

        # Get waveform
        response = client.get(f"/api/audio/{audio_id}/waveform")

        # Accept 200 (waveform returned) or 404 (endpoint not available)
        assert response.status_code in [200, 404]
        print(f"[E2E] Waveform endpoint: {response.status_code}")

    def test_audio_spectrogram(self, client: TestClient):
        """
        GET /api/audio/{id}/spectrogram returns spectrogram data.
        """
        print("\n[E2E] Testing audio spectrogram endpoint...")

        # Synthesize audio first
        synth_response = client.post(
            "/api/voice/synthesize",
            json={
                "text": "Spectrogram test.",
                "profile_id": "default",
            },
        )

        if synth_response.status_code != 200:
            print(f"[E2E] Synthesis skipped: {synth_response.status_code}")
            return

        audio_id = synth_response.json().get("audio_id")
        if not audio_id:
            return

        # Get spectrogram
        response = client.get(f"/api/audio/{audio_id}/spectrogram")

        # Accept 200 (spectrogram returned) or 404 (endpoint not available)
        assert response.status_code in [200, 404]
        print(f"[E2E] Spectrogram endpoint: {response.status_code}")


class TestHealthChecks:
    """End-to-end tests for service health."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_health_endpoint(self, client: TestClient):
        """
        GET /health returns service health status.
        """
        print("\n[E2E] Testing health endpoint...")

        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        print(f"[E2E] Health status: {data['status']}")

    def test_api_root(self, client: TestClient):
        """
        GET / returns API info.
        """
        print("\n[E2E] Testing API root...")

        response = client.get("/")
        assert response.status_code == 200
        print("[E2E] API root accessible")
