"""
Conversation adapter – sliding-window short-term memory from recent interactions.

Reads .cursor/.conversation_history.jsonl; when turn count exceeds threshold,
summarizes older turns and injects summary + recent N turns into context as memory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from tools.context.core.models import AllocationContext, MemoryItem, SourceResult
from tools.context.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

DEFAULT_HISTORY_PATH = ".cursor/.conversation_history.jsonl"
DEFAULT_MAX_TURNS = 10
DEFAULT_RECENT_TURNS = 5
SUMMARY_TRUNCATE = 80


def _truncate(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    return s[: max(0, limit - 3)] + "..."


class ConversationSourceAdapter(BaseSourceAdapter):
    """
    Fetch short-term context from recent conversation history.

    Reads a JSONL file (one JSON object per line: role, content, timestamp).
    When turns > recent_turns, older turns are summarized (truncated join);
    summary + last recent_turns are returned as memory items.
    """

    def __init__(
        self,
        history_path: str = DEFAULT_HISTORY_PATH,
        max_turns: int = DEFAULT_MAX_TURNS,
        recent_turns: int = DEFAULT_RECENT_TURNS,
        offline: bool = True,
    ):
        super().__init__(source_name="memory", priority=52, offline=offline)
        self._history_path = history_path
        self._max_turns = max_turns
        self._recent_turns = recent_turns

    def _resolve_path(self, root: Path) -> Path:
        p = Path(self._history_path)
        if not p.is_absolute():
            p = root / p
        return p

    def _load_turns(self, path: Path) -> list[dict[str, Any]]:
        """Load last max_turns lines from JSONL; each line is {role, content, timestamp}."""
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8").strip().split("\n")
            turns = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    turns.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return turns[-self._max_turns :] if len(turns) > self._max_turns else turns
        except Exception as e:
            logger.debug("Conversation history read failed: %s", e)
            return []

    def _summarize_turns(self, turns: list[dict[str, Any]]) -> str:
        """Condense older turns into one short summary (no LLM)."""
        parts = []
        for t in turns:
            content = (t.get("content") or "").strip()
            role = t.get("role", "user")
            if content:
                parts.append(f"{role}: {_truncate(content, SUMMARY_TRUNCATE)}")
        return "Earlier: " + " | ".join(parts) if parts else ""

    def _format_recent(self, turns: list[dict[str, Any]]) -> str:
        """Format recent turns for context."""
        lines = []
        for t in turns:
            content = (t.get("content") or "").strip()
            role = t.get("role", "user")
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def fetch(self, context: AllocationContext) -> SourceResult:
        """Load conversation history, summarize if needed, return as memory items."""

        def _load() -> dict[str, Any]:
            root = Path(__file__).resolve().parents[4]
            path = self._resolve_path(root)
            turns = self._load_turns(path)
            if not turns:
                return {"memory": []}
            if len(turns) <= self._recent_turns:
                text = self._format_recent(turns)
                return {"memory": [MemoryItem(content=text, source="conversation")]}
            older = turns[: -self._recent_turns]
            recent = turns[-self._recent_turns :]
            summary = self._summarize_turns(older)
            recent_text = self._format_recent(recent)
            items = [
                MemoryItem(content=summary, source="conversation"),
                MemoryItem(content=recent_text, source="conversation"),
            ]
            return {"memory": items}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return self._max_turns * 200


def append_turn(project_root: Path, role: str, content: str) -> None:
    """Append one turn to conversation history (e.g. from inject_context hook)."""
    # Use removeprefix instead of lstrip to avoid stripping too many characters
    # lstrip("./") on ".cursor" incorrectly becomes "cursor"
    history_path = DEFAULT_HISTORY_PATH
    if history_path.startswith("./"):
        history_path = history_path[2:]
    path = project_root / history_path
    path.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    line = json.dumps({"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()}, ensure_ascii=False) + "\n"
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.debug("Conversation append failed: %s", e)
