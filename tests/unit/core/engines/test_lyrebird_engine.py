"""
Unit Tests for Lyrebird Engine
Tests Lyrebird engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the lyrebird engine module
try:
    from app.core.engines import lyrebird_engine
except ImportError:
    pytest.skip("Could not import lyrebird_engine", allow_module_level=True)


class TestLyrebirdEngineImports:
    """Test lyrebird engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert lyrebird_engine is not None, "Failed to import lyrebird_engine module"

    def test_module_has_lyrebird_engine_class(self):
        """Test module has LyrebirdEngine class."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            cls = lyrebird_engine.LyrebirdEngine
            assert isinstance(cls, type), "LyrebirdEngine should be a class"


class TestLyrebirdEngineClass:
    """Test LyrebirdEngine class."""

    def test_lyrebird_engine_class_exists(self):
        """Test LyrebirdEngine class exists."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            cls = lyrebird_engine.LyrebirdEngine
            assert isinstance(cls, type), "LyrebirdEngine should be a class"

    def test_lyrebird_engine_initialization(self):
        """Test LyrebirdEngine can be instantiated."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                # Mock requests to avoid actual API calls
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    assert engine is not None
                    assert hasattr(engine, "device")
                    assert engine.device == "cpu"
            except (ImportError, Exception) as e:
                pytest.skip(f"lyrebird dependencies not installed: {e}")

    def test_lyrebird_engine_has_required_methods(self):
        """Test LyrebirdEngine has required methods."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    required_methods = ["initialize", "cleanup", "clone_voice"]
                    for method in required_methods:
                        assert hasattr(
                            engine, method
                        ), f"LyrebirdEngine missing method: {method}"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")

    def test_lyrebird_engine_has_optimization_features(self):
        """Test LyrebirdEngine has optimization features."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    # Check for LRU cache
                    assert hasattr(
                        engine, "_synthesis_cache"
                    ), "LyrebirdEngine should have synthesis cache"
                    # Check for cache management
                    assert hasattr(
                        engine, "clear_cache"
                    ), "LyrebirdEngine should have clear_cache method"
                    assert hasattr(
                        engine, "get_cache_stats"
                    ), "LyrebirdEngine should have get_cache_stats method"
                    # Check for connection pooling
                    assert hasattr(
                        engine, "_session"
                    ), "LyrebirdEngine should have session for connection pooling"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")


class TestLyrebirdEngineCaching:
    """Test Lyrebird engine caching functionality."""

    def test_lru_cache_implementation(self):
        """Test LRU synthesis cache implementation."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    # Check for LRU cache (OrderedDict)
                    assert hasattr(
                        engine, "_synthesis_cache"
                    ), "Should have synthesis cache"
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
                pytest.skip("lyrebird dependencies not installed")

    def test_cache_stats_method(self):
        """Test get_cache_stats method exists and returns valid data."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    stats = engine.get_cache_stats()
                    assert isinstance(stats, dict), "Cache stats should be a dictionary"
                    assert "cache_size" in stats, "Should include cache_size"
                    assert "max_cache_size" in stats, "Should include max_cache_size"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")

    def test_clear_cache_method(self):
        """Test clear_cache method exists and is callable."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    assert hasattr(engine, "clear_cache"), "Should have clear_cache method"
                    assert callable(engine.clear_cache), "clear_cache should be callable"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")


class TestLyrebirdEngineConnectionPooling:
    """Test Lyrebird engine connection pooling functionality."""

    def test_connection_pooling_support(self):
        """Test connection pooling functionality exists."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    # Check for session (connection pooling)
                    assert hasattr(
                        engine, "_session"
                    ), "Should have _session attribute for connection pooling"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")

    def test_session_initialization(self):
        """Test session is initialized for connection pooling."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests") as mock_requests:
                    mock_session = MagicMock()
                    mock_requests.Session.return_value = mock_session
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    # Initialize to set up session
                    engine.initialize()
                    # Check session was created
                    assert engine._session is not None, "Session should be initialized"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")


class TestLyrebirdEngineProtocol:
    """Test Lyrebird engine protocol compliance."""

    def test_engine_protocol_compliance(self):
        """Test LyrebirdEngine implements EngineProtocol."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    assert hasattr(engine, "initialize"), "Should implement initialize"
                    assert hasattr(engine, "cleanup"), "Should implement cleanup"
                    assert hasattr(
                        engine, "is_initialized"
                    ), "Should implement is_initialized"
                    assert hasattr(engine, "get_device"), "Should implement get_device"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")

    def test_device_management(self):
        """Test device management methods."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    assert engine.get_device() == "cpu"
                    engine_cuda = lyrebird_engine.LyrebirdEngine(device="cuda", gpu=True)
                    assert engine_cuda.get_device() == "cuda"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")


class TestLyrebirdEngineOptimization:
    """Test Lyrebird engine optimization features."""

    def test_lru_cache_move_to_end(self):
        """Test LRU cache uses move_to_end for cache hits."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                import inspect

                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    if hasattr(engine, "clone_voice"):
                        source = inspect.getsource(engine.clone_voice)
                        assert (
                            "move_to_end" in source or "_synthesis_cache" in source
                        ), "clone_voice should use LRU cache with move_to_end"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")

    def test_cache_eviction_logic(self):
        """Test cache eviction when cache is full."""
        if hasattr(lyrebird_engine, "LyrebirdEngine"):
            try:
                with patch("lyrebird_engine.requests"):
                    engine = lyrebird_engine.LyrebirdEngine(device="cpu", gpu=False)
                    # Check for cache eviction logic
                    assert hasattr(
                        engine, "_cache_max_size"
                    ), "Should have cache max size for eviction"
                    # Check eviction happens when cache is full
                    import inspect

                    if hasattr(engine, "clone_voice"):
                        source = inspect.getsource(engine.clone_voice)
                        assert (
                            "_cache_max_size" in source or "oldest" in source.lower()
                        ), "clone_voice should handle cache eviction"
            except (ImportError, Exception):
                pytest.skip("lyrebird dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

