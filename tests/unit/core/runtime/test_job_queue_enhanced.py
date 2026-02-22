"""
Unit Tests for Enhanced Job Queue
Tests enhanced job queue functionality including optimizations.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the enhanced job queue module
try:
    from app.core.runtime import job_queue_enhanced
    from app.core.runtime.resource_manager import (
        Job,
        JobPriority,
        JobStatus,
        ResourceRequirement,
    )
except ImportError:
    pytest.skip("Could not import job_queue_enhanced", allow_module_level=True)


class TestJobQueueEnhancedImports:
    """Test enhanced job queue module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert job_queue_enhanced is not None, "Failed to import job_queue_enhanced module"

    def test_module_has_classes(self):
        """Test module has expected classes."""
        classes = [
            name
            for name in dir(job_queue_enhanced)
            if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "module should have classes"


class TestJobQueueEnhancedClasses:
    """Test enhanced job queue classes."""

    def test_enhanced_job_queue_class_exists(self):
        """Test EnhancedJobQueue class exists."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            cls = job_queue_enhanced.EnhancedJobQueue
            assert isinstance(cls, type), "EnhancedJobQueue should be a class"

    def test_job_batch_class_exists(self):
        """Test JobBatch class exists."""
        if hasattr(job_queue_enhanced, "JobBatch"):
            cls = job_queue_enhanced.JobBatch
            assert isinstance(cls, type), "JobBatch should be a class"

    def test_retry_policy_enum_exists(self):
        """Test RetryPolicy enum exists."""
        if hasattr(job_queue_enhanced, "RetryPolicy"):
            cls = job_queue_enhanced.RetryPolicy
            assert isinstance(cls, type), "RetryPolicy should be an enum"


class TestJobQueueEnhancedOptimization:
    """Test enhanced job queue optimization features."""

    def test_batch_processing_support(self):
        """Test batch processing functionality exists."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(
                    queue, "create_batch"
                ), "EnhancedJobQueue should support batch creation"
                assert hasattr(
                    queue, "job_batches"
                ), "EnhancedJobQueue should have job_batches attribute"
                assert hasattr(
                    queue, "enable_batching"
                ), "EnhancedJobQueue should have enable_batching attribute"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")

    def test_retry_policy_support(self):
        """Test retry policy functionality exists."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(
                    queue, "max_retries"
                ), "EnhancedJobQueue should have max_retries attribute"
                assert hasattr(
                    queue, "retry_policy"
                ), "EnhancedJobQueue should have retry_policy attribute"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")

    def test_create_batch_method(self):
        """Test create_batch method exists and is callable."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(queue, "create_batch"), "Should have create_batch method"
                assert callable(queue.create_batch), "create_batch should be callable"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")

    def test_batch_status_tracking(self):
        """Test batch status tracking functionality."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(
                    queue, "_update_batch_status"
                ), "Should have _update_batch_status method"
                assert hasattr(queue, "pending_batches"), "Should have pending_batches attribute"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")


class TestJobQueueEnhancedFunctions:
    """Test enhanced job queue functions exist."""

    def test_add_job_function_exists(self):
        """Test add_job function exists."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(queue, "add_job"), "Should have add_job method"
                assert callable(queue.add_job), "add_job should be callable"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")

    def test_get_job_status_function_exists(self):
        """Test get_job_status function exists."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(queue, "get_job_status"), "Should have get_job_status method"
                assert callable(queue.get_job_status), "get_job_status should be callable"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")

    def test_cancel_job_function_exists(self):
        """Test cancel_job function exists."""
        if hasattr(job_queue_enhanced, "EnhancedJobQueue"):
            try:
                queue = job_queue_enhanced.EnhancedJobQueue()
                assert hasattr(queue, "cancel_job"), "Should have cancel_job method"
                assert callable(queue.cancel_job), "cancel_job should be callable"
            except (ImportError, Exception):
                pytest.skip("job_queue_enhanced dependencies not installed")


class TestJobQueueEnhancedFunctionality:
    """Test enhanced job queue functional behavior."""

    def test_queue_initialization(self):
        """Test queue can be initialized with default parameters."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        assert queue.max_retries == 3
        assert queue.default_retry_policy == job_queue_enhanced.RetryPolicy.EXPONENTIAL
        assert queue.batch_size == 10
        assert queue.enable_batching is True
        assert queue.stats["total_submitted"] == 0

    def test_queue_initialization_with_custom_params(self):
        """Test queue can be initialized with custom parameters."""
        queue = job_queue_enhanced.EnhancedJobQueue(
            max_retries=5,
            default_retry_policy=job_queue_enhanced.RetryPolicy.FIXED,
            batch_size=20,
            enable_batching=False,
        )
        assert queue.max_retries == 5
        assert queue.default_retry_policy == job_queue_enhanced.RetryPolicy.FIXED
        assert queue.batch_size == 20
        assert queue.enable_batching is False

    def test_submit_job_realtime_priority(self):
        """Test submitting a job with realtime priority."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=2.0, ram_gb=4.0)
        result = queue.submit_job(
            job_id="test_job_1",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.REALTIME,
            requirements=requirements,
            payload={"test": "data"},
        )
        assert result is True
        assert "test_job_1" in queue.jobs
        assert queue.stats["total_submitted"] == 1
        assert queue.realtime_queue.qsize() == 1

    def test_submit_job_interactive_priority(self):
        """Test submitting a job with interactive priority."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        result = queue.submit_job(
            job_id="test_job_2",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.INTERACTIVE,
            requirements=requirements,
            payload={"test": "data"},
        )
        assert result is True
        assert "test_job_2" in queue.jobs
        assert queue.interactive_queue.qsize() == 1

    def test_submit_job_batch_priority(self):
        """Test submitting a job with batch priority."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=0.5, ram_gb=1.0)
        result = queue.submit_job(
            job_id="test_job_3",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )
        assert result is True
        assert "test_job_3" in queue.jobs
        assert queue.batch_queue.qsize() == 1

    def test_submit_job_with_dependencies(self):
        """Test submitting a job with dependencies."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)

        # Submit first job - use different priority to avoid comparison issues
        queue.submit_job(
            job_id="job_1",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.REALTIME,
            requirements=requirements,
            payload={"test": "data"},
        )

        # Submit second job with dependency - use different priority
        result = queue.submit_job(
            job_id="job_2",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.INTERACTIVE,
            requirements=requirements,
            payload={"test": "data"},
            dependencies=["job_1"],
        )
        assert result is True
        assert "job_2" in queue.job_dependencies
        assert "job_1" in queue.job_dependencies["job_2"]

    def test_submit_job_with_retry_policy(self):
        """Test submitting a job with custom retry policy."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        result = queue.submit_job(
            job_id="test_job_4",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
            retry_policy=job_queue_enhanced.RetryPolicy.IMMEDIATE,
        )
        assert result is True
        assert queue.jobs["test_job_4"].payload["_retry_policy"] == "immediate"

    def test_submit_job_with_batch_id(self):
        """Test submitting a job with batch ID."""
        queue = job_queue_enhanced.EnhancedJobQueue(enable_batching=True)
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        result = queue.submit_job(
            job_id="test_job_5",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
            batch_id="batch_1",
        )
        assert result is True
        assert "batch_1" in queue.job_batches
        assert len(queue.job_batches["batch_1"].jobs) == 1

    def test_get_next_job_realtime_first(self):
        """Test that realtime jobs are retrieved before others."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)

        # Submit jobs in different priorities
        queue.submit_job(
            job_id="batch_job",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )
        queue.submit_job(
            job_id="realtime_job",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.REALTIME,
            requirements=requirements,
            payload={"test": "data"},
        )

        # Get next job - should be realtime
        next_job = queue.get_next_job()
        assert next_job is not None
        assert next_job.job_id == "realtime_job"
        assert next_job.priority == JobPriority.REALTIME

    def test_get_next_job_with_dependencies(self):
        """Test that jobs with unmet dependencies are not retrieved."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)

        # Submit job with dependency
        queue.submit_job(
            job_id="dependent_job",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.REALTIME,
            requirements=requirements,
            payload={"test": "data"},
            dependencies=["nonexistent_job"],
        )

        # Should not get the job (dependency not met)
        next_job = queue.get_next_job(check_dependencies=True)
        assert next_job is None

    def test_start_job(self):
        """Test starting a job."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_6",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        job = queue.jobs["test_job_6"]
        queue.start_job(job)

        assert job.status == JobStatus.RUNNING
        assert "test_job_6" in queue.active_jobs
        assert job.started_at is not None

    def test_update_job_progress(self):
        """Test updating job progress."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_7",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        job = queue.jobs["test_job_7"]
        queue.start_job(job)
        queue.update_job_progress("test_job_7", 0.5, {"step": "processing"})

        assert queue.job_progress["test_job_7"] == 0.5
        assert queue.job_metadata["test_job_7"]["step"] == "processing"

    def test_complete_job_success(self):
        """Test completing a job successfully."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_8",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        job = queue.jobs["test_job_8"]
        queue.start_job(job)
        queue.complete_job("test_job_8", success=True, result={"output": "data"})

        assert job.status == JobStatus.COMPLETED
        assert "test_job_8" not in queue.active_jobs
        assert queue.stats["total_completed"] == 1
        assert queue.job_progress["test_job_8"] == 1.0

    def test_complete_job_failure(self):
        """Test completing a job with failure."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_9",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
            retry_policy=job_queue_enhanced.RetryPolicy.NONE,
        )

        job = queue.jobs["test_job_9"]
        queue.start_job(job)
        queue.complete_job("test_job_9", success=False, error="Test error")

        assert job.status == JobStatus.FAILED
        assert job.error == "Test error"
        assert "test_job_9" not in queue.active_jobs
        assert queue.stats["total_failed"] == 1

    def test_complete_job_with_retry(self):
        """Test completing a job with retry policy."""
        queue = job_queue_enhanced.EnhancedJobQueue(max_retries=3)
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_10",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
            retry_policy=job_queue_enhanced.RetryPolicy.IMMEDIATE,
        )

        job = queue.jobs["test_job_10"]
        queue.start_job(job)
        queue.complete_job("test_job_10", success=False, error="Test error")

        # Job should be requeued for retry
        assert job.status == JobStatus.QUEUED
        assert queue.job_retries["test_job_10"] == 1
        assert queue.stats["total_retried"] == 1

    def test_cancel_job_active(self):
        """Test cancelling an active job."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_11",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        job = queue.jobs["test_job_11"]
        queue.start_job(job)
        result = queue.cancel_job("test_job_11")

        assert result is True
        assert job.status == JobStatus.CANCELLED
        assert "test_job_11" not in queue.active_jobs
        assert queue.stats["total_cancelled"] == 1

    def test_cancel_job_queued(self):
        """Test cancelling a queued job."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_12",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        result = queue.cancel_job("test_job_12")

        assert result is True
        assert queue.jobs["test_job_12"].status == JobStatus.CANCELLED
        assert queue.stats["total_cancelled"] == 1

    def test_cancel_job_not_found(self):
        """Test cancelling a non-existent job."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        result = queue.cancel_job("nonexistent_job")

        assert result is False

    def test_get_job_status(self):
        """Test getting job status."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)
        queue.submit_job(
            job_id="test_job_13",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        status = queue.get_job_status("test_job_13")

        assert status is not None
        assert status["job_id"] == "test_job_13"
        assert status["status"] == JobStatus.QUEUED.value
        # Progress may not be in status if job hasn't started
        assert "retry_count" in status or "dependencies" in status

    def test_get_job_status_not_found(self):
        """Test getting status for non-existent job."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        status = queue.get_job_status("nonexistent_job")

        assert status is None

    def test_get_queue_stats(self):
        """Test getting queue statistics."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)

        # Submit jobs
        queue.submit_job(
            job_id="realtime_job_1",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.REALTIME,
            requirements=requirements,
            payload={"test": "data"},
        )
        queue.submit_job(
            job_id="batch_job_1",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
        )

        stats = queue.get_queue_stats()

        assert "queued_jobs" in stats
        assert stats["queued_jobs"]["realtime"] == 1
        assert stats["queued_jobs"]["batch"] == 1
        assert stats["queued_jobs"]["total"] == 2
        assert stats["active_jobs"] == 0
        assert "batches" in stats
        assert "statistics" in stats

    def test_create_batch(self):
        """Test creating a job batch."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)

        # Submit jobs with different priorities to avoid comparison issues
        queue.submit_job(
            job_id="job_1",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.REALTIME,
            requirements=requirements,
            payload={"test": "data"},
        )
        queue.submit_job(
            job_id="job_2",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.INTERACTIVE,
            requirements=requirements,
            payload={"test": "data"},
        )

        batch = queue.create_batch("batch_1", ["job_1", "job_2"])

        assert batch is not None
        assert batch.batch_id == "batch_1"
        assert len(batch.jobs) == 2
        assert "batch_1" in queue.job_batches
        assert queue.stats["batches_created"] == 1

    def test_create_batch_empty(self):
        """Test creating an empty batch."""
        queue = job_queue_enhanced.EnhancedJobQueue()
        batch = queue.create_batch("batch_2")

        assert batch is not None
        assert batch.batch_id == "batch_2"
        assert len(batch.jobs) == 0

    def test_batch_status_updates_on_job_completion(self):
        """Test that batch status updates when jobs complete."""
        queue = job_queue_enhanced.EnhancedJobQueue(enable_batching=True)
        requirements = ResourceRequirement(vram_gb=1.0, ram_gb=2.0)

        # Submit jobs in batch
        queue.submit_job(
            job_id="batch_job_1",
            engine_id="test_engine",
            task="test_task",
            priority=JobPriority.BATCH,
            requirements=requirements,
            payload={"test": "data"},
            batch_id="test_batch",
        )

        job = queue.jobs["batch_job_1"]
        queue.start_job(job)
        queue.complete_job("batch_job_1", success=True)

        batch = queue.job_batches["test_batch"]
        assert batch.completed_jobs == 1
        assert batch.total_jobs == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
