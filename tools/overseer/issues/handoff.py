"""HandoffQueue for cross-role issue escalation."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_HANDOFF_STORE = Path("%APPDATA%/VoiceStudio/handoffs").expanduser()


@dataclass
class HandoffEntry:
    """A single handoff entry."""
    
    id: str
    issue_id: str
    from_role: str
    to_role: str
    message: str
    priority: str  # "low", "medium", "high", "urgent"
    handed_off_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    resolution: Optional[str] = None
    severity: str = "medium"
    status: str = "pending"
    instance_type: str = "agent"
    correlation_id: str = ""
    
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
        )


class HandoffQueue:
    """
    Manages cross-role issue handoffs.
    
    Enables issue escalation and delegation between roles.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir:
            self._storage_dir = storage_dir
        else:
            import os
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            self._storage_dir = Path(appdata) / "VoiceStudio" / "handoffs"
        
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self._storage_dir / "handoff_index.jsonl"
    
    def handoff(
        self,
        issue_id: str,
        from_role: str,
        to_role: str,
        reason: str,
        priority: str = "medium",
        severity: str = "medium",
    ) -> HandoffEntry:
        """
        Create handoff entry for issue.
        
        Args:
            issue_id: Issue ID to handoff
            from_role: Source role
            to_role: Target role
            reason: Explanation for handoff
            priority: Priority level
            severity: Severity level
        
        Returns:
            HandoffEntry record
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
        )
        
        self._append(entry)
        return entry
    
    def get_role_queue(
        self,
        role: str,
        unacknowledged_only: bool = True,
    ) -> List[Dict]:
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
    
    def _load_all(self) -> List[Dict]:
        """Load all handoff entries."""
        if not self._index_file.exists():
            return []
        
        entries = []
        with open(self._index_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return entries
    
    def _rewrite_all(self, entries: List[Dict]) -> None:
        """Rewrite entire index (for updates)."""
        tmp_file = self._index_file.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        import os
        os.replace(tmp_file, self._index_file)
