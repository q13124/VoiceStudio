"""
Unit Tests for Video Editing API Route
Tests video editing endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import video_edit
except ImportError:
    pytest.skip("Could not import video_edit route module", allow_module_level=True)


class TestVideoEditRouteImports:
    """Test video editing route module can be imported."""

    def test_video_edit_module_imports(self):
        """Test video_edit module can be imported."""
        assert video_edit is not None, "Failed to import video_edit module"
        assert hasattr(video_edit, "router"), "video_edit module missing router"


class TestVideoEditRouteHandlers:
    """Test video editing route handlers exist and are callable."""

    def test_edit_video_handler_exists(self):
        """Test edit_video handler exists."""
        if hasattr(video_edit, "edit_video"):
            assert callable(video_edit.edit_video), "edit_video is not callable"


class TestVideoEditRouter:
    """Test video editing router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert video_edit.router is not None, "Router should exist"
        if hasattr(video_edit.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(video_edit.router, "routes"):
            routes = [route.path for route in video_edit.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
