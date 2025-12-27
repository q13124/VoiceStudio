"""
Integration tests for A/B Testing endpoint.

Tests the /api/eval/abx/start and /api/eval/abx/results endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestABTesting:
    """Test suite for A/B Testing endpoints."""
    
    def test_start_ab_test_success(self, client: TestClient, sample_profile_id: str):
        """Test starting an A/B test successfully."""
        response = client.post(
            "/api/eval/abx/start",
            json={
                "items": ["audio-1", "audio-2", "audio-3"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "ok" in data
    
    def test_start_ab_test_empty_items(self, client: TestClient):
        """Test starting A/B test with empty items list."""
        response = client.post(
            "/api/eval/abx/start",
            json={
                "items": []
            }
        )
        
        # Should either accept empty list or return validation error
        assert response.status_code in [200, 422]
    
    def test_start_ab_test_missing_items(self, client: TestClient):
        """Test starting A/B test without items field."""
        response = client.post(
            "/api/eval/abx/start",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_get_ab_test_results(self, client: TestClient):
        """Test getting A/B test results."""
        response = client.get("/api/eval/abx/results")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If results exist, check structure
        if len(data) > 0:
            result = data[0]
            assert "item" in result
            assert "mos" in result
            assert "pref" in result
            assert isinstance(result["mos"], (int, float))
            assert result["mos"] >= 0.0 and result["mos"] <= 5.0
    
    def test_ab_test_workflow(self, client: TestClient):
        """Test complete A/B testing workflow."""
        # 1. Start A/B test
        start_response = client.post(
            "/api/eval/abx/start",
            json={
                "items": ["test-audio-1", "test-audio-2"]
            }
        )
        assert start_response.status_code == 200
        
        # 2. Get results
        results_response = client.get("/api/eval/abx/results")
        assert results_response.status_code == 200
        results = results_response.json()
        assert isinstance(results, list)
    
    def test_ab_test_invalid_item_format(self, client: TestClient):
        """Test A/B test with invalid item format."""
        response = client.post(
            "/api/eval/abx/start",
            json={
                "items": [123, 456]  # Should be strings
            }
        )
        
        # Should either accept or return validation error
        assert response.status_code in [200, 422]
    
    def test_ab_test_large_item_list(self, client: TestClient):
        """Test A/B test with large number of items."""
        large_list = [f"audio-{i}" for i in range(100)]
        response = client.post(
            "/api/eval/abx/start",
            json={
                "items": large_list
            }
        )
        
        # Should handle large lists (may be slow but should not error)
        assert response.status_code in [200, 422, 413]  # 413 = Payload Too Large


class TestABTestingErrorHandling:
    """Test error handling scenarios for A/B Testing."""
    
    def test_invalid_json(self, client: TestClient):
        """Test with invalid JSON."""
        response = client.post(
            "/api/eval/abx/start",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self, client: TestClient):
        """Test without Content-Type header."""
        response = client.post(
            "/api/eval/abx/start",
            data='{"items": ["audio-1"]}'
        )
        # FastAPI may auto-detect JSON or return error
        assert response.status_code in [200, 422, 415]
    
    def test_results_endpoint_methods(self, client: TestClient):
        """Test that results endpoint only accepts GET."""
        # POST should not be allowed
        response = client.post("/api/eval/abx/results")
        assert response.status_code in [405, 404]  # Method Not Allowed or Not Found

