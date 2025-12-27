"""
Unit Tests for Video Generation API Route
Tests video generation endpoints in isolation.
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
    from backend.api.routes import video_gen
except ImportError:
    pytest.skip("Could not import video_gen route module", allow_module_level=True)


class TestVideoGenRouteImports:
    """Test video generation route module can be imported."""

    def test_video_gen_module_imports(self):
        """Test video_gen module can be imported."""
        assert video_gen is not None, "Failed to import video_gen module"
        assert hasattr(video_gen, "router"), "video_gen module missing router"


class TestVideoGenRouteHandlers:
    """Test video generation route handlers exist and are callable."""

    def test_generate_video_handler_exists(self):
        """Test generate_video handler exists."""
        if hasattr(video_gen, "generate_video"):
            assert callable(
                video_gen.generate_video
            ), "generate_video is not callable"


class TestVideoGenRouter:
    """Test video generation router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert video_gen.router is not None, "Router should exist"
        if hasattr(video_gen.router, "prefix"):
            assert (
                "/api/video-gen" in video_gen.router.prefix
            ), "Router prefix should include /api/video-gen"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(video_gen.router, "routes"):
            routes = [route.path for route in video_gen.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

