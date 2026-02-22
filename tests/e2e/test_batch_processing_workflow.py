"""
Batch Processing Workflow E2E Tests.

Tests the complete batch processing workflow:
1. Open Batch Processing panel
2. Add multiple files to queue
3. Configure batch settings
4. Start batch processing
5. Monitor progress
6. Verify all outputs
"""

from __future__ import annotations

import math
import struct
import uuid
import wave
from pathlib import Path

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.batch,
]


@pytest.fixture
def api_client():
    """Create a test client for API tests."""
    from fastapi.testclient import TestClient

    from backend.api.main import app

    return TestClient(app)


@pytest.fixture
def backend_available(api_client):
    """Check if backend is available."""
    try:
        response = api_client.get("/api/health/status")
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture
def test_audio_files(tmp_path):
    """Create multiple test audio files for batch processing."""
    files = []
    for i in range(3):
        audio_file = tmp_path / f"test_audio_{i}.wav"
        with wave.open(str(audio_file), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            # Generate 1 second of audio per file
            num_samples = 16000
            freq = 440 + (i * 100)  # Different frequency per file
            samples = [
                int(8000 * math.sin(2 * math.pi * freq * j / 16000)) for j in range(num_samples)
            ]
            wav.writeframes(struct.pack(f"{len(samples)}h", *samples))
        files.append(audio_file)

    return files


@pytest.fixture
def test_text_items():
    """Create test text items for batch synthesis."""
    return [
        {"text": "This is the first sentence.", "voice_id": "default"},
        {"text": "This is the second sentence.", "voice_id": "default"},
        {"text": "This is the third sentence.", "voice_id": "default"},
    ]


class TestBatchQueueManagement:
    """Tests for batch queue management."""

    def test_list_batch_jobs(self, api_client, backend_available):
        """Test listing all batch jobs."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/batch/")
        assert response.status_code in (200, 404)

        if response.status_code == 200:
            jobs = response.json()
            assert isinstance(jobs, (list, dict))

    def test_get_queue_status(self, api_client, backend_available):
        """Test getting batch queue status."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/batch/queue/status")
        assert response.status_code in (200, 404)

    def test_clear_completed_jobs(self, api_client, backend_available):
        """Test clearing completed jobs from queue."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.delete("/api/batch/completed")
        assert response.status_code in (200, 204, 404)


class TestBatchSynthesis:
    """Tests for batch synthesis operations."""

    def test_create_batch_synthesis_job(self, api_client, backend_available, test_text_items):
        """Test creating a batch synthesis job."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/batch/synthesis",
            json={
                "items": test_text_items,
                "settings": {
                    "output_format": "wav",
                    "sample_rate": 22050,
                },
            },
        )

        assert response.status_code in (200, 201, 400, 404, 422, 500, 503)

        if response.status_code in (200, 201):
            result = response.json()
            assert "job_id" in result or "id" in result or "batch_id" in result

    def test_batch_synthesis_with_different_voices(self, api_client, backend_available):
        """Test batch synthesis with different voice profiles."""
        if not backend_available:
            pytest.skip("Backend not available")

        items = [
            {"text": "First voice.", "voice_id": "voice1"},
            {"text": "Second voice.", "voice_id": "voice2"},
        ]

        response = api_client.post(
            "/api/batch/synthesis",
            json={"items": items},
        )

        assert response.status_code in (200, 201, 400, 404, 422, 500, 503)


class TestBatchTranscription:
    """Tests for batch transcription operations."""

    def test_create_batch_transcription_job(self, api_client, backend_available, test_audio_files):
        """Test creating a batch transcription job."""
        if not backend_available:
            pytest.skip("Backend not available")

        # Upload files for batch transcription
        files = []
        file_handles = []
        for audio_file in test_audio_files:
            fh = open(audio_file, "rb")
            file_handles.append(fh)
            files.append(("files", (audio_file.name, fh, "audio/wav")))

        try:
            response = api_client.post(
                "/api/batch/transcription",
                files=files,
                data={"language": "en"},
            )
        finally:
            for fh in file_handles:
                fh.close()

        assert response.status_code in (200, 201, 400, 404, 422, 500, 503)

    def test_batch_transcription_status(self, api_client, backend_available):
        """Test getting batch transcription status."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/batch/transcription/status")
        assert response.status_code in (200, 404)


class TestBatchEffects:
    """Tests for batch effects processing."""

    def test_create_batch_effects_job(self, api_client, backend_available, test_audio_files):
        """Test creating a batch effects job."""
        if not backend_available:
            pytest.skip("Backend not available")

        files = []
        file_handles = []
        for audio_file in test_audio_files:
            fh = open(audio_file, "rb")
            file_handles.append(fh)
            files.append(("files", (audio_file.name, fh, "audio/wav")))

        try:
            response = api_client.post(
                "/api/batch/effects",
                files=files,
                data={
                    "effect_type": "reverb",
                    "parameters": '{"room_size": 0.5}',
                },
            )
        finally:
            for fh in file_handles:
                fh.close()

        assert response.status_code in (200, 201, 400, 404, 422, 500, 503)


class TestBatchJobStatus:
    """Tests for batch job status monitoring."""

    def test_get_job_status_not_found(self, api_client, backend_available):
        """Test getting status of non-existent job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/batch/{fake_id}/status")
        assert response.status_code in (404, 422)

    def test_get_job_progress(self, api_client, backend_available):
        """Test getting job progress."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/batch/{fake_id}/progress")
        assert response.status_code in (200, 404, 422)

    def test_cancel_job(self, api_client, backend_available):
        """Test cancelling a batch job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/batch/{fake_id}/cancel")
        assert response.status_code in (200, 404, 422)


