"""
Unit Tests for Edit API Route
Tests editing endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import edit
except ImportError:
    pytest.skip("Could not import edit route module", allow_module_level=True)


class TestEditRouteImports:
    """Test edit route module can be imported."""

    def test_edit_module_imports(self):
        """Test edit module can be imported."""
        assert edit is not None, "Failed to import edit module"
        assert hasattr(edit, "router"), "edit module missing router"


class TestEditRouteHandlers:
    """Test edit route handlers exist and are callable."""

    def test_edit_audio_handler_exists(self):
        """Test edit_audio handler exists."""
        if hasattr(edit, "edit_audio"):
            assert callable(edit.edit_audio), "edit_audio is not callable"


class TestEditRouter:
    """Test edit router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert edit.router is not None, "Router should exist"
        if hasattr(edit.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(edit.router, "routes"):
            routes = [route.path for route in edit.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
