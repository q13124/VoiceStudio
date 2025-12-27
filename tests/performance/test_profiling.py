"""
Performance Profiling for VoiceStudio

CPU and memory profiling for:
- Audio processing functions
- Engine operations
- Quality metrics
- API endpoints
"""

import logging
import time
from typing import Dict

import pytest

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import psutil

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    pytest.skip("Missing dependencies for profiling tests", allow_module_level=True)

# Try importing profiling tools
try:
    import cProfile
    import pstats
    from io import StringIO

    HAS_CPROFILE = True
except ImportError:
    HAS_CPROFILE = False

try:
    import memory_profiler

    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    logger.debug("memory_profiler not installed")


class CPUProfiler:
    """CPU profiling utilities."""

    def profile_function(self, func, *args, **kwargs) -> Dict:
        """
        Profile CPU usage of a function.

        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Profiling results
        """
        if not HAS_CPROFILE:
            # Fallback to simple timing
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            return {
                "time_seconds": end_time - start_time,
                "profiling_available": False,
            }

        # Use cProfile
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        # Get statistics
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions
        stats_output = stream.getvalue()

        return {
            "result": result,
            "stats": stats_output,
            "profiling_available": True,
        }

    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage percentage
        """
        return psutil.cpu_percent(interval=0.1)


class MemoryProfiler:
    """Memory profiling utilities."""

    def profile_function(self, func, *args, **kwargs) -> Dict:
        """
        Profile memory usage of a function.

        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Profiling results
        """
        process = psutil.Process()

        # Get memory before
        mem_before = process.memory_info()
        mem_before_mb = mem_before.rss / 1024 / 1024

        # Run function
        result = func(*args, **kwargs)

        # Get memory after
        mem_after = process.memory_info()
        mem_after_mb = mem_after.rss / 1024 / 1024

        # Calculate difference
        mem_used_mb = mem_after_mb - mem_before_mb

        return {
            "result": result,
            "memory_before_mb": mem_before_mb,
            "memory_after_mb": mem_after_mb,
            "memory_used_mb": mem_used_mb,
            "memory_before_bytes": mem_before.rss,
            "memory_after_bytes": mem_after.rss,
            "memory_used_bytes": mem_after.rss - mem_before.rss,
        }

    def get_memory_usage(self) -> Dict:
        """
        Get current memory usage.

        Returns:
            Memory usage dictionary
        """
        process = psutil.Process()
        mem_info = process.memory_info()
        mem_percent = process.memory_percent()

        return {
            "rss_mb": mem_info.rss / 1024 / 1024,
            "vms_mb": mem_info.vms / 1024 / 1024,
            "percent": mem_percent,
        }


@pytest.fixture
def cpu_profiler():
    """Create CPU profiler instance."""
    return CPUProfiler()


@pytest.fixture
def memory_profiler():
    """Create memory profiler instance."""
    return MemoryProfiler()


@pytest.fixture
def sample_audio():
    """Create sample audio for testing."""
    sample_rate = 24000
    duration = 1.0
    samples = int(sample_rate * duration)
    audio = np.random.randn(samples).astype(np.float32)
    return audio, sample_rate


class TestCPUProfiling:
    """CPU profiling tests."""

    def test_audio_processing_cpu_profile(self, cpu_profiler, sample_audio):
        """Profile CPU usage of audio processing."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import normalize_lufs

            result = cpu_profiler.profile_function(
                normalize_lufs, audio, sample_rate
            )

            logger.info(f"CPU profiling result: {result}")
            if result.get("profiling_available"):
                logger.info(f"Stats:\n{result['stats']}")
        except ImportError:
            pytest.skip("audio_utils not available")

    def test_quality_metrics_cpu_profile(self, cpu_profiler, sample_audio):
        """Profile CPU usage of quality metrics."""
        audio, sample_rate = sample_audio

        try:
            from app.core.engines.quality_metrics import calculate_all_metrics

            result = cpu_profiler.profile_function(
                calculate_all_metrics, audio, sample_rate
            )

            logger.info(f"CPU profiling result: {result}")
            if result.get("profiling_available"):
                logger.info(f"Stats:\n{result['stats']}")
        except ImportError:
            pytest.skip("quality_metrics not available")


class TestMemoryProfiling:
    """Memory profiling tests."""

    def test_audio_processing_memory_profile(
        self, memory_profiler, sample_audio
    ):
        """Profile memory usage of audio processing."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import enhance_voice_quality

            result = memory_profiler.profile_function(
                enhance_voice_quality, audio, sample_rate
            )

            logger.info(f"Memory profiling result: {result}")
            assert "memory_used_mb" in result
        except ImportError:
            pytest.skip("audio_utils not available")

    def test_quality_metrics_memory_profile(
        self, memory_profiler, sample_audio
    ):
        """Profile memory usage of quality metrics."""
        audio, sample_rate = sample_audio

        try:
            from app.core.engines.quality_metrics import calculate_all_metrics

            result = memory_profiler.profile_function(
                calculate_all_metrics, audio, sample_rate
            )

            logger.info(f"Memory profiling result: {result}")
            assert "memory_used_mb" in result
        except ImportError:
            pytest.skip("quality_metrics not available")


class TestSystemProfiling:
    """System-wide profiling tests."""

    def test_system_cpu_usage(self, cpu_profiler):
        """Test system CPU usage."""
        cpu_usage = cpu_profiler.get_cpu_usage()
        logger.info(f"System CPU usage: {cpu_usage}%")
        assert 0 <= cpu_usage <= 100

    def test_system_memory_usage(self, memory_profiler):
        """Test system memory usage."""
        mem_usage = memory_profiler.get_memory_usage()
        logger.info(f"System memory usage: {mem_usage}")
        assert "rss_mb" in mem_usage
        assert "percent" in mem_usage


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

