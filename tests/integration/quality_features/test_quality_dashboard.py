"""
Integration tests for Quality Dashboard endpoint.

Tests the /api/quality/dashboard endpoint.
"""

from fastapi.testclient import TestClient


class TestQualityDashboard:
    """Test suite for Quality Dashboard endpoint."""

    def test_get_dashboard_default(self, client: TestClient):
        """Test getting dashboard with default parameters."""
        response = client.get("/api/quality/dashboard")

        assert response.status_code in [
            200,
            503,
        ]  # 503 if quality optimization not available
        if response.status_code == 200:
            data = response.json()
            assert "overview" in data
            assert "trends" in data
            assert "distribution" in data
            assert "alerts" in data
            assert "insights" in data

    def test_get_dashboard_with_project_id(self, client: TestClient):
        """Test getting dashboard filtered by project ID."""
        response = client.get(
            "/api/quality/dashboard", params={"project_id": "test-project-123"}
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "overview" in data

    def test_get_dashboard_with_days(self, client: TestClient):
        """Test getting dashboard with custom days parameter."""
        response = client.get("/api/quality/dashboard", params={"days": 7})

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "trends" in data

    def test_get_dashboard_with_all_parameters(self, client: TestClient):
        """Test getting dashboard with all parameters."""
        response = client.get(
            "/api/quality/dashboard",
            params={"project_id": "test-project-123", "days": 30},
        )

        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "overview" in data
            assert "trends" in data

    def test_get_dashboard_overview_structure(self, client: TestClient):
        """Test that dashboard overview has correct structure."""
        response = client.get("/api/quality/dashboard")

        if response.status_code == 200:
            data = response.json()
            overview = data["overview"]

            assert "total_syntheses" in overview
            assert "average_mos_score" in overview
            assert "average_similarity" in overview
            assert "average_naturalness" in overview
            assert "quality_tier_distribution" in overview

            assert isinstance(overview["total_syntheses"], int)
            assert isinstance(overview["average_mos_score"], (int, float))
            assert isinstance(overview["average_similarity"], (int, float))
            assert isinstance(overview["average_naturalness"], (int, float))
            assert isinstance(overview["quality_tier_distribution"], dict)

    def test_get_dashboard_trends_structure(self, client: TestClient):
        """Test that dashboard trends have correct structure."""
        response = client.get("/api/quality/dashboard")

        if response.status_code == 200:
            data = response.json()
            trends = data["trends"]

            assert "mos_score" in trends
            assert "similarity" in trends
            assert "naturalness" in trends
            assert "dates" in trends

            assert isinstance(trends["mos_score"], list)
            assert isinstance(trends["similarity"], list)
            assert isinstance(trends["naturalness"], list)
            assert isinstance(trends["dates"], list)

    def test_get_dashboard_distribution_structure(self, client: TestClient):
        """Test that dashboard distribution has correct structure."""
        response = client.get("/api/quality/dashboard")

        if response.status_code == 200:
            data = response.json()
            distribution = data["distribution"]

            assert "mos_score" in distribution
            assert "similarity" in distribution
            assert "naturalness" in distribution

            assert isinstance(distribution["mos_score"], dict)
            assert isinstance(distribution["similarity"], dict)
            assert isinstance(distribution["naturalness"], dict)

    def test_get_dashboard_alerts_structure(self, client: TestClient):
        """Test that dashboard alerts have correct structure."""
        response = client.get("/api/quality/dashboard")

        if response.status_code == 200:
            data = response.json()
            alerts = data["alerts"]

            assert isinstance(alerts, list)
            # Alerts can be empty or contain alert objects

    def test_get_dashboard_insights_structure(self, client: TestClient):
        """Test that dashboard insights have correct structure."""
        response = client.get("/api/quality/dashboard")

        if response.status_code == 200:
            data = response.json()
            insights = data["insights"]

            assert isinstance(insights, list)
            # Insights can be empty or contain insight strings

    def test_get_dashboard_invalid_days(self, client: TestClient):
        """Test getting dashboard with invalid days parameter."""
        response = client.get("/api/quality/dashboard", params={"days": -1})

        # Should either clamp to valid range or return validation error
        assert response.status_code in [200, 422, 503]

    def test_get_dashboard_very_large_days(self, client: TestClient):
        """Test getting dashboard with very large days parameter."""
        response = client.get("/api/quality/dashboard", params={"days": 10000})

        # Should either clamp or return validation error
        assert response.status_code in [200, 422, 503]


class TestQualityDashboardErrorHandling:
    """Test error handling scenarios for Quality Dashboard."""

    def test_post_method_not_allowed(self, client: TestClient):
        """Test that POST method is not allowed."""
        response = client.post("/api/quality/dashboard")
        assert response.status_code in [405, 404]  # Method Not Allowed

    def test_invalid_query_parameters(self, client: TestClient):
        """Test with invalid query parameter types."""
        response = client.get("/api/quality/dashboard", params={"days": "not-a-number"})
        assert response.status_code in [422, 400]  # Validation error
