from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tools.overseer.gate_tracker import GateTracker
from tools.overseer.handoff_manager import HandoffManager
from tools.overseer.ledger_parser import LedgerParser


class ReportEngine:
    """Generate simple status reports from ledger and gate tracker."""

    def __init__(
        self,
        ledger_parser: LedgerParser,
        gate_tracker: GateTracker,
        handoff_manager: HandoffManager | None = None,
        reports_dir: Path | None = None,
    ):
        self.ledger_parser = ledger_parser
        self.gate_tracker = gate_tracker
        self.handoff_manager = handoff_manager or HandoffManager(ledger_parser=ledger_parser)
        self.reports_dir = reports_dir or Path("docs/reports/verification")

    def generate_comprehensive_report(self, save: bool = True) -> Path | None:
        summary = self._build_report_lines()
        if not save:
            return None
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.reports_dir / f"OVERSEER_STATUS_{stamp}.md"
        path.write_text("\n".join(summary), encoding="utf-8")
        return path

    def generate_gate_report(self) -> list[str]:
        statuses = self.gate_tracker.compute_statuses(force=True)
        lines = ["## Gate Status", ""]
        for status in statuses:
            lines.append(f"- {status.status_symbol} Gate {status.gate.value}: {status.done_entries}/{status.total_entries}")
        return lines

    def _build_report_lines(self) -> list[str]:
        summary = self.ledger_parser.get_summary()
        statuses = self.gate_tracker.compute_statuses(force=True)
        matched, missing, orphan = self.handoff_manager.reconcile_with_ledger()
        lines = [
            "# Overseer Comprehensive Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Ledger Summary",
            "",
            f"- Total entries: {summary.total_entries}",
            f"- Done entries: {summary.done_entries}",
            f"- Open entries: {summary.open_entries}",
            f"- In progress entries: {summary.in_progress_entries}",
            f"- Blocked entries: {summary.blocked_entries}",
            f"- Completion: {summary.completion_percent:.1f}%",
            "",
            "## Gate Status",
            "",
        ]
        for status in statuses:
            lines.append(f"- {status.status_symbol} Gate {status.gate.value}: {status.done_entries}/{status.total_entries}")
        lines += [
            "",
            "## Handoff Reconciliation",
            "",
            f"- Matched: {len(matched)}",
            f"- Missing: {len(missing)}",
            f"- Orphan: {len(orphan)}",
        ]
        if missing:
            lines.append("")
            lines.append("Missing handoffs:")
            lines.extend([f"- {mid}" for mid in missing[:20]])
        if orphan:
            lines.append("")
            lines.append("Orphan handoffs:")
            lines.extend([f"- {oid}" for oid in orphan[:20]])
        return lines
