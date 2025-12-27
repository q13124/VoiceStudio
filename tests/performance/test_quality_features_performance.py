"""
Performance tests for quality testing and comparison features.

Tests response times, throughput, and resource usage for:
- A/B Testing
- Engine Recommendation
- Quality Benchmarking
- Quality Dashboard
"""

import time
from statistics import mean, median, stdev

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from api.main import app


class TestABTestingPerformance:
    """Performance tests for A/B Testing endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_ab_test_start_performance(self, client: TestClient):
        """Test A/B test start endpoint performance."""
        times = []
        
        for i in range(10):
            start_time = time.time()
            response = client.post(
                "/api/eval/abx/start",
                json={"items": [f"audio-{i}-1", f"audio-{i}-2"]}
            )
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            times.append(elapsed)
            assert response.status_code == 200
        
        avg_time = mean(times)
        median_time = median(times)
        max_time = max(times)
        
        print(f"\n[Performance] A/B Test Start:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Median: {median_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        
        # Performance baseline: should complete in < 500ms
        assert avg_time < 500, f"Average response time {avg_time:.2f}ms exceeds 500ms baseline"
    
    def test_ab_test_results_performance(self, client: TestClient):
        """Test A/B test results endpoint performance."""
        times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get("/api/eval/abx/results")
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
            assert response.status_code == 200
        
        avg_time = mean(times)
        median_time = median(times)
        
        print(f"\n[Performance] A/B Test Results:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Median: {median_time:.2f}ms")
        
        # Performance baseline: should complete in < 100ms
        assert avg_time < 100, f"Average response time {avg_time:.2f}ms exceeds 100ms baseline"
    
    def test_ab_test_concurrent_requests(self, client: TestClient):
        """Test A/B testing with concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.post(
                "/api/eval/abx/start",
                json={"items": ["audio-1", "audio-2"]}
            )
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n[Performance] A/B Test Concurrent (10 requests, 5 workers):")
        print(f"  Total time: {elapsed:.2f}ms")
        print(f"  Average per request: {elapsed/10:.2f}ms")
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)


class TestEngineRecommendationPerformance:
    """Performance tests for Engine Recommendation endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_recommendation_performance(self, client: TestClient):
        """Test engine recommendation endpoint performance."""
        times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get(
                "/api/quality/engine-recommendation",
                params={"target_tier": "standard"}
            )
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
            # May return 503 if quality optimization not available
            assert response.status_code in [200, 503]
        
        successful_times = [t for t in times if t < 1000]  # Filter out timeouts
        
        if successful_times:
            avg_time = mean(successful_times)
            median_time = median(successful_times)
            
            print(f"\n[Performance] Engine Recommendation:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Median: {median_time:.2f}ms")
            print(f"  Successful requests: {len(successful_times)}/10")
            
            # Performance baseline: should complete in < 200ms
            assert avg_time < 200, f"Average response time {avg_time:.2f}ms exceeds 200ms baseline"
    
    def test_recommendation_different_tiers(self, client: TestClient):
        """Test recommendation performance across different tiers."""
        tiers = ["fast", "standard", "high", "ultra"]
        tier_times = {}
        
        for tier in tiers:
            times = []
            for _ in range(5):
                start_time = time.time()
                response = client.get(
                    "/api/quality/engine-recommendation",
                    params={"target_tier": tier}
                )
                elapsed = (time.time() - start_time) * 1000
                times.append(elapsed)
            
            tier_times[tier] = mean(times)
            print(f"[Performance] Tier '{tier}': {tier_times[tier]:.2f}ms")
        
        # All tiers should have similar performance
        avg_all_tiers = mean(tier_times.values())
        print(f"\n[Performance] Average across all tiers: {avg_all_tiers:.2f}ms")


class TestQualityBenchmarkingPerformance:
    """Performance tests for Quality Benchmarking endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_benchmark_single_engine_performance(self, client: TestClient):
        """Test benchmarking performance with single engine."""
        times = []
        
        for _ in range(3):  # Fewer iterations due to longer execution time
            start_time = time.time()
            response = client.post(
                "/api/quality/benchmark",
                json={
                    "profile_id": "test-profile-123",
                    "test_text": "Short test.",
                    "engines": ["xtts"]
                }
            )
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
            # May return 404 or 503
            assert response.status_code in [200, 404, 503]
        
        successful_times = [t for t in times if t < 60000]  # Filter out timeouts (60s)
        
        if successful_times:
            avg_time = mean(successful_times)
            print(f"\n[Performance] Quality Benchmark (single engine):")
            print(f"  Average: {avg_time:.2f}ms ({avg_time/1000:.2f}s)")
            print(f"  Successful: {len(successful_times)}/3")
    
    def test_benchmark_multiple_engines_performance(self, client: TestClient):
        """Test benchmarking performance with multiple engines."""
        start_time = time.time()
        
        response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": "test-profile-123",
                "test_text": "Test.",
                "engines": ["xtts", "chatterbox", "tortoise"]
            }
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n[Performance] Quality Benchmark (3 engines):")
        print(f"  Total time: {elapsed:.2f}ms ({elapsed/1000:.2f}s)")
        print(f"  Status: {response.status_code}")
        
        # Benchmarking is expected to take longer
        # Baseline: should complete in < 120s for 3 engines
        if response.status_code == 200:
            assert elapsed < 120000, f"Benchmark time {elapsed/1000:.2f}s exceeds 120s baseline"


