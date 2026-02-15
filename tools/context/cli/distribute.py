#!/usr/bin/env python3
"""
Context Distribution CLI.

Distribute context to roles automatically.

Usage:
    python -m tools.context.cli.distribute --role overseer
    python -m tools.context.cli.distribute --all --task TASK-0001
    python -m tools.context.cli.distribute --status
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.context.core.distributor import get_distributor


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def cmd_distribute(args: argparse.Namespace) -> int:
    """Distribute context to a role."""
    distributor = get_distributor()

    bundle = distributor.distribute(
        role_id=args.role,
        task_id=args.task,
        phase=args.phase,
        force_refresh=args.force,
    )

    if bundle is None:
        print(f"ERROR: Failed to distribute context to role {args.role}")
        return 1

    if args.json:
        print(bundle.to_json())
    elif args.markdown:
        print(bundle.to_part_markdown())
    else:
        bundle_json = bundle.to_json()
        print(f"Successfully distributed context to role: {args.role}")
        print(f"  Bundle size: {len(bundle_json)} chars")
        print(f"  Task: {bundle.task.id or 'None'}")
        print(f"  Phase: {bundle.state.phase or 'Unknown'}")
        print(f"  Rules loaded: {len(bundle.rules)}")
        print(f"  Memory items: {len(bundle.memory)}")
        if bundle.ledger:
            print(f"  Ledger entries: {len(bundle.ledger)}")

    return 0


def cmd_distribute_all(args: argparse.Namespace) -> int:
    """Distribute context to all roles."""
    distributor = get_distributor()

    roles = args.roles.split(",") if args.roles else None
    results = distributor.distribute_to_all(
        task_id=args.task,
        phase=args.phase,
        roles=roles,
    )

    success_count = sum(1 for b in results.values() if b is not None)
    fail_count = len(results) - success_count

    if args.json:
        output = {
            "success_count": success_count,
            "fail_count": fail_count,
            "results": {
                role_id: {"success": bundle is not None, "size": len(bundle.to_json()) if bundle else 0}
                for role_id, bundle in results.items()
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Distributed context to {success_count}/{len(results)} roles")
        for role_id, bundle in results.items():
            status = "OK" if bundle else "FAILED"
            size = len(bundle.to_json()) if bundle else 0
            print(f"  [{status}] {role_id}: {size} chars")

    return 0 if fail_count == 0 else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show distributor status."""
    distributor = get_distributor()
    status = distributor.get_status()

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("Context Distributor Status")
        print("=" * 40)
        print(f"Configured roles: {status['configured_roles']}")
        print(f"Active distributions: {status['active_distributions']}")
        print(f"History size: {status['history_size']}")
        print(f"Context manager: {'Available' if status['context_manager_available'] else 'Unavailable'}")
        print(f"Recent failures (last 20): {status['recent_failures']}")

    return 0


def cmd_history(args: argparse.Namespace) -> int:
    """Show distribution history."""
    distributor = get_distributor()
    records = distributor.get_history(role_id=args.role, limit=args.limit)

    if args.json:
        print(json.dumps([r.to_dict() for r in records], indent=2))
    else:
        print(f"Distribution History ({len(records)} records)")
        print("=" * 60)
        for record in records:
            status = "OK" if record.success else "FAIL"
            print(
                f"[{status}] {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"role={record.role_id} task={record.task_id or 'None'} "
                f"size={record.bundle_size_chars}"
            )
            if record.error:
                print(f"    Error: {record.error[:60]}")

    return 0


def cmd_invalidate(args: argparse.Namespace) -> int:
    """Invalidate cached distributions."""
    distributor = get_distributor()
    count = distributor.invalidate(role_id=args.role)

    print(f"Invalidated {count} cached distribution(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Context Distribution CLI")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # distribute command
    dist_parser = subparsers.add_parser("distribute", help="Distribute to a role")
    dist_parser.add_argument("--role", "-r", required=True, help="Role ID")
    dist_parser.add_argument("--task", "-t", help="Task ID")
    dist_parser.add_argument("--phase", "-p", help="Phase name")
    dist_parser.add_argument("--force", "-f", action="store_true", help="Force refresh")
    dist_parser.add_argument("--markdown", "-m", action="store_true", help="Output as markdown")

    # all command
    all_parser = subparsers.add_parser("all", help="Distribute to all roles")
    all_parser.add_argument("--roles", help="Comma-separated role IDs")
    all_parser.add_argument("--task", "-t", help="Task ID")
    all_parser.add_argument("--phase", "-p", help="Phase name")

    # status command
    subparsers.add_parser("status", help="Show distributor status")

    # history command
    hist_parser = subparsers.add_parser("history", help="Show distribution history")
    hist_parser.add_argument("--role", "-r", help="Filter by role ID")
    hist_parser.add_argument("--limit", "-l", type=int, default=20, help="Max records")

    # invalidate command
    inv_parser = subparsers.add_parser("invalidate", help="Invalidate cache")
    inv_parser.add_argument("--role", "-r", help="Role to invalidate (all if omitted)")

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "distribute":
        return cmd_distribute(args)
    elif args.command == "all":
        return cmd_distribute_all(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "history":
        return cmd_history(args)
    elif args.command == "invalidate":
        return cmd_invalidate(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
