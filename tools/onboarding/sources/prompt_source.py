from __future__ import annotations

import re
from pathlib import Path

from tools.onboarding.core.models import PromptContent, RoleConfig
from tools.onboarding.core.role_registry import RoleRegistry


class PromptSource:
    """Load and parse role prompts."""

    def __init__(
        self,
        registry: RoleRegistry,
        max_identity_chars: int = 1800,
        max_summary_chars: int = 1200,
    ):
        self._registry = registry
        self._max_identity_chars = max(200, int(max_identity_chars))
        self._max_summary_chars = max(200, int(max_summary_chars))

    def load(self, role: RoleConfig) -> PromptContent:
        path = Path(role.prompt_path)
        if not path.exists():
            return PromptContent(identity_section="", next_actions="", full_text="")
        text = path.read_text(encoding="utf-8")
        identity = self._extract_section(text, "ROLE IDENTITY")
        next_actions = self._extract_section(text, "NEXT ACTIONS") or self._extract_section(text, "NEXT STEPS")
        identity = (identity or "").strip()[: self._max_identity_chars]
        next_actions = (next_actions or "").strip()[: self._max_summary_chars]
        return PromptContent(identity_section=identity, next_actions=next_actions, full_text=text)

    def _extract_section(self, text: str, header: str) -> str:
        pattern = re.compile(rf"^\s*##\s+.*{re.escape(header)}.*$", re.IGNORECASE)
        lines = text.splitlines()
        in_section = False
        out = []
        for line in lines:
            if pattern.match(line):
                in_section = True
                continue
            if in_section and line.strip().startswith("## "):
                break
            if in_section:
                out.append(line)
        return "\n".join(out).strip()
