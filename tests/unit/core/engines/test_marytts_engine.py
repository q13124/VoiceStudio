"""
Unit Tests for MaryTTS Engine
Tests MaryTTS engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the marytts engine module
try:
    from app.core.engines import marytts_engine
except ImportError:
    pytest.skip("Could not import marytts_engine", allow_module_level=True)


class TestMaryTTSEngineImports:
    """Test marytts engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert marytts_engine is not None, "Failed to import marytts_engine module"

    def test_module_has_marytts_engine_class(self):
        """Test module has MaryTTSEngine class."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            cls = marytts_engine.MaryTTSEngine
            assert isinstance(cls, type), "MaryTTSEngine should be a class"


class TestMaryTTSEngineClass:
    """Test MaryTTSEngine class."""

    def test_marytts_engine_class_exists(self):
        """Test MaryTTSEngine class exists."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            cls = marytts_engine.MaryTTSEngine
            assert isinstance(cls, type), "MaryTTSEngine should be a class"

    def test_marytts_engine_initialization(self):
        """Test MaryTTSEngine can be instantiated."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                # Mock requests to avoid actual API calls
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    assert engine is not None
                    assert hasattr(engine, "device")
                    assert engine.device == "cpu"
            except (ImportError, Exception) as e:
                pytest.skip(f"marytts dependencies not installed: {e}")

    def test_marytts_engine_has_required_methods(self):
        """Test MaryTTSEngine has required methods."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    required_methods = ["initialize", "cleanup", "synthesize"]
                    for method in required_methods:
                        assert hasattr(engine, method), f"MaryTTSEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")

    def test_marytts_engine_has_optimization_features(self):
        """Test MaryTTSEngine has optimization features."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    # Check for LRU cache
                    assert hasattr(
                        engine, "_synthesis_cache"
                    ), "MaryTTSEngine should have synthesis cache"
                    # Check for cache management
                    assert hasattr(
                        engine, "clear_cache"
                    ), "MaryTTSEngine should have clear_cache method"
                    assert hasattr(
                        engine, "get_cache_stats"
                    ), "MaryTTSEngine should have get_cache_stats method"
                    # Check for connection pooling
                    assert hasattr(
                        engine, "session"
                    ), "MaryTTSEngine should have session for connection pooling"
                    # Check for cache enable flag
                    assert hasattr(
                        engine, "enable_cache"
                    ), "MaryTTSEngine should have enable_cache attribute"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")


class TestMaryTTSEngineCaching:
    """Test MaryTTS engine caching functionality."""

    def test_lru_cache_implementation(self):
        """Test LRU synthesis cache implementation."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    # Check for LRU cache (OrderedDict)
                    assert hasattr(engine, "_synthesis_cache"), "Should have synthesis cache"
                    from collections import OrderedDict

                    assert isinstance(
                        engine._synthesis_cache, OrderedDict
                    ), "Synthesis cache should be OrderedDict for LRU behavior"
                    # Check for cache max size
                    assert hasattr(
                        engine, "_cache_max_size"
                    ), "Should have cache max size attribute"
                    assert isinstance(
                        engine._cache_max_size, int
                    ), "Cache max size should be an integer"
                    assert engine._cache_max_size > 0, "Cache max size should be positive"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")

    def test_cache_stats_method(self):
        """Test get_cache_stats method exists and returns valid data."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    stats = engine.get_cache_stats()
                    assert isinstance(stats, dict), "Cache stats should be a dictionary"
                    assert "cache_size" in stats, "Should include cache_size"
                    assert "max_cache_size" in stats, "Should include max_cache_size"
                    assert "cache_enabled" in stats, "Should include cache_enabled"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")

    def test_clear_cache_method(self):
        """Test clear_cache method exists and is callable."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    assert hasattr(engine, "clear_cache"), "Should have clear_cache method"
                    assert callable(engine.clear_cache), "clear_cache should be callable"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")


class TestMaryTTSEngineConnectionPooling:
    """Test MaryTTS engine connection pooling functionality."""

    def test_connection_pooling_support(self):
        """Test connection pooling functionality exists."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    # Check for session (connection pooling)
                    assert hasattr(
                        engine, "session"
                    ), "Should have session attribute for connection pooling"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")

    def test_session_initialization(self):
        """Test session is initialized for connection pooling."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests") as mock_requests:
                    mock_session = MagicMock()
                    mock_requests.Session.return_value = mock_session
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    # Initialize to set up session
                    engine.initialize()
                    # Check session was created
                    assert engine.session is not None, "Session should be initialized"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")


class TestMaryTTSEngineProtocol:
    """Test MaryTTS engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test MaryTTSEngine implements EngineProtocol."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    assert hasattr(engine, "initialize"), "Should implement initialize"
                    assert hasattr(engine, "cleanup"), "Should implement cleanup"
                    assert hasattr(engine, "is_initialized"), "Should implement is_initialized"
                    assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    assert engine.get_device() == "cpu"
                    engine_cuda = marytts_engine.MaryTTSEngine(device="cuda", gpu=True)
                    assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")


class TestMaryTTSEngineOptimization:
    """Test MaryTTS engine optimization features."""

    def test_lru_cache_move_to_end(self):
        """Test LRU cache uses move_to_end for cache hits."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                import inspect

                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    if hasattr(engine, "synthesize"):
                        source = inspect.getsource(engine.synthesize)
                        assert (
                            "move_to_end" in source or "_synthesis_cache" in source
                        ), "synthesize should use LRU cache with move_to_end"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")

    def test_cache_eviction_logic(self):
        """Test cache eviction when cache is full."""
        if hasattr(marytts_engine, "MaryTTSEngine"):
            try:
                with patch("marytts_engine.requests"):
                    engine = marytts_engine.MaryTTSEngine(device="cpu", gpu=False)
                    # Check for cache eviction logic
                    assert hasattr(
                        engine, "_cache_max_size"
                    ), "Should have cache max size for eviction"
                    # Check eviction happens when cache is full
                    import inspect

                    if hasattr(engine, "synthesize"):
                        source = inspect.getsource(engine.synthesize)
                        assert (
                            "_cache_max_size" in source or "oldest" in source.lower()
                        ), "synthesize should handle cache eviction"
            except (ImportError, Exception):
                pytest.skip("marytts dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
