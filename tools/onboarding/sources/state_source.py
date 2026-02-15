from __future__ import annotations

import re
from pathlib import Path

from tools.onboarding.core.models import ActiveTask, ProjectState
from tools.overseer.gate_tracker import GateTracker
from tools.overseer.ledger_parser import LedgerParser

STATE_PATH = Path(".cursor/STATE.md")


class StateSource:
    """Load project state and active task from STATE.md."""

    def load(self) -> tuple[ProjectState, ActiveTask | None]:
        if not STATE_PATH.exists():
            return ProjectState(), None
        text = STATE_PATH.read_text(encoding="utf-8")
        phase = self._extract_value(text, "Phase")
        task_id = self._extract_value(text, "ID")
        task_title = self._extract_value(text, "Title")
        task_priority = self._extract_value(text, "Priority")
        task_blockers = self._extract_value(text, "Blockers")

        active_gate = None
        try:
            parser = LedgerParser()
            tracker = GateTracker(parser)
            active_gate = tracker.get_current_gate().value
        except Exception:
            active_gate = None

        state = ProjectState(
            phase=phase,
            active_gate=active_gate,
            active_task_id=task_id,
            active_task_title=task_title,
        )

        if task_id or task_title:
            return state, ActiveTask(
                id=task_id,
                title=task_title,
                priority=task_priority,
                blockers=task_blockers,
            )
        return state, None

    def _extract_value(self, text: str, label: str) -> str | None:
        match = re.search(rf"\*\*{re.escape(label)}\*\*:\s*(.*)", text)
        if match:
            return match.group(1).strip()
        return None
