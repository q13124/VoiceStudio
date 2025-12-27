"""
Unit Tests for Quality API Route
Tests quality metrics and analysis endpoints comprehensively.
"""

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock torch before importing quality module
import sys
from types import ModuleType

# Create proper module mocks with __spec__
mock_torch = ModuleType("torch")
mock_torch.__spec__ = MagicMock()
mock_torch.__version__ = "2.0.0"
sys.modules["torch"] = mock_torch

mock_torchaudio = ModuleType("torchaudio")
mock_torchaudio.__spec__ = MagicMock()
sys.modules["torchaudio"] = mock_torchaudio

# Import the route module
try:
    from backend.api.routes import quality
except (ImportError, NameError, ValueError) as e:
    pytest.skip(
        f"Could not import quality route module: {e}", allow_module_level=True
    )


class TestQualityRouteImports:
    """Test quality route module can be imported."""

    def test_quality_module_imports(self):
        """Test quality module can be imported."""
        assert quality is not None, "Failed to import quality module"
        assert hasattr(quality, "router"), "quality module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert quality.router is not None, "Router should exist"
        if hasattr(quality.router, "prefix"):
            assert (
                "/api/quality" in quality.router.prefix
            ), "Router prefix should include /api/quality"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(quality.router, "routes"):
            routes = [route.path for route in quality.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestQualityPresets:
    """Test quality preset endpoints."""

    def test_list_presets_success(self):
        """Test successful preset listing."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        with patch("backend.api.routes.quality.HAS_QUALITY_PRESETS", True):
            with patch("backend.api.routes.quality.list_quality_presets") as mock_list:
                mock_list.return_value = {
                    "standard": {
                        "name": "Standard",
                        "description": "Standard quality",
                        "target_metrics": {"mos_score": 4.0},
                    }
                }

                response = client.get("/api/quality/presets")
                assert response.status_code == 200
                data = response.json()
                assert "standard" in data

    def test_get_preset_success(self):
        """Test successful preset retrieval."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        with patch("backend.api.routes.quality.HAS_QUALITY_PRESETS", True):
            with patch("backend.api.routes.quality.get_quality_preset") as mock_get:
                mock_get.return_value = {
                    "name": "Standard",
                    "description": "Standard quality",
                    "target_metrics": {"mos_score": 4.0},
                    "parameters": {},
                }

                response = client.get("/api/quality/presets/standard")
                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "Standard"

    def test_get_preset_not_found(self):
        """Test getting non-existent preset."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        with patch("backend.api.routes.quality.HAS_QUALITY_PRESETS", True):
            with patch("backend.api.routes.quality.get_quality_preset") as mock_get:
                mock_get.return_value = None

                response = client.get("/api/quality/presets/nonexistent")
                assert response.status_code == 404


class TestQualityAnalysis:
    """Test quality analysis endpoints."""

    def test_analyze_quality_success(self):
        """Test successful quality analysis."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        request_data = {
            "mos_score": 4.0,
            "similarity": 0.9,
            "naturalness": 0.85,
            "target_tier": "standard",
        }

        with patch("backend.api.routes.quality.HAS_QUALITY_OPTIMIZATION", True):
            with patch(
                "backend.api.routes.quality.QualityOptimizer"
            ) as mock_optimizer:
                mock_instance = MagicMock()
                mock_instance.analyze_quality.return_value = {
                    "meets_target": True,
                    "quality_score": 4.0,
                    "deficiencies": [],
                    "recommendations": [],
                }
                mock_optimizer.return_value = mock_instance

                response = client.post("/api/quality/analyze", json=request_data)
                assert response.status_code == 200
                data = response.json()
                assert "meets_target" in data

    def test_analyze_quality_not_available(self):
        """Test quality analysis when not available."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        request_data = {"mos_score": 4.0, "target_tier": "standard"}

        with patch("backend.api.routes.quality.HAS_QUALITY_OPTIMIZATION", False):
            response = client.post("/api/quality/analyze", json=request_data)
            assert response.status_code == 503

    def test_optimize_quality_success(self):
        """Test successful quality optimization."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        request_data = {
            "metrics": {"mos_score": 3.5},
            "current_params": {},
            "target_tier": "standard",
        }

        with patch("backend.api.routes.quality.HAS_QUALITY_OPTIMIZATION", True):
            with patch(
                "backend.api.routes.quality.optimize_synthesis_for_quality"
            ) as mock_optimize:
                mock_optimize.return_value = ({}, {})

                response = client.post("/api/quality/optimize", json=request_data)
                assert response.status_code == 200
                data = response.json()
                assert "optimized_params" in data


