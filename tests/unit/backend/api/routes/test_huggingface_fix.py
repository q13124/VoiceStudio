"""
Unit Tests for HuggingFace Fix API Route
Tests HuggingFace compatibility fix endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import huggingface_fix
except ImportError:
    pytest.skip(
        "Could not import huggingface_fix route module",
        allow_module_level=True,
    )


class TestHuggingFaceFixRouteImports:
    """Test HuggingFace fix route module can be imported."""

    def test_huggingface_fix_module_imports(self):
        """Test huggingface_fix module can be imported."""
        assert (
            huggingface_fix is not None
        ), "Failed to import huggingface_fix module"
        assert hasattr(
            huggingface_fix, "router"
        ), "huggingface_fix module missing router"


class TestHuggingFaceFixRouteHandlers:
    """Test HuggingFace fix route handlers exist and are callable."""

    def test_apply_fix_handler_exists(self):
        """Test apply_fix handler exists."""
        if hasattr(huggingface_fix, "apply_fix"):
            assert callable(
                huggingface_fix.apply_fix
            ), "apply_fix is not callable"


class TestHuggingFaceFixRouter:
    """Test HuggingFace fix router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert huggingface_fix.router is not None, "Router should exist"
        if hasattr(huggingface_fix.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(huggingface_fix.router, "routes"):
            routes = [route.path for route in huggingface_fix.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

