from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter

if TYPE_CHECKING:
    pass


class GitHubAdapter(BaseSourceAdapter):
    """Adapter for GitHub MCP server (PR, issues, repo integration)."""

    def __init__(self, priority: int = 0, offline: bool = False):
        super().__init__(source_name="github", priority=priority, offline=offline)
        self._mcp_enabled = os.getenv("VOICESTUDIO_GITHUB_MCP_ENABLED", "").strip() == "1"

    def fetch(self, context: AllocationContext) -> SourceResult:
        """
        Fetch PR/issue data from GitHub via MCP.

        When enabled, queries GitHub for:
        - Open PRs related to task
        - Issue discussions and comments
        - CI/CD status
        - Code review feedback

        Falls back gracefully if MCP unavailable.
        """
        def _load() -> dict:
            if not self._mcp_enabled:
                return {"github_prs": [], "github_issues": [], "note": "GitHub MCP disabled"}

            # Attempt MCP call to GitHub
            prs, issues = self._query_github(context)
            return {"github_prs": prs, "github_issues": issues}

        return self._measure(_load, context)

    def _query_github(self, context: AllocationContext) -> tuple[list, list]:
        """
        Query GitHub for PR and issue data.

        Implementation notes:
        - Parse task_id to extract PR/issue numbers if applicable
        - Query GitHub API via MCP for PR details
        - Fetch related issues and comments
        - Get CI/CD check status
        - Return (prs, issues) tuple
        """
        # TODO: Implement actual MCP integration when GitHub MCP server configured
        # Requires: github-mcp-server setup with PAT token
        return [], []

    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate size of GitHub data."""
        # Typical PR + issues: 2000-5000 chars
        return 3000 if self._mcp_enabled else 0
