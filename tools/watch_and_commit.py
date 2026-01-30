"""
File watcher that auto-commits changes.

Watches for file changes and automatically commits them after a short delay.
Respects verification rules.

Usage:
    python tools/watch_and_commit.py [--interval 30] [--skip-verify]

Press Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from threading import Timer

PROJECT_ROOT = Path(__file__).parent.parent
AUTO_COMMIT_SCRIPT = PROJECT_ROOT / "tools" / "auto_commit.py"

# Global timer to debounce commits
commit_timer: Timer | None = None


def has_changes() -> bool:
    """Check if there are any uncommitted changes."""
    try:
        # Check staged
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_ROOT,
        )
        # Check unstaged
        unstaged = subprocess.run(
            ["git", "diff", "--quiet"],
            cwd=PROJECT_ROOT,
        )
        # Check untracked (non-ignored)
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        return (
            staged.returncode != 0
            or unstaged.returncode != 0
            or bool(untracked.stdout.strip())
        )
    except Exception:
        return False


def schedule_commit(interval: float, skip_verify: bool) -> None:
    """Schedule a commit after delay (debouncing)."""
    global commit_timer

    if commit_timer:
        commit_timer.cancel()

    def do_commit():
        if has_changes():
            print(f"\n[{time.strftime('%H:%M:%S')}] Auto-committing changes...")
            result = subprocess.run(
                [sys.executable, str(AUTO_COMMIT_SCRIPT)]
                + (["--skip-verify"] if skip_verify else []),
                cwd=PROJECT_ROOT,
            )

    commit_timer = Timer(interval, do_commit)
    commit_timer.daemon = True
    commit_timer.start()


def watch_files(interval: float, check_interval: float, skip_verify: bool) -> None:
    """Watch for file changes and auto-commit."""
    print(f"Watching for changes (auto-commit after {interval}s of inactivity)...")
    print("Press Ctrl+C to stop\n")

    last_check = time.time()
    last_has_changes = False

    try:
        while True:
            time.sleep(check_interval)

            current_has_changes = has_changes()
            now = time.time()

            if current_has_changes:
                if not last_has_changes:
                    print(
                        f"[{time.strftime('%H:%M:%S')}] Changes detected, scheduling commit..."
                    )
                schedule_commit(interval, skip_verify)
            elif last_has_changes and (now - last_check) > interval:
                # Changes were committed or discarded
                print(f"[{time.strftime('%H:%M:%S')}] No pending changes")

            last_has_changes = current_has_changes
            last_check = now

    except KeyboardInterrupt:
        print("\n\nStopping file watcher...")
        if commit_timer:
            commit_timer.cancel()


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch files and auto-commit changes")
    parser.add_argument(
        "--interval",
        type=float,
        default=30.0,
        help="Seconds to wait after last change before committing (default: 30)",
    )
    parser.add_argument(
        "--check-interval",
        type=float,
        default=5.0,
        help="Seconds between checks for changes (default: 5)",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verification checks (not recommended)",
    )
    args = parser.parse_args()

    watch_files(args.interval, args.check_interval, args.skip_verify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
