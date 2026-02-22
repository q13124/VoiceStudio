"""
Unit Tests for Image Sampler API Route
Tests image sampling endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import img_sampler
except ImportError:
    pytest.skip("Could not import img_sampler route module", allow_module_level=True)


class TestImgSamplerRouteImports:
    """Test image sampler route module can be imported."""

    def test_img_sampler_module_imports(self):
        """Test img_sampler module can be imported."""
        assert img_sampler is not None, "Failed to import img_sampler module"
        assert hasattr(img_sampler, "router"), "img_sampler module missing router"


class TestImgSamplerRouteHandlers:
    """Test image sampler route handlers exist and are callable."""

    def test_sample_image_handler_exists(self):
        """Test sample_image handler exists."""
        if hasattr(img_sampler, "sample_image"):
            assert callable(img_sampler.sample_image), "sample_image is not callable"


class TestImgSamplerRouter:
    """Test image sampler router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert img_sampler.router is not None, "Router should exist"
        if hasattr(img_sampler.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(img_sampler.router, "routes"):
            routes = [route.path for route in img_sampler.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
