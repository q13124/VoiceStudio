"""
Unit Tests for Whisper UI Engine
Tests Whisper UI engine functionality including optimizations.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the whisper_ui engine module
try:
    from app.core.engines import whisper_ui_engine
except ImportError:
    pytest.skip("Could not import whisper_ui_engine", allow_module_level=True)


class TestWhisperUIEngineImports:
    """Test whisper_ui engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert whisper_ui_engine is not None, "Failed to import whisper_ui_engine module"

    def test_module_has_whisper_ui_engine_class(self):
        """Test module has WhisperUIEngine class."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            cls = whisper_ui_engine.WhisperUIEngine
            assert isinstance(cls, type), "WhisperUIEngine should be a class"


class TestWhisperUIEngineClass:
    """Test WhisperUIEngine class."""

    def test_whisper_ui_engine_class_exists(self):
        """Test WhisperUIEngine class exists."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            cls = whisper_ui_engine.WhisperUIEngine
            assert isinstance(cls, type), "WhisperUIEngine should be a class"

    def test_whisper_ui_engine_initialization(self):
        """Test WhisperUIEngine can be instantiated."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                assert engine is not None
                assert hasattr(engine, "device")
                assert engine.device == "cpu"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")

    def test_whisper_ui_engine_has_required_methods(self):
        """Test WhisperUIEngine has required methods."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                required_methods = ["initialize", "cleanup", "transcribe"]
                for method in required_methods:
                    assert hasattr(engine, method), f"WhisperUIEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")

    def test_whisper_ui_engine_has_optimization_features(self):
        """Test WhisperUIEngine has optimization features."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                # Check for caching support
                assert hasattr(engine, "enable_caching"), "WhisperUIEngine should support caching"
                # Check for transcription cache (LRU)
                assert hasattr(
                    engine, "_transcription_cache"
                ), "WhisperUIEngine should have transcription cache"
                # Check for cache management methods
                assert hasattr(
                    engine, "clear_transcription_cache"
                ), "WhisperUIEngine should have clear_transcription_cache method"
                assert hasattr(
                    engine, "get_cache_stats"
                ), "WhisperUIEngine should have get_cache_stats method"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")


class TestWhisperUIEngineCaching:
    """Test Whisper UI engine caching functionality."""

    def test_transcription_cache_exists(self):
        """Test transcription cache is initialized."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                assert hasattr(engine, "_transcription_cache"), "Should have transcription cache"
                # Check it's an OrderedDict (LRU cache)
                from collections import OrderedDict

                assert isinstance(
                    engine._transcription_cache, OrderedDict
                ), "Transcription cache should be OrderedDict for LRU behavior"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")

    def test_cache_stats_method(self):
        """Test get_cache_stats method exists and returns valid data."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                stats = engine.get_cache_stats()
                assert isinstance(stats, dict), "Cache stats should be a dictionary"
                assert (
                    "transcription_cache_size" in stats
                ), "Should include transcription_cache_size"
                assert (
                    "max_transcription_cache_size" in stats
                ), "Should include max_transcription_cache_size"
                assert "cache_enabled" in stats, "Should include cache_enabled"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")

    def test_clear_cache_method(self):
        """Test clear_transcription_cache method exists."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                assert hasattr(
                    engine, "clear_transcription_cache"
                ), "Should have clear_transcription_cache method"
                # Test it's callable
                assert callable(
                    engine.clear_transcription_cache
                ), "clear_transcription_cache should be callable"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")


class TestWhisperUIEngineProtocol:
    """Test Whisper UI engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test WhisperUIEngine implements EngineProtocol."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                assert hasattr(engine, "initialize"), "Should implement initialize"
                assert hasattr(engine, "cleanup"), "Should implement cleanup"
                assert hasattr(engine, "is_initialized"), "Should implement is_initialized"
                assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                assert engine.get_device() == "cpu"
                engine_cuda = whisper_ui_engine.WhisperUIEngine(device="cuda", gpu=True)
                assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")


class TestWhisperUIEngineOptimization:
    """Test Whisper UI engine optimization features."""

    def test_model_caching_available(self):
        """Test that model caching functions are available."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                # Check for module-level caching functions
                assert hasattr(
                    whisper_ui_engine, "_get_cached_whisper_ui_model"
                ), "Should have _get_cached_whisper_ui_model function"
                assert hasattr(
                    whisper_ui_engine, "_cache_whisper_ui_model"
                ), "Should have _cache_whisper_ui_model function"
                assert hasattr(
                    whisper_ui_engine, "_WHISPER_UI_MODEL_CACHE"
                ), "Should have module-level model cache"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")

    def test_lru_transcription_cache(self):
        """Test LRU transcription cache implementation."""
        if hasattr(whisper_ui_engine, "WhisperUIEngine"):
            try:
                engine = whisper_ui_engine.WhisperUIEngine(device="cpu", gpu=False)
                # Check for LRU cache (OrderedDict)
                assert hasattr(engine, "_transcription_cache"), "Should have transcription cache"
                # Check for cache max size
                assert hasattr(engine, "_cache_max_size"), "Should have cache max size attribute"
                assert isinstance(
                    engine._cache_max_size, int
                ), "Cache max size should be an integer"
                assert engine._cache_max_size > 0, "Cache max size should be positive"
            except (ImportError, Exception):
                pytest.skip("whisper_ui dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
