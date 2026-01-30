from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from tools.context.core.models import AllocationContext, GitContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter


class GitSourceAdapter(BaseSourceAdapter):
    """Fetch git status and recent commits for context."""

    def __init__(
        self,
        include_status: bool = True,
        include_shortlog: bool = True,
        shortlog_limit: int = 5,
        offline: bool = True,
    ):
        super().__init__(source_name="git", priority=10, offline=offline)
        self._include_status = include_status
        self._include_shortlog = include_shortlog
        self._shortlog_limit = max(1, int(shortlog_limit))

    def _run_git(self, args: list[str], root: Path) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return None
            return result.stdout.strip()
        except Exception:
            return None

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> Dict[str, Any]:
            root = Path(__file__).resolve().parents[4]
            status = None
            shortlog = None
            if self._include_status:
                status = self._run_git(["status", "-sb"], root)
            if self._include_shortlog:
                shortlog = self._run_git(["log", "-n", str(self._shortlog_limit), "--oneline"], root)
            return {"git": GitContext(status=status, shortlog=shortlog)}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 800
