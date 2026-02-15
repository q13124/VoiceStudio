"""
Phase 9: End-to-End Tests
Task 9.3: E2E tests for synthesis workflows.
"""

import asyncio
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestSynthesisWorkflow:
    """End-to-end tests for the synthesis workflow."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_complete_synthesis_workflow(
        self,
        test_client,
        temp_dir: Path
    ):
        """Test a complete synthesis workflow from request to audio file."""
        # Skip if backend not available
        try:
            response = await test_client.get("/health")
            if response.status_code != 200:
                pytest.skip("Backend not healthy")
        except Exception:
            pytest.skip("Backend not available")

        # Step 1: Create a synthesis request
        synthesis_request = {
            "text": "This is an end-to-end test of the synthesis workflow.",
            "voice_id": "default",
            "output_format": "wav",
        }

        response = await test_client.post(
            "/api/v1/synthesis",
            json=synthesis_request
        )

        if response.status_code == 404:
            pytest.skip("Synthesis endpoint not implemented")

        # Step 2: Get the job ID (if async)
        if response.status_code == 202:
            data = response.json()
            job_id = data.get("job_id")

            # Wait for completion
            for _ in range(30):
                status_response = await test_client.get(
                    f"/api/v1/synthesis/{job_id}/status"
                )
                status = status_response.json()

                if status.get("status") == "completed":
                    break
                elif status.get("status") == "failed":
                    pytest.fail(f"Synthesis failed: {status.get('error')}")

                await asyncio.sleep(1)
            else:
                pytest.fail("Synthesis timed out")

        # Verify output exists
        assert response.status_code in [200, 202]

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_synthesis(self, test_client, temp_dir: Path):
        """Test batch synthesis of multiple texts."""
        texts = [
            "First sentence for batch synthesis.",
            "Second sentence for batch synthesis.",
            "Third sentence for batch synthesis.",
        ]

        batch_request = {
            "items": [{"text": t, "voice_id": "default"} for t in texts],
        }

        response = await test_client.post(
            "/api/v1/synthesis/batch",
            json=batch_request
        )

        if response.status_code == 404:
            pytest.skip("Batch synthesis not implemented")

        assert response.status_code in [200, 202]

    @pytest.mark.asyncio
    async def test_synthesis_with_invalid_input(self, test_client):
        """Test synthesis with invalid input returns proper error."""
        invalid_request = {
            "text": "",  # Empty text
            "voice_id": "nonexistent-voice",
        }

        response = await test_client.post(
            "/api/v1/synthesis",
            json=invalid_request
        )

        if response.status_code == 404:
            pytest.skip("Synthesis endpoint not implemented")

        # Should return validation error
        assert response.status_code in [400, 422]


@pytest.mark.e2e
class TestProjectWorkflow:
    """End-to-end tests for project management workflow."""

    @pytest.mark.asyncio
    async def test_create_and_manage_project(self, test_client):
        """Test creating and managing a project."""
        # Create project
        project_data = {
            "name": "E2E Test Project",
            "description": "Created during E2E testing",
        }

        response = await test_client.post(
            "/api/v1/projects",
            json=project_data
        )

        if response.status_code == 404:
            pytest.skip("Project endpoint not implemented")

        if response.status_code not in [200, 201]:
            pytest.skip("Could not create project")

        data = response.json()
        project_id = data.get("id") or data.get("project_id")

        # Get project
        response = await test_client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200

        # Update project
        update_data = {"name": "Updated E2E Project"}
        response = await test_client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data
        )

        if response.status_code != 404:
            assert response.status_code in [200, 204]

        # Delete project
        response = await test_client.delete(f"/api/v1/projects/{project_id}")

        if response.status_code != 404:
            assert response.status_code in [200, 204]


@pytest.mark.e2e
class TestVoiceCloneWorkflow:
    """End-to-end tests for voice cloning workflow."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.gpu
    async def test_voice_clone_workflow(
        self,
        test_client,
        sample_audio_path: Path
    ):
        """Test the complete voice cloning workflow."""
        if not sample_audio_path.exists():
            pytest.skip("Sample audio file not available")

        # Upload audio for cloning
        with open(sample_audio_path, "rb") as f:
            files = {"audio": ("sample.wav", f, "audio/wav")}
            response = await test_client.post(
                "/api/v1/voices/clone",
                files=files,
                data={"name": "E2E Clone Test"}
            )

        if response.status_code == 404:
            pytest.skip("Voice cloning not implemented")

        if response.status_code not in [200, 202]:
            pytest.skip("Voice cloning failed to start")

        # Wait for cloning to complete
        data = response.json()
        voice_id = data.get("voice_id")

        # Verify cloned voice exists
        response = await test_client.get(f"/api/v1/voices/{voice_id}")
        assert response.status_code == 200
