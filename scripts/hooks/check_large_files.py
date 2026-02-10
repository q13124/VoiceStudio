#!/usr/bin/env python3
"""
check_large_files.py - Pre-commit hook to block large files (>10MB).

Usage:
    python scripts/hooks/check_large_files.py <file1> <file2> ...

Exit codes:
    0: No large files found
    1: Large files detected
"""

import sys
from pathlib import Path


MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
MAX_SIZE_DISPLAY = "10MB"


def format_size(size_bytes: int) -> str:
    """Format file size for display."""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f}KB"
    return f"{size_bytes}B"


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    
    files = sys.argv[1:]
    large_files = []
    
    for file_path_str in files:
        file_path = Path(file_path_str)
        if not file_path.exists() or file_path.is_dir():
            continue
        
        size = file_path.stat().st_size
        if size > MAX_SIZE_BYTES:
            large_files.append((file_path, size))
    
    if large_files:
        print(f"\nERROR: Files larger than {MAX_SIZE_DISPLAY} detected:")
        for file_path, size in large_files:
            print(f"  {file_path}: {format_size(size)}")
        print("\nConsider:")
        print("  - Using Git LFS for large binary files")
        print("  - Compressing the file")
        print("  - Storing large assets externally")
        print("\nTo bypass: git commit --no-verify")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
