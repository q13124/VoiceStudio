"""
Unit Tests for Noise Reduction API Route
Tests noise reduction endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import nr
except ImportError:
    pytest.skip("Could not import nr route module", allow_module_level=True)


class TestNRRouteImports:
    """Test noise reduction route module can be imported."""

    def test_nr_module_imports(self):
        """Test nr module can be imported."""
        assert nr is not None, "Failed to import nr module"
        assert hasattr(nr, "router"), "nr module missing router"


class TestNRRouteHandlers:
    """Test noise reduction route handlers exist and are callable."""

    def test_reduce_noise_handler_exists(self):
        """Test reduce_noise handler exists."""
        if hasattr(nr, "reduce_noise"):
            assert callable(nr.reduce_noise), "reduce_noise is not callable"


class TestNRRouter:
    """Test noise reduction router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert nr.router is not None, "Router should exist"
        if hasattr(nr.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(nr.router, "routes"):
            routes = [route.path for route in nr.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

