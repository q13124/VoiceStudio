from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter
from tools.overseer.issues.models import IssueSeverity
from tools.overseer.issues.store import IssueStore


class IssuesSourceAdapter(BaseSourceAdapter):
    """Fetch recent overseer issues for context injection."""

    def __init__(
        self,
        max_issues: int = 10,
        severity_filter: list[str] | None = None,
        time_window_hours: int = 24,
        include_recommendations: bool = True,
        offline: bool = True,
    ):
        super().__init__(source_name="issues", priority=40, offline=offline)
        self._max_issues = max(1, int(max_issues))
        self._severity_filter = severity_filter or []
        self._time_window_hours = max(1, int(time_window_hours))
        self._include_recommendations = include_recommendations

    def _parse_severity(self) -> list[IssueSeverity] | None:
        if not self._severity_filter:
            return None
        out = []
        for value in self._severity_filter:
            try:
                out.append(IssueSeverity(value.strip().lower()))
            except Exception:
                continue
        return out or None

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> dict[str, Any]:
            store = IssueStore()
            end = datetime.now(timezone.utc)
            start = end - timedelta(hours=self._time_window_hours)
            severity = self._parse_severity()
            issues = store.query(severity=severity, start_time=start, end_time=end, limit=self._max_issues)
            out = []
            for issue in issues:
                record: dict[str, Any] = {
                    "id": issue.id,
                    "timestamp": issue.timestamp.isoformat(),
                    "instance_type": issue.instance_type.value,
                    "severity": issue.severity.value,
                    "status": issue.status.value,
                    "message": issue.message,
                }
                if self._include_recommendations and issue.recommendations:
                    record["recommendations"] = [
                        {"action": r.action, "confidence": r.confidence, "rationale": r.rationale}
                        for r in issue.recommendations
                    ]
                out.append(record)
            return {"issues": out}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 1500
