"""
Unit Tests for Templates API Route
Tests template management endpoints comprehensively.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import templates
except ImportError:
    pytest.skip("Could not import templates route module", allow_module_level=True)


class TestTemplatesRouteImports:
    """Test templates route module can be imported."""

    def test_templates_module_imports(self):
        """Test templates module can be imported."""
        assert templates is not None, "Failed to import templates module"
        assert hasattr(templates, "router"), "templates module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert templates.router is not None, "Router should exist"
        if hasattr(templates.router, "prefix"):
            pass  # Router configuration is valid

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(templates.router, "routes"):
            routes = [route.path for route in templates.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestTemplatesEndpoints:
    """Test template CRUD endpoints."""

    def test_get_templates_success(self):
        """Test successful templates listing."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have default templates

    def test_get_templates_filtered_by_category(self):
        """Test listing templates filtered by category."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates?category=production")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(t["category"] == "production" for t in data)

    def test_get_templates_filtered_by_search(self):
        """Test listing templates filtered by search term."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates?search=audiobook")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_templates_filtered_by_public(self):
        """Test listing templates filtered by is_public."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates?is_public=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(t["is_public"] is True for t in data)

    def test_get_templates_with_limit(self):
        """Test listing templates with limit."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_template_success(self):
        """Test getting a specific template."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        # Use a default template ID
        response = client.get("/api/templates/template-audiobook")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "template-audiobook"
        assert "name" in data

    def test_get_template_not_found(self):
        """Test getting non-existent template."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates/nonexistent")
        assert response.status_code == 404

    def test_create_template_success(self):
        """Test successful template creation."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        request_data = {
            "name": "Test Template",
            "category": "test",
            "description": "A test template",
            "project_data": {"tracks": []},
            "tags": ["test"],
            "is_public": False,
        }

        response = client.post("/api/templates", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Template"
        assert data["category"] == "test"
        assert "id" in data

    def test_create_template_missing_name(self):
        """Test template creation with missing name."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        request_data = {
            "category": "test",
        }

        response = client.post("/api/templates", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_template_missing_category(self):
        """Test template creation with missing category."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        request_data = {
            "name": "Test Template",
        }

        response = client.post("/api/templates", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_update_template_success(self):
        """Test successful template update."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        # Create a template first
        create_data = {
            "name": "Original Name",
            "category": "test",
        }
        create_response = client.post("/api/templates", json=create_data)
        template_id = create_response.json()["id"]

        request_data = {
            "name": "Updated Name",
            "description": "Updated description",
        }

        response = client.put(f"/api/templates/{template_id}", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    def test_update_template_not_found(self):
        """Test updating non-existent template."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        request_data = {"name": "Updated Name"}

        response = client.put("/api/templates/nonexistent", json=request_data)
        assert response.status_code == 404

    def test_update_template_with_project_data(self):
        """Test updating template with project_data."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        # Create a template first
        create_data = {
            "name": "Test Template",
            "category": "test",
        }
        create_response = client.post("/api/templates", json=create_data)
        template_id = create_response.json()["id"]

        request_data = {
            "project_data": {"tracks": [{"id": "track1", "name": "Track 1"}]},
        }

        response = client.put(f"/api/templates/{template_id}", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data["project_data"]
        assert len(data["project_data"]["tracks"]) == 1

    def test_delete_template_success(self):
        """Test successful template deletion."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        # Create a template first
        create_data = {
            "name": "To Delete",
            "category": "test",
        }
        create_response = client.post("/api/templates", json=create_data)
        template_id = create_response.json()["id"]

        response = client.delete(f"/api/templates/{template_id}")
        assert response.status_code == 200

        # Verify template is deleted
        get_response = client.get(f"/api/templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_template_not_found(self):
        """Test deleting non-existent template."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.delete("/api/templates/nonexistent")
        assert response.status_code == 404

    def test_apply_template_success(self):
        """Test successful template application."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        # Use a default template
        request_data = {
            "project_name": "New Project from Template",
        }

        response = client.post(
            "/api/templates/template-audiobook/apply", json=request_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data or "message" in data

    def test_apply_template_not_found(self):
        """Test applying non-existent template."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        request_data = {
            "project_name": "New Project",
        }

        response = client.post("/api/templates/nonexistent/apply", json=request_data)
        assert response.status_code == 404

    def test_apply_template_to_existing_project(self):
        """Test applying template to existing project."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        request_data = {
            "project_id": "existing_project_id",
        }

        response = client.post(
            "/api/templates/template-audiobook/apply", json=request_data
        )
        assert response.status_code == 200

    def test_get_template_categories_success(self):
        """Test successful template categories retrieval."""
        app = FastAPI()
        app.include_router(templates.router)
        client = TestClient(app)

        response = client.get("/api/templates/categories/list")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
