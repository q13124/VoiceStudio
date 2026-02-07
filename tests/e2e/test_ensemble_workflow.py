"""
End-to-End test for Ensemble Synthesis workflow.

Tests the complete ensemble synthesis workflow including:
- Multi-voice synthesis
- Multi-engine ensemble synthesis (IDEA 55)
- Job status polling
- Result aggregation
"""

import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to path to enable proper package imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.main import app


class TestEnsembleWorkflow:
    """End-to-end tests for ensemble synthesis workflows."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_create_ensemble_job(self, client: TestClient):
        """
        POST /api/ensemble creates an ensemble job and returns job_id.
        """
        print("\n[E2E] Creating ensemble synthesis job...")
        
        # Create ensemble request
        response = client.post(
            "/api/ensemble",
            json={
                "voices": [
                    {"profile_id": "default", "text": "Hello from voice one.", "engine": "piper"},
                    {"profile_id": "default", "text": "Hello from voice two.", "engine": "piper"},
                ],
                "mix_mode": "sequential",
                "output_format": "wav",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        print(f"[E2E] Ensemble job created: {data['job_id']}, status: {data['status']}")

    def test_get_ensemble_job_status(self, client: TestClient):
        """
        GET /api/ensemble/{job_id} returns job progress and status.
        """
        print("\n[E2E] Testing ensemble job status polling...")
        
        # Create a job first
        create_response = client.post(
            "/api/ensemble",
            json={
                "voices": [
                    {"profile_id": "test", "text": "Test synthesis."},
                ],
                "mix_mode": "sequential",
            },
        )
        
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        print(f"[E2E] Created job: {job_id}")
        
        # Poll for status
        status_response = client.get(f"/api/ensemble/{job_id}")
        assert status_response.status_code == 200
        
        status = status_response.json()
        assert "status" in status
        assert "progress" in status
        assert "completed_voices" in status
        assert "total_voices" in status
        print(f"[E2E] Job status: {status['status']}, progress: {status['progress']}")

    def test_list_ensemble_jobs(self, client: TestClient):
        """
        GET /api/ensemble lists all ensemble jobs.
        """
        print("\n[E2E] Listing ensemble jobs...")
        
        response = client.get("/api/ensemble")
        assert response.status_code == 200
        
        jobs = response.json()
        assert isinstance(jobs, list)
        print(f"[E2E] Found {len(jobs)} ensemble jobs")

    def test_cancel_ensemble_job(self, client: TestClient):
        """
        POST /api/ensemble/{job_id}/cancel cancels a running job.
        """
        print("\n[E2E] Testing ensemble job cancellation...")
        
        # Create a job
        create_response = client.post(
            "/api/ensemble",
            json={
                "voices": [
                    {"profile_id": "test", "text": "This job will be cancelled."},
                    {"profile_id": "test", "text": "This too."},
                    {"profile_id": "test", "text": "And this."},
                ],
                "mix_mode": "sequential",
            },
        )
        
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        print(f"[E2E] Created job for cancellation: {job_id}")
        
        # Cancel the job
        cancel_response = client.post(f"/api/ensemble/{job_id}/cancel")
        # Accept 200 (cancelled) or 404 (if job already completed)
        assert cancel_response.status_code in [200, 404]
        print(f"[E2E] Cancel response: {cancel_response.status_code}")


class TestMultiEngineEnsembleWorkflow:
    """End-to-end tests for multi-engine ensemble synthesis (IDEA 55)."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_create_multi_engine_ensemble(self, client: TestClient):
        """
        POST /api/ensemble/multi-engine creates a multi-engine ensemble job.
        """
        print("\n[E2E] Creating multi-engine ensemble job...")
        
        response = client.post(
            "/api/ensemble/multi-engine",
            json={
                "text": "Test multi-engine synthesis.",
                "profile_id": "default",
                "engines": ["piper", "silero"],
                "selection_mode": "voting",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"[E2E] Multi-engine ensemble job created: {data['job_id']}")

    def test_get_multi_engine_status(self, client: TestClient):
        """
        GET /api/ensemble/multi-engine/{job_id} returns job status.
        """
        print("\n[E2E] Testing multi-engine ensemble job status...")
        
        # Create a job first
        create_response = client.post(
            "/api/ensemble/multi-engine",
            json={
                "text": "Status check test.",
                "profile_id": "default",
                "engines": ["piper"],
            },
        )
        
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        
        # Get status
        status_response = client.get(f"/api/ensemble/multi-engine/{job_id}")
        assert status_response.status_code == 200
        
        status = status_response.json()
        assert "status" in status
        print(f"[E2E] Multi-engine job status: {status['status']}")

    def test_multi_engine_with_fusion_mode(self, client: TestClient):
        """
        Test multi-engine ensemble with fusion selection mode.
        """
        print("\n[E2E] Testing multi-engine ensemble with fusion mode...")
        
        response = client.post(
            "/api/ensemble/multi-engine",
            json={
                "text": "Fusion mode synthesis test.",
                "profile_id": "default",
                "engines": ["piper", "silero"],
                "selection_mode": "fusion",
                "fusion_strategy": "quality_weighted",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"[E2E] Fusion mode job created: {data['job_id']}")


class TestEnsembleMixModes:
    """End-to-end tests for different ensemble mix modes."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_sequential_mix_mode(self, client: TestClient):
        """
        Test sequential mix mode - voices one after another.
        """
        print("\n[E2E] Testing sequential mix mode...")
        
        response = client.post(
            "/api/ensemble",
            json={
                "voices": [
                    {"profile_id": "voice1", "text": "First voice."},
                    {"profile_id": "voice2", "text": "Second voice."},
                ],
                "mix_mode": "sequential",
            },
        )
        
        assert response.status_code == 200
        print(f"[E2E] Sequential mix job: {response.json()['job_id']}")

    def test_parallel_mix_mode(self, client: TestClient):
        """
        Test parallel mix mode - voices simultaneously.
        """
        print("\n[E2E] Testing parallel mix mode...")
        
        response = client.post(
            "/api/ensemble",
            json={
                "voices": [
                    {"profile_id": "voice1", "text": "Parallel voice one."},
                    {"profile_id": "voice2", "text": "Parallel voice two."},
                ],
                "mix_mode": "parallel",
            },
        )
        
        assert response.status_code == 200
        print(f"[E2E] Parallel mix job: {response.json()['job_id']}")

    def test_layered_mix_mode(self, client: TestClient):
        """
        Test layered mix mode - voices overlapping.
        """
        print("\n[E2E] Testing layered mix mode...")
        
        response = client.post(
            "/api/ensemble",
            json={
                "voices": [
                    {"profile_id": "voice1", "text": "Background layer."},
                    {"profile_id": "voice2", "text": "Foreground layer."},
                ],
                "mix_mode": "layered",
            },
        )
        
        assert response.status_code == 200
        print(f"[E2E] Layered mix job: {response.json()['job_id']}")


class TestEnsembleJobPolling:
    """End-to-end tests for ensemble job polling behavior."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_poll_until_complete(self, client: TestClient):
        """
        Test polling job status until completion or timeout.
        """
        print("\n[E2E] Testing job polling until completion...")
        
        # Create a job
        create_response = client.post(
            "/api/ensemble",
            json={
                "voices": [{"profile_id": "test", "text": "Poll test."}],
                "mix_mode": "sequential",
            },
        )
        
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        print(f"[E2E] Created job: {job_id}")
        
        # Poll with timeout
        max_attempts = 10
        poll_interval = 0.5  # seconds
        
        for attempt in range(max_attempts):
            status_response = client.get(f"/api/ensemble/{job_id}")
            assert status_response.status_code == 200
            
            status = status_response.json()["status"]
            progress = status_response.json().get("progress", 0)
            print(f"[E2E] Attempt {attempt + 1}/{max_attempts}: status={status}, progress={progress}")
            
            if status in ["completed", "failed"]:
                break
            
            time.sleep(poll_interval)
        
        print(f"[E2E] Final status: {status}")

    def test_job_not_found(self, client: TestClient):
        """
        Test retrieving status for non-existent job.
        """
        print("\n[E2E] Testing job not found scenario...")
        
        response = client.get("/api/ensemble/non-existent-job-id")
        assert response.status_code == 404
        print("[E2E] Correctly returned 404 for non-existent job")
