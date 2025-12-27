"""
Integration Tests for Global Search Backend (IDEA 5)
Tests the /api/search endpoint functionality.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    try:
        from backend.api.main import app

        return TestClient(app)
    except ImportError:
        pytest.skip("Backend API not available")


class TestGlobalSearchEndpoint:
    """Test global search endpoint."""

    def test_search_basic_query(self, client):
        """Test basic search query."""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "total_results" in data
        assert "results_by_type" in data
        assert data["query"] == "test"

    def test_search_minimum_length(self, client):
        """Test search requires minimum 2 characters."""
        response = client.get("/api/search?q=t")
        assert response.status_code == 400

    def test_search_with_types_filter(self, client):
        """Test search with type filters."""
        response = client.get("/api/search?q=test&types=profile,audio")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Verify results are filtered by type
        for result in data["results"]:
            assert result["type"] in ["profile", "audio"]

    def test_search_with_limit(self, client):
        """Test search with limit parameter."""
        response = client.get("/api/search?q=test&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 5

    def test_search_empty_results(self, client):
        """Test search with no matching results."""
        response = client.get("/api/search?q=nonexistentquery12345")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0
        assert len(data["results"]) == 0

    def test_search_results_structure(self, client):
        """Test search results have correct structure."""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()

        if data["results"]:
            result = data["results"][0]
            assert "id" in result
            assert "type" in result
            assert "title" in result
            assert "panel_id" in result
            assert result["type"] in ["profile", "project", "audio", "marker", "script"]

    def test_search_results_by_type(self, client):
        """Test results_by_type grouping."""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "results_by_type" in data
        assert isinstance(data["results_by_type"], dict)

    def test_search_natural_language_query(self, client):
        """Test natural language query parsing."""
        response = client.get("/api/search?q=high quality profiles from last week")
        assert response.status_code == 200
        data = response.json()
        assert "parsed_query" in data or "query" in data

    def test_search_error_handling(self, client):
        """Test search error handling."""
        # Test with invalid parameters
        response = client.get("/api/search?q=")
        # Should handle empty query gracefully
        assert response.status_code in [200, 400]

    def test_search_special_characters(self, client):
        """Test search with special characters."""
        response = client.get("/api/search?q=test%20query")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
