"""
Audit Source Adapter for Context Manager.

Injects recent audit log entries into agent context for enhanced
debugging and traceability capabilities.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter


class AuditSourceAdapter(BaseSourceAdapter):
    """
    Fetch recent audit entries for context injection.
    
    Reads audit logs from the .audit/ directory and provides
    filtered entries based on severity and time window.
    """
    
    def __init__(
        self,
        max_entries: int = 20,
        severity_filter: Optional[List[str]] = None,
        hours_lookback: int = 24,
        audit_dir: Optional[Path] = None,
        offline: bool = True,
    ):
        """
        Initialize the AuditSourceAdapter.
        
        Args:
            max_entries: Maximum number of audit entries to include
            severity_filter: List of severity levels to include (default: error, warning)
            hours_lookback: Hours to look back for entries
            audit_dir: Path to audit directory (default: .audit/)
            offline: Whether this is an offline source
        """
        super().__init__(source_name="audit", priority=35, offline=offline)
        self._max_entries = max(1, int(max_entries))
        self._severity_filter = severity_filter or ["error", "warning", "critical"]
        self._hours_lookback = max(1, int(hours_lookback))
        self._audit_dir = audit_dir or Path(".audit")
    
    def fetch(self, context: AllocationContext) -> SourceResult:
        """Fetch recent audit entries for context."""
        
        def _load() -> Dict[str, Any]:
            entries = self._get_recent_entries()
            
            # Group by subsystem for better context organization
            by_subsystem: Dict[str, List[Dict]] = {}
            for entry in entries:
                subsystem = entry.get("subsystem") or "unknown"
                if subsystem not in by_subsystem:
                    by_subsystem[subsystem] = []
                by_subsystem[subsystem].append(self._format_entry(entry))
            
            # Build summary statistics
            stats = {
                "total_entries": len(entries),
                "by_severity": self._count_by_field(entries, "severity"),
                "by_event_type": self._count_by_field(entries, "event_type"),
            }
            
            return {
                "audit_entries": [self._format_entry(e) for e in entries[:self._max_entries]],
                "by_subsystem": by_subsystem,
                "stats": stats,
                "lookback_hours": self._hours_lookback,
            }
        
        return self._measure(_load, context)
    
    def _get_recent_entries(self) -> List[Dict[str, Any]]:
        """Load recent audit entries from log files."""
        entries = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._hours_lookback)
        
        # Read today's log and potentially yesterday's
        for days_ago in range(2):  # Today and yesterday
            log_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            log_path = self._audit_dir / f"log-{log_date}.jsonl"
            
            if not log_path.exists():
                continue
            
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            entry = json.loads(line)
                            
                            # Check timestamp
                            timestamp_str = entry.get("timestamp", "")
                            if timestamp_str:
                                try:
                                    ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                                    if ts.tzinfo is None:
                                        ts = ts.replace(tzinfo=timezone.utc)
                                    if ts < cutoff:
                                        continue
                                # Best effort - failure is acceptable here
                                except (ValueError, TypeError):
                                    pass
                            
                            # Check severity filter
                            severity = (entry.get("severity") or "").lower()
                            if severity and severity not in self._severity_filter:
                                continue
                            
                            entries.append(entry)
                            
                        except json.JSONDecodeError:
                            continue
                            
            except (IOError, OSError):
                continue
        
        # Sort by timestamp descending (most recent first)
        entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        
        return entries[:self._max_entries]
    
    def _format_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Format an entry for context output."""
        return {
            "id": entry.get("entry_id", ""),
            "type": entry.get("event_type", ""),
            "severity": entry.get("severity", ""),
            "time": self._format_timestamp(entry.get("timestamp", "")),
            "subsystem": entry.get("subsystem", ""),
            "summary": entry.get("summary", ""),
            "file": entry.get("file_path", ""),
            "task": entry.get("task_id", ""),
            "error_code": entry.get("error_code", ""),
            "message": self._truncate(entry.get("message", ""), 200),
        }
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display."""
        if not timestamp:
            return ""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return timestamp[:16] if len(timestamp) > 16 else timestamp
    
    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text to max length."""
        if not text or len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."
    
    def _count_by_field(self, entries: List[Dict], field: str) -> Dict[str, int]:
        """Count entries by a field value."""
        counts: Dict[str, int] = {}
        for entry in entries:
            value = entry.get(field) or "unknown"
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate the size of audit context in characters."""
        # Rough estimate: ~150 chars per entry
        return min(self._max_entries * 150, 3000)
