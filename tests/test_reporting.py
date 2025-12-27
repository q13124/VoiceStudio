"""
Test Reporting Utilities
Provides test reporting and coverage utilities for VoiceStudio Quantum+ test suite.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TestReportGenerator:
    """Generates test reports and coverage summaries."""

    def __init__(self, output_dir: Path):
        """
        Initialize test report generator.

        Args:
            output_dir: Directory for report output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reports: List[Dict[str, Any]] = []

    def add_test_result(
        self,
        test_name: str,
        status: str,
        duration: float,
        error: Optional[str] = None,
        category: Optional[str] = None,
    ):
        """
        Add a test result to the report.

        Args:
            test_name: Name of the test
            status: Test status (passed, failed, skipped, error)
            duration: Test duration in seconds
            error: Error message if test failed
            category: Test category (unit, integration, e2e, etc.)
        """
        self.reports.append(
            {
                "test_name": test_name,
                "status": status,
                "duration": duration,
                "error": error,
                "category": category,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate test summary statistics.

        Returns:
            Dictionary with test statistics
        """
        total = len(self.reports)
        passed = sum(1 for r in self.reports if r["status"] == "passed")
        failed = sum(1 for r in self.reports if r["status"] == "failed")
        skipped = sum(1 for r in self.reports if r["status"] == "skipped")
        error = sum(1 for r in self.reports if r["status"] == "error")

        total_duration = sum(r["duration"] for r in self.reports)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "error": error,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "total_duration": total_duration,
            "average_duration": (total_duration / total) if total > 0 else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_category_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate summary by test category.

        Returns:
            Dictionary with statistics per category
        """
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for report in self.reports:
            category = report.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(report)

        summary = {}
        for category, reports in categories.items():
            total = len(reports)
            passed = sum(1 for r in reports if r["status"] == "passed")
            summary[category] = {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": (passed / total * 100) if total > 0 else 0,
            }

        return summary

    def save_json_report(self, filename: str = "test_report.json"):
        """
        Save test report as JSON.

        Args:
            filename: Output filename
        """
        report_path = self.output_dir / filename
        report_data = {
            "summary": self.generate_summary(),
            "category_summary": self.generate_category_summary(),
            "tests": self.reports,
        }
        report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        logger.info(f"Test report saved to {report_path}")

    def save_text_report(self, filename: str = "test_report.txt"):
        """
        Save test report as text.

        Args:
            filename: Output filename
        """
        report_path = self.output_dir / filename
        summary = self.generate_summary()
        category_summary = self.generate_category_summary()

        lines = [
            "=" * 80,
            "VoiceStudio Quantum+ Test Report",
            "=" * 80,
            "",
            f"Generated: {summary['timestamp']}",
            "",
            "Summary:",
            f"  Total Tests: {summary['total']}",
            f"  Passed: {summary['passed']}",
            f"  Failed: {summary['failed']}",
            f"  Skipped: {summary['skipped']}",
            f"  Errors: {summary['error']}",
            f"  Pass Rate: {summary['pass_rate']:.2f}%",
            f"  Total Duration: {summary['total_duration']:.2f}s",
            f"  Average Duration: {summary['average_duration']:.2f}s",
            "",
            "By Category:",
        ]

        for category, stats in category_summary.items():
            lines.append(f"  {category}:")
            lines.append(f"    Total: {stats['total']}")
            lines.append(f"    Passed: {stats['passed']}")
            lines.append(f"    Failed: {stats['failed']}")
            lines.append(f"    Pass Rate: {stats['pass_rate']:.2f}%")
            lines.append("")

        if summary["failed"] > 0 or summary["error"] > 0:
            lines.append("Failed Tests:")
            for report in self.reports:
                if report["status"] in ["failed", "error"]:
                    lines.append(f"  - {report['test_name']}")
                    if report.get("error"):
                        lines.append(f"    Error: {report['error']}")
            lines.append("")

        lines.append("=" * 80)

        report_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Test report saved to {report_path}")


class CoverageReporter:
    """Reports test coverage statistics."""

    def __init__(self, coverage_data: Dict[str, Any]):
        """
        Initialize coverage reporter.

        Args:
            coverage_data: Coverage data from pytest-cov or similar
        """
        self.coverage_data = coverage_data

    def generate_coverage_summary(self) -> Dict[str, Any]:
        """
        Generate coverage summary.

        Returns:
            Dictionary with coverage statistics
        """
        total_lines = self.coverage_data.get("total_lines", 0)
        covered_lines = self.coverage_data.get("covered_lines", 0)
        coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0

        return {
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "missing_lines": total_lines - covered_lines,
            "coverage_percent": coverage_percent,
            "files": self.coverage_data.get("files", {}),
        }

    def save_coverage_report(
        self, output_dir: Path, filename: str = "coverage_report.json"
    ):
        """
        Save coverage report.

        Args:
            output_dir: Output directory
            filename: Output filename
        """
        output_path = Path(output_dir) / filename
        summary = self.generate_coverage_summary()
        output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        logger.info(f"Coverage report saved to {output_path}")
