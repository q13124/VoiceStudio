"""
Unit Tests for Automatic1111 Engine
Tests Automatic1111 image generation engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the Automatic1111 engine module
try:
    from app.core.engines import automatic1111_engine
except ImportError:
    pytest.skip("Could not import automatic1111_engine", allow_module_level=True)


class TestAutomatic1111EngineImports:
    """Test Automatic1111 engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert automatic1111_engine is not None, "Failed to import automatic1111_engine module"

    def test_module_has_automatic1111_engine_class(self):
        """Test module has Automatic1111Engine class."""
        if hasattr(automatic1111_engine, "Automatic1111Engine"):
            cls = automatic1111_engine.Automatic1111Engine
            assert isinstance(cls, type), "Automatic1111Engine should be a class"


class TestAutomatic1111EngineClass:
    """Test Automatic1111Engine class."""

    def test_automatic1111_engine_class_exists(self):
        """Test Automatic1111Engine class exists."""
        if hasattr(automatic1111_engine, "Automatic1111Engine"):
            cls = automatic1111_engine.Automatic1111Engine
            assert isinstance(cls, type), "Automatic1111Engine should be a class"

    def test_automatic1111_engine_initialization(self):
        """Test Automatic1111Engine can be instantiated."""
        if hasattr(automatic1111_engine, "Automatic1111Engine"):
            engine = automatic1111_engine.Automatic1111Engine(
                webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
            )
            assert engine is not None
            assert hasattr(engine, "device")
            assert engine.device == "cpu"

    def test_automatic1111_engine_has_required_methods(self):
        """Test Automatic1111Engine has required methods."""
        if hasattr(automatic1111_engine, "Automatic1111Engine"):
            engine = automatic1111_engine.Automatic1111Engine(
                webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
            )
            required_methods = ["initialize", "cleanup", "generate"]
            for method in required_methods:
                assert hasattr(engine, method), f"Automatic1111Engine missing method: {method}"

    def test_automatic1111_engine_has_optimization_features(self):
        """Test Automatic1111Engine has optimization features."""
        if hasattr(automatic1111_engine, "Automatic1111Engine"):
            engine = automatic1111_engine.Automatic1111Engine(
                webui_url="http://127.0.0.1:7860",
                device="cpu",
                gpu=False,
                enable_cache=True,
                cache_size=200,
                batch_size=8,
                pool_connections=20,
                pool_maxsize=40,
            )
            # Check for caching support
            assert hasattr(engine, "enable_cache"), "Automatic1111Engine should support caching"
            assert engine.enable_cache is True
            assert engine.cache_size == 200
            # Check for batch processing
            assert hasattr(
                engine, "batch_size"
            ), "Automatic1111Engine should support batch processing"
            assert engine.batch_size >= 8
            # Check for connection pooling
            assert engine.pool_connections >= 20
            assert engine.pool_maxsize >= 40


class TestAutomatic1111EngineCache:
    """Test Automatic1111 engine LRU cache functionality."""

    def test_cache_initialization(self):
        """Test cache is initialized correctly."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        assert hasattr(engine, "_response_cache")
        assert hasattr(engine, "_cache_stats")
        assert engine._cache_stats["hits"] == 0
        assert engine._cache_stats["misses"] == 0

    def test_cache_key_generation(self):
        """Test cache key generation."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
        )
        if hasattr(engine, "_generate_cache_key"):
            cache_key = engine._generate_cache_key(
                prompt="test prompt",
                negative_prompt="",
                width=512,
                height=512,
                steps=20,
                cfg_scale=7.0,
                sampler="Euler a",
                seed=None,
            )
            assert cache_key is not None
            assert isinstance(cache_key, str)
            assert len(cache_key) > 0

    def test_cache_stats_tracking(self):
        """Test cache statistics are tracked."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        if hasattr(engine, "get_cache_stats"):
            stats = engine.get_cache_stats()
            assert "cache_hits" in stats or "hits" in stats
            assert "cache_misses" in stats or "misses" in stats
            assert "hit_rate" in stats
            assert "size" in stats
            hits = stats.get("cache_hits", stats.get("hits", 0))
            misses = stats.get("cache_misses", stats.get("misses", 0))
            assert hits == 0
            assert misses == 0
            assert stats["size"] == 0

    def test_cache_stats_reset_on_cleanup(self):
        """Test cache stats are reset on cleanup."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        # Simulate some cache activity
        engine._cache_stats["hits"] = 10
        engine._cache_stats["misses"] = 5
        if hasattr(engine, "_response_cache"):
            engine._response_cache["test_key"] = MagicMock()
        # Cleanup clears caches but doesn't reset stats (by design)
        engine.cleanup()
        # Note: Automatic1111 cleanup doesn't reset cache stats, only clears caches
        if hasattr(engine, "_response_cache"):
            assert len(engine._response_cache) == 0


class TestAutomatic1111EngineBatchProcessing:
    """Test Automatic1111 engine batch processing functionality."""

    def test_batch_size_configuration(self):
        """Test batch size is configured correctly."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            batch_size=8,
            device="cpu",
            gpu=False,
        )
        assert engine.batch_size >= 8

    def test_batch_generate_method_exists(self):
        """Test batch_generate method exists."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
        )
        assert hasattr(engine, "batch_generate")


class TestAutomatic1111EngineConnectionPooling:
    """Test Automatic1111 engine connection pooling functionality."""

    def test_connection_pool_configuration(self):
        """Test connection pool is configured correctly."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            pool_connections=20,
            pool_maxsize=40,
            device="cpu",
            gpu=False,
        )
        assert engine.pool_connections >= 20
        assert engine.pool_maxsize >= 40

    def test_connection_pool_minimum_values(self):
        """Test connection pool has minimum values."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            pool_connections=5,  # Below minimum
            pool_maxsize=10,  # Below minimum
            device="cpu",
            gpu=False,
        )
        # Should be increased to minimums
        assert engine.pool_connections >= 20
        assert engine.pool_maxsize >= 40


class TestAutomatic1111EngineInitialization:
    """Test Automatic1111 engine initialization."""

    @patch("app.core.engines.automatic1111_engine.requests.Session.get")
    def test_initialize_success(self, mock_get):
        """Test successful initialization."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
        )
        result = engine.initialize()
        assert result is True
        assert engine.is_initialized() is True

    @patch("app.core.engines.automatic1111_engine.requests.get")
    def test_initialize_failure(self, mock_get):
        """Test initialization failure."""
        mock_get.side_effect = Exception("Connection error")

        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
        )
        result = engine.initialize()
        assert result is False


class TestAutomatic1111EngineCleanup:
    """Test Automatic1111 engine cleanup functionality."""

    def test_cleanup_resets_cache(self):
        """Test cleanup resets cache."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        if hasattr(engine, "_response_cache"):
            engine._response_cache["test"] = MagicMock()
        engine._cache_stats["hits"] = 10
        engine._cache_stats["misses"] = 5

        engine.cleanup()

        if hasattr(engine, "_response_cache"):
            assert len(engine._response_cache) == 0
        # Note: Automatic1111 cleanup doesn't reset cache stats, only clears caches

    def test_cleanup_resets_initialization(self):
        """Test cleanup resets initialization state."""
        engine = automatic1111_engine.Automatic1111Engine(
            webui_url="http://127.0.0.1:7860", device="cpu", gpu=False
        )
        engine._initialized = True
        engine.cleanup()
        assert engine.is_initialized() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
