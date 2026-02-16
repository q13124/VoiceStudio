"""
Unified Audit Log Schema for VoiceStudio.

This schema combines requirements from:
1. AI Change Logging Architecture - file tracking, build correlation
2. Enhanced Traceability System - context mapping, governance integration

All audit entries use this schema for consistency across Python and C# components.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AuditEventType(str, Enum):
    """Types of events that can be logged to the audit system."""

    FILE_CREATE = "file_create"
    FILE_MODIFY = "file_modify"
    FILE_DELETE = "file_delete"
    FILE_RENAME = "file_rename"
    BUILD_WARNING = "build_warning"
    BUILD_ERROR = "build_error"
    BUILD_SUCCESS = "build_success"
    RUNTIME_EXCEPTION = "runtime_exception"
    XAML_COMPILE_FAILURE = "xaml_compile_failure"
    XAML_BINDING_FAILURE = "xaml_binding_failure"
    CRASH_ARTIFACT = "crash_artifact"
    GATE_PROOF = "gate_proof"
    COMPATIBILITY_DRIFT = "compatibility_drift"
    TEST_FAILURE = "test_failure"
    TEST_SUCCESS = "test_success"


class AuditActor(str, Enum):
    """Who or what performed the action."""

    HUMAN = "human"
    AI_AGENT = "ai-agent"
    SYSTEM = "system"
    CI_PIPELINE = "ci-pipeline"


class AuditOperation(str, Enum):
    """File operation types."""

    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    RENAME = "rename"


@dataclass
class AuditEntry:
    """
    A single audit log entry with full context for traceability.

    This schema enables:
    - Tracing changes back to commits, tasks, and roles
    - Correlating errors with file modifications
    - Cross-referencing crash artifacts with triggering changes
    - Filtering logs by subsystem, role, or task
    """

    # Required fields
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str = field(default="")  # AuditEventType value
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Context fields (from Enhanced Traceability proposal)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str | None = None  # VS-XXXX from Quality Ledger
    role: str | None = None  # Role 0-6 or "AI-Agent"
    actor: str = field(default=AuditActor.SYSTEM.value)

    # File change fields (from AI Change Logging proposal)
    file_path: str | None = None
    operation: str | None = None  # AuditOperation value
    lines_added: int = 0
    lines_removed: int = 0

    # Error fields
    error_code: str | None = None  # CS####, RCS####, XAML####
    message: str | None = None
    stack_trace: str | None = None
    severity: str | None = None  # info, warning, error, critical

    # Linkage fields
    commit_hash: str | None = None
    subsystem: str | None = None  # Panel name, engine ID, workflow
    gate: str | None = None  # Gate A-H if applicable
    linked_artifacts: list[str] = field(default_factory=list)

    # Metadata
    tags: list[str] = field(default_factory=list)
    summary: str = ""  # Human-readable description
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "entry_id": self.entry_id,
            "event_type": self.event_type,
            "correlation_id": self.correlation_id,
            "task_id": self.task_id,
            "role": self.role,
            "actor": self.actor,
            "file_path": self.file_path,
            "operation": self.operation,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "error_code": self.error_code,
            "message": self.message,
            "stack_trace": self.stack_trace,
            "severity": self.severity,
            "commit_hash": self.commit_hash,
            "subsystem": self.subsystem,
            "gate": self.gate,
            "linked_artifacts": self.linked_artifacts,
            "tags": self.tags,
            "summary": self.summary,
            "extra": self.extra,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditEntry:
        """Create AuditEntry from dictionary."""
        return cls(
            timestamp=data.get("timestamp", ""),
            entry_id=data.get("entry_id", str(uuid.uuid4())[:8]),
            event_type=data.get("event_type", ""),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            task_id=data.get("task_id"),
            role=data.get("role"),
            actor=data.get("actor", AuditActor.SYSTEM.value),
            file_path=data.get("file_path"),
            operation=data.get("operation"),
            lines_added=data.get("lines_added", 0),
            lines_removed=data.get("lines_removed", 0),
            error_code=data.get("error_code"),
            message=data.get("message"),
            stack_trace=data.get("stack_trace"),
            severity=data.get("severity"),
            commit_hash=data.get("commit_hash"),
            subsystem=data.get("subsystem"),
            gate=data.get("gate"),
            linked_artifacts=data.get("linked_artifacts", []),
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            extra=data.get("extra", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> AuditEntry:
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def to_markdown(self) -> str:
        """Format as human-readable Markdown row."""
        timestamp_short = self.timestamp[:19].replace("T", " ") if self.timestamp else ""
        role_display = self.role or "System"
        task_display = self.task_id or "-"
        file_display = self.file_path.split("/")[-1] if self.file_path else "-"

        return (
            f"| {timestamp_short} | {self.event_type} | {role_display} | "
            f"{task_display} | {file_display} | {self.summary} |"
        )


def create_file_change_entry(
    file_path: str,
    operation: str,
    role: str,
    task_id: str,
    summary: str,
    lines_added: int = 0,
    lines_removed: int = 0,
    actor: str = AuditActor.AI_AGENT.value,
) -> AuditEntry:
    """Factory function for file change audit entries."""
    event_type_map = {
        "create": AuditEventType.FILE_CREATE.value,
        "modify": AuditEventType.FILE_MODIFY.value,
        "delete": AuditEventType.FILE_DELETE.value,
        "rename": AuditEventType.FILE_RENAME.value,
    }
    return AuditEntry(
        event_type=event_type_map.get(operation.lower(), AuditEventType.FILE_MODIFY.value),
        file_path=file_path,
        operation=operation.lower(),
        role=role,
        task_id=task_id,
        summary=summary,
        lines_added=lines_added,
        lines_removed=lines_removed,
        actor=actor,
    )


def create_build_event_entry(
    event_type: str,
    error_code: str | None = None,
    message: str | None = None,
    file_path: str | None = None,
    task_id: str | None = None,
    commit_hash: str | None = None,
) -> AuditEntry:
    """Factory function for build event audit entries."""
    severity = "error" if "error" in event_type.lower() else "warning"
    return AuditEntry(
        event_type=event_type,
        error_code=error_code,
        message=message,
        file_path=file_path,
        task_id=task_id,
        commit_hash=commit_hash,
        severity=severity,
        actor=AuditActor.SYSTEM.value,
        summary=f"{event_type}: {error_code or 'unknown'} in {file_path or 'build'}",
    )


def create_exception_entry(
    exception: Exception,
    subsystem: str,
    correlation_id: str | None = None,
    task_id: str | None = None,
    extra_context: dict[str, Any] | None = None,
) -> AuditEntry:
    """Factory function for runtime exception audit entries."""
    import traceback

    return AuditEntry(
        event_type=AuditEventType.RUNTIME_EXCEPTION.value,
        message=str(exception),
        stack_trace=traceback.format_exc(),
        subsystem=subsystem,
        correlation_id=correlation_id or str(uuid.uuid4()),
        task_id=task_id,
        severity="error",
        actor=AuditActor.SYSTEM.value,
        summary=f"Exception in {subsystem}: {type(exception).__name__}",
        extra=extra_context or {},
    )


def create_xaml_failure_entry(
    file_path: str,
    error_type: str,
    message: str,
    commit_hash: str | None = None,
) -> AuditEntry:
    """Factory function for XAML failure audit entries."""
    event_type = (
        AuditEventType.XAML_COMPILE_FAILURE.value
        if "compile" in error_type.lower()
        else AuditEventType.XAML_BINDING_FAILURE.value
    )
    return AuditEntry(
        event_type=event_type,
        file_path=file_path,
        message=message,
        commit_hash=commit_hash,
        severity="error",
        subsystem="UI.XAML",
        actor=AuditActor.SYSTEM.value,
        summary=f"XAML {error_type}: {file_path.split('/')[-1]}",
    )
