"""
Unit Tests for Projects API Route
Tests project management endpoints comprehensively.
"""

import sys
from pathlib import Path
from unittest.mock import patch

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


@pytest.fixture(autouse=True)
def _isolate_project_store(tmp_path, monkeypatch):
    """
    Isolate project storage to a per-test temporary directory.

    The Projects API now persists metadata on disk; unit tests must not write to
    the real user profile directory.
    """
    monkeypatch.setenv("VOICESTUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    from backend.api.optimization import _response_cache
    from backend.services.ProjectStoreService import reset_project_store_service

    reset_project_store_service()
    _response_cache.clear()
    yield
    reset_project_store_service()
    _response_cache.clear()


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

        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, dict) and "items" in data:
            assert data["items"] == []
        else:
            assert isinstance(data, list)
            assert data == []

    def test_list_projects_with_data(self):
        """Test listing projects with data."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        create_response = client.post(
            "/api/projects",
            json={"name": "Test Project", "description": "A test project"},
        )
        assert create_response.status_code == 200
        created = create_response.json()

        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        items = data.get("items", []) if isinstance(data, dict) else data
        assert any(item.get("id") == created["id"] for item in items)

    def test_get_project_success(self):
        """Test successful project retrieval."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        create_response = client.post("/api/projects", json={"name": "Test Project"})
        assert create_response.status_code == 200
        created = create_response.json()
        project_id = created["id"]

        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id

    def test_project_persists_across_store_reset(self):
        """Test project metadata persists after store reset (simulated restart)."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        create_response = client.post(
            "/api/projects", json={"name": "Persisted Project"}
        )
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

        from backend.api.optimization import _response_cache
        from backend.services.ProjectStoreService import reset_project_store_service

        reset_project_store_service()
        _response_cache.clear()

        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id

    def test_get_project_not_found(self):
        """Test getting non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        response = client.get("/api/projects/nonexistent")
        assert response.status_code == 404

    def test_create_project_success(self):
        """Test successful project creation."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)
        request_data = {"name": "New Project", "description": "A new project"}

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

        request_data = {"description": "No name"}

        response = client.post("/api/projects", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_project_empty_name(self):
        """Test project creation with empty name."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)
        response = client.post("/api/projects", json={"name": "   "})
        assert response.status_code == 400

    def test_update_project_success(self):
        """Test successful project update."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)
        create_response = client.post("/api/projects", json={"name": "Original Name"})
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

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

        update_data = {"name": "Updated Name"}

        response = client.put("/api/projects/nonexistent", json=update_data)
        assert response.status_code == 404

    def test_update_project_voice_profiles(self):
        """Test updating project voice profiles."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)
        create_response = client.post("/api/projects", json={"name": "Test Project"})
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

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
        create_response = client.post("/api/projects", json={"name": "To Delete"})
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 200

    def test_delete_project_not_found(self):
        """Test deleting non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        response = client.delete("/api/projects/nonexistent")
        assert response.status_code == 404


class TestProjectAudioEndpoints:
    """Test project audio management endpoints."""

    def test_save_audio_to_project_success(self, tmp_path):
        """Test successful audio save to project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)
        create_response = client.post("/api/projects", json={"name": "Test Project"})
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

        audio_id = "audio123"
        source_path = tmp_path / "source.wav"
        source_path.write_bytes(b"RIFF0000WAVEfmt ")

        import types

        fake_voice = types.ModuleType("backend.api.routes.voice")
        fake_voice._audio_storage = {audio_id: str(source_path)}

        with patch.dict(sys.modules, {"backend.api.routes.voice": fake_voice}):
            request_data = {"audio_id": audio_id}
            response = client.post(
                f"/api/projects/{project_id}/audio/save",
                json=request_data,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["filename"].endswith(".wav")

            dest_path = tmp_path / "projects" / project_id / "audio" / data["filename"]
            assert dest_path.exists()

    def test_content_addressed_cache_deduplication(self, tmp_path):
        """Test content-addressed cache deduplicates identical audio files."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        create_response1 = client.post("/api/projects", json={"name": "Project 1"})
        assert create_response1.status_code == 200
        project_id1 = create_response1.json()["id"]

        create_response2 = client.post("/api/projects", json={"name": "Project 2"})
        assert create_response2.status_code == 200
        project_id2 = create_response2.json()["id"]

        audio_id = "audio123"
        source_path = tmp_path / "source.wav"
        source_content = b"RIFF" + b"0" * 100
        source_path.write_bytes(source_content)

        import types

        fake_voice = types.ModuleType("backend.api.routes.voice")
        fake_voice._audio_storage = {audio_id: str(source_path)}

        with patch.dict(sys.modules, {"backend.api.routes.voice": fake_voice}):
            response1 = client.post(
                f"/api/projects/{project_id1}/audio/save",
                json={"audio_id": audio_id, "filename": "test1.wav"},
            )
            assert response1.status_code == 200

            response2 = client.post(
                f"/api/projects/{project_id2}/audio/save",
                json={"audio_id": audio_id, "filename": "test2.wav"},
            )
            assert response2.status_code == 200

            from backend.services.ContentAddressedAudioCache import get_audio_cache

            cache = get_audio_cache()
            cached_path, hash_value = cache.get_or_store(source_path)

            file1 = tmp_path / "projects" / project_id1 / "audio" / "test1.wav"
            file2 = tmp_path / "projects" / project_id2 / "audio" / "test2.wav"

            assert file1.exists()
            assert file2.exists()
            assert cached_path.exists()

            assert file1.read_bytes() == source_content
            assert file2.read_bytes() == source_content
            assert cached_path.read_bytes() == source_content

    def test_save_audio_to_project_not_found(self):
        """Test saving audio to non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

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
        create_response = client.post("/api/projects", json={"name": "Test Project"})
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

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

        response = client.get("/api/projects/nonexistent/audio")
        assert response.status_code == 404

    def test_get_project_audio_not_found(self):
        """Test getting audio from non-existent project."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)

        response = client.get("/api/projects/nonexistent/audio/file.wav")
        assert response.status_code == 404

    def test_get_project_audio_invalid_filename(self):
        """Test getting audio with invalid filename."""
        app = FastAPI()
        app.include_router(projects.router)
        client = TestClient(app)
        create_response = client.post("/api/projects", json={"name": "Test Project"})
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]

        response = client.get(f"/api/projects/{project_id}/audio/..bad.wav")
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
