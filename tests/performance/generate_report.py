#!/usr/bin/env python3
"""
Performance Report Generator

Generates HTML and JSON performance reports from test results.
Can compare against baselines and detect regressions.

Usage:
    python generate_report.py [options]

Options:
    --input PATH       Input JSON file or directory
    --output PATH      Output report path
    --baseline PATH    Baseline file for comparison
    --format FORMAT    Output format (html, json, markdown)
    --threshold FLOAT  Regression threshold (default: 0.2 = 20%)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


class PerformanceReportGenerator:
    """Generates performance reports from test results."""

    def __init__(
        self,
        baseline_path: Path | None = None,
        regression_threshold: float = 0.2,
    ):
        """
        Initialize report generator.

        Args:
            baseline_path: Path to baseline JSON file
            regression_threshold: Threshold for regression detection (0.2 = 20%)
        """
        self.baseline_path = baseline_path
        self.regression_threshold = regression_threshold
        self.baseline: dict | None = None

        if baseline_path and baseline_path.exists():
            with open(baseline_path) as f:
                self.baseline = json.load(f)

    def load_results(self, path: Path) -> dict:
        """Load results from file or directory."""
        if path.is_file():
            with open(path) as f:
                return json.load(f)
        elif path.is_dir():
            # Find most recent report
            reports = sorted(path.glob("performance_report_*.json"), reverse=True)
            if reports:
                with open(reports[0]) as f:
                    return json.load(f)
        raise FileNotFoundError(f"No results found at {path}")

    def compare_with_baseline(self, results: dict) -> list[dict]:
        """Compare results with baseline and detect regressions."""
        if not self.baseline:
            return []

        comparisons = []
        baseline_map = {r["name"]: r for r in self.baseline.get("results", [])}

        for result in results.get("results", []):
            name = result["name"]
            if name not in baseline_map:
                continue

            baseline_result = baseline_map[name]

            # Get times to compare
            current_time = (
                result.get("metrics", {}).get("avg_time") or
                result.get("elapsed", 0)
            )
            baseline_time = (
                baseline_result.get("metrics", {}).get("avg_time") or
                baseline_result.get("elapsed", 0)
            )

            if baseline_time == 0:
                continue

            change = (current_time - baseline_time) / baseline_time
            is_regression = change > self.regression_threshold

            comparisons.append({
                "name": name,
                "baseline_time": baseline_time,
                "current_time": current_time,
                "change_percent": change * 100,
                "is_regression": is_regression,
            })

        return comparisons

    def generate_html_report(self, results: dict, output_path: Path) -> Path:
        """Generate HTML report."""
        comparisons = self.compare_with_baseline(results)
        regressions = [c for c in comparisons if c["is_regression"]]

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>VoiceStudio Performance Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        tr:nth-child(even) {{ background-color: #fafafa; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .regression {{ background-color: #fff3cd; }}
        .improvement {{ background-color: #d4edda; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; flex: 1; }}
        .summary-value {{ font-size: 32px; font-weight: bold; color: #333; }}
        .summary-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>VoiceStudio Performance Report</h1>
    <p>Generated: {results.get('generated_at', 'Unknown')}</p>

    <div class="summary">
        <div class="summary-card">
            <div class="summary-value">{results.get('total_tests', 0)}</div>
            <div class="summary-label">Total Tests</div>
        </div>
        <div class="summary-card">
            <div class="summary-value passed">{results.get('passed', 0)}</div>
            <div class="summary-label">Passed</div>
        </div>
        <div class="summary-card">
            <div class="summary-value failed">{results.get('failed', 0)}</div>
            <div class="summary-label">Failed</div>
        </div>
        <div class="summary-card">
            <div class="summary-value {'failed' if regressions else 'passed'}">{len(regressions)}</div>
            <div class="summary-label">Regressions</div>
        </div>
    </div>

    <h2>Performance Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Time (s)</th>
            <th>Max Time (s)</th>
            <th>Status</th>
        </tr>
"""

        for result in results.get("results", []):
            time_val = (
                result.get("metrics", {}).get("avg_time") or
                result.get("elapsed", 0)
            )
            max_time = result.get("max_time", "-")
            passed = result.get("passed", True)
            status_class = "passed" if passed else "failed"
            status_text = "PASS" if passed else "FAIL"

            html += f"""        <tr>
            <td>{result['name']}</td>
            <td>{time_val:.3f}</td>
            <td>{max_time if isinstance(max_time, str) else f'{max_time:.3f}'}</td>
            <td class="{status_class}">{status_text}</td>
        </tr>
"""

        html += """    </table>
"""

        if comparisons:
            html += """
    <h2>Baseline Comparison</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Baseline (s)</th>
            <th>Current (s)</th>
            <th>Change</th>
        </tr>
"""
            for comp in comparisons:
                row_class = "regression" if comp["is_regression"] else (
                    "improvement" if comp["change_percent"] < -10 else ""
                )
                change_sign = "+" if comp["change_percent"] > 0 else ""

                html += f"""        <tr class="{row_class}">
            <td>{comp['name']}</td>
            <td>{comp['baseline_time']:.3f}</td>
            <td>{comp['current_time']:.3f}</td>
            <td>{change_sign}{comp['change_percent']:.1f}%</td>
        </tr>
"""

            html += """    </table>
"""

        html += """</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html)

        return output_path

    def generate_markdown_report(self, results: dict, output_path: Path) -> Path:
        """Generate Markdown report."""
        comparisons = self.compare_with_baseline(results)
        regressions = [c for c in comparisons if c["is_regression"]]

        md = f"""# VoiceStudio Performance Report

