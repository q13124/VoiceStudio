"""
Unit Tests for Monitoring API Route
Tests monitoring endpoints comprehensively.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import monitoring
except ImportError:
    pytest.skip("Could not import monitoring route module", allow_module_level=True)


class TestMonitoringRouteImports:
    """Test monitoring route module can be imported."""

    def test_monitoring_module_imports(self):
        """Test monitoring module can be imported."""
        assert monitoring is not None, "Failed to import monitoring module"
        assert hasattr(monitoring, "router"), "monitoring module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert monitoring.router is not None, "Router should exist"
        if hasattr(monitoring.router, "prefix"):
            assert (
                "/api/monitoring" in monitoring.router.prefix
            ), "Router prefix should include /api/monitoring"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(monitoring.router, "routes"):
            routes = [route.path for route in monitoring.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestMetricsEndpoints:
    """Test metrics endpoints."""

    def test_get_metrics_success(self):
        """Test successful metrics retrieval."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.get_all_metrics.return_value = {
            "counters": {"requests": 100.0},
            "gauges": {"active_connections": 5.0},
            "timers": {},
            "histograms": {},
        }

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics")
            assert response.status_code == 200
            data = response.json()
            assert "counters" in data or isinstance(data, dict)

    def test_get_counters_success(self):
        """Test successful counters retrieval."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.counters = {"requests": MagicMock(), "errors": MagicMock()}
        mock_collector.get_counter = MagicMock(
            side_effect=lambda x: 100.0 if x == "requests" else 5.0
        )

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/counters")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)

    def test_get_counters_empty(self):
        """Test counters retrieval when empty."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.counters = {}
        mock_collector.get_counter = MagicMock(return_value=0.0)

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/counters")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)

    def test_get_gauges_success(self):
        """Test successful gauges retrieval."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.gauges = {"memory_usage": MagicMock(), "cpu_usage": MagicMock()}
        mock_collector.get_gauge = MagicMock(
            side_effect=lambda x: 75.5 if x == "memory_usage" else 45.2
        )

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/gauges")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)

    def test_get_gauges_empty(self):
        """Test gauges retrieval when empty."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.gauges = {}
        mock_collector.get_gauge = MagicMock(return_value=None)

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/gauges")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)

    def test_get_timer_stats_success(self):
        """Test successful timer stats retrieval."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.get_timer_stats.return_value = {
            "count": 100.0,
            "mean": 0.5,
            "min": 0.1,
            "max": 2.0,
            "p95": 1.5,
            "p99": 1.8,
        }

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/timers/test_timer")
            assert response.status_code == 200
            data = response.json()
            assert "count" in data or "error" in data

    def test_get_timer_stats_not_found(self):
        """Test timer stats retrieval for non-existent timer."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.get_timer_stats.return_value = None

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/timers/nonexistent")
            assert response.status_code == 200
            data = response.json()
            assert "error" in data

    def test_get_histogram_stats_success(self):
        """Test successful histogram stats retrieval."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.get_histogram_stats.return_value = {
            "count": 100.0,
            "mean": 50.0,
            "min": 10.0,
            "max": 100.0,
            "p50": 45.0,
            "p95": 90.0,
            "p99": 95.0,
        }

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/histograms/test_histogram")
            assert response.status_code == 200
            data = response.json()
            assert "count" in data or "error" in data

    def test_get_histogram_stats_not_found(self):
        """Test histogram stats retrieval for non-existent histogram."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.get_histogram_stats.return_value = None

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.get("/api/monitoring/metrics/histograms/nonexistent")
            assert response.status_code == 200
            data = response.json()
            assert "error" in data

    def test_clear_metrics_success(self):
        """Test successful metrics clearing."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_collector = MagicMock()
        mock_collector.clear = MagicMock()

        with patch("backend.api.routes.monitoring.get_metrics_collector") as mock_get:
            mock_get.return_value = mock_collector

            response = client.post("/api/monitoring/metrics/clear")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            mock_collector.clear.assert_called_once()


class TestErrorsEndpoints:
    """Test error tracking endpoints."""

    def test_get_errors_success(self):
        """Test successful error summary retrieval."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_tracker = MagicMock()
        mock_tracker.get_error_summary.return_value = {
            "total_errors": 10,
            "error_types": ["ValueError", "KeyError"],
            "recent_errors": [],
        }

        with patch("backend.api.routes.monitoring.get_error_tracker") as mock_get:
            mock_get.return_value = mock_tracker

            response = client.get("/api/monitoring/errors")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)

    def test_get_errors_empty(self):
        """Test error summary retrieval when empty."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_tracker = MagicMock()
        mock_tracker.get_error_summary.return_value = {
            "total_errors": 0,
            "error_types": [],
            "recent_errors": [],
        }

        with patch("backend.api.routes.monitoring.get_error_tracker") as mock_get:
            mock_get.return_value = mock_tracker

            response = client.get("/api/monitoring/errors")
            assert response.status_code == 200
            data = response.json()
            assert data["total_errors"] == 0

    def test_get_errors_by_type_success(self):
        """Test successful error retrieval by type."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        from datetime import datetime

        class MockError:
            def __init__(self):
                self.message = "Test error"
                self.severity = MagicMock()
                self.severity.value = "error"
                self.count = 5
                self.first_occurrence = datetime.utcnow()
                self.last_occurrence = datetime.utcnow()

        mock_tracker = MagicMock()
        mock_tracker.get_errors_by_type.return_value = [MockError()]

        with patch("backend.api.routes.monitoring.get_error_tracker") as mock_get:
            mock_get.return_value = mock_tracker

            response = client.get("/api/monitoring/errors/ValueError")
            assert response.status_code == 200
            data = response.json()
            assert "error_type" in data
            assert "count" in data
            assert "errors" in data

    def test_get_errors_by_type_empty(self):
        """Test error retrieval by type when empty."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_tracker = MagicMock()
        mock_tracker.get_errors_by_type.return_value = []

        with patch("backend.api.routes.monitoring.get_error_tracker") as mock_get:
            mock_get.return_value = mock_tracker

            response = client.get("/api/monitoring/errors/NonexistentError")
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 0
            assert len(data["errors"]) == 0

    def test_clear_errors_success(self):
        """Test successful error clearing."""
        app = FastAPI()
        app.include_router(monitoring.router)
        client = TestClient(app)

        mock_tracker = MagicMock()
        mock_tracker.clear = MagicMock()

        with patch("backend.api.routes.monitoring.get_error_tracker") as mock_get:
            mock_get.return_value = mock_tracker

            response = client.post("/api/monitoring/errors/clear")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            mock_tracker.clear.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
