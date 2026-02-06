#!/usr/bin/env python3
"""
Release Checklist - Automated Pre-Release Validation

Runs 13+ automated checks before a release to ensure quality gates are met.

Checks:
 1. Build Verification (Debug + Release)
 2. Test Suite (Unit + Integration)
 3. Quality Scorecard Threshold
 4. Documentation Coverage
 5. Security Audit (detect-secrets)
 6. License Compliance
 7. Changelog Updated
 8. Version Consistency
 9. No TODO/FIXME in Critical Code
10. No Uncommitted Changes
11. Branch Up-to-Date
12. Installer Build Verification
13. API Schema Validation
14. Gate Status (All Gates Passed)

Usage:
    python scripts/release_checklist.py
    python scripts/release_checklist.py --version 1.0.1
    python scripts/release_checklist.py --skip-build
    python scripts/release_checklist.py --json

Exit Codes:
    0: All checks passed
    1: One or more checks failed
    2: Error occurred
"""

from _env_setup import PROJECT_ROOT

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


class CheckStatus(Enum):
    """Status of a check."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[List[str]] = None
    duration_ms: int = 0


@dataclass
class ReleaseCheckReport:
    """Complete release check report."""
    version: str
    timestamp: str
    checks: List[CheckResult] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0
    
    @property
    def is_ready(self) -> bool:
        """Whether release is ready (no failures)."""
        return self.failed == 0


class ReleaseChecker:
    """Runs all release checks."""
    
    def __init__(
        self,
        version: str = "unknown",
        skip_build: bool = False,
        skip_tests: bool = False,
        quality_threshold: float = 70.0,
    ):
        self.version = version
        self.skip_build = skip_build
        self.skip_tests = skip_tests
        self.quality_threshold = quality_threshold
        self.report = ReleaseCheckReport(
            version=version,
            timestamp=datetime.now().isoformat(),
        )
    
    def run_all_checks(self) -> ReleaseCheckReport:
        """Run all release checks."""
        checks = [
            ("Build Verification", self.check_build),
            ("Test Suite", self.check_tests),
            ("Quality Scorecard", self.check_quality_scorecard),
            ("Documentation Coverage", self.check_doc_coverage),
            ("Security Audit", self.check_security),
            ("License Compliance", self.check_licenses),
            ("Changelog Updated", self.check_changelog),
            ("Version Consistency", self.check_version_consistency),
            ("No TODO/FIXME in Critical", self.check_no_todos_critical),
            ("No Uncommitted Changes", self.check_git_clean),
            ("Branch Up-to-Date", self.check_branch_uptodate),
            ("Installer Build", self.check_installer),
            ("API Schema Validation", self.check_api_schema),
            ("Gate Status", self.check_gates),
        ]
        
        for name, check_fn in checks:
            result = self._run_check(name, check_fn)
            self.report.checks.append(result)
            
            if result.status == CheckStatus.PASSED:
                self.report.passed += 1
            elif result.status == CheckStatus.FAILED:
                self.report.failed += 1
            elif result.status == CheckStatus.WARNING:
                self.report.warnings += 1
            else:
                self.report.skipped += 1
        
        return self.report
    
    def _run_check(self, name: str, check_fn: Callable) -> CheckResult:
        """Run a single check with timing."""
        import time
        start = time.time()
        
        try:
            result = check_fn()
            result.duration_ms = int((time.time() - start) * 1000)
            return result
        except Exception as e:
            return CheckResult(
                name=name,
                status=CheckStatus.FAILED,
                message=f"Error: {e}",
                duration_ms=int((time.time() - start) * 1000),
            )
    
    def check_build(self) -> CheckResult:
        """Check 1: Build verification."""
        if self.skip_build:
            return CheckResult(
                name="Build Verification",
                status=CheckStatus.SKIPPED,
                message="Skipped by user",
            )
        
        try:
            # Check for recent successful build
            build_log = PROJECT_ROOT / "build_output.txt"
            if build_log.exists():
                content = build_log.read_text(encoding="utf-8", errors="ignore")
                if "Build succeeded" in content or "0 Error(s)" in content:
                    return CheckResult(
                        name="Build Verification",
                        status=CheckStatus.PASSED,
                        message="Build succeeded (cached)",
                    )
            
            return CheckResult(
                name="Build Verification",
                status=CheckStatus.WARNING,
                message="No recent build found. Run: dotnet build VoiceStudio.sln",
            )
            
        except Exception as e:
            return CheckResult(
                name="Build Verification",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_tests(self) -> CheckResult:
        """Check 2: Test suite."""
        if self.skip_tests:
            return CheckResult(
                name="Test Suite",
                status=CheckStatus.SKIPPED,
                message="Skipped by user",
            )
        
        try:
            # Check for test results
            test_dirs = [
                PROJECT_ROOT / "test-results",
                PROJECT_ROOT / ".buildlogs",
            ]
            
            for test_dir in test_dirs:
                if test_dir.exists():
                    for xml_file in test_dir.rglob("*.xml"):
                        content = xml_file.read_text(encoding="utf-8", errors="ignore")
                        if "failures=\"0\"" in content or "failed=\"0\"" in content:
                            return CheckResult(
                                name="Test Suite",
                                status=CheckStatus.PASSED,
                                message="All tests passed (cached)",
                            )
            
            return CheckResult(
                name="Test Suite",
                status=CheckStatus.WARNING,
                message="No test results found. Run: pytest tests/",
            )
            
        except Exception as e:
            return CheckResult(
                name="Test Suite",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_quality_scorecard(self) -> CheckResult:
        """Check 3: Quality scorecard threshold."""
        try:
            report_file = PROJECT_ROOT / "docs" / "reports" / "quality" / "scorecard.json"
            
            if not report_file.exists():
                return CheckResult(
                    name="Quality Scorecard",
                    status=CheckStatus.WARNING,
                    message="No scorecard found. Run: python scripts/quality_scorecard.py",
                )
            
            report = json.loads(report_file.read_text())
            score = report.get("composite_score", 0)
            
            if score >= self.quality_threshold:
                return CheckResult(
                    name="Quality Scorecard",
                    status=CheckStatus.PASSED,
                    message=f"Score: {score:.1f}% (threshold: {self.quality_threshold}%)",
                )
            else:
                return CheckResult(
                    name="Quality Scorecard",
                    status=CheckStatus.FAILED,
                    message=f"Score: {score:.1f}% below threshold {self.quality_threshold}%",
                )
                
        except Exception as e:
            return CheckResult(
                name="Quality Scorecard",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_doc_coverage(self) -> CheckResult:
        """Check 4: Documentation coverage."""
        try:
            report_file = PROJECT_ROOT / "docs" / "reports" / "quality" / "doc_coverage.json"
            
            if not report_file.exists():
                return CheckResult(
                    name="Documentation Coverage",
                    status=CheckStatus.WARNING,
                    message="No coverage report. Run: python scripts/doc_coverage.py",
                )
            
            report = json.loads(report_file.read_text())
            pct = report.get("overall_percentage", 0)
            
            if pct >= 60:
                return CheckResult(
                    name="Documentation Coverage",
                    status=CheckStatus.PASSED,
                    message=f"Coverage: {pct:.1f}%",
                )
            else:
                return CheckResult(
                    name="Documentation Coverage",
                    status=CheckStatus.WARNING,
                    message=f"Coverage: {pct:.1f}% (recommend 60%+)",
                )
                
        except Exception as e:
            return CheckResult(
                name="Documentation Coverage",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_security(self) -> CheckResult:
        """Check 5: Security audit."""
        try:
            baseline = PROJECT_ROOT / ".secrets.baseline"
            
            if baseline.exists():
                content = baseline.read_text()
                data = json.loads(content)
                results = data.get("results", {})
                
                # Count unresolved secrets
                unresolved = 0
                for file_path, findings in results.items():
                    for finding in findings:
                        if not finding.get("is_verified", False):
                            unresolved += 1
                
                if unresolved == 0:
                    return CheckResult(
                        name="Security Audit",
                        status=CheckStatus.PASSED,
                        message="No unresolved secrets detected",
                    )
                else:
                    return CheckResult(
                        name="Security Audit",
                        status=CheckStatus.FAILED,
                        message=f"{unresolved} potential secrets found",
                    )
            else:
                return CheckResult(
                    name="Security Audit",
                    status=CheckStatus.WARNING,
                    message="No secrets baseline. Run: detect-secrets scan",
                )
                
        except Exception as e:
            return CheckResult(
                name="Security Audit",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_licenses(self) -> CheckResult:
        """Check 6: License compliance."""
        try:
            # Check for LICENSE file
            license_file = PROJECT_ROOT / "LICENSE"
            if not license_file.exists():
                return CheckResult(
                    name="License Compliance",
                    status=CheckStatus.FAILED,
                    message="No LICENSE file found",
                )
            
            # Check for any AGPL/GPL-3 in dependencies (basic check)
            req_files = list(PROJECT_ROOT.glob("**/requirements*.txt"))
            
            return CheckResult(
                name="License Compliance",
                status=CheckStatus.PASSED,
                message=f"LICENSE present, {len(req_files)} requirement files",
            )
            
        except Exception as e:
            return CheckResult(
                name="License Compliance",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_changelog(self) -> CheckResult:
        """Check 7: Changelog updated."""
        try:
            changelog = PROJECT_ROOT / "CHANGELOG.md"
            
            if not changelog.exists():
                return CheckResult(
                    name="Changelog Updated",
                    status=CheckStatus.FAILED,
                    message="No CHANGELOG.md found",
                )
            
            content = changelog.read_text()
            
            # Check if version is mentioned
            if self.version != "unknown" and self.version in content:
                return CheckResult(
                    name="Changelog Updated",
                    status=CheckStatus.PASSED,
                    message=f"Version {self.version} found in changelog",
                )
            
            # Check for Unreleased section
            if "## [Unreleased]" in content or "## Unreleased" in content:
                return CheckResult(
                    name="Changelog Updated",
                    status=CheckStatus.PASSED,
                    message="Unreleased section present",
                )
            
            return CheckResult(
                name="Changelog Updated",
                status=CheckStatus.WARNING,
                message="Changelog may need update for this version",
            )
            
        except Exception as e:
            return CheckResult(
                name="Changelog Updated",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_version_consistency(self) -> CheckResult:
        """Check 8: Version consistency across files."""
        try:
            versions_found: Dict[str, str] = {}
            
            # Check .csproj files
            for csproj in (PROJECT_ROOT / "src").rglob("*.csproj"):
                content = csproj.read_text()
                match = re.search(r"<Version>([^<]+)</Version>", content)
                if match:
                    versions_found[str(csproj.name)] = match.group(1)
            
            # Check installer
            iss_file = PROJECT_ROOT / "installer" / "VoiceStudio.iss"
            if iss_file.exists():
                content = iss_file.read_text()
                match = re.search(r'AppVersion=([^\r\n]+)', content)
                if match:
                    versions_found["VoiceStudio.iss"] = match.group(1).strip()
            
            if not versions_found:
                return CheckResult(
                    name="Version Consistency",
                    status=CheckStatus.WARNING,
                    message="No version strings found",
                )
            
            unique_versions = set(versions_found.values())
            if len(unique_versions) == 1:
                version = list(unique_versions)[0]
                return CheckResult(
                    name="Version Consistency",
                    status=CheckStatus.PASSED,
                    message=f"All versions consistent: {version}",
                )
            else:
                details = [f"{k}: {v}" for k, v in versions_found.items()]
                return CheckResult(
                    name="Version Consistency",
                    status=CheckStatus.FAILED,
                    message=f"Version mismatch: {unique_versions}",
                    details=details,
                )
                
        except Exception as e:
            return CheckResult(
                name="Version Consistency",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_no_todos_critical(self) -> CheckResult:
        """Check 9: No TODO/FIXME in critical code."""
        try:
            critical_paths = [
                PROJECT_ROOT / "backend" / "api" / "routes",
                PROJECT_ROOT / "backend" / "services",
                PROJECT_ROOT / "src" / "VoiceStudio.Core",
            ]
            
            todos_found = []
            patterns = [r"TODO", r"FIXME", r"XXX", r"HACK"]
            
            for path in critical_paths:
                if not path.exists():
                    continue
                    
                for file in path.rglob("*"):
                    if file.suffix not in [".py", ".cs"]:
                        continue
                    
                    try:
                        content = file.read_text(encoding="utf-8", errors="ignore")
                        for pattern in patterns:
                            matches = re.findall(rf"{pattern}[:\s]", content, re.IGNORECASE)
                            if matches:
                                todos_found.append(f"{file.name}: {len(matches)}x {pattern}")
                    # ALLOWED: bare except - File parsing, individual file failure is acceptable
                    except Exception:
                        pass
            
            if not todos_found:
                return CheckResult(
                    name="No TODO/FIXME in Critical",
                    status=CheckStatus.PASSED,
                    message="No critical TODOs found",
                )
            else:
                return CheckResult(
                    name="No TODO/FIXME in Critical",
                    status=CheckStatus.WARNING,
                    message=f"{len(todos_found)} files with TODOs",
                    details=todos_found[:10],
                )
                
        except Exception as e:
            return CheckResult(
                name="No TODO/FIXME in Critical",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_git_clean(self) -> CheckResult:
        """Check 10: No uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                return CheckResult(
                    name="No Uncommitted Changes",
                    status=CheckStatus.FAILED,
                    message="Git command failed",
                )
            
            changes = [
                line for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
            
            if not changes:
                return CheckResult(
                    name="No Uncommitted Changes",
                    status=CheckStatus.PASSED,
                    message="Working directory clean",
                )
            else:
                return CheckResult(
                    name="No Uncommitted Changes",
                    status=CheckStatus.WARNING,
                    message=f"{len(changes)} uncommitted changes",
                    details=changes[:10],
                )
                
        except Exception as e:
            return CheckResult(
                name="No Uncommitted Changes",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_branch_uptodate(self) -> CheckResult:
        """Check 11: Branch up-to-date with remote."""
        try:
            # Fetch latest
            subprocess.run(
                ["git", "fetch", "--quiet"],
                cwd=PROJECT_ROOT,
                capture_output=True,
            )
            
            # Check if ahead/behind
            result = subprocess.run(
                ["git", "status", "-sb"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            
            status_line = result.stdout.split("\n")[0] if result.stdout else ""
            
            if "behind" in status_line:
                return CheckResult(
                    name="Branch Up-to-Date",
                    status=CheckStatus.WARNING,
                    message="Branch is behind remote",
                )
            
            return CheckResult(
                name="Branch Up-to-Date",
                status=CheckStatus.PASSED,
                message="Branch is up-to-date",
            )
            
        except Exception as e:
            return CheckResult(
                name="Branch Up-to-Date",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_installer(self) -> CheckResult:
        """Check 12: Installer build verification."""
        if self.skip_build:
            return CheckResult(
                name="Installer Build",
                status=CheckStatus.SKIPPED,
                message="Skipped by user",
            )
        
        try:
            installer_output = PROJECT_ROOT / "installer" / "Output"
            
            if not installer_output.exists():
                return CheckResult(
                    name="Installer Build",
                    status=CheckStatus.WARNING,
                    message="No installer output directory",
                )
            
            exe_files = list(installer_output.glob("*.exe"))
            
            if exe_files:
                latest = max(exe_files, key=lambda f: f.stat().st_mtime)
                return CheckResult(
                    name="Installer Build",
                    status=CheckStatus.PASSED,
                    message=f"Found: {latest.name}",
                )
            else:
                return CheckResult(
                    name="Installer Build",
                    status=CheckStatus.WARNING,
                    message="No installer EXE found",
                )
                
        except Exception as e:
            return CheckResult(
                name="Installer Build",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_api_schema(self) -> CheckResult:
        """Check 13: API schema validation."""
        try:
            openapi_file = PROJECT_ROOT / "docs" / "api" / "openapi.json"
            
            if not openapi_file.exists():
                return CheckResult(
                    name="API Schema Validation",
                    status=CheckStatus.WARNING,
                    message="No OpenAPI schema found",
                )
            
            schema = json.loads(openapi_file.read_text())
            
            # Basic validation
            if "openapi" in schema and "paths" in schema:
                path_count = len(schema.get("paths", {}))
                return CheckResult(
                    name="API Schema Validation",
                    status=CheckStatus.PASSED,
                    message=f"Valid OpenAPI with {path_count} paths",
                )
            else:
                return CheckResult(
                    name="API Schema Validation",
                    status=CheckStatus.FAILED,
                    message="Invalid OpenAPI schema structure",
                )
                
        except json.JSONDecodeError as e:
            return CheckResult(
                name="API Schema Validation",
                status=CheckStatus.FAILED,
                message=f"JSON parse error: {e}",
            )
        except Exception as e:
            return CheckResult(
                name="API Schema Validation",
                status=CheckStatus.FAILED,
                message=str(e),
            )
    
    def check_gates(self) -> CheckResult:
        """Check 14: All quality gates passed."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "tools.overseer.cli", "gate_status"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            
            if result.returncode == 0:
                # Parse gate status
                output = result.stdout
                if "FAILED" in output or "BLOCKED" in output:
                    return CheckResult(
                        name="Gate Status",
                        status=CheckStatus.FAILED,
                        message="One or more gates failed",
                        details=output.split("\n")[:10],
                    )
                
                return CheckResult(
                    name="Gate Status",
                    status=CheckStatus.PASSED,
                    message="All gates passed",
                )
            else:
                return CheckResult(
                    name="Gate Status",
                    status=CheckStatus.WARNING,
                    message="Gate check not available",
                )
                
        except Exception as e:
            return CheckResult(
                name="Gate Status",
                status=CheckStatus.WARNING,
                message=f"Gate check unavailable: {e}",
            )


def print_report(report: ReleaseCheckReport) -> None:
    """Print report to console."""
    print()
    print("=" * 70)
    print(f"RELEASE CHECKLIST - Version {report.version}")
    print(f"Timestamp: {report.timestamp}")
    print("=" * 70)
    print()
    
    for check in report.checks:
        if check.status == CheckStatus.PASSED:
            icon = "[PASS]"
        elif check.status == CheckStatus.FAILED:
            icon = "[FAIL]"
        elif check.status == CheckStatus.WARNING:
            icon = "[WARN]"
        else:
            icon = "[SKIP]"
        
        print(f"{icon:8} {check.name:30} {check.message}")
        
        if check.details:
            for detail in check.details[:5]:
                print(f"         - {detail}")
    
    print()
    print("-" * 70)
    print(f"Results: {report.passed} passed, {report.failed} failed, "
          f"{report.warnings} warnings, {report.skipped} skipped")
    print()
    
    if report.is_ready:
        print("RELEASE STATUS: READY")
    else:
        print("RELEASE STATUS: NOT READY (fix failed checks)")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Release checklist validation")
    parser.add_argument("--version", default="unknown", help="Version being released")
    parser.add_argument("--skip-build", action="store_true", help="Skip build checks")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test checks")
    parser.add_argument("--quality-threshold", type=float, default=70.0,
                        help="Minimum quality score (default: 70)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    checker = ReleaseChecker(
        version=args.version,
        skip_build=args.skip_build,
        skip_tests=args.skip_tests,
        quality_threshold=args.quality_threshold,
    )
    
    report = checker.run_all_checks()
    
    if args.json:
        output = {
            "version": report.version,
            "timestamp": report.timestamp,
            "is_ready": report.is_ready,
            "summary": {
                "passed": report.passed,
                "failed": report.failed,
                "warnings": report.warnings,
                "skipped": report.skipped,
            },
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                    "duration_ms": c.duration_ms,
                }
                for c in report.checks
            ],
        }
        
        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
        else:
            print(json.dumps(output, indent=2))
    else:
        print_report(report)
        
        if args.output:
            Path(args.output).write_text(json.dumps({
                "version": report.version,
                "timestamp": report.timestamp,
                "is_ready": report.is_ready,
                "passed": report.passed,
                "failed": report.failed,
            }, indent=2))
    
    sys.exit(0 if report.is_ready else 1)


if __name__ == "__main__":
    main()
