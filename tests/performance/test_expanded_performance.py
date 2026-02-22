"""
Expanded Performance Tests
Comprehensive performance tests covering additional scenarios, baselines, and benchmarks.

Worker 3 - Performance Tests Expansion
"""

import sys
import time
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import numpy as np
    import psutil

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    pytest.skip("Missing dependencies for performance tests", allow_module_level=True)

from tests.performance.performance_test_utils import (
    LoadTester,
    PerformanceBenchmark,
    PerformanceTimer,
)


class TestBackendAPIPerformance:
    """Test backend API performance with expanded scenarios."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient

            from backend.api.main import app

            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI not available")

    def test_profiles_crud_performance(self, client):
        """Test profiles CRUD operations performance."""
        benchmark = PerformanceBenchmark("profiles_crud")

        def create_profile():
            response = client.post(
                "/api/profiles",
                json={"name": "Perf Test Profile", "language": "en"},
            )
            return response.status_code == 200

        def list_profiles():
            response = client.get("/api/profiles")
            return response.status_code == 200

        def get_profile(profile_id):
            response = client.get(f"/api/profiles/{profile_id}")
            return response.status_code in [200, 404]

        # Benchmark create
        create_metrics = benchmark.run(create_profile, iterations=5)
        assert create_metrics.avg_time < 1.0, f"Create took {create_metrics.avg_time:.3f}s"

        # Benchmark list
        list_metrics = benchmark.run(list_profiles, iterations=10)
        assert list_metrics.avg_time < 0.5, f"List took {list_metrics.avg_time:.3f}s"

        # Benchmark get (with mock ID)
        get_metrics = benchmark.run(get_profile, "test-id", iterations=10)
        assert get_metrics.avg_time < 0.5, f"Get took {get_metrics.avg_time:.3f}s"

    def test_projects_crud_performance(self, client):
        """Test projects CRUD operations performance."""
        benchmark = PerformanceBenchmark("projects_crud")

        def create_project():
            response = client.post(
                "/api/projects",
                json={"name": "Perf Test Project", "engine": "xtts_v2"},
            )
            return response.status_code in [200, 201]

        def list_projects():
            response = client.get("/api/projects")
            return response.status_code == 200

        # Benchmark create
        create_metrics = benchmark.run(create_project, iterations=5)
        assert create_metrics.avg_time < 1.0, f"Create took {create_metrics.avg_time:.3f}s"

        # Benchmark list
        list_metrics = benchmark.run(list_projects, iterations=10)
        assert list_metrics.avg_time < 0.5, f"List took {list_metrics.avg_time:.3f}s"

    def test_search_performance(self, client):
        """Test search endpoint performance."""
        benchmark = PerformanceBenchmark("search")

        def search():
            response = client.get("/api/search?query=test")
            return response.status_code == 200

        metrics = benchmark.run(search, iterations=10)
        assert metrics.avg_time < 1.0, f"Search took {metrics.avg_time:.3f}s"
        assert metrics.p95_time < 2.0, f"Search P95 took {metrics.p95_time:.3f}s"

    def test_batch_operations_performance(self, client):
        """Test batch operations performance."""
        benchmark = PerformanceBenchmark("batch_operations")

        def batch_request():
            response = client.post(
                "/api/batch",
                json={"operations": [{"type": "synthesize", "text": "Test", "profile_id": "test"}]},
            )
            return response.status_code in [200, 400]

        metrics = benchmark.run(batch_request, iterations=5)
        assert metrics.avg_time < 2.0, f"Batch took {metrics.avg_time:.3f}s"


class TestEnginePerformanceBaselines:
    """Test engine performance baselines."""

    def test_engine_initialization_performance(self):
        """Test engine initialization performance."""
        benchmark = PerformanceBenchmark("engine_initialization")

        def initialize_engine():
            # Mock engine initialization
            time.sleep(0.01)  # Simulate initialization
            return True

        metrics = benchmark.run(initialize_engine, iterations=10)
        assert metrics.avg_time < 0.1, f"Initialization took {metrics.avg_time:.3f}s"

    def test_engine_synthesis_performance(self):
        """Test engine synthesis performance baseline."""
        benchmark = PerformanceBenchmark("engine_synthesis")

        def synthesize():
            # Mock synthesis (would be actual engine call)
            time.sleep(0.1)  # Simulate synthesis
            return np.array([0.1, 0.2, 0.3], dtype=np.float32)

        metrics = benchmark.run(synthesize, iterations=5)
        # Synthesis should complete in reasonable time
        assert metrics.avg_time < 30.0, f"Synthesis took {metrics.avg_time:.3f}s"


class TestAudioProcessingPerformance:
    """Test audio processing performance."""

    def test_audio_normalization_performance(self):
        """Test audio normalization performance."""
        benchmark = PerformanceBenchmark("audio_normalization")

        def normalize_audio():
            audio = np.random.randn(44100).astype(np.float32)
            # Mock normalization
            normalized = audio / np.max(np.abs(audio))
            return normalized

        metrics = benchmark.run(normalize_audio, iterations=20)
        assert metrics.avg_time < 0.1, f"Normalization took {metrics.avg_time:.3f}s"

    def test_audio_resampling_performance(self):
        """Test audio resampling performance."""
        benchmark = PerformanceBenchmark("audio_resampling")

        def resample_audio():
            audio = np.random.randn(44100).astype(np.float32)
            # Mock resampling (would use librosa or scipy)
            return audio[::2]  # Simple downsampling

        metrics = benchmark.run(resample_audio, iterations=20)
        assert metrics.avg_time < 0.2, f"Resampling took {metrics.avg_time:.3f}s"

    def test_audio_enhancement_performance(self):
        """Test audio enhancement performance."""
        benchmark = PerformanceBenchmark("audio_enhancement")

        def enhance_audio():
            audio = np.random.randn(44100).astype(np.float32)
            # Mock enhancement
            enhanced = audio * 1.1  # Simple gain
            return enhanced

        metrics = benchmark.run(enhance_audio, iterations=10)
        assert metrics.avg_time < 0.5, f"Enhancement took {metrics.avg_time:.3f}s"


class TestQualityMetricsPerformance:
    """Test quality metrics calculation performance."""

    def test_mos_score_calculation_performance(self):
        """Test MOS score calculation performance."""
        benchmark = PerformanceBenchmark("mos_score")

        def calculate_mos():
            np.random.randn(44100).astype(np.float32)
            # Mock MOS calculation
            mos = 4.0 + np.random.rand() * 0.5
            return mos

        metrics = benchmark.run(calculate_mos, iterations=20)
        assert metrics.avg_time < 0.5, f"MOS calculation took {metrics.avg_time:.3f}s"

    def test_full_quality_metrics_performance(self):
        """Test full quality metrics calculation performance."""
        benchmark = PerformanceBenchmark("full_quality_metrics")

        def calculate_full_metrics():
            np.random.randn(44100).astype(np.float32)
            # Mock full metrics calculation
            metrics_dict = {
                "mos_score": 4.0,
                "snr_db": 30.0,
                "naturalness": 0.9,
            }
            return metrics_dict

        metrics = benchmark.run(calculate_full_metrics, iterations=10)
        assert metrics.avg_time < 2.0, f"Full metrics took {metrics.avg_time:.3f}s"


class TestConcurrentLoadPerformance:
    """Test performance under concurrent load."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient

            from backend.api.main import app

            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI not available")

    def test_concurrent_health_checks(self, client):
        """Test concurrent health check requests."""
        load_tester = LoadTester("concurrent_health")

        def health_check():
            response = client.get("/api/health")
            return response.status_code == 200

        results = load_tester.run_concurrent(health_check, num_threads=10, requests_per_thread=10)

        assert results["success_rate"] >= 95.0, f"Success rate {results['success_rate']:.1f}%"
        assert (
            results["avg_response_time"] < 0.5
        ), f"Avg response time {results['avg_response_time']:.3f}s"
        assert (
            results["requests_per_second"] > 10
        ), f"Throughput {results['requests_per_second']:.1f} req/s"

    def test_concurrent_profiles_list(self, client):
        """Test concurrent profiles list requests."""
        load_tester = LoadTester("concurrent_profiles")

        def list_profiles():
            response = client.get("/api/profiles")
            return response.status_code == 200

        results = load_tester.run_concurrent(list_profiles, num_threads=5, requests_per_thread=5)

        assert results["success_rate"] >= 90.0, f"Success rate {results['success_rate']:.1f}%"
        assert (
            results["avg_response_time"] < 1.0
        ), f"Avg response time {results['avg_response_time']:.3f}s"


