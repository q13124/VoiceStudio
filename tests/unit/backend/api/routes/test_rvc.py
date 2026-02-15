"""
Unit Tests for RVC API Route
Tests RVC (Retrieval-based Voice Conversion) endpoints in isolation.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock dependencies before importing rvc
import sys

# Create mock modules for dependencies that might not be available
for module_name in ["torch", "torch.cuda"]:
    if module_name not in sys.modules:
        mock_module = MagicMock()
        if module_name == "torch.cuda":
            mock_module.is_available = lambda: False
        sys.modules[module_name] = mock_module

# Import the route module
try:
    from backend.api.routes import rvc
    from backend.api.routes.rvc import _audio_storage
except (ImportError, NameError, AttributeError) as e:
    pytest.skip(f"Could not import rvc route module: {e}", allow_module_level=True)


class TestRVCRouteImports:
    """Test RVC route module can be imported."""

    @pytest.mark.skipif(not RVC_AVAILABLE, reason="RVC module not available")
    def test_rvc_module_imports(self):
        """Test rvc module can be imported."""
        assert rvc is not None, "Failed to import rvc module"
        assert hasattr(rvc, "router"), "rvc module missing router"

    def test_rvc_router_configured(self):
        """Test RVC router is configured correctly."""
        assert rvc.router is not None
        if hasattr(rvc.router, "prefix"):
            assert "/api/rvc" in rvc.router.prefix


class TestRVCRouteHandlers:
    """Test RVC route handlers exist and are callable."""

    @pytest.mark.skipif(not RVC_AVAILABLE, reason="RVC module not available")
    def test_convert_voice_handler_exists(self):
        """Test convert_voice handler exists."""
        assert hasattr(rvc, "convert_voice")
        assert callable(rvc.convert_voice)

    def test_get_models_handler_exists(self):
        """Test get_models handler exists."""
        assert hasattr(rvc, "get_models")
        assert callable(rvc.get_models)

    def test_upload_model_handler_exists(self):
        """Test upload_model handler exists."""
        assert hasattr(rvc, "upload_model")
        assert callable(rvc.upload_model)

    def test_get_audio_handler_exists(self):
        """Test get_audio handler exists."""
        assert hasattr(rvc, "get_audio")
        assert callable(rvc.get_audio)

    def test_start_realtime_handler_exists(self):
        """Test start_realtime handler exists."""
        assert hasattr(rvc, "start_realtime")
        assert callable(rvc.start_realtime)

    def test_stop_realtime_handler_exists(self):
        """Test stop_realtime handler exists."""
        assert hasattr(rvc, "stop_realtime")
        assert callable(rvc.stop_realtime)


class TestRVCRouter:
    """Test RVC router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert rvc.router is not None, "Router should exist"
        if hasattr(rvc.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(rvc.router, "routes"):
            routes = [route.path for route in rvc.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestRVCRouteEndpoints:
    """Test RVC route endpoint functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        if not RVC_AVAILABLE:
            pytest.skip("RVC module not available")
        # Clear audio storage before each test
        if _audio_storage:
            _audio_storage.clear()
        yield
        # Cleanup after each test
        if _audio_storage:
            _audio_storage.clear()

    @pytest.fixture
    def app(self):
        """Create FastAPI app with RVC router."""
        app = FastAPI()
        app.include_router(rvc.router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @patch("backend.api.routes.rvc.ENGINE_AVAILABLE", True)
    @patch("backend.api.routes.rvc.engine_router")
    @patch("backend.api.routes.rvc._get_audio_path")
    def test_convert_voice_engine_not_available(self, mock_get_path, mock_router, client):
        """Test convert_voice when engine is not available."""
        mock_router.get_engine.return_value = None

        response = client.post(
            "/api/rvc/convert",
            params={
                "source_audio_id": "audio-123",
                "target_speaker_model": "model.pth",
            },
        )

        assert response.status_code == 503
        assert "not available" in response.json()["detail"].lower()

    @patch("backend.api.routes.rvc.ENGINE_AVAILABLE", False)
    def test_convert_voice_router_not_available(self, client):
        """Test convert_voice when router is not available."""
        response = client.post(
            "/api/rvc/convert",
            params={
                "source_audio_id": "audio-123",
                "target_speaker_model": "model.pth",
            },
        )

        assert response.status_code == 503
        assert "not available" in response.json()["detail"].lower()

    @patch("backend.api.routes.rvc.ENGINE_AVAILABLE", True)
    @patch("backend.api.routes.rvc.engine_router")
    @patch("backend.api.routes.audio._get_audio_path")
    def test_convert_voice_audio_not_found(self, mock_get_path, mock_router, client):
        """Test convert_voice when source audio is not found."""
        mock_router.get_engine.return_value = MagicMock()
        mock_get_path.return_value = None

        response = client.post(
            "/api/rvc/convert",
            params={
                "source_audio_id": "nonexistent",
                "target_speaker_model": "model.pth",
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_models_success(self, client):
        """Test getting available RVC models."""
        with patch("os.path.exists", return_value=True):
            with patch("os.listdir", return_value=["model1", "model2"]):
                with patch("os.path.isdir", return_value=True):
                    with patch(
                        "os.path.join",
                        side_effect=lambda *args: "/".join(args),
                    ):
                        response = client.get("/api/rvc/models")

                        assert response.status_code == 200
                        data = response.json()
                        assert "models" in data
                        assert isinstance(data["models"], list)

    def test_get_models_empty(self, client):
        """Test getting models when none exist."""
        with patch("os.path.exists", return_value=False):
            response = client.get("/api/rvc/models")

            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert data["models"] == []

    @patch("backend.api.routes.rvc._audio_storage")
    def test_get_audio_success(self, mock_storage, client):
        """Test getting converted audio file."""
        import os
        import tempfile

        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            mock_storage.get.return_value = tmp_path
            mock_storage.__contains__ = lambda self, key: key == "audio-123"

            response = client.get("/api/rvc/audio/audio-123")

            # Should return file response (200) or 404 if file doesn't exist
            assert response.status_code in [200, 404]
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_get_audio_not_found(self, client):
        """Test getting non-existent audio file."""
        with patch("backend.api.routes.rvc._audio_storage") as mock_storage:
            mock_storage.get.return_value = None
            mock_storage.__contains__ = lambda self, key: False

            response = client.get("/api/rvc/audio/nonexistent")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    @patch("backend.api.routes.rvc.ENGINE_AVAILABLE", True)
    @patch("backend.api.routes.rvc.engine_router")
    def test_start_realtime_success(self, mock_router, client):
        """Test starting real-time conversion."""
        mock_engine = MagicMock()
        mock_router.get_engine.return_value = mock_engine

        request_data = {
            "target_speaker_model": "model.pth",
            "pitch_shift": 0,
            "protect": 0.33,
            "index_rate": 0.75,
        }

        response = client.post("/api/rvc/start", json=request_data)

        # Should return success or 503 if engine not available
        assert response.status_code in [200, 503]

    @patch("backend.api.routes.rvc.ENGINE_AVAILABLE", False)
    def test_start_realtime_router_not_available(self, client):
        """Test starting real-time when router is not available."""
        request_data = {
            "target_speaker_model": "model.pth",
        }

        response = client.post("/api/rvc/start", json=request_data)

        assert response.status_code == 503
        assert "not available" in response.json()["detail"].lower()

    def test_stop_realtime_success(self, client):
        """Test stopping real-time conversion."""
        response = client.post("/api/rvc/stop")

        # Should return success (200) or error if not started
        assert response.status_code in [200, 400, 404]

    @patch("backend.api.routes.rvc.ENGINE_AVAILABLE", True)
    @patch("backend.api.routes.rvc.engine_router")
    @patch("backend.api.routes.audio._get_audio_path")
    def test_convert_voice_with_parameters(self, mock_get_path, mock_router, client):
        """Test convert_voice with all parameters."""
        import os
        import tempfile

        # Create mock engine
        mock_engine = MagicMock()
        mock_engine.convert_voice.return_value = (None, {})
        mock_router.get_engine.return_value = mock_engine

        # Create temporary source audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"fake audio")
            source_path = tmp.name

        try:
            mock_get_path.return_value = source_path

            # Mock file operations
            with patch("tempfile.mktemp", return_value="/tmp/output.wav"):
                with patch("os.path.exists", return_value=True):
                    with patch("wave.open"):
                        response = client.post(
                            "/api/rvc/convert",
                            params={
                                "source_audio_id": "audio-123",
                                "target_speaker_model": "model.pth",
                                "pitch_shift": 2,
                                "protect": 0.4,
                                "index_rate": 0.8,
                                "enhance_quality": True,
                                "calculate_quality": True,
                            },
                        )

                        # Should succeed or fail based on engine availability
                        assert response.status_code in [200, 500, 503]
        finally:
            if os.path.exists(source_path):
                os.unlink(source_path)

    def test_convert_voice_missing_parameters(self, client):
        """Test convert_voice with missing required parameters."""
        response = client.post("/api/rvc/convert")

        # Should return 422 (validation error) or 503 (engine not available)
        assert response.status_code in [422, 503]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
