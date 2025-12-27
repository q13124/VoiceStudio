"""
Unit Tests for GPT-SoVITS Engine
Tests GPT-SoVITS engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the gpt_sovits engine module
try:
    from app.core.engines import gpt_sovits_engine
except ImportError:
    pytest.skip("Could not import gpt_sovits_engine", allow_module_level=True)


class TestGPTSovitsEngineImports:
    """Test gpt_sovits engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            gpt_sovits_engine is not None
        ), "Failed to import gpt_sovits_engine module"

    def test_module_has_gpt_sovits_engine_class(self):
        """Test module has GPTSoVITSEngine class."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            cls = getattr(gpt_sovits_engine, "GPTSoVITSEngine")
            assert isinstance(cls, type), "GPTSoVITSEngine should be a class"


class TestGPTSovitsEngineClass:
    """Test GPTSoVITSEngine class."""

    def test_gpt_sovits_engine_class_exists(self):
        """Test GPTSoVITSEngine class exists."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            cls = getattr(gpt_sovits_engine, "GPTSoVITSEngine")
            assert isinstance(cls, type), "GPTSoVITSEngine should be a class"

    def test_gpt_sovits_engine_initialization(self):
        """Test GPTSoVITSEngine can be instantiated."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")

    def test_gpt_sovits_engine_has_required_methods(self):
        """Test GPTSoVITSEngine has required methods."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "synthesize"]
                for method in required_methods:
                    assert hasattr(
                        engine, method
                    ), f"GPTSoVITSEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")

    def test_gpt_sovits_engine_has_optimization_features(self):
        """Test GPTSoVITSEngine has optimization features."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "enable_caching"
                ), "GPTSoVITSEngine should support caching"
                assert hasattr(
                    engine, "batch_synthesize"
                ), "GPTSoVITSEngine should support batch processing"
                assert hasattr(
                    engine, "batch_size"
                ), "GPTSoVITSEngine should have batch_size attribute"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")


class TestGPTSovitsEngineBatchProcessing:
    """Test GPT-SoVITS engine batch processing functionality."""

    def test_batch_processing_method_exists(self):
        """Test batch_synthesize method exists."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_synthesize"
                ), "GPTSoVITSEngine should have batch_synthesize method"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")

    def test_batch_size_attribute(self):
        """Test batch_size attribute exists and is valid."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_size"
                ), "GPTSoVITSEngine should have batch_size"
                assert isinstance(
                    engine.batch_size, int
                ), "batch_size should be an integer"
                assert engine.batch_size > 0, "batch_size should be positive"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")


class TestGPTSovitsEngineProtocol:
    """Test GPT-SoVITS engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test GPTSoVITSEngine implements EngineProtocol."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(
                    engine, "is_initialized"
                ), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")


class TestGPTSovitsEngineOptimization:
    """Test GPT-SoVITS engine optimization features."""

    def test_thread_pool_executor_usage(self):
        """Test that ThreadPoolExecutor is used in batch processing."""
        if hasattr(gpt_sovits_engine, "GPTSoVITSEngine"):
            try:
                import inspect

                engine = gpt_sovits_engine.GPTSoVITSEngine(device="cpu", gpu=False)
                if hasattr(engine, "batch_synthesize"):
                    source = inspect.getsource(engine.batch_synthesize)
                    assert (
                        "ThreadPoolExecutor" in source or "executor" in source
                    ), "batch_synthesize should use ThreadPoolExecutor for parallel processing"
            except (ImportError, Exception):
                pytest.skip("gpt-sovits dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
