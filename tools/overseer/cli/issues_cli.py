"""
Issues CLI - query and manage overseer issues for AI Overseer review.
Supports bulk operations, watch mode, CSV export, and paging.
"""

import argparse
import csv
import io
import json
import sys
import time
from datetime import datetime
from typing import List, Optional

from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssueSeverity,
    IssueStatus,
)
from tools.overseer.issues.store import IssueStore


def _query(args: argparse.Namespace) -> int:
    store = IssueStore()
    severity = None
    if args.severity:
        severity = [IssueSeverity(s.strip().lower()) for s in args.severity.split(",")]
    status = None
    if args.status:
        status = [IssueStatus(s.strip().lower()) for s in args.status.split(",")]
    instance_type = None
    if args.instance_type:
        instance_type = [
            InstanceType(t.strip().lower()) for t in args.instance_type.split(",")
        ]

    page_size = getattr(args, "page_size", None) or args.limit
    page = getattr(args, "page", 1)
    offset = (max(1, page) - 1) * page_size if page_size else 0
    fetch_limit = (offset + page_size) if page_size else args.limit

    issues = store.query(
        severity=severity,
        status=status,
        instance_type=instance_type,
        limit=fetch_limit,
    )
    if offset > 0 and offset < len(issues):
        issues = issues[offset:offset + page_size]
    elif offset > 0:
        issues = []

    if getattr(args, "format", None) == "csv":
        _print_issues_csv(issues)
    elif args.format == "json":
        out = [i.to_dict() for i in issues]
        print(json.dumps(out, indent=2, default=str))
    elif args.format == "table":
        _print_issues_table(issues)
    else:
        _print_issues_summary(issues)
    return 0


def _print_issues_table(issues: List[Issue]) -> None:
    """Print issues as a simple table."""
    print(f"{'ID':<38} {'Time':<22} {'Type':<8} {'Sev':<8} {'Status':<12} Message")
    print("-" * 120)
    for i in issues:
        ts = i.timestamp.strftime("%Y-%m-%dT%H:%M:%S") if i.timestamp else ""
        msg = (i.message or "")[:50]
        print(f"{i.id:<38} {ts:<22} {i.instance_type.value:<8} {i.severity.value:<8} {i.status.value:<12} {msg}")


def _print_issues_summary(issues: List[Issue]) -> None:
    """Print a short summary of issues."""
    print(f"Issues: {len(issues)}")
    for i in issues:
        msg = (i.message or "")[:60]
        print(f"- {i.id} | {i.timestamp.isoformat()} | {i.instance_type.value} | {i.severity.value} | {i.status.value} | {msg}")