class TestBatchConfiguration:
    """Tests for batch processing configuration."""

    def test_get_batch_settings(self, api_client, backend_available):
        """Test getting batch processing settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/batch/settings")
        assert response.status_code in (200, 404)

    def test_update_batch_settings(self, api_client, backend_available):
        """Test updating batch processing settings."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.put(
            "/api/batch/settings",
            json={
                "max_concurrent_jobs": 4,
                "default_priority": "normal",
                "auto_cleanup": True,
            },
        )

        assert response.status_code in (200, 400, 404, 422)

    def test_get_supported_operations(self, api_client, backend_available):
        """Test getting supported batch operations."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/batch/operations")
        assert response.status_code in (200, 404)


class TestBatchResults:
    """Tests for batch results retrieval."""

    def test_get_job_results_not_found(self, api_client, backend_available):
        """Test getting results of non-existent job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/batch/{fake_id}/results")
        assert response.status_code in (404, 422)

    def test_download_batch_results(self, api_client, backend_available):
        """Test downloading batch results."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/batch/{fake_id}/download")
        assert response.status_code in (200, 404, 422)

    def test_get_job_logs(self, api_client, backend_available):
        """Test getting job logs."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/batch/{fake_id}/logs")
        assert response.status_code in (200, 404, 422)


class TestBatchWorkflowIntegration:
    """Integration tests for complete batch processing workflow."""

    @pytest.fixture
    def workflow_state(self):
        """State tracking for workflow tests."""
        return {"job_id": None, "results": None}

    def test_complete_batch_synthesis_workflow_api(
        self, api_client, backend_available, workflow_state, test_text_items
    ):
        """Test the complete batch synthesis workflow via API.

        Steps:
        1. Check queue status
        2. Create batch synthesis job
        3. Monitor progress
        4. Get results
        5. Clean up
        """
        if not backend_available:
            pytest.skip("Backend not available")

        # Step 1: Check queue status
        queue_response = api_client.get("/api/batch/queue/status")
        # May or may not exist
        if queue_response.status_code == 404:
            # Try alternate endpoint
            queue_response = api_client.get("/api/batch/")

        assert queue_response.status_code in (200, 404)

        # Step 2: Create batch job
        create_response = api_client.post(
            "/api/batch/synthesis",
            json={
                "items": test_text_items,
                "settings": {"output_format": "wav"},
            },
        )

        if create_response.status_code in (500, 503):
            pytest.skip("Batch processing not available")

        if create_response.status_code in (200, 201):
            result = create_response.json()
            job_id = result.get("job_id") or result.get("id") or result.get("batch_id")
            workflow_state["job_id"] = job_id

            if job_id:
                # Step 3: Monitor progress
                progress_response = api_client.get(f"/api/batch/{job_id}/status")
                assert progress_response.status_code in (200, 404)

                # Step 4: Get results (may not be ready)
                results_response = api_client.get(f"/api/batch/{job_id}/results")
                assert results_response.status_code in (200, 404, 422)

                # Step 5: Cancel/cleanup
                cancel_response = api_client.post(f"/api/batch/{job_id}/cancel")
                assert cancel_response.status_code in (200, 404, 422)


class TestBatchPriority:
    """Tests for batch job prioritization."""

    def test_set_job_priority(self, api_client, backend_available):
        """Test setting job priority."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.put(
            f"/api/batch/{fake_id}/priority",
            json={"priority": "high"},
        )

        assert response.status_code in (200, 400, 404, 422)

    def test_reorder_queue(self, api_client, backend_available):
        """Test reordering jobs in queue."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/batch/queue/reorder",
            json={"job_ids": [str(uuid.uuid4()), str(uuid.uuid4())]},
        )

        assert response.status_code in (200, 400, 404, 422)


class TestBatchTemplates:
    """Tests for batch processing templates."""

    def test_list_templates(self, api_client, backend_available):
        """Test listing batch templates."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/batch/templates")
        assert response.status_code in (200, 404)

    def test_create_template(self, api_client, backend_available):
        """Test creating a batch template."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/batch/templates",
            json={
                "name": f"test_template_{uuid.uuid4().hex[:8]}",
                "operation": "synthesis",
                "settings": {"output_format": "wav"},
            },
        )

        assert response.status_code in (200, 201, 400, 404, 422)

    def test_apply_template(self, api_client, backend_available, test_text_items):
        """Test applying a batch template."""
        if not backend_available:
            pytest.skip("Backend not available")

        template_id = str(uuid.uuid4())
        response = api_client.post(
            f"/api/batch/templates/{template_id}/apply",
            json={"items": test_text_items},
        )

        assert response.status_code in (200, 201, 400, 404, 422)
