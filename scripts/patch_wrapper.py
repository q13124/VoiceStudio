#!/usr/bin/env python3
"""
Patch Wrapper for AI Change Logging.

Wraps AI patch operations to log all file changes to the audit system.
This script should be used by AI agents to apply patches with automatic logging.

Usage:
    python scripts/patch_wrapper.py --role "Role 2" --task "VS-0018" < patch.diff
    python scripts/patch_wrapper.py --role "Role 2" --task "VS-0018" --patch-file changes.diff
    python scripts/patch_wrapper.py --files file1.py file2.py --summary "Updated logging"

Environment Variables:
    ROLE_ID: Current role (e.g., "Role 2 - Core Engineer")
    TASK_ID: Current task (e.g., "VS-0018")
    AUDIT_CONSOLE: Set to "1" to echo audit entries to console
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from _env_setup import PROJECT_ROOT

from app.core.audit import AuditActor, ContextEnricher, get_audit_logger


def parse_unified_diff(diff_content: str) -> list[dict]:
    """
    Parse a unified diff to extract file changes.

    Args:
        diff_content: Content of unified diff

    Returns:
        List of dicts with file_path, operation, lines_added, lines_removed
    """
    changes = []
    current_file = None
    lines_added = 0
    lines_removed = 0

    for line in diff_content.split("\n"):
        # New file header
        if line.startswith("diff --git"):
            # Save previous file if exists
            if current_file:
                changes.append({
                    "file_path": current_file,
                    "operation": "modify",
                    "lines_added": lines_added,
                    "lines_removed": lines_removed,
                })

            # Extract file path from diff header
            match = re.search(r"diff --git a/(.*) b/(.*)", line)
            current_file = match.group(2) if match else None
            lines_added = 0
            lines_removed = 0

        # New file indicator
        elif line.startswith("new file"):
            if current_file:
                changes[-1]["operation"] = "create" if changes else None

        # Deleted file indicator
        elif line.startswith("deleted file"):
            if current_file:
                changes[-1]["operation"] = "delete" if changes else None

        # Count additions and deletions
        elif line.startswith("+") and not line.startswith("+++"):
            lines_added += 1
        elif line.startswith("-") and not line.startswith("---"):
            lines_removed += 1

    # Save last file
    if current_file:
        changes.append({
            "file_path": current_file,
            "operation": "modify",
            "lines_added": lines_added,
            "lines_removed": lines_removed,
        })

    return changes


def get_file_changes_from_git() -> list[dict]:
    """
    Get list of changed files from git status.

    Returns:
        List of dicts with file_path and operation
    """
    changes = []
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                status = line[:2].strip()
                file_path = line[3:].strip()

                # Map git status to operation
                if status == "A" or status == "??":
                    operation = "create"
                elif status == "D":
                    operation = "delete"
                elif status == "R":
                    operation = "rename"
                else:
                    operation = "modify"

                changes.append({
                    "file_path": file_path,
                    "operation": operation,
                    "lines_added": 0,
                    "lines_removed": 0,
                })
    # Best effort - failure is acceptable here
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return changes


def get_diff_stats(file_path: str) -> tuple[int, int]:
    """
    Get lines added/removed for a specific file.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (lines_added, lines_removed)
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--numstat", file_path],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("\t")
            if len(parts) >= 2:
                added = int(parts[0]) if parts[0] != "-" else 0
                removed = int(parts[1]) if parts[1] != "-" else 0
                return added, removed
    # Best effort - failure is acceptable here
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        pass

    return 0, 0


