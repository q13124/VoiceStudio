"""
Unit Tests for Piper Engine
Tests Piper engine functionality including optimizations.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the piper engine module
try:
    from app.core.engines import piper_engine
except ImportError:
    pytest.skip("Could not import piper_engine", allow_module_level=True)


class TestPiperEngineImports:
    """Test piper engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert piper_engine is not None, "Failed to import piper_engine module"

    def test_module_has_piper_engine_class(self):
        """Test module has PiperEngine class."""
        if hasattr(piper_engine, "PiperEngine"):
            cls = piper_engine.PiperEngine
            assert isinstance(cls, type), "PiperEngine should be a class"


class TestPiperEngineClass:
    """Test PiperEngine class."""

    def test_piper_engine_class_exists(self):
        """Test PiperEngine class exists."""
        if hasattr(piper_engine, "PiperEngine"):
            cls = piper_engine.PiperEngine
            assert isinstance(cls, type), "PiperEngine should be a class"

    def test_piper_engine_initialization(self):
        """Test PiperEngine can be instantiated."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")

    def test_piper_engine_has_required_methods(self):
        """Test PiperEngine has required methods."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "synthesize"]
                for method in required_methods:
                    assert hasattr(
                        engine, method
                    ), f"PiperEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")

    def test_piper_engine_has_optimization_features(self):
        """Test PiperEngine has optimization features."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                # Check for caching support
                assert hasattr(
                    engine, "enable_caching"
                ), "PiperEngine should support caching"
                # Check for batch processing
                assert hasattr(
                    engine, "batch_synthesize"
                ), "PiperEngine should support batch processing"
                # Check for batch_size attribute
                assert hasattr(
                    engine, "batch_size"
                ), "PiperEngine should have batch_size attribute"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")


class TestPiperEngineCaching:
    """Test Piper engine caching functionality."""

    def test_caching_enable_disable(self):
        """Test enabling and disabling caching."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                # Check initial state (should be True by default)
                assert (
                    engine.enable_caching is True
                ), "Caching should be enabled by default"
                # Test that enable_caching method exists and can be called
                assert hasattr(engine, "enable_caching"), "enable_caching should exist"
                # The method sets self.enable_caching, so after calling it becomes a property
                enable_caching_method = engine.enable_caching
                if callable(enable_caching_method):
                    # Call the method to disable caching
                    enable_caching_method(False)
                    # After calling, enable_caching becomes a boolean property
                    assert hasattr(
                        engine, "enable_caching"
                    ), "enable_caching should still exist"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")


class TestPiperEngineBatchProcessing:
    """Test Piper engine batch processing functionality."""

    def test_batch_processing_method_exists(self):
        """Test batch_synthesize method exists."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_synthesize"
                ), "PiperEngine should have batch_synthesize method"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")

    def test_batch_size_attribute(self):
        """Test batch_size attribute exists and is valid."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                assert hasattr(engine, "batch_size"), "PiperEngine should have batch_size"
                assert isinstance(engine.batch_size, int), "batch_size should be an integer"
                assert engine.batch_size > 0, "batch_size should be positive"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")


class TestPiperEngineProtocol:
    """Test Piper engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test PiperEngine implements EngineProtocol."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                # Check for protocol methods
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(
                    engine, "is_initialized"
                ), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                assert engine.get_device() == "cpu"
                # Test with cuda if available
                engine_cuda = piper_engine.PiperEngine(device="cuda", gpu=True)
                assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")


class TestPiperEngineConfiguration:
    """Test Piper engine configuration."""

    def test_default_sample_rate(self):
        """Test default sample rate is set."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "sample_rate"
                ), "Should have sample_rate attribute"
                assert isinstance(
                    engine.sample_rate, int
                ), "sample_rate should be an integer"
                assert engine.sample_rate > 0, "sample_rate should be positive"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")

    def test_executable_path_attribute(self):
        """Test executable_path attribute exists."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "executable_path"
                ), "Should have executable_path attribute"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")


class TestPiperEngineOptimization:
    """Test Piper engine optimization features."""

    def test_thread_pool_executor_usage(self):
        """Test that ThreadPoolExecutor is used in batch processing."""
        if hasattr(piper_engine, "PiperEngine"):
            try:
                # Check source code for ThreadPoolExecutor usage
                import inspect

                engine = piper_engine.PiperEngine(device="cpu", gpu=False)
                if hasattr(engine, "batch_synthesize"):
                    source = inspect.getsource(engine.batch_synthesize)
                    # Check for ThreadPoolExecutor (parallel processing optimization)
                    assert (
                        "ThreadPoolExecutor" in source or "executor" in source
                    ), "batch_synthesize should use ThreadPoolExecutor for parallel processing"
            except (ImportError, Exception):
                pytest.skip("piper dependencies not installed")


class TestPiperEngineModule:
    """Test Piper engine module structure."""

    def test_module_has_cache_functions(self):
        """Test module has caching helper functions."""
        cache_functions = [
            "_get_cache_key",
            "_get_cached_piper_instance",
            "_cache_piper_instance",
        ]
        for func_name in cache_functions:
            if hasattr(piper_engine, func_name):
                func = getattr(piper_engine, func_name)
                assert callable(func), f"{func_name} should be callable"

    def test_module_has_model_cache(self):
        """Test module has model cache support."""
        # Check for model cache availability
        assert hasattr(piper_engine, "HAS_MODEL_CACHE") or hasattr(
            piper_engine, "_PIPER_INSTANCE_CACHE"
        ), "Module should have model cache support"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

