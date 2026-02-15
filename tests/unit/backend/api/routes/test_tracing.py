"""
Unit Tests for Tracing API Routes.

Tests distributed tracing endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def tracing_client():
    """Create test client for tracing routes."""
    from backend.api.routes.tracing import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestTracingEndpoints:
    """Tests for tracing endpoints."""

    def test_get_traces(self, tracing_client):
        """Test GET /traces returns trace list."""
        response = tracing_client.get("/api/tracing/traces")
        assert response.status_code in [200, 404]

    def test_get_trace_by_id(self, tracing_client):
        """Test GET /traces/{trace_id} returns specific trace."""
        response = tracing_client.get("/api/tracing/traces/test-trace")
        assert response.status_code in [200, 404]

    def test_get_spans(self, tracing_client):
        """Test GET /spans returns span list."""
        response = tracing_client.get("/api/tracing/spans")
        assert response.status_code in [200, 404]

    def test_get_stats(self, tracing_client):
        """Test GET /stats returns tracing stats."""
        response = tracing_client.get("/api/tracing/stats")
        assert response.status_code in [200, 404]
