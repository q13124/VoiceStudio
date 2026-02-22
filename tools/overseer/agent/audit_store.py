"""
Audit Store

Append-only local storage for audit entries with efficient querying.
"""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class AuditEntry:
    """
    A single audit log entry.

    Attributes:
        timestamp: When the action occurred
        agent_id: ID of the agent performing the action
        user_id: ID of the user
        correlation_id: Cross-layer tracing ID
        tool_name: Name of the tool invoked
        parameters: Tool parameters (secrets redacted)
        result: success/failure/denied
        error_stack: Error traceback if failed
        input_hash: Hash of inputs for large payloads
        output_hash: Hash of outputs for large payloads
        approval_id: ID of approval record if action required approval
        duration_ms: Execution duration in milliseconds
        risk_tier: Risk tier of the action
        session_id: Session identifier
    """

    timestamp: datetime
    agent_id: str
    user_id: str
    correlation_id: str
    tool_name: str
    parameters: dict = field(default_factory=dict)
    result: str = "success"
    error_stack: str | None = None
    input_hash: str | None = None
    output_hash: str | None = None
    approval_id: str | None = None
    duration_ms: int = 0
    risk_tier: str = "low"
    session_id: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "result": self.result,
            "error_stack": self.error_stack,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "approval_id": self.approval_id,
            "duration_ms": self.duration_ms,
            "risk_tier": self.risk_tier,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AuditEntry:
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_id=data["agent_id"],
            user_id=data["user_id"],
            correlation_id=data["correlation_id"],
            tool_name=data["tool_name"],
            parameters=data.get("parameters", {}),
            result=data.get("result", "success"),
            error_stack=data.get("error_stack"),
            input_hash=data.get("input_hash"),
            output_hash=data.get("output_hash"),
            approval_id=data.get("approval_id"),
            duration_ms=data.get("duration_ms", 0),
            risk_tier=data.get("risk_tier", "low"),
            session_id=data.get("session_id", ""),
        )

    def to_json_line(self) -> str:
        """Convert to JSON line format."""
        return json.dumps(self.to_dict(), separators=(",", ":"))


