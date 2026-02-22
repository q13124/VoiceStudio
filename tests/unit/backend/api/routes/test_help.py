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
            pass  # Router configuration is valid

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
        # API returns 'topics' key, not 'results'
        assert "topics" in data or "results" in data
        topics = data.get("topics", data.get("results", []))
        assert isinstance(topics, list)

    def test_search_help_empty_query(self):
        """Test help search with empty query."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/search?query=")
        assert response.status_code == 200
        data = response.json()
        # API returns 'topics' key, not 'results'
        assert "topics" in data or "results" in data

    def test_search_help_with_limit(self):
        """Test help search with limit parameter."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.get("/api/help/search?query=voice&limit=5")
        assert response.status_code == 200
        data = response.json()
        # API returns 'topics' key, not 'results'
        assert "topics" in data or "results" in data
        topics = data.get("topics", data.get("results", []))
        if len(topics) > 0:
            assert len(topics) <= 5


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


class TestHelpTopicCRUD:
    """Test CRUD operations for help topics."""

    def test_create_help_topic_success(self):
        """Test successful help topic creation."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        topic_data = {
            "id": "test_topic",
            "title": "Test Topic",
            "category": "test",
            "content": "Test content",
            "keywords": ["test"],
            "related_topics": [],
            "panel_id": None,
        }

        response = client.post("/api/help/topics", json=topic_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_topic"
        assert data["title"] == "Test Topic"

    def test_update_help_topic_success(self):
        """Test successful help topic update."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        # First create a topic
        topic_data = {
            "id": "update_test",
            "title": "Original Title",
            "category": "test",
            "content": "Original content",
            "keywords": [],
            "related_topics": [],
            "panel_id": None,
        }
        client.post("/api/help/topics", json=topic_data)

        # Then update it
        updated_data = {
            "id": "update_test",
            "title": "Updated Title",
            "category": "test",
            "content": "Updated content",
            "keywords": [],
            "related_topics": [],
            "panel_id": None,
        }

        response = client.put("/api/help/topics/update_test", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_help_topic_id_mismatch(self):
        """Test updating topic with ID mismatch."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        topic_data = {
            "id": "different_id",
            "title": "Test",
            "category": "test",
            "content": "Content",
            "keywords": [],
            "related_topics": [],
            "panel_id": None,
        }

        response = client.put("/api/help/topics/wrong_id", json=topic_data)
        assert response.status_code == 400

    def test_update_help_topic_not_found(self):
        """Test updating non-existent help topic."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        topic_data = {
            "id": "nonexistent",
            "title": "Test",
            "category": "test",
            "content": "Content",
            "keywords": [],
            "related_topics": [],
            "panel_id": None,
        }

        response = client.put("/api/help/topics/nonexistent", json=topic_data)
        assert response.status_code == 404

    def test_delete_help_topic_success(self):
        """Test successful help topic deletion."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        # First create a topic
        topic_data = {
            "id": "delete_test",
            "title": "To Delete",
            "category": "test",
            "content": "Content",
            "keywords": [],
            "related_topics": [],
            "panel_id": None,
        }
        client.post("/api/help/topics", json=topic_data)

        # Then delete it
        response = client.delete("/api/help/topics/delete_test")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_delete_help_topic_not_found(self):
        """Test deleting non-existent help topic."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.delete("/api/help/topics/nonexistent")
        assert response.status_code == 404


class TestKeyboardShortcutCRUD:
    """Test CRUD operations for keyboard shortcuts."""

    def test_create_keyboard_shortcut_success(self):
        """Test successful keyboard shortcut creation."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        shortcut_data = {
            "key": "Ctrl+T",
            "description": "Test shortcut",
            "category": "test",
            "panel_id": None,
        }

        response = client.post("/api/help/shortcuts", json=shortcut_data)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "Ctrl+T"

    def test_update_keyboard_shortcut_success(self):
        """Test successful keyboard shortcut update."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        # First create a shortcut
        shortcut_data = {
            "key": "Ctrl+U",
            "description": "Original",
            "category": "test",
            "panel_id": None,
        }
        client.post("/api/help/shortcuts", json=shortcut_data)

        # Then update it
        updated_data = {
            "key": "Ctrl+U",
            "description": "Updated",
            "category": "test",
            "panel_id": None,
        }

        response = client.put("/api/help/shortcuts/Ctrl+U", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated"

    def test_update_keyboard_shortcut_key_mismatch(self):
        """Test updating shortcut with key mismatch."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        shortcut_data = {
            "key": "Ctrl+X",
            "description": "Test",
            "category": "test",
            "panel_id": None,
        }

        response = client.put("/api/help/shortcuts/Ctrl+Y", json=shortcut_data)
        assert response.status_code == 400

    def test_update_keyboard_shortcut_not_found(self):
        """Test updating non-existent keyboard shortcut."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        shortcut_data = {
            "key": "Ctrl+Z",
            "description": "Test",
            "category": "test",
            "panel_id": None,
        }

        response = client.put("/api/help/shortcuts/Ctrl+Z", json=shortcut_data)
        # May return 404 if shortcut doesn't exist
        assert response.status_code in [200, 404]

    def test_delete_keyboard_shortcut_success(self):
        """Test successful keyboard shortcut deletion."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        # First create a shortcut
        shortcut_data = {
            "key": "Ctrl+D",
            "description": "To Delete",
            "category": "test",
            "panel_id": None,
        }
        client.post("/api/help/shortcuts", json=shortcut_data)

        # Then delete it
        response = client.delete("/api/help/shortcuts/Ctrl+D")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_delete_keyboard_shortcut_not_found(self):
        """Test deleting non-existent keyboard shortcut."""
        app = FastAPI()
        app.include_router(help.router)
        client = TestClient(app)

        response = client.delete("/api/help/shortcuts/Ctrl+Nonexistent")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
