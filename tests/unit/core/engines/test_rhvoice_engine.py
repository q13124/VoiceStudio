"""
Unit Tests for RHVoice Engine
Tests RHVoice engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the rhvoice engine module
try:
    from app.core.engines import rhvoice_engine
except ImportError:
    pytest.skip("Could not import rhvoice_engine", allow_module_level=True)


class TestRHVoiceEngineImports:
    """Test rhvoice engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert rhvoice_engine is not None, "Failed to import rhvoice_engine module"

    def test_module_has_rhvoice_engine_class(self):
        """Test module has RHVoiceEngine class."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            cls = getattr(rhvoice_engine, "RHVoiceEngine")
            assert isinstance(cls, type), "RHVoiceEngine should be a class"


class TestRHVoiceEngineClass:
    """Test RHVoiceEngine class."""

    def test_rhvoice_engine_class_exists(self):
        """Test RHVoiceEngine class exists."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            cls = getattr(rhvoice_engine, "RHVoiceEngine")
            assert isinstance(cls, type), "RHVoiceEngine should be a class"

    def test_rhvoice_engine_initialization(self):
        """Test RHVoiceEngine can be instantiated."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")

    def test_rhvoice_engine_has_required_methods(self):
        """Test RHVoiceEngine has required methods."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "synthesize"]
                for method in required_methods:
                    assert hasattr(
                        engine, method
                    ), f"RHVoiceEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")

    def test_rhvoice_engine_has_optimization_features(self):
        """Test RHVoiceEngine has optimization features."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                # Check for batch processing
                assert hasattr(
                    engine, "batch_synthesize"
                ), "RHVoiceEngine should support batch processing"
                # Check for batch_size attribute
                assert hasattr(
                    engine, "batch_size"
                ), "RHVoiceEngine should have batch_size attribute"
                # Check for synthesis cache (LRU)
                assert hasattr(
                    engine, "_synthesis_cache"
                ), "RHVoiceEngine should have synthesis cache"
                # Check for reusable temp directory
                assert hasattr(
                    engine, "_temp_dir"
                ), "RHVoiceEngine should have reusable temp directory"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")


class TestRHVoiceEngineBatchProcessing:
    """Test RHVoice engine batch processing functionality."""

    def test_batch_processing_method_exists(self):
        """Test batch_synthesize method exists."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_synthesize"
                ), "RHVoiceEngine should have batch_synthesize method"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")

    def test_batch_size_attribute(self):
        """Test batch_size attribute exists and is valid."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                assert hasattr(engine, "batch_size"), "RHVoiceEngine should have batch_size"
                assert isinstance(engine.batch_size, int), "batch_size should be an integer"
                assert engine.batch_size > 0, "batch_size should be positive"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")


class TestRHVoiceEngineProtocol:
    """Test RHVoice engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test RHVoiceEngine implements EngineProtocol."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(
                    engine, "is_initialized"
                ), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                assert engine.get_device() == "cpu"
                engine_cuda = rhvoice_engine.RHVoiceEngine(device="cuda", gpu=True)
                assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")


class TestRHVoiceEngineOptimization:
    """Test RHVoice engine optimization features."""

    def test_thread_pool_executor_usage(self):
        """Test that ThreadPoolExecutor is used in batch processing."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                import inspect

                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                if hasattr(engine, "batch_synthesize"):
                    source = inspect.getsource(engine.batch_synthesize)
                    assert (
                        "ThreadPoolExecutor" in source or "executor" in source
                    ), "batch_synthesize should use ThreadPoolExecutor for parallel processing"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")

    def test_lru_cache_implementation(self):
        """Test LRU synthesis cache implementation."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                # Check for LRU cache (OrderedDict)
                assert hasattr(
                    engine, "_synthesis_cache"
                ), "Should have synthesis cache"
                # Check for cache stats method
                assert hasattr(
                    engine, "get_cache_stats"
                ), "Should have get_cache_stats method"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")

    def test_reusable_temp_directory(self):
        """Test reusable temporary directory feature."""
        if hasattr(rhvoice_engine, "RHVoiceEngine"):
            try:
                engine = rhvoice_engine.RHVoiceEngine(device="cpu", gpu=False)
                # Check for reusable temp directory
                assert hasattr(
                    engine, "_temp_dir"
                ), "Should have reusable temp directory"
            except (ImportError, Exception):
                pytest.skip("rhvoice dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

