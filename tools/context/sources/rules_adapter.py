from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.context.core.models import AllocationContext, RuleContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter


DEFAULT_RULES_DIR = ".cursor/rules"


def _parse_frontmatter(text: str) -> Dict[str, str]:
    if not text.lstrip().startswith("---"):
        return {}
    lines = text.splitlines()
    if len(lines) < 3:
        return {}
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}
    data: Dict[str, str] = {}
    for line in lines[1:end_idx]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


class RulesSourceAdapter(BaseSourceAdapter):
    """Load Cursor rule metadata for context injection."""

    def __init__(
        self,
        rules_dir: str = DEFAULT_RULES_DIR,
        include_always_apply_only: bool = False,
        max_rules: Optional[int] = None,
        offline: bool = True,
    ):
        super().__init__(source_name="rules", priority=90, offline=offline)
        self._rules_dir = rules_dir
        self._include_always_apply_only = include_always_apply_only
        self._max_rules = max_rules

    def _resolve_dir(self, root: Path) -> Path:
        p = Path(self._rules_dir)
        if not p.is_absolute():
            p = root / p
        return p

    def _read_rule(self, path: Path) -> Optional[RuleContext]:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return None
        meta = _parse_frontmatter(text)
        always_apply = meta.get("alwaysApply", "false").lower() == "true"
        if self._include_always_apply_only and not always_apply:
            return None
        desc = meta.get("description")
        rel = str(path)
        return RuleContext(path=rel, description=desc, always_apply=always_apply)

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> Dict[str, Any]:
            root = Path(__file__).resolve().parents[4]
            rules_dir = self._resolve_dir(root)
            if not rules_dir.exists():
                return {"rules": []}
            rules: List[RuleContext] = []
            for path in sorted(rules_dir.rglob("*.mdc")):
                rule = self._read_rule(path)
                if rule:
                    rules.append(rule)
                if self._max_rules and len(rules) >= self._max_rules:
                    break
            return {"rules": rules}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 1500
