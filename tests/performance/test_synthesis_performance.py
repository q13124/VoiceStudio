"""
Phase 9: Performance Tests
Task 9.7: Performance tests for synthesis operations.
"""

import asyncio
import statistics
import time

import pytest


@pytest.mark.slow
@pytest.mark.performance
class TestSynthesisPerformance:
    """Performance tests for synthesis operations."""

    @pytest.mark.asyncio
    async def test_synthesis_latency(self, test_client):
        """Test synthesis latency for short text."""
        request = {
            "text": "Hello, this is a short test.",
            "voice_id": "default",
        }

        latencies = []

        for _ in range(10):
            start = time.perf_counter()

            response = await test_client.post(
                "/api/v1/synthesis",
                json=request
            )

            end = time.perf_counter()

            if response.status_code == 404:
                pytest.skip("Synthesis endpoint not implemented")

            latencies.append((end - start) * 1000)  # Convert to ms

        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print("\nSynthesis Latency (10 runs):")
        print(f"  Average: {avg_latency:.2f} ms")
        print(f"  P95: {p95_latency:.2f} ms")
        print(f"  Min: {min(latencies):.2f} ms")
        print(f"  Max: {max(latencies):.2f} ms")

        # Performance assertions
        assert avg_latency < 5000, f"Average latency too high: {avg_latency}ms"

    @pytest.mark.asyncio
    async def test_synthesis_throughput(self, test_client):
        """Test synthesis throughput with concurrent requests."""
        request = {
            "text": "Throughput test sentence.",
            "voice_id": "default",
        }

        num_requests = 20

        async def make_request():
            start = time.perf_counter()
            await test_client.post(
                "/api/v1/synthesis",
                json=request
            )
            return time.perf_counter() - start

        # Check endpoint exists
        response = await test_client.post("/api/v1/synthesis", json=request)
        if response.status_code == 404:
            pytest.skip("Synthesis endpoint not implemented")

        # Run concurrent requests
        start = time.perf_counter()
        tasks = [make_request() for _ in range(num_requests)]
        durations = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start

        throughput = num_requests / total_time

        print(f"\nSynthesis Throughput ({num_requests} concurrent requests):")
        print(f"  Total time: {total_time:.2f} s")
        print(f"  Throughput: {throughput:.2f} requests/s")
        print(f"  Avg per request: {statistics.mean(durations) * 1000:.2f} ms")

    @pytest.mark.asyncio
    async def test_long_text_performance(self, test_client):
        """Test performance with long text."""
        # Generate long text (approx 1000 words)
        long_text = " ".join(["This is a test sentence."] * 200)

        request = {
            "text": long_text,
            "voice_id": "default",
        }

        start = time.perf_counter()
        response = await test_client.post(
            "/api/v1/synthesis",
            json=request
        )
        duration = time.perf_counter() - start

        if response.status_code == 404:
            pytest.skip("Synthesis endpoint not implemented")

        words_per_second = len(long_text.split()) / duration

        print("\nLong Text Performance:")
        print(f"  Text length: {len(long_text.split())} words")
        print(f"  Duration: {duration:.2f} s")
        print(f"  Words/second: {words_per_second:.2f}")


@pytest.mark.slow
@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint_latency(self, test_client):
        """Test health endpoint latency."""
        latencies = []

        for _ in range(100):
            start = time.perf_counter()
            response = await test_client.get("/health")
            end = time.perf_counter()

            if response.status_code == 200:
                latencies.append((end - start) * 1000)

        if not latencies:
            pytest.skip("Health endpoint not available")

        avg = statistics.mean(latencies)
        p99 = sorted(latencies)[int(len(latencies) * 0.99)]

        print("\nHealth Endpoint Latency (100 runs):")
        print(f"  Average: {avg:.2f} ms")
        print(f"  P99: {p99:.2f} ms")

        assert avg < 100, f"Average latency too high: {avg}ms"
        assert p99 < 500, f"P99 latency too high: {p99}ms"

    @pytest.mark.asyncio
    async def test_list_endpoints_performance(self, test_client):
        """Test list endpoints performance."""
        endpoints = [
            "/api/v1/voices",
            "/api/v1/engines",
            "/api/v1/projects",
        ]

        results = {}

        for endpoint in endpoints:
            latencies = []

            for _ in range(10):
                start = time.perf_counter()
                response = await test_client.get(endpoint)
                end = time.perf_counter()

                if response.status_code == 200:
                    latencies.append((end - start) * 1000)

            if latencies:
                results[endpoint] = {
                    "avg": statistics.mean(latencies),
                    "p95": sorted(latencies)[int(len(latencies) * 0.95)],
                }

        print("\nList Endpoints Performance:")
        for endpoint, stats in results.items():
            print(f"  {endpoint}:")
            print(f"    Avg: {stats['avg']:.2f} ms, P95: {stats['p95']:.2f} ms")


@pytest.mark.slow
@pytest.mark.performance
class TestMemoryPerformance:
    """Memory performance tests."""

    def test_memory_usage_baseline(self):
        """Test baseline memory usage."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        print("\nMemory Usage Baseline:")
        print(f"  RSS: {memory_info.rss / (1024 * 1024):.2f} MB")
        print(f"  VMS: {memory_info.vms / (1024 * 1024):.2f} MB")

        # Baseline should be under 500MB
        assert memory_info.rss < 500 * 1024 * 1024, "Memory usage too high"

    def test_memory_leak_detection(self):
        """Basic memory leak detection."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Force garbage collection
        gc.collect()

        initial_memory = process.memory_info().rss

        # Simulate some operations
        for _ in range(100):
            data = {"key": "value" * 1000}
            _ = str(data)

        gc.collect()

        final_memory = process.memory_info().rss

        increase = (final_memory - initial_memory) / (1024 * 1024)

        print("\nMemory Leak Detection:")
        print(f"  Initial: {initial_memory / (1024 * 1024):.2f} MB")
        print(f"  Final: {final_memory / (1024 * 1024):.2f} MB")
        print(f"  Increase: {increase:.2f} MB")

        # Should not increase by more than 10MB
        assert increase < 10, f"Possible memory leak: {increase:.2f} MB increase"