def _print_issues_csv(issues: List[Issue]) -> None:
    """Print issues as CSV to stdout."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "timestamp", "instance_type", "instance_id", "severity", "status", "category", "error_type", "message"])
    for i in issues:
        msg = (i.message or "").replace("\n", " ").replace("\r", "")[:500]
        w.writerow([
            i.id,
            i.timestamp.isoformat() if i.timestamp else "",
            i.instance_type.value,
            i.instance_id,
            i.severity.value,
            i.status.value,
            i.category,
            i.error_type,
            msg,
        ])
    print(buf.getvalue(), end="")


def _get(args: argparse.Namespace) -> int:
    store = IssueStore()
    issue = store.get_by_id(args.issue_id)
    if issue is None:
        print(f"Issue not found: {args.issue_id}", file=sys.stderr)
        return 1
    from tools.overseer.issues.recommendation_engine import generate_recommendations
    issue.recommendations = generate_recommendations(issue)
    if args.format == "json":
        print(json.dumps(issue.to_dict(), indent=2, default=str))
    else:
        print(f"ID: {issue.id}")
        print(f"Timestamp: {issue.timestamp.isoformat()}")
        print(f"Instance: {issue.instance_type.value} / {issue.instance_id}")
        print(f"Severity: {issue.severity.value} | Status: {issue.status.value}")
        print(f"Error: {issue.error_type} - {issue.message}")
        print("Recommendations:")
        for r in issue.recommendations:
            print(f"  - {r.action} (confidence={r.confidence}): {r.rationale}")
    return 0


def _patterns(args: argparse.Namespace) -> int:
    store = IssueStore()
    hours = 24
    if args.time_window:
        if args.time_window.endswith("h"):
            hours = int(args.time_window[:-1])
        elif args.time_window.endswith("d"):
            hours = int(args.time_window[:-1]) * 24
    top = store.get_top_patterns(limit=args.limit, time_window_hours=hours)
    if args.format == "json":
        print(json.dumps(top, indent=2))
    else:
        print(f"Top {len(top)} patterns (last {hours}h):")
        for p in top:
            print(f"  {p['pattern_hash']} count={p['count']} | {p['sample_message'][:60]}")
    return 0


def _trace(args: argparse.Namespace) -> int:
    store = IssueStore()
    issues = store.get_by_correlation(args.correlation_id)
    if args.format == "json":
        print(json.dumps([i.to_dict() for i in issues], indent=2, default=str))
    else:
        print(f"Correlation trace: {args.correlation_id} ({len(issues)} issues)")
        for i in issues:
            print(f"  - {i.id} | {i.instance_type.value} | {i.severity.value} | {i.message[:50]}")
    return 0


def _export(args: argparse.Namespace) -> int:
    store = IssueStore()
    severity = None
    if args.severity:
        severity = [IssueSeverity(s.strip().lower()) for s in args.severity.split(",")]
    status = None
    if args.status:
        status = [IssueStatus(s.strip().lower()) for s in args.status.split(",")]
    issues = store.query(severity=severity, status=status, limit=args.limit)
    fmt = getattr(args, "format", "jsonl")
    out_path = args.output or ("overseer_review.csv" if fmt == "csv" else "overseer_review.jsonl")
    if fmt == "csv":
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "timestamp", "instance_type", "instance_id", "severity", "status", "category", "error_type", "message"])
            for i in issues:
                msg = (i.message or "").replace("\n", " ").replace("\r", "")[:500]
                w.writerow([i.id, i.timestamp.isoformat() if i.timestamp else "", i.instance_type.value, i.instance_id, i.severity.value, i.status.value, i.category, i.error_type, msg])
    else:
        with open(out_path, "w", encoding="utf-8") as f:
            for i in issues:
                f.write(i.to_json_line() + "\n")
    print(f"Exported {len(issues)} issues to {out_path}")
    return 0


def _acknowledge(args: argparse.Namespace) -> int:
    store = IssueStore()
    ok = store.update_status(args.issue_id, IssueStatus.ACKNOWLEDGED)
    if not ok:
        print(f"Issue not found: {args.issue_id}", file=sys.stderr)
        return 1
    print(f"Acknowledged {args.issue_id}")
    return 0


def _resolve(args: argparse.Namespace) -> int:
    store = IssueStore()
    ok = store.update_status(
        args.issue_id,
        IssueStatus.RESOLVED,
        resolved_by=args.note or "cli",
    )
    if not ok:
        print(f"Issue not found: {args.issue_id}", file=sys.stderr)
        return 1
    if getattr(args, "action", None) and getattr(args, "outcome", None):
        from tools.overseer.issues.recommendation_engine import record_recommendation_outcome
        record_recommendation_outcome(
            args.issue_id,
            args.action,
            args.outcome,
            note=args.note,
        )
    print(f"Resolved {args.issue_id}")
    return 0


def _feedback(args: argparse.Namespace) -> int:
    """Record that a recommendation was applied and its outcome (action validation)."""
    from tools.overseer.issues.recommendation_engine import record_recommendation_outcome
    ok = record_recommendation_outcome(
        args.issue_id,
        args.action,
        args.outcome,
        note=args.note,
    )
    if not ok:
        print("Invalid outcome; use success, failure, or deferred", file=sys.stderr)
        return 1
    print(f"Recorded {args.outcome} for {args.action} on issue {args.issue_id}")
    return 0


def _escalate(args: argparse.Namespace) -> int:
    store = IssueStore()
    ok = store.update_status(args.issue_id, IssueStatus.ESCALATED)
    if not ok:
        print(f"Issue not found: {args.issue_id}", file=sys.stderr)
        return 1
    print(f"Escalated {args.issue_id}")
    return 0


def _bulk_ack(args: argparse.Namespace) -> int:
    """Batch acknowledge issues by IDs or by query (--status/--severity)."""
    store = IssueStore()
    if getattr(args, "ids", None):
        id_list = [x.strip() for x in args.ids.split(",") if x.strip()]
    else:
        severity = None
        if getattr(args, "severity", None):
            severity = [IssueSeverity(s.strip().lower()) for s in args.severity.split(",")]
        status = None
        if getattr(args, "status", None):
            status = [IssueStatus(s.strip().lower()) for s in args.status.split(",")]
        issues = store.query(severity=severity, status=status, limit=getattr(args, "limit", 100))
        id_list = [i.id for i in issues]
    done = 0
    for issue_id in id_list:
        if store.update_status(issue_id, IssueStatus.ACKNOWLEDGED):
            done += 1
            if getattr(args, "verbose", False):
                print(f"Acknowledged {issue_id}")
    print(f"Acknowledged {done}/{len(id_list)} issues")
    return 0


def _bulk_resolve(args: argparse.Namespace) -> int:
    """Batch resolve issues by IDs or by query (--status/--severity)."""
    store = IssueStore()
    note = getattr(args, "note", None) or "cli-bulk"
    if getattr(args, "ids", None):
        id_list = [x.strip() for x in args.ids.split(",") if x.strip()]
    else:
        severity = None
        if getattr(args, "severity", None):
            severity = [IssueSeverity(s.strip().lower()) for s in args.severity.split(",")]
        status = None
        if getattr(args, "status", None):
            status = [IssueStatus(s.strip().lower()) for s in args.status.split(",")]
        issues = store.query(severity=severity, status=status, limit=getattr(args, "limit", 100))
        id_list = [i.id for i in issues]
    done = 0
    for issue_id in id_list:
        if store.update_status(issue_id, IssueStatus.RESOLVED, resolved_by=note):
            done += 1
            if getattr(args, "verbose", False):
                print(f"Resolved {issue_id}")
    print(f"Resolved {done}/{len(id_list)} issues")
    return 0


def _create_task(args: argparse.Namespace) -> int:
    """Create a task brief from a single issue."""
    from tools.overseer.issues.task_generator import IssueToTaskGenerator
    
    store = IssueStore()
    issue = store.get_by_id(args.issue_id)
    
    if not issue:
        print(f"Issue not found: {args.issue_id}")
        return 1
    
    generator = IssueToTaskGenerator()
    
    if getattr(args, "dry_run", False):
        content = generator.generate_task_brief(issue)
        print(content)
        return 0
    
    task_path = generator.create_task_file(issue)
    
    # Link issue to task
    task_id = task_path.stem  # e.g., "TASK-0014"
    generator.link_issue_to_task(args.issue_id, task_id)
    
    print(f"Created: {task_path}")
    print(f"Linked issue {args.issue_id} to {task_id}")
    return 0


def _auto_task(args: argparse.Namespace) -> int:
    """Auto-create tasks for qualifying issues (critical/high, recurring)."""
    from tools.overseer.issues.task_generator import IssueToTaskGenerator
    
    store = IssueStore()
    generator = IssueToTaskGenerator(issue_store=store)
    
    # Query unlinked critical/high issues
    issues = store.query(
        severity=[IssueSeverity.CRITICAL, IssueSeverity.HIGH],
        status=[IssueStatus.NEW, IssueStatus.ACKNOWLEDGED],
        limit=getattr(args, "limit", 10) * 3,  # Get extra for filtering
    )
    
    # Filter to those without linked tasks and check if should create
    to_create = []
    for issue in issues:
        if issue.context and issue.context.get("linked_task"):
            continue
        if generator.should_create_task(issue):
            to_create.append(issue)
    
    # Limit
    to_create = to_create[:getattr(args, "limit", 10)]
    
    if getattr(args, "dry_run", False):
        print(f"Would create {len(to_create)} tasks:")
        for issue in to_create:
            sev = issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity)
            print(f"  - {issue.id}: [{sev.upper()}] {issue.message[:50]}...")
        return 0
    
    created = 0
    for issue in to_create:
        try:
            task_path = generator.create_task_file(issue)
            task_id = task_path.stem
            generator.link_issue_to_task(issue.id, task_id)
            print(f"Created {task_id} from {issue.id}")
            created += 1
        except Exception as e:
            print(f"Failed to create task for {issue.id}: {e}")
    
    print(f"Created {created}/{len(to_create)} tasks")
    return 0


def _link_task(args: argparse.Namespace) -> int:
    """Link an existing issue to an existing task."""
    from tools.overseer.issues.task_generator import IssueToTaskGenerator
    
    generator = IssueToTaskGenerator()
    
    if generator.link_issue_to_task(args.issue_id, args.task_id):
        print(f"Linked {args.issue_id} to {args.task_id}")
        return 0
    else:
        print(f"Failed to link {args.issue_id} to {args.task_id}")
        return 1


def _watch(args: argparse.Namespace) -> int:
    """Stream new issues (tail -f style). Polls store at --interval seconds."""
    store = IssueStore()
    interval = max(1, getattr(args, "interval", 5))
    seen: set = set()
    try:
        while True:
            issues = store.query(limit=getattr(args, "limit", 100))
            for i in issues:
                if i.id not in seen:
                    seen.add(i.id)
                    ts = i.timestamp.strftime("%Y-%m-%dT%H:%M:%S") if i.timestamp else ""
                    msg = (i.message or "")[:60]
                    print(f"{i.id} | {ts} | {i.instance_type.value} | {i.severity.value} | {i.status.value} | {msg}")
            time.sleep(interval)
    # Best effort - failure is acceptable here
    except KeyboardInterrupt:
        pass
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="overseer issues",
        description="Issue logging and recommendation system for Overseer review",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Query issues with filters")
    query_parser.add_argument(
        "--severity",
        help="Comma-separated severity (low,medium,high,critical)",
    )
    query_parser.add_argument(
        "--status",
        help="Comma-separated status (new,acknowledged,in_progress,resolved,escalated)",
    )
    query_parser.add_argument(
        "--instance-type",
        help="Comma-separated instance type (agent,engine,build)",
    )
    query_parser.add_argument("--limit", type=int, default=20, help="Max issues to return")
    query_parser.add_argument("--page", type=int, default=1, help="Page number (1-based)")
    query_parser.add_argument("--page-size", type=int, help="Page size (defaults to --limit)")
    query_parser.add_argument(
        "--format",
        choices=["json", "table", "summary", "csv"],
        default="summary",
        help="Output format",
    )
    query_parser.set_defaults(func=_query)

    get_parser = subparsers.add_parser("get", help="Get issue by ID with recommendations")
    get_parser.add_argument("issue_id", help="Issue UUID")
    get_parser.add_argument("--format", choices=["json", "text"], default="text")
    get_parser.set_defaults(func=_get)

    patterns_parser = subparsers.add_parser("patterns", help="Top issue patterns by frequency")
    patterns_parser.add_argument("--time-window", default="24h", help="e.g. 24h or 7d")
    patterns_parser.add_argument("--limit", type=int, default=10)
    patterns_parser.add_argument("--format", choices=["json", "text"], default="text")
    patterns_parser.set_defaults(func=_patterns)

    trace_parser = subparsers.add_parser("trace", help="All issues for a correlation ID")
    trace_parser.add_argument("correlation_id", help="Correlation UUID")
    trace_parser.add_argument("--format", choices=["json", "text"], default="text")
    trace_parser.set_defaults(func=_trace)

    export_parser = subparsers.add_parser("export", help="Export issues to JSONL or CSV for AI review")
    export_parser.add_argument("--output", "-o", help="Output file path")
    export_parser.add_argument("--severity", help="Comma-separated severity filter")
    export_parser.add_argument("--status", help="Comma-separated status filter")
    export_parser.add_argument("--limit", type=int, default=1000)
    export_parser.add_argument("--format", choices=["jsonl", "csv"], default="jsonl", help="Export format")
    export_parser.set_defaults(func=_export)

    ack_parser = subparsers.add_parser("acknowledge", help="Mark issue as acknowledged")
    ack_parser.add_argument("issue_id", help="Issue UUID")
    ack_parser.set_defaults(func=_acknowledge)

    resolve_parser = subparsers.add_parser("resolve", help="Mark issue as resolved")
    resolve_parser.add_argument("issue_id", help="Issue UUID")
    resolve_parser.add_argument("--note", help="Resolution note")
    resolve_parser.add_argument(
        "--action",
        help="Recommendation action applied (e.g. retry_with_params, apply_fix:fix-1)",
    )
    resolve_parser.add_argument(
        "--outcome",
        choices=["success", "failure", "deferred"],
        help="Outcome of the action (records feedback for calibration)",
    )
    resolve_parser.set_defaults(func=_resolve)

    feedback_parser = subparsers.add_parser(
        "feedback",
        help="Record recommendation outcome (action validation) without resolving",
    )
    feedback_parser.add_argument("issue_id", help="Issue UUID")
    feedback_parser.add_argument(
        "action",
        help="Recommendation action applied (e.g. retry_with_params)",
    )
    feedback_parser.add_argument(
        "outcome",
        choices=["success", "failure", "deferred"],
        help="Outcome of the action",
    )
    feedback_parser.add_argument("--note", help="Optional note")
    feedback_parser.set_defaults(func=_feedback)

    escalate_parser = subparsers.add_parser("escalate", help="Escalate issue to human")
    escalate_parser.add_argument("issue_id", help="Issue UUID")
    escalate_parser.set_defaults(func=_escalate)

    bulk_ack_parser = subparsers.add_parser("bulk-ack", help="Batch acknowledge issues by IDs or query")
    bulk_ack_parser.add_argument("--ids", help="Comma-separated issue IDs")
    bulk_ack_parser.add_argument("--status", help="Filter by status (with --limit)")
    bulk_ack_parser.add_argument("--severity", help="Comma-separated severity filter")
    bulk_ack_parser.add_argument("--limit", type=int, default=100, help="Max issues when using --status/--severity")
    bulk_ack_parser.add_argument("-v", "--verbose", action="store_true", help="Print each ID")
    bulk_ack_parser.set_defaults(func=_bulk_ack)

    bulk_resolve_parser = subparsers.add_parser("bulk-resolve", help="Batch resolve issues by IDs or query")
    bulk_resolve_parser.add_argument("--ids", help="Comma-separated issue IDs")
    bulk_resolve_parser.add_argument("--status", help="Filter by status (with --limit)")
    bulk_resolve_parser.add_argument("--severity", help="Comma-separated severity filter")
    bulk_resolve_parser.add_argument("--limit", type=int, default=100, help="Max issues when using --status/--severity")
    bulk_resolve_parser.add_argument("--note", help="Resolution note for all")
    bulk_resolve_parser.add_argument("-v", "--verbose", action="store_true", help="Print each ID")
    bulk_resolve_parser.set_defaults(func=_bulk_resolve)

    watch_parser = subparsers.add_parser("watch", help="Stream new issues (tail -f style; Ctrl+C to stop)")
    watch_parser.add_argument("--interval", type=int, default=5, help="Poll interval in seconds")
    watch_parser.add_argument("--limit", type=int, default=100, help="Max issues per poll")
    watch_parser.set_defaults(func=_watch)

    # Task generation commands
    create_task_parser = subparsers.add_parser("create-task", help="Create a task brief from an issue")
    create_task_parser.add_argument("issue_id", help="Issue UUID")
    create_task_parser.add_argument("--dry-run", action="store_true", help="Print brief without creating file")
    create_task_parser.set_defaults(func=_create_task)

    auto_task_parser = subparsers.add_parser("auto-task", help="Auto-create tasks for qualifying issues")
    auto_task_parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    auto_task_parser.add_argument("--limit", type=int, default=10, help="Max tasks to create")
    auto_task_parser.set_defaults(func=_auto_task)

    link_task_parser = subparsers.add_parser("link-task", help="Link an existing issue to an existing task")
    link_task_parser.add_argument("issue_id", help="Issue UUID")
    link_task_parser.add_argument("task_id", help="Task ID (e.g., TASK-0014)")
    link_task_parser.set_defaults(func=_link_task)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
