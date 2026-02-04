#!/usr/bin/env python3
"""
Add AutomationIds to panel XAML files for UI automation testing.

Adds AutomationProperties.AutomationId="{ViewName}_Root" to the root Grid element
in each panel XAML file.

Usage:
    python scripts/add_automation_ids.py
    python scripts/add_automation_ids.py --dry-run
"""

import argparse
import re
from pathlib import Path


def get_view_name(file_path: Path) -> str:
    """Extract view name from file path (e.g., ProfilesView from ProfilesView.xaml)."""
    return file_path.stem


def add_automation_id(content: str, view_name: str) -> tuple[str, bool]:
    """
    Add AutomationId to the first Grid element in the XAML content.
    
    Returns:
        tuple of (modified_content, was_modified)
    """
    automation_id = f'{view_name}_Root'
    
    # Check if AutomationId already exists on any element
    if f'AutomationId="{automation_id}"' in content:
        return content, False
    
    # Pattern to match first <Grid with optional attributes
    # We want to add AutomationProperties.AutomationId after the opening <Grid
    grid_pattern = r'(<Grid)(\s*)([^>]*)(>)'
    
    def add_id_to_first_grid(match):
        tag = match.group(1)      # <Grid
        whitespace = match.group(2)  # existing whitespace
        attrs = match.group(3)    # existing attributes
        suffix = match.group(4)   # >
        
        # Check if this Grid already has AutomationId
        if 'AutomationId' in attrs:
            return match.group(0)
        
        # Add the AutomationId
        new_attr = f'AutomationProperties.AutomationId="{automation_id}"'
        
        if attrs.strip():
            # Has other attributes - add after them
            return f'{tag} {new_attr} {attrs.rstrip()}{suffix}'
        else:
            # No other attributes
            return f'{tag} {new_attr}{suffix}'
    
    # Only replace the first occurrence
    modified, count = re.subn(grid_pattern, add_id_to_first_grid, content, count=1)
    
    return modified, count > 0 and modified != content


def process_file(file_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """
    Process a single XAML file to add AutomationId.
    
    Returns:
        tuple of (success, message)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        view_name = get_view_name(file_path)
        
        modified_content, was_modified = add_automation_id(content, view_name)
        
        if not was_modified:
            return True, f"SKIP: {file_path.name} - AutomationId already present or no Grid found"
        
        if dry_run:
            return True, f"DRY-RUN: Would add AutomationId to {file_path.name}"
        
        file_path.write_text(modified_content, encoding='utf-8')
        return True, f"ADDED: {file_path.name} - AutomationId='{view_name}_Root'"
        
    except Exception as e:
        return False, f"ERROR: {file_path.name} - {e}"


def main():
    parser = argparse.ArgumentParser(description="Add AutomationIds to panel XAML files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--panels-dir", default="src/VoiceStudio.App/Views/Panels", help="Path to panels directory")
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    panels_dir = project_root / args.panels_dir
    
    if not panels_dir.exists():
        print(f"ERROR: Panels directory not found: {panels_dir}")
        return 1
    
    # Find all XAML files
    xaml_files = sorted(panels_dir.glob("*.xaml"))
    
    print(f"Processing {len(xaml_files)} XAML files in {panels_dir}")
    print("=" * 60)
    
    added = 0
    skipped = 0
    errors = 0
    
    for file_path in xaml_files:
        success, message = process_file(file_path, args.dry_run)
        print(message)
        
        if "ADDED" in message or "DRY-RUN" in message:
            added += 1
        elif "SKIP" in message:
            skipped += 1
        else:
            errors += 1
    
    print("=" * 60)
    print(f"Summary: {added} added, {skipped} skipped, {errors} errors")
    
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    exit(main())
