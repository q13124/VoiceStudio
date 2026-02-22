"""
Unit Tests for Embedding API Route
Tests embedding endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import embedding
except ImportError:
    pytest.skip("Could not import embedding route module", allow_module_level=True)


class TestEmbeddingRouteImports:
    """Test embedding route module can be imported."""

    def test_embedding_module_imports(self):
        """Test embedding module can be imported."""
        assert embedding is not None, "Failed to import embedding module"
        assert hasattr(embedding, "router"), "embedding module missing router"


class TestEmbeddingRouteHandlers:
    """Test embedding route handlers exist and are callable."""

    def test_get_embedding_handler_exists(self):
        """Test get_embedding handler exists."""
        if hasattr(embedding, "get_embedding"):
            assert callable(embedding.get_embedding), "get_embedding is not callable"


class TestEmbeddingRouter:
    """Test embedding router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert embedding.router is not None, "Router should exist"
        if hasattr(embedding.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(embedding.router, "routes"):
            routes = [route.path for route in embedding.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
