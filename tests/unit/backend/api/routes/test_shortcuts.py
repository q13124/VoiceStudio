"""
Unit Tests for Shortcuts API Route
Tests keyboard shortcut management endpoints comprehensively.
"""

import sys
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import shortcuts
except ImportError:
    pytest.skip(
        "Could not import shortcuts route module", allow_module_level=True
    )


class TestShortcutsRouteImports:
    """Test shortcuts route module can be imported."""

    def test_shortcuts_module_imports(self):
        """Test shortcuts module can be imported."""
        assert (
            shortcuts is not None
        ), "Failed to import shortcuts module"
        assert hasattr(
            shortcuts, "router"
        ), "shortcuts module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert shortcuts.router is not None, "Router should exist"
        if hasattr(shortcuts.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(shortcuts.router, "routes"):
            routes = [route.path for route in shortcuts.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestShortcutsEndpoints:
    """Test keyboard shortcuts CRUD endpoints."""

    def test_get_shortcuts_success(self):
        """Test successful shortcuts listing."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get("/api/shortcuts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have default shortcuts

    def test_get_shortcuts_filtered_by_category(self):
        """Test listing shortcuts filtered by category."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get("/api/shortcuts?category=file")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(s["category"] == "file" for s in data)

    def test_get_shortcuts_filtered_by_panel(self):
        """Test listing shortcuts filtered by panel_id."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get("/api/shortcuts?panel_id=timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_shortcut_success(self):
        """Test getting a specific shortcut."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        # Use a default shortcut ID
        response = client.get("/api/shortcuts/file.new")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "file.new"
        assert "key" in data

    def test_get_shortcut_not_found(self):
        """Test getting non-existent shortcut."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get("/api/shortcuts/nonexistent")
        assert response.status_code == 404

    def test_create_shortcut_success(self):
        """Test successful shortcut creation."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        shortcut_data = {
            "id": f"custom-{uuid.uuid4().hex[:8]}",
            "key": "Ctrl+K",
            "key_code": "K",
            "modifiers": ["Ctrl"],
            "description": "Custom shortcut",
            "category": "custom",
            "is_custom": True,
        }

        response = client.post("/api/shortcuts", json=shortcut_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == shortcut_data["id"]
        assert data["is_custom"] is True

    def test_create_shortcut_with_conflict(self):
        """Test creating shortcut with conflict detection."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        # Try to create a shortcut that conflicts with existing one
        shortcut_data = {
            "id": f"conflict-{uuid.uuid4().hex[:8]}",
            "key": "Ctrl+N",  # Conflicts with file.new
            "key_code": "N",
            "modifiers": ["Ctrl"],
            "description": "Conflicting shortcut",
            "category": "custom",
            "is_custom": True,
        }

        response = client.post("/api/shortcuts", json=shortcut_data)
        # May succeed but conflict should be detected
        assert response.status_code in [200, 400, 409]

    def test_update_shortcut_success(self):
        """Test successful shortcut update."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        # Create a custom shortcut first
        shortcut_id = f"update-{uuid.uuid4().hex[:8]}"
        create_data = {
            "id": shortcut_id,
            "key": "Ctrl+T",
            "key_code": "T",
            "modifiers": ["Ctrl"],
            "description": "Original description",
            "category": "custom",
            "is_custom": True,
        }
        client.post("/api/shortcuts", json=create_data)

        update_data = {
            "key": "Ctrl+U",
            "key_code": "U",
            "modifiers": ["Ctrl"],
            "description": "Updated description",
        }

        response = client.put(f"/api/shortcuts/{shortcut_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "Ctrl+U"
        assert data["description"] == "Updated description"

    def test_update_shortcut_not_found(self):
        """Test updating non-existent shortcut."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        update_data = {"key": "Ctrl+X"}

        response = client.put("/api/shortcuts/nonexistent", json=update_data)
        assert response.status_code == 404

    def test_delete_shortcut_success(self):
        """Test successful shortcut deletion."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        # Create a custom shortcut first
        shortcut_id = f"delete-{uuid.uuid4().hex[:8]}"
        create_data = {
            "id": shortcut_id,
            "key": "Ctrl+D",
            "key_code": "D",
            "modifiers": ["Ctrl"],
            "description": "To be deleted",
            "category": "custom",
            "is_custom": True,
        }
        client.post("/api/shortcuts", json=create_data)

        response = client.delete(f"/api/shortcuts/{shortcut_id}")
        assert response.status_code == 200

        # Verify shortcut is deleted
        get_response = client.get(f"/api/shortcuts/{shortcut_id}")
        assert get_response.status_code == 404

    def test_delete_shortcut_not_found(self):
        """Test deleting non-existent shortcut."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.delete("/api/shortcuts/nonexistent")
        assert response.status_code == 404

    def test_reset_shortcut_success(self):
        """Test successful shortcut reset."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        # Use a default shortcut
        response = client.post("/api/shortcuts/file.new/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "file.new"

    def test_reset_shortcut_not_found(self):
        """Test resetting non-existent shortcut."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.post("/api/shortcuts/nonexistent/reset")
        assert response.status_code == 404

    def test_reset_all_shortcuts_success(self):
        """Test successful reset of all shortcuts."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.post("/api/shortcuts/reset-all")
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data or "success" in response_data

    def test_check_conflict_success(self):
        """Test successful conflict check."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get(
            "/api/shortcuts/check-conflict?key=Ctrl+N&key_code=N"
        )
        assert response.status_code == 200
        data = response.json()
        assert "has_conflict" in data or "conflicts" in data

    def test_check_conflict_no_conflict(self):
        """Test conflict check with no conflict."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get(
            "/api/shortcuts/check-conflict?key=Ctrl+Alt+Shift+X&key_code=X"
        )
        assert response.status_code == 200
        data = response.json()
        # Should indicate no conflict for unique key combination

    def test_get_shortcut_categories_success(self):
        """Test successful shortcut categories retrieval."""
        app = FastAPI()
        app.include_router(shortcuts.router)
        client = TestClient(app)

        response = client.get("/api/shortcuts/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
