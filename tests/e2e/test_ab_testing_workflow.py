"""
End-to-End test for A/B Testing workflow.

Tests the complete A/B testing workflow from start to results analysis.
"""

import os
import sys
from pathlib import Path

# Set test mode BEFORE any backend imports
os.environ["VOICESTUDIO_TEST_MODE"] = "1"

import pytest
from fastapi.testclient import TestClient

# Add project root to path to enable proper package imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.main import app


class TestABTestingWorkflow:
    """End-to-end test for A/B testing complete workflow."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_complete_ab_testing_workflow(self, client: TestClient):
        """
        Test complete A/B testing workflow:
        1. Start A/B test
        2. Wait for results
        3. Retrieve results
        4. Analyze results
        """
        # Step 1: Start A/B test
        print("\n[E2E] Step 1: Starting A/B test...")
        start_response = client.post(
            "/api/eval/abx/start",
            json={"items": ["test-audio-1", "test-audio-2", "test-audio-3"]},
        )
        assert start_response.status_code == 200
        print(f"[E2E] A/B test started: {start_response.json()}")

        # Step 2: Retrieve results
        print("[E2E] Step 2: Retrieving A/B test results...")
        results_response = client.get("/api/eval/abx/results")
        assert results_response.status_code == 200
        results = results_response.json()
        assert isinstance(results, list)
        print(f"[E2E] Retrieved {len(results)} results")

        # Step 3: Analyze results
        print("[E2E] Step 3: Analyzing results...")
        if len(results) > 0:
            for i, result in enumerate(results, 1):
                assert "item" in result
                assert "mos" in result
                assert "pref" in result
                print(
                    f"[E2E] Result {i}: Item={result['item']}, MOS={result['mos']}, Pref={result['pref']}"
                )

        print("[E2E] ✅ A/B Testing workflow completed successfully")

    def test_ab_testing_with_multiple_runs(self, client: TestClient):
        """
        Test A/B testing workflow with multiple test runs.
        """
        print("\n[E2E] Testing multiple A/B test runs...")

        # Run multiple A/B tests
        for run_num in range(3):
            print(f"[E2E] Run {run_num + 1}/3")

            # Start test
            start_response = client.post(
                "/api/eval/abx/start",
                json={"items": [f"audio-{run_num}-1", f"audio-{run_num}-2"]},
            )
            assert start_response.status_code == 200

            # Get results
            results_response = client.get("/api/eval/abx/results")
            assert results_response.status_code == 200

        print("[E2E] ✅ Multiple A/B test runs completed")

    def test_ab_testing_error_recovery(self, client: TestClient):
        """
        Test A/B testing workflow with error recovery.
        """
        print("\n[E2E] Testing error recovery in A/B testing...")

        # Try invalid request
        invalid_response = client.post("/api/eval/abx/start", json={"items": []})  # Empty items
        # Should return validation error (400 for business logic, 422 for schema)
        assert invalid_response.status_code in [400, 422]

        # Recover with valid request
        valid_response = client.post("/api/eval/abx/start", json={"items": ["audio-1", "audio-2"]})
        assert valid_response.status_code == 200

        print("[E2E] ✅ Error recovery successful")
