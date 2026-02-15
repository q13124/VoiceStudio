from __future__ import annotations

from pathlib import Path

from tools.overseer.ledger_parser import LedgerParser

DEFAULT_HANDOFF_DIR = Path("docs/governance/overseer/handoffs")


class HandoffManager:
    """Manage handoff files and reconcile with ledger entries."""

    def __init__(self, handoff_dir: Path | None = None, ledger_parser: LedgerParser | None = None):
        self.handoff_dir = handoff_dir or DEFAULT_HANDOFF_DIR
        self.ledger_parser = ledger_parser or LedgerParser()

    def list_handoffs(self) -> list[Path]:
        if not self.handoff_dir.exists():
            return []
        return sorted(self.handoff_dir.glob("*.md"))

    def load_handoff(self, name: str) -> str:
        path = self._resolve_handoff_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Handoff not found: {name}")
        return path.read_text(encoding="utf-8")

    def reconcile_with_ledger(self) -> tuple[list[str], list[str], list[str]]:
        entries = self.ledger_parser.parse()
        ledger_ids = {e.id for e in entries}
        handoff_ids = self._collect_handoff_ids()
        matched = sorted(ledger_ids & handoff_ids)
        missing = sorted(ledger_ids - handoff_ids)
        orphan = sorted(handoff_ids - ledger_ids)
        return matched, missing, orphan

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.handoff_dir.exists():
            errors.append(f"Handoff directory not found: {self.handoff_dir}")
            return errors
        for path in self.list_handoffs():
            if path.stat().st_size == 0:
                errors.append(f"Empty handoff file: {path.name}")
        return errors

    def _collect_handoff_ids(self) -> set[str]:
        ids: set[str] = set()
        for path in self.list_handoffs():
            stem = path.stem
            if stem.startswith("VS-"):
                ids.add(stem.split("_")[0])
        return ids

    def _resolve_handoff_path(self, name: str) -> Path:
        if name.endswith(".md"):
            path = self.handoff_dir / name
        elif name.startswith("VS-"):
            path = self.handoff_dir / f"{name}.md"
        else:
            path = self.handoff_dir / f"{name}.md"
        return path