def apply_patch(patch_content: str) -> bool:
    """
    Apply a unified diff patch using git apply.

    Args:
        patch_content: Content of the patch

    Returns:
        True if patch applied successfully
    """
    try:
        result = subprocess.run(
            ["git", "apply", "--check"],
            input=patch_content,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            print(f"Patch check failed: {result.stderr}", file=sys.stderr)
            return False

        result = subprocess.run(
            ["git", "apply"],
            input=patch_content,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            print(f"Patch apply failed: {result.stderr}", file=sys.stderr)
            return False

        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error applying patch: {e}", file=sys.stderr)
        return False


def log_changes(
    changes: list[dict],
    role: str,
    task_id: str,
    summary: str,
    actor: str = AuditActor.AI_AGENT.value,
) -> list[str]:
    """
    Log file changes to the audit system.

    Args:
        changes: List of change dicts
        role: Role performing the changes
        task_id: Task ID from Quality Ledger
        summary: Human-readable summary
        actor: Actor type

    Returns:
        List of entry IDs
    """
    enable_console = os.environ.get("AUDIT_CONSOLE", "").lower() in ("1", "true", "yes")
    audit_logger = get_audit_logger()
    audit_logger._enable_console = enable_console

    # Set up context enricher
    enricher = ContextEnricher()
    audit_logger.set_context_enricher(enricher)

    entry_ids = []
    for change in changes:
        file_path = change.get("file_path", "")
        operation = change.get("operation", "modify")
        lines_added = change.get("lines_added", 0)
        lines_removed = change.get("lines_removed", 0)

        # Generate file-specific summary
        file_summary = f"{summary} - {operation} {file_path.split('/')[-1]}"
        if lines_added or lines_removed:
            file_summary += f" (+{lines_added}/-{lines_removed})"

        entry_id = audit_logger.log_file_change(
            file_path=file_path,
            operation=operation,
            role=role,
            task_id=task_id,
            summary=file_summary,
            lines_added=lines_added,
            lines_removed=lines_removed,
            actor=actor,
        )
        entry_ids.append(entry_id)

        if enable_console:
            print(f"  Logged: {operation} {file_path} (ID: {entry_id})")

    return entry_ids


def main():
    parser = argparse.ArgumentParser(
        description="AI Patch Wrapper with Audit Logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--role",
        default=os.environ.get("ROLE_ID", "AI-Agent"),
        help="Role performing the change (default: AI-Agent or $ROLE_ID)",
    )
    parser.add_argument(
        "--task",
        default=os.environ.get("TASK_ID", ""),
        help="Task ID from Quality Ledger (default: $TASK_ID)",
    )
    parser.add_argument(
        "--summary",
        default="AI-generated changes",
        help="Human-readable summary of changes",
    )
    parser.add_argument(
        "--patch-file",
        type=Path,
        help="Path to patch file (if not reading from stdin)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="List of files to log (instead of parsing a patch)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the patch (default: just log without applying)",
    )
    parser.add_argument(
        "--actor",
        default=AuditActor.AI_AGENT.value,
        choices=[a.value for a in AuditActor],
        help="Actor type (default: ai-agent)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be logged without actually logging",
    )

    args = parser.parse_args()

    changes = []

    if args.files:
        # Log specific files
        for file_path in args.files:
            lines_added, lines_removed = get_diff_stats(file_path)
            changes.append({
                "file_path": file_path,
                "operation": "modify",
                "lines_added": lines_added,
                "lines_removed": lines_removed,
            })
    elif args.patch_file:
        # Read patch from file
        if not args.patch_file.exists():
            print(f"Error: Patch file not found: {args.patch_file}", file=sys.stderr)
            sys.exit(1)

        patch_content = args.patch_file.read_text()
        changes = parse_unified_diff(patch_content)

        if args.apply and not apply_patch(patch_content):
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Read patch from stdin
        patch_content = sys.stdin.read()
        changes = parse_unified_diff(patch_content)

        if args.apply and not apply_patch(patch_content):
            sys.exit(1)
    else:
        # No input - get changes from git status
        changes = get_file_changes_from_git()
        if not changes:
            print("No changes detected. Provide a patch or use --files.")
            sys.exit(0)

    if not changes:
        print("No file changes found in input.")
        sys.exit(0)

    print(f"Found {len(changes)} file change(s)")

    if args.dry_run:
        print("\nDry run - would log the following changes:")
        for change in changes:
            print(f"  {change['operation']}: {change['file_path']} "
                  f"(+{change['lines_added']}/-{change['lines_removed']})")
        sys.exit(0)

    # Log changes
    entry_ids = log_changes(
        changes=changes,
        role=args.role,
        task_id=args.task,
        summary=args.summary,
        actor=args.actor,
    )

    print(f"\nLogged {len(entry_ids)} audit entries")
    print(f"Entry IDs: {', '.join(entry_ids)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
