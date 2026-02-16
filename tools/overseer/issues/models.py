"""
Overseer Issue Logging - Data Models.

Issue, Recommendation, and related enums for unified issue tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class InstanceType(Enum):
    """Source of the issue."""

    AGENT = "agent"
    ENGINE = "engine"
    BUILD = "build"
    FRONTEND = "frontend"
    BACKEND = "backend"


class IssueSeverity(Enum):
    """Severity of the issue."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(Enum):
    """Current status of the issue."""

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class IssuePriority(Enum):
    """Business priority (urgency) of the issue."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class StateTransition:
    """A single state transition in issue lifecycle."""

    status: str
    at: datetime
    by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "at": self.at.isoformat(),
            "by": self.by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StateTransition:
        return cls(
            status=data["status"],
            at=datetime.fromisoformat(data["at"]),
            by=data.get("by"),
        )


@dataclass
class Recommendation:
    """A recommended action for an issue."""

    action: str
    confidence: float
    rationale: str
    similar_issues: list[str]
    risk_assessment: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action": self.action,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "similar_issues": self.similar_issues,
            "risk_assessment": self.risk_assessment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Recommendation:
        """Create from dictionary."""
        return cls(
            action=data["action"],
            confidence=float(data["confidence"]),
            rationale=data["rationale"],
            similar_issues=list(data.get("similar_issues", [])),
            risk_assessment=dict(data.get("risk_assessment", {})),
        )


@dataclass
class Issue:
    """A unified issue record from any instance type."""

    id: str
    timestamp: datetime
    instance_type: InstanceType
    instance_id: str
    correlation_id: str
    severity: IssueSeverity
    category: str
    error_type: str
    message: str
    context: dict[str, Any]
    pattern_hash: str
    status: IssueStatus
    recommendations: list[Recommendation] = field(default_factory=list)
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    state_history: list[StateTransition] = field(default_factory=list)
    parent_id: str | None = None
    related_ids: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    priority: IssuePriority | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        out = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "instance_type": self.instance_type.value,
            "instance_id": self.instance_id,
            "correlation_id": self.correlation_id,
            "severity": self.severity.value,
            "category": self.category,
            "error_type": self.error_type,
            "message": self.message,
            "context": self.context,
            "pattern_hash": self.pattern_hash,
            "status": self.status.value,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
        }
        if self.state_history:
            out["state_history"] = [s.to_dict() for s in self.state_history]
        if self.parent_id is not None:
            out["parent_id"] = self.parent_id
        if self.related_ids:
            out["related_ids"] = list(self.related_ids)
        if self.labels:
            out["labels"] = list(self.labels)
        if self.priority is not None:
            out["priority"] = self.priority.value
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Issue:
        """Create from dictionary."""
        state_history = [
            StateTransition.from_dict(s)
            for s in data.get("state_history", [])
        ]
        priority = data.get("priority")
        if priority is not None:
            priority = IssuePriority(priority)
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            instance_type=InstanceType(data["instance_type"]),
            instance_id=data["instance_id"],
            correlation_id=data["correlation_id"],
            severity=IssueSeverity(data["severity"]),
            category=data["category"],
            error_type=data["error_type"],
            message=data["message"],
            context=dict(data.get("context", {})),
            pattern_hash=data["pattern_hash"],
            status=IssueStatus(data["status"]),
            recommendations=[
                Recommendation.from_dict(r) for r in data.get("recommendations", [])
            ],
            resolved_at=(
                datetime.fromisoformat(data["resolved_at"])
                if data.get("resolved_at")
                else None
            ),
            resolved_by=data.get("resolved_by"),
            state_history=state_history,
            parent_id=data.get("parent_id"),
            related_ids=list(data.get("related_ids", [])),
            labels=list(data.get("labels", [])),
            priority=priority,
        )

    def to_json_line(self) -> str:
        """Convert to JSON line format."""
        import json
        return json.dumps(self.to_dict(), separators=(",", ":"))
