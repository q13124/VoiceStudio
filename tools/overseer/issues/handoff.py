"""HandoffQueue for cross-role issue escalation with context distribution."""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tools.context.core.models import ContextBundle

logger = logging.getLogger(__name__)

DEFAULT_HANDOFF_STORE = Path("%APPDATA%/VoiceStudio/handoffs").expanduser()


@dataclass
class HandoffEntry:
    """A single handoff entry with context distribution support."""

    id: str
    issue_id: str
    from_role: str
    to_role: str
    message: str
    priority: str  # "low", "medium", "high", "urgent"
    handed_off_at: datetime
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    completed_at: datetime | None = None
    resolution: str | None = None
    severity: str = "medium"
    status: str = "pending"
    instance_type: str = "agent"
    correlation_id: str = ""
    task_id: str | None = None
    phase: str | None = None
    context_prepared: bool = False
    context_size_chars: int = 0
    auto_distributed: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "from_role": self.from_role,
            "to_role": self.to_role,
            "message": self.message,
            "priority": self.priority,
            "handed_off_at": self.handed_off_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "resolution": self.resolution,
            "severity": self.severity,
            "status": self.status,
            "instance_type": self.instance_type,
            "correlation_id": self.correlation_id,
            "task_id": self.task_id,
            "phase": self.phase,
            "context_prepared": self.context_prepared,
            "context_size_chars": self.context_size_chars,
            "auto_distributed": self.auto_distributed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> HandoffEntry:
        return cls(
            id=data["id"],
            issue_id=data["issue_id"],
            from_role=data["from_role"],
            to_role=data["to_role"],
            message=data["message"],
            priority=data["priority"],
            handed_off_at=datetime.fromisoformat(data["handed_off_at"]),
            acknowledged_at=datetime.fromisoformat(data["acknowledged_at"]) if data.get("acknowledged_at") else None,
            acknowledged_by=data.get("acknowledged_by"),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            resolution=data.get("resolution"),
            severity=data.get("severity", "medium"),
            status=data.get("status", "pending"),
            instance_type=data.get("instance_type", "agent"),
            correlation_id=data.get("correlation_id", ""),
            task_id=data.get("task_id"),
            phase=data.get("phase"),
            context_prepared=data.get("context_prepared", False),
            context_size_chars=data.get("context_size_chars", 0),
            auto_distributed=data.get("auto_distributed", False),
        )


