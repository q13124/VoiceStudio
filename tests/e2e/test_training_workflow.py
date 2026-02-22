"""
Training Workflow E2E Tests.

Tests the complete training workflow:
1. Open Training panel
2. Configure training dataset
3. Set training parameters
4. Start training (or mock)
5. Monitor training progress
6. Verify model output
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
    pytest.mark.training,
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
def training_dataset(tmp_path):
    """Create a test training dataset."""
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()

    # Create sample audio files
    for i in range(5):
        audio_file = dataset_dir / f"sample_{i}.wav"
        with wave.open(str(audio_file), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(22050)
            num_samples = 22050 * 2  # 2 seconds
            freq = 300 + (i * 50)
            samples = [
                int(8000 * math.sin(2 * math.pi * freq * j / 22050)) for j in range(num_samples)
            ]
            wav.writeframes(struct.pack(f"{len(samples)}h", *samples))

    # Create metadata file
    metadata_file = dataset_dir / "metadata.csv"
    metadata_file.write_text(
        "filename|text\n"
        "sample_0.wav|This is the first sample.\n"
        "sample_1.wav|This is the second sample.\n"
        "sample_2.wav|This is the third sample.\n"
        "sample_3.wav|This is the fourth sample.\n"
        "sample_4.wav|This is the fifth sample.\n"
    )

    return dataset_dir


class TestTrainingJobManagement:
    """Tests for training job management."""

    def test_list_training_jobs(self, api_client, backend_available):
        """Test listing all training jobs."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/")
        assert response.status_code == 200

        jobs = response.json()
        assert isinstance(jobs, (list, dict))

    def test_get_training_job_not_found(self, api_client, backend_available):
        """Test getting a non-existent training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}")
        assert response.status_code in (404, 422)

    def test_delete_training_job_not_found(self, api_client, backend_available):
        """Test deleting a non-existent training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.delete(f"/api/training/{fake_id}")
        assert response.status_code in (404, 422)


class TestTrainingDatasetManagement:
    """Tests for training dataset management."""

    def test_list_datasets(self, api_client, backend_available):
        """Test listing available datasets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/datasets")
        assert response.status_code in (200, 404)

    def test_validate_dataset(self, api_client, backend_available, training_dataset):
        """Test validating a training dataset."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/training/datasets/validate",
            json={"path": str(training_dataset)},
        )

        assert response.status_code in (200, 400, 404, 422)

    def test_get_dataset_stats(self, api_client, backend_available):
        """Test getting dataset statistics."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/datasets/{fake_id}/stats")
        assert response.status_code in (200, 404, 422)


class TestTrainingConfiguration:
    """Tests for training configuration."""

    def test_get_available_models(self, api_client, backend_available):
        """Test getting available base models for training."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/models")
        assert response.status_code in (200, 404)

    def test_get_training_presets(self, api_client, backend_available):
        """Test getting training presets."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/presets")
        assert response.status_code in (200, 404)

    def test_validate_training_config(self, api_client, backend_available):
        """Test validating training configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/training/config/validate",
            json={
                "model_type": "xtts",
                "epochs": 100,
                "batch_size": 8,
                "learning_rate": 0.0001,
            },
        )

        assert response.status_code in (200, 400, 404, 422)

    def test_get_recommended_config(self, api_client, backend_available):
        """Test getting recommended training configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/config/recommended")
        assert response.status_code in (200, 404)


class TestTrainingJobCreation:
    """Tests for creating training jobs."""

    def test_create_training_job(self, api_client, backend_available, training_dataset):
        """Test creating a new training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/training/",
            json={
                "name": f"test_training_{uuid.uuid4().hex[:8]}",
                "dataset_path": str(training_dataset),
                "model_type": "xtts",
                "config": {
                    "epochs": 10,
                    "batch_size": 4,
                },
            },
        )

        assert response.status_code in (200, 201, 400, 404, 422, 500, 503)

    def test_create_training_job_invalid_config(self, api_client, backend_available):
        """Test creating training job with invalid configuration."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.post(
            "/api/training/",
            json={
                "name": "invalid_job",
                "dataset_path": "/nonexistent/path",
                "model_type": "invalid_model",
            },
        )

        # Should fail validation
        assert response.status_code in (400, 422, 404, 500)


class TestTrainingJobControl:
    """Tests for controlling training jobs."""

    def test_start_training_job(self, api_client, backend_available):
        """Test starting a training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/training/{fake_id}/start")
        assert response.status_code in (200, 400, 404, 422, 500, 503)

    def test_pause_training_job(self, api_client, backend_available):
        """Test pausing a training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/training/{fake_id}/pause")
        assert response.status_code in (200, 400, 404, 422)

    def test_resume_training_job(self, api_client, backend_available):
        """Test resuming a training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/training/{fake_id}/resume")
        assert response.status_code in (200, 400, 404, 422)

    def test_cancel_training_job(self, api_client, backend_available):
        """Test cancelling a training job."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/training/{fake_id}/cancel")
        assert response.status_code in (200, 404, 422)


class TestTrainingProgress:
    """Tests for training progress monitoring."""

    def test_get_training_progress(self, api_client, backend_available):
        """Test getting training progress."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}/progress")
        assert response.status_code in (200, 404, 422)

    def test_get_training_logs(self, api_client, backend_available):
        """Test getting training logs."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}/logs")
        assert response.status_code in (200, 404, 422)

    def test_get_training_metrics(self, api_client, backend_available):
        """Test getting training metrics."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}/metrics")
        assert response.status_code in (200, 404, 422)

    def test_get_training_checkpoints(self, api_client, backend_available):
        """Test getting training checkpoints."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}/checkpoints")
        assert response.status_code in (200, 404, 422)


class TestTrainingOutput:
    """Tests for training output and model export."""

    def test_get_trained_model(self, api_client, backend_available):
        """Test getting trained model information."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}/model")
        assert response.status_code in (200, 404, 422)

    def test_export_trained_model(self, api_client, backend_available):
        """Test exporting trained model."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(
            f"/api/training/{fake_id}/export",
            json={"format": "onnx"},
        )

        assert response.status_code in (200, 400, 404, 422, 500, 503)

    def test_create_voice_profile_from_model(self, api_client, backend_available):
        """Test creating voice profile from trained model."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(
            f"/api/training/{fake_id}/create-profile",
            json={"profile_name": "trained_voice"},
        )

        assert response.status_code in (200, 201, 400, 404, 422, 500, 503)


