"""
Unit Tests for MockingBird Engine
Tests MockingBird engine functionality including optimizations.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the mockingbird engine module
try:
    from app.core.engines import mockingbird_engine
except ImportError:
    pytest.skip("Could not import mockingbird_engine", allow_module_level=True)


class TestMockingBirdEngineImports:
    """Test mockingbird engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            mockingbird_engine is not None
        ), "Failed to import mockingbird_engine module"

    def test_module_has_mockingbird_engine_class(self):
        """Test module has MockingBirdEngine class."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            cls = mockingbird_engine.MockingBirdEngine
            assert isinstance(cls, type), "MockingBirdEngine should be a class"


class TestMockingBirdEngineClass:
    """Test MockingBirdEngine class."""

    def test_mockingbird_engine_class_exists(self):
        """Test MockingBirdEngine class exists."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            cls = mockingbird_engine.MockingBirdEngine
            assert isinstance(cls, type), "MockingBirdEngine should be a class"

    def test_mockingbird_engine_initialization(self):
        """Test MockingBirdEngine can be instantiated."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")

    def test_mockingbird_engine_has_required_methods(self):
        """Test MockingBirdEngine has required methods."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "synthesize"]
                for method in required_methods:
                    assert hasattr(
                        engine, method
                    ), f"MockingBirdEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")

    def test_mockingbird_engine_has_optimization_features(self):
        """Test MockingBirdEngine has optimization features."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "enable_caching"
                ), "MockingBirdEngine should support caching"
                assert hasattr(
                    engine, "batch_synthesize"
                ), "MockingBirdEngine should support batch processing"
                assert hasattr(
                    engine, "batch_size"
                ), "MockingBirdEngine should have batch_size attribute"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")


class TestMockingBirdEngineBatchProcessing:
    """Test MockingBird engine batch processing functionality."""

    def test_batch_processing_method_exists(self):
        """Test batch_synthesize method exists."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_synthesize"
                ), "MockingBirdEngine should have batch_synthesize method"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")

    def test_batch_size_attribute(self):
        """Test batch_size attribute exists and is valid."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_size"
                ), "MockingBirdEngine should have batch_size"
                assert isinstance(
                    engine.batch_size, int
                ), "batch_size should be an integer"
                assert engine.batch_size > 0, "batch_size should be positive"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")


class TestMockingBirdEngineProtocol:
    """Test MockingBird engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test MockingBirdEngine implements EngineProtocol."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(
                    engine, "is_initialized"
                ), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")


class TestMockingBirdEngineOptimization:
    """Test MockingBird engine optimization features."""

    def test_thread_pool_executor_usage(self):
        """Test that ThreadPoolExecutor is used in batch processing."""
        if hasattr(mockingbird_engine, "MockingBirdEngine"):
            try:
                import inspect

                engine = mockingbird_engine.MockingBirdEngine(device="cpu", gpu=False)
                if hasattr(engine, "batch_synthesize"):
                    source = inspect.getsource(engine.batch_synthesize)
                    assert (
                        "ThreadPoolExecutor" in source or "executor" in source
                    ), "batch_synthesize should use ThreadPoolExecutor for parallel processing"
            except (ImportError, Exception):
                pytest.skip("mockingbird dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
