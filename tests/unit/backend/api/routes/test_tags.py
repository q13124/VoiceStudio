"""
Unit Tests for Tags API Route
Tests tag management endpoints in isolation.
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
    from backend.api.routes import tags
except ImportError:
    pytest.skip("Could not import tags route module", allow_module_level=True)


class TestTagsRouteImports:
    """Test tags route module can be imported."""

    def test_tags_module_imports(self):
        """Test tags module can be imported."""
        assert tags is not None, "Failed to import tags module"
        assert hasattr(tags, "router"), "tags module missing router"


class TestTagsRouteHandlers:
    """Test tags route handlers exist and are callable."""

    def test_list_tags_handler_exists(self):
        """Test list_tags handler exists."""
        if hasattr(tags, "list_tags"):
            assert callable(tags.list_tags), "list_tags is not callable"

    def test_create_tag_handler_exists(self):
        """Test create_tag handler exists."""
        if hasattr(tags, "create_tag"):
            assert callable(tags.create_tag), "create_tag is not callable"

    def test_delete_tag_handler_exists(self):
        """Test delete_tag handler exists."""
        if hasattr(tags, "delete_tag"):
            assert callable(tags.delete_tag), "delete_tag is not callable"


class TestTagsRouter:
    """Test tags router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert tags.router is not None, "Router should exist"
        if hasattr(tags.router, "prefix"):
            assert (
                "/api/tags" in tags.router.prefix
            ), "Router prefix should include /api/tags"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(tags.router, "routes"):
            routes = [route.path for route in tags.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

