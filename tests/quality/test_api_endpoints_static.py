"""
API Endpoint Static Analysis Test
Test all 133+ backend API endpoints for completeness, error handling, and placeholder detection.

Worker 3 - Task: TASK-W3-F2-001
"""

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EndpointTestResult:
    """Result of testing an endpoint."""
    method: str
    path: str
    file: str
    function_name: str = ""
    has_placeholders: bool = False
    placeholder_count: int = 0
    has_error_handling: bool = False
    error_handling_count: int = 0
    has_validation: bool = False
    validation_count: int = 0
    has_response_model: bool = False
    status: str = "pending"  # pending, pass, fail, warning


class APIEndpointTester:
    """Test all API endpoints for integration quality."""

    def __init__(self):
        self.routes_dir = project_root / "backend" / "api" / "routes"
        self.endpoints: list[EndpointTestResult] = []
        self.placeholder_patterns = [
            r"TODO",
            r"FIXME",
            r"PLACEHOLDER",
            r"NotImplemented",
            r"NotImplementedError",
            r"raise NotImplemented",
            r"pass\s*#\s*TODO",
            r"pass\s*#\s*FIXME",
            r"#\s*TODO:",
            r"#\s*FIXME:",
            r"placeholder",
            r"coming soon",
            r"not implemented",
        ]

    def find_all_route_files(self) -> list[Path]:
        """Find all route Python files."""
        if not self.routes_dir.exists():
            return []

        route_files = list(self.routes_dir.glob("*.py"))
        route_files = [f for f in route_files if f.name != "__init__.py"]

        logger.info(f"Found {len(route_files)} route files")
        return sorted(route_files)

    def extract_endpoints_from_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Extract endpoint definitions from route file."""
        endpoints = []

        try:
            content = file_path.read_text(encoding="utf-8")

            # Pattern for FastAPI router decorators
            # @router.get("/path"), @router.post("/path"), etc.
            pattern = r'@router\.(get|post|put|delete|patch)\("([^"]+)"'

            for match in re.finditer(pattern, content):
                method = match.group(1).upper()
                path = match.group(2)

                # Find the function name after the decorator
                func_match = re.search(r'def\s+(\w+)\s*\(', content[match.end():match.end()+200])
                function_name = func_match.group(1) if func_match else ""

                endpoints.append({
                    "method": method,
                    "path": path,
                    "file": file_path.name,
                    "function_name": function_name,
                    "start_pos": match.start()
                })

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")

        return endpoints

    def check_for_placeholders(self, file_path: Path, start_pos: int, end_pos: int | None = None) -> tuple[bool, int]:
        """Check if endpoint function has placeholders."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract function content
            if end_pos is None:
                # Find the end of the function (next @router or end of file)
                next_decorator = content.find("@router", start_pos + 1)
                end_pos = len(content) if next_decorator == -1 else next_decorator

            function_content = content[start_pos:end_pos]

            placeholder_count = 0
            for pattern in self.placeholder_patterns:
                matches = re.findall(pattern, function_content, re.IGNORECASE)
                placeholder_count += len(matches)

            has_placeholders = placeholder_count > 0
            return has_placeholders, placeholder_count

        except Exception as e:
            logger.error(f"Error checking placeholders in {file_path}: {e}")
            return True, 1

    def check_error_handling(self, file_path: Path, start_pos: int, end_pos: int | None = None) -> tuple[bool, int]:
        """Check if endpoint has error handling."""
        try:
            content = file_path.read_text(encoding="utf-8")

            if end_pos is None:
                next_decorator = content.find("@router", start_pos + 1)
                end_pos = len(content) if next_decorator == -1 else next_decorator

            function_content = content[start_pos:end_pos]

            error_patterns = [
                r"try:",
                r"except",
                r"HTTPException",
                r"ValueError",
                r"FileNotFoundError",
                r"Exception",
                r"logger\.error",
                r"logger\.warning",
                r"raise HTTPException",
            ]

            error_handling_count = 0
            for pattern in error_patterns:
                matches = re.findall(pattern, function_content)
                error_handling_count += len(matches)

            has_error_handling = error_handling_count > 0
            return has_error_handling, error_handling_count

        except Exception as e:
            logger.error(f"Error checking error handling in {file_path}: {e}")
            return False, 0

    def check_validation(self, file_path: Path, start_pos: int, end_pos: int | None = None) -> tuple[bool, int]:
        """Check if endpoint has validation."""
        try:
            content = file_path.read_text(encoding="utf-8")

            if end_pos is None:
                next_decorator = content.find("@router", start_pos + 1)
                end_pos = len(content) if next_decorator == -1 else next_decorator

            function_content = content[start_pos:end_pos]

            validation_patterns = [
                r"field_validator",
                r"validator",
                r"validate",
                r"if.*is None",
                r"if not.*:",
                r"assert",
                r"Pydantic",
            ]

            validation_count = 0
            for pattern in validation_patterns:
                matches = re.findall(pattern, function_content, re.IGNORECASE)
                validation_count += len(matches)

            has_validation = validation_count > 0
            return has_validation, validation_count

        except Exception as e:
            logger.error(f"Error checking validation in {file_path}: {e}")
            return False, 0

    def check_response_model(self, file_path: Path, start_pos: int) -> bool:
        """Check if endpoint has response_model."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Look backwards from start_pos to find the decorator
            decorator_start = content.rfind("@router", 0, start_pos)
            if decorator_start == -1:
                return False

            decorator_end = content.find("\n", start_pos)
            if decorator_end == -1:
                decorator_end = start_pos + 500

            decorator_content = content[decorator_start:decorator_end]

            # Check for response_model parameter
            has_response_model = "response_model" in decorator_content

            return has_response_model

        except Exception as e:
            logger.error(f"Error checking response model in {file_path}: {e}")
            return False

    def test_endpoint(self, endpoint: dict[str, Any], file_path: Path) -> EndpointTestResult:
        """Test a single endpoint."""
        method = endpoint["method"]
        path = endpoint["path"]
        function_name = endpoint.get("function_name", "")
        start_pos = endpoint.get("start_pos", 0)

        logger.debug(f"Testing {method} {path} in {file_path.name}")

        # Check for placeholders
        has_placeholders, placeholder_count = self.check_for_placeholders(file_path, start_pos)

        # Check error handling
        has_error_handling, error_handling_count = self.check_error_handling(file_path, start_pos)

        # Check validation
        has_validation, validation_count = self.check_validation(file_path, start_pos)

        # Check response model
        has_response_model = self.check_response_model(file_path, start_pos)

        # Determine status
        if has_placeholders:
            status = "fail"
        elif not has_error_handling and not has_response_model:
            status = "warning"
        else:
            status = "pass"

        result = EndpointTestResult(
            method=method,
            path=path,
            file=file_path.name,
            function_name=function_name,
            has_placeholders=has_placeholders,
            placeholder_count=placeholder_count,
            has_error_handling=has_error_handling,
            error_handling_count=error_handling_count,
            has_validation=has_validation,
            validation_count=validation_count,
            has_response_model=has_response_model,
            status=status
        )

        return result

    def run_all_tests(self) -> list[EndpointTestResult]:
        """Run tests on all endpoints."""
        route_files = self.find_all_route_files()

        logger.info(f"Testing endpoints in {len(route_files)} route files...")

        for file_path in route_files:
            try:
                endpoints = self.extract_endpoints_from_file(file_path)

                for endpoint in endpoints:
                    result = self.test_endpoint(endpoint, file_path)
                    self.endpoints.append(result)

                    status_icon = "✅" if result.status == "pass" else "⚠️" if result.status == "warning" else "❌"
                    logger.debug(f"{status_icon} {result.method} {result.path}: {result.status}")

            except Exception as e:
                logger.error(f"Error testing {file_path.name}: {e}")

        logger.info(f"Tested {len(self.endpoints)} endpoints")
        return self.endpoints

    def generate_report(self) -> str:
        """Generate test report."""
        total = len(self.endpoints)
        passed = sum(1 for e in self.endpoints if e.status == "pass")
        warnings = sum(1 for e in self.endpoints if e.status == "warning")
        failed = sum(1 for e in self.endpoints if e.status == "fail")

        # Group by file
        endpoints_by_file: dict[str, list[EndpointTestResult]] = {}
        for endpoint in self.endpoints:
            if endpoint.file not in endpoints_by_file:
                endpoints_by_file[endpoint.file] = []
            endpoints_by_file[endpoint.file].append(endpoint)

        report = f"""
