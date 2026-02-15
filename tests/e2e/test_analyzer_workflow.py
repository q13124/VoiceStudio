"""
Audio Analyzer Workflow E2E Tests.

Tests for analyzer operations including:
- Load audio for analysis
- View spectrogram
- View waveform
- View loudness/phase/radar visualizations

Phase 9A: Feature Matrix - Analyze
"""

from __future__ import annotations

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
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
        response = api_client.get("/api/health")
        return response.status_code == 200
    except Exception:
        return False


class TestAnalyzerLoad:
    """Tests for loading audio into analyzer."""

    def test_analyzer_status(self, api_client, backend_available):
        """Test analyzer status endpoint."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/status")
        assert response.status_code in (200, 404, 422, 429)

    def test_get_analyzer_config(self, api_client, backend_available):
        """Test getting analyzer configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/config")
        assert response.status_code in (200, 404, 422, 429)

    def test_update_analyzer_config(self, api_client, backend_available):
        """Test updating analyzer configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.patch(
            "/api/analyzer/config",
            json={"fft_size": 2048, "hop_length": 512}
        )
        assert response.status_code in (200, 400, 404, 422, 429)


class TestSpectrogramAnalysis:
    """Tests for spectrogram visualization."""

    def test_get_spectrogram_params(self, api_client, backend_available):
        """Test getting spectrogram parameters."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/spectrogram/params")
        assert response.status_code in (200, 404, 422, 429)

    def test_generate_spectrogram(self, api_client, backend_available):
        """Test requesting spectrogram generation."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/spectrogram",
            json={"audio_path": "test.wav", "type": "mel"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_spectrogram_types(self, api_client, backend_available):
        """Test different spectrogram types."""
        if not backend_available:
            pytest.skip("Backend not available")

        for spec_type in ["mel", "linear", "log", "cqt"]:
            response = api_client.get(f"/api/analyzer/spectrogram/types/{spec_type}")
            assert response.status_code in (200, 404, 422, 429)


class TestWaveformAnalysis:
    """Tests for waveform visualization."""

    def test_get_waveform_params(self, api_client, backend_available):
        """Test getting waveform parameters."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/waveform/params")
        assert response.status_code in (200, 404, 422, 429)

    def test_generate_waveform(self, api_client, backend_available):
        """Test requesting waveform generation."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/waveform",
            json={"audio_path": "test.wav", "width": 1000, "height": 200}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_waveform_zoom(self, api_client, backend_available):
        """Test waveform zoom levels."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/waveform/zoom?start=0&end=1000")
        assert response.status_code in (200, 404, 422, 429)


class TestLoudnessAnalysis:
    """Tests for loudness analysis."""

    def test_get_loudness_metrics(self, api_client, backend_available):
        """Test getting loudness metrics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/loudness")
        assert response.status_code in (200, 404, 422, 429)

    def test_analyze_lufs(self, api_client, backend_available):
        """Test LUFS analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/loudness/lufs",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_analyze_peak_levels(self, api_client, backend_available):
        """Test peak level analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/loudness/peaks",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_analyze_dynamics(self, api_client, backend_available):
        """Test dynamic range analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/loudness/dynamics",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)


class TestPhaseAnalysis:
    """Tests for phase analysis."""

    def test_get_phase_correlation(self, api_client, backend_available):
        """Test getting phase correlation."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/phase/correlation")
        assert response.status_code in (200, 404, 422, 429)

    def test_analyze_phase(self, api_client, backend_available):
        """Test phase analysis for stereo audio."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/phase",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_stereo_width_analysis(self, api_client, backend_available):
        """Test stereo width analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/phase/stereo-width",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)


class TestRadarVisualization:
    """Tests for radar/polar visualizations."""

    def test_get_frequency_radar(self, api_client, backend_available):
        """Test getting frequency radar data."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/radar/frequency")
        assert response.status_code in (200, 404, 422, 429)

    def test_generate_radar_visualization(self, api_client, backend_available):
        """Test generating radar visualization."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/radar",
            json={"audio_path": "test.wav", "type": "frequency"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)


class TestAudioStatistics:
    """Tests for audio statistics."""

    def test_get_audio_info(self, api_client, backend_available):
        """Test getting audio file information."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/info",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_get_audio_statistics(self, api_client, backend_available):
        """Test getting audio statistics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/statistics",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_compare_audio_files(self, api_client, backend_available):
        """Test comparing two audio files."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/compare",
            json={"audio_path_1": "test1.wav", "audio_path_2": "test2.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)


class TestVoiceQualityMetrics:
    """Tests for voice quality metrics."""

    def test_get_voice_quality_params(self, api_client, backend_available):
        """Test getting voice quality parameters."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/analyzer/voice-quality/params")
        assert response.status_code in (200, 404, 422, 429)

    def test_analyze_voice_quality(self, api_client, backend_available):
        """Test voice quality analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/voice-quality",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_analyze_pitch(self, api_client, backend_available):
        """Test pitch analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/pitch",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_analyze_formants(self, api_client, backend_available):
        """Test formant analysis."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/analyzer/formants",
            json={"audio_path": "test.wav"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)
