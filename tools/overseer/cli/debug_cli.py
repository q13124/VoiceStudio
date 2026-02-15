from __future__ import annotations

import argparse
import json

from tools.overseer.issues.recommendation_engine import generate_recommendations
from tools.overseer.issues.store import IssueStore


def _scan(args: argparse.Namespace) -> int:
    store = IssueStore()
    patterns = store.get_top_patterns(limit=args.limit, time_window_hours=args.hours)
    print(f"Top {len(patterns)} patterns (last {args.hours}h):")
    for p in patterns:
        print(f"- {p['pattern_hash']} count={p['count']} | {p['sample_message'][:80]}")
    return 0


def _triage(args: argparse.Namespace) -> int:
    store = IssueStore()
    issues = store.query(limit=args.limit)
    for issue in issues:
        print(f"{issue.id} | {issue.timestamp.isoformat()} | {issue.severity.value} | {issue.status.value} | {issue.message[:80]}")
    return 0


def _analyze(args: argparse.Namespace) -> int:
    store = IssueStore()
    issue = store.get_by_id(args.issue_id)
    if issue is None:
        print(f"Issue not found: {args.issue_id}")
        return 1
    issue.recommendations = generate_recommendations(issue)
    if args.format == "json":
        print(json.dumps(issue.to_dict(), indent=2, default=str))
    else:
        print(f"ID: {issue.id}")
        print(f"Severity: {issue.severity.value} | Status: {issue.status.value}")
        print(f"Message: {issue.message}")
        print("Recommendations:")
        for rec in issue.recommendations:
            print(f"  - {rec.action} (confidence={rec.confidence}): {rec.rationale}")
    return 0


def _validate(args: argparse.Namespace) -> int:
    store = IssueStore()
    issue = store.get_by_id(args.issue_id)
    if issue is None:
        print(f"Issue not found: {args.issue_id}")
        return 1
    print(f"Latest status: {issue.status.value}")
    return 0


def _trace(args: argparse.Namespace) -> int:
    """Trace issues and audit entries by correlation ID."""
    correlation_id = args.correlation_id

    # Query issues with this correlation ID
    store = IssueStore()
    issues = store.get_by_correlation(correlation_id)

    print(f"=== Correlation Trace: {correlation_id} ===")
    print()

    # Display issues
    if issues:
        print(f"Issues ({len(issues)}):")
        for issue in sorted(issues, key=lambda i: i.timestamp):
            print(f"  [{issue.timestamp.isoformat()}] {issue.id}")
            print(f"    Severity: {issue.severity.value} | Status: {issue.status.value}")
            print(f"    Message: {issue.message[:100]}...")
            if issue.component:
                print(f"    Component: {issue.component}")
            print()
    else:
        print("Issues: None found")
        print()

    # Try to get audit entries for this correlation ID
    try:
        from tools.overseer.agent.audit_store import AuditStore
        audit_store = AuditStore()
        audit_entries = audit_store.get_by_correlation_id(correlation_id)

        if audit_entries:
            print(f"Audit Trail ({len(audit_entries)}):")
            for entry in sorted(audit_entries, key=lambda e: e.timestamp):
                print(f"  [{entry.timestamp.isoformat()}] {entry.action}")
                print(f"    Agent: {entry.agent_id} | Success: {entry.success}")
                if entry.details:
                    details_str = json.dumps(entry.details, default=str)[:100]
                    print(f"    Details: {details_str}...")
                print()
        else:
            print("Audit Trail: None found")
    except Exception as e:
        print(f"Audit Trail: Error loading ({e})")

    return 0 if issues else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="overseer debug", description="Debug workflows")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan for issue patterns")
    scan_parser.add_argument("--hours", type=int, default=24, help="Time window in hours")
    scan_parser.add_argument("--limit", type=int, default=10, help="Max patterns")
    scan_parser.set_defaults(func=_scan)

    triage_parser = subparsers.add_parser("triage", help="List recent issues")
    triage_parser.add_argument("--limit", type=int, default=20, help="Max issues")
    triage_parser.set_defaults(func=_triage)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a specific issue")
    analyze_parser.add_argument("issue_id", help="Issue id")
    analyze_parser.add_argument("--format", choices=["text", "json"], default="text")
    analyze_parser.set_defaults(func=_analyze)

    validate_parser = subparsers.add_parser("validate", help="Validate fix status for issue")
    validate_parser.add_argument("issue_id", help="Issue id")
    validate_parser.set_defaults(func=_validate)

    trace_parser = subparsers.add_parser("trace", help="Trace issues and audit entries by correlation ID")
    trace_parser.add_argument("correlation_id", help="Correlation UUID to trace")
    trace_parser.set_defaults(func=_trace)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
