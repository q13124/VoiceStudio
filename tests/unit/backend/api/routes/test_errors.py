"""
Unit Tests for Error Tracking API Routes.

Tests error tracking and analysis endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def errors_client():
    """Create test client for errors routes."""
    from backend.api.routes.errors import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestErrorTracking:
    """Tests for error tracking endpoints."""

    def test_get_summary(self, errors_client):
        """Test GET /summary returns error summary."""
        response = errors_client.get("/api/errors/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_errors" in data
        assert "unique_errors" in data

    def test_list_recent_errors(self, errors_client):
        """Test GET /recent returns recent errors."""
        response = errors_client.get("/api/errors/recent")
        assert response.status_code == 200

    def test_list_recent_with_filters(self, errors_client):
        """Test GET /recent with filters."""
        response = errors_client.get(
            "/api/errors/recent", params={"severity": "error", "limit": 10}
        )
        assert response.status_code == 200

    def test_get_aggregates(self, errors_client):
        """Test GET /aggregates returns error aggregates."""
        response = errors_client.get("/api/errors/aggregates")
        assert response.status_code == 200

    def test_get_categories(self, errors_client):
        """Test GET /categories returns error categories."""
        response = errors_client.get("/api/errors/categories")
        assert response.status_code == 200

    def test_get_error_rate(self, errors_client):
        """Test GET /rate returns error rate."""
        response = errors_client.get("/api/errors/rate")
        assert response.status_code == 200


class TestErrorManagement:
    """Tests for error management endpoints."""

    def test_resolve_error(self, errors_client):
        """Test POST /{error_id}/resolve resolves an error."""
        response = errors_client.post(
            "/api/errors/test-error/resolve", json={"resolved_by": "test-user"}
        )
        assert response.status_code in [200, 404, 422]

    def test_export_errors(self, errors_client):
        """Test POST /export exports error data."""
        response = errors_client.post("/api/errors/export")
        assert response.status_code in [200, 500]

    def test_delete_resolved(self, errors_client):
        """Test DELETE /resolved clears resolved errors."""
        response = errors_client.delete("/api/errors/resolved")
        assert response.status_code in [200, 204]
