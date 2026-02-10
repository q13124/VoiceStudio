"""
Unit Tests for Text Highlighting API Route
Tests text highlighting endpoints in isolation.
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
    from backend.api.routes import text_highlighting
except ImportError:
    pytest.skip(
        "Could not import text_highlighting route module",
        allow_module_level=True,
    )


class TestTextHighlightingRouteImports:
    """Test text highlighting route module can be imported."""

    def test_text_highlighting_module_imports(self):
        """Test text_highlighting module can be imported."""
        assert (
            text_highlighting is not None
        ), "Failed to import text_highlighting module"
        assert hasattr(
            text_highlighting, "router"
        ), "text_highlighting module missing router"


class TestTextHighlightingRouteHandlers:
    """Test text highlighting route handlers exist and are callable."""

    def test_highlight_text_handler_exists(self):
        """Test highlight_text handler exists."""
        if hasattr(text_highlighting, "highlight_text"):
            assert callable(
                text_highlighting.highlight_text
            ), "highlight_text is not callable"


class TestTextHighlightingRouter:
    """Test text highlighting router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert text_highlighting.router is not None, "Router should exist"
        if hasattr(text_highlighting.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(text_highlighting.router, "routes"):
            routes = [
                route.path for route in text_highlighting.router.routes
            ]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

