"""
Notes adapter – structured agent note-taking (persistent notes per role).

Reads .cursor/agent_notes/{role}_notes.md for the current allocation role;
injects content as memory so agents can refer to their own prior decisions and patterns.
Agents are instructed via prompts to update their notes file with key decisions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.context.core.models import AllocationContext, MemoryItem, SourceResult
from tools.context.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

DEFAULT_NOTES_DIR = ".cursor/agent_notes"
NOTES_SUFFIX = "_notes.md"


def _role_to_filename(role: Optional[str]) -> Optional[str]:
    """Map role short_name to notes filename stem (e.g. overseer -> overseer_notes.md)."""
    if not role or not role.strip():
        return None
    stem = role.strip().lower().replace(" ", "-")
    return f"{stem}{NOTES_SUFFIX}"


class NotesSourceAdapter(BaseSourceAdapter):
    """
    Load role-specific agent notes from .cursor/agent_notes/.

    When context.role is set, reads {role}_notes.md and injects as memory.
    Agents can be instructed to update this file with key decisions and patterns.
    """

    def __init__(
        self,
        notes_dir: str = DEFAULT_NOTES_DIR,
        offline: bool = True,
    ):
        super().__init__(source_name="memory", priority=54, offline=offline)
        self._notes_dir = notes_dir

    def _resolve_dir(self, root: Path) -> Path:
        p = Path(self._notes_dir)
        if not p.is_absolute():
            p = root / p
        return p

    def _load_notes_for_role(self, root: Path, role: str) -> Optional[str]:
        """Load notes file content for role; returns None if missing or error."""
        dir_path = self._resolve_dir(root)
        name = _role_to_filename(role)
        if not name:
            return None
        path = dir_path / name
        if not path.exists():
            return None
        try:
            return path.read_text(encoding="utf-8").strip()
        except Exception as e:
            logger.debug("Notes read failed for %s: %s", path, e)
            return None

    def fetch(self, context: AllocationContext) -> SourceResult:
        """Load notes for context.role and return as memory item."""

        def _load() -> Dict[str, Any]:
            root = Path(__file__).resolve().parents[4]
            if not context.role:
                return {"memory": []}
            content = self._load_notes_for_role(root, context.role)
            if not content:
                return {"memory": []}
            return {"memory": [MemoryItem(content=content, source=f"agent_notes:{context.role}")]}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 1024 if context.role else 0
