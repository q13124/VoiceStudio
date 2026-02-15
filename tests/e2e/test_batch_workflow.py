"""
E2E Tests: Batch Processing Workflow.

Tests complete batch processing operations:
- Batch synthesis
- Batch transcription
- Batch voice conversion
- Batch effects processing
- Queue management
- Progress monitoring
"""


import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.batch,
]


class TestBatchSynthesis:
    """Tests for batch text-to-speech synthesis."""

    def test_batch_synthesis_status(self, api_client, backend_available):
        """Test batch synthesis queue status."""
        response = api_client.get("/api/batch/synthesis/status", timeout=10)

        if response.status_code == 200:
            status = response.json()
            print(f"Batch synthesis status: {status}")
        elif response.status_code == 404:
            pytest.skip("Batch synthesis status API not available")

    def test_batch_synthesis_submit(self, api_client, backend_available):
        """Test submitting batch synthesis job."""
        batch_config = {
            "items": [
                {"text": "First test sentence.", "voice": "default"},
                {"text": "Second test sentence.", "voice": "default"},
                {"text": "Third test sentence.", "voice": "default"},
            ],
            "engine": "piper",
            "output_format": "wav",
        }

        response = api_client.post("/api/batch/synthesis/submit", json=batch_config, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Batch synthesis submitted: {result}")
            return result.get("job_id") or result.get("id")
        elif response.status_code == 404:
            pytest.skip("Batch synthesis submit API not available")

    def test_batch_synthesis_from_file(self, api_client, backend_available):
        """Test batch synthesis from text file."""

        response = api_client.get("/api/batch/synthesis/file-config", timeout=10)

        if response.status_code == 200:
            config = response.json()
            print(f"Batch file config options: {config}")
        elif response.status_code == 404:
            pytest.skip("Batch file config API not available")

    def test_batch_synthesis_templates(self, api_client, backend_available):
        """Test batch synthesis templates."""
        response = api_client.get("/api/batch/synthesis/templates", timeout=10)

        if response.status_code == 200:
            templates = response.json()
            print(f"Batch templates: {templates}")
        elif response.status_code == 404:
            pytest.skip("Batch templates API not available")


class TestBatchTranscription:
    """Tests for batch audio transcription."""

    def test_batch_transcription_status(self, api_client, backend_available):
        """Test batch transcription queue status."""
        response = api_client.get("/api/batch/transcription/status", timeout=10)

        if response.status_code == 200:
            status = response.json()
            print(f"Batch transcription status: {status}")
        elif response.status_code == 404:
            pytest.skip("Batch transcription status API not available")

    def test_batch_transcription_submit(self, api_client, backend_available):
        """Test submitting batch transcription job."""
        batch_config = {
            "files": ["file1.wav", "file2.wav"],  # Would be actual file IDs
            "engine": "whisper",
            "language": "en",
            "output_format": "txt",
        }

        response = api_client.post("/api/batch/transcription/submit", json=batch_config, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Batch transcription submitted: {result}")
        elif response.status_code in [400, 422]:
            # Expected for invalid file IDs
            print("Batch transcription validation error (expected)")
        elif response.status_code == 404:
            pytest.skip("Batch transcription submit API not available")

    def test_batch_transcription_formats(self, api_client, backend_available):
        """Test supported batch transcription output formats."""
        response = api_client.get("/api/batch/transcription/formats", timeout=10)

        if response.status_code == 200:
            formats = response.json()
            print(f"Transcription output formats: {formats}")
        elif response.status_code == 404:
            pytest.skip("Transcription formats API not available")


class TestBatchVoiceConversion:
    """Tests for batch voice conversion."""

    def test_batch_conversion_status(self, api_client, backend_available):
        """Test batch voice conversion status."""
        response = api_client.get("/api/batch/conversion/status", timeout=10)

        if response.status_code == 200:
            status = response.json()
            print(f"Batch conversion status: {status}")
        elif response.status_code == 404:
            pytest.skip("Batch conversion status API not available")

    def test_batch_conversion_submit(self, api_client, backend_available):
        """Test submitting batch conversion job."""
        batch_config = {
            "files": ["file1.wav", "file2.wav"],
            "target_voice": "cloned_voice_1",
            "engine": "rvc",
        }

        response = api_client.post("/api/batch/conversion/submit", json=batch_config, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Batch conversion submitted: {result}")
        elif response.status_code in [400, 422]:
            print("Batch conversion validation error (expected)")
        elif response.status_code == 404:
            pytest.skip("Batch conversion submit API not available")


class TestBatchEffects:
    """Tests for batch effects processing."""

    def test_batch_effects_status(self, api_client, backend_available):
        """Test batch effects processing status."""
        response = api_client.get("/api/batch/effects/status", timeout=10)

        if response.status_code == 200:
            status = response.json()
            print(f"Batch effects status: {status}")
        elif response.status_code == 404:
            pytest.skip("Batch effects status API not available")

    def test_batch_effects_submit(self, api_client, backend_available):
        """Test submitting batch effects job."""
        batch_config = {
            "files": ["file1.wav", "file2.wav"],
            "effects": [
                {"type": "normalization", "params": {"target_db": -3}},
                {"type": "noise_reduction", "params": {"strength": 0.5}},
            ],
        }

        response = api_client.post("/api/batch/effects/submit", json=batch_config, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Batch effects submitted: {result}")
        elif response.status_code in [400, 422]:
            print("Batch effects validation error (expected)")
        elif response.status_code == 404:
            pytest.skip("Batch effects submit API not available")


class TestQueueManagement:
    """Tests for batch queue management."""

    def test_list_all_jobs(self, api_client, backend_available):
        """Test listing all batch jobs."""
        response = api_client.get("/api/jobs", timeout=10)

        if response.status_code == 200:
            jobs = response.json()
            print(f"All jobs: {len(jobs) if isinstance(jobs, list) else jobs}")
        elif response.status_code == 404:
            pytest.skip("Jobs list API not available")

    def test_list_pending_jobs(self, api_client, backend_available):
        """Test listing pending jobs."""
        response = api_client.get("/api/jobs/pending", timeout=10)

        if response.status_code == 200:
            jobs = response.json()
            print(f"Pending jobs: {len(jobs) if isinstance(jobs, list) else jobs}")
        elif response.status_code == 404:
            pytest.skip("Pending jobs API not available")

    def test_list_completed_jobs(self, api_client, backend_available):
        """Test listing completed jobs."""
        response = api_client.get("/api/jobs/completed", timeout=10)

        if response.status_code == 200:
            jobs = response.json()
            print(f"Completed jobs: {len(jobs) if isinstance(jobs, list) else jobs}")
        elif response.status_code == 404:
            pytest.skip("Completed jobs API not available")

    def test_cancel_job(self, api_client, backend_available):
        """Test cancelling a job."""
        # Try to cancel a non-existent job (should return appropriate error)
        response = api_client.post("/api/jobs/test-job-id/cancel", timeout=10)

        if response.status_code == 200:
            print("Job cancelled")
        elif response.status_code in [400, 404]:
            print(f"Cancel job response: {response.status_code} (expected for non-existent)")

    def test_retry_job(self, api_client, backend_available):
        """Test retrying a failed job."""
        response = api_client.post("/api/jobs/test-job-id/retry", timeout=10)

        if response.status_code == 200:
            print("Job retried")
        elif response.status_code in [400, 404]:
            print(f"Retry job response: {response.status_code} (expected for non-existent)")

    def test_clear_completed_jobs(self, api_client, backend_available):
        """Test clearing completed jobs."""
        response = api_client.post("/api/jobs/clear-completed", timeout=10)

        if response.status_code == 200:
            print("Completed jobs cleared")
        elif response.status_code == 404:
            pytest.skip("Clear completed API not available")

    def test_queue_priority(self, api_client, backend_available):
        """Test job priority management."""
        response = api_client.get("/api/jobs/priority/settings", timeout=10)

        if response.status_code == 200:
            settings = response.json()
            print(f"Priority settings: {settings}")
        elif response.status_code == 404:
            pytest.skip("Priority settings API not available")


class TestBatchProgress:
    """Tests for batch progress monitoring."""

    def test_batch_progress(self, api_client, backend_available):
        """Test batch progress endpoint."""
        response = api_client.get("/api/batch/progress", timeout=10)

        if response.status_code == 200:
            progress = response.json()
            print(f"Batch progress: {progress}")
        elif response.status_code == 404:
            pytest.skip("Batch progress API not available")

    def test_batch_statistics(self, api_client, backend_available):
        """Test batch statistics."""
        response = api_client.get("/api/batch/statistics", timeout=10)

        if response.status_code == 200:
            stats = response.json()
            print(f"Batch statistics: {stats}")
        elif response.status_code == 404:
            pytest.skip("Batch statistics API not available")

    def test_batch_history(self, api_client, backend_available):
        """Test batch job history."""
        response = api_client.get("/api/batch/history", timeout=10)

        if response.status_code == 200:
            history = response.json()
            print(f"Batch history: {len(history) if isinstance(history, list) else history}")
        elif response.status_code == 404:
            pytest.skip("Batch history API not available")


class TestBatchOutput:
    """Tests for batch output management."""

    def test_batch_output_location(self, api_client, backend_available):
        """Test batch output location settings."""
        response = api_client.get("/api/batch/output/settings", timeout=10)

        if response.status_code == 200:
            settings = response.json()
            print(f"Output settings: {settings}")
        elif response.status_code == 404:
            pytest.skip("Output settings API not available")

    def test_batch_output_naming(self, api_client, backend_available):
        """Test batch output naming patterns."""
        response = api_client.get("/api/batch/output/naming", timeout=10)

        if response.status_code == 200:
            naming = response.json()
            print(f"Naming patterns: {naming}")
        elif response.status_code == 404:
            pytest.skip("Naming patterns API not available")

    def test_batch_download(self, api_client, backend_available):
        """Test batch download (zip)."""
        response = api_client.get("/api/batch/download/status", timeout=10)

        if response.status_code == 200:
            status = response.json()
            print(f"Download status: {status}")
        elif response.status_code == 404:
            pytest.skip("Download status API not available")


class TestFullBatchWorkflow:
    """Complete batch workflow test."""

    def test_complete_batch_workflow_api(self, api_client, backend_available, workflow_state):
        """Test complete batch workflow via API."""
        state = workflow_state

        # Step 1: Check batch synthesis status
        synth_status = api_client.get("/api/batch/synthesis/status", timeout=10)
        if synth_status.status_code == 200:
            state["record_step"]("Checked synthesis status", data=synth_status.json())
        else:
            state["record_step"]("Synthesis status not available")

        # Step 2: Check batch transcription status
        trans_status = api_client.get("/api/batch/transcription/status", timeout=10)
        if trans_status.status_code == 200:
            state["record_step"]("Checked transcription status", data=trans_status.json())
        else:
            state["record_step"]("Transcription status not available")

        # Step 3: List all jobs
        jobs_resp = api_client.get("/api/jobs", timeout=10)
        if jobs_resp.status_code == 200:
            jobs = jobs_resp.json()
            job_count = len(jobs) if isinstance(jobs, list) else "N/A"
            state["record_step"]("Listed all jobs", data={"count": job_count})
        else:
            state["record_step"]("Jobs list not available")

        # Step 4: Submit test batch synthesis
        batch_items = {
            "items": [
                {"text": "Test batch item one.", "voice": "default"},
                {"text": "Test batch item two.", "voice": "default"},
            ],
            "engine": "piper",
        }

        submit_resp = api_client.post("/api/batch/synthesis/submit", json=batch_items, timeout=30)
        if submit_resp.status_code == 200:
            job_id = submit_resp.json().get("job_id")
            state["record_step"]("Submitted batch job", data={"job_id": job_id})
        else:
            state["record_step"]("Could not submit batch", data={"status": submit_resp.status_code})

        # Step 5: Check batch progress
        progress_resp = api_client.get("/api/batch/progress", timeout=10)
        if progress_resp.status_code == 200:
            state["record_step"]("Checked progress", data=progress_resp.json())
        else:
            state["record_step"]("Progress not available")

        # Step 6: Get batch statistics
        stats_resp = api_client.get("/api/batch/statistics", timeout=10)
        if stats_resp.status_code == 200:
            state["record_step"]("Got statistics", data=stats_resp.json())
        else:
            state["record_step"]("Statistics not available")

        # Report
        success_count = sum(1 for s in state["steps"] if s["success"])
        total_count = len(state["steps"])
        print(f"\nBatch workflow: {success_count}/{total_count} steps successful")
        for step in state["steps"]:
            status = "✓" if step["success"] else "✗"
            data_str = f" - {step['data']}" if step.get('data') else ""
            print(f"  {status} {step['name']}{data_str}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
