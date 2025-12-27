"""
Engine Verification Script

Verifies that all engines have complete implementations with no placeholders, stubs, or incomplete code.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Forbidden patterns (must be in comments or standalone)
FORBIDDEN_PATTERNS = [
    ("TODO", r"#\s*TODO\b|//\s*TODO\b"),  # Only flag actual TODO comments
    ("FIXME", r"#\s*FIXME\b|//\s*FIXME\b"),  # Only flag actual FIXME comments
    (
        "PLACEHOLDER",
        r"\bPLACEHOLDER\b",
    ),  # Flag PLACEHOLDER anywhere (except in strings)
    ("STUB", r"\bSTUB\b"),  # Flag STUB anywhere (except in strings)
    (
        "NotImplemented",
        r"\bNotImplemented\b",
    ),  # Flag NotImplementedError/NotImplemented
    ("NotImplementedError", r"\bNotImplementedError\b"),
    ("raise NotImplemented", r"raise\s+NotImplemented"),
]


def check_file_for_placeholders(file_path: Path) -> Tuple[List[Dict], bool]:
    """
    Check a Python file for placeholders and incomplete code.

    Args:
        file_path: Path to the Python file

    Returns:
        Tuple of (issues list, has_issues boolean)
    """
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        import re

        for line_num, line in enumerate(lines, 1):
            # Skip comments that are just documentation
            stripped = line.strip()
            if stripped.startswith("#") and not any(
                keyword in stripped.upper()
                for keyword in ["TODO", "FIXME", "PLACEHOLDER", "STUB"]
            ):
                continue

            # Check for forbidden patterns
            for pattern_name, pattern_regex in FORBIDDEN_PATTERNS:
                if re.search(pattern_regex, line, re.IGNORECASE):
                    # Check if it's in an allowed context
                    is_allowed = False

                    # Allow if it's part of a word (e.g., "Todo" class name, not "TODO" comment)
                    if pattern_name == "TODO":
                        # Only flag if it's actually a TODO comment, not "Todo" in code
                        if not re.search(r"#.*TODO|//.*TODO", line, re.IGNORECASE):
                            # Check if it's "Todo" (capitalized, part of identifier)
                            if re.search(r"\bTodo\b", line) and not re.search(
                                r"#", line
                            ):
                                is_allowed = True

                    # Allow if it's in a string literal (not a comment)
                    if '"' in line or "'" in line:
                        # Check if pattern is in a string
                        in_string = False
                        quote_char = None
                        for char in line:
                            if char in ['"', "'"]:
                                if quote_char is None:
                                    quote_char = char
                                    in_string = True
                                elif char == quote_char:
                                    in_string = False
                                    quote_char = None
                        if in_string:
                            is_allowed = True

                    # Allow pass in except blocks
                    if "except" in line.lower() and "pass" in line.lower():
                        is_allowed = True

                    if not is_allowed:
                        issues.append(
                            {
                                "file": str(file_path),
                                "line": line_num,
                                "pattern": pattern_name,
                                "content": line.strip(),
                            }
                        )

        # Parse AST to check for NotImplementedError
        try:
            tree = ast.parse("".join(lines), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise):
                    if isinstance(node.exc, ast.Name):
                        if node.exc.id == "NotImplementedError":
                            # Get line number
                            line_num = node.lineno
                            issues.append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "pattern": "NotImplementedError",
                                    "content": (
                                        lines[line_num - 1].strip()
                                        if line_num <= len(lines)
                                        else ""
                                    ),
                                }
                            )
        except SyntaxError:
            # Skip files with syntax errors (they'll be caught by other tools)
            pass

    except Exception as e:
        logger.error(f"Error checking {file_path}: {e}")
        issues.append(
            {
                "file": str(file_path),
                "line": 0,
                "pattern": "ERROR",
                "content": f"Failed to check file: {e}",
            }
        )

    return issues, len(issues) > 0


def verify_engines() -> Dict:
    """
    Verify all engines for completeness.

    Returns:
        Dictionary with verification results
    """
    engines_dir = Path("app/core/engines")

    if not engines_dir.exists():
        logger.error(f"Engines directory not found: {engines_dir}")
        return {
            "success": False,
            "error": f"Engines directory not found: {engines_dir}",
        }

    all_issues = []
    files_checked = 0
    files_with_issues = 0

    # Check all engine files
    for engine_file in sorted(engines_dir.glob("*_engine.py")):
        files_checked += 1
        issues, has_issues = check_file_for_placeholders(engine_file)

        if has_issues:
            files_with_issues += 1
            all_issues.extend(issues)
            logger.warning(f"Found issues in {engine_file.name}: {len(issues)} issues")

    # Summary
    result = {
        "success": len(all_issues) == 0,
        "files_checked": files_checked,
        "files_with_issues": files_with_issues,
        "total_issues": len(all_issues),
        "issues": all_issues,
    }

    return result


def main():
    """Main verification function."""
    logger.info("Starting engine verification...")

    result = verify_engines()

    print("\n" + "=" * 80)
    print("ENGINE VERIFICATION REPORT")
    print("=" * 80)
    print(f"\nFiles Checked: {result['files_checked']}")
    print(f"Files With Issues: {result['files_with_issues']}")
    print(f"Total Issues Found: {result['total_issues']}")

    if result["total_issues"] > 0:
        print("\n" + "-" * 80)
        print("ISSUES FOUND:")
        print("-" * 80)

        # Group by file
        issues_by_file = {}
        for issue in result["issues"]:
            file = issue["file"]
            if file not in issues_by_file:
                issues_by_file[file] = []
            issues_by_file[file].append(issue)

        for file, issues in sorted(issues_by_file.items()):
            print(f"\n{file}:")
            for issue in issues:
                print(f"  Line {issue['line']}: {issue['pattern']}")
                print(f"    {issue['content']}")

        print("\n" + "=" * 80)
        print("VERIFICATION FAILED")
        print("=" * 80)
        return 1
    else:
        print("\n" + "=" * 80)
        print("VERIFICATION PASSED - All engines are complete!")
        print("=" * 80)
        return 0


if __name__ == "__main__":
    exit(main())
