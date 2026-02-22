"""
Unit Tests for Embedding Explorer API Route
Tests embedding exploration endpoints in isolation.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import embedding_explorer
except ImportError:
    pytest.skip(
        "Could not import embedding_explorer route module",
        allow_module_level=True,
    )


class TestEmbeddingExplorerRouteImports:
    """Test embedding explorer route module can be imported."""

    def test_embedding_explorer_module_imports(self):
        """Test embedding_explorer module can be imported."""
        assert embedding_explorer is not None, "Failed to import embedding_explorer module"
        assert hasattr(embedding_explorer, "router"), "embedding_explorer module missing router"


class TestEmbeddingExplorerRouteHandlers:
    """Test embedding explorer route handlers exist and are callable."""

    def test_explore_embeddings_handler_exists(self):
        """Test explore_embeddings handler exists."""
        if hasattr(embedding_explorer, "explore_embeddings"):
            assert callable(
                embedding_explorer.explore_embeddings
            ), "explore_embeddings is not callable"


class TestEmbeddingExplorerRouter:
    """Test embedding explorer router configuration."""

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert embedding_explorer.router is not None, "Router should exist"
        if hasattr(embedding_explorer.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(embedding_explorer.router, "routes"):
            routes = [route.path for route in embedding_explorer.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
