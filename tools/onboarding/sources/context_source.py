from __future__ import annotations

from typing import List

from tools.onboarding.core.models import Blocker, RoleConfig, RoleContext
from tools.overseer.ledger_parser import LedgerParser


class RoleContextSource:
    """Load blockers relevant to a role based on gate ownership."""

    def __init__(self, blockers_limit: int = 8):
        self._limit = max(1, int(blockers_limit))

    def load(self, role: RoleConfig, active_task=None) -> RoleContext:
        if not role.primary_gates:
            return RoleContext(blockers=[])
        parser = LedgerParser()
        entries = parser.parse()
        blockers: List[Blocker] = []
        for entry in entries:
            if entry.state.value != "BLOCKED":
                continue
            if entry.gate.value not in role.primary_gates:
                continue
            blockers.append(
                Blocker(
                    id=entry.id,
                    severity=entry.severity.value,
                    gate=entry.gate.value,
                    title=entry.title,
                    owner_role=entry.owner_role,
                )
            )
            if len(blockers) >= self._limit:
                break
        return RoleContext(blockers=blockers)
