"""
Unit Tests for Projects API Route
Tests project management endpoints comprehensively.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import projects
except ImportError:
    pytest.skip("Could not import projects route module", allow_module_level=True)


class TestProjectsRouteImports:
    """Test projects route module can be imported."""

    def test_projects_module_imports(self):
        """Test projects module can be imported."""
        assert projects is not None, "Failed to import projects module"
        assert hasattr(projects, "router"), "projects module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert projects.router is not None, "Router should exist"
        if hasattr(projects.router, "prefix"):
            assert (
                "/api/projects" in projects.router.prefix
            ), "Router prefix should include /api/projects"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(projects.router, "routes"):
            routes = [route.path for route in projects.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestProjectsEndpoints:
    """Test project CRUD endpoints."""

    def test_list_projects_empty(self):
        """Test listing projects when empty."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_list_projects_with_data(self):
        """Test listing projects with data."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Test Project",
            description="A test project",
            created_at=now,
            updated_at=now,
        )

        response = client.get("/api/projects")
        assert response.status_code == 200

    def test_get_project_success(self):
        """Test successful project retrieval."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Test Project",
            created_at=now,
            updated_at=now,
        )

        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id

    def test_get_project_not_found(self):
        """Test getting non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        response = client.get("/api/projects/nonexistent")
        assert response.status_code == 404

    def test_create_project_success(self):
        """Test successful project creation."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        with patch("backend.api.routes.projects._ensure_project_dir"):
            request_data = {
                "name": "New Project",
                "description": "A new project",
            }

            response = client.post("/api/projects", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "New Project"
            assert "id" in data

    def test_create_project_missing_name(self):
        """Test project creation with missing name."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        request_data = {"description": "No name"}

        response = client.post("/api/projects", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_project_empty_name(self):
        """Test project creation with empty name."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        with patch("backend.api.routes.projects._ensure_project_dir"):
            request_data = {"name": "   "}

            response = client.post("/api/projects", json=request_data)
            assert response.status_code == 400

    def test_update_project_success(self):
        """Test successful project update."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Original Name",
            created_at=now,
            updated_at=now,
        )

        update_data = {"name": "Updated Name"}

        response = client.put(f"/api/projects/{project_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_project_not_found(self):
        """Test updating non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        update_data = {"name": "Updated Name"}

        response = client.put("/api/projects/nonexistent", json=update_data)
        assert response.status_code == 404

    def test_update_project_voice_profiles(self):
        """Test updating project voice profiles."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Test Project",
            created_at=now,
            updated_at=now,
        )

        update_data = {"voice_profile_ids": ["voice1", "voice2"]}

        response = client.put(f"/api/projects/{project_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["voice_profile_ids"]) == 2

    def test_delete_project_success(self):
        """Test successful project deletion."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="To Delete",
            created_at=now,
            updated_at=now,
        )

        with patch("os.path.exists", return_value=False):
            response = client.delete(f"/api/projects/{project_id}")
            assert response.status_code == 200

    def test_delete_project_not_found(self):
        """Test deleting non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        response = client.delete("/api/projects/nonexistent")
        assert response.status_code == 404


class TestProjectAudioEndpoints:
    """Test project audio management endpoints."""

    def test_save_audio_to_project_success(self):
        """Test successful audio save to project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Test Project",
            created_at=now,
            updated_at=now,
        )

        audio_id = "audio123"
        with patch("backend.api.routes.projects._ensure_project_dir"):
            with patch("os.path.exists", return_value=True):
                with patch("shutil.copy2"):
                    with patch("os.stat") as mock_stat:
                        mock_stat.return_value = MagicMock(
                            st_size=1024, st_mtime=1234567890
                        )
                        with patch(
                            "backend.api.routes.projects._audio_storage",
                            {audio_id: "/path/to/audio.wav"},
                        ):
                            request_data = {"audio_id": audio_id}

                            response = client.post(
                                f"/api/projects/{project_id}/audio/save",
                                json=request_data,
                            )
                            assert response.status_code == 200
                            data = response.json()
                            assert "filename" in data

    def test_save_audio_to_project_not_found(self):
        """Test saving audio to non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        request_data = {"audio_id": "audio123"}

        response = client.post(
            "/api/projects/nonexistent/audio/save", json=request_data
        )
        assert response.status_code == 404

    def test_list_project_audio_success(self):
        """Test successful project audio listing."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Test Project",
            created_at=now,
            updated_at=now,
        )

        with patch("backend.api.routes.projects._ensure_project_dir"):
            with patch("os.path.exists", return_value=False):
                response = client.get(f"/api/projects/{project_id}/audio")
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)

    def test_list_project_audio_not_found(self):
        """Test listing audio for non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        response = client.get("/api/projects/nonexistent/audio")
        assert response.status_code == 404

    def test_get_project_audio_not_found(self):
        """Test getting audio from non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        response = client.get("/api/projects/nonexistent/audio/file.wav")
        assert response.status_code == 404

    def test_get_project_audio_invalid_filename(self):
        """Test getting audio with invalid filename."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        projects._projects.clear()

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        projects._projects[project_id] = projects.Project(
            id=project_id,
            name="Test Project",
            created_at=now,
            updated_at=now,
        )

        response = client.get(f"/api/projects/{project_id}/audio/../../../etc/passwd")
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
