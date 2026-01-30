from __future__ import annotations

from typing import Any, Dict

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter


class GitKrakenAdapter(BaseSourceAdapter):
    """Placeholder adapter for GitKraken metadata (disabled by default)."""

    def __init__(self, include_issues: bool = True, include_prs: bool = True, commit_limit: int = 5, offline: bool = True):
        super().__init__(source_name="gitkraken", priority=15, offline=offline)
        self._include_issues = include_issues
        self._include_prs = include_prs
        self._commit_limit = commit_limit

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> Dict[str, Any]:
            return {"gitkraken": {"issues": [] if self._include_issues else None, "prs": [] if self._include_prs else None}}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 500
