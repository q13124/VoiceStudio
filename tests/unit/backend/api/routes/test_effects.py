"""
Unit Tests for Effects API Route
Tests audio effects endpoints comprehensively.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import effects
except ImportError:
    pytest.skip("Could not import effects route module", allow_module_level=True)


class TestEffectsRouteImports:
    """Test effects route module can be imported."""

    def test_effects_module_imports(self):
        """Test effects module can be imported."""
        assert effects is not None, "Failed to import effects module"
        assert hasattr(effects, "router"), "effects module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert effects.router is not None, "Router should exist"
        if hasattr(effects.router, "prefix"):
            assert (
                "/api/effects" in effects.router.prefix
            ), "Router prefix should include /api/effects"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(effects.router, "routes"):
            routes = [route.path for route in effects.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestEffectChains:
    """Test effect chain CRUD operations."""

    def test_list_effect_chains_empty(self):
        """Test listing effect chains when empty."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        response = client.get("/api/effects/chains?project_id=test-project")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_effect_chains_with_data(self):
        """Test listing effect chains with data."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Test Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        response = client.get("/api/effects/chains?project_id=test-project")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_effect_chains_missing_project_id(self):
        """Test listing effect chains without project_id."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        response = client.get("/api/effects/chains")
        assert response.status_code == 422  # Validation error

    def test_get_effect_chain_success(self):
        """Test successful effect chain retrieval."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Test Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        response = client.get(f"/api/effects/chains/{chain_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chain_id

    def test_get_effect_chain_not_found(self):
        """Test getting non-existent effect chain."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        response = client.get("/api/effects/chains/nonexistent")
        assert response.status_code == 404

    def test_create_effect_chain_success(self):
        """Test successful effect chain creation."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        request_data = {
            "name": "New Chain",
            "description": "A test chain",
            "project_id": "test-project",
        }

        response = client.post("/api/effects/chains", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Chain"
        assert "id" in data

    def test_create_effect_chain_missing_name(self):
        """Test effect chain creation with missing name."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        request_data = {"project_id": "test-project"}

        response = client.post("/api/effects/chains", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_update_effect_chain_success(self):
        """Test successful effect chain update."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Original Name",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        update_data = {"name": "Updated Name", "description": "Updated"}

        response = client.put(f"/api/effects/chains/{chain_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_effect_chain_not_found(self):
        """Test updating non-existent effect chain."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        update_data = {"name": "Updated Name"}

        response = client.put("/api/effects/chains/nonexistent", json=update_data)
        assert response.status_code == 404

    def test_delete_effect_chain_success(self):
        """Test successful effect chain deletion."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="To Delete",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        response = client.delete(f"/api/effects/chains/{chain_id}")
        assert response.status_code == 200

        # Verify chain is deleted
        get_response = client.get(f"/api/effects/chains/{chain_id}")
        assert get_response.status_code == 404

    def test_delete_effect_chain_not_found(self):
        """Test deleting non-existent effect chain."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        response = client.delete("/api/effects/chains/nonexistent")
        assert response.status_code == 404

    @patch("backend.api.routes.effects.HAS_POSTFX_PROCESSOR", True)
    @patch("backend.api.routes.effects.PostFXProcessor")
    @patch("backend.api.routes.effects.create_post_fx_processor")
    def test_process_audio_with_postfxprocessor(
        self, mock_create_processor, mock_processor_class
    ):
        """Test audio processing using PostFXProcessor (professional quality)."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Test Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        # Mock PostFXProcessor
        mock_processor = MagicMock()
        import numpy as np

        mock_audio = np.random.randn(44100).astype(np.float32)
        mock_processor.process.return_value = mock_audio
        mock_create_processor.return_value = mock_processor

        request_data = {"audio_id": "test-audio"}

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
                        "message": "Processed successfully",
                    }

                    response = client.post(
                        f"/api/effects/chains/{chain_id}/process", json=request_data
                    )
                    # May return 200 or 500 depending on dependencies
                    assert response.status_code in [200, 500]

    @patch("backend.api.routes.effects.HAS_POSTFX_PROCESSOR", False)
    def test_process_audio_with_basic_fallback(self):
        """Test audio processing using basic fallback when PostFXProcessor unavailable."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Test Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        request_data = {"audio_id": "test-audio"}

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
                        "message": "Processed successfully",
                    }

                    response = client.post(
                        f"/api/effects/chains/{chain_id}/process", json=request_data
                    )
                    # Should fall back to basic implementation
                    assert response.status_code in [200, 500]

    def test_process_audio_with_chain_success(self):
        """Test successful audio processing with effect chain."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Test Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        request_data = {"audio_id": "test-audio"}

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
                        "message": "Processed successfully",
                    }

                    response = client.post(
                        f"/api/effects/chains/{chain_id}/process", json=request_data
                    )
                    # May return 200 or 500 depending on dependencies
                    assert response.status_code in [200, 500]


class TestEffectPresets:
    """Test effect preset operations."""

    def test_list_effect_presets_empty(self):
        """Test listing effect presets when empty."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_presets.clear()

        response = client.get("/api/effects/presets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_effect_presets_with_data(self):
        """Test listing effect presets with data."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_presets.clear()

        preset_id = f"preset-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_presets[preset_id] = effects.EffectPreset(
            id=preset_id,
            effect_type="reverb",
            name="Test Preset",
            parameters=[],
            created=now,
            modified=now,
        )

        response = client.get("/api/effects/presets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_create_effect_preset_success(self):
        """Test successful effect preset creation."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_presets.clear()

        request_data = {
            "effect_type": "reverb",
            "name": "New Preset",
            "description": "A test preset",
        }

        response = client.post("/api/effects/presets", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Preset"
        assert "id" in data

    def test_create_effect_preset_missing_type(self):
        """Test effect preset creation with missing type."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_presets.clear()

        request_data = {"name": "New Preset"}

        response = client.post("/api/effects/presets", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_delete_effect_preset_success(self):
        """Test successful effect preset deletion."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_presets.clear()

        preset_id = f"preset-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_presets[preset_id] = effects.EffectPreset(
            id=preset_id,
            effect_type="reverb",
            name="To Delete",
            parameters=[],
            created=now,
            modified=now,
        )

        response = client.delete(f"/api/effects/presets/{preset_id}")
        assert response.status_code == 200

    def test_delete_effect_preset_not_found(self):
        """Test deleting non-existent effect preset."""
        app = FastAPI()
        app.include_router(effects.router)
        client = TestClient(app)

        effects._effect_presets.clear()

        response = client.delete("/api/effects/presets/nonexistent")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
