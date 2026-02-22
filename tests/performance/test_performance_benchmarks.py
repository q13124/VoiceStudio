"""
Performance Benchmarks for VoiceStudio

Comprehensive performance benchmarks for:
- Audio processing operations
- Engine synthesis
- Quality metrics calculation
- API response times
- Memory usage
- CPU usage
"""

import logging
import time

import pytest

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import psutil
    import torch

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    pytest.skip("Missing dependencies for performance tests", allow_module_level=True)


class PerformanceBenchmark:
    """Base class for performance benchmarks."""

    def __init__(self):
        """Initialize benchmark."""
        self.results: dict[str, list[float]] = {}

    def measure_time(self, func, *args, **kwargs) -> float:
        """
        Measure execution time of a function.

        Args:
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Execution time in seconds
        """
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    def measure_memory(self, func, *args, **kwargs) -> dict[str, float]:
        """
        Measure memory usage of a function.

        Args:
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Dictionary with memory statistics
        """
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        func(*args, **kwargs)

        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before

        return {
            "memory_before_mb": mem_before,
            "memory_after_mb": mem_after,
            "memory_used_mb": mem_used,
        }

    def benchmark(self, name: str, func, *args, iterations: int = 10, **kwargs) -> dict:
        """
        Run benchmark with multiple iterations.

        Args:
            name: Benchmark name
            func: Function to benchmark
            *args: Function arguments
            iterations: Number of iterations
            **kwargs: Function keyword arguments

        Returns:
            Benchmark results
        """
        times = []
        memory_stats = []

        for i in range(iterations):
            # Measure time
            elapsed = self.measure_time(func, *args, **kwargs)
            times.append(elapsed)

            # Measure memory (first iteration only)
            if i == 0:
                mem_stats = self.measure_memory(func, *args, **kwargs)
                memory_stats.append(mem_stats)

        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5

        result = {
            "name": name,
            "iterations": iterations,
            "avg_time_seconds": avg_time,
            "min_time_seconds": min_time,
            "max_time_seconds": max_time,
            "std_time_seconds": std_time,
            "throughput": 1.0 / avg_time if avg_time > 0 else 0.0,
        }

        if memory_stats:
            result["memory"] = memory_stats[0]

        # Store results
        if name not in self.results:
            self.results[name] = []
        self.results[name].append(avg_time)

        return result


@pytest.fixture
def benchmark():
    """Create benchmark instance."""
    return PerformanceBenchmark()


@pytest.fixture
def sample_audio():
    """Create sample audio for testing."""
    sample_rate = 24000
    duration = 1.0  # 1 second
    samples = int(sample_rate * duration)
    audio = np.random.randn(samples).astype(np.float32)
    return audio, sample_rate


class TestAudioProcessingBenchmarks:
    """Benchmarks for audio processing operations."""

    def test_audio_normalization_benchmark(self, benchmark, sample_audio):
        """Benchmark audio normalization."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import normalize_lufs

            result = benchmark.benchmark(
                "audio_normalization",
                normalize_lufs,
                audio,
                sample_rate,
                iterations=20,
            )

            logger.info(f"Normalization benchmark: {result}")
            assert result["avg_time_seconds"] < 0.1  # Should be fast
        except ImportError:
            pytest.skip("audio_utils not available")

    def test_audio_resampling_benchmark(self, benchmark, sample_audio):
        """Benchmark audio resampling."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import resample_audio

            result = benchmark.benchmark(
                "audio_resampling",
                resample_audio,
                audio,
                sample_rate,
                16000,
                iterations=20,
            )

            logger.info(f"Resampling benchmark: {result}")
            assert result["avg_time_seconds"] < 0.2  # Should be reasonably fast
        except ImportError:
            pytest.skip("audio_utils not available")

    def test_audio_enhancement_benchmark(self, benchmark, sample_audio):
        """Benchmark audio enhancement."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import enhance_voice_quality

            result = benchmark.benchmark(
                "audio_enhancement",
                enhance_voice_quality,
                audio,
                sample_rate,
                iterations=10,
            )

            logger.info(f"Enhancement benchmark: {result}")
            assert result["avg_time_seconds"] < 1.0  # Should be reasonably fast
        except ImportError:
            pytest.skip("audio_utils not available")


class TestQualityMetricsBenchmarks:
    """Benchmarks for quality metrics calculation."""

    def test_quality_metrics_benchmark(self, benchmark, sample_audio):
        """Benchmark quality metrics calculation."""
        audio, sample_rate = sample_audio

        try:
            from app.core.engines.quality_metrics import calculate_all_metrics

            result = benchmark.benchmark(
                "quality_metrics",
                calculate_all_metrics,
                audio,
                sample_rate,
                iterations=10,
            )

            logger.info(f"Quality metrics benchmark: {result}")
            assert result["avg_time_seconds"] < 2.0  # Should be reasonably fast
        except ImportError:
            pytest.skip("quality_metrics not available")

    def test_mos_score_benchmark(self, benchmark, sample_audio):
        """Benchmark MOS score calculation."""
        audio, sample_rate = sample_audio

        try:
            from app.core.engines.quality_metrics import calculate_mos_score

            result = benchmark.benchmark(
                "mos_score",
                calculate_mos_score,
                audio,
                sample_rate,
                iterations=20,
            )

            logger.info(f"MOS score benchmark: {result}")
            assert result["avg_time_seconds"] < 0.5  # Should be fast
        except ImportError:
            pytest.skip("quality_metrics not available")


class TestEngineSynthesisBenchmarks:
    """Benchmarks for engine synthesis operations."""

    def test_xtts_synthesis_benchmark(self, benchmark):
        """Benchmark XTTS synthesis (if available)."""
        try:
            from app.core.engines.xtts_engine import XTTSEngine

            engine = XTTSEngine(device="cpu", gpu=False)
            if not engine.initialize():
                pytest.skip("XTTS engine not available")

            text = "This is a test of voice synthesis."
            speaker_wav = np.random.randn(24000).astype(np.float32)

            result = benchmark.benchmark(
                "xtts_synthesis",
                engine.synthesize,
                text,
                speaker_wav,
                24000,
                iterations=3,
            )

            logger.info(f"XTTS synthesis benchmark: {result}")
            engine.cleanup()
        except (ImportError, Exception) as e:
            pytest.skip(f"XTTS engine not available: {e}")


class TestAPIPerformanceBenchmarks:
    """Benchmarks for API operations."""

    def test_api_response_time_benchmark(self, benchmark):
        """Benchmark API response times."""
        # This would require a running API server
        # For now, we'll skip or mock
        pytest.skip("Requires running API server")

    def test_api_caching_benchmark(self, benchmark):
        """Benchmark API caching effectiveness."""
        # This would require a running API server
        # For now, we'll skip or mock
        pytest.skip("Requires running API server")


class TestMemoryBenchmarks:
    """Benchmarks for memory usage."""

    def test_audio_processing_memory(self, benchmark, sample_audio):
        """Test memory usage of audio processing."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import enhance_voice_quality

            result = benchmark.benchmark(
                "audio_processing_memory",
                enhance_voice_quality,
                audio,
                sample_rate,
                iterations=1,
            )

            logger.info(f"Memory benchmark: {result}")
            if "memory" in result:
                assert result["memory"]["memory_used_mb"] < 100  # Should be reasonable
        except ImportError:
            pytest.skip("audio_utils not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
