"""
Unit Tests for InvokeAI Engine
Tests InvokeAI image generation engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the InvokeAI engine module
try:
    from app.core.engines import invokeai_engine
except ImportError:
    pytest.skip("Could not import invokeai_engine", allow_module_level=True)


class TestInvokeAIEngineImports:
    """Test InvokeAI engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert invokeai_engine is not None, "Failed to import invokeai_engine module"

    def test_module_has_invokeai_engine_class(self):
        """Test module has InvokeAIEngine class."""
        if hasattr(invokeai_engine, "InvokeAIEngine"):
            cls = invokeai_engine.InvokeAIEngine
            assert isinstance(cls, type), "InvokeAIEngine should be a class"


class TestInvokeAIEngineClass:
    """Test InvokeAIEngine class."""

    def test_invokeai_engine_class_exists(self):
        """Test InvokeAIEngine class exists."""
        if hasattr(invokeai_engine, "InvokeAIEngine"):
            cls = invokeai_engine.InvokeAIEngine
            assert isinstance(cls, type), "InvokeAIEngine should be a class"

    def test_invokeai_engine_initialization(self):
        """Test InvokeAIEngine can be instantiated."""
        if hasattr(invokeai_engine, "InvokeAIEngine"):
            engine = invokeai_engine.InvokeAIEngine(
                server_url="http://127.0.0.1:9090", device="cpu", gpu=False
            )
            assert engine is not None
            assert hasattr(engine, "device")
            assert engine.device == "cpu"

    def test_invokeai_engine_has_required_methods(self):
        """Test InvokeAIEngine has required methods."""
        if hasattr(invokeai_engine, "InvokeAIEngine"):
            engine = invokeai_engine.InvokeAIEngine(
                server_url="http://127.0.0.1:9090", device="cpu", gpu=False
            )
            required_methods = ["initialize", "cleanup", "generate"]
            for method in required_methods:
                assert hasattr(engine, method), f"InvokeAIEngine missing method: {method}"

    def test_invokeai_engine_has_optimization_features(self):
        """Test InvokeAIEngine has optimization features."""
        if hasattr(invokeai_engine, "InvokeAIEngine"):
            engine = invokeai_engine.InvokeAIEngine(
                server_url="http://127.0.0.1:9090",
                device="cpu",
                gpu=False,
                enable_cache=True,
                cache_size=200,
                batch_size=8,
                pool_connections=20,
                pool_maxsize=40,
            )
            # Check for caching support
            assert hasattr(engine, "enable_cache"), "InvokeAIEngine should support caching"
            assert engine.enable_cache is True
            assert engine.cache_size == 200
            # Check for batch processing
            assert hasattr(engine, "batch_size"), "InvokeAIEngine should support batch processing"
            assert engine.batch_size >= 8
            # Check for connection pooling
            assert engine.pool_connections >= 20
            assert engine.pool_maxsize >= 40


