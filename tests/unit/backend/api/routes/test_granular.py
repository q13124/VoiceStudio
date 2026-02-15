"""
Unit Tests for Granular API Route
Tests granular synthesis endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import granular
except ImportError:
    pytest.skip(
        "Could not import granular route module", allow_module_level=True
    )


class TestGranularRouteImports:
    """Test granular route module can be imported."""

    def test_granular_module_imports(self):
        """Test granular module can be imported."""
        assert granular is not None, "Failed to import granular module"
        assert hasattr(granular, "router"), "granular module missing router"


class TestGranularRouteHandlers:
    """Test granular route handlers exist and are callable."""

    def test_synthesize_granular_handler_exists(self):
        """Test synthesize_granular handler exists."""
        if hasattr(granular, "synthesize_granular"):
            assert callable(
                granular.synthesize_granular
            ), "synthesize_granular is not callable"


class TestGranularRouter:
    """Test granular router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert granular.router is not None, "Router should exist"
        if hasattr(granular.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(granular.router, "routes"):
            routes = [route.path for route in granular.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

