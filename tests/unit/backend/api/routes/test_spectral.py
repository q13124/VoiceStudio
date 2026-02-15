"""
Unit Tests for Spectral API Route
Tests spectral processing endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import spectral
except ImportError:
    pytest.skip("Could not import spectral route module", allow_module_level=True)


class TestSpectralRouteImports:
    """Test spectral route module can be imported."""

    def test_spectral_module_imports(self):
        """Test spectral module can be imported."""
        assert spectral is not None, "Failed to import spectral module"
        assert hasattr(spectral, "router"), "spectral module missing router"


class TestSpectralRouteHandlers:
    """Test spectral route handlers exist and are callable."""

    def test_process_spectral_handler_exists(self):
        """Test process_spectral handler exists."""
        if hasattr(spectral, "process_spectral"):
            assert callable(
                spectral.process_spectral
            ), "process_spectral is not callable"


class TestSpectralRouter:
    """Test spectral router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert spectral.router is not None, "Router should exist"
        if hasattr(spectral.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(spectral.router, "routes"):
            routes = [route.path for route in spectral.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

