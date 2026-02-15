#!/usr/bin/env python3
"""
VoiceStudio Non-Mock Code Verification Tool

Automatically checks code for mock outputs, placeholders, stubs, and incomplete implementations.

Usage:
    python tools/verify_non_mock.py                    # Check all code
    python tools/verify_non_mock.py --path backend/    # Check specific directory
    python tools/verify_non_mock.py --strict          # Strict mode (fails on warnings)
    python tools/verify_non_mock.py --fix              # Auto-fix simple issues (experimental)
"""

import argparse
import logging
import re
import sys
from pathlib import Path

# Fix Windows console encoding for emoji
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Patterns to detect mock/placeholder code
MOCK_PATTERNS = {
    "mock_return": [
        r'return\s+\{\s*["\']mock["\']\s*:',
        r'return\s+\{\s*["\']Mock["\']\s*:',
        r"return\s+new\s+\w+\s*\{\s*Mock\s*=",
        r"return\s+\{\s*mock_audio\s*:",
        r"return\s+\{\s*mock_data\s*:",
    ],
    "todo_comment": [
        r"#\s*TODO:",
        r"//\s*TODO:",
        r"#\s*TODO\s+implement",
        r"//\s*TODO\s+implement",
        r"#\s*TODO\s+add",
        r"//\s*TODO\s+add",
    ],
    "placeholder": [
        r"\[PLACEHOLDER\]",
        r"placeholder",
        r"Placeholder",
        r"PLACEHOLDER",
    ],
    "not_implemented": [
        r"NotImplementedException",
        r"raise\s+NotImplementedError",
        r"throw\s+new\s+NotImplementedException",
    ],
    "pass_only": [
        r"^\s*def\s+\w+.*:\s*$.*^\s*pass\s*$",
        r"^\s*async\s+def\s+\w+.*:\s*$.*^\s*pass\s*$",
    ],
    "empty_function": [
        r"^\s*def\s+\w+.*:\s*$.*^\s*$",  # Function with only docstring/comments
    ],
    "coming_soon": [
        r"coming\s+soon",
        r"Coming\s+Soon",
        r"COMING\s+SOON",
    ],
    "hardcoded_filler": [
        r'["\']test["\']',
        r'["\']example["\']',
        r'["\']dummy["\']',
        r'["\']fake["\']',
        r"Fake",
        r"Dummy",
    ],
}

# File extensions to check
CODE_EXTENSIONS = {
    ".py",
    ".cs",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
}

# Directories to exclude
EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
    "bin",
    "obj",
    ".vs",
    ".vscode",
    "venv",
    "env",
    ".venv",
    "build",
    "dist",
}


class MockCodeDetector:
    """Detects mock code, placeholders, and incomplete implementations."""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.issues: list[dict] = []
        self.file_count = 0
        self.issue_count = 0

    def check_file(self, file_path: Path) -> list[dict]:
        """Check a single file for mock code patterns."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for pattern_type, patterns in MOCK_PATTERNS.items():
                for pattern in patterns:
                    # Check each line
                    for line_num, line in enumerate(lines, 1):
                        # Skip test mode exceptions
                        if "TEST_MODE" in line or "test_mode" in line:
                            continue

                        match = re.search(pattern, line, re.IGNORECASE | re.MULTILINE)
                        if match:
                            # Additional context check for false positives
                            if self._is_false_positive(line, pattern_type):
                                continue

                            issues.append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "type": pattern_type,
                                    "pattern": pattern,
                                    "content": line.strip(),
                                    "severity": (
                                        "error"
                                        if pattern_type
                                        in ["mock_return", "not_implemented"]
                                        else "warning"
                                    ),
                                }
                            )

        except Exception as e:
            logger.warning(f"Error checking {file_path}: {e}")

        return issues

    def _is_false_positive(self, line: str, pattern_type: str) -> bool:
        """Check if a match is a false positive."""
        line_lower = line.lower()

        # Allow test mode mocks
        if "test_mode" in line_lower or "TEST_MODE" in line:
            return True

        # Allow test files to have test data
        if "test" in line_lower and ("test" in pattern_type or "test" in line_lower):
            # Check if it's actually test code, not production mock
            if "def test_" in line_lower or "@pytest" in line_lower:
                return True

        # Allow documentation examples
        return bool("# Example:" in line or "// Example:" in line)

    def check_directory(self, directory: Path) -> list[dict]:
        """Recursively check all code files in a directory."""
        all_issues = []

        for file_path in directory.rglob("*"):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
                continue

            # Check only code files
            if file_path.suffix not in CODE_EXTENSIONS:
                continue

            if not file_path.is_file():
                continue

            self.file_count += 1
            issues = self.check_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def print_report(self, issues: list[dict]):
        """Print a formatted report of all issues."""
        if not issues:
            print("\n[OK] No mock code or placeholders detected!")
            print(f"   Checked {self.file_count} files")
            return

        # Group by severity
        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]

        print(f"\n{'='*80}")
        print("Mock Code Detection Report")
        print(f"{'='*80}")
        print(f"Files checked: {self.file_count}")
        print(f"Total issues: {len(issues)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"{'='*80}\n")

        # Group by file
        by_file: dict[str, list[dict]] = {}
        for issue in issues:
            file_path = issue["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)

        # Print issues by file
        for file_path, file_issues in sorted(by_file.items()):
            print(f"\n[FILE] {file_path}")
            print(f"   {len(file_issues)} issue(s)")

            for issue in sorted(file_issues, key=lambda x: x["line"]):
                severity_icon = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
                print(f"   {severity_icon} Line {issue['line']}: [{issue['type']}]")
                print(f"      {issue['content']}")

        print(f"\n{'='*80}")

    def run(self, path: Path) -> int:
        """Run verification on a path."""
        if path.is_file():
            issues = self.check_file(path)
            self.file_count = 1
        else:
            issues = self.check_directory(path)

        self.issues = issues
        self.issue_count = len(issues)

        self.print_report(issues)

        # Return exit code
        errors = [i for i in issues if i["severity"] == "error"]
        if errors:
            return 1
        if self.strict and warnings:
            return 1
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Verify code for mock outputs and placeholders"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to check (file or directory, default: current directory)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail on warnings too",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix simple issues (experimental, not implemented)",
    )

    args = parser.parse_args()

    path = Path(args.path).resolve()

    if not path.exists():
        logger.error(f"Path does not exist: {path}")
        return 1

    detector = MockCodeDetector(strict=args.strict)
    exit_code = detector.run(path)

    if exit_code == 0:
        print("\n[OK] Verification passed!")
    else:
        print("\n[FAIL] Verification failed! Fix issues before committing.")
        print("\nSee: docs/governance/NO_MOCK_OUTPUTS_RULE.md for guidelines")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
