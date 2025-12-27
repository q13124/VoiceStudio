"""
Integration tests for Quality Benchmarking endpoint.

Tests the /api/quality/benchmark endpoint.
"""

import pytest
from fastapi.testclient import TestClient


class TestQualityBenchmarking:
    """Test suite for Quality Benchmarking endpoint."""
    
    def test_run_benchmark_with_profile_id(self, client: TestClient, sample_profile_id: str, sample_test_text: str):
        """Test running benchmark with profile ID."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": sample_test_text,
                "language": "en",
                "engines": ["xtts", "chatterbox"],
                "enhance_quality": True
            }
        )
        
        assert response.status_code in [200, 404, 503]  # 404 if profile not found, 503 if engines not available
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "total_engines" in data
            assert "successful_engines" in data
            assert isinstance(data["results"], list)
            assert data["total_engines"] >= 0
            assert data["successful_engines"] >= 0
    
    def test_run_benchmark_with_reference_audio(self, client: TestClient, sample_reference_audio_id: str, sample_test_text: str):
        """Test running benchmark with reference audio ID."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "reference_audio_id": sample_reference_audio_id,
                "test_text": sample_test_text,
                "language": "en",
                "engines": ["tortoise"],
                "enhance_quality": False
            }
        )
        
        assert response.status_code in [200, 404, 503]
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
    
    def test_run_benchmark_all_engines(self, client: TestClient, sample_profile_id: str, sample_test_text: str):
        """Test running benchmark with all available engines."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": sample_test_text,
                "language": "en",
                "enhance_quality": True
            }
        )
        
        assert response.status_code in [200, 404, 503]
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert len(data["results"]) > 0
    
    def test_run_benchmark_minimal_request(self, client: TestClient, sample_profile_id: str):
        """Test running benchmark with minimal required fields."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": "Test"
            }
        )
        
        assert response.status_code in [200, 404, 503]
    
    def test_run_benchmark_result_structure(self, client: TestClient, sample_profile_id: str, sample_test_text: str):
        """Test that benchmark results have correct structure."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": sample_test_text,
                "engines": ["xtts"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data["results"]
            
            for result in results:
                assert "engine" in result
                assert "success" in result
                assert isinstance(result["success"], bool)
                
                if result["success"]:
                    assert "quality_metrics" in result
                    assert "performance" in result
                    
                    metrics = result["quality_metrics"]
                    if metrics:
                        # Check that metrics are valid if present
                        if "mos_score" in metrics:
                            assert isinstance(metrics["mos_score"], (int, float))
                            assert 0.0 <= metrics["mos_score"] <= 5.0
    
    def test_run_benchmark_missing_profile_and_audio(self, client: TestClient, sample_test_text: str):
        """Test running benchmark without profile_id or reference_audio_id."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "test_text": sample_test_text
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_run_benchmark_missing_test_text(self, client: TestClient, sample_profile_id: str):
        """Test running benchmark without test_text."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_run_benchmark_invalid_engine_list(self, client: TestClient, sample_profile_id: str, sample_test_text: str):
        """Test running benchmark with invalid engine names."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": sample_test_text,
                "engines": ["invalid_engine_1", "invalid_engine_2"]
            }
        )
        
        # Should either accept and return failures or return validation error
        assert response.status_code in [200, 422, 503]
        if response.status_code == 200:
            data = response.json()
            # All engines should fail
            for result in data["results"]:
                assert result["success"] == False
                assert "error" in result


class TestQualityBenchmarkingErrorHandling:
    """Test error handling scenarios for Quality Benchmarking."""
    
    def test_invalid_json(self, client: TestClient):
        """Test with invalid JSON."""
        response = client.post(
            "/api/quality/benchmark",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_empty_test_text(self, client: TestClient, sample_profile_id: str):
        """Test with empty test text."""
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": ""
            }
        )
        
        # Should either accept empty text or return validation error
        assert response.status_code in [200, 422]
    
    def test_very_long_test_text(self, client: TestClient, sample_profile_id: str):
        """Test with very long test text."""
        long_text = "Test " * 1000
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": sample_profile_id,
                "test_text": long_text
            }
        )
        
        # Should handle long text (may be slow but should not error)
        assert response.status_code in [200, 404, 413, 503]  # 413 = Payload Too Large

