from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.overseer.ledger_parser import LedgerParser


def _validate(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    result = parser.validate()
    for warn in result.warnings:
        print(f"[WARN] {warn}")
    if result.errors:
        for err in result.errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return 1
    print("Ledger validation PASS")
    return 0


def _status(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    summary = parser.get_summary()
    print(f"Entries: {summary.total_entries}")
    print(f"DONE: {summary.done_entries}")
    print(f"OPEN: {summary.open_entries}")
    print(f"IN_PROGRESS: {summary.in_progress_entries}")
    print(f"BLOCKED: {summary.blocked_entries}")
    print(f"Completion: {summary.completion_percent:.1f}%")
    return 0


def _gaps(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    result = parser.validate()
    if not result.errors:
        print("No ledger gaps detected.")
        return 0
    for err in result.errors:
        print(f"- {err}")
    return 1


def _entry(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    entries = parser.parse()
    for entry in entries:
        if entry.id == args.entry_id:
            print(f"ID: {entry.id}")
            print(f"State: {entry.state.value}")
            print(f"Severity: {entry.severity.value}")
            print(f"Gate: {entry.gate.value}")
            print(f"Owner: {entry.owner_role}")
            print(f"Categories: {', '.join([c.value for c in entry.categories])}")
            print(f"Title: {entry.title}")
            return 0
    print(f"Entry not found: {args.entry_id}", file=sys.stderr)
    return 1


def _list(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    entries = parser.parse()
    for entry in entries:
        print(entry.id)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="overseer ledger", description="Ledger commands")
    parser.add_argument("--ledger", help="Path to QUALITY_LEDGER.md")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate ledger")
    validate_parser.set_defaults(func=_validate)

    status_parser = subparsers.add_parser("status", help="Ledger summary")
    status_parser.set_defaults(func=_status)

    gaps_parser = subparsers.add_parser("gaps", help="Show validation gaps")
    gaps_parser.set_defaults(func=_gaps)

    entry_parser = subparsers.add_parser("entry", help="Show entry details")
    entry_parser.add_argument("entry_id", help="Ledger ID to display")
    entry_parser.set_defaults(func=_entry)

    list_parser = subparsers.add_parser("list", help="List ledger IDs")
    list_parser.set_defaults(func=_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
