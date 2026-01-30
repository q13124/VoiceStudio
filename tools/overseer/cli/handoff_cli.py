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

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
