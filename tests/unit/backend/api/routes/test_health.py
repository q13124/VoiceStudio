"""
Unit Tests for Health API Route
Tests health check endpoints comprehensively.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import health
except ImportError:
    pytest.skip("Could not import health route module", allow_module_level=True)


class TestHealthRouteImports:
    """Test health route module can be imported."""

    def test_health_module_imports(self):
        """Test health module can be imported."""
        assert health is not None, "Failed to import health module"
        assert hasattr(health, "router"), "health module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert health.router is not None, "Router should exist"
        if hasattr(health.router, "prefix"):
            assert (
                "/api/health" in health.router.prefix
            ), "Router prefix should include /api/health"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(health.router, "routes"):
            routes = [route.path for route in health.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check_success(self):
        """Test successful health check."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health._health_checker.run_all_checks"
        ) as mock_checks:
            mock_checks.return_value = {
                "database": MagicMock(
                    status=MagicMock(value="healthy"),
                    message="OK",
                    response_time_ms=10.0,
                )
            }

            with patch(
                "backend.api.routes.health._health_checker.get_overall_status"
            ) as mock_status:
                mock_status.return_value = MagicMock(value="healthy")

                response = client.get("/api/health/")
                assert response.status_code == 200
                data = response.json()
                assert "status" in data
                assert "timestamp" in data

    def test_simple_health_check_success(self):
        """Test successful simple health check."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        response = client.get("/api/health/simple")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_detailed_health_check_success(self):
        """Test successful detailed health check."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health._health_checker.run_all_checks"
        ) as mock_checks:
            mock_checks.return_value = {
                "database": MagicMock(
                    status=MagicMock(value="healthy"),
                    message="OK",
                    response_time_ms=10.0,
                    error=None,
                    details={},
                )
            }

            with patch(
                "backend.api.routes.health._health_checker.get_overall_status"
            ) as mock_status:
                mock_status.return_value = MagicMock(value="healthy")

                with patch(
                    "backend.api.routes.health._get_system_metrics"
                ) as mock_metrics:
                    mock_metrics.return_value = {"cpu_percent": 50.0}

                    with patch(
                        "backend.api.routes.health._get_resource_usage"
                    ) as mock_resources:
                        mock_resources.return_value = {}

                        with patch(
                            "backend.api.routes.health._check_engines"
                        ) as mock_engines:
                            mock_engines.return_value = {"status": "healthy"}

                            response = client.get("/api/health/detailed")
                            assert response.status_code == 200
                            data = response.json()
                            assert "status" in data
                            assert "system" in data

    def test_readiness_check_success(self):
        """Test successful readiness check."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health._health_checker.run_all_checks"
        ) as mock_checks:
            mock_checks.return_value = {
                "database": MagicMock(
                    status=MagicMock(value="healthy"),
                    message="OK",
                )
            }

            with patch(
                "backend.api.routes.health._health_checker.checks",
                {"database": {"critical": True}},
            ):
                response = client.get("/api/health/readiness")
                assert response.status_code == 200
                data = response.json()
                assert data["ready"] is True

    def test_readiness_check_failure(self):
        """Test readiness check failure."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health._health_checker.run_all_checks"
        ) as mock_checks:
            mock_checks.return_value = {
                "database": MagicMock(
                    status=MagicMock(value="unhealthy"),
                    message="Failed",
                )
            }

            with patch(
                "backend.api.routes.health._health_checker.checks",
                {"database": {"critical": True}},
            ):
                response = client.get("/api/health/readiness")
                assert response.status_code == 503

    def test_liveness_check_success(self):
        """Test successful liveness check."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        response = client.get("/api/health/liveness")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert data["status"] == "alive"

    def test_preflight_check_success(self, tmp_path):
        """Test preflight check returns readiness report."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        projects_dir = tmp_path / "projects"
        cache_dir = tmp_path / "cache"
        registry_path = tmp_path / "cache" / "audio_registry.json"

        mock_project_store = MagicMock()
        mock_project_store.projects_dir = projects_dir

        mock_audio_cache = MagicMock()
        mock_audio_cache.cache_dir = cache_dir

        mock_registry = MagicMock()
        mock_registry.registry_path = registry_path

        mock_engine_config = MagicMock()
        mock_engine_config.config = {"model_paths": {"base": str(tmp_path / "models")}}

        with patch(
            "backend.services.ProjectStoreService.get_project_store_service",
            return_value=mock_project_store,
        ), patch(
            "backend.services.ContentAddressedAudioCache.get_audio_cache",
            return_value=mock_audio_cache,
        ), patch(
            "backend.services.AudioArtifactRegistry.get_audio_registry",
            return_value=mock_registry,
        ), patch(
            "backend.services.EngineConfigService.get_engine_config_service",
            return_value=mock_engine_config,
        ), patch(
            "backend.api.routes.health.shutil.which",
            return_value=str(tmp_path / "ffmpeg.exe"),
        ), patch.dict(
            "os.environ",
            {"VOICESTUDIO_MODELS_PATH": str(tmp_path / "models")},
            clear=False,
        ):
            response = client.get("/api/health/preflight")
            assert response.status_code == 200
            data = response.json()
            assert "ok" in data
            assert "checks" in data
            assert data["checks"]["projects_root"]["ok"] is True
            assert data["checks"]["cache_root"]["ok"] is True
            assert data["checks"]["model_root"]["ok"] is True
            assert data["checks"]["ffmpeg"]["ok"] is True

    def test_resource_usage_success(self):
        """Test successful resource usage retrieval."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health._get_system_metrics"
        ) as mock_metrics:
            mock_metrics.return_value = {"cpu_percent": 50.0}

            with patch(
                "backend.api.routes.health._get_resource_usage"
            ) as mock_resources:
                mock_resources.return_value = {"gpu": {"available": False}}

                response = client.get("/api/health/resources")
                assert response.status_code == 200
                data = response.json()
                assert "system" in data
                assert "resources" in data

    def test_engine_health_success(self):
        """Test successful engine health retrieval."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch("backend.api.routes.health._check_engines") as mock_engines:
            mock_engines.return_value = {
                "status": "healthy",
                "available_engines": 5,
            }

            response = client.get("/api/health/engines")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data

    def test_performance_metrics_success(self):
        """Test successful performance metrics retrieval."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health.get_performance_middleware"
        ) as mock_middleware:
            mock_middleware.return_value = MagicMock(
                get_stats=lambda: {"total_requests": 100}
            )

            response = client.get("/api/health/performance")
            assert response.status_code == 200
            data = response.json()
            assert "timestamp" in data

    def test_performance_metrics_not_initialized(self):
        """Test performance metrics when middleware not initialized."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health.get_performance_middleware"
        ) as mock_middleware:
            mock_middleware.return_value = None

            response = client.get("/api/health/performance")
            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] is False

    def test_endpoint_performance_metrics_success(self):
        """Test successful endpoint performance metrics."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health.get_performance_middleware"
        ) as mock_middleware:
            mock_middleware.return_value = MagicMock(
                get_metrics=lambda endpoint: {"avg_time_ms": 50.0}
            )

            response = client.get("/api/health/performance/GET:/api/test")
            assert response.status_code == 200
            data = response.json()
            assert "endpoint" in data

    def test_endpoint_performance_metrics_not_found(self):
        """Test endpoint performance metrics not found."""
        app = FastAPI()
        app.include_router(health.router)
        client = TestClient(app)

        with patch(
            "backend.api.routes.health.get_performance_middleware"
        ) as mock_middleware:
            mock_middleware.return_value = MagicMock(get_metrics=lambda x: None)

            response = client.get("/api/health/performance/nonexistent")
            assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
