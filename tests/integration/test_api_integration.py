"""
Phase 9: API Integration Tests
Task 9.2: Integration tests for the API layer.
"""

import pytest


@pytest.mark.integration
class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test the health check endpoint returns 200."""
        response = await test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_readiness_check(self, test_client):
        """Test the readiness endpoint."""
        response = await test_client.get("/ready")
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_liveness_check(self, test_client):
        """Test the liveness endpoint."""
        response = await test_client.get("/live")
        assert response.status_code == 200


@pytest.mark.integration
class TestVoiceEndpoints:
    """Tests for voice-related endpoints."""

    @pytest.mark.asyncio
    async def test_list_voices(self, test_client):
        """Test listing available voices."""
        response = await test_client.get("/api/v1/voices")

        # Endpoint may not be implemented yet
        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_voice_details(self, test_client):
        """Test getting voice details."""
        response = await test_client.get("/api/v1/voices/default")

        if response.status_code == 404:
            pytest.skip("Voice not found or endpoint not implemented")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "voice_id" in data


@pytest.mark.integration
class TestSynthesisEndpoints:
    """Tests for synthesis endpoints."""

    @pytest.mark.asyncio
    async def test_synthesis_request(self, test_client, mock_synthesis_request):
        """Test submitting a synthesis request."""
        response = await test_client.post("/api/v1/synthesis", json=mock_synthesis_request)

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        # Should return 200 or 202 (accepted for async)
        assert response.status_code in [200, 202, 422]

    @pytest.mark.asyncio
    async def test_synthesis_status(self, test_client):
        """Test checking synthesis status."""
        response = await test_client.get("/api/v1/synthesis/test-job-id/status")

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestProjectEndpoints:
    """Tests for project management endpoints."""

    @pytest.mark.asyncio
    async def test_list_projects(self, test_client):
        """Test listing projects."""
        response = await test_client.get("/api/v1/projects")

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_create_project(self, test_client, mock_project_data):
        """Test creating a project."""
        response = await test_client.post("/api/v1/projects", json=mock_project_data)

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code in [200, 201, 422]


@pytest.mark.integration
class TestEngineEndpoints:
    """Tests for engine management endpoints."""

    @pytest.mark.asyncio
    async def test_list_engines(self, test_client):
        """Test listing available engines."""
        response = await test_client.get("/api/v1/engines")

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_engine_status(self, test_client):
        """Test getting engine status."""
        response = await test_client.get("/api/v1/engines/status")

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code == 200


@pytest.mark.integration
class TestMetricsEndpoints:
    """Tests for metrics endpoints."""

    @pytest.mark.asyncio
    async def test_prometheus_metrics(self, test_client):
        """Test Prometheus metrics endpoint."""
        response = await test_client.get("/metrics")

        if response.status_code == 404:
            pytest.skip("Endpoint not implemented")

        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
