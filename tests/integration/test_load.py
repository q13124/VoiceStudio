"""
VoiceStudio Load Tests.

Tests system behavior under load:
- Concurrent API requests
- Sustained traffic patterns
- Resource usage under load
- Degradation characteristics
- Recovery after load
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import statistics
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Any

import pytest

try:
    import requests
except ImportError:
    requests = None
    pytest.skip("requests not installed", allow_module_level=True)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8001")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/load"))

# Load test configuration
LOAD_CONFIG = {
    "light": {"concurrent": 5, "requests_per_worker": 10, "delay_ms": 100},
    "medium": {"concurrent": 10, "requests_per_worker": 20, "delay_ms": 50},
    "heavy": {"concurrent": 25, "requests_per_worker": 50, "delay_ms": 10},
    "stress": {"concurrent": 50, "requests_per_worker": 100, "delay_ms": 0},
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pytestmark = [
    pytest.mark.load,
    pytest.mark.integration,
    pytest.mark.slow,
]


@dataclass
class RequestResult:
    """Result of a single HTTP request."""
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    success: bool
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    thread_id: int = 0


@dataclass
class LoadTestResult:
    """Result of a load test."""
    test_name: str
    config: dict
    start_time: datetime
    end_time: datetime
    results: list[RequestResult] = field(default_factory=list)

    @property
    def total_requests(self) -> int:
        return len(self.results)

    @property
    def successful_requests(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed_requests(self) -> int:
        return self.total_requests - self.successful_requests

    @property
    def success_rate(self) -> float:
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    @property
    def requests_per_second(self) -> float:
        return self.total_requests / self.duration_seconds if self.duration_seconds > 0 else 0

    def get_latency_stats(self) -> dict:
        """Get latency statistics."""
        successful = [r.duration_ms for r in self.results if r.success]

        if not successful:
            return {"count": 0}

        return {
            "count": len(successful),
            "min_ms": min(successful),
            "max_ms": max(successful),
            "mean_ms": statistics.mean(successful),
            "median_ms": statistics.median(successful),
            "p95_ms": sorted(successful)[int(len(successful) * 0.95)] if len(successful) > 1 else successful[0],
            "p99_ms": sorted(successful)[int(len(successful) * 0.99)] if len(successful) > 1 else successful[0],
            "stdev_ms": statistics.stdev(successful) if len(successful) > 1 else 0,
        }


@pytest.fixture
def api_client():
    """Create API client."""
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        def timed_request(self, method: str, path: str, **kwargs) -> RequestResult:
            """Execute timed HTTP request."""
            start = time.perf_counter()

            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{path}", **kwargs)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{path}", **kwargs)
                else:
                    response = requests.request(method, f"{self.base_url}{path}", **kwargs)

                duration_ms = (time.perf_counter() - start) * 1000

                return RequestResult(
                    endpoint=path,
                    method=method,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    success=response.status_code < 500,
                    thread_id=threading.current_thread().ident,
                )
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000

                return RequestResult(
                    endpoint=path,
                    method=method,
                    status_code=0,
                    duration_ms=duration_ms,
                    success=False,
                    error=str(e),
                    thread_id=threading.current_thread().ident,
                )

    return APIClient(BACKEND_URL)


@pytest.fixture
def backend_available(api_client):
    """Check if backend is available."""
    result = api_client.timed_request("GET", "/api/health", timeout=5)
    if not result.success:
        pytest.skip("Backend not available")
    return True


# Critical endpoints for load testing
CRITICAL_ENDPOINTS = [
    ("GET", "/api/health", None),
    ("GET", "/api/voice/engines", None),
    ("GET", "/api/profiles", None),
    ("GET", "/api/settings", None),
    ("GET", "/api/jobs", None),
    ("GET", "/api/audio/formats", None),
]


def worker_function(
    client,
    endpoint_config: tuple[str, str, Any],
    num_requests: int,
    delay_ms: float,
    results_queue: Queue,
):
    """Worker function for concurrent load testing."""
    method, path, data = endpoint_config

    for _ in range(num_requests):
        kwargs = {"timeout": 30}
        if data:
            kwargs["json"] = data

        result = client.timed_request(method, path, **kwargs)
        results_queue.put(result)

        if delay_ms > 0:
            time.sleep(delay_ms / 1000)


def run_load_test(
    api_client,
    test_name: str,
    endpoint_config: tuple[str, str, Any],
    concurrent_workers: int,
    requests_per_worker: int,
    delay_ms: float,
) -> LoadTestResult:
    """Run a load test."""
    results_queue = Queue()

    config = {
        "concurrent_workers": concurrent_workers,
        "requests_per_worker": requests_per_worker,
        "delay_ms": delay_ms,
        "endpoint": endpoint_config[1],
        "method": endpoint_config[0],
    }

    start_time = datetime.now()

    # Create thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
        # Submit worker tasks
        futures = [
            executor.submit(
                worker_function,
                api_client,
                endpoint_config,
                requests_per_worker,
                delay_ms,
                results_queue,
            )
            for _ in range(concurrent_workers)
        ]

        # Wait for completion
        concurrent.futures.wait(futures)

    end_time = datetime.now()

    # Collect results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    return LoadTestResult(
        test_name=test_name,
        config=config,
        start_time=start_time,
        end_time=end_time,
        results=results,
    )


class TestLightLoad:
    """Light load tests - basic concurrency."""

    def test_health_light_load(self, api_client, backend_available):
        """Test health endpoint under light load."""
        config = LOAD_CONFIG["light"]

        result = run_load_test(
            api_client,
            "health_light",
            ("GET", "/api/health", None),
            concurrent_workers=config["concurrent"],
            requests_per_worker=config["requests_per_worker"],
            delay_ms=config["delay_ms"],
        )

        print("\nLight Load - Health Endpoint:")
        print(f"  Total requests: {result.total_requests}")
        print(f"  Success rate: {result.success_rate * 100:.1f}%")
        print(f"  Duration: {result.duration_seconds:.2f}s")
        print(f"  RPS: {result.requests_per_second:.1f}")

        stats = result.get_latency_stats()
        if stats["count"] > 0:
            print(f"  Latency - Mean: {stats['mean_ms']:.0f}ms, P95: {stats['p95_ms']:.0f}ms")

        assert result.success_rate > 0.95, f"Success rate too low: {result.success_rate}"

    def test_multiple_endpoints_light_load(self, api_client, backend_available):
        """Test multiple endpoints under light load."""
        config = LOAD_CONFIG["light"]
        results = []

        for endpoint_config in CRITICAL_ENDPOINTS:
            result = run_load_test(
                api_client,
                f"light_{endpoint_config[1].replace('/', '_')}",
                endpoint_config,
                concurrent_workers=config["concurrent"],
                requests_per_worker=config["requests_per_worker"] // 2,  # Fewer per endpoint
                delay_ms=config["delay_ms"],
            )
            results.append(result)

        print("\nLight Load - Multiple Endpoints:")
        for r in results:
            print(f"  {r.config['endpoint']}: {r.success_rate*100:.0f}% success, {r.requests_per_second:.1f} RPS")

        # All should have high success rate
        for r in results:
            assert r.success_rate > 0.90, f"{r.config['endpoint']} success rate too low"


class TestMediumLoad:
    """Medium load tests - moderate concurrency."""

    def test_health_medium_load(self, api_client, backend_available):
        """Test health endpoint under medium load."""
        config = LOAD_CONFIG["medium"]

        result = run_load_test(
            api_client,
            "health_medium",
            ("GET", "/api/health", None),
            concurrent_workers=config["concurrent"],
            requests_per_worker=config["requests_per_worker"],
            delay_ms=config["delay_ms"],
        )

        print("\nMedium Load - Health Endpoint:")
        print(f"  Total requests: {result.total_requests}")
        print(f"  Success rate: {result.success_rate * 100:.1f}%")
        print(f"  RPS: {result.requests_per_second:.1f}")

        stats = result.get_latency_stats()
        if stats["count"] > 0:
            print(f"  Latency - Mean: {stats['mean_ms']:.0f}ms, P95: {stats['p95_ms']:.0f}ms, P99: {stats['p99_ms']:.0f}ms")

        assert result.success_rate > 0.90, f"Success rate too low: {result.success_rate}"


class TestHeavyLoad:
    """Heavy load tests - high concurrency."""

    @pytest.mark.slow
    def test_health_heavy_load(self, api_client, backend_available):
        """Test health endpoint under heavy load."""
        config = LOAD_CONFIG["heavy"]

        result = run_load_test(
            api_client,
            "health_heavy",
            ("GET", "/api/health", None),
            concurrent_workers=config["concurrent"],
            requests_per_worker=config["requests_per_worker"],
            delay_ms=config["delay_ms"],
        )

        print("\nHeavy Load - Health Endpoint:")
        print(f"  Total requests: {result.total_requests}")
        print(f"  Success rate: {result.success_rate * 100:.1f}%")
        print(f"  RPS: {result.requests_per_second:.1f}")

        stats = result.get_latency_stats()
        if stats["count"] > 0:
            print(f"  Latency - Mean: {stats['mean_ms']:.0f}ms, P95: {stats['p95_ms']:.0f}ms")

        # Under heavy load, accept lower success rate
        assert result.success_rate > 0.80, f"Success rate too low: {result.success_rate}"


class TestSustainedLoad:
    """Sustained load tests - extended duration."""

    @pytest.mark.slow
    def test_sustained_light_load(self, api_client, backend_available):
        """Test sustained light load over 30 seconds."""
        duration_seconds = 30
        requests_per_second = 5

        results = []
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            result = api_client.timed_request("GET", "/api/health", timeout=10)
            results.append(result)
            time.sleep(1 / requests_per_second)

        successful = [r for r in results if r.success]

        print(f"\nSustained Load ({duration_seconds}s):")
        print(f"  Total requests: {len(results)}")
        print(f"  Success rate: {len(successful)/len(results)*100:.1f}%")

        if successful:
            durations = [r.duration_ms for r in successful]
            print(f"  Latency - Mean: {statistics.mean(durations):.0f}ms")

            # Check for degradation over time
            first_half = durations[:len(durations)//2]
            second_half = durations[len(durations)//2:]

            if first_half and second_half:
                degradation = statistics.mean(second_half) - statistics.mean(first_half)
                print(f"  Degradation: {degradation:.0f}ms")

        assert len(successful) / len(results) > 0.95


class TestSpikeLoad:
    """Spike load tests - sudden traffic increase."""

    def test_spike_recovery(self, api_client, backend_available):
        """Test recovery after traffic spike."""
        # Baseline measurement
        baseline_result = api_client.timed_request("GET", "/api/health", timeout=10)
        baseline_latency = baseline_result.duration_ms

        # Generate spike
        spike_result = run_load_test(
            api_client,
            "spike",
            ("GET", "/api/health", None),
            concurrent_workers=20,
            requests_per_worker=10,
            delay_ms=0,
        )

        # Wait for recovery
        time.sleep(2)

        # Post-spike measurement
        recovery_results = []
        for _ in range(5):
            result = api_client.timed_request("GET", "/api/health", timeout=10)
            recovery_results.append(result)
            time.sleep(0.2)

        successful_recovery = [r for r in recovery_results if r.success]

        print("\nSpike Recovery Test:")
        print(f"  Baseline latency: {baseline_latency:.0f}ms")
        print(f"  Spike success rate: {spike_result.success_rate*100:.1f}%")

        if successful_recovery:
            recovery_latency = statistics.mean([r.duration_ms for r in successful_recovery])
            print(f"  Recovery latency: {recovery_latency:.0f}ms")

            # Should recover to near baseline
            assert recovery_latency < baseline_latency * 2, "System did not recover from spike"


class TestResourceUsageUnderLoad:
    """Test resource usage during load."""

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
    def test_memory_under_load(self, api_client, backend_available):
        """Test memory usage during load test."""
        # Find backend process
        backend_pid = None
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'uvicorn' in cmdline or 'fastapi' in cmdline.lower():
                    backend_pid = proc.info['pid']
                    break
            except Exception:
                continue

        if not backend_pid:
            print("Backend process not found - skipping memory test")
            return

        process = psutil.Process(backend_pid)
        initial_memory = process.memory_info().rss / (1024 * 1024)

        # Run load test
        config = LOAD_CONFIG["medium"]
        run_load_test(
            api_client,
            "memory_test",
            ("GET", "/api/health", None),
            concurrent_workers=config["concurrent"],
            requests_per_worker=config["requests_per_worker"],
            delay_ms=config["delay_ms"],
        )

        final_memory = process.memory_info().rss / (1024 * 1024)
        memory_increase = final_memory - initial_memory

        print("\nMemory Usage Under Load:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")

        # Memory should not increase dramatically
        assert memory_increase < 200, f"Memory increase too high: {memory_increase} MB"


class TestLoadReport:
    """Generate load test report."""

    def test_generate_load_report(self, api_client, backend_available):
        """Generate comprehensive load test report."""
        all_results = []

        # Run tests at different load levels
        for level_name in ["light", "medium"]:
            config = LOAD_CONFIG[level_name]

            for endpoint_config in CRITICAL_ENDPOINTS[:3]:  # First 3 endpoints
                result = run_load_test(
                    api_client,
                    f"{level_name}_{endpoint_config[1]}",
                    endpoint_config,
                    concurrent_workers=config["concurrent"],
                    requests_per_worker=config["requests_per_worker"] // 2,
                    delay_ms=config["delay_ms"],
                )
                all_results.append(result)

        # Generate report
        print("\n" + "=" * 60)
        print("LOAD TEST REPORT")
        print("=" * 60)

        for result in all_results:
            print(f"\n{result.test_name}:")
            print(f"  Config: {result.config['concurrent_workers']} workers × {result.config['requests_per_worker']} requests")
            print(f"  Total: {result.total_requests} requests in {result.duration_seconds:.2f}s")
            print(f"  Success: {result.success_rate * 100:.1f}%")
            print(f"  RPS: {result.requests_per_second:.1f}")

            stats = result.get_latency_stats()
            if stats["count"] > 0:
                print(f"  Latency: mean={stats['mean_ms']:.0f}ms, p95={stats['p95_ms']:.0f}ms")

        # Save JSON report
        report_path = OUTPUT_DIR / "load_test_report.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "tests": [
                {
                    "name": r.test_name,
                    "config": r.config,
                    "total_requests": r.total_requests,
                    "success_rate": r.success_rate,
                    "duration_seconds": r.duration_seconds,
                    "requests_per_second": r.requests_per_second,
                    "latency_stats": r.get_latency_stats(),
                }
                for r in all_results
            ],
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
