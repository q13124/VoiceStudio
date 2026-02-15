"""
Overseer Issue Metrics - Prometheus exposition format.

Exposes issue counts and recommendation feedback for dashboards and alerting.
No optional dependency: emits Prometheus text format (RFC) directly.
Links issue categories/severity to SLO definitions in docs/governance/SERVICE_LEVEL_OBJECTIVES.md.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from tools.overseer.issues.store import IssueStore, get_feedback_file_path, iter_feedback_lines

# Map issue category/context to affected SLO IDs (from SERVICE_LEVEL_OBJECTIVES.md)
# Used for SLO-aware prioritization and metrics.
# Extended with comprehensive keyword mappings for issue classification.
ISSUE_CATEGORY_TO_SLO: dict[str, list] = {
    # SLO-1: Synthesis latency and reliability
    "synthesis": ["SLO-1"],
    "tts": ["SLO-1"],
    "voice": ["SLO-1"],
    "audio": ["SLO-1"],
    "xtts": ["SLO-1"],
    "tacotron": ["SLO-1"],

    # SLO-2: Transcription latency and reliability
    "transcription": ["SLO-2"],
    "stt": ["SLO-2"],
    "whisper": ["SLO-2"],

    # SLO-3: API response time and availability
    "api": ["SLO-3"],
    "backend": ["SLO-3"],
    "service": ["SLO-3"],
    "ipc": ["SLO-3"],
    "rest": ["SLO-3"],
    "websocket": ["SLO-3"],

    # SLO-4: UI responsiveness
    "ui": ["SLO-4"],
    "xaml": ["SLO-4"],
    "panel": ["SLO-4"],
    "view": ["SLO-4"],
    "winui": ["SLO-4"],
    "layout": ["SLO-4"],
    "animation": ["SLO-4"],
    "control": ["SLO-4"],

    # SLO-5: Engine availability and performance
    "engine": ["SLO-5"],
    "rvc": ["SLO-5"],
    "model": ["SLO-5"],
    "inference": ["SLO-5"],
    "gpu": ["SLO-5"],
    "cuda": ["SLO-5"],
    "tensor": ["SLO-5"],
    "torch": ["SLO-5"],

    # SLO-6: Quality metrics
    "quality": ["SLO-6"],

    # No direct SLO impact (infra/tooling)
    "build": [],
    "ci": [],
    "cd": [],
    "pipeline": [],
    "compile": [],
    "msbuild": [],
    "dotnet": [],
    "nuget": [],
    "pip": [],
    "dependency": [],
    "toolchain": [],
    "test": [],
    "pytest": [],
    "mstest": [],
    "lint": [],
    "agent": [],
    "packaging": [],
    "installer": [],
    "msix": [],
    "release": [],
    "deploy": [],
    "version": [],
    "update": [],
    "distribution": [],
    "governance": [],
    "coordination": [],
    "priority": [],
    "escalation": [],
    "task": [],
    "workflow": [],
    "architecture": [],
    "adr": [],
    "contract": [],
    "boundary": [],
    "interface": [],
    "protocol": [],
    "schema": [],

    # Debug/error categories typically affect multiple SLOs
    "debug": ["SLO-3", "SLO-4", "SLO-5"],
    "error": ["SLO-3", "SLO-4", "SLO-5"],
    "exception": ["SLO-3", "SLO-4", "SLO-5"],
    "crash": ["SLO-3", "SLO-4", "SLO-5"],
    "diagnostic": [],
    "traceback": ["SLO-3"],
    "stacktrace": ["SLO-3"],
    "memory": ["SLO-5"],
    "leak": ["SLO-5"],
    "hang": ["SLO-4", "SLO-5"],
    "deadlock": ["SLO-4", "SLO-5"],
    "timeout": ["SLO-3", "SLO-5"],
    "regression": ["SLO-1", "SLO-2", "SLO-6"],

    # Core platform
    "runtime": ["SLO-5"],
    "storage": ["SLO-3"],
    "boot": ["SLO-4"],
    "job": ["SLO-3"],
    "queue": ["SLO-3"],
    "preflight": ["SLO-5"],
    "config": [],
    "settings": [],
    "database": ["SLO-3"],
}
DEFAULT_SLO = ["SLO-3"]


def _escape_prometheus_label_value(s: str) -> str:
    """Escape backslash and quote for Prometheus label value."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def get_store_stats(
    store: IssueStore | None = None,
    time_window_hours: int | None = 24,
) -> dict[str, Any]:
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


def get_feedback_counts(days: int = 7) -> dict[str, int]:
    """Count recommendation feedback outcomes (success, failure, deferred) in the last N days."""
    counts: dict[str, int] = {"success": 0, "failure": 0, "deferred": 0}
    path = get_feedback_file_path()
    if not path.exists():
        return counts
    for data in iter_feedback_lines(days=days):
        outcome = (data.get("outcome") or "").lower()
        if outcome in counts:
            counts[outcome] += 1
    return counts


def get_prometheus_metrics(
    store: IssueStore | None = None,
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
