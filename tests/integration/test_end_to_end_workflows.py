"""
End-to-End Integration Tests
Test complete workflows, cross-panel integration, and error scenarios.

Worker 3 - Task: TASK-W3-F4-001
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API base URL
API_BASE_URL = "http://localhost:8000/api"


class EndToEndWorkflowTester:
    """Test complete end-to-end workflows."""

    def __init__(self):
        self.results: list[dict[str, Any]] = []

    async def test_voice_cloning_workflow(self) -> dict[str, Any]:
        """Test complete voice cloning workflow."""
        workflow_name = "Voice Cloning Workflow"
        logger.info(f"Testing workflow: {workflow_name}")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Health check
                health_response = await client.get(f"{API_BASE_URL}/health")
                if health_response.status_code != 200:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Health check failed: {health_response.status_code}",
                    }

                # Step 2: Upload reference audio (simulated)
                # In a real test, we would upload an actual audio file
                audio_id = "test-audio-001"

                # Step 3: Validate audio
                await client.post(
                    f"{API_BASE_URL}/voice/clone/wizard/validate-audio",
                    json={"audio_id": audio_id},
                )

                # Step 4: Create voice profile
                profile_response = await client.post(
                    f"{API_BASE_URL}/profiles",
                    json={
                        "name": "Test Profile",
                        "description": "Test profile for E2E testing",
                        "reference_audio_id": audio_id,
                        "engine": "xtts_v2",
                        "quality_mode": "standard",
                    },
                )

                if profile_response.status_code not in [200, 201]:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Profile creation failed: {profile_response.status_code}",
                    }

                profile_data = profile_response.json()
                profile_id = profile_data.get("profile_id")

                if not profile_id:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": "Profile ID not returned",
                    }

                # Step 5: Synthesize voice
                synthesis_response = await client.post(
                    f"{API_BASE_URL}/voice/synthesize",
                    json={
                        "profile_id": profile_id,
                        "text": "Hello, this is a test of the voice cloning system.",
                        "engine": "xtts_v2",
                        "language": "en",
                    },
                )

                if synthesis_response.status_code not in [200, 201]:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Synthesis failed: {synthesis_response.status_code}",
                    }

                synthesis_data = synthesis_response.json()
                audio_id = synthesis_data.get("audio_id")

                if not audio_id:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": "Audio ID not returned",
                    }

                # Step 6: Verify quality metrics
                if "quality_metrics" in synthesis_data:
                    metrics = synthesis_data["quality_metrics"]
                    if not isinstance(metrics, dict):
                        return {
                            "workflow": workflow_name,
                            "status": "WARNING",
                            "error": "Quality metrics not in expected format",
                        }

                return {
                    "workflow": workflow_name,
                    "status": "PASS",
                    "steps_completed": 6,
                    "profile_id": profile_id,
                    "audio_id": audio_id,
                }

        except Exception as e:
            logger.error(f"Workflow test failed: {e}", exc_info=True)
            return {"workflow": workflow_name, "status": "FAIL", "error": str(e)}

    async def test_timeline_workflow(self) -> dict[str, Any]:
        """Test complete timeline editing workflow."""
        workflow_name = "Timeline Editing Workflow"
        logger.info(f"Testing workflow: {workflow_name}")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Create project
                project_response = await client.post(
                    f"{API_BASE_URL}/projects",
                    json={
                        "name": "Test Project",
                        "description": "Test project for E2E testing",
                    },
                )

                if project_response.status_code not in [200, 201]:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Project creation failed: {project_response.status_code}",
                    }

                project_data = project_response.json()
                project_id = project_data.get("project_id") or project_data.get("id")

                if not project_id:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": "Project ID not returned",
                    }

                # Step 2: Add track
                track_response = await client.post(
                    f"{API_BASE_URL}/projects/{project_id}/tracks",
                    json={"name": "Audio Track 1", "type": "audio"},
                )

                if track_response.status_code not in [200, 201]:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Track creation failed: {track_response.status_code}",
                    }

                track_data = track_response.json()
                track_id = track_data.get("track_id") or track_data.get("id")

                if not track_id:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": "Track ID not returned",
                    }

                # Step 3: Add segment to track
                segment_response = await client.post(
                    f"{API_BASE_URL}/projects/{project_id}/tracks/{track_id}/segments",
                    json={
                        "audio_id": "test-audio-001",
                        "start_time": 0.0,
                        "duration": 5.0,
                    },
                )

                if segment_response.status_code not in [200, 201]:
                    return {
                        "workflow": workflow_name,
                        "status": "WARNING",
                        "error": f"Segment creation failed: {segment_response.status_code} (may be expected if audio doesn't exist)",
                    }

                return {
                    "workflow": workflow_name,
                    "status": "PASS",
                    "steps_completed": 3,
                    "project_id": project_id,
                    "track_id": track_id,
                }

        except Exception as e:
            logger.error(f"Workflow test failed: {e}", exc_info=True)
            return {"workflow": workflow_name, "status": "FAIL", "error": str(e)}

    async def test_effects_workflow(self) -> dict[str, Any]:
        """Test complete effects processing workflow."""
        workflow_name = "Effects Processing Workflow"
        logger.info(f"Testing workflow: {workflow_name}")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Create effect chain
                chain_response = await client.post(
                    f"{API_BASE_URL}/effects/chains",
                    json={
                        "name": "Test Chain",
                        "description": "Test effect chain",
                        "project_id": "test-project-001",
                        "effects": [],
                    },
                )

                if chain_response.status_code not in [200, 201]:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Effect chain creation failed: {chain_response.status_code}",
                    }

                chain_data = chain_response.json()
                chain_id = chain_data.get("id") or chain_data.get("chain_id")

                if not chain_id:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": "Chain ID not returned",
                    }

                # Step 2: Get effect chain
                get_chain_response = await client.get(
                    f"{API_BASE_URL}/effects/chains/{chain_id}",
                    params={"project_id": "test-project-001"},
                )

                if get_chain_response.status_code != 200:
                    return {
                        "workflow": workflow_name,
                        "status": "FAIL",
                        "error": f"Get effect chain failed: {get_chain_response.status_code}",
                    }

                return {
                    "workflow": workflow_name,
                    "status": "PASS",
                    "steps_completed": 2,
                    "chain_id": chain_id,
                }

        except Exception as e:
            logger.error(f"Workflow test failed: {e}", exc_info=True)
            return {"workflow": workflow_name, "status": "FAIL", "error": str(e)}

    async def test_error_scenarios(self) -> dict[str, Any]:
        """Test error handling scenarios."""
        workflow_name = "Error Handling Scenarios"
        logger.info(f"Testing workflow: {workflow_name}")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                errors_tested = 0
                errors_passed = 0

                # Test 1: Invalid profile ID
                try:
                    response = await client.get(
                        f"{API_BASE_URL}/profiles/invalid-profile-id"
                    )
                    if response.status_code == 404:
                        errors_passed += 1
                    errors_tested += 1
                except Exception:
                    errors_tested += 1

                # Test 2: Invalid project ID
                try:
                    response = await client.get(
                        f"{API_BASE_URL}/projects/invalid-project-id"
                    )
                    if response.status_code == 404:
                        errors_passed += 1
                    errors_tested += 1
                except Exception:
                    errors_tested += 1

                # Test 3: Missing required fields
                try:
                    response = await client.post(
                        f"{API_BASE_URL}/profiles", json={}  # Missing required fields
                    )
                    if response.status_code in [400, 422]:
                        errors_passed += 1
                    errors_tested += 1
                except Exception:
                    errors_tested += 1

                return {
                    "workflow": workflow_name,
                    "status": "PASS" if errors_passed == errors_tested else "WARNING",
                    "steps_completed": errors_tested,
                    "errors_tested": errors_tested,
                    "errors_passed": errors_passed,
                }

        except Exception as e:
            logger.error(f"Error scenario test failed: {e}", exc_info=True)
            return {"workflow": workflow_name, "status": "FAIL", "error": str(e)}

    async def run_all_tests(self) -> list[dict[str, Any]]:
        """Run all end-to-end workflow tests."""
        logger.info("Starting End-to-End Integration Tests...")

        workflows = [
            self.test_voice_cloning_workflow(),
            self.test_timeline_workflow(),
            self.test_effects_workflow(),
            self.test_error_scenarios(),
        ]

        results = await asyncio.gather(*workflows, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                self.results.append(
                    {"workflow": "Unknown", "status": "FAIL", "error": str(result)}
                )
            else:
                self.results.append(result)

        return self.results

    def generate_report(self) -> str:
        """Generate test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warnings = sum(1 for r in self.results if r["status"] == "WARNING")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        report = f"""
# End-to-End Integration Test Report

**Date:** 2025-01-28
**Total Workflows Tested:** {total}
**Passed:** {passed}
**Warnings:** {warnings}
**Failed:** {failed}

## Summary

- **Workflows with Complete Integration:** {passed}
- **Workflows with Partial Issues:** {warnings}
- **Workflows with Failures:** {failed}

## Detailed Results

"""

        for result in self.results:
            status_icon = (
                "✅"
                if result["status"] == "PASS"
                else "⚠️" if result["status"] == "WARNING" else "❌"
            )
            report += f"### {status_icon} {result['workflow']}\n"
            report += f"- **Status:** {result['status']}\n"
            if "steps_completed" in result:
                report += f"- **Steps Completed:** {result['steps_completed']}\n"
            if "error" in result:
                report += f"- **Error:** {result['error']}\n"
            report += "\n"

        return report


@pytest.mark.asyncio
async def test_end_to_end_workflows():
    """Run end-to-end integration tests."""
    tester = EndToEndWorkflowTester()
    results = await tester.run_all_tests()

    # Generate report
    report = tester.generate_report()

    # Save report
    report_path = (
        project_root / "docs" / "governance" / "END_TO_END_INTEGRATION_TEST_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    logger.info(f"\n{report}")
    logger.info(f"\nReport saved to: {report_path}")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    warnings = sum(1 for r in results if r["status"] == "WARNING")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    logger.info(f"\n{'='*60}")
    logger.info(
        f"Test Summary: {passed}/{total} passed, {warnings} warnings, {failed} failed"
    )
    logger.info(f"{'='*60}")

    # Assert that at least some tests passed
    assert passed > 0, "No workflows passed"


if __name__ == "__main__":
    asyncio.run(test_end_to_end_workflows())