class TestQualityDashboardPerformance:
    """Performance tests for Quality Dashboard endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_dashboard_performance(self, client: TestClient):
        """Test quality dashboard endpoint performance."""
        times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get("/api/quality/dashboard")
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
            # May return 503 if quality optimization not available
            assert response.status_code in [200, 503]
        
        successful_times = [t for t in times if t < 1000]  # Filter out timeouts
        
        if successful_times:
            avg_time = mean(successful_times)
            median_time = median(successful_times)
            
            print(f"\n[Performance] Quality Dashboard:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Median: {median_time:.2f}ms")
            print(f"  Successful: {len(successful_times)}/10")
            
            # Performance baseline: should complete in < 300ms
            assert avg_time < 300, f"Average response time {avg_time:.2f}ms exceeds 300ms baseline"
    
    def test_dashboard_different_time_ranges(self, client: TestClient):
        """Test dashboard performance with different time ranges."""
        time_ranges = [7, 30, 90]
        range_times = {}
        
        for days in time_ranges:
            times = []
            for _ in range(5):
                start_time = time.time()
                response = client.get(
                    "/api/quality/dashboard",
                    params={"days": days}
                )
                elapsed = (time.time() - start_time) * 1000
                times.append(elapsed)
            
            range_times[days] = mean(times)
            print(f"[Performance] Dashboard ({days} days): {range_times[days]:.2f}ms")
        
        # Performance should be similar across time ranges
        avg_all_ranges = mean(range_times.values())
        print(f"\n[Performance] Average across all ranges: {avg_all_ranges:.2f}ms")


class TestConcurrentLoadPerformance:
    """Performance tests for concurrent load scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_concurrent_recommendations(self, client: TestClient):
        """Test concurrent engine recommendation requests."""
        import concurrent.futures
        
        def make_request():
            return client.get(
                "/api/quality/engine-recommendation",
                params={"target_tier": "standard"}
            )
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n[Performance] Concurrent Recommendations (20 requests, 10 workers):")
        print(f"  Total time: {elapsed:.2f}ms")
        print(f"  Average per request: {elapsed/20:.2f}ms")
        print(f"  Successful: {sum(1 for r in results if r.status_code == 200)}/20")
    
    def test_concurrent_dashboard_requests(self, client: TestClient):
        """Test concurrent dashboard requests."""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/quality/dashboard")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n[Performance] Concurrent Dashboard (10 requests, 5 workers):")
        print(f"  Total time: {elapsed:.2f}ms")
        print(f"  Average per request: {elapsed/10:.2f}ms")
        print(f"  Successful: {sum(1 for r in results if r.status_code == 200)}/10")

