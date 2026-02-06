#!/usr/bin/env python3
"""
Monitor dependencies for new CVEs and vulnerabilities.

Scans Python and .NET dependencies for known security vulnerabilities
and outputs a report. Designed to run daily via GitHub Actions.

Usage:
    python scripts/monitor_cves.py [--output PATH] [--severity LEVEL]

Requirements:
    pip install pip-audit safety

Phase 6.3.4 Security Hardening
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class Vulnerability:
    """Represents a single vulnerability finding."""

    package: str
    installed_version: str
    vulnerability_id: str
    severity: str
    description: str
    fixed_version: Optional[str] = None
    ecosystem: str = "python"
    source: str = "unknown"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "package": self.package,
            "installed_version": self.installed_version,
            "vulnerability_id": self.vulnerability_id,
            "severity": self.severity,
            "description": self.description,
            "fixed_version": self.fixed_version,
            "ecosystem": self.ecosystem,
            "source": self.source,
        }


@dataclass
class ScanReport:
    """Aggregated scan report."""

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "summary": self.summary,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "errors": self.errors,
        }


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def normalize_severity(severity: str) -> str:
    """Normalize severity levels to standard values."""
    severity = severity.upper().strip()
    severity_map = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "MODERATE": "MEDIUM",
        "LOW": "LOW",
        "UNKNOWN": "UNKNOWN",
    }
    return severity_map.get(severity, "UNKNOWN")


def run_pip_audit(project_root: Path) -> list[Vulnerability]:
    """
    Run pip-audit to scan Python dependencies.

    Returns list of vulnerabilities found.
    """
    print("Running pip-audit...")
    vulnerabilities = []

    # Check if pip-audit is installed
    returncode, _, _ = run_command(["python", "-m", "pip_audit", "--version"])
    if returncode != 0:
        print("  pip-audit not found. Installing...")
        run_command(["python", "-m", "pip", "install", "pip-audit"])

    # Run pip-audit in JSON format
    returncode, stdout, stderr = run_command(
        ["python", "-m", "pip_audit", "--format", "json", "--progress-spinner", "off"],
        cwd=project_root,
    )

    if returncode == 0:
        print("  No vulnerabilities found by pip-audit")
        return vulnerabilities

    # Parse JSON output
    try:
        findings = json.loads(stdout)
        if isinstance(findings, dict):
            # New format: {"dependencies": [...]}
            findings = findings.get("dependencies", [])

        for finding in findings:
            if isinstance(finding, dict) and finding.get("vulns"):
                package = finding.get("name", "unknown")
                version = finding.get("version", "unknown")
                for vuln in finding.get("vulns", []):
                    vulnerabilities.append(
                        Vulnerability(
                            package=package,
                            installed_version=version,
                            vulnerability_id=vuln.get("id", "UNKNOWN"),
                            severity=normalize_severity(
                                vuln.get("fix_versions", [""])[0]
                                if vuln.get("fix_versions")
                                else "UNKNOWN"
                            ),
                            description=vuln.get("description", "")[:500],
                            fixed_version=(
                                vuln.get("fix_versions", [None])[0]
                                if vuln.get("fix_versions")
                                else None
                            ),
                            ecosystem="python",
                            source="pip-audit",
                        )
                    )
    except json.JSONDecodeError:
        print(f"  Warning: Could not parse pip-audit output: {stderr}")

    print(f"  Found {len(vulnerabilities)} vulnerabilities via pip-audit")
    return vulnerabilities


def run_safety_check(project_root: Path) -> list[Vulnerability]:
    """
    Run safety to scan Python dependencies.

    Returns list of vulnerabilities found.
    """
    print("Running safety check...")
    vulnerabilities = []

    # Check if safety is installed
    returncode, _, _ = run_command(["safety", "--version"])
    if returncode != 0:
        print("  safety not found. Installing...")
        run_command(["python", "-m", "pip", "install", "safety"])

    # Run safety in JSON format
    returncode, stdout, stderr = run_command(
        ["safety", "check", "--json"],
        cwd=project_root,
    )

    if returncode == 0 and not stdout.strip():
        print("  No vulnerabilities found by safety")
        return vulnerabilities

    # Parse JSON output
    try:
        result = json.loads(stdout)
        # Safety output format varies by version
        vulns = result if isinstance(result, list) else result.get("vulnerabilities", [])

        for vuln in vulns:
            if isinstance(vuln, list):
                # Old format: [package, spec, installed, vuln_desc, vuln_id]
                if len(vuln) >= 5:
                    vulnerabilities.append(
                        Vulnerability(
                            package=vuln[0],
                            installed_version=vuln[2],
                            vulnerability_id=str(vuln[4]),
                            severity="UNKNOWN",
                            description=str(vuln[3])[:500],
                            ecosystem="python",
                            source="safety",
                        )
                    )
            elif isinstance(vuln, dict):
                # New format
                vulnerabilities.append(
                    Vulnerability(
                        package=vuln.get("package_name", "unknown"),
                        installed_version=vuln.get("analyzed_version", "unknown"),
                        vulnerability_id=vuln.get("vulnerability_id", "UNKNOWN"),
                        severity=normalize_severity(vuln.get("severity", "UNKNOWN")),
                        description=vuln.get("advisory", "")[:500],
                        fixed_version=vuln.get("more_info_path"),
                        ecosystem="python",
                        source="safety",
                    )
                )
    except json.JSONDecodeError:
        print("  Warning: Could not parse safety output")

    print(f"  Found {len(vulnerabilities)} vulnerabilities via safety")
    return vulnerabilities


def run_nuget_audit(project_root: Path) -> list[Vulnerability]:
    """
    Run dotnet list package --vulnerable to scan .NET dependencies.

    Returns list of vulnerabilities found.
    """
    print("Running NuGet vulnerability scan...")
    vulnerabilities = []

    sln_file = project_root / "VoiceStudio.sln"
    if not sln_file.exists():
        print("  No solution file found, skipping .NET scan")
        return vulnerabilities

    returncode, stdout, stderr = run_command(
        ["dotnet", "list", str(sln_file), "package", "--vulnerable", "--format", "json"],
        cwd=project_root,
    )

    if returncode != 0:
        # Try without JSON format (older .NET versions)
        returncode, stdout, stderr = run_command(
            ["dotnet", "list", str(sln_file), "package", "--vulnerable"],
            cwd=project_root,
        )

        if returncode != 0:
            print(f"  NuGet scan failed: {stderr}")
            return vulnerabilities

        # Parse text output (basic parsing)
        lines = stdout.split("\n")
        for line in lines:
            if ">" in line and any(sev in line.upper() for sev in ["HIGH", "CRITICAL", "MODERATE"]):
                parts = line.split()
                if len(parts) >= 3:
                    vulnerabilities.append(
                        Vulnerability(
                            package=parts[1] if len(parts) > 1 else "unknown",
                            installed_version=parts[2] if len(parts) > 2 else "unknown",
                            vulnerability_id="NUGET-VULN",
                            severity=normalize_severity(
                                next(
                                    (
                                        p
                                        for p in parts
                                        if p.upper() in ["HIGH", "CRITICAL", "MODERATE", "LOW"]
                                    ),
                                    "UNKNOWN",
                                )
                            ),
                            description=line.strip(),
                            ecosystem="dotnet",
                            source="nuget-audit",
                        )
                    )
        print(f"  Found {len(vulnerabilities)} vulnerabilities via NuGet")
        return vulnerabilities

    # Parse JSON output (newer .NET versions)
    try:
        result = json.loads(stdout)
        for project in result.get("projects", []):
            for framework in project.get("frameworks", []):
                for pkg in framework.get("topLevelPackages", []):
                    for vuln in pkg.get("vulnerabilities", []):
                        vulnerabilities.append(
                            Vulnerability(
                                package=pkg.get("id", "unknown"),
                                installed_version=pkg.get("resolvedVersion", "unknown"),
                                vulnerability_id=vuln.get("advisoryUrl", "UNKNOWN"),
                                severity=normalize_severity(vuln.get("severity", "UNKNOWN")),
                                description=vuln.get("advisoryUrl", ""),
                                ecosystem="dotnet",
                                source="nuget-audit",
                            )
                        )
    except json.JSONDecodeError:
        print("  Warning: Could not parse NuGet JSON output")

    print(f"  Found {len(vulnerabilities)} vulnerabilities via NuGet")
    return vulnerabilities


def deduplicate_vulnerabilities(vulnerabilities: list[Vulnerability]) -> list[Vulnerability]:
    """Remove duplicate vulnerabilities based on package + vulnerability_id."""
    seen = set()
    unique = []
    for vuln in vulnerabilities:
        key = (vuln.package, vuln.vulnerability_id)
        if key not in seen:
            seen.add(key)
            unique.append(vuln)
    return unique


def filter_by_severity(
    vulnerabilities: list[Vulnerability], min_severity: str
) -> list[Vulnerability]:
    """Filter vulnerabilities by minimum severity level."""
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
    min_level = severity_order.get(min_severity.upper(), 0)
    return [v for v in vulnerabilities if severity_order.get(v.severity, 0) >= min_level]


def generate_summary(vulnerabilities: list[Vulnerability]) -> dict:
    """Generate summary statistics."""
    summary = {
        "total": len(vulnerabilities),
        "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0},
        "by_ecosystem": {"python": 0, "dotnet": 0},
        "actionable": 0,
    }

    for vuln in vulnerabilities:
        if vuln.severity in summary["by_severity"]:
            summary["by_severity"][vuln.severity] += 1
        if vuln.ecosystem in summary["by_ecosystem"]:
            summary["by_ecosystem"][vuln.ecosystem] += 1
        if vuln.fixed_version:
            summary["actionable"] += 1

    return summary


def print_report(report: ScanReport) -> None:
    """Print human-readable report to stdout."""
    print("\n" + "=" * 60)
    print("CVE MONITORING REPORT")
    print("=" * 60)
    print(f"Timestamp: {report.timestamp}")
    print(f"Total vulnerabilities: {report.summary.get('total', 0)}")
    print()

    if report.summary.get("total", 0) == 0:
        print("No vulnerabilities found!")
        return

    print("By Severity:")
    for severity, count in report.summary.get("by_severity", {}).items():
        if count > 0:
            print(f"  {severity}: {count}")

    print("\nBy Ecosystem:")
    for ecosystem, count in report.summary.get("by_ecosystem", {}).items():
        if count > 0:
            print(f"  {ecosystem}: {count}")

    print(f"\nActionable (fix available): {report.summary.get('actionable', 0)}")

    print("\nDetails:")
    print("-" * 60)
    for vuln in report.vulnerabilities:
        print(f"\n[{vuln.severity}] {vuln.package} {vuln.installed_version}")
        print(f"  ID: {vuln.vulnerability_id}")
        if vuln.fixed_version:
            print(f"  Fix: Upgrade to {vuln.fixed_version}")
        if vuln.description:
            print(f"  Description: {vuln.description[:200]}...")

    if report.errors:
        print("\nErrors encountered:")
        for error in report.errors:
            print(f"  - {error}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor dependencies for CVEs and vulnerabilities"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output JSON file path (default: .buildlogs/security/cve-report.json)",
    )
    parser.add_argument(
        "--severity",
        "-s",
        choices=["critical", "high", "medium", "low", "all"],
        default="all",
        help="Minimum severity to report (default: all)",
    )
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low", "none"],
        default="none",
        help="Exit with error if vulnerabilities at this level or above (default: none)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON (no human-readable summary)",
    )

    args = parser.parse_args()

    project_root = get_project_root()

    # Set up output path
    if args.output:
        output_path = args.output
    else:
        output_dir = project_root / ".buildlogs" / "security"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "cve-report.json"

    print("VoiceStudio CVE Monitor")
    print(f"Project root: {project_root}")
    print("-" * 50)

    report = ScanReport()
    all_vulnerabilities = []

    # Run Python vulnerability scans
    try:
        all_vulnerabilities.extend(run_pip_audit(project_root))
    except Exception as e:
        report.errors.append(f"pip-audit error: {e}")

    try:
        all_vulnerabilities.extend(run_safety_check(project_root))
    except Exception as e:
        report.errors.append(f"safety error: {e}")

    # Run .NET vulnerability scan
    try:
        all_vulnerabilities.extend(run_nuget_audit(project_root))
    except Exception as e:
        report.errors.append(f"nuget-audit error: {e}")

    # Deduplicate and filter
    all_vulnerabilities = deduplicate_vulnerabilities(all_vulnerabilities)

    if args.severity != "all":
        all_vulnerabilities = filter_by_severity(
            all_vulnerabilities, args.severity.upper()
        )

    report.vulnerabilities = all_vulnerabilities
    report.summary = generate_summary(all_vulnerabilities)

    # Write JSON report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)

    # Print human-readable report
    if not args.json_only:
        print_report(report)
        print("\n" + "-" * 50)
        print(f"Report written to: {output_path}")

    # Determine exit code based on --fail-on
    if args.fail_on != "none":
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        fail_level = severity_order.get(args.fail_on.lower(), 0)

        for vuln in report.vulnerabilities:
            vuln_level = severity_order.get(vuln.severity.lower(), 0)
            if vuln_level >= fail_level:
                print(
                    f"\nFailing due to {vuln.severity} vulnerability: "
                    f"{vuln.package} ({vuln.vulnerability_id})"
                )
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