**Generated:** {results.get('generated_at', 'Unknown')}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {results.get('total_tests', 0)} |
| Passed | {results.get('passed', 0)} |
| Failed | {results.get('failed', 0)} |
| Regressions | {len(regressions)} |

## Performance Results

| Test Name | Time (s) | Max Time (s) | Status |
|-----------|----------|--------------|--------|
"""

        for result in results.get("results", []):
            time_val = (
                result.get("metrics", {}).get("avg_time") or
                result.get("elapsed", 0)
            )
            max_time = result.get("max_time", "-")
            passed = result.get("passed", True)
            status = ":white_check_mark:" if passed else ":x:"

            max_time_str = max_time if isinstance(max_time, str) else f"{max_time:.3f}"
            md += f"| {result['name']} | {time_val:.3f} | {max_time_str} | {status} |\n"

        if comparisons:
            md += """
## Baseline Comparison

| Test Name | Baseline (s) | Current (s) | Change |
|-----------|--------------|-------------|--------|
"""
            for comp in comparisons:
                change_sign = "+" if comp["change_percent"] > 0 else ""
                status = ":warning:" if comp["is_regression"] else ""

                md += (
                    f"| {comp['name']} | {comp['baseline_time']:.3f} | "
                    f"{comp['current_time']:.3f} | {change_sign}{comp['change_percent']:.1f}% {status} |\n"
                )

        with open(output_path, "w") as f:
            f.write(md)

        return output_path

    def generate_json_report(self, results: dict, output_path: Path) -> Path:
        """Generate JSON report with comparisons."""
        comparisons = self.compare_with_baseline(results)

        report = {
            **results,
            "comparisons": comparisons,
            "regressions": [c for c in comparisons if c["is_regression"]],
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate performance reports")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(".buildlogs/performance/reports"),
        help="Input JSON file or directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output report path",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Baseline file for comparison",
    )
    parser.add_argument(
        "--format",
        choices=["html", "json", "markdown"],
        default="html",
        help="Output format",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.2,
        help="Regression threshold (default: 0.2 = 20%%)",
    )

    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "html" if args.format == "html" else (
            "md" if args.format == "markdown" else "json"
        )
        output_path = Path(f".buildlogs/performance/report_{timestamp}.{ext}")

    # Generate report
    generator = PerformanceReportGenerator(
        baseline_path=args.baseline,
        regression_threshold=args.threshold,
    )

    try:
        results = generator.load_results(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "html":
        generator.generate_html_report(results, output_path)
    elif args.format == "markdown":
        generator.generate_markdown_report(results, output_path)
    else:
        generator.generate_json_report(results, output_path)

    print(f"Report generated: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
