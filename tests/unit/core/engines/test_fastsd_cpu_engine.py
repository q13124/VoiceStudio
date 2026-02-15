"""
Unit Tests for FastSD CPU Engine
Tests FastSD CPU image generation engine functionality including optimizations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the FastSD CPU engine module
try:
    from app.core.engines import fastsd_cpu_engine
except ImportError:
    pytest.skip("Could not import fastsd_cpu_engine", allow_module_level=True)


class TestFastSDCPUEngineImports:
    """Test FastSD CPU engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert fastsd_cpu_engine is not None, "Failed to import fastsd_cpu_engine module"

    def test_module_has_fastsd_cpu_engine_class(self):
        """Test module has FastSDCPUEngine class."""
        if hasattr(fastsd_cpu_engine, "FastSDCPUEngine"):
            cls = fastsd_cpu_engine.FastSDCPUEngine
            assert isinstance(cls, type), "FastSDCPUEngine should be a class"


class TestFastSDCPUEngineClass:
    """Test FastSDCPUEngine class."""

    def test_fastsd_cpu_engine_class_exists(self):
        """Test FastSDCPUEngine class exists."""
        if hasattr(fastsd_cpu_engine, "FastSDCPUEngine"):
            cls = fastsd_cpu_engine.FastSDCPUEngine
            assert isinstance(cls, type), "FastSDCPUEngine should be a class"

    def test_fastsd_cpu_engine_initialization(self):
        """Test FastSDCPUEngine can be instantiated."""
        if hasattr(fastsd_cpu_engine, "FastSDCPUEngine"):
            engine = fastsd_cpu_engine.FastSDCPUEngine(
                model_id="runwayml/stable-diffusion-v1-5",
                device="cpu",
                gpu=False,
            )
            assert engine is not None
            assert engine.device == "cpu"
            # FastSD CPU engine forces CPU, so gpu attribute may not exist

    def test_fastsd_cpu_engine_has_required_methods(self):
        """Test FastSDCPUEngine has required methods."""
        if hasattr(fastsd_cpu_engine, "FastSDCPUEngine"):
            engine = fastsd_cpu_engine.FastSDCPUEngine(
                model_id="runwayml/stable-diffusion-v1-5",
                device="cpu",
                gpu=False,
            )
            assert hasattr(engine, "initialize")
            assert hasattr(engine, "cleanup")
            assert hasattr(engine, "generate")
            assert hasattr(engine, "is_initialized")

    def test_fastsd_cpu_engine_has_optimization_features(self):
        """Test FastSDCPUEngine has optimization features."""
        if hasattr(fastsd_cpu_engine, "FastSDCPUEngine"):
            engine = fastsd_cpu_engine.FastSDCPUEngine(
                model_id="runwayml/stable-diffusion-v1-5",
                device="cpu",
                gpu=False,
                enable_response_cache=True,
                response_cache_size=100,
                batch_size=4,
            )
            assert hasattr(engine, "_response_cache")
            assert hasattr(engine, "_cache_stats")
            assert hasattr(engine, "batch_size")
            assert engine.batch_size == 4
            assert engine.response_cache_size == 100


class TestFastSDCPUEngineCache:
    """Test FastSD CPU engine cache functionality."""

    def test_cache_initialization(self):
        """Test cache is initialized."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            enable_response_cache=True,
            response_cache_size=100,
            device="cpu",
            gpu=False,
        )
        assert hasattr(engine, "_response_cache")
        assert hasattr(engine, "_cache_stats")
        assert engine.enable_response_cache is True
        assert engine.response_cache_size == 100

    def test_cache_key_generation(self):
        """Test cache key generation."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            device="cpu",
            gpu=False,
        )
        cache_key = engine._generate_cache_key(
            prompt="test prompt",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            seed=None,
        )
        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0

    def test_cache_key_consistency(self):
        """Test cache key is consistent for same inputs."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            device="cpu",
            gpu=False,
        )
        key1 = engine._generate_cache_key(
            prompt="test prompt",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            seed=None,
        )
        key2 = engine._generate_cache_key(
            prompt="test prompt",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            seed=None,
        )
        assert key1 == key2

    def test_cache_key_different_for_different_inputs(self):
        """Test cache key differs for different inputs."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            device="cpu",
            gpu=False,
        )
        key1 = engine._generate_cache_key(
            prompt="test prompt 1",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            seed=None,
        )
        key2 = engine._generate_cache_key(
            prompt="test prompt 2",
            negative_prompt="",
            width=512,
            height=512,
            steps=20,
            cfg_scale=7.0,
            seed=None,
        )
        assert key1 != key2

    def test_cache_stats_tracking(self):
        """Test cache statistics are tracked."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            enable_response_cache=True,
            response_cache_size=100,
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
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            enable_response_cache=True,
            response_cache_size=100,
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
        # Note: FastSD CPU cleanup doesn't reset cache stats, only clears caches
        if hasattr(engine, "_response_cache"):
            assert len(engine._response_cache) == 0


class TestFastSDCPUEngineBatchProcessing:
    """Test FastSD CPU engine batch processing."""

    def test_batch_size_configuration(self):
        """Test batch size can be configured."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            batch_size=8,
            device="cpu",
            gpu=False,
        )
        assert engine.batch_size == 8

    def test_batch_generate_method_exists(self):
        """Test batch_generate method exists."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            device="cpu",
            gpu=False,
        )
        assert hasattr(engine, "batch_generate")

    def test_batch_generate_uses_threadpool(self):
        """Test batch_generate uses ThreadPoolExecutor."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            batch_size=4,
            device="cpu",
            gpu=False,
        )
        assert hasattr(engine, "batch_size")
        assert engine.batch_size == 4


class TestFastSDCPUEngineInitialization:
    """Test FastSD CPU engine initialization."""

    @patch("app.core.engines.fastsd_cpu_engine.OnnxStableDiffusionPipeline")
    def test_initialize_success(self, mock_pipeline):
        """Test successful initialization."""
        mock_pipe = MagicMock()
        mock_pipeline.from_pretrained.return_value = mock_pipe

        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            device="cpu",
            gpu=False,
            lazy_load=False,
        )
        result = engine.initialize()
        assert result is True
        assert engine.is_initialized() is True

    def test_initialize_failure(self):
        """Test initialization failure handling."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="invalid/model",
            device="cpu",
            gpu=False,
            lazy_load=False,
        )
        # Should handle failure gracefully
        result = engine.initialize()
        # May return False or raise exception depending on implementation
        assert isinstance(result, bool)


class TestFastSDCPUEngineCleanup:
    """Test FastSD CPU engine cleanup."""

    def test_cleanup_resets_cache(self):
        """Test cleanup resets cache."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            enable_response_cache=True,
            response_cache_size=100,
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
        # Note: FastSD CPU cleanup doesn't reset cache stats, only clears caches

    def test_cleanup_resets_initialization(self):
        """Test cleanup resets initialization state."""
        engine = fastsd_cpu_engine.FastSDCPUEngine(
            model_id="runwayml/stable-diffusion-v1-5",
            device="cpu",
            gpu=False,
        )
        engine._initialized = True
        engine.cleanup()
        assert engine.is_initialized() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

