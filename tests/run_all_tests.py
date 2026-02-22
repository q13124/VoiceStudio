"""
Comprehensive Test Runner
Runs all test suites and generates a complete test report.
"""

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent


def run_test_suite(suite_name: str, test_path: Path) -> dict[str, Any]:
    """Run a test suite and return results."""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"Running {suite_name}")
    logger.info(f"{'=' * 80}")

    if not test_path.exists():
        logger.warning(f"Test path does not exist: {test_path}")
        return {"suite": suite_name, "status": "skipped", "reason": "Test path not found"}

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        "-v",
        "--tb=short",
        "--json-report",
        "--json-report-file=.pytest_cache/report.json",
    ]

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=300)

        return {
            "suite": suite_name,
            "status": "passed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "suite": suite_name,
            "status": "timeout",
            "reason": "Test suite exceeded 5 minute timeout",
        }
    except Exception as e:
        return {"suite": suite_name, "status": "error", "error": str(e)}


def run_placeholder_verification() -> dict[str, Any]:
    """Run placeholder verification script."""
    logger.info(f"\n{'=' * 80}")
    logger.info("Running Placeholder Verification")
    logger.info(f"{'=' * 80}")

    script_path = project_root / "tests" / "quality" / "verify_no_placeholders.py"

    if not script_path.exists():
        logger.warning(f"Placeholder verification script not found: {script_path}")
        return {
            "suite": "placeholder_verification",
            "status": "skipped",
            "reason": "Script not found",
        }

    cmd = [sys.executable, str(script_path)]

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=600)

        return {
            "suite": "placeholder_verification",
            "status": "passed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"suite": "placeholder_verification", "status": "error", "error": str(e)}


def generate_test_report(results: list[dict[str, Any]]) -> str:
    """Generate comprehensive test report."""
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("COMPREHENSIVE TEST REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().isoformat()}")
    report_lines.append("")

    total_suites = len(results)
    passed_suites = sum(1 for r in results if r.get("status") == "passed")
    failed_suites = sum(1 for r in results if r.get("status") == "failed")
    skipped_suites = sum(1 for r in results if r.get("status") in ["skipped", "timeout", "error"])

    report_lines.append(f"Total Test Suites: {total_suites}")
    report_lines.append(f"Passed: {passed_suites}")
    report_lines.append(f"Failed: {failed_suites}")
    report_lines.append(f"Skipped/Error: {skipped_suites}")
    report_lines.append("")

    for result in results:
        suite_name = result.get("suite", "unknown")
        status = result.get("status", "unknown")

        report_lines.append(f"\n{suite_name}: {status.upper()}")

        if status == "failed":
            if "stdout" in result:
                report_lines.append(f"  Output: {result['stdout'][:200]}")
            if "stderr" in result:
                report_lines.append(f"  Error: {result['stderr'][:200]}")
        elif status in ["skipped", "timeout", "error"]:
            if "reason" in result:
                report_lines.append(f"  Reason: {result['reason']}")
            if "error" in result:
                report_lines.append(f"  Error: {result['error']}")

    report_lines.append("")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def main():
    """Main function."""
    logger.info("Starting comprehensive test run...")
    logger.info(f"Project root: {project_root}")

    test_suites = [
        (
            "Engine Integration Tests",
            project_root / "tests" / "integration" / "engines" / "test_engine_integration.py",
        ),
        (
            "Backend API Tests",
            project_root / "tests" / "integration" / "api" / "test_backend_endpoints.py",
        ),
        ("End-to-End Tests", project_root / "tests" / "e2e" / "test_complete_workflows.py"),
        ("Engine Unit Tests", project_root / "tests" / "unit" / "test_engines_unit.py"),
        (
            "Backend Route Unit Tests",
            project_root / "tests" / "unit" / "test_backend_routes_unit.py",
        ),
    ]

    results = []

    for suite_name, test_path in test_suites:
        result = run_test_suite(suite_name, test_path)
        results.append(result)

    placeholder_result = run_placeholder_verification()
    results.append(placeholder_result)

    report = generate_test_report(results)
    print(report)

    report_file = project_root / "test_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Test report saved to: {report_file}")

    failed_count = sum(1 for r in results if r.get("status") == "failed")
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
