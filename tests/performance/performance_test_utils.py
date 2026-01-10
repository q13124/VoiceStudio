"""
Performance Test Utilities
Provides utilities and helpers for performance testing.
"""

import time
import statistics
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import logging

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a test."""

    name: str
    min_time: float
    max_time: float
    avg_time: float
    median_time: float
    p95_time: float
    p99_time: float
    iterations: int
    total_time: float
    memory_used_mb: Optional[float] = None
    cpu_percent: Optional[float] = None


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, name: str = "operation"):
        """
        Initialize performance timer.

        Args:
            name: Name of the operation being timed
        """
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing."""
        self.end_time = time.perf_counter()
        self.elapsed_time = self.end_time - self.start_time

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.elapsed_time is None:
            raise RuntimeError("Timer not stopped")
        return self.elapsed_time


class PerformanceBenchmark:
    """Benchmark utility for performance testing."""

    def __init__(self, name: str):
        """
        Initialize benchmark.

        Args:
            name: Benchmark name
        """
        self.name = name
        self.times: List[float] = []
        self.memory_samples: List[float] = []

    def run(
        self,
        func: Callable,
        *args,
        iterations: int = 10,
        warmup_iterations: int = 2,
        measure_memory: bool = False,
        **kwargs,
    ) -> PerformanceMetrics:
        """
        Run benchmark.

        Args:
            func: Function to benchmark
            *args: Function arguments
            iterations: Number of iterations
            warmup_iterations: Number of warmup iterations
            measure_memory: Whether to measure memory usage
            **kwargs: Function keyword arguments

        Returns:
            Performance metrics
        """
        # Warmup
        for _ in range(warmup_iterations):
            try:
                func(*args, **kwargs)
            except Exception:
                ...

        # Benchmark
        self.times.clear()
        self.memory_samples.clear()

        process = psutil.Process() if HAS_PSUTIL and measure_memory else None

        for _ in range(iterations):
            if process and measure_memory:
                mem_before = process.memory_info().rss / 1024 / 1024  # MB

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Benchmark iteration failed: {e}")
                continue
            elapsed = time.perf_counter() - start_time

            self.times.append(elapsed)

            if process and measure_memory:
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                self.memory_samples.append(mem_after - mem_before)

        if not self.times:
            raise RuntimeError("No successful iterations")

        # Calculate statistics
        sorted_times = sorted(self.times)
        memory_used = (
            statistics.mean(self.memory_samples) if self.memory_samples else None
        )

        return PerformanceMetrics(
            name=self.name,
            min_time=min(self.times),
            max_time=max(self.times),
            avg_time=statistics.mean(self.times),
            median_time=statistics.median(self.times),
            p95_time=sorted_times[int(len(sorted_times) * 0.95)]
            if len(sorted_times) > 0
            else 0,
            p99_time=sorted_times[int(len(sorted_times) * 0.99)]
            if len(sorted_times) > 0
            else 0,
            iterations=len(self.times),
            total_time=sum(self.times),
            memory_used_mb=memory_used,
        )

    def assert_performance(
        self,
        metrics: PerformanceMetrics,
        max_avg_time: Optional[float] = None,
        max_p95_time: Optional[float] = None,
        max_p99_time: Optional[float] = None,
    ):
        """
        Assert performance meets requirements.

        Args:
            metrics: Performance metrics
            max_avg_time: Maximum average time in seconds
            max_p95_time: Maximum P95 time in seconds
            max_p99_time: Maximum P99 time in seconds
        """
        if max_avg_time is not None:
            assert metrics.avg_time <= max_avg_time, \
                f"{self.name} average time {metrics.avg_time:.3f}s exceeds {max_avg_time:.3f}s"

        if max_p95_time is not None:
            assert metrics.p95_time <= max_p95_time, \
                f"{self.name} P95 time {metrics.p95_time:.3f}s exceeds {max_p95_time:.3f}s"

        if max_p99_time is not None:
            assert metrics.p99_time <= max_p99_time, \
                f"{self.name} P99 time {metrics.p99_time:.3f}s exceeds {max_p99_time:.3f}s"


class LoadTester:
    """Load testing utility."""

    def __init__(self, name: str = "load_test"):
        """
        Initialize load tester.

        Args:
            name: Test name
        """
        self.name = name
        self.results: List[Dict[str, Any]] = []

    def run_concurrent(
        self,
        func: Callable,
        *args,
        num_threads: int = 10,
        requests_per_thread: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run concurrent load test.

        Args:
            func: Function to test
            *args: Function arguments
            num_threads: Number of concurrent threads
            requests_per_thread: Requests per thread
            **kwargs: Function keyword arguments

        Returns:
            Load test results
        """
        import concurrent.futures

        def run_request():
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
            elapsed = time.perf_counter() - start
            return {
                "success": success,
                "elapsed": elapsed,
                "error": error,
            }

        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(run_request)
                for _ in range(num_threads * requests_per_thread)
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        total_time = time.perf_counter() - start_time

        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        elapsed_times = [r["elapsed"] for r in successful]

        return {
            "total_requests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "total_time": total_time,
            "requests_per_second": len(results) / total_time if total_time > 0 else 0,
            "avg_response_time": statistics.mean(elapsed_times) if elapsed_times else 0,
            "min_response_time": min(elapsed_times) if elapsed_times else 0,
            "max_response_time": max(elapsed_times) if elapsed_times else 0,
            "p95_response_time": sorted(elapsed_times)[int(len(elapsed_times) * 0.95)]
            if len(elapsed_times) > 0
            else 0,
        }


