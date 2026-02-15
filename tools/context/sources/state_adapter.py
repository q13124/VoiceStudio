from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tools.context.core.models import AllocationContext, SourceResult, StateContext, TaskContext
from tools.context.sources.base import BaseSourceAdapter

STATE_PATH = Path(".cursor/STATE.md")


def _parse_proof_index(text: str) -> list[dict[str, Any]]:
    """Parse Proof Index table from STATE.md into list of dicts (Date, Task, Artifact, Type, Verified)."""
    out: list[dict[str, Any]] = []
    in_section = False
    for line in text.splitlines():
        if re.search(r"^\s*##\s+Proof\s+Index", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("## "):
                break
            if not line.strip().startswith("|") or "---" in line:
                if "---" in line:
                    continue
                continue
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 5:
                if parts[0].lower() == "date" and parts[1].lower() == "task":
                    continue
                out.append({
                    "date": parts[0],
                    "task": parts[1],
                    "artifact": parts[2],
                    "type": parts[3],
                    "verified": parts[4],
                })
    return out


def _extract_list(lines: list[str], header: str) -> list:
    items = []
    in_section = False
    for line in lines:
        if line.strip().startswith("##") and header.lower() in line.lower():
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            if line.strip().startswith(("-", "*")):
                items.append(line.strip("-* ").strip())
    return items


class StateSourceAdapter(BaseSourceAdapter):
    def __init__(self, path: Path = STATE_PATH):
        super().__init__(source_name="state", priority=100, offline=True)
        self.path = path

    def health_check(self) -> bool:
        """
        Check if STATE.md exists and is readable.

        Returns:
            True if STATE.md exists and can be parsed
        """
        try:
            if not self.path.exists():
                return True  # Missing file is OK (will use defaults)
            # Try to read and parse
            text = self.path.read_text(encoding="utf-8")
            return len(text) > 0
        except Exception:
            return False

    def _read_state(self) -> StateContext:
        if not self.path.exists():
            return StateContext()
        text = self.path.read_text(encoding="utf-8")
        lines = text.splitlines()
        phase = re.search(r"\*\*Phase\*\*:\s*(.*)", text)
        started = re.search(r"\*\*Started\*\*:\s*(.*)", text)
        context_line = re.search(r"\*\*Context\*\*:\s*(.*)", text)
        next_steps = _extract_list(lines, "Next 3 Steps")
        return StateContext(
            phase=phase.group(1).strip() if phase else None,
            started=started.group(1).strip() if started else None,
            context=context_line.group(1).strip() if context_line else None,
            next_steps=next_steps,
        )

    def _read_task(self) -> TaskContext:
        if not self.path.exists():
            return TaskContext()
        text = self.path.read_text(encoding="utf-8")
        tid = re.search(r"\*\*ID\*\*:\s*(.*)", text)
        title = re.search(r"\*\*Title\*\*:\s*(.*)", text)
        priority = re.search(r"\*\*Priority\*\*:\s*(.*)", text)
        blockers = re.search(r"\*\*Blockers\*\*:\s*(.*)", text)
        return TaskContext(
            id=tid.group(1).strip() if tid else None,
            title=title.group(1).strip() if title else None,
            priority=priority.group(1).strip() if priority else None,
            blockers=blockers.group(1).strip() if blockers else None,
        )

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load():
            text = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
            return {
                "state": self._read_state(),
                "task": self._read_task(),
                "proof_index": _parse_proof_index(text) if text else [],
            }

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 1024
