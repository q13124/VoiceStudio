from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.overseer.gate_tracker import GateTracker
from tools.overseer.ledger_parser import LedgerParser


def _status(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    validation = parser.validate()
    for warn in validation.warnings:
        print(f"[WARN] {warn}")
    if validation.errors:
        for err in validation.errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return 1
    tracker = GateTracker(parser)
    statuses = tracker.compute_statuses(force=True)
    for status in statuses:
        print(f"{status.status_symbol} Gate {status.gate.value}: {status.done_entries}/{status.total_entries}")
    return 0


def _blockers(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    blockers = tracker.get_blockers()
    if not blockers:
        print("No blockers found.")
        return 0
    for entry in blockers:
        print(f"- {entry.id}: {entry.title}")
    return 0


def _next(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    actions = tracker.get_next_actions()
    if not actions:
        print("No pending actions.")
        return 0
    for action in actions:
        print(f"- {action}")
    return 0


def _dashboard(args: argparse.Namespace) -> int:
    return _status(args)


def _export(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    statuses = tracker.compute_statuses(force=True)
    payload = [
        {
            "gate": s.gate.value,
            "total_entries": s.total_entries,
            "done_entries": s.done_entries,
            "blocked_entries": s.blocked_entries,
            "in_progress_entries": s.in_progress_entries,
            "open_entries": s.open_entries,
            "is_green": s.is_green,
        }
        for s in statuses
    ]
    output = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {len(payload)} gate statuses to {args.output}")
        return 0
    print(output)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="overseer gate", description="Gate status commands")
    parser.add_argument("--ledger", help="Path to QUALITY_LEDGER.md")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show gate statuses")
    status_parser.set_defaults(func=_status)

    blockers_parser = subparsers.add_parser("blockers", help="List blockers")
    blockers_parser.set_defaults(func=_blockers)

    next_parser = subparsers.add_parser("next", help="Show next actions")
    next_parser.set_defaults(func=_next)

    dash_parser = subparsers.add_parser("dashboard", help="Show gate dashboard")
    dash_parser.set_defaults(func=_dashboard)

    export_parser = subparsers.add_parser("export", help="Export gate status as JSON")
    export_parser.add_argument("--output", "-o", help="Output file path")
    export_parser.set_defaults(func=_export)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
