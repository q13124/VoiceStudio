#!/usr/bin/env python3
"""
Compatibility Drift Checker.

Detects drift between dependency files and the Technical Stack Specification.
Logs compatibility alerts to the audit system.

Usage:
    python scripts/compatibility_checker.py              # Check all
    python scripts/compatibility_checker.py --fix       # Show fix suggestions
    python scripts/compatibility_checker.py --json      # Output as JSON
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _env_setup import PROJECT_ROOT


# Files to monitor for drift
SPEC_FILE = PROJECT_ROOT / "docs" / "design" / "TECHNICAL_STACK_SPECIFICATION.md"
MONITORED_FILES = [
    PROJECT_ROOT / "requirements_engines.txt",
    PROJECT_ROOT / "requirements.txt",
    PROJECT_ROOT / "version_lock.json",
]


def parse_requirements_file(path: Path) -> Dict[str, str]:
    """
    Parse a requirements.txt file.
    
    Returns:
        Dict mapping package name to version constraint
    """
    packages = {}
    if not path.exists():
        return packages
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse package==version, package>=version, etc.
            match = re.match(r"([a-zA-Z0-9_-]+)([<>=!~]+)(.+)", line)
            if match:
                packages[match.group(1).lower()] = f"{match.group(2)}{match.group(3)}"
            elif not line.startswith("-"):
                # Package name only
                packages[line.lower()] = ""
    
    return packages


def parse_version_lock(path: Path) -> Dict[str, str]:
    """
    Parse version_lock.json file.
    
    Returns:
        Dict mapping package name to version
    """
    if not path.exists():
        return {}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle different structures
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, str):
                    result[key.lower()] = value
                elif isinstance(value, dict) and "version" in value:
                    result[key.lower()] = value["version"]
            return result
    # Best effort - failure is acceptable here
    except (json.JSONDecodeError, IOError):
        pass
    
    return {}


def parse_spec_file(path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Parse the Technical Stack Specification for pinned versions.
    
    Returns:
        Dict mapping package name to spec info
    """
    specs = {}
    if not path.exists():
        return specs
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Look for version specifications in tables or lists
    # Pattern: | package | version | or - package: version
    table_pattern = re.compile(
        r"\|\s*([a-zA-Z0-9_-]+)\s*\|\s*([0-9.]+[a-zA-Z0-9.-]*)\s*\|"
    )
    list_pattern = re.compile(
        r"-\s*\*?\*?([a-zA-Z0-9_-]+)\*?\*?:\s*([0-9.]+[a-zA-Z0-9.-]*)"
    )
    
    for match in table_pattern.finditer(content):
        package = match.group(1).lower()
        version = match.group(2)
        specs[package] = {"version": version, "source": "table"}
    
    for match in list_pattern.finditer(content):
        package = match.group(1).lower()
        version = match.group(2)
        if package not in specs:
            specs[package] = {"version": version, "source": "list"}
    
    return specs


def compare_versions(spec_version: str, actual_version: str) -> str:
    """
    Compare two version strings.
    
    Returns:
        "match", "drift", or "unknown"
    """
    if not spec_version or not actual_version:
        return "unknown"
    
    # Remove operators from actual version
    actual_clean = re.sub(r"^[<>=!~]+", "", actual_version)
    
    if spec_version == actual_clean:
        return "match"
    
    # Check if actual is compatible (starts with spec)
    if actual_clean.startswith(spec_version.rstrip(".")):
        return "match"
    
    return "drift"


def check_drift() -> List[Dict[str, Any]]:
    """
    Check for compatibility drift.
    
    Returns:
        List of drift issues
    """
    issues = []
    
    # Parse spec
    spec = parse_spec_file(SPEC_FILE)
    
    # Parse actual versions from monitored files
    actual = {}
    for path in MONITORED_FILES:
        if path.suffix == ".txt":
            actual.update(parse_requirements_file(path))
        elif path.suffix == ".json":
            actual.update(parse_version_lock(path))
    
    # Compare
    for package, spec_info in spec.items():
        spec_version = spec_info.get("version", "")
        actual_version = actual.get(package, "")
        
        status = compare_versions(spec_version, actual_version)
        
        if status == "drift":
            issues.append({
                "package": package,
                "expected": spec_version,
                "actual": actual_version or "not found",
                "severity": "warning",
                "message": f"Version drift: {package} expected {spec_version}, found {actual_version or 'none'}",
            })
        elif status == "unknown" and actual_version:
            issues.append({
                "package": package,
                "expected": spec_version,
                "actual": actual_version,
                "severity": "info",
                "message": f"Unable to verify: {package} (spec: {spec_version}, actual: {actual_version})",
            })
    
    return issues


def log_drift_issues(issues: List[Dict[str, Any]]):
    """Log drift issues to audit system."""
    try:
        from app.core.audit import get_audit_logger
        audit_logger = get_audit_logger()
        
        for issue in issues:
            audit_logger.log_compatibility_drift(
                file_path="requirements",
                expected=issue["expected"],
                actual=issue["actual"],
                component=issue["package"],
            )
    except ImportError:
        pass  # Audit system not available


def main():
    parser = argparse.ArgumentParser(
        description="Compatibility Drift Checker"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show fix suggestions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Log issues to audit system",
    )
    
    args = parser.parse_args()
    
    issues = check_drift()
    
    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        if not issues:
            print("No compatibility drift detected")
        else:
            print(f"Found {len(issues)} issue(s):\n")
            for issue in issues:
                severity = issue["severity"].upper()
                print(f"[{severity}] {issue['message']}")
                
                if args.fix:
                    print(f"  Fix: Update {issue['package']} to {issue['expected']}")
            
            print()
    
    if args.log and issues:
        log_drift_issues(issues)
        print(f"Logged {len(issues)} issue(s) to audit system")
    
    # Return non-zero if there are warning-level issues
    warnings = [i for i in issues if i["severity"] == "warning"]
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
