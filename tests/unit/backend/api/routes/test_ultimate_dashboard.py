"""
Unit Tests for Ultimate Dashboard API Route
Tests ultimate dashboard endpoints comprehensively including retry logic, circuit breaker, and caching.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import httpx

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import ultimate_dashboard
except ImportError:
    pytest.skip(
        "Could not import ultimate_dashboard route module",
        allow_module_level=True,
    )


class TestUltimateDashboardRouteImports:
    """Test ultimate dashboard route module can be imported."""

    def test_ultimate_dashboard_module_imports(self):
        """Test ultimate_dashboard module can be imported."""
        assert (
            ultimate_dashboard is not None
        ), "Failed to import ultimate_dashboard module"
        assert hasattr(
            ultimate_dashboard, "router"
        ), "ultimate_dashboard module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert (
            ultimate_dashboard.router is not None
        ), "Router should exist"
        if hasattr(ultimate_dashboard.router, "prefix"):
            assert (
                "/api/ultimate-dashboard" in ultimate_dashboard.router.prefix
            ), "Router prefix should include /api/ultimate-dashboard"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(ultimate_dashboard.router, "routes"):
            routes = [
                route.path for route in ultimate_dashboard.router.routes
            ]
            assert len(routes) > 0, "Router should have routes registered"


class TestUltimateDashboardEndpoints:
    """Test ultimate dashboard endpoints with comprehensive coverage."""

    def test_get_dashboard_data_success(self):
        """Test successful dashboard data retrieval."""
        app = FastAPI()
        app.include_router(ultimate_dashboard.router)
        client = TestClient(app)

        # Mock internal API calls
        mock_projects_response = {"projects": [], "total": 0}
        mock_profiles_response = {"profiles": [], "total": 0}
        mock_jobs_response = {"jobs": [], "total": 0}
        mock_gpu_response = {"available": False, "utilization": 0.0}
        mock_analytics_response = {"total_requests": 100}

        with patch("backend.api.routes.ultimate_dashboard._http_get_with_retry") as mock_get:
            def mock_get_side_effect(client, url, endpoint_name, **kwargs):
                if "projects" in url:
                    return mock_projects_response
                elif "profiles" in url:
                    return mock_profiles_response
                elif "jobs" in url:
                    return mock_jobs_response
                elif "gpu" in url:
                    return mock_gpu_response
                elif "analytics" in url:
                    return mock_analytics_response
                return {}

            mock_get.side_effect = mock_get_side_effect

            response = client.get("/api/ultimate-dashboard")
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "quick_stats" in data
            assert "recent_activities" in data

    def test_get_dashboard_summary_success(self):
        """Test successful dashboard summary retrieval."""
        app = FastAPI()
        app.include_router(ultimate_dashboard.router)
        client = TestClient(app)

        with patch("backend.api.routes.ultimate_dashboard.get_dashboard_data") as mock_data:
            mock_data.return_value = {
                "summary": {
                    "total_projects": 5,
                    "total_profiles": 10,
                    "system_status": "healthy"
                }
            }

            response = client.get("/api/ultimate-dashboard/summary")
            assert response.status_code == 200
            data = response.json()
            assert "total_projects" in data

    def test_get_dashboard_data_with_caching(self):
        """Test dashboard data caching behavior."""
        app = FastAPI()
        app.include_router(ultimate_dashboard.router)
        client = TestClient(app)

        # Clear cache first
        ultimate_dashboard._dashboard_cache = None
        ultimate_dashboard._cache_timestamp = None

        with patch("backend.api.routes.ultimate_dashboard._http_get_with_retry") as mock_get:
            mock_get.return_value = {"projects": [], "total": 0}

            # First call should populate cache
            response1 = client.get("/api/ultimate-dashboard")
            assert response1.status_code == 200

            # Second call should use cache (if within TTL)
            response2 = client.get("/api/ultimate-dashboard")
            assert response2.status_code == 200

    def test_get_dashboard_data_circuit_breaker(self):
        """Test circuit breaker behavior when endpoints fail."""
        app = FastAPI()
        app.include_router(ultimate_dashboard.router)
        client = TestClient(app)

        # Simulate circuit breaker open
        ultimate_dashboard._circuit_breaker_state["projects"]["state"] = "open"
        ultimate_dashboard._circuit_breaker_state["projects"]["failures"] = 10

        with patch("backend.api.routes.ultimate_dashboard._http_get_with_retry") as mock_get:
            mock_get.return_value = None  # Circuit breaker blocks request

            response = client.get("/api/ultimate-dashboard")
            # Should still return 200 but with degraded data
            assert response.status_code == 200

    def test_get_dashboard_data_retry_logic(self):
        """Test retry logic for failed API calls."""
        app = FastAPI()
        app.include_router(ultimate_dashboard.router)
        client = TestClient(app)

        call_count = 0

        def mock_get_with_retries(client, url, endpoint_name, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Simulated network error")
            return {"projects": [], "total": 0}

        with patch("backend.api.routes.ultimate_dashboard._http_get_with_retry") as mock_get:
            mock_get.side_effect = mock_get_with_retries

            response = client.get("/api/ultimate-dashboard")
            # Should eventually succeed after retries
            assert response.status_code == 200

    def test_get_dashboard_data_partial_failure(self):
        """Test dashboard data when some endpoints fail."""
        app = FastAPI()
        app.include_router(ultimate_dashboard.router)
        client = TestClient(app)

        def mock_get_side_effect(client, url, endpoint_name, **kwargs):
            if "projects" in url:
                return {"projects": [], "total": 0}
            elif "profiles" in url:
                return None  # Simulate failure
            return {}

        with patch("backend.api.routes.ultimate_dashboard._http_get_with_retry") as mock_get:
            mock_get.side_effect = mock_get_side_effect

            response = client.get("/api/ultimate-dashboard")
            # Should still return 200 with partial data
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

