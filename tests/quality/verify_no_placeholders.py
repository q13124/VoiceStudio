"""
Placeholder Verification Script
Comprehensive scan of all code files for forbidden placeholder terms.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent

# Complete list of forbidden terms from MASTER_RULES_COMPLETE.md
FORBIDDEN_TERMS = [
    # Bookmarks
    "TODO",
    "FIXME",
    "NOTE",
    "HACK",
    "REMINDER",
    "XXX",
    "WARNING",
    "CAUTION",
    "BUG",
    "ISSUE",
    "REFACTOR",
    "OPTIMIZE",
    "REVIEW",
    "CHECK",
    "VERIFY",
    "TEST",
    "DEBUG",
    "DEPRECATED",
    "OBSOLETE",
    # Placeholders
    "placeholder",
    "stub",
    "dummy",
    "mock",
    "fake",
    "sample",
    "temporary",
    "NotImplementedError",
    "NotImplementedException",
    # Status words
    "incomplete",
    "unfinished",
    "partial",
    "coming soon",
    "not yet",
    "eventually",
    "later",
    "for now",
    "temporary",
    "needs",
    "requires",
    "missing",
    "WIP",
    "tbd",
    "tba",
    "tbc",
    # Variations
    "to be done",
    "will be implemented",
    "coming soon",
    "not yet",
    "eventually",
    "later",
    "for now",
    "temporary",
    "in progress",
    "under development",
    "work in progress",
]

# File patterns to check
INCLUDE_PATTERNS = [
    "**/*.py",
    "**/*.cs",
    "**/*.xaml",
    "**/*.json",
    "**/*.md",
]

# Directories to exclude
EXCLUDE_DIRS = [
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache",
    "tests",  # Exclude test files
    "test_data",  # Exclude test data
]

# Files to exclude
EXCLUDE_FILES = [
    "test_*.py",
    "*_test.py",
    "conftest.py",
    "verify_*.py",  # Exclude verification scripts themselves
    "calculate_*.py",  # Exclude calculation scripts
    "run_*.py",  # Exclude test runners
    "README*.md",  # Exclude README files
    "*.iss",  # Inno Setup scripts
    "*.wxs",  # WiX scripts
]

# Contexts where forbidden terms are acceptable
ACCEPTABLE_CONTEXTS = [
    ("partial", "class"),  # C# partial classes
    ("sample", "rate"),  # Audio sample rate
    ("sample", "count"),  # Sample count
    ("sample", "index"),  # Sample index
    ("sample", "data"),  # Sample data (audio)
    ("sample", "file"),  # Sample files
    ("test", "file"),  # Test files (in test directory)
    ("test", "data"),  # Test data
    ("test", "profile"),  # Test profiles
    ("test", "project"),  # Test projects
    ("check", "health"),  # Health check
    ("check", "sum"),  # Checksum
    ("verify", "model"),  # Model verification
    ("verify", "checksum"),  # Checksum verification
    ("review", "code"),  # Code review (documentation)
    ("note", "field"),  # Notes field
    ("warning", "level"),  # Warning level (error handling)
    ("warning", "severity"),  # Warning severity
    ("placeholder", "text"),  # UI PlaceholderText (acceptable)
]


def should_check_file(file_path: Path) -> bool:
    """Determine if file should be checked."""
    # Check if in exclude directory
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in str(file_path):
            return False

    # Check if matches exclude pattern
    for exclude_pattern in EXCLUDE_FILES:
        if file_path.match(exclude_pattern):
            return False

    # Check if matches include pattern
    for include_pattern in INCLUDE_PATTERNS:
        if file_path.match(include_pattern):
            return True

    return False


def check_file_for_violations(file_path: Path) -> List[Tuple[int, str, str]]:
    """Check file for forbidden terms and return violations."""
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()
                line_stripped = line.strip()

                for term in FORBIDDEN_TERMS:
                    term_lower = term.lower()

                    if term_lower in line_lower:
                        violations.append((line_num, term, line_stripped[:100]))
    except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")

    return violations


def scan_directory(directory: Path) -> Dict[str, List[Tuple[int, str, str]]]:
    """Scan directory for placeholder violations."""
    violations_by_file = {}

    for file_path in directory.rglob("*"):
        if file_path.is_file() and should_check_file(file_path):
            violations = check_file_for_violations(file_path)
            if violations:
                violations_by_file[str(file_path.relative_to(project_root))] = (
                    violations
                )

    return violations_by_file


def generate_report(violations_by_file: Dict[str, List[Tuple[int, str, str]]]) -> str:
    """Generate violation report."""
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("PLACEHOLDER VERIFICATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().isoformat()}")
    report_lines.append(f"Total files with violations: {len(violations_by_file)}")
    report_lines.append("")

    total_violations = sum(len(v) for v in violations_by_file.values())
    report_lines.append(f"Total violations found: {total_violations}")
    report_lines.append("")

    for file_path, violations in sorted(violations_by_file.items()):
        report_lines.append(f"\nFile: {file_path}")
        report_lines.append(f"  Violations: {len(violations)}")
        report_lines.append("")

        for line_num, term, line_content in violations[:10]:
            report_lines.append(f"  Line {line_num}: Found '{term}'")
            report_lines.append(f"    {line_content}")

        if len(violations) > 10:
            report_lines.append(f"  ... and {len(violations) - 10} more violations")

    report_lines.append("")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def main():
    """Main function."""
    logger.info("Starting placeholder verification scan...")
    logger.info(f"Project root: {project_root}")

    violations_by_file = scan_directory(project_root)

    if violations_by_file:
        report = generate_report(violations_by_file)
        print(report)

        report_file = project_root / "placeholder_verification_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.error(f"Found {len(violations_by_file)} files with violations")
        logger.error(f"Report saved to: {report_file}")

        return 1
    else:
        logger.info("No placeholder violations found!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
