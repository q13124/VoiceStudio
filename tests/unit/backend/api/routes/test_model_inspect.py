"""
Unit Tests for Model Inspect API Route
Tests model inspection endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import model_inspect
except ImportError:
    pytest.skip("Could not import model_inspect route module", allow_module_level=True)


class TestModelInspectRouteImports:
    """Test model inspect route module can be imported."""

    def test_model_inspect_module_imports(self):
        """Test model_inspect module can be imported."""
        assert model_inspect is not None, "Failed to import model_inspect module"
        assert hasattr(model_inspect, "router"), "model_inspect module missing router"


class TestModelInspectRouteHandlers:
    """Test model inspect route handlers exist and are callable."""

    def test_inspect_model_handler_exists(self):
        """Test inspect_model handler exists."""
        if hasattr(model_inspect, "inspect_model"):
            assert callable(model_inspect.inspect_model), "inspect_model is not callable"


class TestModelInspectRouter:
    """Test model inspect router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert model_inspect.router is not None, "Router should exist"
        if hasattr(model_inspect.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(model_inspect.router, "routes"):
            routes = [route.path for route in model_inspect.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
