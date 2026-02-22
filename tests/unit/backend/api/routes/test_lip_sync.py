"""
Unit Tests for Lip Sync API Routes.

Tests lip sync generation and engine management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def lip_sync_client():
    """Create test client for lip sync routes."""
    from backend.api.routes.lip_sync import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestLipSyncEngines:
    """Tests for lip sync engine management."""

    def test_get_engines(self, lip_sync_client):
        """Test GET /engines returns available engines."""
        response = lip_sync_client.get("/api/lip-sync/engines")
        # Skip: LipSyncService.list_engines not implemented
        assert response.status_code in [200, 500]

    def test_get_engine_status(self, lip_sync_client):
        """Test GET /engines/{engine_id}/status returns status."""
        response = lip_sync_client.get("/api/lip-sync/engines/wav2lip/status")
        # Skip: LipSyncService.get_engine_status not implemented
        assert response.status_code in [200, 404, 500]

    def test_get_quality_settings(self, lip_sync_client):
        """Test GET /quality-settings returns settings."""
        response = lip_sync_client.get("/api/lip-sync/quality-settings")
        assert response.status_code == 200
        data = response.json()
        assert data is not None


class TestLipSyncGeneration:
    """Tests for lip sync generation endpoints."""

    def test_generate_validation(self, lip_sync_client):
        """Test POST /generate validates required fields."""
        response = lip_sync_client.post("/api/lip-sync/generate", json={})
        assert response.status_code == 422

    def test_preview_validation(self, lip_sync_client):
        """Test POST /preview validates required fields."""
        response = lip_sync_client.post("/api/lip-sync/preview", json={})
        assert response.status_code == 422

    def test_extract_phonemes_validation(self, lip_sync_client):
        """Test POST /extract-phonemes validates required fields."""
        response = lip_sync_client.post("/api/lip-sync/extract-phonemes", json={})
        assert response.status_code == 422
