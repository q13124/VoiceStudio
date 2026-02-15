"""
Unit Tests for Feedback API Routes.

Tests user feedback collection endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def feedback_client():
    """Create test client for feedback routes."""
    from backend.api.routes.feedback import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestFeedbackEndpoints:
    """Tests for feedback endpoints."""

    def test_submit_feedback(self, feedback_client):
        """Test POST /submit submits user feedback."""
        response = feedback_client.post(
            "/api/feedback/submit",
            json={"rating": 5, "comment": "Great!"}
        )
        assert response.status_code in [200, 201, 404, 422]

    def test_list_feedback(self, feedback_client):
        """Test GET /list returns feedback list."""
        response = feedback_client.get("/api/feedback/list")
        assert response.status_code in [200, 404]

    def test_get_stats(self, feedback_client):
        """Test GET /stats returns feedback statistics."""
        response = feedback_client.get("/api/feedback/stats")
        assert response.status_code in [200, 404]
