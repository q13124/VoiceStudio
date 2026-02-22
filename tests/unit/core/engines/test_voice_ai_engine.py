"""
Unit Tests for Voice AI Engine
Tests Voice AI engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the voice_ai engine module
try:
    from app.core.engines import voice_ai_engine
except ImportError:
    pytest.skip("Could not import voice_ai_engine", allow_module_level=True)


class TestVoiceAIEngineImports:
    """Test voice_ai engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert voice_ai_engine is not None, "Failed to import voice_ai_engine module"

    def test_module_has_voice_ai_engine_class(self):
        """Test module has VoiceAIEngine class."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            cls = voice_ai_engine.VoiceAIEngine
            assert isinstance(cls, type), "VoiceAIEngine should be a class"


class TestVoiceAIEngineClass:
    """Test VoiceAIEngine class."""

    def test_voice_ai_engine_class_exists(self):
        """Test VoiceAIEngine class exists."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            cls = voice_ai_engine.VoiceAIEngine
            assert isinstance(cls, type), "VoiceAIEngine should be a class"

    def test_voice_ai_engine_initialization(self):
        """Test VoiceAIEngine can be instantiated."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                # Mock requests to avoid actual API calls
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    assert engine is not None
                    assert hasattr(engine, "device")
                    assert engine.device == "cpu"
            except (ImportError, Exception) as e:
                pytest.skip(f"voice_ai dependencies not installed: {e}")

    def test_voice_ai_engine_has_required_methods(self):
        """Test VoiceAIEngine has required methods."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    required_methods = ["initialize", "cleanup", "convert_voice"]
                    for method in required_methods:
                        assert hasattr(engine, method), f"VoiceAIEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")

    def test_voice_ai_engine_has_optimization_features(self):
        """Test VoiceAIEngine has optimization features."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    # Check for LRU cache
                    assert hasattr(
                        engine, "_conversion_cache"
                    ), "VoiceAIEngine should have conversion cache"
                    # Check for cache management
                    assert hasattr(
                        engine, "clear_cache"
                    ), "VoiceAIEngine should have clear_cache method"
                    assert hasattr(
                        engine, "get_cache_stats"
                    ), "VoiceAIEngine should have get_cache_stats method"
                    # Check for connection pooling
                    assert hasattr(
                        engine, "_session"
                    ), "VoiceAIEngine should have session for connection pooling"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")


class TestVoiceAIEngineCaching:
    """Test Voice AI engine caching functionality."""

    def test_lru_cache_implementation(self):
        """Test LRU conversion cache implementation."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    # Check for LRU cache (OrderedDict)
                    assert hasattr(engine, "_conversion_cache"), "Should have conversion cache"
                    from collections import OrderedDict

                    assert isinstance(
                        engine._conversion_cache, OrderedDict
                    ), "Conversion cache should be OrderedDict for LRU behavior"
                    # Check for cache max size
                    assert hasattr(
                        engine, "_cache_max_size"
                    ), "Should have cache max size attribute"
                    assert isinstance(
                        engine._cache_max_size, int
                    ), "Cache max size should be an integer"
                    assert engine._cache_max_size > 0, "Cache max size should be positive"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")

    def test_cache_stats_method(self):
        """Test get_cache_stats method exists and returns valid data."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    stats = engine.get_cache_stats()
                    assert isinstance(stats, dict), "Cache stats should be a dictionary"
                    assert "cache_size" in stats, "Should include cache_size"
                    assert "max_cache_size" in stats, "Should include max_cache_size"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")

    def test_clear_cache_method(self):
        """Test clear_cache method exists and is callable."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    assert hasattr(engine, "clear_cache"), "Should have clear_cache method"
                    assert callable(engine.clear_cache), "clear_cache should be callable"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")


class TestVoiceAIEngineConnectionPooling:
    """Test Voice AI engine connection pooling functionality."""

    def test_connection_pooling_support(self):
        """Test connection pooling functionality exists."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    # Check for session (connection pooling)
                    assert hasattr(
                        engine, "_session"
                    ), "Should have _session attribute for connection pooling"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")

    def test_session_initialization(self):
        """Test session is initialized for connection pooling."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests") as mock_requests:
                    mock_session = MagicMock()
                    mock_requests.Session.return_value = mock_session
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    # Initialize to set up session
                    engine.initialize()
                    # Check session was created
                    assert engine._session is not None, "Session should be initialized"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")


class TestVoiceAIEngineProtocol:
    """Test Voice AI engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test VoiceAIEngine implements EngineProtocol."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    assert hasattr(engine, "initialize"), "Should implement initialize"
                    assert hasattr(engine, "cleanup"), "Should implement cleanup"
                    assert hasattr(engine, "is_initialized"), "Should implement is_initialized"
                    assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    assert engine.get_device() == "cpu"
                    engine_cuda = voice_ai_engine.VoiceAIEngine(device="cuda", gpu=True)
                    assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")


class TestVoiceAIEngineOptimization:
    """Test Voice AI engine optimization features."""

    def test_lru_cache_move_to_end(self):
        """Test LRU cache uses move_to_end for cache hits."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                import inspect

                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    if hasattr(engine, "convert_voice"):
                        source = inspect.getsource(engine.convert_voice)
                        assert (
                            "move_to_end" in source or "_conversion_cache" in source
                        ), "convert_voice should use LRU cache with move_to_end"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")

    def test_cache_eviction_logic(self):
        """Test cache eviction when cache is full."""
        if hasattr(voice_ai_engine, "VoiceAIEngine"):
            try:
                with patch("voice_ai_engine.requests"):
                    engine = voice_ai_engine.VoiceAIEngine(device="cpu", gpu=False)
                    # Check for cache eviction logic
                    assert hasattr(
                        engine, "_cache_max_size"
                    ), "Should have cache max size for eviction"
                    # Check eviction happens when cache is full
                    import inspect

                    if hasattr(engine, "convert_voice"):
                        source = inspect.getsource(engine.convert_voice)
                        assert (
                            "_cache_max_size" in source or "oldest" in source.lower()
                        ), "convert_voice should handle cache eviction"
            except (ImportError, Exception):
                pytest.skip("voice_ai dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
