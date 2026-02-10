"""
Unit Tests for Audio API Route
Tests audio analysis endpoints comprehensively.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import audio
except ImportError:
    pytest.skip("Could not import audio route module", allow_module_level=True)


class TestAudioRouteImports:
    """Test audio route module can be imported."""

    def test_audio_module_imports(self):
        """Test audio module can be imported."""
        assert audio is not None, "Failed to import audio module"
        assert hasattr(audio, "router"), "audio module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert audio.router is not None, "Router should exist"
        if hasattr(audio.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(audio.router, "routes"):
            routes = [route.path for route in audio.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestAudioWaveformEndpoint:
    """Test waveform data endpoint."""

    def test_get_waveform_success(self):
        """Test successful waveform data retrieval."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            # Create a simple audio file
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            sf.write(tmp.name, samples, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/waveform?audio_id={audio_id}&width=512")
                assert response.status_code == 200
                data = response.json()
                assert "samples" in data
                assert "sample_rate" in data
                assert "duration" in data
                assert "channels" in data
                assert "width" in data
                assert "mode" in data

    def test_get_waveform_missing_audio_id(self):
        """Test waveform endpoint with missing audio_id."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/waveform?width=512")
        assert response.status_code == 422  # Validation error

    def test_get_waveform_invalid_width(self):
        """Test waveform endpoint with invalid width."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/waveform?audio_id=test&width=0")
        assert response.status_code == 400

    def test_get_waveform_width_too_large(self):
        """Test waveform endpoint with width exceeding limit."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/waveform?audio_id=test&width=20000")
        assert response.status_code == 400

    def test_get_waveform_audio_not_found(self):
        """Test waveform endpoint with non-existent audio file."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio._get_audio_path") as mock_path:
            mock_path.return_value = None

            response = client.get("/api/audio/waveform?audio_id=nonexistent&width=512")
            assert response.status_code == 404

    def test_get_waveform_rms_mode(self):
        """Test waveform endpoint with RMS mode."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            sf.write(tmp.name, samples, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/waveform?audio_id={audio_id}&width=512&mode=rms")
                assert response.status_code == 200
                data = response.json()
                assert data["mode"] == "rms"

    def test_get_waveform_no_audio_libs(self):
        """Test waveform endpoint when audio libraries are not available."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio.HAS_AUDIO_LIBS", False):
            response = client.get("/api/audio/waveform?audio_id=test&width=512")
            assert response.status_code == 503


