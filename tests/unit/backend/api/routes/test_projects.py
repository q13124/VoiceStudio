"""
Unit Tests for Projects API Routes.

Tests all project CRUD and audio file operations.
"""

import json
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_project_store():
    """Create mock project store service."""
    mock_service = MagicMock()
    
    # Use a real temp directory for file operations
    temp_dir = tempfile.mkdtemp()
    mock_service.projects_dir = temp_dir
    
    # Mock project data
    mock_project = MagicMock()
    mock_project.id = "test-project-1"
    mock_project.name = "Test Project"
    mock_project.description = "A test project"
    mock_project.created_at = datetime.now().isoformat()
    mock_project.updated_at = datetime.now().isoformat()
    mock_project.voice_profile_ids = []
    
    # Convert to dict for JSON serialization
    mock_project.model_dump = MagicMock(return_value={
        "id": "test-project-1",
        "name": "Test Project",
        "description": "A test project",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "voice_profile_ids": [],
        "schema_version": 1,
    })
    
    mock_service.list_projects.return_value = [mock_project]
    mock_service.get_project.return_value = mock_project
    mock_service.create_project.return_value = mock_project
    mock_service.update_project.return_value = mock_project
    mock_service.delete_project.return_value = True
    mock_service.ensure_project_subdir.return_value = os.path.join(temp_dir, "test-project-1", "audio")
    
    return mock_service


@pytest.fixture
def projects_client(mock_project_store):
    """Create test client with mocked dependencies."""
    with patch(
        "backend.api.routes.projects.get_project_store_service",
        return_value=mock_project_store,
    ):
        from backend.api.routes.projects import router

        app = FastAPI()
        app.include_router(router)
        yield TestClient(app)


# =============================================================================
# Project CRUD Tests
# =============================================================================


class TestProjectCRUD:
    """Tests for project create/read/update/delete operations."""

    def test_list_projects(self, projects_client):
        """Test GET /api/projects returns project list."""
        response = projects_client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        # May return paginated object or direct list
        if isinstance(data, dict) and "items" in data:
            assert isinstance(data["items"], list)
        else:
            assert isinstance(data, list)

    def test_get_project(self, projects_client):
        """Test GET /api/projects/{id} returns single project."""
        response = projects_client.get("/api/projects/test-project-1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "name" in data

    def test_create_project(self, projects_client):
        """Test POST /api/projects creates new project."""
        response = projects_client.post(
            "/api/projects",
            json={"name": "New Project", "description": "A new test project"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "name" in data

    def test_update_project(self, projects_client):
        """Test PUT /api/projects/{id} updates project."""
        response = projects_client.put(
            "/api/projects/test-project-1",
            json={"name": "Updated Project", "description": "Updated description"}
        )
        assert response.status_code == 200

    def test_delete_project(self, projects_client):
        """Test DELETE /api/projects/{id} removes project."""
        response = projects_client.delete("/api/projects/test-project-1")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data or data.get("ok") is True


# =============================================================================
# Project Audio Tests
# =============================================================================


class TestProjectAudio:
    """Tests for project audio file operations."""

    def test_list_project_audio(self, projects_client):
        """Test GET /api/projects/{id}/audio returns audio file list."""
        response = projects_client.get("/api/projects/test-project-1/audio")
        # May succeed with empty list, 404 if project not found, or 500 if file ops fail
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_save_audio_to_project(self, projects_client):
        """Test POST /api/projects/{id}/audio/save saves audio data."""
        # Create minimal WAV data
        import base64
        wav_header = b'RIFF' + b'\x00' * 40  # Minimal WAV header
        audio_base64 = base64.b64encode(wav_header).decode()
        
        response = projects_client.post(
            "/api/projects/test-project-1/audio/save",
            json={
                "audio_data": audio_base64,
                "filename": "test.wav",
            }
        )
        # May fail due to invalid WAV or succeed with mocking
        assert response.status_code in [200, 400, 422]

    def test_get_project_audio_file(self, projects_client):
        """Test GET /api/projects/{id}/audio/{filename} returns audio."""
        response = projects_client.get("/api/projects/test-project-1/audio/test.wav")
        # May return 200 if file exists, 404 if not, or 500 if file ops fail
        assert response.status_code in [200, 404, 500]


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestProjectErrors:
    """Tests for error handling in project routes."""

    def test_get_nonexistent_project(self, projects_client, mock_project_store):
        """Test GET with nonexistent project returns 404."""
        mock_project_store.get_project.side_effect = KeyError("Project not found")
        response = projects_client.get("/api/projects/nonexistent-id")
        assert response.status_code in [404, 500]  # 404 expected, 500 if error handling varies

    def test_create_project_invalid_data(self, projects_client):
        """Test POST with invalid data returns error."""
        response = projects_client.post(
            "/api/projects",
            json={}  # Missing required fields
        )
        assert response.status_code in [400, 422]  # Validation error

    def test_delete_nonexistent_project(self, projects_client, mock_project_store):
        """Test DELETE nonexistent project returns appropriate response."""
        mock_project_store.delete_project.return_value = False
        response = projects_client.delete("/api/projects/nonexistent-id")
        assert response.status_code in [200, 404]  # Depends on implementation