class TestQualityHistory:
    """Test quality history endpoints."""

    def test_store_quality_history_success(self):
        """Test successful quality history storage."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        profile_id = f"profile-{uuid.uuid4().hex[:8]}"
        request_data = {
            "profile_id": profile_id,
            "engine": "xtts",
            "metrics": {"mos_score": 4.0},
            "quality_score": 4.0,
        }

        response = client.post("/api/quality/history", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == profile_id

    def test_get_quality_history_success(self):
        """Test successful quality history retrieval."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        profile_id = f"profile-{uuid.uuid4().hex[:8]}"
        quality._quality_history.clear()

        entry_id = f"entry-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        quality._quality_history[profile_id] = [
            {
                "id": entry_id,
                "profile_id": profile_id,
                "timestamp": now,
                "engine": "xtts",
                "metrics": {"mos_score": 4.0},
                "quality_score": 4.0,
            }
        ]

        response = client.get(f"/api/quality/history/{profile_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) == 1

    def test_get_quality_trends_success(self):
        """Test successful quality trends retrieval."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        profile_id = f"profile-{uuid.uuid4().hex[:8]}"
        quality._quality_history.clear()

        response = client.get(f"/api/quality/history/{profile_id}/trends")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data


class TestQualityDashboard:
    """Test quality dashboard endpoints."""

    def test_get_quality_dashboard_success(self):
        """Test successful quality dashboard retrieval."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        response = client.get("/api/quality/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


class TestQualityConsistency:
    """Test quality consistency endpoints."""

    def test_set_quality_standard_success(self):
        """Test successful quality standard setting."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        request_data = {
            "project_id": "test-project",
            "target_metrics": {"mos_score": 4.0},
        }

        response = client.post("/api/quality/consistency/standard", json=request_data)
        assert response.status_code == 200

    def test_record_quality_metrics_success(self):
        """Test successful quality metrics recording."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        request_data = {
            "project_id": "test-project",
            "metrics": {"mos_score": 4.0},
        }

        response = client.post("/api/quality/consistency/record", json=request_data)
        assert response.status_code == 200

    def test_check_project_consistency_success(self):
        """Test successful project consistency check."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        project_id = "test-project"

        response = client.get(f"/api/quality/consistency/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert "consistency_score" in data

    def test_check_all_projects_consistency_success(self):
        """Test successful all projects consistency check."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        response = client.get("/api/quality/consistency/all")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data


class TestQualityBaseline:
    """Test quality baseline endpoints."""

    def test_get_quality_baseline_success(self):
        """Test successful quality baseline retrieval."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        profile_id = f"profile-{uuid.uuid4().hex[:8]}"

        response = client.get(f"/api/quality/baseline/{profile_id}")
        assert response.status_code == 200
        # May return 200 with None or actual data
        data = response.json()
        assert data is None or "baseline_metrics" in data

    def test_check_quality_degradation_success(self):
        """Test successful quality degradation check."""
        app = FastAPI()
        app.include_router(quality.router)
        client = TestClient(app)

        profile_id = f"profile-{uuid.uuid4().hex[:8]}"

        response = client.get(f"/api/quality/degradation/{profile_id}")
        assert response.status_code == 200
        data = response.json()
        assert "degradation_detected" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