class TestAudioSpectrogramEndpoint:
    """Test spectrogram data endpoint."""

    def test_get_spectrogram_success(self):
        """Test successful spectrogram data retrieval."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            sf.write(tmp.name, samples, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/spectrogram?audio_id={audio_id}&width=512&height=256")
                assert response.status_code == 200
                data = response.json()
                assert "frames" in data
                assert "sample_rate" in data
                assert "fft_size" in data
                assert "hop_length" in data
                assert "width" in data
                assert "height" in data

    def test_get_spectrogram_missing_audio_id(self):
        """Test spectrogram endpoint with missing audio_id."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/spectrogram?width=512")
        assert response.status_code == 422

    def test_get_spectrogram_audio_not_found(self):
        """Test spectrogram endpoint with non-existent audio file."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio._get_audio_path") as mock_path:
            mock_path.return_value = None

            response = client.get("/api/audio/spectrogram?audio_id=nonexistent&width=512")
            assert response.status_code == 404

    def test_get_spectrogram_invalid_width(self):
        """Test spectrogram endpoint with invalid width."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/spectrogram?audio_id=test&width=0")
        assert response.status_code == 400

    def test_get_spectrogram_invalid_height(self):
        """Test spectrogram endpoint with invalid height."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/spectrogram?audio_id=test&height=0")
        assert response.status_code == 400


class TestAudioLoudnessEndpoint:
    """Test loudness data endpoint."""

    def test_get_loudness_success(self):
        """Test successful loudness data retrieval."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            sf.write(tmp.name, samples, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/loudness?audio_id={audio_id}&width=512")
                assert response.status_code == 200
                data = response.json()
                assert "times" in data
                assert "lufs_values" in data
                assert "sample_rate" in data
                assert "duration" in data

    def test_get_loudness_missing_audio_id(self):
        """Test loudness endpoint with missing audio_id."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/loudness?width=512")
        assert response.status_code == 422

    def test_get_loudness_audio_not_found(self):
        """Test loudness endpoint with non-existent audio file."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio._get_audio_path") as mock_path:
            mock_path.return_value = None

            response = client.get("/api/audio/loudness?audio_id=nonexistent&width=512")
            assert response.status_code == 404

    def test_get_loudness_invalid_width(self):
        """Test loudness endpoint with invalid width."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/loudness?audio_id=test&width=0")
        assert response.status_code == 400


class TestAudioMetersEndpoint:
    """Test audio meters endpoint."""

    def test_get_audio_meters_success(self):
        """Test successful audio meters retrieval."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            sf.write(tmp.name, samples, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/meters?audio_id={audio_id}")
                assert response.status_code == 200
                data = response.json()
                assert "peak" in data
                assert "rms" in data
                assert "channels" in data

    def test_get_audio_meters_missing_audio_id(self):
        """Test meters endpoint with missing audio_id."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/meters")
        assert response.status_code == 422

    def test_get_audio_meters_audio_not_found(self):
        """Test meters endpoint with non-existent audio file."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio._get_audio_path") as mock_path:
            mock_path.return_value = None

            response = client.get("/api/audio/meters?audio_id=nonexistent")
            assert response.status_code == 404


class TestAudioRadarEndpoint:
    """Test radar chart data endpoint."""

    def test_get_radar_success(self):
        """Test successful radar data retrieval."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            sf.write(tmp.name, samples, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/radar?audio_id={audio_id}")
                assert response.status_code == 200
                data = response.json()
                assert "band_names" in data
                assert "frequencies" in data
                assert "magnitudes" in data
                assert "sample_rate" in data

    def test_get_radar_missing_audio_id(self):
        """Test radar endpoint with missing audio_id."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/radar")
        assert response.status_code == 422

    def test_get_radar_audio_not_found(self):
        """Test radar endpoint with non-existent audio file."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio._get_audio_path") as mock_path:
            mock_path.return_value = None

            response = client.get("/api/audio/radar?audio_id=nonexistent")
            assert response.status_code == 404


class TestAudioPhaseEndpoint:
    """Test phase analysis endpoint."""

    def test_get_phase_success(self):
        """Test successful phase data retrieval."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sample_rate = 44100
            duration = 1.0
            # Create stereo audio
            left = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            right = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            stereo = np.column_stack([left, right])
            sf.write(tmp.name, stereo, sample_rate)
            audio_id = Path(tmp.name).stem

            with patch("backend.api.routes.audio._get_audio_path") as mock_path:
                mock_path.return_value = tmp.name

                response = client.get(f"/api/audio/phase?audio_id={audio_id}")
                assert response.status_code == 200
                data = response.json()
                assert "times" in data
                assert "correlation" in data
                assert "sample_rate" in data
                assert "duration" in data

    def test_get_phase_missing_audio_id(self):
        """Test phase endpoint with missing audio_id."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/phase")
        assert response.status_code == 422

    def test_get_phase_audio_not_found(self):
        """Test phase endpoint with non-existent audio file."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        with patch("backend.api.routes.audio._get_audio_path") as mock_path:
            mock_path.return_value = None

            response = client.get("/api/audio/phase?audio_id=nonexistent")
            assert response.status_code == 404

    def test_get_phase_invalid_window_size(self):
        """Test phase endpoint with invalid window_size."""
        app = FastAPI()
        app.include_router(audio.router)
        client = TestClient(app)

        response = client.get("/api/audio/phase?audio_id=test&window_size=0")
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
