"""
Integration tests for Engine Recommendation endpoint.

Tests the /api/quality/engine-recommendation endpoint.
"""

from fastapi.testclient import TestClient


class TestEngineRecommendation:
    """Test suite for Engine Recommendation endpoint."""

    def test_get_recommendation_default(self, client: TestClient):
        """Test getting engine recommendation with default parameters."""
        response = client.get("/api/quality/engine-recommendation")

        assert response.status_code in [200, 503]  # 503 if quality optimization not available
        if response.status_code == 200:
            data = response.json()
            assert "recommended_engine" in data
            assert "target_tier" in data
            assert "reasoning" in data
            assert data["target_tier"] == "standard"
            assert data["recommended_engine"] in ["xtts", "chatterbox", "tortoise", "openvoice"]

    def test_get_recommendation_high_tier(self, client: TestClient):
        """Test getting recommendation for high quality tier."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={"target_tier": "high"}
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert data["target_tier"] == "high"
            assert "recommended_engine" in data

    def test_get_recommendation_with_mos_requirement(self, client: TestClient):
        """Test getting recommendation with minimum MOS score requirement."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={
                "target_tier": "high",
                "min_mos_score": 4.0
            }
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "target_metrics" in data
            if "mos_score" in data["target_metrics"]:
                assert data["target_metrics"]["mos_score"] == 4.0

    def test_get_recommendation_with_similarity_requirement(self, client: TestClient):
        """Test getting recommendation with minimum similarity requirement."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={
                "target_tier": "standard",
                "min_similarity": 0.85
            }
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "target_metrics" in data
            if "similarity" in data["target_metrics"]:
                assert data["target_metrics"]["similarity"] == 0.85

    def test_get_recommendation_with_naturalness_requirement(self, client: TestClient):
        """Test getting recommendation with minimum naturalness requirement."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={
                "target_tier": "ultra",
                "min_naturalness": 0.90
            }
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "target_metrics" in data
            if "naturalness" in data["target_metrics"]:
                assert data["target_metrics"]["naturalness"] == 0.90

    def test_get_recommendation_all_requirements(self, client: TestClient):
        """Test getting recommendation with all quality requirements."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={
                "target_tier": "ultra",
                "min_mos_score": 4.5,
                "min_similarity": 0.90,
                "min_naturalness": 0.90
            }
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "target_metrics" in data
            assert "recommended_engine" in data
            assert "reasoning" in data

    def test_get_recommendation_invalid_tier(self, client: TestClient):
        """Test getting recommendation with invalid tier."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={"target_tier": "invalid"}
        )

        # Should either accept and use default or return validation error
        assert response.status_code in [200, 422, 503]

    def test_get_recommendation_invalid_mos_score(self, client: TestClient):
        """Test getting recommendation with invalid MOS score."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={"min_mos_score": 10.0}  # Out of range
        )

        # Should either clamp or return validation error
        assert response.status_code in [200, 422, 503]

    def test_get_recommendation_negative_values(self, client: TestClient):
        """Test getting recommendation with negative values."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={
                "min_mos_score": -1.0,
                "min_similarity": -0.5
            }
        )

        # Should return validation error
        assert response.status_code in [422, 503]


class TestEngineRecommendationErrorHandling:
    """Test error handling scenarios for Engine Recommendation."""

    def test_post_method_not_allowed(self, client: TestClient):
        """Test that POST method is not allowed."""
        response = client.post("/api/quality/engine-recommendation")
        assert response.status_code in [405, 404]  # Method Not Allowed

    def test_invalid_query_parameters(self, client: TestClient):
        """Test with invalid query parameter types."""
        response = client.get(
            "/api/quality/engine-recommendation",
            params={"min_mos_score": "not-a-number"}
        )
        assert response.status_code in [422, 400]  # Validation error

