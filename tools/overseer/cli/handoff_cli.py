from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.overseer.handoff_manager import HandoffManager
from tools.overseer.ledger_parser import LedgerParser


def _list(args: argparse.Namespace) -> int:
    manager = HandoffManager(Path(args.dir) if args.dir else None)
    handoffs = manager.list_handoffs()
    for path in handoffs:
        print(path.name)
    return 0


def _show(args: argparse.Namespace) -> int:
    manager = HandoffManager(Path(args.dir) if args.dir else None)
    try:
        content = manager.load_handoff(args.name)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(content)
    return 0


def _validate(args: argparse.Namespace) -> int:
    manager = HandoffManager(Path(args.dir) if args.dir else None)
    errors = manager.validate()
    if errors:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return 1
    print("Handoff validation PASS")
    return 0


def _reconcile(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    manager = HandoffManager(Path(args.dir) if args.dir else None, ledger_parser=parser)
    matched, missing, orphan = manager.reconcile_with_ledger()
    print(f"Matched: {len(matched)}")
    print(f"Missing: {len(missing)}")
    print(f"Orphan: {len(orphan)}")
    if missing:
        print("Missing handoffs:")
        for mid in missing:
            print(f"- {mid}")
    if orphan:
        print("Orphan handoffs:")
        for oid in orphan:
            print(f"- {oid}")
    return 1 if missing or orphan else 0


def _index(args: argparse.Namespace) -> int:
    manager = HandoffManager(Path(args.dir) if args.dir else None)
    handoffs = manager.list_handoffs()
    lines = ["# Handoff Index", ""]
    for path in handoffs:
        lines.append(f"- {path.name}")
    output = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote index to {args.output}")
    else:
        print(output)
    return 0


def _create(args: argparse.Namespace) -> int:
    manager = HandoffManager(Path(args.dir) if args.dir else None)
    target = manager._resolve_handoff_path(args.name)
    if target.exists():
        print(f"Handoff already exists: {target}", file=sys.stderr)
        return 1
    template = Path(args.template) if args.template else Path("docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md")
    if template.exists():
        content = template.read_text(encoding="utf-8")
    else:
        content = f"# {args.name} Handoff\n\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"Created {target}")
    return 0


# Queue-based handoff commands with context distribution
def _queue_list(args: argparse.Namespace) -> int:
    """List pending handoffs in queue for a role."""
    from tools.overseer.issues.handoff import get_handoff_queue

    queue = get_handoff_queue()
    pending = queue.get_pending_with_context(args.role)

    if not pending:
        print(f"No pending handoffs for role: {args.role}")
        return 0

    print(f"Pending handoffs for {args.role}:")
    print("-" * 60)
    for entry in pending:
        ctx_status = "CTX" if entry.get("context_prepared") else "---"
        print(
            f"[{entry['priority'].upper():6}] {entry['id']} "
            f"from {entry['from_role']} [{ctx_status}]"
        )
        print(f"         Issue: {entry['issue_id']}")
        print(f"         {entry['message'][:60]}...")
        print()

    return 0


def _queue_handoff(args: argparse.Namespace) -> int:
    """Create a new handoff with context distribution."""
    from tools.overseer.issues.handoff import get_handoff_queue

    queue = get_handoff_queue()
    entry = queue.handoff(
        issue_id=args.issue,
        from_role=args.from_role,
        to_role=args.to_role,
        reason=args.reason,
        priority=args.priority,
        task_id=args.task,
        distribute_context=not args.no_context,
    )

    print(f"Created handoff: {entry.id}")
    print(f"  From: {entry.from_role} -> To: {entry.to_role}")
    print(f"  Issue: {entry.issue_id}")
    print(f"  Context: {'prepared' if entry.context_prepared else 'not prepared'}")
    if entry.context_size_chars:
        print(f"  Context size: {entry.context_size_chars} chars")

    return 0


def _queue_acknowledge(args: argparse.Namespace) -> int:
    """Acknowledge a handoff."""
    from tools.overseer.issues.handoff import get_handoff_queue

    queue = get_handoff_queue()
    if queue.acknowledge(args.entry_id, args.role):
        print(f"Acknowledged: {args.entry_id}")
        return 0
    else:
        print(f"Handoff not found: {args.entry_id}", file=sys.stderr)
        return 1


def _queue_complete(args: argparse.Namespace) -> int:
    """Complete a handoff."""
    from tools.overseer.issues.handoff import get_handoff_queue

    queue = get_handoff_queue()
    if queue.complete(args.entry_id, args.resolution):
        print(f"Completed: {args.entry_id}")
        return 0
    else:
        print(f"Handoff not found: {args.entry_id}", file=sys.stderr)
        return 1


def _queue_stats(args: argparse.Namespace) -> int:
    """Show handoff queue statistics."""
    from tools.overseer.issues.handoff import get_handoff_queue

    queue = get_handoff_queue()
    stats = queue.get_statistics()

    print("Handoff Queue Statistics")
    print("=" * 40)
    print(f"Total handoffs: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Acknowledged: {stats['acknowledged']}")
    print(f"  Completed: {stats['completed']}")
    print()
    print(f"With context: {stats['with_context']} ({stats['context_rate']:.1%})")
    print()

    if stats['pending_by_role']:
        print("Pending by role:")
        for role, count in stats['pending_by_role'].items():
            print(f"  {role}: {count}")

    return 0


def _queue_refresh(args: argparse.Namespace) -> int:
    """Refresh context for a handoff."""
    from tools.overseer.issues.handoff import get_handoff_queue

    queue = get_handoff_queue()
    if queue.refresh_context(args.entry_id):
        print(f"Context refreshed for: {args.entry_id}")
        return 0
    else:
        print(f"Failed to refresh context for: {args.entry_id}", file=sys.stderr)
        return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="overseer handoff", description="Handoff management")
    parser.add_argument("--dir", help="Handoff directory override")
    parser.add_argument("--ledger", help="Ledger path override")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List handoff files")
    list_parser.set_defaults(func=_list)

    show_parser = subparsers.add_parser("show", help="Show a handoff file")
    show_parser.add_argument("name", help="Handoff name or VS-XXXX id")
    show_parser.set_defaults(func=_show)

    validate_parser = subparsers.add_parser("validate", help="Validate handoff files")
    validate_parser.set_defaults(func=_validate)

    reconcile_parser = subparsers.add_parser("reconcile", help="Reconcile ledger vs handoffs")
    reconcile_parser.set_defaults(func=_reconcile)

    index_parser = subparsers.add_parser("index", help="Generate handoff index")
    index_parser.add_argument("--output", "-o", help="Write index to file")
    index_parser.set_defaults(func=_index)

    create_parser = subparsers.add_parser("create", help="Create a new handoff from template")
    create_parser.add_argument("name", help="Handoff name or VS-XXXX id")
    create_parser.add_argument("--template", help="Template markdown path")
    create_parser.set_defaults(func=_create)

    # Queue-based commands with context distribution
    queue_list_parser = subparsers.add_parser("queue", help="List pending queue handoffs for a role")
    queue_list_parser.add_argument("role", help="Role to check (e.g., debug-agent)")
    queue_list_parser.set_defaults(func=_queue_list)

    send_parser = subparsers.add_parser("send", help="Create handoff with context distribution")
    send_parser.add_argument("--issue", "-i", required=True, help="Issue ID")
    send_parser.add_argument("--from-role", "-f", required=True, help="Source role")
    send_parser.add_argument("--to-role", "-t", required=True, help="Target role")
    send_parser.add_argument("--reason", "-r", required=True, help="Handoff reason")
    send_parser.add_argument("--priority", "-p", default="medium", choices=["low", "medium", "high", "urgent"])
    send_parser.add_argument("--task", help="Task ID for context")
    send_parser.add_argument("--no-context", action="store_true", help="Skip context distribution")
    send_parser.set_defaults(func=_queue_handoff)

    ack_parser = subparsers.add_parser("ack", help="Acknowledge a handoff")
    ack_parser.add_argument("entry_id", help="Handoff entry ID (HO-xxxxxxxx)")
    ack_parser.add_argument("--role", "-r", required=True, help="Acknowledging role")
    ack_parser.set_defaults(func=_queue_acknowledge)

    done_parser = subparsers.add_parser("done", help="Complete a handoff")
    done_parser.add_argument("entry_id", help="Handoff entry ID")
    done_parser.add_argument("--resolution", "-r", required=True, help="Resolution description")
    done_parser.set_defaults(func=_queue_complete)

    stats_parser = subparsers.add_parser("stats", help="Show handoff queue statistics")
    stats_parser.set_defaults(func=_queue_stats)

    refresh_parser = subparsers.add_parser("refresh", help="Refresh context for handoff")
    refresh_parser.add_argument("entry_id", help="Handoff entry ID")
    refresh_parser.set_defaults(func=_queue_refresh)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
