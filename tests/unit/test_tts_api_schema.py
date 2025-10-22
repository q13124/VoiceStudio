#!/usr/bin/env python3
"""
Unit tests for TTS API schema with metrics
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from services.voice_engine_router import (
    app,
    TTSRequest,
    TTSResponse,
    AudioMetricsResponse,
    CONFIG,
    REGISTRY,
    ROUTER,
)


class TestTTSAPISchema:
    """Test TTS API schema with metrics integration"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_audio_data(self):
        """Mock audio data"""
        return b"fake_wav_data"

    def test_tts_request_schema(self):
        """Test TTS request schema validation"""
        # Valid request
        request_data = {
            "text": "Hello world",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {},
            "mode": "sync",
        }

        request = TTSRequest(**request_data)
        assert request.text == "Hello world"
        assert request.language == "en"
        assert request.quality == "balanced"
        assert request.mode == "sync"

    def test_tts_request_validation(self):
        """Test TTS request validation"""
        # Empty text should fail
        with pytest.raises(ValueError):
            TTSRequest(text="")

        # Language should be lowercased
        request = TTSRequest(text="test", language="EN")
        assert request.language == "en"

    def test_audio_metrics_response_schema(self):
        """Test AudioMetricsResponse schema"""
        metrics = AudioMetricsResponse(
            lufs=-16.0,
            clipping_percent=0.1,
            dc_offset=-60.0,
            head_silence_ms=50.0,
            tail_silence_ms=100.0,
            duration_ms=2000.0,
            sample_rate=16000,
            channels=1,
            rms_db=-20.0,
            peak_db=-6.0,
        )

        # All fields should be optional
        assert metrics.lufs == -16.0
        assert metrics.clipping_percent == 0.1
        assert metrics.dc_offset == -60.0
        assert metrics.head_silence_ms == 50.0
        assert metrics.tail_silence_ms == 100.0
        assert metrics.duration_ms == 2000.0
        assert metrics.sample_rate == 16000
        assert metrics.channels == 1
        assert metrics.rms_db == -20.0
        assert metrics.peak_db == -6.0

    def test_audio_metrics_response_optional_fields(self):
        """Test AudioMetricsResponse with optional fields"""
        # Should work with minimal data
        metrics = AudioMetricsResponse()
        assert metrics.lufs is None
        assert metrics.clipping_percent is None
        assert metrics.dc_offset is None

    def test_tts_response_schema_with_metrics(self):
        """Test TTS response schema with metrics"""
        metrics = AudioMetricsResponse(
            lufs=-16.0, clipping_percent=0.1, duration_ms=2000.0
        )

        response = TTSResponse(
            engine="xtts",
            tried_order=["xtts", "openvoice"],
            result_b64_wav="base64_encoded_audio",
            metrics=metrics,
        )

        assert response.engine == "xtts"
        assert response.tried_order == ["xtts", "openvoice"]
        assert response.result_b64_wav == "base64_encoded_audio"
        assert response.metrics is not None
        assert response.metrics.lufs == -16.0
        assert response.metrics.clipping_percent == 0.1

    def test_tts_response_schema_without_metrics(self):
        """Test TTS response schema without metrics"""
        response = TTSResponse(
            engine="xtts",
            tried_order=["xtts", "openvoice"],
            result_b64_wav="base64_encoded_audio",
        )

        assert response.engine == "xtts"
        assert response.tried_order == ["xtts", "openvoice"]
        assert response.result_b64_wav == "base64_encoded_audio"
        assert response.metrics is None

    def test_tts_response_async_mode(self):
        """Test TTS response schema for async mode"""
        response = TTSResponse(
            engine="xtts", tried_order=["xtts", "openvoice"], job_id="job_12345"
        )

        assert response.engine == "xtts"
        assert response.tried_order == ["xtts", "openvoice"]
        assert response.job_id == "job_12345"
        assert response.result_b64_wav is None
        assert response.metrics is None

    @patch("services.voice_engine_router.CONFIG.metrics_enabled", True)
    @patch("services.voice_engine_router.ROUTER.select_engine")
    @patch("services.voice_engine_router.ROUTER.generate")
    @patch("services.voice_engine_router.extract_audio_metrics")
    def test_tts_endpoint_with_metrics(
        self, mock_extract_metrics, mock_generate, mock_select, client
    ):
        """Test TTS endpoint with metrics enabled"""
        # Setup mocks
        mock_select.return_value = ("xtts", ["xtts", "openvoice"])
        mock_generate.return_value = b"fake_audio_data"

        from services.metrics.audio_metrics import AudioMetrics

        mock_metrics = AudioMetrics(
            lufs=-16.0,
            clipping_percent=0.1,
            dc_offset=-60.0,
            head_silence_ms=50.0,
            tail_silence_ms=100.0,
            duration_ms=2000.0,
            sample_rate=16000,
            channels=1,
            rms_db=-20.0,
            peak_db=-6.0,
        )
        mock_extract_metrics.return_value = mock_metrics

        # Make request
        response = client.post(
            "/tts",
            json={"text": "Hello world", "language": "en", "quality": "balanced"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "engine" in data
        assert "tried_order" in data
        assert "result_b64_wav" in data
        assert "metrics" in data

        # Check metrics are present
        assert data["metrics"] is not None
        assert data["metrics"]["lufs"] == -16.0
        assert data["metrics"]["clipping_percent"] == 0.1
        assert data["metrics"]["dc_offset"] == -60.0
        assert data["metrics"]["head_silence_ms"] == 50.0
        assert data["metrics"]["tail_silence_ms"] == 100.0
        assert data["metrics"]["duration_ms"] == 2000.0
        assert data["metrics"]["sample_rate"] == 16000
        assert data["metrics"]["channels"] == 1
        assert data["metrics"]["rms_db"] == -20.0
        assert data["metrics"]["peak_db"] == -6.0

    @patch("services.voice_engine_router.CONFIG.metrics_enabled", False)
    @patch("services.voice_engine_router.ROUTER.select_engine")
    @patch("services.voice_engine_router.ROUTER.generate")
    def test_tts_endpoint_without_metrics(self, mock_generate, mock_select, client):
        """Test TTS endpoint with metrics disabled"""
        # Setup mocks
        mock_select.return_value = ("xtts", ["xtts", "openvoice"])
        mock_generate.return_value = b"fake_audio_data"

        # Make request
        response = client.post(
            "/tts",
            json={"text": "Hello world", "language": "en", "quality": "balanced"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "engine" in data
        assert "tried_order" in data
        assert "result_b64_wav" in data
        assert "metrics" in data

        # Check metrics are None when disabled
        assert data["metrics"] is None

    @patch("services.voice_engine_router.CONFIG.metrics_enabled", True)
    @patch("services.voice_engine_router.ROUTER.select_engine")
    @patch("services.voice_engine_router.ROUTER.generate")
    @patch("services.voice_engine_router.extract_audio_metrics")
    def test_tts_endpoint_metrics_extraction_failure(
        self, mock_extract_metrics, mock_generate, mock_select, client
    ):
        """Test TTS endpoint when metrics extraction fails"""
        # Setup mocks
        mock_select.return_value = ("xtts", ["xtts", "openvoice"])
        mock_generate.return_value = b"fake_audio_data"
        mock_extract_metrics.side_effect = Exception("Metrics extraction failed")

        # Make request
        response = client.post(
            "/tts",
            json={"text": "Hello world", "language": "en", "quality": "balanced"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should still work, but metrics should be None
        assert "engine" in data
        assert "tried_order" in data
        assert "result_b64_wav" in data
        assert data["metrics"] is None

    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data
        assert "engines" in data

    def test_engines_endpoint(self, client):
        """Test engines endpoint"""
        response = client.get("/engines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "charset=utf-8" in response.headers["content-type"]

        # Check that metrics content is present
        content = response.text
        assert "voicestudio_requests_total" in content
        assert "voicestudio_request_duration_seconds" in content
        assert "voicestudio_tts_generation_seconds" in content

    def test_api_schema_backward_compatibility(self):
        """Test that API schema changes are backward compatible"""
        # Old clients should still work without metrics
        old_response = TTSResponse(
            engine="xtts", tried_order=["xtts"], result_b64_wav="base64_data"
        )

        # Should not require metrics field
        assert old_response.metrics is None

        # New clients can include metrics
        new_response = TTSResponse(
            engine="xtts",
            tried_order=["xtts"],
            result_b64_wav="base64_data",
            metrics=AudioMetricsResponse(lufs=-16.0),
        )

        assert new_response.metrics is not None
        assert new_response.metrics.lufs == -16.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
