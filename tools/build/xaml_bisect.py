#!/usr/bin/env python3
# Copyright (c) VoiceStudio. All rights reserved.
# Licensed under the MIT License.

"""
XAML Build Bisection Tool.

When XAML build fails with exit code 1 and no output (silent crash),
this tool automatically bisects XAML files to find the problematic file.

Usage:
    python tools/build/xaml_bisect.py
    
This will:
1. Get a list of all XAML files in the project
2. Use binary search to identify which file causes the build failure
3. Report the problematic file and suggest fixes
"""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import argparse

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"
SOLUTION_FILE = PROJECT_ROOT / "VoiceStudio.sln"


def get_all_xaml_files() -> List[Path]:
    """Get all XAML files in the project."""
    xaml_files = []
    for path in SRC_DIR.rglob("*.xaml"):
        if "bin" not in path.parts and "obj" not in path.parts:
            xaml_files.append(path)
    return sorted(xaml_files)


def create_backup(files: List[Path]) -> Path:
    """Create a temporary backup of XAML files."""
    backup_dir = Path(tempfile.mkdtemp(prefix="xaml_bisect_"))
    for f in files:
        rel_path = f.relative_to(PROJECT_ROOT)
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, backup_path)
    return backup_dir


def restore_from_backup(backup_dir: Path, files: List[Path]):
    """Restore XAML files from backup."""
    for f in files:
        rel_path = f.relative_to(PROJECT_ROOT)
        backup_path = backup_dir / rel_path
        if backup_path.exists():
            shutil.copy2(backup_path, f)


def create_empty_xaml(path: Path):
    """Replace a XAML file with an empty but valid placeholder."""
    # Determine the type based on content
    content = path.read_text(encoding='utf-8')
    
    if '<Window' in content:
        placeholder = '''<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
</Window>'''
    elif '<Page' in content:
        placeholder = '''<Page
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
</Page>'''
    elif '<UserControl' in content:
        placeholder = '''<UserControl
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
</UserControl>'''
    elif '<ResourceDictionary' in content:
        placeholder = '''<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
</ResourceDictionary>'''
    else:
        # Default to UserControl
        placeholder = '''<UserControl
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
</UserControl>'''
    
    path.write_text(placeholder, encoding='utf-8')


def run_build() -> Tuple[bool, str]:
    """
    Run the dotnet build and return (success, output).
    """
    try:
        result = subprocess.run(
            ["dotnet", "build", str(SOLUTION_FILE), "-c", "Debug", "-p:Platform=x64", "--no-incremental"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=PROJECT_ROOT
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Build timed out"
    except Exception as e:
        return False, str(e)


def bisect_files(files: List[Path], backup_dir: Path) -> Optional[Path]:
    """
    Use binary search to find the problematic XAML file.
    
    Returns the problematic file path, or None if not found.
    """
    if not files:
        return None
    
    if len(files) == 1:
        # Test this single file
        print(f"  Testing: {files[0].name}")
        create_empty_xaml(files[0])
        success, _ = run_build()
        restore_from_backup(backup_dir, files)
        
        if success:
            return files[0]  # This file was the problem
        return None
    
    # Split in half
    mid = len(files) // 2
    left_half = files[:mid]
    right_half = files[mid:]
    
    print(f"  Bisecting {len(files)} files (testing {len(left_half)} vs {len(right_half)})...")
    
    # Empty out the left half and test
    for f in left_half:
        create_empty_xaml(f)
    
    success, _ = run_build()
    restore_from_backup(backup_dir, left_half)
    
    if success:
        # Problem was in the left half
        print(f"  -> Problem in left half ({len(left_half)} files)")
        return bisect_files(left_half, backup_dir)
    else:
        # Problem might be in the right half or both
        # Test right half alone
        for f in right_half:
            create_empty_xaml(f)
        
        success, _ = run_build()
        restore_from_backup(backup_dir, right_half)
        
        if success:
            print(f"  -> Problem in right half ({len(right_half)} files)")
            return bisect_files(right_half, backup_dir)
        else:
            # Problem in both or combination - try linear for right half
            print(f"  -> Complex interaction, checking right half linearly...")
            return bisect_files(right_half, backup_dir)


def main():
    parser = argparse.ArgumentParser(description="Bisect XAML files to find build failure cause")
    parser.add_argument("--dry-run", action="store_true", help="Just list files without bisecting")
    args = parser.parse_args()
    
    print("=" * 70)
    print("XAML Build Bisection Tool")
    print("=" * 70)
    print()
    
    # Get all XAML files
    xaml_files = get_all_xaml_files()
    print(f"Found {len(xaml_files)} XAML files to analyze")
    
    if args.dry_run:
        print("\nFiles that would be tested:")
        for f in xaml_files:
            print(f"  {f.relative_to(PROJECT_ROOT)}")
        return 0
    
    # First, verify the build actually fails
    print("\nVerifying build fails...")
    success, output = run_build()
    
    if success:
        print("Build SUCCEEDED - no bisection needed!")
        return 0
    
    print("Build failed as expected. Starting bisection...\n")
    
    # Create backup
    print("Creating backup of XAML files...")
    backup_dir = create_backup(xaml_files)
    print(f"Backup created at: {backup_dir}\n")
    
    try:
        # Run bisection
        problematic_file = bisect_files(xaml_files, backup_dir)
        
        print("\n" + "=" * 70)
        if problematic_file:
            print("FOUND PROBLEMATIC FILE:")
            print(f"  {problematic_file.relative_to(PROJECT_ROOT)}")
            print()
            print("SUGGESTED ACTIONS:")
            print("  1. Run: python scripts/lint_xaml.py " + str(problematic_file))
            print("  2. Check for attached property issues")
            print("  3. Check for complex ControlTemplate nesting")
            print("  4. Try removing sections incrementally")
        else:
            print("Could not isolate a single problematic file.")
            print("The issue may involve interactions between multiple files.")
            print()
            print("SUGGESTED ACTIONS:")
            print("  1. Review recent XAML changes in git history")
            print("  2. Check for shared resource dictionary issues")
            print("  3. Run: python scripts/lint_xaml.py")
        print("=" * 70)
        
    finally:
        # Always restore from backup
        print("\nRestoring original files from backup...")
        restore_from_backup(backup_dir, xaml_files)
        shutil.rmtree(backup_dir)
        print("Restoration complete.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