# API Endpoint Test Report

**Date:** 2025-01-28
**Total Endpoints Tested:** {total}
**Passed:** {passed}
**Warnings:** {warnings}
**Failed:** {failed}

## Summary

- **Endpoints with Placeholders:** {sum(1 for e in self.endpoints if e.has_placeholders)}
- **Endpoints with Error Handling:** {sum(1 for e in self.endpoints if e.has_error_handling)}
- **Endpoints with Validation:** {sum(1 for e in self.endpoints if e.has_validation)}
- **Endpoints with Response Models:** {sum(1 for e in self.endpoints if e.has_response_model)}

## Results by Route File

"""

        for file_name in sorted(endpoints_by_file.keys()):
            file_endpoints = endpoints_by_file[file_name]
            file_passed = sum(1 for e in file_endpoints if e.status == "pass")
            file_warnings = sum(1 for e in file_endpoints if e.status == "warning")
            file_failed = sum(1 for e in file_endpoints if e.status == "fail")

            report += f"### {file_name}\n"
            report += f"- **Total Endpoints:** {len(file_endpoints)}\n"
            report += f"- **Passed:** {file_passed}, **Warnings:** {file_warnings}, **Failed:** {file_failed}\n\n"

            # List failed endpoints
            failed_endpoints = [e for e in file_endpoints if e.status == "fail"]
            if failed_endpoints:
                report += "**Failed Endpoints:**\n"
                for endpoint in failed_endpoints:
                    report += f"- `{endpoint.method} {endpoint.path}` - {endpoint.placeholder_count} placeholders found\n"
                report += "\n"

        # Detailed results for failed endpoints
        failed_endpoints = [e for e in self.endpoints if e.status == "fail"]
        if failed_endpoints:
            report += "## Failed Endpoints Details\n\n"
            for endpoint in failed_endpoints:
                report += f"### {endpoint.method} {endpoint.path}\n"
                report += f"- **File:** `{endpoint.file}`\n"
                report += f"- **Function:** `{endpoint.function_name}`\n"
                report += f"- **Placeholders Found:** {endpoint.placeholder_count}\n"
                report += f"- **Error Handling:** {endpoint.has_error_handling}\n"
                report += f"- **Validation:** {endpoint.has_validation}\n"
                report += f"- **Response Model:** {endpoint.has_response_model}\n\n"

        return report


def main():
    """Run API endpoint tests."""
    logger.info("Starting API Endpoint Tests...")

    tester = APIEndpointTester()
    results = tester.run_all_tests()

    # Generate report
    report = tester.generate_report()

    # Save report
    report_path = project_root / "docs" / "governance" / "API_ENDPOINT_TEST_REPORT.md"
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

