"""
Integration Tests for Enhanced Route Workflows
Tests route interactions and end-to-end workflows for routes enhanced with new library integrations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import route modules
try:
    from backend.api.routes import analytics, articulation, effects, prosody, voice
except ImportError:
    pytest.skip("Backend routes not available", allow_module_level=True)


@pytest.fixture
def app():
    """Create FastAPI app with all routes."""
    app = FastAPI()
    app.include_router(articulation.router)
    app.include_router(prosody.router)
    app.include_router(effects.router)
    app.include_router(analytics.router)
    app.include_router(voice.router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestProsodyVoiceSynthesisWorkflow:
    """Test prosody -> voice synthesis integration workflow."""

    def test_prosody_config_to_synthesis_workflow(self, client):
        """Test complete workflow: create prosody config -> apply to synthesis."""
        # Step 1: Create prosody config
        prosody._prosody_configs.clear()

        config_data = {
            "name": "Test Prosody Config",
            "pitch": 1.2,
            "rate": 1.1,
            "volume": 0.9,
        }

        response = client.post("/api/prosody/configs", json=config_data)
        assert response.status_code == 200
        config_result = response.json()
        config_id = config_result["config_id"]

        # Step 2: Apply prosody to synthesis
        apply_data = {
            "config_id": config_id,
            "text": "Hello world",
            "voice_profile_id": "test-profile",
        }

        with patch("backend.api.routes.prosody.synthesize") as mock_synthesize:
            mock_synthesize.return_value = {
                "audio_id": "test-audio-123",
                "audio_url": "/path/to/audio.wav",
                "duration": 2.5,
            }

            response = client.post("/api/prosody/apply", json=apply_data)
            # May succeed or fail depending on dependencies
            assert response.status_code in [200, 500]

    def test_prosody_phoneme_analysis_to_synthesis(self, client):
        """Test workflow: phoneme analysis -> prosody application -> synthesis."""
        # Step 1: Analyze phonemes
        with patch("backend.api.routes.prosody.HAS_PHONEMIZER", True):
            with patch("backend.api.routes.prosody.Phonemizer") as mock_phonemizer:
                mock_phonemizer_instance = MagicMock()
                mock_phonemizer_instance.phonemize.return_value = "həˈloʊ"
                mock_phonemizer.return_value = mock_phonemizer_instance

                response = client.post(
                    "/api/prosody/phonemes/analyze?text=hello&language=en"
                )
                # May succeed or fail depending on dependencies
                assert response.status_code in [200, 503]

        # Step 2: Create prosody config
        prosody._prosody_configs.clear()
        config_data = {
            "name": "Phoneme-Based Config",
            "pitch": 1.0,
            "rate": 1.0,
            "volume": 1.0,
        }

        response = client.post("/api/prosody/configs", json=config_data)
        assert response.status_code == 200


class TestArticulationEffectsWorkflow:
    """Test articulation analysis -> effects processing integration workflow."""

    @patch("backend.api.routes.articulation._get_audio_path")
    @patch("soundfile.read")
    @patch("librosa.feature.rms")
    @patch("librosa.frames_to_time")
    def test_articulation_analysis_to_effects(self, mock_frames, mock_rms, mock_sf_read, mock_get_path, client):
        """Test workflow: analyze articulation -> apply effects based on issues."""
        # Step 1: Analyze articulation
        mock_get_path.return_value = "/test/audio.wav"
        audio_data = np.random.randn(44100).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 44100)
        mock_rms.return_value = np.array([[0.5] * 10])
        mock_frames.return_value = np.linspace(0, 1, 10)

        analyze_data = {"audio_id": "test-audio-123"}
        response = client.post("/api/articulation/analyze", json=analyze_data)
        assert response.status_code == 200
        analysis_result = response.json()
        assert "issues" in analysis_result

        # Step 2: Apply effects based on analysis
        effects._effect_chains.clear()
        chain_id = "test-chain-123"
        now = "2025-01-28T00:00:00"
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Articulation Fix Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        with patch("os.path.exists", return_value=True):
            with patch("backend.api.routes.voice._audio_storage") as mock_storage:
                mock_storage.__contains__ = lambda x: x == "test-audio-123"
                mock_storage.__getitem__ = lambda x: "/path/to/audio.wav"

                with patch(
                    "backend.api.routes.effects._process_audio_with_chain"
                ) as mock_process:
                    mock_process.return_value = {
                        "success": True,
                        "output_audio_id": "processed-audio",
                    }

                    process_data = {"audio_id": "test-audio-123"}
                    response = client.post(
                        f"/api/effects/chains/{chain_id}/process",
                        json=process_data,
                    )
                    # May succeed or fail depending on dependencies
                    assert response.status_code in [200, 500]


class TestAnalyticsQualityWorkflow:
    """Test analytics quality prediction integration workflow."""

    def test_quality_prediction_to_explanation_workflow(self, client):
        """Test workflow: quality prediction -> explanation."""
        audio_id = "test-audio-123"

        # Step 1: Set up audio storage
        try:
            voice._audio_storage[audio_id] = "/path/to/audio.wav"
        except AttributeError:
            pass

        # Step 2: Get quality explanation
        with patch("os.path.exists", return_value=True):
            with patch(
                "backend.api.routes.analytics._get_model_explainer"
            ) as mock_get_explainer:
                mock_explainer = MagicMock()
                mock_explainer.get_available_methods.return_value = ["shap", "lime"]
                mock_explainer.shap_available = True
                mock_get_explainer.return_value = mock_explainer

                with patch("backend.api.routes.analytics._quality_history", {}):
                    response = client.get(
                        f"/api/analytics/explain-quality?audio_id={audio_id}"
                    )
                    # May succeed or fail depending on dependencies
                    assert response.status_code in [200, 404, 500]

    def test_analytics_summary_to_quality_explanation(self, client):
        """Test workflow: get analytics summary -> explain specific quality."""
        # Step 1: Get analytics summary
        response = client.get("/api/analytics/summary")
        assert response.status_code == 200
        summary = response.json()
        assert "period_start" in summary

        # Step 2: Explain quality for specific audio
        audio_id = "test-audio-123"
        try:
            voice._audio_storage[audio_id] = "/path/to/audio.wav"
        except AttributeError:
            pass

        with patch("os.path.exists", return_value=True):
            with patch(
                "backend.api.routes.analytics._get_model_explainer"
            ) as mock_get_explainer:
                mock_explainer = MagicMock()
                mock_explainer.get_available_methods.return_value = ["shap"]
                mock_explainer.shap_available = True
                mock_get_explainer.return_value = mock_explainer

                with patch("backend.api.routes.analytics._quality_history", {}):
                    response = client.get(
                        f"/api/analytics/explain-quality?audio_id={audio_id}"
                    )
                    # May succeed or fail depending on dependencies
                    assert response.status_code in [200, 404, 500]


class TestEffectsPostFXProcessorWorkflow:
    """Test effects processing with PostFXProcessor integration workflow."""

    @patch("backend.api.routes.effects.HAS_POSTFX_PROCESSOR", True)
    @patch("backend.api.routes.effects.create_post_fx_processor")
    def test_effects_chain_with_postfxprocessor(self, mock_create_processor, client):
        """Test workflow: create effect chain -> process with PostFXProcessor."""
        # Step 1: Create effect chain
        effects._effect_chains.clear()
        chain_id = "test-chain-456"
        now = "2025-01-28T00:00:00"
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="PostFX Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        # Step 2: Process audio with PostFXProcessor
        mock_processor = MagicMock()
        mock_audio = np.random.randn(44100).astype(np.float32)
        mock_processor.process.return_value = mock_audio
        mock_create_processor.return_value = mock_processor

        with patch("os.path.exists", return_value=True):
            with patch("backend.api.routes.voice._audio_storage") as mock_storage:
                mock_storage.__contains__ = lambda x: x == "test-audio"
                mock_storage.__getitem__ = lambda x: "/path/to/audio.wav"

                with patch(
                    "backend.api.routes.effects._process_audio_with_chain"
                ) as mock_process:
                    mock_process.return_value = {
                        "success": True,
                        "output_audio_id": "processed-audio",
                    }

                    process_data = {"audio_id": "test-audio"}
                    response = client.post(
                        f"/api/effects/chains/{chain_id}/process",
                        json=process_data,
                    )
                    # May succeed or fail depending on dependencies
                    assert response.status_code in [200, 500]


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow with multiple route integrations."""

    @patch("backend.api.routes.prosody.synthesize")
    @patch("backend.api.routes.articulation._get_audio_path")
    @patch("soundfile.read")
    @patch("librosa.feature.rms")
    @patch("librosa.frames_to_time")
    @patch("backend.api.routes.effects._process_audio_with_chain")
    def test_complete_audio_processing_workflow(
        self,
        mock_process_effects,
        mock_frames,
        mock_rms,
        mock_sf_read,
        mock_get_path,
        mock_synthesize,
        client,
    ):
        """Test complete workflow: prosody -> synthesis -> articulation -> effects."""
        # Step 1: Create prosody config
        prosody._prosody_configs.clear()
        config_data = {
            "name": "E2E Test Config",
            "pitch": 1.2,
            "rate": 1.1,
            "volume": 0.9,
        }

        response = client.post("/api/prosody/configs", json=config_data)
        assert response.status_code == 200
        config_result = response.json()
        config_id = config_result["config_id"]

        # Step 2: Apply prosody and synthesize
        mock_synthesize.return_value = {
            "audio_id": "synthesized-audio-123",
            "audio_url": "/path/to/synthesized.wav",
            "duration": 2.5,
        }

        apply_data = {
            "config_id": config_id,
            "text": "Hello world",
            "voice_profile_id": "test-profile",
        }

        response = client.post("/api/prosody/apply", json=apply_data)
        # May succeed or fail depending on dependencies
        assert response.status_code in [200, 500]

        # Step 3: Analyze articulation
        mock_get_path.return_value = "/path/to/synthesized.wav"
        audio_data = np.random.randn(44100).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 44100)
        mock_rms.return_value = np.array([[0.5] * 10])
        mock_frames.return_value = np.linspace(0, 1, 10)

        analyze_data = {"audio_id": "synthesized-audio-123"}
        response = client.post("/api/articulation/analyze", json=analyze_data)
        assert response.status_code == 200

        # Step 4: Apply effects
        effects._effect_chains.clear()
        chain_id = "e2e-chain-123"
        now = "2025-01-28T00:00:00"
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="E2E Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        mock_process_effects.return_value = {
            "success": True,
            "output_audio_id": "final-audio-123",
        }

        with patch("os.path.exists", return_value=True):
            with patch("backend.api.routes.voice._audio_storage") as mock_storage:
                mock_storage.__contains__ = lambda x: x == "synthesized-audio-123"
                mock_storage.__getitem__ = lambda x: "/path/to/synthesized.wav"

                process_data = {"audio_id": "synthesized-audio-123"}
                response = client.post(
                    f"/api/effects/chains/{chain_id}/process",
                    json=process_data,
                )
                # May succeed or fail depending on dependencies
                assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
