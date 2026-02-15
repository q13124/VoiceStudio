#!/usr/bin/env python3
"""
Pre-commit hook: Block .env files from being committed.
Cross-platform replacement for bash -c hook.
"""

import re
import sys


def main():
    """Check if any staged files are .env files."""
    env_pattern = re.compile(r"\.env($|\.local|\.prod|\.dev)", re.IGNORECASE)

    errors = []
    for filename in sys.argv[1:]:
        if env_pattern.search(filename):
            errors.append(f"ERROR: .env file should not be committed: {filename}")

    if errors:
        for error in errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
