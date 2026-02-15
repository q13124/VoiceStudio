from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tools.context.core.models import AllocationContext, BriefContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter

DEFAULT_TASKS_DIR = "docs/tasks"
STATE_PATH = Path(".cursor/STATE.md")


def _extract_section(text: str, header: str) -> str | None:
    pattern = re.compile(rf"^\s*##\s+{re.escape(header)}\s*$", re.IGNORECASE)
    lines = text.splitlines()
    out = []
    in_section = False
    for line in lines:
        if pattern.match(line):
            in_section = True
            continue
        if in_section and line.strip().startswith("## "):
            break
        if in_section:
            out.append(line)
    content = "\n".join([l.rstrip() for l in out]).strip()
    return content or None


def _parse_active_task_id(state_text: str) -> str | None:
    in_active = False
    for line in state_text.splitlines():
        if line.strip().startswith("## Active Task"):
            in_active = True
            continue
        if in_active and line.strip().startswith("## "):
            break
        if in_active and "**ID**" in line:
            match = re.search(r"\*\*ID\*\*:\s*(.*)", line)
            if match:
                return match.group(1).strip()
    return None


class TaskSourceAdapter(BaseSourceAdapter):
    """Load task brief context from docs/tasks/."""

    def __init__(self, tasks_dir: str = DEFAULT_TASKS_DIR, offline: bool = True):
        super().__init__(source_name="brief", priority=95, offline=offline)
        self._tasks_dir = tasks_dir

    def _resolve_dir(self, root: Path) -> Path:
        p = Path(self._tasks_dir)
        if not p.is_absolute():
            p = root / p
        return p

    def _resolve_task_id(self, context: AllocationContext, root: Path) -> str | None:
        if context.task_id:
            return context.task_id
        if STATE_PATH.exists():
            try:
                text = STATE_PATH.read_text(encoding="utf-8")
            except Exception:
                return None
            return _parse_active_task_id(text)
        return None

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> dict[str, Any]:
            root = Path(__file__).resolve().parents[4]
            task_id = self._resolve_task_id(context, root)
            if not task_id:
                return {"brief": None}
            tasks_dir = self._resolve_dir(root)
            path = tasks_dir / f"{task_id}.md"
            if not path.exists():
                return {"brief": None}
            text = path.read_text(encoding="utf-8")
            brief = BriefContext(
                path=str(path),
                objective=_extract_section(text, "Objective"),
                acceptance=_extract_section(text, "Acceptance Criteria"),
                proofs=_extract_section(text, "Required Proofs"),
            )
            return {"brief": brief}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 1500
