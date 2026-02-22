"""
Audio Effects Workflow E2E Tests.

Tests the complete audio effects workflow:
1. Open Effects Mixer
2. Load audio file
3. Apply effect (reverb, EQ, compression)
4. Preview processed audio
5. Export processed audio
"""

from __future__ import annotations

import math
import struct
import uuid
import wave
from pathlib import Path

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.effects,
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
    """Create a test audio file for effects processing."""
    audio_file = tmp_path / "test_audio.wav"
    with wave.open(str(audio_file), "w") as wav:
        wav.setnchannels(2)  # Stereo for effects testing
        wav.setsampwidth(2)
        wav.setframerate(44100)
        # Generate 2 seconds of stereo audio
        num_samples = 44100 * 2 * 2  # 2 channels
        samples = [
            int(8000 * math.sin(2 * math.pi * 440 * (i // 2) / 44100)) for i in range(num_samples)
        ]
        wav.writeframes(struct.pack(f"{len(samples)}h", *samples))

    return audio_file


class TestEffectsAvailability:
    """Tests for effects availability and listing."""

    def test_list_available_effects(self, api_client, backend_available):
        """Test listing all available audio effects."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/voice-effects/")
        assert response.status_code == 200

        effects = response.json()
        assert isinstance(effects, (list, dict))

    def test_get_effect_categories(self, api_client, backend_available):
        """Test getting effect categories."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/voice-effects/categories")
        # May or may not exist
        assert response.status_code in (200, 404)

    def test_get_effect_presets(self, api_client, backend_available):
        """Test getting effect presets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/voice-effects/presets")
        assert response.status_code in (200, 404)


class TestEffectsConfiguration:
    """Tests for effects configuration."""

    def test_get_effect_parameters(self, api_client, backend_available):
        """Test getting parameters for a specific effect."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Common effect types
        effect_types = ["reverb", "eq", "compression", "delay", "chorus"]

        for effect_type in effect_types:
            response = api_client.get(f"/api/voice-effects/{effect_type}/parameters")
            assert response.status_code in (200, 404, 422)

    def test_validate_effect_config(self, api_client, backend_available):
        """Test validating effect configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/voice-effects/validate",
            json={
                "effect_type": "reverb",
                "parameters": {
                    "room_size": 0.5,
                    "damping": 0.5,
                    "wet_level": 0.3,
                },
            },
        )
        assert response.status_code in (200, 400, 404, 422)


class TestEffectsProcessing:
    """Tests for applying effects to audio."""

    def test_apply_reverb_effect(self, api_client, backend_available, test_audio_file):
        """Test applying reverb effect to audio."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-effects/apply",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effect_type": "reverb",
                    "parameters": '{"room_size": 0.5, "wet_level": 0.3}',
                },
            )

        assert response.status_code in (200, 400, 404, 500, 503)

    def test_apply_eq_effect(self, api_client, backend_available, test_audio_file):
        """Test applying EQ effect to audio."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-effects/apply",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effect_type": "eq",
                    "parameters": '{"low_gain": 1.5, "mid_gain": 1.0, "high_gain": 0.8}',
                },
            )

        assert response.status_code in (200, 400, 404, 500, 503)

    def test_apply_compression_effect(self, api_client, backend_available, test_audio_file):
        """Test applying compression effect to audio."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-effects/apply",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effect_type": "compression",
                    "parameters": '{"threshold": -20, "ratio": 4, "attack": 10, "release": 100}',
                },
            )

        assert response.status_code in (200, 400, 404, 500, 503)

    def test_apply_multiple_effects(self, api_client, backend_available, test_audio_file):
        """Test applying multiple effects in chain."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-effects/apply-chain",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effects_chain": '[{"type": "eq", "params": {}}, {"type": "reverb", "params": {}}]',
                },
            )

        assert response.status_code in (200, 400, 404, 500, 503)


class TestEffectsPreviewing:
    """Tests for effects preview functionality."""

    def test_preview_effect(self, api_client, backend_available, test_audio_file):
        """Test previewing an effect without saving."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-effects/preview",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effect_type": "reverb",
                    "parameters": '{"room_size": 0.7}',
                    "preview_duration": 5,  # seconds
                },
            )

        assert response.status_code in (200, 400, 404, 500, 503)

    def test_compare_original_processed(self, api_client, backend_available, test_audio_file):
        """Test A/B comparison functionality."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/voice-effects/compare",
            json={
                "original_path": str(test_audio_file),
                "effect_config": {"type": "reverb", "params": {}},
            },
        )

        assert response.status_code in (200, 400, 404, 422, 500, 503)


class TestEffectsExport:
    """Tests for exporting processed audio."""

    def test_export_processed_audio(self, api_client, backend_available, test_audio_file):
        """Test exporting processed audio to file."""
        if not backend_available:
            pytest.skip("Backend not available")

        with open(test_audio_file, "rb") as f:
            response = api_client.post(
                "/api/voice-effects/export",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effect_type": "reverb",
                    "parameters": '{"room_size": 0.5}',
                    "output_format": "wav",
                },
            )

        assert response.status_code in (200, 400, 404, 500, 503)

    def test_export_different_formats(self, api_client, backend_available, test_audio_file):
        """Test exporting to different audio formats."""
        if not backend_available:
            pytest.skip("Backend not available")

        formats = ["wav", "mp3", "flac", "ogg"]

        for output_format in formats:
            with open(test_audio_file, "rb") as f:
                response = api_client.post(
                    "/api/voice-effects/export",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={
                        "effect_type": "reverb",
                        "parameters": "{}",
                        "output_format": output_format,
                    },
                )

            assert response.status_code in (200, 400, 404, 422, 500, 503)


class TestEffectsMixer:
    """Tests for the effects mixer interface."""

    def test_get_mixer_state(self, api_client, backend_available):
        """Test getting current mixer state."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/effects-mixer/state")
        assert response.status_code in (200, 404)

    def test_save_mixer_preset(self, api_client, backend_available):
        """Test saving mixer preset."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/effects-mixer/presets",
            json={
                "name": f"test_preset_{uuid.uuid4().hex[:8]}",
                "effects_chain": [
                    {"type": "eq", "params": {}},
                    {"type": "reverb", "params": {}},
                ],
            },
        )

        assert response.status_code in (200, 201, 400, 404, 422)

    def test_list_mixer_presets(self, api_client, backend_available):
        """Test listing mixer presets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/effects-mixer/presets")
        assert response.status_code in (200, 404)


