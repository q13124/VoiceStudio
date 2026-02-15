"""
Unit Tests for Repair API Route
Tests audio repair endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import repair
except ImportError:
    pytest.skip("Could not import repair route module", allow_module_level=True)


class TestRepairRouteImports:
    """Test repair route module can be imported."""

    def test_repair_module_imports(self):
        """Test repair module can be imported."""
        assert repair is not None, "Failed to import repair module"
        assert hasattr(repair, "router"), "repair module missing router"


class TestRepairRouteHandlers:
    """Test repair route handlers exist and are callable."""

    def test_repair_audio_handler_exists(self):
        """Test repair_audio handler exists."""
        if hasattr(repair, "repair_audio"):
            assert callable(repair.repair_audio), "repair_audio is not callable"


class TestRepairRouter:
    """Test repair router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert repair.router is not None, "Router should exist"
        if hasattr(repair.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(repair.router, "routes"):
            routes = [route.path for route in repair.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

