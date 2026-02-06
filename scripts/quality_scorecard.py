#!/usr/bin/env python3
"""
Quality Scorecard Generator

Aggregates quality metrics into a composite score across 6 dimensions:
- Gate Status (20%): Verification system gate results
- Test Coverage (25%): Python and C# code coverage
- Build Health (15%): Build errors and warnings
- Tech Debt (15%): Quality Ledger issue counts
- Documentation (15%): Documentation coverage
- Security (10%): Security scan results

Usage:
    python scripts/quality_scorecard.py
    python scripts/quality_scorecard.py --output-format json
    python scripts/quality_scorecard.py --ci  # Exit code reflects quality
    python scripts/quality_scorecard.py --threshold 85

Exit Codes:
    0: Quality score meets threshold (default 85)
    1: Quality score below threshold
    2: Error occurred
"""

from _env_setup import PROJECT_ROOT, BUILDLOGS_DIR

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure output directories exist
QUALITY_DIR = BUILDLOGS_DIR / "quality"
QUALITY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DimensionScore:
    """Score for a single quality dimension."""
    name: str
    score: float  # 0-100
    weight: float  # 0-1
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class ScorecardResult:
    """Complete quality scorecard result."""
    timestamp: str
    overall_score: float
    grade: str
    dimensions: Dict[str, DimensionScore]
    passed: bool
    threshold: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "overall_score": round(self.overall_score, 2),
            "grade": self.grade,
            "passed": self.passed,
            "threshold": self.threshold,
            "dimensions": {
                name: {
                    "score": round(dim.score, 2),
                    "weight": dim.weight,
                    "weighted_score": round(dim.weighted_score, 2),
                    "details": dim.details,
                    "errors": dim.errors,
                }
                for name, dim in self.dimensions.items()
            }
        }


class GateStatusCollector:
    """Collect gate status from verification system."""
    
    WEIGHT = 0.20
    
    def collect(self) -> DimensionScore:
        """Collect gate status metrics."""
        details = {}
        errors = []
        
        try:
            # Try to run gate_status command
            result = subprocess.run(
                [sys.executable, "-m", "tools.overseer.cli.main", "gate_status"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT)
            )
            
            # Parse output for gate statuses
            output = result.stdout + result.stderr
            
            # Count GREEN/RED gates
            green_count = len(re.findall(r"GREEN|PASS|✓", output, re.IGNORECASE))
            red_count = len(re.findall(r"RED|FAIL|✗", output, re.IGNORECASE))
            total_gates = green_count + red_count if (green_count + red_count) > 0 else 8
            
            if total_gates > 0:
                score = (green_count / total_gates) * 100
            else:
                # Assume all gates pass if no explicit status
                score = 100.0 if result.returncode == 0 else 50.0
            
            details = {
                "green_gates": green_count,
                "red_gates": red_count,
                "total_gates": total_gates,
                "exit_code": result.returncode,
            }
            
        except subprocess.TimeoutExpired:
            score = 50.0
            errors.append("Gate status check timed out")
        except Exception as e:
            score = 50.0
            errors.append(f"Gate status check failed: {e}")
        
        return DimensionScore(
            name="Gate Status",
            score=score,
            weight=self.WEIGHT,
            details=details,
            errors=errors,
        )


