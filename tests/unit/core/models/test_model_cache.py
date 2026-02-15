"""
Unit tests for Model Caching System.

Tests LRU cache, memory limits, TTL, statistics, and cache warming.
"""

import time
from unittest.mock import Mock, patch

import pytest

from app.core.models.cache import ModelCache, clear_global_cache, get_model_cache


class TestModelCache:
    """Tests for ModelCache class."""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = ModelCache(max_models=5, max_memory_mb=100.0, default_ttl=60)
        assert cache.max_models == 5
        assert cache.max_memory_mb == 100.0
        assert cache.default_ttl == 60
        assert len(cache._cache) == 0

    def test_generate_key(self):
        """Test cache key generation."""
        cache = ModelCache()

        key1 = cache._generate_key("xtts", "model1", "cuda")
        key2 = cache._generate_key("xtts", "model1", "cuda")
        key3 = cache._generate_key("xtts", "model2", "cuda")
        key4 = cache._generate_key("xtts", "model1", "cpu")

        assert key1 == key2
        assert key1 != key3
        assert key1 != key4  # Different device

    def test_set_and_get(self):
        """Test setting and getting models."""
        cache = ModelCache()
        model = Mock()

        cache.set("xtts", "model1", model, device="cuda")

        cached = cache.get("xtts", "model1", device="cuda")
        assert cached == model

        # Different device should not return
        assert cache.get("xtts", "model1", device="cpu") is None

    def test_cache_expiration(self):
        """Test cache expiration with TTL."""
        cache = ModelCache(default_ttl=1)  # 1 second TTL
        model = Mock()

        cache.set("xtts", "model1", model)

        # Should be available immediately
        assert cache.get("xtts", "model1") is not None

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("xtts", "model1") is None

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = ModelCache(max_models=2)

        model1 = Mock()
        model2 = Mock()
        model3 = Mock()

        cache.set("xtts", "model1", model1)
        cache.set("xtts", "model2", model2)
        cache.set("xtts", "model3", model3)  # Should evict model1

        assert cache.get("xtts", "model1") is None
        assert cache.get("xtts", "model2") is not None
        assert cache.get("xtts", "model3") is not None

    def test_memory_limit_eviction(self):
        """Test eviction when memory limit exceeded."""
        cache = ModelCache(max_memory_mb=200.0)

        model1 = Mock()
        model2 = Mock()
        Mock()

        # Set models with memory usage
        cache.set("xtts", "model1", model1, memory_mb=150.0)
        cache.set("xtts", "model2", model2, memory_mb=100.0)  # Should evict model1

        assert cache.get("xtts", "model1") is None
        assert cache.get("xtts", "model2") is not None

    def test_remove(self):
        """Test removing model from cache."""
        cache = ModelCache()
        model = Mock()

        cache.set("xtts", "model1", model)
        assert cache.get("xtts", "model1") is not None

        removed = cache.remove("xtts", "model1")
        assert removed is True
        assert cache.get("xtts", "model1") is None

        # Remove non-existent
        assert cache.remove("xtts", "nonexistent") is False

    def test_clear(self):
        """Test clearing cache."""
        cache = ModelCache()

        cache.set("xtts", "model1", Mock())
        cache.set("whisper", "model2", Mock())

        assert len(cache._cache) == 2

        cache.clear()
        assert len(cache._cache) == 0
        assert cache._stats["current_memory_mb"] == 0.0

    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = ModelCache()

        cache.set("xtts", "model1", Mock())
        cache.get("xtts", "model1")  # Hit
        cache.get("xtts", "model2")  # Miss

        stats = cache.get_stats()

        assert stats["cache_size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert "current_memory_mb" in stats

    def test_list_cached_models(self):
        """Test listing cached models."""
        cache = ModelCache()

        cache.set("xtts", "model1", Mock(), device="cuda")
        cache.set("whisper", "model2", Mock(), device="cpu")

        models = cache.list_cached_models()

        assert len(models) == 2
        assert models[0]["engine"] in ["xtts", "whisper"]
        assert "key" in models[0]
        assert "memory_mb" in models[0]
        assert "cached_at" in models[0]

    def test_warm_cache(self):
        """Test cache warming."""
        cache = ModelCache()

        model1 = Mock()
        model2 = Mock()

        def load_model1():
            return model1

        def load_model2():
            return model2

        models_to_warm = [
            ("xtts", "model1", "cuda", load_model1),
            ("whisper", "model2", "cpu", load_model2),
        ]

        cache.warm_cache(models_to_warm)

        assert cache.get("xtts", "model1", device="cuda") == model1
        assert cache.get("whisper", "model2", device="cpu") == model2

    def test_warm_cache_skip_existing(self):
        """Test that cache warming skips already cached models."""
        cache = ModelCache()

        model1 = Mock()
        cache.set("xtts", "model1", model1)

        load_count = 0

        def load_model():
            nonlocal load_count
            load_count += 1
            return Mock()

        models_to_warm = [("xtts", "model1", None, load_model)]
        cache.warm_cache(models_to_warm)

        # Should not have called load_model
        assert load_count == 0

    def test_estimate_memory_mb(self):
        """Test memory estimation for models."""
        cache = ModelCache()

        # Test with PyTorch-like model
        model_with_params = Mock()
        model_with_params.parameters.return_value = [
            Mock(numel=Mock(return_value=1000000))  # 1M parameters
        ]

        memory_mb = cache._estimate_memory_mb(model_with_params)
        # 1M params * 4 bytes = 4MB
        assert memory_mb > 0
        assert memory_mb < 10  # Should be around 4MB

        # Test with regular object
        regular_model = Mock()
        memory_mb = cache._estimate_memory_mb(regular_model)
        assert memory_mb == 100.0  # Default estimate

    def test_ttl_expiration(self):
        """Test TTL expiration with different default TTL values."""
        # Test with short TTL
        cache_short = ModelCache(default_ttl=1)  # 1 second TTL
        model1 = Mock()
        cache_short.set("xtts", "model1", model1)

        # Should be available immediately
        assert cache_short.get("xtts", "model1") is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache_short.get("xtts", "model1") is None

        # Test with longer TTL
        cache_long = ModelCache(default_ttl=60)  # 60 second TTL
        model2 = Mock()
        cache_long.set("xtts", "model2", model2)

        # Should be available immediately
        assert cache_long.get("xtts", "model2") is not None

        # Wait a bit (but not long enough to expire)
        time.sleep(0.5)

        # Should still be valid
        assert cache_long.get("xtts", "model2") is not None

    @patch("app.core.models.cache.psutil")
    def test_system_memory_usage(self, mock_psutil):
        """Test system memory usage detection."""
        cache = ModelCache()

        # Mock psutil
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 2 * 1024 * 1024 * 1024  # 2GB
        mock_psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
        cache._process = mock_process

        memory_usage = cache._get_system_memory_usage()
        assert memory_usage is not None
        assert 0.0 <= memory_usage <= 1.0
        # 2GB / 8GB = 0.25
        assert abs(memory_usage - 0.25) < 0.01

    @patch("app.core.models.cache.psutil")
    def test_memory_pressure_detection(self, mock_psutil):
        """Test memory pressure detection."""
        cache = ModelCache(
            memory_pressure_threshold=0.85,
            auto_eviction_enabled=True
        )

        # Mock high memory usage (90%)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 7.2 * 1024 * 1024 * 1024  # 7.2GB
        mock_psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
        cache._process = mock_process

        assert cache._detect_memory_pressure() is True

        # Mock low memory usage (50%)
        mock_process.memory_info.return_value.rss = 4 * 1024 * 1024 * 1024  # 4GB
        assert cache._detect_memory_pressure() is False

    @patch("app.core.models.cache.psutil")
    def test_dynamic_memory_limits(self, mock_psutil):
        """Test dynamic memory limit adjustment."""
        cache = ModelCache(
            max_models=10,
            max_memory_mb=1000.0,
            enable_dynamic_limits=True,
            memory_pressure_threshold=0.85
        )

        # Mock high memory usage (90%)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 7.2 * 1024 * 1024 * 1024  # 7.2GB
        mock_psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
        cache._process = mock_process

        # Trigger adjustment
        cache._adjust_memory_limits()

        # Limits should be reduced to 70% of original
        assert cache.max_memory_mb == 700.0  # 1000 * 0.7
        assert cache.max_models == 7  # 10 * 0.7 = 7
        assert cache._stats["dynamic_adjustments"] > 0

        # Mock low memory usage (50%)
        mock_process.memory_info.return_value.rss = 4 * 1024 * 1024 * 1024  # 4GB

        # Trigger adjustment again
        cache._adjust_memory_limits()

        # Limits should be restored
        assert cache.max_memory_mb == 1000.0
        assert cache.max_models == 10

    @patch("app.core.models.cache.psutil")
    def test_auto_eviction_on_memory_pressure(self, mock_psutil):
        """Test automatic eviction when memory pressure is detected."""
        cache = ModelCache(
            memory_pressure_threshold=0.85,
            auto_eviction_enabled=True
        )

        # Add some models
        model1 = Mock()
        model2 = Mock()
        cache.set("xtts", "model1", model1, memory_mb=50.0)
        cache.set("whisper", "model2", model2, memory_mb=50.0)

        initial_evictions = cache._stats["evictions"]

        # Mock high memory usage (90%)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 7.2 * 1024 * 1024 * 1024  # 7.2GB
        mock_psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
        cache._process = mock_process

        # Trigger eviction check
        cache._evict_on_memory_pressure()

        # Should have evicted models
        assert cache._stats["pressure_evictions"] > 0
        assert cache._stats["evictions"] > initial_evictions

    def test_statistics_completeness(self):
        """Test that all statistics are tracked."""
        cache = ModelCache()

        model1 = Mock()
        cache.set("xtts", "model1", model1)
        cache.get("xtts", "model1")  # Hit
        cache.get("xtts", "model2")  # Miss

        stats = cache.get_stats()

        # Check all expected statistics
        assert "cache_size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "evictions" in stats
        assert "total_loaded" in stats
        assert "current_memory_mb" in stats
        assert "hit_rate" in stats
        assert "dynamic_adjustments" in stats
        assert "pressure_evictions" in stats

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_loaded"] == 1

    def test_dynamic_limits_disabled(self):
        """Test that dynamic limits can be disabled."""
        cache = ModelCache(
            max_models=10,
            max_memory_mb=1000.0,
            enable_dynamic_limits=False
        )

        original_max_models = cache.max_models
        original_max_memory = cache.max_memory_mb

        # Try to adjust (should not change)
        cache._adjust_memory_limits()

        assert cache.max_models == original_max_models
        assert cache.max_memory_mb == original_max_memory

    def test_auto_eviction_disabled(self):
        """Test that auto eviction can be disabled."""
        cache = ModelCache(
            auto_eviction_enabled=False
        )

        # Add models
        model1 = Mock()
        cache.set("xtts", "model1", model1)

        initial_evictions = cache._stats["evictions"]

        # Should not evict even under pressure
        cache._evict_on_memory_pressure()

        assert cache._stats["evictions"] == initial_evictions
        assert cache._stats["pressure_evictions"] == 0


class TestGlobalModelCache:
    """Tests for global model cache functions."""

    def test_get_model_cache(self):
        """Test getting global model cache."""
        clear_global_cache()

        cache1 = get_model_cache()
        cache2 = get_model_cache()

        # Should return same instance
        assert cache1 is cache2

    def test_clear_global_cache(self):
        """Test clearing global cache."""
        cache = get_model_cache()
        cache.set("xtts", "model1", Mock())

        assert len(cache._cache) > 0

        clear_global_cache()

        # Cache should be cleared
        assert len(cache._cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