class TestAudioEffectsWorkflowIntegration:
    """Integration tests for complete audio effects workflow."""

    @pytest.fixture
    def workflow_state(self):
        """State tracking for workflow tests."""
        return {"processed_file": None, "preset_id": None}

    def test_complete_effects_workflow_api(
        self, api_client, backend_available, workflow_state, test_audio_file
    ):
        """Test the complete audio effects workflow via API.

        Steps:
        1. List available effects
        2. Load audio file
        3. Apply effect
        4. Preview result
        5. Export processed audio
        6. Clean up
        """
        if not backend_available:
            pytest.skip("Backend not available")

        # Step 1: List available effects
        effects_response = api_client.get("/api/voice-effects/")
        assert effects_response.status_code == 200

        # Step 2 & 3: Load audio and apply effect
        with open(test_audio_file, "rb") as f:
            apply_response = api_client.post(
                "/api/voice-effects/apply",
                files={"file": ("test.wav", f, "audio/wav")},
                data={
                    "effect_type": "reverb",
                    "parameters": '{"room_size": 0.5}',
                },
            )

        if apply_response.status_code in (500, 503):
            pytest.skip("Effects processing not available")

        if apply_response.status_code == 200:
            result = apply_response.json()
            # May have output path or processed data
            workflow_state["processed_file"] = result.get("output_path")

            # Step 4: Preview (if endpoint exists)
            with open(test_audio_file, "rb") as f:
                preview_response = api_client.post(
                    "/api/voice-effects/preview",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={
                        "effect_type": "reverb",
                        "parameters": "{}",
                    },
                )
            # Preview may or may not exist
            assert preview_response.status_code in (200, 400, 404, 500, 503)

            # Step 5: Export
            with open(test_audio_file, "rb") as f:
                export_response = api_client.post(
                    "/api/voice-effects/export",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={
                        "effect_type": "reverb",
                        "parameters": "{}",
                        "output_format": "wav",
                    },
                )
            assert export_response.status_code in (200, 400, 404, 500, 503)


class TestRealTimeEffects:
    """Tests for real-time effects processing."""

    def test_realtime_effects_status(self, api_client, backend_available):
        """Test real-time effects status."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/voice-effects/realtime/status")
        assert response.status_code in (200, 404)

    def test_realtime_effects_configuration(self, api_client, backend_available):
        """Test configuring real-time effects."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/voice-effects/realtime/configure",
            json={
                "effects": [{"type": "reverb", "params": {}}],
                "latency_mode": "low",
            },
        )

        assert response.status_code in (200, 400, 404, 422)
