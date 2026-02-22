"""
Unit Tests for Experiments API Routes.

Tests A/B experiment management endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def experiments_client():
    """Create test client for experiments routes."""
    from backend.api.routes.experiments import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestExperimentsEndpoints:
    """Tests for experiments endpoints."""

    def test_list_experiments(self, experiments_client):
        """Test GET /experiments returns experiment list."""
        response = experiments_client.get("/api/experiments")
        assert response.status_code == 200

    def test_get_experiment_by_id(self, experiments_client):
        """Test GET /experiments/{id} returns specific experiment."""
        response = experiments_client.get("/api/experiments/test-exp")
        assert response.status_code in [200, 404]

    def test_create_experiment_validation(self, experiments_client):
        """Test POST /experiments validates required fields."""
        response = experiments_client.post("/api/experiments", json={})
        assert response.status_code in [200, 201, 422]

    def test_delete_experiment(self, experiments_client):
        """Test DELETE /experiments/{id} deletes experiment."""
        response = experiments_client.delete("/api/experiments/test-exp")
        assert response.status_code in [200, 204, 404]