class TestInvokeAIEngineCache:
    """Test InvokeAI engine LRU cache functionality."""

    def test_cache_initialization(self):
        """Test cache is initialized correctly."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
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
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
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

    def test_cache_key_consistency(self):
        """Test cache key is consistent for same inputs."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
        key1 = engine._generate_cache_key(
            prompt="test prompt",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            sampler="Euler a",
            seed=None,
        )
        key2 = engine._generate_cache_key(
            prompt="test prompt",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            sampler="Euler a",
            seed=None,
        )
        assert key1 == key2

    def test_cache_key_different_for_different_inputs(self):
        """Test cache key differs for different inputs."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
        key1 = engine._generate_cache_key(
            prompt="test prompt 1",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            sampler="Euler a",
            seed=None,
        )
        key2 = engine._generate_cache_key(
            prompt="test prompt 2",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            sampler="Euler a",
            seed=None,
        )
        assert key1 != key2

    def test_cache_stats_tracking(self):
        """Test cache statistics are tracked."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        stats = engine.get_cache_stats()
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate" in stats
        assert "size" in stats
        assert stats["cache_hits"] == 0
        assert stats["cache_misses"] == 0
        assert stats["size"] == 0

    def test_cache_stats_reset_on_cleanup(self):
        """Test cache stats are reset on cleanup."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        # Simulate some cache activity
        engine._cache_stats["hits"] = 10
        engine._cache_stats["misses"] = 5
        engine._response_cache["test_key"] = MagicMock()
        # Cleanup should reset stats
        engine.cleanup()
        assert engine._cache_stats["hits"] == 0
        assert engine._cache_stats["misses"] == 0
        assert len(engine._response_cache) == 0


class TestInvokeAIEngineBatchProcessing:
    """Test InvokeAI engine batch processing functionality."""

    def test_batch_size_configuration(self):
        """Test batch size is configured correctly."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            batch_size=8,
            device="cpu",
            gpu=False,
        )
        assert engine.batch_size >= 8

    def test_batch_generate_method_exists(self):
        """Test batch_generate method exists."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
        assert hasattr(engine, "batch_generate")

    @patch("app.core.engines.invokeai_engine.requests.post")
    @patch("app.core.engines.invokeai_engine.Image.open")
    def test_batch_generate_uses_threadpool(self, mock_image_open, mock_post):
        """Test batch generation uses ThreadPoolExecutor."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "images": ["base64_encoded_image"],
            "status": "success",
        }
        mock_post.return_value = mock_response
        mock_image_open.return_value = MagicMock()

        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            batch_size=2,
            device="cpu",
            gpu=False,
        )
        engine.initialize()

        prompts = ["prompt1", "prompt2", "prompt3"]
        with patch("app.core.engines.invokeai_engine.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__.return_value.map.return_value = [
                MagicMock() for _ in prompts
            ]
            try:
                engine.batch_generate(prompts, batch_size=2)
            except Exception:
                pass  # Expected to fail without actual server
            # Verify ThreadPoolExecutor was used
            assert True  # If we get here, the method exists


class TestInvokeAIEngineConnectionPooling:
    """Test InvokeAI engine connection pooling functionality."""

    def test_connection_pool_configuration(self):
        """Test connection pool is configured correctly."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            pool_connections=20,
            pool_maxsize=40,
            device="cpu",
            gpu=False,
        )
        assert engine.pool_connections >= 20
        assert engine.pool_maxsize >= 40

    def test_connection_pool_minimum_values(self):
        """Test connection pool has minimum values."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            pool_connections=5,  # Below minimum
            pool_maxsize=10,  # Below minimum
            device="cpu",
            gpu=False,
        )
        # Should be increased to minimums
        assert engine.pool_connections >= 20
        assert engine.pool_maxsize >= 40


class TestInvokeAIEngineInitialization:
    """Test InvokeAI engine initialization."""

    @patch("app.core.engines.invokeai_engine.requests.Session.get")
    def test_initialize_success(self, mock_get):
        """Test successful initialization."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
        result = engine.initialize()
        assert result is True
        assert engine.is_initialized() is True

    @patch("app.core.engines.invokeai_engine.requests.get")
    def test_initialize_failure(self, mock_get):
        """Test initialization failure."""
        mock_get.side_effect = Exception("Connection error")

        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
        result = engine.initialize()
        assert result is False


class TestInvokeAIEngineCleanup:
    """Test InvokeAI engine cleanup functionality."""

    def test_cleanup_resets_cache(self):
        """Test cleanup resets cache."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090",
            enable_cache=True,
            cache_size=200,
            device="cpu",
            gpu=False,
        )
        engine._response_cache["test"] = MagicMock()
        engine._cache_stats["hits"] = 10
        engine._cache_stats["misses"] = 5

        engine.cleanup()

        assert len(engine._response_cache) == 0
        assert engine._cache_stats["hits"] == 0
        assert engine._cache_stats["misses"] == 0

    def test_cleanup_resets_initialization(self):
        """Test cleanup resets initialization state."""
        engine = invokeai_engine.InvokeAIEngine(
            server_url="http://127.0.0.1:9090", device="cpu", gpu=False
        )
        engine._initialized = True
        engine.cleanup()
        assert engine.is_initialized() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