class AuditStore:
    """
    Append-only audit log storage.

    Stores entries in JSONL (JSON Lines) format for efficient appending.
    Supports rotation by date and size.
    """

    # Secrets patterns to redact
    SECRET_PATTERNS = [
        "password", "secret", "token", "api_key", "apikey",
        "auth", "credential", "private_key", "access_key",
    ]

    def __init__(
        self,
        storage_dir: Path | None = None,
        max_file_size_mb: int = 100,
        retention_days: int = 30,
    ):
        """
        Initialize the audit store.

        Args:
            storage_dir: Directory for audit logs.
                        Defaults to %APPDATA%/VoiceStudio/logs/agent_audit/
            max_file_size_mb: Maximum size of a single log file before rotation
            retention_days: Number of days to retain logs
        """
        if storage_dir:
            self._storage_dir = storage_dir
        else:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._storage_dir = Path(appdata) / "VoiceStudio" / "logs" / "agent_audit"

        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._max_file_size = max_file_size_mb * 1024 * 1024
        self._retention_days = retention_days
        self._lock = threading.Lock()
        self._current_file: Path | None = None

    def _get_current_log_file(self) -> Path:
        """Get or create the current log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        base_name = f"audit_{date_str}"

        # Find the current file for today
        index = 0
        while True:
            suffix = f"_{index:03d}" if index > 0 else ""
            log_file = self._storage_dir / f"{base_name}{suffix}.jsonl"

            if not log_file.exists():
                return log_file

            # Check if file is too large
            if log_file.stat().st_size < self._max_file_size:
                return log_file

            index += 1

    def _redact_secrets(self, params: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive values from parameters."""
        redacted: dict[str, Any] = {}
        for key, value in params.items():
            key_lower = key.lower()
            if any(pattern in key_lower for pattern in self.SECRET_PATTERNS):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_secrets(value)
            elif isinstance(value, str) and len(value) > 100:
                # Truncate long strings
                redacted[key] = value[:100] + "...[truncated]"
            else:
                redacted[key] = value
        return redacted

    def append(self, entry: AuditEntry) -> None:
        """
        Append an entry to the audit log.

        Args:
            entry: The audit entry to append
        """
        # Redact secrets from parameters
        entry.parameters = self._redact_secrets(entry.parameters)

        with self._lock:
            log_file = self._get_current_log_file()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(entry.to_json_line() + "\n")

    def query(
        self,
        agent_id: str | None = None,
        user_id: str | None = None,
        correlation_id: str | None = None,
        tool_name: str | None = None,
        result: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        session_id: str | None = None,
        limit: int = 1000,
    ) -> list[AuditEntry]:
        """
        Query audit entries with filters.

        Args:
            agent_id: Filter by agent ID
            user_id: Filter by user ID
            correlation_id: Filter by correlation ID
            tool_name: Filter by tool name
            result: Filter by result (success/failure/denied)
            start_time: Filter entries after this time
            end_time: Filter entries before this time
            session_id: Filter by session ID
            limit: Maximum number of entries to return

        Returns:
            List of matching audit entries
        """
        results = []

        for entry in self._iter_entries(start_time, end_time):
            # Apply filters
            if agent_id and entry.agent_id != agent_id:
                continue
            if user_id and entry.user_id != user_id:
                continue
            if correlation_id and entry.correlation_id != correlation_id:
                continue
            if tool_name and entry.tool_name != tool_name:
                continue
            if result and entry.result != result:
                continue
            if session_id and entry.session_id != session_id:
                continue

            results.append(entry)

            if len(results) >= limit:
                break

        return results

    def _iter_entries(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Iterator[AuditEntry]:
        """Iterate over entries in time range."""
        # Get relevant log files
        log_files = sorted(self._storage_dir.glob("audit_*.jsonl"), reverse=True)

        for log_file in log_files:
            # Parse date from filename for quick filtering
            try:
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if start_time and file_date.date() < start_time.date():
                    continue
                if end_time and file_date.date() > end_time.date():
                    continue
            except (IndexError, ValueError):
                continue

            # Read entries from file
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                            entry = AuditEntry.from_dict(data)

                            # Time range filter
                            if start_time and entry.timestamp < start_time:
                                continue
                            if end_time and entry.timestamp > end_time:
                                continue

                            yield entry
                        except (json.JSONDecodeError, KeyError):
                            continue
            except OSError:
                continue

    def get_by_correlation_id(self, correlation_id: str) -> list[AuditEntry]:
        """Get all entries for a correlation ID (full trace)."""
        return self.query(correlation_id=correlation_id, limit=10000)

    def get_agent_history(
        self,
        agent_id: str,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get recent history for an agent."""
        return self.query(agent_id=agent_id, limit=limit)

    def get_failures(
        self,
        start_time: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get recent failures."""
        return self.query(result="failure", start_time=start_time, limit=limit)

    def get_denials(
        self,
        start_time: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get recent denied actions."""
        return self.query(result="denied", start_time=start_time, limit=limit)

    def cleanup_old_logs(self) -> int:
        """
        Remove log files older than retention period.

        Returns:
            Number of files removed
        """
        cutoff = datetime.now() - timedelta(days=self._retention_days)
        removed = 0

        for log_file in self._storage_dir.glob("audit_*.jsonl"):
            try:
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    log_file.unlink()
                    removed += 1
            except (IndexError, ValueError, OSError):
                continue

        return removed

    def get_stats(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Get statistics for the time range."""
        total = 0
        success = 0
        failure = 0
        denied = 0
        by_tool: dict[str, int] = {}
        by_agent: dict[str, int] = {}
        by_risk_tier: dict[str, int] = {}

        for entry in self._iter_entries(start_time, end_time):
            total += 1

            if entry.result == "success":
                success += 1
            elif entry.result == "failure":
                failure += 1
            elif entry.result == "denied":
                denied += 1

            by_tool[entry.tool_name] = by_tool.get(entry.tool_name, 0) + 1
            by_agent[entry.agent_id] = by_agent.get(entry.agent_id, 0) + 1
            by_risk_tier[entry.risk_tier] = by_risk_tier.get(entry.risk_tier, 0) + 1

        return {
            "total": total,
            "success": success,
            "failure": failure,
            "denied": denied,
            "by_tool": by_tool,
            "by_agent": by_agent,
            "by_risk_tier": by_risk_tier,
        }
