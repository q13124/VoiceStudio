#!/usr/bin/env python3
"""
Update Commit Hash in Audit Entries.

Updates recent audit entries with the final commit hash after a commit.
Called by the post-commit hook.

Usage:
    python scripts/update_commit_hash.py --commit <hash>
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

from _env_setup import PROJECT_ROOT


def update_entries(commit_hash: str, minutes: int = 30) -> int:
    """
    Update recent audit entries with commit hash.

    Args:
        commit_hash: Full or short commit hash
        minutes: How far back to look for entries to update

    Returns:
        Number of entries updated
    """
    audit_dir = PROJECT_ROOT / ".audit"

    if not audit_dir.exists():
        return 0

    # Get today's log
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = audit_dir / f"log-{today}.jsonl"

    if not log_path.exists():
        return 0

    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    short_hash = commit_hash[:7] if len(commit_hash) > 7 else commit_hash

    updated_count = 0
    entries = []

    try:
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    # Check if entry is recent and doesn't have commit hash
                    timestamp_str = entry.get("timestamp", "")
                    if timestamp_str:
                        entry_time = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                        if entry_time >= cutoff_time:
                            if not entry.get("commit_hash"):
                                entry["commit_hash"] = short_hash
                                updated_count += 1

                    entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    # Keep unparseable lines as-is
                    entries.append({"_raw": line.strip()})
    except OSError:
        return 0

    # Write back
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            for entry in entries:
                if "_raw" in entry:
                    f.write(entry["_raw"] + "\n")
                else:
                    f.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        return 0

    return updated_count


def main():
    parser = argparse.ArgumentParser(
        description="Update audit entries with commit hash"
    )
    parser.add_argument(
        "--commit",
        required=True,
        help="Git commit hash",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=30,
        help="How far back to look for entries (default: 30)",
    )

    args = parser.parse_args()

    updated = update_entries(args.commit, args.minutes)
    print(f"Updated {updated} audit entries with commit hash {args.commit[:7]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
