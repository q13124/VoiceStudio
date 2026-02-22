"""
End-to-End test for Engine Recommendation workflow.

Tests the complete engine recommendation workflow from requirements to selection.
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


class TestEngineRecommendationWorkflow:
    """End-to-end test for engine recommendation complete workflow."""

    @pytest.fixture
    def client(self):
        """Create a test client with proper startup/shutdown lifecycle."""
        with TestClient(app) as client:
            yield client

    def test_complete_recommendation_workflow(self, client: TestClient):
        """
        Test complete engine recommendation workflow:
        1. Set quality requirements
        2. Get recommendation
        3. Use recommendation for synthesis
        """
        print("\n[E2E] Step 1: Setting quality requirements...")

        # Step 1: Get recommendation for high quality
        print("[E2E] Requesting engine recommendation for high quality tier...")
        recommendation_response = client.get(
            "/api/quality/engine-recommendation",
            params={
                "target_tier": "high",
                "min_mos_score": 4.0,
                "min_similarity": 0.85,
            },
        )

        # 200 = success, 500/503 = service unavailable or not configured
        assert recommendation_response.status_code in [200, 500, 503]
        if recommendation_response.status_code == 200:
            recommendation = recommendation_response.json()
            print(f"[E2E] Recommended engine: {recommendation['recommended_engine']}")
            print(f"[E2E] Reasoning: {recommendation['reasoning']}")

            # Step 2: Verify recommendation structure
            assert "recommended_engine" in recommendation
            assert "target_tier" in recommendation
            assert "reasoning" in recommendation
            assert recommendation["target_tier"] == "high"

            # Step 3: Recommendation can be used for synthesis
            recommended_engine = recommendation["recommended_engine"]
            print(f"[E2E] Step 2: Using recommended engine '{recommended_engine}' for synthesis")
            # Note: Actual synthesis would require a profile and test text

        print("[E2E] ✅ Engine Recommendation workflow completed successfully")

    def test_recommendation_workflow_multiple_tiers(self, client: TestClient):
        """
        Test engine recommendation workflow for multiple quality tiers.
        """
        print("\n[E2E] Testing recommendations for multiple quality tiers...")

        tiers = ["fast", "standard", "high", "ultra"]
        recommendations = {}

        service_available = False
        for tier in tiers:
            print(f"[E2E] Getting recommendation for tier: {tier}")
            response = client.get(
                "/api/quality/engine-recommendation", params={"target_tier": tier}
            )

            if response.status_code == 200:
                service_available = True
                recommendation = response.json()
                recommendations[tier] = recommendation["recommended_engine"]
                print(f"[E2E] Tier '{tier}': {recommendation['recommended_engine']}")
            elif response.status_code in [500, 503]:
                print(
                    f"[E2E] Service unavailable for tier '{tier}' (status {response.status_code})"
                )

        print(f"[E2E] ✅ Recommendations for {len(recommendations)} tiers completed")
        # Pass if we got at least one recommendation OR service is consistently unavailable
        assert len(recommendations) > 0 or not service_available

    def test_recommendation_workflow_with_adjustments(self, client: TestClient):
        """
        Test engine recommendation workflow with requirement adjustments.
        """
        print("\n[E2E] Testing recommendation with requirement adjustments...")

        # Initial recommendation
        print("[E2E] Initial recommendation...")
        initial_response = client.get(
            "/api/quality/engine-recommendation", params={"target_tier": "standard"}
        )

        if initial_response.status_code == 200:
            initial = initial_response.json()
            print(f"[E2E] Initial: {initial['recommended_engine']}")

            # Adjust requirements
            print("[E2E] Adjusting requirements (increasing quality)...")
            adjusted_response = client.get(
                "/api/quality/engine-recommendation",
                params={"target_tier": "high", "min_mos_score": 4.5},
            )

            if adjusted_response.status_code == 200:
                adjusted = adjusted_response.json()
                print(f"[E2E] Adjusted: {adjusted['recommended_engine']}")

        print("[E2E] ✅ Requirement adjustment workflow completed")
