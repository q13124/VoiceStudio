from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter

if TYPE_CHECKING:
    pass


class LinearAdapter(BaseSourceAdapter):
    """Adapter for Linear MCP server (project management integration)."""

    def __init__(self, priority: int = 0, offline: bool = False):
        super().__init__(source_name="linear", priority=priority, offline=offline)
        self._mcp_enabled = os.getenv("VOICESTUDIO_LINEAR_ENABLED", "").strip() == "1"

    def fetch(self, context: AllocationContext) -> SourceResult:
        """
        Fetch task/issue data from Linear via MCP.
        
        When enabled, queries Linear for:
        - Task details and status
        - Related issues and PRs
        - Team assignments
        - Sprint/milestone context
        
        Falls back gracefully if MCP unavailable.
        """
        start_ms = self._measure()
        
        if not self._mcp_enabled:
            return SourceResult(
                source_name=self.source_name,
                success=True,
                data={"linear_tasks": [], "note": "Linear MCP disabled"},
                size_chars=0,
                fetch_time_ms=self._measure(start_ms),
            )
        
        try:
            # Attempt MCP call to Linear
            tasks = self._query_linear(context)
            
            return SourceResult(
                source_name=self.source_name,
                success=True,
                data={"linear_tasks": tasks},
                size_chars=sum(len(str(t)) for t in tasks),
                fetch_time_ms=self._measure(start_ms),
            )
        except Exception as exc:
            return SourceResult(
                source_name=self.source_name,
                success=False,
                data={},
                size_chars=0,
                fetch_time_ms=self._measure(start_ms),
                error=str(exc),
            )

    def _query_linear(self, context: AllocationContext) -> list:
        """
        Query Linear for task/issue data.
        
        Implementation notes:
        - Use task_id to query Linear for task details
        - Fetch related issues, blockers, dependencies
        - Get sprint/milestone context
        - Return structured task data
        """
        # TODO: Implement actual MCP integration when Linear MCP server configured
        # Requires: linear-mcp-server setup with API key
        return []

    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate size of Linear data."""
        # Typical task: 1000-3000 chars
        return 2000 if self._mcp_enabled else 0
