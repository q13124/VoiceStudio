"""
Unit Tests for Markers API Routes.

Tests all marker endpoints:
- CRUD operations
- Filtering and categories
- Project-scoped markers
- Validation
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_markers_state():
    """Reset markers state before each test."""
    from backend.api.routes import markers
    markers._markers = {}
    yield
    markers._markers = {}


@pytest.fixture
def markers_client():
    """Create test client for markers routes."""
    from backend.api.routes.markers import router, project_markers_router

    app = FastAPI()
    app.include_router(router)
    app.include_router(project_markers_router)
    return TestClient(app)


@pytest.fixture
def sample_marker_data():
    """Sample marker data for tests."""
    return {
        "name": "Test Marker",
        "time": 5.0,
        "color": "#FF0000",
        "category": "chapter",
        "description": "A test marker",
        "project_id": "proj-123",
    }


# =============================================================================
# Marker CRUD Tests
# =============================================================================


class TestMarkerCRUD:
    """Tests for marker CRUD operations."""

    def test_create_marker(self, markers_client, sample_marker_data):
        """Test POST /api/markers creates a marker."""
        response = markers_client.post("/api/markers", json=sample_marker_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Marker"
        assert data["time"] == 5.0
        assert data["color"] == "#FF0000"
        assert data["category"] == "chapter"
        assert data["project_id"] == "proj-123"
        assert "id" in data
        assert data["id"].startswith("marker-")

    def test_create_marker_minimal(self, markers_client):
        """Test creating marker with minimal data."""
        response = markers_client.post(
            "/api/markers",
            json={
                "name": "Minimal",
                "time": 0.0,
                "project_id": "proj-1",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["color"] == "#00FFFF"  # Default color

    def test_create_marker_invalid_name_empty(self, markers_client):
        """Test creating marker with empty name fails."""
        response = markers_client.post(
            "/api/markers",
            json={
                "name": "",
                "time": 0.0,
                "project_id": "proj-1",
            },
        )
        assert response.status_code == 422

    def test_create_marker_invalid_time_negative(self, markers_client):
        """Test creating marker with negative time fails."""
        response = markers_client.post(
            "/api/markers",
            json={
                "name": "Bad Time",
                "time": -5.0,
                "project_id": "proj-1",
            },
        )
        assert response.status_code == 422

    def test_create_marker_invalid_color(self, markers_client):
        """Test creating marker with invalid color fails."""
        response = markers_client.post(
            "/api/markers",
            json={
                "name": "Bad Color",
                "time": 0.0,
                "color": "red",  # Not a hex code
                "project_id": "proj-1",
            },
        )
        assert response.status_code == 422

    def test_get_marker(self, markers_client, sample_marker_data):
        """Test GET /api/markers/{id} retrieves a marker."""
        # Create marker first
        create_response = markers_client.post("/api/markers", json=sample_marker_data)
        marker_id = create_response.json()["id"]

        # Get the marker
        response = markers_client.get(f"/api/markers/{marker_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == marker_id
        assert data["name"] == "Test Marker"

    def test_get_nonexistent_marker(self, markers_client):
        """Test getting a marker that doesn't exist."""
        response = markers_client.get("/api/markers/nonexistent-id")
        assert response.status_code == 404

    def test_update_marker(self, markers_client, sample_marker_data):
        """Test PUT /api/markers/{id} updates a marker."""
        # Create marker first
        create_response = markers_client.post("/api/markers", json=sample_marker_data)
        marker_id = create_response.json()["id"]

        # Update the marker
        response = markers_client.put(
            f"/api/markers/{marker_id}",
            json={"name": "Updated Marker", "time": 10.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Marker"
        assert data["time"] == 10.0
        # Other fields should be preserved
        assert data["color"] == "#FF0000"

    def test_update_nonexistent_marker(self, markers_client):
        """Test updating a marker that doesn't exist."""
        response = markers_client.put(
            "/api/markers/nonexistent-id",
            json={"name": "Won't work"},
        )
        assert response.status_code == 404

    def test_delete_marker(self, markers_client, sample_marker_data):
        """Test DELETE /api/markers/{id} deletes a marker."""
        # Create marker first
        create_response = markers_client.post("/api/markers", json=sample_marker_data)
        marker_id = create_response.json()["id"]

        # Delete the marker
        response = markers_client.delete(f"/api/markers/{marker_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify marker is gone
        get_response = markers_client.get(f"/api/markers/{marker_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_marker(self, markers_client):
        """Test deleting a marker that doesn't exist."""
        response = markers_client.delete("/api/markers/nonexistent-id")
        assert response.status_code == 404


# =============================================================================
# Marker List and Filter Tests
# =============================================================================


class TestMarkerListAndFilter:
    """Tests for listing and filtering markers."""

    def test_get_all_markers(self, markers_client):
        """Test GET /api/markers returns all markers."""
        # Create multiple markers
        for i in range(3):
            markers_client.post(
                "/api/markers",
                json={
                    "name": f"Marker {i}",
                    "time": float(i),
                    "project_id": "proj-1",
                },
            )

        response = markers_client.get("/api/markers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_markers_filtered_by_project(self, markers_client):
        """Test filtering markers by project_id."""
        # Create markers for different projects
        markers_client.post(
            "/api/markers",
            json={"name": "P1 Marker", "time": 0.0, "project_id": "proj-1"},
        )
        markers_client.post(
            "/api/markers",
            json={"name": "P2 Marker", "time": 0.0, "project_id": "proj-2"},
        )

        response = markers_client.get("/api/markers?project_id=proj-1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["project_id"] == "proj-1"

    def test_get_markers_filtered_by_category(self, markers_client):
        """Test filtering markers by category."""
        # Create markers with different categories
        markers_client.post(
            "/api/markers",
            json={
                "name": "Chapter 1",
                "time": 0.0,
                "category": "chapter",
                "project_id": "proj-1",
            },
        )
        markers_client.post(
            "/api/markers",
            json={
                "name": "Note 1",
                "time": 1.0,
                "category": "note",
                "project_id": "proj-1",
            },
        )

        response = markers_client.get("/api/markers?category=chapter")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "chapter"

    def test_get_markers_sorted_by_time(self, markers_client):
        """Test markers are returned sorted by time."""
        # Use a unique project to isolate this test
        test_project = "sort-test-proj"
        
        # Create markers out of order
        markers_client.post(
            "/api/markers",
            json={"name": "Second", "time": 5.0, "project_id": test_project},
        )
        markers_client.post(
            "/api/markers",
            json={"name": "First", "time": 1.0, "project_id": test_project},
        )
        markers_client.post(
            "/api/markers",
            json={"name": "Third", "time": 10.0, "project_id": test_project},
        )

        # Filter by project to ensure isolation
        response = markers_client.get(f"/api/markers?project_id={test_project}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "First"
        assert data[1]["name"] == "Second"
        assert data[2]["name"] == "Third"


# =============================================================================
# Category Tests
# =============================================================================


class TestCategories:
    """Tests for marker categories."""

    def test_get_categories(self, markers_client):
        """Test GET /api/markers/categories/list returns categories."""
        # Create markers with categories
        markers_client.post(
            "/api/markers",
            json={
                "name": "M1",
                "time": 0.0,
                "category": "chapter",
                "project_id": "proj-1",
            },
        )
        markers_client.post(
            "/api/markers",
            json={
                "name": "M2",
                "time": 1.0,
                "category": "note",
                "project_id": "proj-1",
            },
        )
        markers_client.post(
            "/api/markers",
            json={
                "name": "M3",
                "time": 2.0,
                "category": "chapter",  # Duplicate
                "project_id": "proj-1",
            },
        )

        response = markers_client.get("/api/markers/categories/list")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "chapter" in data["categories"]
        assert "note" in data["categories"]
        assert len(data["categories"]) == 2

    def test_get_categories_by_project(self, markers_client):
        """Test filtering categories by project."""
        # Create markers in different projects
        markers_client.post(
            "/api/markers",
            json={
                "name": "M1",
                "time": 0.0,
                "category": "chapter",
                "project_id": "proj-1",
            },
        )
        markers_client.post(
            "/api/markers",
            json={
                "name": "M2",
                "time": 0.0,
                "category": "scene",
                "project_id": "proj-2",
            },
        )

        response = markers_client.get("/api/markers/categories/list?project_id=proj-1")
        assert response.status_code == 200
        data = response.json()
        assert "chapter" in data["categories"]
        assert "scene" not in data["categories"]


# =============================================================================
# Project-Scoped Marker Tests
# =============================================================================


class TestProjectMarkers:
    """Tests for project-scoped marker endpoints."""

    def test_get_project_markers(self, markers_client):
        """Test GET /api/projects/{id}/markers returns project markers."""
        # Create markers for different projects
        markers_client.post(
            "/api/markers",
            json={"name": "P1 Marker 1", "time": 0.0, "project_id": "proj-1"},
        )
        markers_client.post(
            "/api/markers",
            json={"name": "P1 Marker 2", "time": 1.0, "project_id": "proj-1"},
        )
        markers_client.post(
            "/api/markers",
            json={"name": "P2 Marker", "time": 0.0, "project_id": "proj-2"},
        )

        response = markers_client.get("/api/projects/proj-1/markers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(m["project_id"] == "proj-1" for m in data)

    def test_get_project_marker_by_id(self, markers_client):
        """Test GET /api/projects/{pid}/markers/{mid} returns specific marker."""
        # Create a marker
        create_response = markers_client.post(
            "/api/markers",
            json={"name": "Specific", "time": 0.0, "project_id": "proj-1"},
        )
        marker_id = create_response.json()["id"]

        response = markers_client.get(f"/api/projects/proj-1/markers/{marker_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Specific"

    def test_get_project_marker_wrong_project(self, markers_client):
        """Test accessing marker from wrong project returns 404."""
        # Create a marker in proj-1
        create_response = markers_client.post(
            "/api/markers",
            json={"name": "P1 Only", "time": 0.0, "project_id": "proj-1"},
        )
        marker_id = create_response.json()["id"]

        # Try to access from proj-2
        response = markers_client.get(f"/api/projects/proj-2/markers/{marker_id}")
        assert response.status_code == 404
