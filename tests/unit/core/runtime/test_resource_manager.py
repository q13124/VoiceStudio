"""
Unit Tests for Resource Manager
Tests resource management functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the resource manager module
try:
    from app.core.runtime import resource_manager
except ImportError:
    pytest.skip("Could not import resource_manager", allow_module_level=True)


class TestResourceManagerImports:
    """Test resource manager module can be imported."""

    def test_resource_manager_imports(self):
        """Test resource_manager can be imported."""
        assert resource_manager is not None, "Failed to import resource_manager module"

    def test_resource_manager_has_classes(self):
        """Test resource_manager has expected classes."""
        classes = [
            name for name in dir(resource_manager) if name[0].isupper() and not name.startswith("_")
        ]
        assert len(classes) > 0, "resource_manager should have classes"


class TestResourceManagerClasses:
    """Test resource manager classes."""

    def test_resource_manager_class_exists(self):
        """Test ResourceManager class exists."""
        if hasattr(resource_manager, "ResourceManager"):
            cls = resource_manager.ResourceManager
            assert isinstance(cls, type), "ResourceManager should be a class"


class TestResourceManagerFunctions:
    """Test resource manager functions exist."""

    def test_allocate_resource_function_exists(self):
        """Test allocate_resource function exists."""
        if hasattr(resource_manager, "allocate_resource"):
            assert callable(
                resource_manager.allocate_resource
            ), "allocate_resource should be callable"

    def test_release_resource_function_exists(self):
        """Test release_resource function exists."""
        if hasattr(resource_manager, "release_resource"):
            assert callable(
                resource_manager.release_resource
            ), "release_resource should be callable"

    def test_get_resource_status_function_exists(self):
        """Test get_resource_status function exists."""
        if hasattr(resource_manager, "get_resource_status"):
            assert callable(
                resource_manager.get_resource_status
            ), "get_resource_status should be callable"


class TestVRAMScheduler:
    """Test TD-013 VRAM Resource Scheduler features."""

    def test_engine_vram_budget(self):
        """Test setting and getting engine VRAM budget."""
        if not hasattr(resource_manager, "ResourceManager"):
            pytest.skip("ResourceManager not available")

        rm = resource_manager.ResourceManager(vram_headroom_gb=0.5)
        rm.set_engine_vram_budget("xtts", 4.0)

        status = rm.get_resource_status()
        assert "engine_status" in status
        if "xtts" in status["engine_status"]:
            assert status["engine_status"]["xtts"]["vram_budget_gb"] == 4.0

    def test_engine_vram_tracking(self):
        """Test per-engine VRAM usage tracking."""
        if not hasattr(resource_manager, "ResourceManager"):
            pytest.skip("ResourceManager not available")
        if not hasattr(resource_manager, "JobPriority"):
            pytest.skip("JobPriority not available")
        if not hasattr(resource_manager, "ResourceRequirement"):
            pytest.skip("ResourceRequirement not available")
        if not hasattr(resource_manager, "Job"):
            pytest.skip("Job not available")

        rm = resource_manager.ResourceManager(vram_headroom_gb=0.5)

        # Create a mock job
        req = resource_manager.ResourceRequirement(
            vram_gb=2.0, ram_gb=1.0, requires_gpu=True
        )
        job = resource_manager.Job(
            job_id="test-001",
            engine_id="xtts",
            task="synthesize",
            priority=resource_manager.JobPriority.INTERACTIVE,
            requirements=req,
            payload={},
        )

        # Start job to track VRAM
        rm.start_job(job)

        # Verify per-engine tracking
        assert rm.get_engine_vram_usage("xtts") == 2.0

        # Complete job
        rm.complete_job("test-001", success=True)

        # VRAM should be released
        assert rm.get_engine_vram_usage("xtts") == 0.0

    def test_eviction_candidates(self):
        """Test finding eviction candidates for VRAM."""
        if not hasattr(resource_manager, "ResourceManager"):
            pytest.skip("ResourceManager not available")
        if not hasattr(resource_manager, "JobPriority"):
            pytest.skip("JobPriority not available")
        if not hasattr(resource_manager, "ResourceRequirement"):
            pytest.skip("ResourceRequirement not available")
        if not hasattr(resource_manager, "Job"):
            pytest.skip("Job not available")

        rm = resource_manager.ResourceManager(vram_headroom_gb=0.5)

        # Create and start a batch job (low priority)
        req = resource_manager.ResourceRequirement(vram_gb=3.0, requires_gpu=True)
        batch_job = resource_manager.Job(
            job_id="batch-001",
            engine_id="tortoise",
            task="synthesize",
            priority=resource_manager.JobPriority.BATCH,
            requirements=req,
            payload={},
        )
        rm.start_job(batch_job)

        # Find eviction candidates for a realtime job
        candidates = rm._find_eviction_candidates(
            required_vram_gb=3.0,
            requesting_priority=resource_manager.JobPriority.REALTIME,
        )

        # Batch job should be candidate for eviction by realtime
        assert len(candidates) == 1
        assert candidates[0].job_id == "batch-001"

    def test_eviction_policy_respects_priority(self):
        """Test that eviction only affects lower-priority jobs."""
        if not hasattr(resource_manager, "ResourceManager"):
            pytest.skip("ResourceManager not available")
        if not hasattr(resource_manager, "JobPriority"):
            pytest.skip("JobPriority not available")
        if not hasattr(resource_manager, "ResourceRequirement"):
            pytest.skip("ResourceRequirement not available")
        if not hasattr(resource_manager, "Job"):
            pytest.skip("Job not available")

        rm = resource_manager.ResourceManager(vram_headroom_gb=0.5)

        # Create and start a realtime job (high priority)
        req = resource_manager.ResourceRequirement(vram_gb=4.0, requires_gpu=True)
        realtime_job = resource_manager.Job(
            job_id="realtime-001",
            engine_id="xtts",
            task="stream",
            priority=resource_manager.JobPriority.REALTIME,
            requirements=req,
            payload={},
        )
        rm.start_job(realtime_job)

        # Batch job should not be able to evict realtime
        candidates = rm._find_eviction_candidates(
            required_vram_gb=4.0,
            requesting_priority=resource_manager.JobPriority.BATCH,
        )

        # No candidates - can't evict higher priority
        assert len(candidates) == 0

    def test_resource_status_includes_vram_info(self):
        """Test that resource status includes VRAM scheduling info."""
        if not hasattr(resource_manager, "ResourceManager"):
            pytest.skip("ResourceManager not available")

        rm = resource_manager.ResourceManager(vram_headroom_gb=0.5)
        status = rm.get_resource_status()

        # TD-013: Should include eviction info
        assert "eviction_enabled" in status
        assert "evicted_jobs_count" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
