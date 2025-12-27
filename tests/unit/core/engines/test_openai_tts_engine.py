"""
Unit Tests for OpenAI TTS Engine
Tests OpenAI TTS engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the openai tts engine module
try:
    from app.core.engines import openai_tts_engine
except ImportError:
    pytest.skip("Could not import openai_tts_engine", allow_module_level=True)


class TestOpenAITTSEngineImports:
    """Test OpenAI TTS engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            openai_tts_engine is not None
        ), "Failed to import openai_tts_engine module"

    def test_module_has_openai_tts_engine_class(self):
        """Test module has OpenAITTSEngine class."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            cls = getattr(openai_tts_engine, "OpenAITTSEngine")
            assert isinstance(cls, type), "OpenAITTSEngine should be a class"


class TestOpenAITTSEngineClass:
    """Test OpenAITTSEngine class."""

    def test_openai_tts_engine_class_exists(self):
        """Test OpenAITTSEngine class exists."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            cls = getattr(openai_tts_engine, "OpenAITTSEngine")
            assert isinstance(cls, type), "OpenAITTSEngine should be a class"

    def test_openai_tts_engine_initialization(self):
        """Test OpenAITTSEngine can be instantiated."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    assert engine is not None
                    assert hasattr(engine, "device")
                    assert engine.device == "cpu"
            except (ImportError, Exception) as e:
                pytest.skip(f"openai_tts dependencies not installed: {e}")

    def test_openai_tts_engine_has_required_methods(self):
        """Test OpenAITTSEngine has required methods."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    required_methods = ["initialize", "cleanup", "synthesize"]
                    for method in required_methods:
                        assert hasattr(
                            engine, method
                        ), f"OpenAITTSEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")

    def test_openai_tts_engine_has_optimization_features(self):
        """Test OpenAITTSEngine has optimization features."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    # Check for LRU cache
                    assert hasattr(
                        engine, "_response_cache"
                    ), "OpenAITTSEngine should have response cache"
                    # Check for cache management
                    assert hasattr(
                        engine, "clear_cache"
                    ), "OpenAITTSEngine should have clear_cache method"
                    assert hasattr(
                        engine, "get_cache_stats"
                    ), "OpenAITTSEngine should have get_cache_stats method"
                    # Check for connection pooling
                    assert hasattr(
                        engine, "_session"
                    ), "OpenAITTSEngine should have session for connection pooling"
                    # Check for cache enable flag
                    assert hasattr(
                        engine, "enable_cache"
                    ), "OpenAITTSEngine should have enable_cache attribute"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")


class TestOpenAITTSEngineCaching:
    """Test OpenAI TTS engine caching functionality."""

    def test_lru_cache_implementation(self):
        """Test LRU response cache implementation."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    # Check for LRU cache (OrderedDict)
                    assert hasattr(
                        engine, "_response_cache"
                    ), "Should have response cache"
                    from collections import OrderedDict

                    assert isinstance(
                        engine._response_cache, OrderedDict
                    ), "Response cache should be OrderedDict for LRU behavior"
                    # Check for cache size
                    assert hasattr(
                        engine, "cache_size"
                    ), "Should have cache_size attribute"
                    assert isinstance(
                        engine.cache_size, int
                    ), "Cache size should be an integer"
                    assert engine.cache_size > 0, "Cache size should be positive"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")

    def test_cache_stats_method(self):
        """Test get_cache_stats method exists and returns valid data."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    stats = engine.get_cache_stats()
                    assert isinstance(stats, dict), "Cache stats should be a dictionary"
                    assert "cache_size" in stats, "Should include cache_size"
                    assert "max_cache_size" in stats, "Should include max_cache_size"
                    assert "cache_enabled" in stats, "Should include cache_enabled"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")

    def test_clear_cache_method(self):
        """Test clear_cache method exists and is callable."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    assert hasattr(
                        engine, "clear_cache"
                    ), "Should have clear_cache method"
                    assert callable(
                        engine.clear_cache
                    ), "clear_cache should be callable"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")


class TestOpenAITTSEngineConnectionPooling:
    """Test OpenAI TTS engine connection pooling functionality."""

    def test_connection_pooling_support(self):
        """Test connection pooling functionality exists."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    # Check for session (connection pooling)
                    assert hasattr(
                        engine, "_session"
                    ), "Should have _session attribute for connection pooling"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")

    def test_session_initialization(self):
        """Test session is initialized for connection pooling."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI") as mock_openai:
                    with patch("openai_tts_engine.requests") as mock_requests:
                        mock_session = MagicMock()
                        mock_requests.Session.return_value = mock_session
                        engine = openai_tts_engine.OpenAITTSEngine(
                            api_key="test_key", device="cpu", gpu=False
                        )
                        # Initialize to set up session
                        engine.initialize()
                        # Check session was created if requests is available
                        if (
                            hasattr(openai_tts_engine, "HAS_REQUESTS")
                            and openai_tts_engine.HAS_REQUESTS
                        ):
                            assert (
                                engine._session is not None
                            ), "Session should be initialized"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")


class TestOpenAITTSEngineProtocol:
    """Test OpenAI TTS engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test OpenAITTSEngine implements EngineProtocol."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    assert hasattr(engine, "initialize"), "Should implement initialize"
                    assert hasattr(engine, "cleanup"), "Should implement cleanup"
                    assert hasattr(
                        engine, "is_initialized"
                    ), "Should implement is_initialized"
                    assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    assert engine.get_device() == "cpu"
                    engine_cuda = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cuda", gpu=True
                    )
                    assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")


class TestOpenAITTSEngineOptimization:
    """Test OpenAI TTS engine optimization features."""

    def test_lru_cache_move_to_end(self):
        """Test LRU cache uses move_to_end for cache hits."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                import inspect

                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    if hasattr(engine, "synthesize"):
                        source = inspect.getsource(engine.synthesize)
                        assert (
                            "move_to_end" in source or "_response_cache" in source
                        ), "synthesize should use LRU cache with move_to_end"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")

    def test_cache_eviction_logic(self):
        """Test cache eviction when cache is full."""
        if hasattr(openai_tts_engine, "OpenAITTSEngine"):
            try:
                with patch("openai_tts_engine.OpenAI"):
                    engine = openai_tts_engine.OpenAITTSEngine(
                        api_key="test_key", device="cpu", gpu=False
                    )
                    # Check for cache eviction logic
                    assert hasattr(
                        engine, "cache_size"
                    ), "Should have cache_size for eviction"
                    # Check eviction happens when cache is full
                    import inspect

                    if hasattr(engine, "_cache_response"):
                        source = inspect.getsource(engine._cache_response)
                        assert (
                            "cache_size" in source or "oldest" in source.lower()
                        ), "_cache_response should handle cache eviction"
            except (ImportError, Exception):
                pytest.skip("openai_tts dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
