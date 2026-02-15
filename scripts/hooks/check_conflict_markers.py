#!/usr/bin/env python3
"""
Pre-commit hook: Check for merge conflict markers.
Cross-platform replacement for bash -c hook.
"""

import sys
from pathlib import Path


def main():
    """Check if any staged files contain merge conflict markers."""
    conflict_marker = "<<<<<<< HEAD"

    errors = []
    for filename in sys.argv[1:]:
        try:
            path = Path(filename)
            if path.exists() and path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                if conflict_marker in content:
                    errors.append(f"ERROR: Conflict markers in {filename}")
        except Exception:
            # Skip files that can't be read (binary, permissions, etc.)
            pass

    if errors:
        for error in errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
