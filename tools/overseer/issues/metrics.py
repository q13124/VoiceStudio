"""
Overseer Issue Metrics - Prometheus exposition format.

Exposes issue counts and recommendation feedback for dashboards and alerting.
No optional dependency: emits Prometheus text format (RFC) directly.
Links issue categories/severity to SLO definitions in docs/governance/SERVICE_LEVEL_OBJECTIVES.md.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from tools.overseer.issues.store import IssueStore, get_feedback_file_path, iter_feedback_lines


# Map issue category/context to affected SLO IDs (from SERVICE_LEVEL_OBJECTIVES.md)
# Used for SLO-aware prioritization and metrics.
ISSUE_CATEGORY_TO_SLO: Dict[str, list] = {
    "synthesis": ["SLO-1"],
    "transcription": ["SLO-2"],
    "api": ["SLO-3"],
    "ui": ["SLO-4"],
    "engine": ["SLO-5"],
    "quality": ["SLO-6"],
    "build": [],
    "agent": [],
}
DEFAULT_SLO = ["SLO-3"]


def _escape_prometheus_label_value(s: str) -> str:
    """Escape backslash and quote for Prometheus label value."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def get_store_stats(
    store: Optional[IssueStore] = None,
    time_window_hours: Optional[int] = 24,
) -> Dict[str, Any]:
    """
    Get issue store statistics for the optional time window.
    If time_window_hours is None, all-time stats are returned.
    """
    s = store if store is not None else IssueStore()
    if time_window_hours is not None:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=time_window_hours)
        stats = s.get_stats(start_time=start, end_time=end)
    else:
        stats = s.get_stats()
    return stats


def get_feedback_counts(days: int = 7) -> Dict[str, int]:
    """Count recommendation feedback outcomes (success, failure, deferred) in the last N days."""
    counts: Dict[str, int] = {"success": 0, "failure": 0, "deferred": 0}
    path = get_feedback_file_path()
    if not path.exists():
        return counts
    for data in iter_feedback_lines(days=days):
        outcome = (data.get("outcome") or "").lower()
        if outcome in counts:
            counts[outcome] += 1
    return counts


def get_prometheus_metrics(
    store: Optional[IssueStore] = None,
    time_window_hours: int = 24,
    include_feedback: bool = True,
) -> str:
    """
    Return Prometheus text exposition format for issue and feedback metrics.

    Metrics:
      overseer_issues_total{severity,status,instance_type} - count in window
      overseer_recommendation_feedback_total{outcome} - count in last 7 days
    """
    lines: list = []
    stats = get_store_stats(store=store, time_window_hours=time_window_hours)

    # Issue counts: one metric with labels (severity, status, instance_type)
    by_sev = stats.get("by_severity") or {}
    for sev, count in by_sev.items():
        v = _escape_prometheus_label_value(sev)
        lines.append(f'overseer_issues_total{{dimension="severity",value="{v}"}} {count}')
    by_status = stats.get("by_status") or {}
    for st, count in by_status.items():
        v = _escape_prometheus_label_value(st)
        lines.append(f'overseer_issues_total{{dimension="status",value="{v}"}} {count}')
    by_type = stats.get("by_instance_type") or {}
    for it, count in by_type.items():
        v = _escape_prometheus_label_value(it)
        lines.append(f'overseer_issues_total{{dimension="instance_type",value="{v}"}} {count}')
    lines.append(f'overseer_issues_total{{dimension="total"}} {stats.get("total", 0)}')

    if include_feedback:
        feedback = get_feedback_counts(days=7)
        for outcome, count in feedback.items():
            v = _escape_prometheus_label_value(outcome)
            lines.append(f'overseer_recommendation_feedback_total{{outcome="{v}"}} {count}')

    return "\n".join(lines) + "\n"


def get_affected_slos(category: str) -> list:
    """
    Return SLO IDs affected by an issue category (from SERVICE_LEVEL_OBJECTIVES.md).
    Used for SLO-aware prioritization and linking issues to SLO definitions.
    """
    return list(ISSUE_CATEGORY_TO_SLO.get(category.lower(), DEFAULT_SLO))
