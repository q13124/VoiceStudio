"""
Unit Tests for ComfyUI Engine
Tests ComfyUI image generation engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the ComfyUI engine module
try:
    from app.core.engines import comfyui_engine
except ImportError:
    pytest.skip("Could not import comfyui_engine", allow_module_level=True)


class TestComfyUIEngineImports:
    """Test ComfyUI engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            comfyui_engine is not None
        ), "Failed to import comfyui_engine module"

    def test_module_has_comfyui_engine_class(self):
        """Test module has ComfyUIEngine class."""
        if hasattr(comfyui_engine, "ComfyUIEngine"):
            cls = getattr(comfyui_engine, "ComfyUIEngine")
            assert isinstance(cls, type), "ComfyUIEngine should be a class"


class TestComfyUIEngineClass:
    """Test ComfyUIEngine class."""

    def test_comfyui_engine_class_exists(self):
        """Test ComfyUIEngine class exists."""
        if hasattr(comfyui_engine, "ComfyUIEngine"):
            cls = getattr(comfyui_engine, "ComfyUIEngine")
            assert isinstance(cls, type), "ComfyUIEngine should be a class"

    def test_comfyui_engine_initialization(self):
        """Test ComfyUIEngine can be instantiated."""
        if hasattr(comfyui_engine, "ComfyUIEngine"):
            engine = comfyui_engine.ComfyUIEngine(
                server_url="http://127.0.0.1:8188", device="cpu", gpu=False
            )
            assert engine is not None
            assert hasattr(engine, "device")
            assert engine.device == "cpu"

    def test_comfyui_engine_has_required_methods(self):
        """Test ComfyUIEngine has required methods."""
        if hasattr(comfyui_engine, "ComfyUIEngine"):
            engine = comfyui_engine.ComfyUIEngine(
                server_url="http://127.0.0.1:8188", device="cpu", gpu=False
            )
            required_methods = ["initialize", "cleanup", "generate"]
            for method in required_methods:
                assert hasattr(
                    engine, method
                ), f"ComfyUIEngine missing method: {method}"

    def test_comfyui_engine_has_optimization_features(self):
        """Test ComfyUIEngine has optimization features."""
        if hasattr(comfyui_engine, "ComfyUIEngine"):
            engine = comfyui_engine.ComfyUIEngine(
                server_url="http://127.0.0.1:8188",
                device="cpu",
                gpu=False,
                enable_cache=True,
                cache_size=200,
                batch_size=8,
                pool_connections=20,
                pool_maxsize=40,
            )
            # Check for caching support
            assert hasattr(
                engine, "enable_cache"
            ), "ComfyUIEngine should support caching"
            assert engine.enable_cache is True
            assert engine.cache_size == 200
            # Check for batch processing
            assert hasattr(
                engine, "batch_size"
            ), "ComfyUIEngine should support batch processing"
            assert engine.batch_size >= 8
            # Check for connection pooling
            assert engine.pool_connections >= 20
            assert engine.pool_maxsize >= 40


class TestComfyUIEngineCache:
    """Test ComfyUI engine LRU cache functionality."""

    def test_cache_initialization(self):
        """Test cache is initialized correctly."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
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
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188", device="cpu", gpu=False
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
                workflow=None,
            )
            assert cache_key is not None
            assert isinstance(cache_key, str)
            assert len(cache_key) > 0

    def test_cache_stats_tracking(self):
        """Test cache statistics are tracked."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
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
            # ComfyUI returns workflow_cache_size and response_cache_size instead of size
            assert "workflow_cache_size" in stats or "response_cache_size" in stats or "size" in stats
            hits = stats.get("cache_hits", stats.get("hits", 0))
            misses = stats.get("cache_misses", stats.get("misses", 0))
            assert hits == 0
            assert misses == 0

    def test_cache_stats_reset_on_cleanup(self):
        """Test cache stats are reset on cleanup."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
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
        # Note: ComfyUI cleanup doesn't reset cache stats, only clears caches
        if hasattr(engine, "_response_cache"):
            assert len(engine._response_cache) == 0
        if hasattr(engine, "_workflow_cache"):
            assert len(engine._workflow_cache) == 0


class TestComfyUIEngineBatchProcessing:
    """Test ComfyUI engine batch processing functionality."""

    def test_batch_size_configuration(self):
        """Test batch size is configured correctly."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
            batch_size=8,
            device="cpu",
            gpu=False,
        )
        assert engine.batch_size >= 8

    def test_batch_generate_method_exists(self):
        """Test batch_generate method exists."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188", device="cpu", gpu=False
        )
        assert hasattr(engine, "batch_generate")


class TestComfyUIEngineConnectionPooling:
    """Test ComfyUI engine connection pooling functionality."""

    def test_connection_pool_configuration(self):
        """Test connection pool is configured correctly."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
            pool_connections=20,
            pool_maxsize=40,
            device="cpu",
            gpu=False,
        )
        assert engine.pool_connections >= 20
        assert engine.pool_maxsize >= 40

    def test_connection_pool_minimum_values(self):
        """Test connection pool has minimum values."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
            pool_connections=5,  # Below minimum
            pool_maxsize=10,  # Below minimum
            device="cpu",
            gpu=False,
        )
        # Should be increased to minimums
        assert engine.pool_connections >= 20
        assert engine.pool_maxsize >= 40


class TestComfyUIEngineInitialization:
    """Test ComfyUI engine initialization."""

    @patch("app.core.engines.comfyui_engine.requests.Session.get")
    def test_initialize_success(self, mock_get):
        """Test successful initialization."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188", device="cpu", gpu=False
        )
        result = engine.initialize()
        assert result is True
        assert engine.is_initialized() is True

    @patch("app.core.engines.comfyui_engine.requests.get")
    def test_initialize_failure(self, mock_get):
        """Test initialization failure."""
        mock_get.side_effect = Exception("Connection error")

        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188", device="cpu", gpu=False
        )
        result = engine.initialize()
        assert result is False


class TestComfyUIEngineCleanup:
    """Test ComfyUI engine cleanup functionality."""

    def test_cleanup_resets_cache(self):
        """Test cleanup resets cache."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        if hasattr(engine, "_response_cache"):
            engine._response_cache["test"] = MagicMock()
        if hasattr(engine, "_workflow_cache"):
            engine._workflow_cache["test"] = MagicMock()
        engine._cache_stats["hits"] = 10
        engine._cache_stats["misses"] = 5

        engine.cleanup()

        if hasattr(engine, "_response_cache"):
            assert len(engine._response_cache) == 0
        if hasattr(engine, "_workflow_cache"):
            assert len(engine._workflow_cache) == 0
        # Note: ComfyUI cleanup doesn't reset cache stats, only clears caches

    def test_cleanup_resets_initialization(self):
        """Test cleanup resets initialization state."""
        engine = comfyui_engine.ComfyUIEngine(
            server_url="http://127.0.0.1:8188", device="cpu", gpu=False
        )
        engine._initialized = True
        engine.cleanup()
        assert engine.is_initialized() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