class HandoffQueue:
    """
    Manages cross-role issue handoffs with automatic context distribution.

    Features:
    - Issue escalation and delegation between roles
    - Automatic context bundle preparation for target role
    - Notification hooks for handoff events
    - Progress tracking integration
    """

    def __init__(
        self,
        storage_dir: Path | None = None,
        auto_distribute_context: bool = True,
    ):
        if storage_dir:
            self._storage_dir = storage_dir
        else:
            import os
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            self._storage_dir = Path(appdata) / "VoiceStudio" / "handoffs"

        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self._storage_dir / "handoff_index.jsonl"
        self._auto_distribute = auto_distribute_context
        self._distributor = None
        self._notification_callbacks: list[Callable[[HandoffEntry], None]] = []

    def _get_distributor(self):
        """Lazy-load context distributor."""
        if self._distributor is None:
            try:
                from tools.context.core.distributor import ContextDistributor
                self._distributor = ContextDistributor()
            except Exception as e:
                logger.warning("Failed to load ContextDistributor: %s", e)
        return self._distributor

    def register_notification(
        self,
        callback: Callable[[HandoffEntry], None],
    ) -> None:
        """
        Register a callback for handoff notifications.

        Args:
            callback: Function called when handoff is created
        """
        self._notification_callbacks.append(callback)

    def handoff(
        self,
        issue_id: str,
        from_role: str,
        to_role: str,
        reason: str,
        priority: str = "medium",
        severity: str = "medium",
        task_id: str | None = None,
        phase: str | None = None,
        distribute_context: bool | None = None,
    ) -> HandoffEntry:
        """
        Create handoff entry for issue with automatic context distribution.

        Args:
            issue_id: Issue ID to handoff
            from_role: Source role
            to_role: Target role
            reason: Explanation for handoff
            priority: Priority level
            severity: Severity level
            task_id: Optional task ID for context
            phase: Optional phase name for context
            distribute_context: Override auto_distribute setting

        Returns:
            HandoffEntry record with context prepared if enabled
        """
        entry = HandoffEntry(
            id=f"HO-{uuid.uuid4().hex[:8]}",
            issue_id=issue_id,
            from_role=from_role,
            to_role=to_role,
            message=reason,
            priority=priority,
            handed_off_at=datetime.now(),
            severity=severity,
            status="pending",
            task_id=task_id,
            phase=phase,
        )

        # Auto-distribute context to target role if enabled
        should_distribute = (
            distribute_context if distribute_context is not None
            else self._auto_distribute
        )

        if should_distribute:
            entry = self._distribute_context_for_handoff(entry)

        self._append(entry)

        # Fire notification callbacks
        for callback in self._notification_callbacks:
            try:
                callback(entry)
            except Exception as e:
                logger.warning("Notification callback failed: %s", e)

        logger.info(
            "Handoff created: %s -> %s (issue: %s, context: %s)",
            from_role,
            to_role,
            issue_id,
            "prepared" if entry.context_prepared else "skipped",
        )

        return entry

    def _distribute_context_for_handoff(
        self,
        entry: HandoffEntry,
    ) -> HandoffEntry:
        """Prepare context bundle for target role."""
        distributor = self._get_distributor()
        if distributor is None:
            return entry

        try:
            bundle = distributor.distribute(
                role_id=entry.to_role,
                task_id=entry.task_id,
                phase=entry.phase,
                force_refresh=True,
            )

            if bundle:
                entry.context_prepared = True
                entry.context_size_chars = len(bundle.to_json())
                entry.auto_distributed = True
                logger.debug(
                    "Context prepared for handoff %s: %d chars",
                    entry.id,
                    entry.context_size_chars,
                )
        except Exception as e:
            logger.warning("Failed to distribute context for handoff: %s", e)

        return entry

    def get_context_for_handoff(
        self,
        entry_id: str,
    ) -> ContextBundle | None:
        """
        Get the prepared context bundle for a handoff.

        Args:
            entry_id: Handoff entry ID

        Returns:
            ContextBundle if available, None otherwise
        """
        entries = self._load_all()

        for entry_data in entries:
            if entry_data["id"] == entry_id:
                if not entry_data.get("context_prepared"):
                    return None

                distributor = self._get_distributor()
                if distributor is None:
                    return None

                to_role = entry_data.get("to_role")
                return distributor.get_active_distribution(to_role)

        return None

    def get_role_queue(
        self,
        role: str,
        unacknowledged_only: bool = True,
    ) -> list[dict]:
        """
        Get handoff queue for a role.

        Args:
            role: Role short name (e.g., "core-platform")
            unacknowledged_only: Only return unacknowledged entries

        Returns:
            List of handoff entries as dicts
        """
        entries = self._load_all()

        filtered = [
            e for e in entries
            if e["to_role"] == role
            and (not unacknowledged_only or e["acknowledged_at"] is None)
            and e["status"] != "completed"
        ]

        # Sort by priority then date
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        filtered.sort(
            key=lambda e: (
                priority_order.get(e["priority"], 2),
                e["handed_off_at"]
            )
        )

        return filtered

    def acknowledge(self, entry_id: str, role: str) -> bool:
        """
        Acknowledge receipt of handoff.

        Args:
            entry_id: Handoff entry ID
            role: Role acknowledging

        Returns:
            True if acknowledged, False if not found
        """
        entries = self._load_all()

        for entry in entries:
            if entry["id"] == entry_id:
                entry["acknowledged_at"] = datetime.now().isoformat()
                entry["acknowledged_by"] = role
                entry["status"] = "acknowledged"
                self._rewrite_all(entries)
                return True

        return False

    def complete(self, entry_id: str, resolution: str) -> bool:
        """
        Mark handoff as completed.

        Args:
            entry_id: Handoff entry ID
            resolution: Resolution description

        Returns:
            True if completed, False if not found
        """
        entries = self._load_all()

        for entry in entries:
            if entry["id"] == entry_id:
                entry["completed_at"] = datetime.now().isoformat()
                entry["resolution"] = resolution
                entry["status"] = "completed"
                self._rewrite_all(entries)
                return True

        return False

    def _append(self, entry: HandoffEntry) -> None:
        """Append handoff entry to index."""
        with open(self._index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def _load_all(self) -> list[dict]:
        """Load all handoff entries."""
        if not self._index_file.exists():
            return []

        entries = []
        with open(self._index_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    # GAP-PY-001: Skip malformed index entry
                    logger.debug(f"Failed to parse handoff index entry: {e}")
                    continue

        return entries

    def _rewrite_all(self, entries: list[dict]) -> None:
        """Rewrite entire index (for updates)."""
        tmp_file = self._index_file.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        import os
        os.replace(tmp_file, self._index_file)

    def get_pending_with_context(
        self,
        role: str,
    ) -> list[dict[str, Any]]:
        """
        Get pending handoffs for a role with context summary.

        Args:
            role: Target role

        Returns:
            List of handoffs with context_summary field
        """
        pending = self.get_role_queue(role, unacknowledged_only=True)

        for entry in pending:
            if entry.get("context_prepared"):
                entry["context_summary"] = {
                    "size_chars": entry.get("context_size_chars", 0),
                    "task_id": entry.get("task_id"),
                    "phase": entry.get("phase"),
                    "ready": True,
                }
            else:
                entry["context_summary"] = {"ready": False}

        return pending

    def refresh_context(self, entry_id: str) -> bool:
        """
        Refresh context for an existing handoff.

        Args:
            entry_id: Handoff entry ID

        Returns:
            True if refresh succeeded
        """
        entries = self._load_all()

        for entry_data in entries:
            if entry_data["id"] == entry_id:
                entry = HandoffEntry.from_dict(entry_data)
                entry = self._distribute_context_for_handoff(entry)

                # Update entry in list
                entry_data.update(entry.to_dict())
                self._rewrite_all(entries)
                return entry.context_prepared

        return False

    def get_statistics(self) -> dict[str, Any]:
        """Get handoff queue statistics."""
        entries = self._load_all()

        pending = [e for e in entries if e.get("status") == "pending"]
        acknowledged = [e for e in entries if e.get("status") == "acknowledged"]
        completed = [e for e in entries if e.get("status") == "completed"]

        # Group by role
        by_role: dict[str, int] = {}
        for e in pending:
            role = e.get("to_role", "unknown")
            by_role[role] = by_role.get(role, 0) + 1

        # Context stats
        with_context = sum(1 for e in entries if e.get("context_prepared"))

        return {
            "total": len(entries),
            "pending": len(pending),
            "acknowledged": len(acknowledged),
            "completed": len(completed),
            "pending_by_role": by_role,
            "with_context": with_context,
            "context_rate": with_context / max(1, len(entries)),
        }


# Global handoff queue instance
_global_queue: HandoffQueue | None = None


def get_handoff_queue() -> HandoffQueue:
    """Get or create global handoff queue."""
    global _global_queue
    if _global_queue is None:
        _global_queue = HandoffQueue()
    return _global_queue


def create_handoff(
    issue_id: str,
    from_role: str,
    to_role: str,
    reason: str,
    priority: str = "medium",
    task_id: str | None = None,
) -> HandoffEntry:
    """Convenience function to create a handoff."""
    return get_handoff_queue().handoff(
        issue_id=issue_id,
        from_role=from_role,
        to_role=to_role,
        reason=reason,
        priority=priority,
        task_id=task_id,
    )
