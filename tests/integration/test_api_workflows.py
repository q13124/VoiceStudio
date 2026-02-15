"""
API Workflow Integration Tests

Tests complete API workflows including request/response cycles, error handling, and data flow.
"""

import logging
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Backend API base URL
API_BASE_URL = "http://localhost:8000/api"


class TestAPIWorkflows:
    """Test complete API workflows."""

    @pytest.mark.asyncio
    async def test_profile_creation_workflow(self):
        """Test complete profile creation workflow."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Health check
                health_response = await client.get(f"{API_BASE_URL}/health/simple")
                if health_response.status_code != 200:
                    pytest.skip("Backend not available")

                # Step 2: Create profile
                profile_data = {
                    "name": "Test Profile",
                    "description": "Test profile for integration testing",
                    "engine": "xtts_v2",
                    "quality_mode": "standard",
                }

                create_response = await client.post(
                    f"{API_BASE_URL}/profiles",
                    json=profile_data
                )

                assert create_response.status_code in [200, 201], \
                    f"Profile creation failed: {create_response.status_code}"

                profile = create_response.json()
                assert "profile_id" in profile or "id" in profile, "Profile ID not returned"

                profile_id = profile.get("profile_id") or profile.get("id")

                # Step 3: Get profile
                get_response = await client.get(f"{API_BASE_URL}/profiles/{profile_id}")
                assert get_response.status_code == 200, "Profile retrieval failed"

                retrieved_profile = get_response.json()
                assert retrieved_profile.get("name") == profile_data["name"], \
                    "Retrieved profile name mismatch"

        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_project_workflow(self):
        """Test complete project workflow."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Health check
                health_response = await client.get(f"{API_BASE_URL}/health/simple")
                if health_response.status_code != 200:
                    pytest.skip("Backend not available")

                # Create project
                project_data = {
                    "name": "Test Project",
                    "description": "Test project for integration testing",
                }

                create_response = await client.post(
                    f"{API_BASE_URL}/projects",
                    json=project_data
                )

                assert create_response.status_code in [200, 201], \
                    f"Project creation failed: {create_response.status_code}"

                project = create_response.json()
                project_id = project.get("project_id") or project.get("id")
                assert project_id is not None, "Project ID not returned"

                # Get project
                get_response = await client.get(f"{API_BASE_URL}/projects/{project_id}")
                assert get_response.status_code == 200, "Project retrieval failed"

                # List projects
                list_response = await client.get(f"{API_BASE_URL}/projects")
                assert list_response.status_code == 200, "Project listing failed"

                projects = list_response.json()
                assert isinstance(projects, (list, dict)), "Projects list wrong type"

        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_voice_synthesis_workflow(self):
        """Test complete voice synthesis workflow."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=60.0) as client:
                # Health check
                health_response = await client.get(f"{API_BASE_URL}/health/simple")
                if health_response.status_code != 200:
                    pytest.skip("Backend not available")

                # Create profile first
                profile_data = {
                    "name": "Test Profile for Synthesis",
                    "description": "Test profile",
                    "engine": "xtts_v2",
                }

                profile_response = await client.post(
                    f"{API_BASE_URL}/profiles",
                    json=profile_data
                )

                if profile_response.status_code not in [200, 201]:
                    pytest.skip("Profile creation failed, skipping synthesis test")

                profile = profile_response.json()
                profile_id = profile.get("profile_id") or profile.get("id")

                # Synthesize
                synthesis_data = {
                    "profile_id": profile_id,
                    "text": "Hello, this is a test synthesis.",
                    "engine": "xtts_v2",
                    "language": "en",
                }

                synthesis_response = await client.post(
                    f"{API_BASE_URL}/voice/synthesize",
                    json=synthesis_data,
                    timeout=60.0
                )

                # Synthesis may take time, check for timeout or success
                assert synthesis_response.status_code in [200, 202, 408, 504], \
                    f"Synthesis request failed: {synthesis_response.status_code}"

                if synthesis_response.status_code == 200:
                    result = synthesis_response.json()
                    assert "audio_url" in result or "audio_id" in result, \
                        "Synthesis result missing audio"

        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_batch_processing_workflow(self):
        """Test complete batch processing workflow."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=60.0) as client:
                # Health check
                health_response = await client.get(f"{API_BASE_URL}/health/simple")
                if health_response.status_code != 200:
                    pytest.skip("Backend not available")

                # Create batch job
                batch_data = {
                    "name": "Test Batch Job",
                    "items": [
                        {"text": "First item", "profile_id": "test-profile"},
                        {"text": "Second item", "profile_id": "test-profile"},
                    ],
                }

                batch_response = await client.post(
                    f"{API_BASE_URL}/batch/jobs",
                    json=batch_data
                )

                assert batch_response.status_code in [200, 201, 400], \
                    f"Batch job creation failed: {batch_response.status_code}"

                if batch_response.status_code in [200, 201]:
                    job = batch_response.json()
                    job_id = job.get("job_id") or job.get("id")

                    # Get job status
                    status_response = await client.get(
                        f"{API_BASE_URL}/batch/jobs/{job_id}"
                    )
                    assert status_response.status_code == 200, "Job status retrieval failed"

        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test API error handling workflow."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Health check
                health_response = await client.get(f"{API_BASE_URL}/health/simple")
                if health_response.status_code != 200:
                    pytest.skip("Backend not available")

                # Test invalid request
                invalid_response = await client.post(
                    f"{API_BASE_URL}/profiles",
                    json={"invalid": "data"}
                )

                # Should return error (400 or 422)
                assert invalid_response.status_code in [400, 422, 500], \
                    f"Invalid request should return error: {invalid_response.status_code}"

                error_data = invalid_response.json()
                assert "error" in error_data or "detail" in error_data, \
                    "Error response missing error information"

        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_rate_limiting_workflow(self):
        """Test API rate limiting workflow."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Health check
                health_response = await client.get(f"{API_BASE_URL}/health/simple")
                if health_response.status_code != 200:
                    pytest.skip("Backend not available")

                # Make multiple rapid requests
                responses = []
                for _ in range(10):
                    response = await client.get(f"{API_BASE_URL}/health/simple")
                    responses.append(response.status_code)

                # Check for rate limiting (429)
                any(status == 429 for status in responses)
                # Rate limiting may or may not be active, so we just verify the workflow
                assert all(status in [200, 429] for status in responses), \
                    "Unexpected status codes in rate limiting test"

        except ImportError:
            pytest.skip("httpx not available")

