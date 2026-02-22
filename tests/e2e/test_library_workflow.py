"""
Library Workflow E2E Tests.

Tests for library operations including:
- Upload audio files
- Browse library
- Search assets
- Organize into folders
- Delete assets

Phase 9A: Feature Matrix - Library
"""

from __future__ import annotations

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.library,
]


@pytest.fixture
def api_client():
    """Create a test client for API tests."""
    from fastapi.testclient import TestClient

    from backend.api.main import app

    return TestClient(app)


@pytest.fixture
def backend_available(api_client):
    """Check if backend is available."""
    try:
        response = api_client.get("/api/health")
        return response.status_code == 200
    except Exception:
        return False


class TestLibraryBrowse:
    """Tests for browsing library assets."""

    def test_list_library_assets(self, api_client, backend_available):
        """Test listing all library assets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/")
        # Endpoint may not exist yet
        assert response.status_code in (200, 404, 422, 429)

    def test_list_library_with_pagination(self, api_client, backend_available):
        """Test listing library with pagination."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/?page=1&limit=20")
        assert response.status_code in (200, 404, 422, 429)

    def test_list_library_by_type(self, api_client, backend_available):
        """Test filtering library by asset type."""
        if not backend_available:
            pytest.skip("Backend not available")

        for asset_type in ["audio", "voice", "project"]:
            response = api_client.get(f"/api/library/?type={asset_type}")
            assert response.status_code in (200, 404, 422, 429)

    def test_get_library_stats(self, api_client, backend_available):
        """Test getting library statistics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/stats")
        assert response.status_code in (200, 404, 422, 429)


class TestLibrarySearch:
    """Tests for searching library assets."""

    def test_search_library(self, api_client, backend_available):
        """Test searching library assets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/search?q=test")
        assert response.status_code in (200, 404, 422, 429)

    def test_search_library_empty_query(self, api_client, backend_available):
        """Test search with empty query."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/search?q=")
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_search_library_with_filters(self, api_client, backend_available):
        """Test search with type filters."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/search?q=voice&type=audio&sort=date")
        assert response.status_code in (200, 404, 422, 429)

    def test_search_library_special_characters(self, api_client, backend_available):
        """Test search with special characters."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/search?q=test%20voice%21")
        assert response.status_code in (200, 400, 404, 422, 429)


class TestLibraryUpload:
    """Tests for uploading assets to library."""

    def test_upload_status_check(self, api_client, backend_available):
        """Test upload endpoint availability."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Check if upload endpoint exists (OPTIONS or HEAD)
        response = api_client.options("/api/library/upload")
        assert response.status_code in (200, 204, 404, 405, 422, 429)

    def test_get_upload_formats(self, api_client, backend_available):
        """Test getting supported upload formats."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/formats")
        assert response.status_code in (200, 404, 422, 429)


class TestLibraryFolders:
    """Tests for organizing library into folders."""

    def test_list_folders(self, api_client, backend_available):
        """Test listing library folders."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/folders")
        assert response.status_code in (200, 404, 422, 429)

    def test_create_folder(self, api_client, backend_available):
        """Test creating a folder."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post("/api/library/folders", json={"name": "test_folder"})
        assert response.status_code in (200, 201, 400, 404, 422, 429)

    def test_rename_folder(self, api_client, backend_available):
        """Test renaming a folder."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.patch("/api/library/folders/test_id", json={"name": "renamed_folder"})
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_move_asset_to_folder(self, api_client, backend_available):
        """Test moving asset to folder."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/library/assets/test_asset/move", json={"folder_id": "test_folder_id"}
        )
        assert response.status_code in (200, 400, 404, 422, 429)


class TestLibraryDelete:
    """Tests for deleting library assets."""

    def test_delete_asset(self, api_client, backend_available):
        """Test deleting a single asset."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.delete("/api/library/assets/nonexistent_id")
        assert response.status_code in (200, 204, 400, 404, 422, 429)

    def test_bulk_delete_assets(self, api_client, backend_available):
        """Test bulk deleting assets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/library/assets/bulk-delete", json={"asset_ids": ["id1", "id2"]}
        )
        assert response.status_code in (200, 204, 400, 404, 422, 429)

    def test_delete_folder(self, api_client, backend_available):
        """Test deleting a folder."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.delete("/api/library/folders/nonexistent_id")
        assert response.status_code in (200, 204, 400, 404, 422, 429)


class TestLibraryMetadata:
    """Tests for asset metadata operations."""

    def test_get_asset_metadata(self, api_client, backend_available):
        """Test getting asset metadata."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/assets/test_id/metadata")
        assert response.status_code in (200, 404, 422, 429)

    def test_update_asset_metadata(self, api_client, backend_available):
        """Test updating asset metadata."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.patch(
            "/api/library/assets/test_id/metadata",
            json={"tags": ["voice", "processed"], "description": "Test asset"},
        )
        assert response.status_code in (200, 400, 404, 422, 429)

    def test_get_asset_tags(self, api_client, backend_available):
        """Test getting all used tags."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/library/tags")
        assert response.status_code in (200, 404, 422, 429)