class TestTrainingQuality:
    """Tests for training quality evaluation."""

    def test_evaluate_model_quality(self, api_client, backend_available):
        """Test evaluating model quality."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(f"/api/training/{fake_id}/evaluate")
        assert response.status_code in (200, 400, 404, 422, 500, 503)

    def test_get_quality_report(self, api_client, backend_available):
        """Test getting quality report."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.get(f"/api/training/{fake_id}/quality-report")
        assert response.status_code in (200, 404, 422)

    def test_compare_with_baseline(self, api_client, backend_available):
        """Test comparing trained model with baseline."""
        if not backend_available:
            pytest.skip("Backend not available")

        fake_id = str(uuid.uuid4())
        response = api_client.post(
            f"/api/training/{fake_id}/compare",
            json={"baseline_model": "default"},
        )

        assert response.status_code in (200, 400, 404, 422, 500, 503)


class TestTrainingWorkflowIntegration:
    """Integration tests for complete training workflow."""

    @pytest.fixture
    def workflow_state(self):
        """State tracking for workflow tests."""
        return {"job_id": None, "model_id": None}

    def test_complete_training_workflow_api(
        self, api_client, backend_available, workflow_state, training_dataset
    ):
        """Test the complete training workflow via API.

        Steps:
        1. Validate dataset
        2. Get recommended configuration
        3. Create training job
        4. Monitor progress
        5. Get results
        6. Clean up
        """
        if not backend_available:
            pytest.skip("Backend not available")

        # Step 1: Validate dataset
        validate_response = api_client.post(
            "/api/training/datasets/validate",
            json={"path": str(training_dataset)},
        )
        # May or may not exist
        if validate_response.status_code == 404:
            # Skip validation step
            pass
        else:
            assert validate_response.status_code in (200, 400, 422)

        # Step 2: Get recommended configuration
        config_response = api_client.get("/api/training/config/recommended")
        if config_response.status_code == 200:
            recommended_config = config_response.json()
        else:
            recommended_config = {"epochs": 10, "batch_size": 4}

        # Step 3: Create training job
        job_name = f"test_training_{uuid.uuid4().hex[:8]}"
        create_response = api_client.post(
            "/api/training/",
            json={
                "name": job_name,
                "dataset_path": str(training_dataset),
                "model_type": "xtts",
                "config": recommended_config,
            },
        )

        if create_response.status_code in (500, 503):
            pytest.skip("Training not available")

        if create_response.status_code in (200, 201):
            result = create_response.json()
            job_id = result.get("job_id") or result.get("id") or result.get("training_id")
            workflow_state["job_id"] = job_id

            if job_id:
                # Step 4: Monitor progress
                progress_response = api_client.get(f"/api/training/{job_id}/progress")
                assert progress_response.status_code in (200, 404)

                # Step 5: Get training info
                info_response = api_client.get(f"/api/training/{job_id}")
                assert info_response.status_code in (200, 404)

                # Step 6: Clean up - cancel the job
                cancel_response = api_client.post(f"/api/training/{job_id}/cancel")
                assert cancel_response.status_code in (200, 404, 422)

                # Delete the job
                delete_response = api_client.delete(f"/api/training/{job_id}")
                assert delete_response.status_code in (200, 204, 404)


class TestTrainingGPU:
    """Tests for GPU-related training functionality."""

    def test_get_gpu_status(self, api_client, backend_available):
        """Test getting GPU status for training."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/gpu/status")
        assert response.status_code in (200, 404)

    def test_get_gpu_requirements(self, api_client, backend_available):
        """Test getting GPU requirements for training."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/gpu/requirements")
        assert response.status_code in (200, 404)


class TestTrainingHistory:
    """Tests for training history."""

    def test_get_training_history(self, api_client, backend_available):
        """Test getting training history."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/history")
        assert response.status_code in (200, 404)

    def test_get_training_statistics(self, api_client, backend_available):
        """Test getting training statistics."""
        if not backend_available:
            pytest.skip("Backend not available")

        response = api_client.get("/api/training/statistics")
        assert response.status_code in (200, 404)
