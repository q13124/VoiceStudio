from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from tools.onboarding.core.models import RoleConfig


DEFAULT_ROLES_CONFIG = Path("tools/onboarding/config/roles.json")
PROMPT_DIR = Path(".cursor/prompts")
GUIDE_DIR = Path("docs/governance/roles")


_ACRONYMS = {"UI", "AI", "GPU", "CPU", "API", "SLO", "XTTS"}


def _title_case(token: str) -> str:
    if token.upper() in _ACRONYMS:
        return token.upper()
    return token.title()


def _format_role_name(raw: str) -> str:
    words = raw.split("_")
    return " ".join(_title_case(w) for w in words if w)


def _default_prompt_path(role_id: str, stem: str) -> Optional[str]:
    candidate = PROMPT_DIR / f"ROLE_{role_id}_{stem}_PROMPT.md"
    if candidate.exists():
        return str(candidate)
    return None


def _default_guide_path(role_id: str, stem: str) -> Optional[str]:
    candidate = GUIDE_DIR / f"ROLE_{role_id}_{stem}_GUIDE.md"
    if candidate.exists():
        return str(candidate)
    return None


class RoleRegistry:
    """Registry for onboarding roles and prompt/guide paths."""

    def __init__(self, roles: List[RoleConfig]):
        self._roles = roles
        self._by_id = {r.id: r for r in roles}
        self._by_short = {r.short_name: r for r in roles}

    @classmethod
    def from_config(cls, config_path: Path = DEFAULT_ROLES_CONFIG) -> "RoleRegistry":
        root = Path(__file__).resolve().parents[3]
        path = config_path if config_path.is_absolute() else root / config_path
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            roles = []
            roles_data = data.get("roles", {})
            # Handle both dict format {"0": {...}} and list format [{...}]
            if isinstance(roles_data, dict):
                for role_id, entry in roles_data.items():
                    if not isinstance(entry, dict):
                        continue
                    roles.append(
                        RoleConfig(
                            id=str(role_id),
                            short_name=entry.get("name", "").strip(),
                            name=entry.get("display_name", entry.get("name", "")).strip(),
                            prompt_path=entry.get("prompt", entry.get("prompt_path", "")).strip(),
                            guide_path=entry.get("guide", entry.get("guide_path")),
                            primary_gates=list(entry.get("gates", entry.get("primary_gates", []))),
                        )
                    )
            else:
                # Legacy list format
                for entry in roles_data:
                    if not isinstance(entry, dict):
                        continue
                    roles.append(
                        RoleConfig(
                            id=str(entry.get("id")),
                            short_name=entry.get("short_name", "").strip(),
                            name=entry.get("name", "").strip(),
                            prompt_path=entry.get("prompt_path", "").strip(),
                            guide_path=entry.get("guide_path"),
                            primary_gates=list(entry.get("primary_gates", [])),
                        )
                    )
            return cls(roles)
        return cls(cls._scan_roles(root))

    @classmethod
    def _scan_roles(cls, root: Path) -> List[RoleConfig]:
        roles: List[RoleConfig] = []
        prompt_dir = root / PROMPT_DIR
        if not prompt_dir.exists():
            return roles
        for prompt in sorted(prompt_dir.glob("ROLE_*_PROMPT.md")):
            match = re.match(r"ROLE_(\d+)_([A-Z0-9_]+)_PROMPT\.md", prompt.name)
            if not match:
                continue
            role_id, stem = match.group(1), match.group(2)
            name = _format_role_name(stem)
            short_name = stem.lower().replace("_", "-")
            guide_path = _default_guide_path(role_id, stem)
            roles.append(
                RoleConfig(
                    id=role_id,
                    short_name=short_name,
                    name=name,
                    prompt_path=str(prompt),
                    guide_path=guide_path,
                    primary_gates=cls._parse_primary_gates(prompt),
                )
            )
        return roles

    @classmethod
    def _parse_primary_gates(cls, prompt_path: Path) -> List[str]:
        try:
            text = prompt_path.read_text(encoding="utf-8")
        except Exception:
            return []
        match = re.search(r"Primary Gates:\s*(.*)", text, flags=re.IGNORECASE)
        if not match:
            return []
        raw = match.group(1)
        gates = [g.strip().upper() for g in re.split(r"[,\s]+", raw) if g.strip()]
        return [g for g in gates if g]

    def list_roles(self) -> List[RoleConfig]:
        return list(self._roles)

    def resolve_role_id(self, role_id: str | int) -> str:
        candidate = str(role_id).strip()
        if candidate in self._by_id:
            return candidate
        if candidate in self._by_short:
            return self._by_short[candidate].id
        for role in self._roles:
            if role.name.lower() == candidate.lower():
                return role.id
        raise ValueError(f"Unknown role id: {role_id}")

    def get_role(self, role_id: str | int) -> RoleConfig:
        resolved = self.resolve_role_id(role_id)
        return self._by_id[resolved]