class CoverageCollector:
    """Collect test coverage metrics."""
    
    WEIGHT = 0.25
    
    def collect(self) -> DimensionScore:
        """Collect coverage metrics from Python and C#."""
        details = {}
        errors = []
        scores = []
        
        # Python coverage
        python_cov = self._get_python_coverage()
        if python_cov is not None:
            scores.append(python_cov)
            details["python_coverage"] = python_cov
        else:
            errors.append("Python coverage not available")
        
        # C# coverage (from Cobertura XML if available)
        csharp_cov = self._get_csharp_coverage()
        if csharp_cov is not None:
            scores.append(csharp_cov)
            details["csharp_coverage"] = csharp_cov
        else:
            errors.append("C# coverage not available")
        
        # Calculate average score
        if scores:
            score = sum(scores) / len(scores)
        else:
            score = 0.0
        
        return DimensionScore(
            name="Test Coverage",
            score=score,
            weight=self.WEIGHT,
            details=details,
            errors=errors,
        )
    
    def _get_python_coverage(self) -> Optional[float]:
        """Get Python coverage from coverage.xml or .coverage."""
        coverage_xml = PROJECT_ROOT / "coverage.xml"
        
        if coverage_xml.exists():
            try:
                tree = ET.parse(coverage_xml)
                root = tree.getroot()
                line_rate = float(root.get("line-rate", 0))
                return line_rate * 100
            except Exception:
                pass
        
        # Try running coverage report
        try:
            result = subprocess.run(
                [sys.executable, "-m", "coverage", "report", "--format=total"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                # Output is just the percentage
                return float(result.stdout.strip())
        except Exception:
            pass
        
        return None
    
    def _get_csharp_coverage(self) -> Optional[float]:
        """Get C# coverage from Cobertura XML."""
        # Look for coverage file in common locations
        possible_paths = [
            PROJECT_ROOT / "TestResults" / "coverage.cobertura.xml",
            PROJECT_ROOT / ".buildlogs" / "coverage.cobertura.xml",
            PROJECT_ROOT / "coverage.cobertura.xml",
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    tree = ET.parse(path)
                    root = tree.getroot()
                    line_rate = float(root.get("line-rate", 0))
                    return line_rate * 100
                except Exception:
                    pass
        
        return None


class BuildHealthCollector:
    """Collect build health metrics."""
    
    WEIGHT = 0.15
    
    def collect(self) -> DimensionScore:
        """Collect build health metrics."""
        details = {}
        errors_list = []
        
        # Check for recent build output
        build_output = PROJECT_ROOT / "build_output.txt"
        build_warnings = PROJECT_ROOT / "build_warnings.txt"
        
        error_count = 0
        warning_count = 0
        
        if build_output.exists():
            content = build_output.read_text(errors="ignore")
            error_count = len(re.findall(r": error [A-Z]+\d+:", content))
            warning_count += len(re.findall(r": warning [A-Z]+\d+:", content))
            details["build_output_exists"] = True
        
        if build_warnings.exists():
            content = build_warnings.read_text(errors="ignore")
            warning_count += content.count("\n")
            details["warnings_file_exists"] = True
        
        details["error_count"] = error_count
        details["warning_count"] = warning_count
        
        # Calculate score: 100 if no errors, -5 per warning, min 0
        if error_count > 0:
            score = 0.0
            errors_list.append(f"Build has {error_count} error(s)")
        else:
            score = max(0.0, 100.0 - (warning_count * 2))
        
        return DimensionScore(
            name="Build Health",
            score=score,
            weight=self.WEIGHT,
            details=details,
            errors=errors_list,
        )


class TechDebtCollector:
    """Collect tech debt metrics from Quality Ledger."""
    
    WEIGHT = 0.15
    
    def collect(self) -> DimensionScore:
        """Collect tech debt metrics."""
        details = {}
        errors = []
        
        try:
            # Run ledger_validate
            result = subprocess.run(
                [sys.executable, "-m", "tools.overseer.cli.main", "ledger_validate"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT)
            )
            
            output = result.stdout + result.stderr
            
            # Parse for issue counts
            open_issues = len(re.findall(r"OPEN|TODO|IN_PROGRESS", output, re.IGNORECASE))
            done_issues = len(re.findall(r"DONE|CLOSED|COMPLETE", output, re.IGNORECASE))
            
            total = open_issues + done_issues
            
            if total > 0:
                # Score based on completion rate
                score = (done_issues / total) * 100
            else:
                score = 100.0  # No issues = perfect
            
            details = {
                "open_issues": open_issues,
                "done_issues": done_issues,
                "total_issues": total,
                "exit_code": result.returncode,
            }
            
        except subprocess.TimeoutExpired:
            score = 50.0
            errors.append("Ledger validation timed out")
        except Exception as e:
            score = 50.0
            errors.append(f"Ledger validation failed: {e}")
        
        return DimensionScore(
            name="Tech Debt",
            score=score,
            weight=self.WEIGHT,
            details=details,
            errors=errors,
        )


class DocCoverageCollector:
    """Collect documentation coverage metrics."""
    
    WEIGHT = 0.15
    
    def collect(self) -> DimensionScore:
        """Collect documentation coverage metrics."""
        details = {}
        errors = []
        
        # Count documentation files
        docs_dir = PROJECT_ROOT / "docs"
        
        if docs_dir.exists():
            md_files = list(docs_dir.rglob("*.md"))
            details["doc_files"] = len(md_files)
            
            # Check for key documentation
            key_docs = [
                "docs/user/USER_MANUAL.md",
                "docs/user/INSTALLATION.md",
                "docs/user/FAQ.md",
                "docs/api/API_REFERENCE.md",
                "docs/developer/TESTING_GUIDE.md",
                "CHANGELOG.md",
                "README.md",
            ]
            
            present = sum(1 for doc in key_docs if (PROJECT_ROOT / doc).exists())
            details["key_docs_present"] = present
            details["key_docs_total"] = len(key_docs)
            
            # Score based on key doc presence
            score = (present / len(key_docs)) * 100
        else:
            score = 0.0
            errors.append("Documentation directory not found")
        
        return DimensionScore(
            name="Documentation",
            score=score,
            weight=self.WEIGHT,
            details=details,
            errors=errors,
        )


class SecurityCollector:
    """Collect security metrics."""
    
    WEIGHT = 0.10
    
    def collect(self) -> DimensionScore:
        """Collect security metrics."""
        details = {}
        errors = []
        score = 100.0  # Start with perfect score
        
        # Check for secrets baseline
        secrets_baseline = PROJECT_ROOT / ".secrets.baseline"
        if secrets_baseline.exists():
            details["secrets_baseline_exists"] = True
        else:
            details["secrets_baseline_exists"] = False
            score -= 20
            errors.append("No secrets baseline file")
        
        # Check for security headers middleware
        security_headers = PROJECT_ROOT / "backend" / "api" / "middleware" / "security_headers.py"
        if security_headers.exists():
            details["security_headers_exists"] = True
        else:
            details["security_headers_exists"] = False
            score -= 15
        
        # Check for input validation middleware
        input_validation = PROJECT_ROOT / "backend" / "api" / "middleware" / "input_validation.py"
        if input_validation.exists():
            details["input_validation_exists"] = True
        else:
            details["input_validation_exists"] = False
            score -= 15
        
        # Try running detect-secrets scan
        try:
            result = subprocess.run(
                ["detect-secrets", "scan", "--baseline", ".secrets.baseline"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(PROJECT_ROOT)
            )
            
            if result.returncode == 0:
                details["secrets_scan_passed"] = True
            else:
                details["secrets_scan_passed"] = False
                score -= 30
                
        except FileNotFoundError:
            details["secrets_scan_available"] = False
        except Exception as e:
            errors.append(f"Security scan failed: {e}")
        
        return DimensionScore(
            name="Security",
            score=max(0.0, score),
            weight=self.WEIGHT,
            details=details,
            errors=errors,
        )


class QualityScorecard:
    """Main quality scorecard generator."""
    
    def __init__(self, threshold: float = 85.0):
        self.threshold = threshold
        self.collectors = {
            "gates": GateStatusCollector(),
            "coverage": CoverageCollector(),
            "build": BuildHealthCollector(),
            "debt": TechDebtCollector(),
            "docs": DocCoverageCollector(),
            "security": SecurityCollector(),
        }
    
    def generate(self) -> ScorecardResult:
        """Generate complete quality scorecard."""
        dimensions = {}
        
        for name, collector in self.collectors.items():
            try:
                dimensions[name] = collector.collect()
            except Exception as e:
                dimensions[name] = DimensionScore(
                    name=name,
                    score=0.0,
                    weight=collector.WEIGHT,
                    errors=[f"Collection failed: {e}"]
                )
        
        # Calculate overall score
        overall_score = sum(dim.weighted_score for dim in dimensions.values())
        
        # Determine grade
        grade = self._calculate_grade(overall_score)
        
        return ScorecardResult(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            grade=grade,
            dimensions=dimensions,
            passed=overall_score >= self.threshold,
            threshold=self.threshold,
        )
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


def format_markdown(result: ScorecardResult) -> str:
    """Format scorecard as Markdown."""
    lines = [
        "# VoiceStudio Quality Scorecard",
        "",
        f"**Generated**: {result.timestamp}",
        f"**Overall Score**: {result.overall_score:.1f}/100 ({result.grade})",
        f"**Status**: {'PASS' if result.passed else 'FAIL'} (threshold: {result.threshold})",
        "",
        "## Dimension Scores",
        "",
        "| Dimension | Score | Weight | Weighted |",
        "|-----------|-------|--------|----------|",
    ]
    
    for name, dim in result.dimensions.items():
        lines.append(
            f"| {dim.name} | {dim.score:.1f} | {dim.weight*100:.0f}% | {dim.weighted_score:.1f} |"
        )
    
    lines.extend([
        "",
        "## Details",
        "",
    ])
    
    for name, dim in result.dimensions.items():
        lines.append(f"### {dim.name}")
        lines.append("")
        
        if dim.details:
            for key, value in dim.details.items():
                lines.append(f"- **{key}**: {value}")
        
        if dim.errors:
            lines.append("")
            lines.append("**Errors:**")
            for error in dim.errors:
                lines.append(f"- {error}")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate quality scorecard")
    parser.add_argument(
        "--output-format", 
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with non-zero if below threshold"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=85.0,
        help="Quality threshold (default: 85)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: .buildlogs/quality)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir) if args.output_dir else QUALITY_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("VoiceStudio Quality Scorecard Generator")
    print("=" * 60)
    print()
    
    scorecard = QualityScorecard(threshold=args.threshold)
    result = scorecard.generate()
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Output results
    if args.output_format in ["json", "both"]:
        json_path = output_dir / f"scorecard_{timestamp}.json"
        json_path.write_text(json.dumps(result.to_dict(), indent=2))
        print(f"JSON saved: {json_path}")
    
    if args.output_format in ["markdown", "both"]:
        md_path = output_dir / f"scorecard_{timestamp}.md"
        md_path.write_text(format_markdown(result))
        print(f"Markdown saved: {md_path}")
    
    # Print summary
    print()
    print("-" * 60)
    print(f"Overall Score: {result.overall_score:.1f}/100 ({result.grade})")
    print("-" * 60)
    
    for name, dim in result.dimensions.items():
        status = "OK" if dim.score >= 70 else "LOW"
        print(f"  {dim.name:15} {dim.score:5.1f} x {dim.weight*100:3.0f}% = {dim.weighted_score:5.1f} [{status}]")
    
    print("-" * 60)
    print(f"Status: {'PASS' if result.passed else 'FAIL'} (threshold: {args.threshold})")
    print()
    
    # Exit code for CI
    if args.ci and not result.passed:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
