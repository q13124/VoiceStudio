from __future__ import annotations

from pathlib import Path

from tools.onboarding.core.models import GuideContent, RoleConfig
from tools.onboarding.core.role_registry import RoleRegistry


class GuideSource:
    """Load and summarize role guides."""

    def __init__(self, registry: RoleRegistry, max_chars: int = 3200):
        self._registry = registry
        self._max_chars = max(200, int(max_chars))

    def summarize(self, role: RoleConfig, include_full: bool = False) -> GuideContent:
        if not role.guide_path:
            return GuideContent(summary="", full_text="")
        path = Path(role.guide_path)
        if not path.exists():
            return GuideContent(summary="", full_text="")
        text = path.read_text(encoding="utf-8")
        summary = self._summarize(text)
        full = text if include_full else ""
        return GuideContent(summary=summary, full_text=full)

    def _summarize(self, text: str) -> str:
        stripped = text.strip()
        if len(stripped) <= self._max_chars:
            return stripped
        return stripped[: self._max_chars].rstrip() + "..."
