from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.overseer.gate_tracker import GateTracker
from tools.overseer.ledger_parser import LedgerParser
from tools.overseer.report_engine import ReportEngine


def _daily(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    engine = ReportEngine(parser, tracker)
    lines = engine._build_report_lines()
    if args.output:
        Path(args.output).write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote daily report to {args.output}")
        return 0
    print("\n".join(lines))
    return 0


def _gate(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    engine = ReportEngine(parser, tracker)
    lines = engine.generate_gate_report()
    if args.output:
        Path(args.output).write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote gate report to {args.output}")
        return 0
    print("\n".join(lines))
    return 0


def _comprehensive(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    engine = ReportEngine(parser, tracker)
    path = engine.generate_comprehensive_report(save=bool(args.output or args.save))
    if args.output and path:
        Path(args.output).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Wrote comprehensive report to {args.output}")
        return 0
    if args.save:
        print(f"Saved report to {path}")
        return 0
    if path:
        print(path.read_text(encoding="utf-8"))
    return 0


def _export(args: argparse.Namespace) -> int:
    parser = LedgerParser(Path(args.ledger) if args.ledger else None)
    tracker = GateTracker(parser)
    summary = parser.get_summary()
    statuses = tracker.compute_statuses(force=True)
    payload = {
        "summary": {
            "total_entries": summary.total_entries,
            "done_entries": summary.done_entries,
            "open_entries": summary.open_entries,
            "blocked_entries": summary.blocked_entries,
            "in_progress_entries": summary.in_progress_entries,
            "completion_percent": summary.completion_percent,
        },
        "gates": [
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
        ],
    }
    output = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote report JSON to {args.output}")
        return 0
    print(output)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="overseer report", description="Report generation")
    parser.add_argument("--ledger", help="Ledger path override")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily_parser = subparsers.add_parser("daily", help="Generate daily status report")
    daily_parser.add_argument("--output", "-o", help="Write report to file")
    daily_parser.set_defaults(func=_daily)

    gate_parser = subparsers.add_parser("gate", help="Generate gate report")
    gate_parser.add_argument("--output", "-o", help="Write report to file")
    gate_parser.set_defaults(func=_gate)

    comp_parser = subparsers.add_parser("comprehensive", help="Generate comprehensive report")
    comp_parser.add_argument("--save", action="store_true", help="Save report under docs/reports/verification")
    comp_parser.add_argument("--output", "-o", help="Write report to file")
    comp_parser.set_defaults(func=_comprehensive)

    export_parser = subparsers.add_parser("export", help="Export report as JSON")
    export_parser.add_argument("--output", "-o", help="Write JSON to file")
    export_parser.set_defaults(func=_export)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
