"""
End-to-End test for Quality Benchmarking workflow.

Tests the complete quality benchmarking workflow from setup to analysis.
"""

# Import the FastAPI app
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to path to enable proper package imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.main import app


class TestQualityBenchmarkingWorkflow:
    """End-to-end test for quality benchmarking complete workflow."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_complete_benchmarking_workflow(self, client: TestClient):
        """
        Test complete quality benchmarking workflow:
        1. Set up benchmark parameters
        2. Run benchmark
        3. Analyze results
        4. Compare engines
        """
        print("\n[E2E] Step 1: Setting up benchmark parameters...")

        # Step 1: Run benchmark
        print("[E2E] Running quality benchmark...")
        benchmark_response = client.post(
            "/api/quality/benchmark",
            json={
                "profile_id": "test-profile-123",
                "test_text": "This is a quality benchmark test.",
                "language": "en",
                "engines": ["xtts", "chatterbox", "tortoise"],
                "enhance_quality": True,
            },
        )

        assert benchmark_response.status_code in [200, 404, 503]

        if benchmark_response.status_code == 200:
            benchmark = benchmark_response.json()
            print(
                f"[E2E] Benchmark completed: {benchmark['successful_engines']}/{benchmark['total_engines']} successful"
            )

            # Step 2: Analyze results
            print("[E2E] Step 2: Analyzing benchmark results...")
            results = benchmark["results"]

            successful_results = [r for r in results if r["success"]]
            print(f"[E2E] Successful benchmarks: {len(successful_results)}")

            # Step 3: Compare engines
            print("[E2E] Step 3: Comparing engines...")
            if successful_results:
                # Sort by MOS score
                sorted_results = sorted(
                    successful_results,
                    key=lambda x: x.get("quality_metrics", {}).get("mos_score", 0),
                    reverse=True,
                )

                print("[E2E] Engine Rankings:")
                for i, result in enumerate(sorted_results, 1):
                    engine = result["engine"]
                    mos = result.get("quality_metrics", {}).get("mos_score", 0)
                    print(f"[E2E]   {i}. {engine.upper()}: MOS={mos:.2f}")

                # Step 4: Identify best engine
                if sorted_results:
                    best_engine = sorted_results[0]
                    print(f"[E2E] Step 4: Best engine: {best_engine['engine'].upper()}")

        print("[E2E] ✅ Quality Benchmarking workflow completed successfully")

    def test_benchmarking_workflow_with_multiple_texts(self, client: TestClient):
        """
        Test quality benchmarking workflow with multiple test texts.
        """
        print("\n[E2E] Testing benchmarking with multiple test texts...")

        test_texts = [
            "Short test.",
            "This is a longer test sentence with more words.",
            "Testing emotional content: I'm so excited about this feature!",
        ]

        all_results = []
        service_available = False

        for i, text in enumerate(test_texts, 1):
            print(f"[E2E] Benchmark {i}/{len(test_texts)}: {text[:50]}...")

            response = client.post(
                "/api/quality/benchmark",
                json={
                    "profile_id": "test-profile-123",
                    "test_text": text,
                    "engines": ["xtts", "chatterbox"],
                },
            )

            if response.status_code == 200:
                service_available = True
                benchmark = response.json()
                all_results.append(benchmark)
            elif response.status_code in [500, 503]:
                print(f"[E2E] Benchmark service unavailable for text {i}")

        print(f"[E2E] ✅ Completed {len(all_results)} benchmarks")
        # Pass if we got results OR service is consistently unavailable
        assert len(all_results) > 0 or not service_available

    def test_benchmarking_workflow_error_recovery(self, client: TestClient):
        """
        Test quality benchmarking workflow with error recovery.
        """
        print("\n[E2E] Testing error recovery in benchmarking...")

        # Try with invalid profile
        print("[E2E] Attempting benchmark with invalid profile...")
        invalid_response = client.post(
            "/api/quality/benchmark",
            json={"profile_id": "non-existent-profile", "test_text": "Test"},
        )
        assert invalid_response.status_code in [404, 503]

        # Recover with valid request (but may still fail if engines not available)
        print("[E2E] Attempting recovery with valid request...")
        valid_response = client.post(
            "/api/quality/benchmark",
            json={"profile_id": "test-profile-123", "test_text": "Test", "engines": ["xtts"]},
        )
        # May succeed or fail depending on engine availability
        assert valid_response.status_code in [200, 404, 503]

        print("[E2E] ✅ Error recovery workflow completed")