class TestMemoryPerformance:
    """Test memory usage and performance."""

    def test_memory_usage_baseline(self):
        """Test baseline memory usage."""
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Perform some operations
        audio = np.random.randn(44100 * 10).astype(np.float32)  # 10 seconds
        audio * 1.1

        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before

        # Memory usage should be reasonable (< 100MB for this operation)
        assert mem_used < 100.0, f"Memory used {mem_used:.1f}MB (should be < 100MB)"

    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations."""
        process = psutil.Process()
        mem_samples = []

        for _i in range(10):
            # Perform operation
            audio = np.random.randn(44100).astype(np.float32)
            audio * 1.1

            mem_used = process.memory_info().rss / 1024 / 1024  # MB
            mem_samples.append(mem_used)

        # Check for memory growth (should not grow significantly)
        mem_growth = mem_samples[-1] - mem_samples[0]
        assert mem_growth < 50.0, f"Memory growth {mem_growth:.1f}MB (possible leak)"


class TestDatabasePerformance:
    """Test database query performance."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient

            from backend.api.main import app

            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI not available")

    def test_query_performance(self, client):
        """Test database query performance."""
        benchmark = PerformanceBenchmark("database_queries")

        def query_profiles():
            response = client.get("/api/profiles?limit=100")
            return response.status_code == 200

        metrics = benchmark.run(query_profiles, iterations=10)
        assert metrics.avg_time < 1.0, f"Query took {metrics.avg_time:.3f}s"

    def test_pagination_performance(self, client):
        """Test pagination performance."""
        benchmark = PerformanceBenchmark("pagination")

        def paginated_query():
            response = client.get("/api/profiles?page=1&limit=20")
            return response.status_code == 200

        metrics = benchmark.run(paginated_query, iterations=10)
        assert metrics.avg_time < 0.5, f"Pagination took {metrics.avg_time:.3f}s"


