"""
Auto-commit script for VoiceStudio.

Runs verification checks before committing, respects project rules.
Can be run manually or via file watcher.

Usage:
    python tools/auto_commit.py [--message "Custom message"] [--skip-verify]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
VERIFY_SCRIPT = PROJECT_ROOT / "tools" / "verify_no_stubs_placeholders.py"


def run_verification() -> tuple[bool, str]:
    """Run verification script. Returns (success, output)."""
    try:
        result = subprocess.run(
            [sys.executable, str(VERIFY_SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, f"Verification failed: {e}"


def get_changed_files() -> list[str]:
    """Get list of changed files (staged + unstaged)."""
    try:
        # Get staged files
        staged = (
            subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .splitlines()
        )

        # Get unstaged files (excluding ignored)
        unstaged = (
            subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .splitlines()
        )

        all_changed = [f for f in staged + unstaged if f.strip()]
        return list(set(all_changed))  # Deduplicate
    except Exception:
        return []


def generate_commit_message(custom_message: str | None = None) -> str:
    """Generate commit message."""
    if custom_message:
        return custom_message

    changed = get_changed_files()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Categorize changes
    categories = {
        "backend": [f for f in changed if f.startswith("backend/")],
        "app": [f for f in changed if f.startswith("app/")],
        "src": [f for f in changed if f.startswith("src/")],
        "docs": [f for f in changed if f.startswith("docs/")],
        "tools": [f for f in changed if f.startswith("tools/")],
        "tests": [f for f in changed if f.startswith("tests/")],
    }

    active_categories = [k for k, v in categories.items() if v]
    category_str = ", ".join(active_categories) if active_categories else "misc"

    file_count = len(changed)
    if file_count == 0:
        return f"Auto-commit: {timestamp}"

    if file_count <= 3:
        files_str = ", ".join([Path(f).name for f in changed[:3]])
        return f"Auto-commit ({category_str}): {files_str} - {timestamp}"
    else:
        return f"Auto-commit ({category_str}): {file_count} files - {timestamp}"


def commit_changes(message: str, skip_verify: bool = False) -> tuple[bool, str]:
    """Stage and commit all changes."""
    try:
        # Run verification unless skipped
        if not skip_verify:
            print("Running verification checks...")
            success, output = run_verification()
            if not success:
                return False, f"Verification failed:\n{output}"

        # Stage all changes (respects .gitignore)
        stage_result = subprocess.run(
            ["git", "add", "-A"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if stage_result.returncode != 0:
            return False, f"git add failed: {stage_result.stderr}"

        # Check if there's anything to commit
        status_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_ROOT,
        )
        if status_result.returncode == 0:
            # Check unstaged too
            unstaged_result = subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=PROJECT_ROOT,
            )
            if unstaged_result.returncode == 0:
                return False, "No changes to commit"

        # Commit
        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if commit_result.returncode != 0:
            return False, f"git commit failed: {commit_result.stderr}"

        return True, commit_result.stdout

    except Exception as e:
        return False, f"Commit failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-commit with verification")
    parser.add_argument("--message", "-m", help="Custom commit message", default=None)
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verification checks (not recommended)",
    )
    args = parser.parse_args()

    message = generate_commit_message(args.message)
    print(f"Commit message: {message}")

    success, output = commit_changes(message, skip_verify=args.skip_verify)
    if success:
        print(f"✅ Committed successfully\n{output}")
        return 0
    else:
        print(f"❌ Commit failed:\n{output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
