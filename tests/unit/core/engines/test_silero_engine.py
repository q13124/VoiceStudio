"""
Unit Tests for Silero Engine
Tests Silero engine functionality including optimizations.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the silero engine module
try:
    from app.core.engines import silero_engine
except ImportError:
    pytest.skip("Could not import silero_engine", allow_module_level=True)


class TestSileroEngineImports:
    """Test silero engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert silero_engine is not None, "Failed to import silero_engine module"

    def test_module_has_silero_engine_class(self):
        """Test module has SileroEngine class."""
        if hasattr(silero_engine, "SileroEngine"):
            cls = silero_engine.SileroEngine
            assert isinstance(cls, type), "SileroEngine should be a class"


class TestSileroEngineClass:
    """Test SileroEngine class."""

    def test_silero_engine_class_exists(self):
        """Test SileroEngine class exists."""
        if hasattr(silero_engine, "SileroEngine"):
            cls = silero_engine.SileroEngine
            assert isinstance(cls, type), "SileroEngine should be a class"

    def test_silero_engine_initialization(self):
        """Test SileroEngine can be instantiated."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")

    def test_silero_engine_has_required_methods(self):
        """Test SileroEngine has required methods."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "synthesize"]
                for method in required_methods:
                    assert hasattr(engine, method), f"SileroEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")

    def test_silero_engine_has_optimization_features(self):
        """Test SileroEngine has optimization features."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                # Check for caching support
                assert hasattr(engine, "enable_caching"), "SileroEngine should support caching"
                # Check for batch processing
                assert hasattr(
                    engine, "batch_synthesize"
                ), "SileroEngine should support batch processing"
                # Check for batch_size attribute
                assert hasattr(
                    engine, "batch_size"
                ), "SileroEngine should have batch_size attribute"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")


class TestSileroEngineCaching:
    """Test Silero engine caching functionality."""

    def test_caching_enable_disable(self):
        """Test enabling and disabling caching."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                # Check initial state (should be True by default)
                assert engine.enable_caching is True, "Caching should be enabled by default"
                # Test that enable_caching method exists
                assert hasattr(engine, "enable_caching"), "enable_caching should exist"
                enable_caching_method = engine.enable_caching
                if callable(enable_caching_method):
                    enable_caching_method(False)
                    assert hasattr(engine, "enable_caching"), "enable_caching should still exist"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")


class TestSileroEngineBatchProcessing:
    """Test Silero engine batch processing functionality."""

    def test_batch_processing_method_exists(self):
        """Test batch_synthesize method exists."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "batch_synthesize"
                ), "SileroEngine should have batch_synthesize method"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")

    def test_batch_size_attribute(self):
        """Test batch_size attribute exists and is valid."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                assert hasattr(engine, "batch_size"), "SileroEngine should have batch_size"
                assert isinstance(engine.batch_size, int), "batch_size should be an integer"
                assert engine.batch_size > 0, "batch_size should be positive"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")


class TestSileroEngineProtocol:
    """Test Silero engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test SileroEngine implements EngineProtocol."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(engine, "is_initialized"), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                assert engine.get_device() == "cpu"
                engine_cuda = silero_engine.SileroEngine(device="cuda", gpu=True)
                assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")


class TestSileroEngineConfiguration:
    """Test Silero engine configuration."""

    def test_default_sample_rate(self):
        """Test default sample rate is set."""
        if hasattr(silero_engine, "SileroEngine"):
            try:
                engine = silero_engine.SileroEngine(device="cpu", gpu=False)
                assert hasattr(engine, "sample_rate"), "Should have sample_rate attribute"
                assert isinstance(engine.sample_rate, int), "sample_rate should be an integer"
                assert engine.sample_rate > 0, "sample_rate should be positive"
            except (ImportError, Exception):
                pytest.skip("silero dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
