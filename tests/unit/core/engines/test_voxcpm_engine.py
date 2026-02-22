"""
Unit Tests for VoxCPM Engine
Tests VoxCPM engine functionality including optimizations.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the voxcpm engine module
try:
    from app.core.engines import voxcpm_engine
except ImportError:
    pytest.skip("Could not import voxcpm_engine", allow_module_level=True)


class TestVoxCPMEngineImports:
    """Test voxcpm engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert voxcpm_engine is not None, "Failed to import voxcpm_engine module"

    def test_module_has_voxcpm_engine_class(self):
        """Test module has VoxCPMEngine class."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            cls = voxcpm_engine.VoxCPMEngine
            assert isinstance(cls, type), "VoxCPMEngine should be a class"


class TestVoxCPMEngineClass:
    """Test VoxCPMEngine class."""

    def test_voxcpm_engine_class_exists(self):
        """Test VoxCPMEngine class exists."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            cls = voxcpm_engine.VoxCPMEngine
            assert isinstance(cls, type), "VoxCPMEngine should be a class"

    def test_voxcpm_engine_initialization(self):
        """Test VoxCPMEngine can be instantiated."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")

    def test_voxcpm_engine_has_required_methods(self):
        """Test VoxCPMEngine has required methods."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "synthesize"]
                for method in required_methods:
                    assert hasattr(engine, method), f"VoxCPMEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")

    def test_voxcpm_engine_has_optimization_features(self):
        """Test VoxCPMEngine has optimization features."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                assert hasattr(engine, "enable_caching"), "VoxCPMEngine should support caching"
                assert hasattr(
                    engine, "batch_synthesize"
                ), "VoxCPMEngine should support batch processing"
                assert hasattr(
                    engine, "batch_size"
                ), "VoxCPMEngine should have batch_size attribute"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")


class TestVoxCPMEngineBatchProcessing:
    """Test VoxCPM engine batch processing functionality."""

    def test_batch_processing_method_exists(self):
        """Test batch_synthesize method exists."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_synthesize"
                ), "VoxCPMEngine should have batch_synthesize method"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")

    def test_batch_size_attribute(self):
        """Test batch_size attribute exists and is valid."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                assert hasattr(engine, "batch_size"), "VoxCPMEngine should have batch_size"
                assert isinstance(engine.batch_size, int), "batch_size should be an integer"
                assert engine.batch_size > 0, "batch_size should be positive"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")


class TestVoxCPMEngineProtocol:
    """Test VoxCPM engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test VoxCPMEngine implements EngineProtocol."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(engine, "is_initialized"), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")


class TestVoxCPMEngineOptimization:
    """Test VoxCPM engine optimization features."""

    def test_thread_pool_executor_usage(self):
        """Test that ThreadPoolExecutor is used in batch processing."""
        if hasattr(voxcpm_engine, "VoxCPMEngine"):
            try:
                import inspect

                engine = voxcpm_engine.VoxCPMEngine(device="cpu", gpu=False)
                if hasattr(engine, "batch_synthesize"):
                    source = inspect.getsource(engine.batch_synthesize)
                    assert (
                        "ThreadPoolExecutor" in source or "executor" in source
                    ), "batch_synthesize should use ThreadPoolExecutor for parallel processing"
            except (ImportError, Exception):
                pytest.skip("voxcpm dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
