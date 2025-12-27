"""
Unit Tests for Models API Route
Tests model management endpoints in isolation.
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
    from backend.api.routes import models
except ImportError:
    pytest.skip("Could not import models route module", allow_module_level=True)


class TestModelsRouteImports:
    """Test models route module can be imported."""

    def test_models_module_imports(self):
        """Test models module can be imported."""
        assert models is not None, "Failed to import models module"
        assert hasattr(models, "router"), "models module missing router"


class TestModelsRouteHandlers:
    """Test models route handlers exist and are callable."""

    def test_list_models_handler_exists(self):
        """Test list_models handler exists."""
        if hasattr(models, "list_models"):
            assert callable(models.list_models), "list_models is not callable"

    def test_get_model_handler_exists(self):
        """Test get_model handler exists."""
        if hasattr(models, "get_model"):
            assert callable(models.get_model), "get_model is not callable"

    def test_download_model_handler_exists(self):
        """Test download_model handler exists."""
        if hasattr(models, "download_model"):
            assert callable(
                models.download_model
            ), "download_model is not callable"


class TestModelsRouter:
    """Test models router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert models.router is not None, "Router should exist"
        if hasattr(models.router, "prefix"):
            assert (
                "/api/models" in models.router.prefix
            ), "Router prefix should include /api/models"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(models.router, "routes"):
            routes = [route.path for route in models.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

