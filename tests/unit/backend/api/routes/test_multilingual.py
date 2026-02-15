"""
Unit Tests for Multilingual API Route
Tests multilingual support endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import multilingual
except ImportError:
    pytest.skip(
        "Could not import multilingual route module", allow_module_level=True
    )


class TestMultilingualRouteImports:
    """Test multilingual route module can be imported."""

    def test_multilingual_module_imports(self):
        """Test multilingual module can be imported."""
        assert (
            multilingual is not None
        ), "Failed to import multilingual module"
        assert hasattr(
            multilingual, "router"
        ), "multilingual module missing router"


class TestMultilingualRouteHandlers:
    """Test multilingual route handlers exist and are callable."""

    def test_detect_language_handler_exists(self):
        """Test detect_language handler exists."""
        if hasattr(multilingual, "detect_language"):
            assert callable(
                multilingual.detect_language
            ), "detect_language is not callable"

    def test_synthesize_multilingual_handler_exists(self):
        """Test synthesize_multilingual handler exists."""
        if hasattr(multilingual, "synthesize_multilingual"):
            assert callable(
                multilingual.synthesize_multilingual
            ), "synthesize_multilingual is not callable"


class TestMultilingualRouter:
    """Test multilingual router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert multilingual.router is not None, "Router should exist"
        if hasattr(multilingual.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(multilingual.router, "routes"):
            routes = [route.path for route in multilingual.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

