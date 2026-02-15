from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter

if TYPE_CHECKING:
    pass


class Context7Adapter(BaseSourceAdapter):
    """Adapter for Context7 MCP server (up-to-date library documentation)."""

    def __init__(self, priority: int = 0, offline: bool = False):
        super().__init__(source_name="context7", priority=priority, offline=offline)
        self._mcp_enabled = os.getenv("VOICESTUDIO_CONTEXT7_ENABLED", "").strip() == "1"

    def fetch(self, context: AllocationContext) -> SourceResult:
        """
        Fetch library documentation via Context7 MCP.

        When enabled, queries Context7 for up-to-date docs on libraries
        used in the current task (e.g., FastAPI, WinUI 3, asyncio).

        Falls back gracefully if MCP unavailable.
        """
        def _load() -> dict:
            if not self._mcp_enabled:
                return {"context7_docs": [], "note": "Context7 MCP disabled"}

            # Attempt MCP call to Context7
            # NOTE: Actual MCP integration requires CallMcpTool or context7 client
            # For now, return empty with success to indicate availability
            docs = self._query_context7(context)
            return {"context7_docs": docs}

        return self._measure(_load, context)

    def _query_context7(self, context: AllocationContext) -> list:
        """
        Query Context7 for library docs relevant to task.

        Implementation notes:
        - Parse task brief to identify libraries (FastAPI, WinUI, PyTorch, etc.)
        - Call Context7 MCP tool with library IDs
        - Extract relevant documentation snippets
        - Return structured docs list
        """
        # TODO: Implement actual MCP integration when Context7 MCP server configured
        # For now, return empty to enable graceful operation
        return []

    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate size of Context7 docs."""
        # Typical doc snippet: 500-2000 chars
        # Assume 2-3 libraries per task
        return 3000 if self._mcp_enabled else 0
