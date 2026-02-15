"""
Cross-Role Protocol Module.

Provides validation functions and protocols for role transitions, handoffs,
and cross-role communication in the VoiceStudio context management system.

This module ensures:
- Valid role transitions are enforced
- Handoff payloads conform to expected structure
- Context preservation during role switches
- Proper escalation paths are followed
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any


class RoleID(IntEnum):
    """VoiceStudio role identifiers."""
    OVERSEER = 0
    SYSTEM_ARCHITECT = 1
    BUILD_TOOLING = 2
    UI_ENGINEER = 3
    CORE_PLATFORM = 4
    ENGINE_ENGINEER = 5
    RELEASE_ENGINEER = 6
    DEBUG_AGENT = 7


ROLE_NAMES: dict[RoleID, str] = {
    RoleID.OVERSEER: "overseer",
    RoleID.SYSTEM_ARCHITECT: "system-architect",
    RoleID.BUILD_TOOLING: "build-tooling",
    RoleID.UI_ENGINEER: "ui-engineer",
    RoleID.CORE_PLATFORM: "core-platform",
    RoleID.ENGINE_ENGINEER: "engine-engineer",
    RoleID.RELEASE_ENGINEER: "release-engineer",
    RoleID.DEBUG_AGENT: "debug-agent",
}

NAME_TO_ROLE: dict[str, RoleID] = {v: k for k, v in ROLE_NAMES.items()}


# Valid role transition matrix
# Key: source role, Value: set of valid target roles
VALID_TRANSITIONS: dict[RoleID, set[RoleID]] = {
    # Overseer can transition to any role (coordination)
    RoleID.OVERSEER: set(RoleID),

    # System Architect can transition to implementation roles
    RoleID.SYSTEM_ARCHITECT: {
        RoleID.OVERSEER,  # Escalate
        RoleID.BUILD_TOOLING,
        RoleID.UI_ENGINEER,
        RoleID.CORE_PLATFORM,
        RoleID.ENGINE_ENGINEER,
        RoleID.RELEASE_ENGINEER,
        RoleID.DEBUG_AGENT,
    },

    # Build & Tooling transitions
    RoleID.BUILD_TOOLING: {
        RoleID.OVERSEER,  # Escalate
        RoleID.SYSTEM_ARCHITECT,  # Architecture questions
        RoleID.RELEASE_ENGINEER,  # Release integration
        RoleID.DEBUG_AGENT,  # Build failures
    },

    # UI Engineer transitions
    RoleID.UI_ENGINEER: {
        RoleID.OVERSEER,  # Escalate
        RoleID.SYSTEM_ARCHITECT,  # Design review
        RoleID.CORE_PLATFORM,  # Backend integration
        RoleID.DEBUG_AGENT,  # UI bugs
    },

    # Core Platform transitions
    RoleID.CORE_PLATFORM: {
        RoleID.OVERSEER,  # Escalate
        RoleID.SYSTEM_ARCHITECT,  # Architecture review
        RoleID.ENGINE_ENGINEER,  # Engine integration
        RoleID.BUILD_TOOLING,  # Build setup
        RoleID.DEBUG_AGENT,  # Platform bugs
    },

    # Engine Engineer transitions
    RoleID.ENGINE_ENGINEER: {
        RoleID.OVERSEER,  # Escalate
        RoleID.SYSTEM_ARCHITECT,  # Architecture review
        RoleID.CORE_PLATFORM,  # Platform integration
        RoleID.DEBUG_AGENT,  # Engine bugs
    },

    # Release Engineer transitions
    RoleID.RELEASE_ENGINEER: {
        RoleID.OVERSEER,  # Escalate
        RoleID.BUILD_TOOLING,  # Build issues
        RoleID.DEBUG_AGENT,  # Release bugs
    },

    # Debug Agent can return to any role after investigation
    RoleID.DEBUG_AGENT: set(RoleID),
}


@dataclass
class HandoffPayload:
    """Standard payload structure for role handoffs."""

    source_role: str
    target_role: str
    task_id: str | None = None
    reason: str = ""
    context_summary: str = ""
    escalation_level: str = "normal"  # normal, urgent, critical
    artifacts: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_role": self.source_role,
            "target_role": self.target_role,
            "task_id": self.task_id,
            "reason": self.reason,
            "context_summary": self.context_summary,
            "escalation_level": self.escalation_level,
            "artifacts": self.artifacts,
            "blockers": self.blockers,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HandoffPayload:
        """Create from dictionary."""
        return cls(
            source_role=data.get("source_role", ""),
            target_role=data.get("target_role", ""),
            task_id=data.get("task_id"),
            reason=data.get("reason", ""),
            context_summary=data.get("context_summary", ""),
            escalation_level=data.get("escalation_level", "normal"),
            artifacts=data.get("artifacts", []),
            blockers=data.get("blockers", []),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_suggestion(self, message: str) -> None:
        """Add a suggestion."""
        self.suggestions.append(message)

    def merge(self, other: ValidationResult) -> None:
        """Merge another validation result into this one."""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.suggestions.extend(other.suggestions)


class RoleTransitionValidator:
    """Validates role transitions according to defined protocols."""

    def __init__(self, transitions: dict[RoleID, set[RoleID]] | None = None):
        """Initialize with optional custom transition matrix."""
        self.transitions = transitions or VALID_TRANSITIONS

    def validate_transition(
        self,
        source_role: str,
        target_role: str,
    ) -> ValidationResult:
        """Validate a role transition."""
        result = ValidationResult(is_valid=True)

        # Resolve role names to IDs
        source_id = NAME_TO_ROLE.get(source_role.lower())
        target_id = NAME_TO_ROLE.get(target_role.lower())

        if source_id is None:
            result.add_error(f"Unknown source role: {source_role}")
            return result

        if target_id is None:
            result.add_error(f"Unknown target role: {target_role}")
            return result

        # Check if transition is valid
        valid_targets = self.transitions.get(source_id, set())
        if target_id not in valid_targets:
            result.add_error(
                f"Invalid transition: {source_role} -> {target_role}. "
                f"Valid targets: {[ROLE_NAMES[r] for r in valid_targets]}"
            )
            result.add_suggestion(
                f"Consider escalating to Overseer first, then transitioning to {target_role}"
            )

        # Add warnings for specific transition patterns
        if source_id != RoleID.OVERSEER and target_id == RoleID.OVERSEER:
            result.add_warning(
                "Escalating to Overseer. Ensure you've documented the escalation reason."
            )

        if target_id == RoleID.DEBUG_AGENT:
            result.add_warning(
                "Transitioning to Debug Agent. Ensure error context and stack traces are included."
            )

        return result

    def get_valid_targets(self, source_role: str) -> list[str]:
        """Get list of valid target roles for a source role."""
        source_id = NAME_TO_ROLE.get(source_role.lower())
        if source_id is None:
            return []

        valid_ids = self.transitions.get(source_id, set())
        return [ROLE_NAMES[r] for r in valid_ids]


class HandoffPayloadValidator:
    """Validates handoff payloads for completeness and correctness."""

    # Required fields based on escalation level
    REQUIRED_BY_LEVEL = {
        "normal": {"source_role", "target_role", "reason"},
        "urgent": {"source_role", "target_role", "reason", "context_summary"},
        "critical": {"source_role", "target_role", "reason", "context_summary", "blockers"},
    }

    # Fields that should have content
    NON_EMPTY_FIELDS = {"source_role", "target_role", "reason"}

    def validate(self, payload: HandoffPayload) -> ValidationResult:
        """Validate a handoff payload."""
        result = ValidationResult(is_valid=True)

        # Check escalation level
        if payload.escalation_level not in self.REQUIRED_BY_LEVEL:
            result.add_error(
                f"Invalid escalation level: {payload.escalation_level}. "
                f"Valid levels: {list(self.REQUIRED_BY_LEVEL.keys())}"
            )
            return result

        # Check required fields
        required = self.REQUIRED_BY_LEVEL[payload.escalation_level]
        payload_dict = payload.to_dict()

        for field_name in required:
            value = payload_dict.get(field_name)
            if value is None or (isinstance(value, (str, list)) and not value):
                result.add_error(f"Missing required field for {payload.escalation_level} escalation: {field_name}")

        # Check non-empty fields
        for field_name in self.NON_EMPTY_FIELDS:
            value = payload_dict.get(field_name)
            if isinstance(value, str) and not value.strip():
                result.add_error(f"Field must not be empty: {field_name}")

        # Validate task ID format if present
        if payload.task_id and not self._validate_task_id(payload.task_id):
            result.add_warning(f"Task ID format may be incorrect: {payload.task_id}")
            result.add_suggestion("Expected format: TASK-XXXX (e.g., TASK-0001)")

        # Check for context preservation
        if payload.escalation_level in ("urgent", "critical") and not payload.context_summary:
            result.add_warning(
                "Context summary is recommended for urgent/critical handoffs "
                "to ensure continuity"
            )

        # Check blockers for critical escalations
        if payload.escalation_level == "critical" and not payload.blockers:
            result.add_warning(
                "Critical escalations should include blockers to help prioritize resolution"
            )

        return result

    def _validate_task_id(self, task_id: str) -> bool:
        """Validate task ID format."""
        return bool(re.match(r"^TASK-\d{4,}$", task_id))


class CrossRoleProtocol:
    """Main protocol coordinator for cross-role operations."""

    def __init__(self):
        """Initialize protocol validators."""
        self.transition_validator = RoleTransitionValidator()
        self.payload_validator = HandoffPayloadValidator()

    def validate_handoff(
        self,
        payload: HandoffPayload,
    ) -> ValidationResult:
        """Validate a complete handoff operation."""
        result = ValidationResult(is_valid=True)

        # Validate payload structure
        payload_result = self.payload_validator.validate(payload)
        result.merge(payload_result)

        # Validate transition
        transition_result = self.transition_validator.validate_transition(
            payload.source_role,
            payload.target_role,
        )
        result.merge(transition_result)

        return result

    def create_handoff(
        self,
        source_role: str,
        target_role: str,
        reason: str,
        task_id: str | None = None,
        context_summary: str = "",
        escalation_level: str = "normal",
        artifacts: list[str] | None = None,
        blockers: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[HandoffPayload, ValidationResult]:
        """Create and validate a handoff payload."""
        payload = HandoffPayload(
            source_role=source_role,
            target_role=target_role,
            task_id=task_id,
            reason=reason,
            context_summary=context_summary,
            escalation_level=escalation_level,
            artifacts=artifacts or [],
            blockers=blockers or [],
            metadata=metadata or {},
        )

        validation = self.validate_handoff(payload)
        return payload, validation

    def get_escalation_path(self, current_role: str, issue_type: str) -> list[str]:
        """Get recommended escalation path for an issue type."""
        paths = {
            "build_failure": ["debug-agent", "build-tooling", "overseer"],
            "architecture_issue": ["system-architect", "overseer"],
            "ui_bug": ["debug-agent", "ui-engineer"],
            "engine_error": ["debug-agent", "engine-engineer"],
            "platform_issue": ["debug-agent", "core-platform"],
            "release_blocker": ["build-tooling", "release-engineer", "overseer"],
            "security_issue": ["system-architect", "overseer"],
            "performance_issue": ["debug-agent", "engine-engineer", "core-platform"],
        }

        path = paths.get(issue_type.lower(), ["overseer"])

        # Remove current role from path
        current_lower = current_role.lower()
        return [r for r in path if r != current_lower]

    def get_all_roles(self) -> list[dict[str, Any]]:
        """Get information about all roles."""
        return [
            {
                "id": role_id.value,
                "name": name,
                "valid_targets": self.transition_validator.get_valid_targets(name),
            }
            for role_id, name in ROLE_NAMES.items()
        ]


# Convenience functions for common operations
def validate_transition(source: str, target: str) -> ValidationResult:
    """Validate a role transition."""
    return RoleTransitionValidator().validate_transition(source, target)


def validate_handoff(payload: HandoffPayload) -> ValidationResult:
    """Validate a handoff payload."""
    return CrossRoleProtocol().validate_handoff(payload)


def create_handoff(
    source_role: str,
    target_role: str,
    reason: str,
    **kwargs,
) -> tuple[HandoffPayload, ValidationResult]:
    """Create and validate a handoff."""
    return CrossRoleProtocol().create_handoff(source_role, target_role, reason, **kwargs)


def get_valid_targets(source_role: str) -> list[str]:
    """Get valid target roles for a source role."""
    return RoleTransitionValidator().get_valid_targets(source_role)


def get_escalation_path(current_role: str, issue_type: str) -> list[str]:
    """Get recommended escalation path for an issue."""
    return CrossRoleProtocol().get_escalation_path(current_role, issue_type)
