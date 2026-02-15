"""
Load and Stress Testing for VoiceStudio

Tests system behavior under:
- High load conditions
- Concurrent requests
- Resource exhaustion
- Stress scenarios
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import psutil

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    pytest.skip("Missing dependencies for load tests", allow_module_level=True)


class LoadTester:
    """Load testing utilities."""

    def __init__(self):
        """Initialize load tester."""
        self.results: dict[str, list] = {}

    def run_concurrent_requests(
        self, func, args_list: list, max_workers: int = 10
    ) -> dict:
        """
        Run concurrent requests.

        Args:
            func: Function to execute
            args_list: List of argument tuples
            max_workers: Maximum concurrent workers

        Returns:
            Results dictionary
        """
        start_time = time.time()
        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(func, *args): args for args in args_list
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    errors.append(str(e))
                    logger.error(f"Request failed: {e}")

        end_time = time.time()
        total_time = end_time - start_time

        return {
            "total_requests": len(args_list),
            "successful_requests": len(results),
            "failed_requests": len(errors),
            "total_time_seconds": total_time,
            "requests_per_second": len(args_list) / total_time if total_time > 0 else 0,
            "errors": errors[:10],  # First 10 errors
        }

    def stress_test(
        self, func, args, duration_seconds: int = 60, max_workers: int = 20
    ) -> dict:
        """
        Run stress test for specified duration.

        Args:
            func: Function to stress test
            args: Function arguments
            duration_seconds: Test duration
            max_workers: Maximum concurrent workers

        Returns:
            Stress test results
        """
        start_time = time.time()
        request_count = 0
        error_count = 0
        results = []

        def run_request():
            nonlocal request_count, error_count
            try:
                result = func(*args)
                request_count += 1
                return result
            except Exception as e:
                error_count += 1
                logger.error(f"Stress test error: {e}")
                return None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while time.time() - start_time < duration_seconds:
                futures = [
                    executor.submit(run_request) for _ in range(max_workers)
                ]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        results.append(result)

        end_time = time.time()
        total_time = end_time - start_time

        return {
            "duration_seconds": total_time,
            "total_requests": request_count,
            "failed_requests": error_count,
            "requests_per_second": request_count / total_time if total_time > 0 else 0,
            "success_rate": (
                (request_count - error_count) / request_count
                if request_count > 0
                else 0.0
            ),
        }


@pytest.fixture
def load_tester():
    """Create load tester instance."""
    return LoadTester()


@pytest.fixture
def sample_audio():
    """Create sample audio for testing."""
    sample_rate = 24000
    duration = 1.0
    samples = int(sample_rate * duration)
    audio = np.random.randn(samples).astype(np.float32)
    return audio, sample_rate


class TestLoadTesting:
    """Load testing scenarios."""

    def test_concurrent_audio_processing(self, load_tester, sample_audio):
        """Test concurrent audio processing."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import normalize_lufs

            # Create multiple requests
            args_list = [(audio, sample_rate) for _ in range(50)]

            result = load_tester.run_concurrent_requests(
                normalize_lufs, args_list, max_workers=10
            )

            logger.info(f"Concurrent processing result: {result}")
            assert result["successful_requests"] > 0
            assert result["requests_per_second"] > 0
        except ImportError:
            pytest.skip("audio_utils not available")

    def test_concurrent_quality_metrics(self, load_tester, sample_audio):
        """Test concurrent quality metrics calculation."""
        audio, sample_rate = sample_audio

        try:
            from app.core.engines.quality_metrics import calculate_all_metrics

            # Create multiple requests
            args_list = [(audio, sample_rate) for _ in range(20)]

            result = load_tester.run_concurrent_requests(
                calculate_all_metrics, args_list, max_workers=5
            )

            logger.info(f"Concurrent quality metrics result: {result}")
            assert result["successful_requests"] > 0
        except ImportError:
            pytest.skip("quality_metrics not available")


class TestStressTesting:
    """Stress testing scenarios."""

    @pytest.mark.slow
    def test_audio_processing_stress(self, load_tester, sample_audio):
        """Stress test audio processing."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import normalize_lufs

            result = load_tester.stress_test(
                normalize_lufs,
                (audio, sample_rate),
                duration_seconds=30,
                max_workers=10,
            )

            logger.info(f"Stress test result: {result}")
            assert result["total_requests"] > 0
            assert result["success_rate"] > 0.8  # At least 80% success
        except ImportError:
            pytest.skip("audio_utils not available")

    @pytest.mark.slow
    def test_memory_stress(self, load_tester, sample_audio):
        """Stress test memory usage."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import enhance_voice_quality

            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB

            # Run stress test
            result = load_tester.stress_test(
                enhance_voice_quality,
                (audio, sample_rate),
                duration_seconds=30,
                max_workers=5,
            )

            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_used = mem_after - mem_before

            logger.info(f"Memory stress test: {result}, Memory used: {mem_used}MB")
            assert result["total_requests"] > 0
            # Memory should not grow excessively
            assert mem_used < 500  # Less than 500MB growth
        except ImportError:
            pytest.skip("audio_utils not available")


class TestResourceExhaustion:
    """Test system behavior under resource exhaustion."""

    def test_cpu_exhaustion(self, load_tester, sample_audio):
        """Test behavior under CPU load."""
        audio, sample_rate = sample_audio

        try:
            from app.core.audio.audio_utils import normalize_lufs

            # Create many concurrent requests
            args_list = [(audio, sample_rate) for _ in range(100)]

            result = load_tester.run_concurrent_requests(
                normalize_lufs, args_list, max_workers=50
            )

            logger.info(f"CPU exhaustion test: {result}")
            # System should still handle requests (maybe slower)
            assert result["successful_requests"] > 0
        except ImportError:
            pytest.skip("audio_utils not available")

    def test_memory_pressure(self, load_tester):
        """Test behavior under memory pressure."""
        # Create large audio arrays
        large_audio = np.random.randn(24000 * 10).astype(np.float32)  # 10 seconds

        try:
            from app.core.audio.audio_utils import normalize_lufs

            args_list = [(large_audio, 24000) for _ in range(20)]

            result = load_tester.run_concurrent_requests(
                normalize_lufs, args_list, max_workers=5
            )

            logger.info(f"Memory pressure test: {result}")
            assert result["successful_requests"] > 0
        except ImportError:
            pytest.skip("audio_utils not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

