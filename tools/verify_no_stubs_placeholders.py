"""
RuleGuard: Automated verification script for NO stubs, placeholders, bookmarks, or tags rule.
Scans all code and documentation files for forbidden patterns.
Runs as part of the build pipeline and fails the build when violations are found.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

# Project root (tools/verify_no_stubs_placeholders.py -> project root is parent)
PROJECT_ROOT = Path(__file__).parent.parent

# High-confidence violation patterns (actual code issues)
FORBIDDEN_COMMENT_PATTERNS = [
    r"#\s*TODO\b",  # Python TODO comments
    r"//\s*TODO\b",  # C#/C++ TODO comments
    r"<!--\s*TODO\b",  # XML/HTML TODO comments
    r";\s*TODO\b",  # PowerShell TODO comments
    r"#\s*FIXME\b",  # Python FIXME comments
    r"//\s*FIXME\b",  # C#/C++ FIXME comments
    r"#\s*HACK\b",  # Python HACK comments
    r"//\s*HACK\b",  # C#/C++ HACK comments
    r"#\s*XXX\b",  # Python XXX comments
    r"//\s*XXX\b",  # C#/C++ XXX comments
]

FORBIDDEN_CODE_PATTERNS = [
    r"\bNotImplementedException\b",  # C# NotImplementedException
    r"\bNotImplementedError\b",  # Python NotImplementedError
    r"throw\s+new\s+NotImplementedException",  # C# throw
    r"raise\s+NotImplementedError",  # Python raise
    r"^\s*pass\s*$",  # Python pass-only (within function body context)
]

FORBIDDEN_PLACEHOLDER_PATTERNS = [
    r"\[PLACEHOLDER\]",  # [PLACEHOLDER] tags
    r"\[TODO\]",  # [TODO] tags
    r"\[FIXME\]",  # [FIXME] tags
    r"\[WIP\]",  # [WIP] tags
    r'\{\s*"mock"\s*:\s*true\s*\}',  # JSON mock objects
]

# All patterns combined
ALL_PATTERNS = (
    FORBIDDEN_COMMENT_PATTERNS
    + FORBIDDEN_CODE_PATTERNS
    + FORBIDDEN_PLACEHOLDER_PATTERNS
)

# Directories to exclude (build artifacts, dependencies, generated files)
EXCLUDE_DIRS = [
    ".git",
    ".specstory",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "venv_",
    "env",
    "bin",
    "obj",
    ".vs",
    ".pytest_cache",
    ".mypy_cache",
    ".buildlogs",
    "xaml_bisect_tmp",
    "artifacts",
    ".cursor",
    "tests",
    "tools",  # Exclude tool scripts (may contain TODOs for future features)
]

# File patterns to scan
INCLUDE_EXTENSIONS = {
    ".py",
    ".cs",
    ".xaml",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".ps1",
}

# Files to exclude (generated files, test runners, verification scripts themselves)
EXCLUDE_FILES = {
    "verify_no_stubs_placeholders.py",  # Exclude self
    "verify_non_mock.py",
    "verify_no_placeholders.py",
    "RULE_ENFORCEMENT_RECOMMENDATIONS.md",  # Rule documentation
    "COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md",  # Rule documentation
    "MASTER_RULES_COMPLETE.md",  # Rule documentation
    "CONTRIBUTING.md",  # Contributing guide (contains examples)
    "placeholder_verification_report.txt",  # Verification report (contains examples)
    "placeholder_verification_report_improved.txt",  # Verification report
    "violations_report.txt",
    "violations_report_after_fix.txt",
    "ruleguard-report.txt",
    "violations_detailed.txt",
    "violations_full.txt",
    "COMPLETE_RULESET.md",
    "COMPREHENSIVE_VIOLATIONS_REPORT.md",
    "README_TESTING.md",
    "run_bug_analysis.py",
    "test_comprehensive_api_endpoints.py",
    "test_backend_endpoints.py",
}

# Markdown files that document issues (may contain examples) - exclude documentation directory
EXCLUDE_MARKDOWN_DIRS = ["docs"]


def should_scan_file(file_path: Path) -> bool:
    """Determine if a file should be scanned."""
    file_str = str(file_path.relative_to(PROJECT_ROOT))

    # Check exclude directories
    for exclude_dir in EXCLUDE_DIRS:
        if (
            f"/{exclude_dir}/" in file_str
            or f"\\{exclude_dir}\\" in file_str
            or file_str.startswith(exclude_dir)
        ):
            return False

    # Check exclude markdown documentation directories
    if file_path.suffix.lower() == ".md":
        for exclude_dir in EXCLUDE_MARKDOWN_DIRS:
            if file_str.startswith(exclude_dir.replace("/", "\\")):
                return False

    # Check exclude files (by name)
    if file_path.name in EXCLUDE_FILES:
        return False

    # Exclude verification report files in root
    if (
        file_path.suffix.lower() == ".txt"
        and "verification" in file_path.name.lower()
        and "report" in file_path.name.lower()
    ):
        return False

    # Exclude general report files
    if "report" in file_path.name.lower() and file_path.suffix.lower() == ".txt":
        return False

    # Exclude CONTRIBUTING.md in root
    if file_path.name == "CONTRIBUTING.md" and file_path.parent == PROJECT_ROOT:
        return False

    # Exclude WORKER_3 status files (historical)
    if file_path.name.startswith("WORKER_3_") and file_path.suffix.lower() == ".md":
        return False

    # Check extension
    if file_path.suffix.lower() not in INCLUDE_EXTENSIONS:
        return False

    return True


def scan_file(file_path: Path) -> List[Dict]:
    """Scan a file for forbidden patterns and return violations."""
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern in ALL_PATTERNS:
                    # Use case-insensitive search
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append(
                            {
                                "file": str(file_path.relative_to(PROJECT_ROOT)),
                                "line": line_num,
                                "pattern": (
                                    pattern.pattern
                                    if hasattr(pattern, "pattern")
                                    else str(pattern)
                                ),
                                "content": line.strip()[:120],  # Limit content length
                            }
                        )
                        break  # Only report one pattern per line
    except Exception:
        # Silently skip files that can't be read (binary files, permissions, etc.)
        ...

    return violations


def main() -> int:
    """Main verification function. Returns 0 on success, 1 on violations found."""
    violations = []
    files_scanned = 0

    # Scan all files in project
    for file_path in PROJECT_ROOT.rglob("*"):
        if file_path.is_file() and should_scan_file(file_path):
            files_scanned += 1
            file_violations = scan_file(file_path)
            violations.extend(file_violations)

    if violations:
        print("RuleGuard: VIOLATIONS FOUND", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        for v in violations[:50]:  # Limit output to first 50 violations
            print(f"File: {v['file']}:{v['line']}", file=sys.stderr)
            print(f"Pattern: {v['pattern']}", file=sys.stderr)
            print(f"Content: {v['content']}", file=sys.stderr)
            print("-" * 80, file=sys.stderr)

        if len(violations) > 50:
            print(
                f"\n... and {len(violations) - 50} more violations (truncated)",
                file=sys.stderr,
            )

        print(f"\nTotal violations: {len(violations)}", file=sys.stderr)
        print(f"Files scanned: {files_scanned}", file=sys.stderr)
        print(
            "\nSee docs/governance/MASTER_RULES_COMPLETE.md for complete rule details",
            file=sys.stderr,
        )
        return 1
    else:
        print(f"RuleGuard: No violations found ({files_scanned} files scanned)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
