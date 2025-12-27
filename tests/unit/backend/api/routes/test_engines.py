"""
Unit Tests for Engines API Route
Tests engine management endpoints comprehensively.
"""

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock torch before importing engines module
mock_torch = ModuleType("torch")
mock_torch.__spec__ = MagicMock()
mock_torch.__version__ = "2.0.0"
sys.modules["torch"] = mock_torch

mock_torchaudio = ModuleType("torchaudio")
mock_torchaudio.__spec__ = MagicMock()
sys.modules["torchaudio"] = mock_torchaudio

# Import the route module
try:
    from backend.api.routes import engines
except (ImportError, NameError, ValueError) as e:
    pytest.skip(
        f"Could not import engines route module: {e}", allow_module_level=True
    )


class TestEnginesRouteImports:
    """Test engines route module can be imported."""

    def test_engines_module_imports(self):
        """Test engines module can be imported."""
        assert engines is not None, "Failed to import engines module"
        assert hasattr(engines, "router"), "engines module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert engines.router is not None, "Router should exist"
        if hasattr(engines.router, "prefix"):
            assert (
                "/api/engines" in engines.router.prefix
            ), "Router prefix should include /api/engines"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(engines.router, "routes"):
            routes = [route.path for route in engines.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestEnginesEndpoints:
    """Test engine management endpoints."""

    def test_list_engines_success(self):
        """Test successful engine listing."""
        app = FastAPI()
        app.include_router(engines.router)
        client = TestClient(app)

        with patch("backend.api.routes.engines.ENGINE_AVAILABLE", True):
            with patch("backend.api.routes.engines.engine_router") as mock_router:
                mock_router.list_engines.return_value = ["xtts", "tortoise"]

                response = client.get("/api/engines/list")
                assert response.status_code == 200
                data = response.json()
                assert "engines" in data
                assert data["available"] is True

    def test_list_engines_not_available(self):
        """Test listing engines when router not available."""
        app = FastAPI()
        app.include_router(engines.router)
        client = TestClient(app)

        with patch("backend.api.routes.engines.ENGINE_AVAILABLE", False):
            response = client.get("/api/engines/list")
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is False

    def test_recommend_engine_success(self):
        """Test successful engine recommendation."""
        app = FastAPI()
        app.include_router(engines.router)
        client = TestClient(app)

        request_data = {
            "task_type": "tts",
            "min_mos_score": 4.0,
            "quality_tier": "standard",
        }

        with patch("backend.api.routes.engines.ENGINE_AVAILABLE", True):
            with patch("backend.api.routes.engines.engine_router") as mock_router:
                mock_router.list_engines.return_value = ["xtts"]
                mock_router.get_manifest.return_value = {
                    "type": "audio",
                    "subtype": "tts",
                    "name": "XTTS",
                    "quality_features": {
                        "mos_estimate": "4.5",
                        "quality_tier": "standard",
                    },
                }

                response = client.post("/api/engines/recommend", json=request_data)
                assert response.status_code == 200
                data = response.json()
                assert "recommendations" in data

    def test_recommend_engine_not_available(self):
        """Test engine recommendation when router not available."""
        app = FastAPI()
        app.include_router(engines.router)
        client = TestClient(app)

        request_data = {"task_type": "tts"}

        with patch("backend.api.routes.engines.ENGINE_AVAILABLE", False):
            response = client.post("/api/engines/recommend", json=request_data)
            assert response.status_code == 503

    def test_compare_engines_success(self):
        """Test successful engine comparison."""
        app = FastAPI()
        app.include_router(engines.router)
        client = TestClient(app)

        with patch("backend.api.routes.engines.ENGINE_AVAILABLE", True):
            with patch("backend.api.routes.engines.engine_router") as mock_router:
                mock_router.list_engines.return_value = ["xtts", "tortoise"]
                mock_router.get_manifest.side_effect = [
                    {
                        "type": "audio",
                        "subtype": "tts",
                        "name": "XTTS",
                        "quality_features": {},
                    },
                    {
                        "type": "audio",
                        "subtype": "tts",
                        "name": "Tortoise",
                        "quality_features": {},
                    },
                ]

                response = client.get("/api/engines/compare?engines=xtts,tortoise")
                assert response.status_code == 200
                data = response.json()
                assert "comparison" in data

    def test_compare_engines_not_available(self):
        """Test engine comparison when router not available."""
        app = FastAPI()
        app.include_router(engines.router)
        client = TestClient(app)

        with patch("backend.api.routes.engines.ENGINE_AVAILABLE", False):
            response = client.get("/api/engines/compare?engines=xtts,tortoise")
            assert response.status_code == 200
            data = response.json()
            assert "available" in data
            assert data["available"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
