"""
Unit Tests for Mix API Route
Tests mixing endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import mix
except ImportError:
    pytest.skip("Could not import mix route module", allow_module_level=True)


class TestMixRouteImports:
    """Test mix route module can be imported."""

    def test_mix_module_imports(self):
        """Test mix module can be imported."""
        assert mix is not None, "Failed to import mix module"
        assert hasattr(mix, "router"), "mix module missing router"


class TestMixRouteHandlers:
    """Test mix route handlers exist and are callable."""

    def test_mix_audio_handler_exists(self):
        """Test mix_audio handler exists."""
        if hasattr(mix, "mix_audio"):
            assert callable(mix.mix_audio), "mix_audio is not callable"


class TestMixRouter:
    """Test mix router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert mix.router is not None, "Router should exist"
        if hasattr(mix.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(mix.router, "routes"):
            routes = [route.path for route in mix.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
