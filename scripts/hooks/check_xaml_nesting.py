#!/usr/bin/env python3
"""
check_xaml_nesting.py - Pre-commit hook to detect deeply nested XAML files.

Deeply nested XAML files in Views/ can cause silent XamlCompiler.exe failures.
See: https://github.com/microsoft/microsoft-ui-xaml/issues/10947

Usage:
    python scripts/hooks/check_xaml_nesting.py <file1> <file2> ...

Exit codes:
    0: No issues found
    1: Deeply nested XAML detected
"""

import re
import sys

# Pattern to detect deeply nested Views subfolders
# Views/{category}/{subcategory}/{file}.xaml is too deep
NESTED_VIEWS_PATTERN = re.compile(r'Views[/\\][^/\\]+[/\\][^/\\]+[/\\][^/\\]+\.xaml$')


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    files = sys.argv[1:]
    nested_files = []

    for file_path_str in files:
        # Only check .xaml files
        if not file_path_str.endswith('.xaml'):
            continue

        if NESTED_VIEWS_PATTERN.search(file_path_str):
            nested_files.append(file_path_str)

    if nested_files:
        print("\nERROR: Deeply nested XAML files in Views/ detected!")
        print("This can cause silent XamlCompiler.exe failures.")
        print("See: https://github.com/microsoft/microsoft-ui-xaml/issues/10947")
        print("\nAffected files:")
        for file_path in nested_files:
            print(f"  {file_path}")
        print("\nFix: Move to Views/ root or Views/{Category}/ (max 1 level deep)")
        print("\nTo bypass: git commit --no-verify")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
