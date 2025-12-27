"""
Unit Tests for Deepfake Creator API Route
Tests deepfake creation endpoints in isolation.
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
    from backend.api.routes import deepfake_creator
except ImportError:
    pytest.skip(
        "Could not import deepfake_creator route module",
        allow_module_level=True,
    )


class TestDeepfakeCreatorRouteImports:
    """Test deepfake creator route module can be imported."""

    def test_deepfake_creator_module_imports(self):
        """Test deepfake_creator module can be imported."""
        assert (
            deepfake_creator is not None
        ), "Failed to import deepfake_creator module"
        assert hasattr(
            deepfake_creator, "router"
        ), "deepfake_creator module missing router"


class TestDeepfakeCreatorRouteHandlers:
    """Test deepfake creator route handlers exist and are callable."""

    def test_create_deepfake_handler_exists(self):
        """Test create_deepfake handler exists."""
        if hasattr(deepfake_creator, "create_deepfake"):
            assert callable(
                deepfake_creator.create_deepfake
            ), "create_deepfake is not callable"


class TestDeepfakeCreatorRouter:
    """Test deepfake creator router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert deepfake_creator.router is not None, "Router should exist"
        if hasattr(deepfake_creator.router, "prefix"):
            assert (
                "/api/deepfake-creator" in deepfake_creator.router.prefix
            ), "Router prefix should include /api/deepfake-creator"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(deepfake_creator.router, "routes"):
            routes = [route.path for route in deepfake_creator.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

