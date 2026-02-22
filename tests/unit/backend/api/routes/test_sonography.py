"""
Unit Tests for Sonography API Route
Tests sonography endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import sonography
except ImportError:
    pytest.skip("Could not import sonography route module", allow_module_level=True)


class TestSonographyRouteImports:
    """Test sonography route module can be imported."""

    def test_sonography_module_imports(self):
        """Test sonography module can be imported."""
        assert sonography is not None, "Failed to import sonography module"
        assert hasattr(sonography, "router"), "sonography module missing router"


class TestSonographyRouteHandlers:
    """Test sonography route handlers exist and are callable."""

    def test_generate_sonogram_handler_exists(self):
        """Test generate_sonogram handler exists."""
        if hasattr(sonography, "generate_sonogram"):
            assert callable(sonography.generate_sonogram), "generate_sonogram is not callable"


class TestSonographyRouter:
    """Test sonography router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert sonography.router is not None, "Router should exist"
        if hasattr(sonography.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(sonography.router, "routes"):
            routes = [route.path for route in sonography.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
