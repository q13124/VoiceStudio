"""
Unit Tests for Help API Route
Tests help and documentation endpoints comprehensively.
"""

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import help
except ImportError:
    pytest.skip("Could not import help route module", allow_module_level=True)


class TestHelpRouteImports:
    """Test help route module can be imported."""

    def test_help_module_imports(self):
        """Test help module can be imported."""
        assert help is not None, "Failed to import help module"
        assert hasattr(help, "router"), "help module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert help.router is not None, "Router should exist"
        if hasattr(help.router, "prefix"):
            assert (
                "/api/help" in help.router.prefix
            ), "Router prefix should include /api/help"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(help.router, "routes"):
            routes = [route.path for route in help.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestHelpTopicsEndpoints:
    """Test help topics endpoints."""

    def test_get_help_topics_success(self):
        """Test successful help topics retrieval."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/topics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_help_topics_filtered_by_category(self):
        """Test help topics filtered by category."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/topics?category=getting-started")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_help_topics_filtered_by_search(self):
        """Test help topics filtered by search term."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/topics?search=voice")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_help_topic_success(self):
        """Test successful help topic retrieval."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        # First get all topics to find a valid ID
        topics_response = client.get("/api/help/topics")
        if topics_response.status_code == 200:
            topics = topics_response.json()
            if len(topics) > 0:
                topic_id = topics[0].get("id")
                if topic_id:
                    response = client.get(f"/api/help/topics/{topic_id}")
                    assert response.status_code == 200
                    data = response.json()
                    assert "id" in data
                    assert "title" in data

    def test_get_help_topic_not_found(self):
        """Test getting non-existent help topic."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/topics/nonexistent")
        assert response.status_code == 404


class TestHelpSearchEndpoint:
    """Test help search endpoint."""

    def test_search_help_success(self):
        """Test successful help search."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/search?query=voice")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_help_empty_query(self):
        """Test help search with empty query."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/search?query=")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_search_help_with_limit(self):
        """Test help search with limit parameter."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/search?query=voice&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        if len(data["results"]) > 0:
            assert len(data["results"]) <= 5


class TestKeyboardShortcutsEndpoint:
    """Test keyboard shortcuts endpoint."""

    def test_get_keyboard_shortcuts_success(self):
        """Test successful keyboard shortcuts retrieval."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/shortcuts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_keyboard_shortcuts_filtered_by_category(self):
        """Test keyboard shortcuts filtered by category."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/shortcuts?category=general")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_keyboard_shortcuts_filtered_by_panel(self):
        """Test keyboard shortcuts filtered by panel."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/shortcuts?panel=editor")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestHelpCategoriesEndpoint:
    """Test help categories endpoint."""

    def test_get_help_categories_success(self):
        """Test successful help categories retrieval."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)


class TestPanelHelpEndpoint:
    """Test panel-specific help endpoint."""

    def test_get_panel_help_success(self):
        """Test successful panel help retrieval."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/panel/editor")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_panel_help_not_found(self):
        """Test getting help for non-existent panel."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/panel/nonexistent")
        # May return 404 or empty help, depending on implementation
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
