from __future__ import annotations

from typing import List

from tools.overseer.ledger_parser import LedgerParser
from tools.overseer.models import Gate, GateStatus, LedgerEntry, LedgerState


class GateTracker:
    """Compute gate status from ledger entries."""

    def __init__(self, ledger_parser: LedgerParser):
        self.parser = ledger_parser
        self._statuses: List[GateStatus] = []

    def compute_statuses(self, force: bool = False) -> List[GateStatus]:
        entries = self.parser.parse(force=force)
        statuses: List[GateStatus] = []
        for gate in Gate:
            gate_entries = [e for e in entries if e.gate == gate]
            status = GateStatus(gate=gate, entries=gate_entries)
            status.total_entries = len(gate_entries)
            status.done_entries = sum(1 for e in gate_entries if self._is_done(e))
            status.blocked_entries = sum(1 for e in gate_entries if e.state == LedgerState.BLOCKED)
            status.in_progress_entries = sum(1 for e in gate_entries if e.state in {LedgerState.IN_PROGRESS, LedgerState.FIXED_PENDING_PROOF, LedgerState.TRIAGE})
            status.open_entries = sum(1 for e in gate_entries if e.state == LedgerState.OPEN)
            statuses.append(status)
        self._statuses = statuses
        return statuses

    def get_all_statuses(self) -> List[GateStatus]:
        if not self._statuses:
            return self.compute_statuses(force=False)
        return list(self._statuses)

    def get_current_gate(self) -> Gate:
        for status in self.get_all_statuses():
            if status.total_entries > 0 and not status.is_green:
                return status.gate
        return Gate.H

    def get_blockers(self) -> List[LedgerEntry]:
        return [e for e in self.parser.parse() if e.state == LedgerState.BLOCKED]

    def get_next_actions(self) -> List[str]:
        actions: List[str] = []
        for status in self.get_all_statuses():
            if status.total_entries == 0:
                continue
            if status.is_green:
                continue
            if status.blocked_entries > 0:
                actions.append(f"Gate {status.gate.value}: resolve {status.blocked_entries} blockers")
            elif status.open_entries > 0 or status.in_progress_entries > 0:
                actions.append(f"Gate {status.gate.value}: {status.done_entries}/{status.total_entries} done")
        return actions

    def _is_done(self, entry: LedgerEntry) -> bool:
        return entry.state in {LedgerState.DONE, LedgerState.WONT_FIX}
