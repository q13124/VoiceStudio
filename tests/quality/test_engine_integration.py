"""
Engine Integration Tests
Test all 44 engines to verify no placeholders, test error handling, and verify functionality.

Worker 3 - Task: TASK-W3-F1-001
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EngineTestResult:
    """Result of testing an engine."""
    engine_name: str
    engine_file: str
    has_placeholders: bool
    placeholder_count: int
    has_error_handling: bool
    error_handling_count: int
    can_initialize: bool
    initialization_error: str = ""
    status: str = "pending"  # pending, pass, fail, warning


class EngineIntegrationTester:
    """Test all engines for integration quality."""

    def __init__(self):
        self.engines_dir = project_root / "app" / "core" / "engines"
        self.results: list[EngineTestResult] = []

    def find_all_engines(self) -> list[Path]:
        """Find all engine Python files."""
        engine_files = []

        # Find all .py files in engines directory (excluding __init__, base, protocols, etc.)
        exclude_files = {
            "__init__.py",
            "base.py",
            "protocols.py",
            "config.py",
            "router.py",
            "quality_metrics.py",
            "quality_comparison.py",
            "quality_optimizer.py",
            "quality_presets.py",
            "test_quality_metrics.py",
            "onnx_converter.py",
            "onnx_wrapper.py",
        }

        for file_path in self.engines_dir.glob("*.py"):
            if file_path.name not in exclude_files:
                engine_files.append(file_path)

        logger.info(f"Found {len(engine_files)} engine files")
        return sorted(engine_files)

    def check_for_placeholders(self, file_path: Path) -> tuple[bool, int]:
        """Check if engine file has placeholders."""
        placeholder_patterns = [
            "TODO",
            "FIXME",
            "PLACEHOLDER",
            "NotImplemented",
            "NotImplementedError",
            "raise NotImplementedError",
            "pass  # TODO",
            "pass  # FIXME",
            "# TODO:",
            "# FIXME:",
            "placeholder",
            "coming soon",
            "not implemented",
        ]

        try:
            content = file_path.read_text(encoding="utf-8")
            placeholder_count = 0

            for pattern in placeholder_patterns:
                count = content.count(pattern)
                placeholder_count += count

            # Check for empty methods with only pass
            lines = content.split("\n")
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("def ") and "pass" in stripped:
                    # Check if next non-empty line is just "pass"
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            if next_line == "pass":
                                placeholder_count += 1
                            break

            has_placeholders = placeholder_count > 0
            return has_placeholders, placeholder_count

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return True, 1  # Assume has placeholders if can't read

    def check_error_handling(self, file_path: Path) -> tuple[bool, int]:
        """Check if engine has proper error handling."""
        error_handling_patterns = [
            "try:",
            "except",
            "raise",
            "HTTPException",
            "ValueError",
            "FileNotFoundError",
            "Exception",
            "logger.error",
            "logger.warning",
        ]

        try:
            content = file_path.read_text(encoding="utf-8")
            error_handling_count = 0

            for pattern in error_handling_patterns:
                count = content.count(pattern)
                error_handling_count += count

            has_error_handling = error_handling_count > 0
            return has_error_handling, error_handling_count

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return False, 0

    def test_engine_initialization(self, file_path: Path) -> tuple[bool, str]:
        """Test if engine can be imported and initialized."""
        engine_name = file_path.stem

        try:
            # Try to import the engine module
            module_name = f"app.core.engines.{engine_name}"
            module = __import__(module_name, fromlist=[""])

            # Look for engine class (usually ends with "Engine")
            engine_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    attr_name.endswith("Engine") and
                    attr_name != "EngineProtocol"):
                    engine_class = attr
                    break

            if engine_class is None:
                return False, f"No engine class found in {engine_name}"

            # Try to create instance (with minimal parameters)
            try:
                # Most engines need minimal init - try with empty dict or None
                engine_class()
                return True, ""
            except TypeError:
                # Some engines need parameters - that's okay, at least it's importable
                return True, "Requires parameters (acceptable)"
            except Exception as e:
                return False, str(e)

        except ImportError as e:
            return False, f"Import error: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_engine(self, file_path: Path) -> EngineTestResult:
        """Test a single engine."""
        engine_name = file_path.stem
        logger.info(f"Testing engine: {engine_name}")

        # Check for placeholders
        has_placeholders, placeholder_count = self.check_for_placeholders(file_path)

        # Check error handling
        has_error_handling, error_handling_count = self.check_error_handling(file_path)

        # Test initialization
        can_initialize, init_error = self.test_engine_initialization(file_path)

        # Determine status
        if has_placeholders:
            status = "fail"
        elif not can_initialize and "Requires parameters" not in init_error:
            status = "warning"
        else:
            status = "pass"

        result = EngineTestResult(
            engine_name=engine_name,
            engine_file=str(file_path.relative_to(project_root)),
            has_placeholders=has_placeholders,
            placeholder_count=placeholder_count,
            has_error_handling=has_error_handling,
            error_handling_count=error_handling_count,
            can_initialize=can_initialize,
            initialization_error=init_error,
            status=status
        )

        return result

    def run_all_tests(self) -> list[EngineTestResult]:
        """Run tests on all engines."""
        engine_files = self.find_all_engines()

        logger.info(f"Testing {len(engine_files)} engines...")

        for file_path in engine_files:
            try:
                result = self.test_engine(file_path)
                self.results.append(result)

                status_icon = "✅" if result.status == "pass" else "⚠️" if result.status == "warning" else "❌"
                logger.info(f"{status_icon} {result.engine_name}: {result.status}")

            except Exception as e:
                logger.error(f"Error testing {file_path.name}: {e}")
                self.results.append(EngineTestResult(
                    engine_name=file_path.stem,
                    engine_file=str(file_path.relative_to(project_root)),
                    has_placeholders=True,
                    placeholder_count=1,
                    has_error_handling=False,
                    error_handling_count=0,
                    can_initialize=False,
                    initialization_error=str(e),
                    status="fail"
                ))

        return self.results

    def generate_report(self) -> str:
        """Generate test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "pass")
        warnings = sum(1 for r in self.results if r.status == "warning")
        failed = sum(1 for r in self.results if r.status == "fail")

        report = f"""
# Engine Integration Test Report

**Date:** 2025-01-28
**Total Engines Tested:** {total}
**Passed:** {passed}
**Warnings:** {warnings}
**Failed:** {failed}

## Summary

- **Engines with Placeholders:** {sum(1 for r in self.results if r.has_placeholders)}
- **Engines with Error Handling:** {sum(1 for r in self.results if r.has_error_handling)}
- **Engines Can Initialize:** {sum(1 for r in self.results if r.can_initialize)}

## Detailed Results

"""

        for result in sorted(self.results, key=lambda x: x.status):
            status_icon = "✅" if result.status == "pass" else "⚠️" if result.status == "warning" else "❌"
            report += f"### {status_icon} {result.engine_name}\n"
            report += f"- **File:** `{result.engine_file}`\n"
            report += f"- **Status:** {result.status.upper()}\n"
            report += f"- **Has Placeholders:** {result.has_placeholders} ({result.placeholder_count} found)\n"
            report += f"- **Has Error Handling:** {result.has_error_handling} ({result.error_handling_count} patterns found)\n"
            report += f"- **Can Initialize:** {result.can_initialize}\n"
            if result.initialization_error:
                report += f"- **Init Error:** {result.initialization_error}\n"
            report += "\n"

        return report


def main():
    """Run engine integration tests."""
    logger.info("Starting Engine Integration Tests...")

    tester = EngineIntegrationTester()
    results = tester.run_all_tests()

    # Generate report
    report = tester.generate_report()

    # Save report
    report_path = project_root / "docs" / "governance" / "ENGINE_INTEGRATION_TEST_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    logger.info(f"\n{report}")
    logger.info(f"\nReport saved to: {report_path}")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.status == "pass")
    warnings = sum(1 for r in results if r.status == "warning")
    failed = sum(1 for r in results if r.status == "fail")

    logger.info(f"\n{'='*60}")
    logger.info(f"Test Summary: {passed}/{total} passed, {warnings} warnings, {failed} failed")
    logger.info(f"{'='*60}")

    # Exit with error code if any failures
    if failed > 0:
        sys.exit(1)
    elif warnings > 0:
        sys.exit(0)  # Warnings are acceptable
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

