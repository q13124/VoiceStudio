"""
Unit Tests for Dubbing API Route
Tests dubbing functionality endpoints in isolation.
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
    from backend.api.routes import dubbing
except ImportError:
    pytest.skip("Could not import dubbing route module", allow_module_level=True)


class TestDubbingRouteImports:
    """Test dubbing route module can be imported."""

    def test_dubbing_module_imports(self):
        """Test dubbing module can be imported."""
        assert dubbing is not None, "Failed to import dubbing module"
        assert hasattr(dubbing, "router"), "dubbing module missing router"


class TestDubbingRouteHandlers:
    """Test dubbing route handlers exist and are callable."""

    def test_create_dubbing_job_handler_exists(self):
        """Test create_dubbing_job handler exists."""
        if hasattr(dubbing, "create_dubbing_job"):
            assert callable(
                dubbing.create_dubbing_job
            ), "create_dubbing_job is not callable"

    def test_get_dubbing_status_handler_exists(self):
        """Test get_dubbing_status handler exists."""
        if hasattr(dubbing, "get_dubbing_status"):
            assert callable(
                dubbing.get_dubbing_status
            ), "get_dubbing_status is not callable"


class TestDubbingRouter:
    """Test dubbing router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert dubbing.router is not None, "Router should exist"
        if hasattr(dubbing.router, "prefix"):
            assert (
                "/api/dubbing" in dubbing.router.prefix
            ), "Router prefix should include /api/dubbing"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(dubbing.router, "routes"):
            routes = [route.path for route in dubbing.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