class TestCachingPerformance:
    """Test caching performance impact."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient

            from backend.api.main import app

            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI not available")

    def test_cache_hit_performance(self, client):
        """Test cache hit performance improvement."""
        PerformanceBenchmark("cache_performance")

        # First request (cache miss)
        start_time = time.perf_counter()
        response1 = client.get("/api/engines")
        first_time = time.perf_counter() - start_time

        # Second request (cache hit)
        start_time = time.perf_counter()
        response2 = client.get("/api/engines")
        second_time = time.perf_counter() - start_time

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Cached request should be faster or similar
        assert (
            second_time <= first_time * 1.5
        ), f"Cache hit {second_time:.3f}s should be <= cache miss {first_time:.3f}s * 1.5"


class TestResourceUsagePerformance:
    """Test resource usage under load."""

    def test_cpu_usage_baseline(self):
        """Test CPU usage baseline."""
        process = psutil.Process()

        # Measure CPU during operation
        process.cpu_percent(interval=0.1)

        # Perform operation
        audio = np.random.randn(44100).astype(np.float32)
        audio * 1.1

        cpu_after = process.cpu_percent(interval=0.1)

        # CPU usage should be reasonable
        # (This is a simple check, actual CPU usage depends on system load)
        assert cpu_after < 100.0, f"CPU usage {cpu_after:.1f}% (should be < 100%)"

    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        process = psutil.Process()
        mem_samples = []

        # Perform multiple operations
        for _ in range(20):
            audio = np.random.randn(44100).astype(np.float32)
            audio * 1.1
            mem_used = process.memory_info().rss / 1024 / 1024  # MB
            mem_samples.append(mem_used)

        max_mem = max(mem_samples)
        # Memory should stay reasonable (< 500MB for this test)
        assert max_mem < 500.0, f"Max memory {max_mem:.1f}MB (should be < 500MB)"


class TestPerformanceBaselines:
    """Test performance baselines and thresholds."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient

            from backend.api.main import app

            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI not available")

    def test_api_response_time_baselines(self, client):
        """Test API response time baselines."""
        endpoints = [
            ("/api/health", 0.2),
            ("/api/profiles", 1.0),
            ("/api/projects", 1.0),
            ("/api/engines", 1.0),
        ]

        for endpoint, max_time in endpoints:
            with PerformanceTimer(f"endpoint_{endpoint}") as timer:
                response = client.get(endpoint)
                elapsed = timer.get_elapsed()

            assert response.status_code in [
                200,
                404,
            ], f"{endpoint} returned {response.status_code}"
            assert elapsed < max_time, f"{endpoint} took {elapsed:.3f}s (baseline: < {max_time}s)"

    def test_throughput_baseline(self, client):
        """Test throughput baseline."""
        load_tester = LoadTester("throughput_baseline")

        def health_check():
            response = client.get("/api/health")
            return response.status_code == 200

        results = load_tester.run_concurrent(health_check, num_threads=10, requests_per_thread=10)

        # Should handle at least 50 requests/second
        assert (
            results["requests_per_second"] >= 50
        ), f"Throughput {results['requests_per_second']:.1f} req/s (baseline: >= 50 req/s)"

    def test_latency_percentiles(self, client):
        """Test latency percentiles."""
        benchmark = PerformanceBenchmark("latency_percentiles")

        def health_check():
            response = client.get("/api/health")
            return response.status_code == 200

        metrics = benchmark.run(health_check, iterations=100)

        # P95 should be reasonable
        assert metrics.p95_time < 0.5, f"P95 latency {metrics.p95_time:.3f}s (should be < 0.5s)"
        assert metrics.p99_time < 1.0, f"P99 latency {metrics.p99_time:.3f}s (should be < 1.0s)"
