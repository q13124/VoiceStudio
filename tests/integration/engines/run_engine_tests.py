"""
Engine Integration Test Runner
Runs all engine integration tests and generates a comprehensive report.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent


def run_tests():
    """Run all engine integration tests."""
    print("=" * 80)
    print("Engine Integration Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}\n")

    test_file = project_root / "tests" / "integration" / "engines" / "test_engine_integration.py"

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return 1

    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--json-report",
        "--json-report-file=engine_test_report.json"
    ]

    print(f"Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        print("\n" + "=" * 80)
        print(f"Tests completed at: {datetime.now().isoformat()}")
        print(f"Exit code: {result.returncode}")
        print("=" * 80)

        return result.returncode
    except Exception as e:
        print(f"ERROR running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())

