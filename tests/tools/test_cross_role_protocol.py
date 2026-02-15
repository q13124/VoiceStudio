"""Tests for cross-role protocol module."""
from __future__ import annotations

from tools.context.core.cross_role_protocol import (
    ROLE_NAMES,
    CrossRoleProtocol,
    HandoffPayload,
    HandoffPayloadValidator,
    RoleTransitionValidator,
    create_handoff,
    get_escalation_path,
    get_valid_targets,
    validate_handoff,
    validate_transition,
)


class TestRoleTransitionValidator:
    """Tests for role transition validation."""

    def test_valid_overseer_to_any_role(self) -> None:
        """Overseer can transition to any role."""
        validator = RoleTransitionValidator()
        for role_name in ROLE_NAMES.values():
            result = validator.validate_transition("overseer", role_name)
            assert result.is_valid, f"Overseer -> {role_name} should be valid"

    def test_valid_debug_agent_to_any_role(self) -> None:
        """Debug Agent can return to any role after investigation."""
        validator = RoleTransitionValidator()
        for role_name in ROLE_NAMES.values():
            result = validator.validate_transition("debug-agent", role_name)
            assert result.is_valid, f"debug-agent -> {role_name} should be valid"

    def test_invalid_ui_to_engine_direct(self) -> None:
        """UI Engineer cannot transition directly to Engine Engineer."""
        result = validate_transition("ui-engineer", "engine-engineer")
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Invalid transition" in result.errors[0]

    def test_valid_ui_to_debug(self) -> None:
        """UI Engineer can transition to Debug Agent."""
        result = validate_transition("ui-engineer", "debug-agent")
        assert result.is_valid

    def test_unknown_source_role(self) -> None:
        """Unknown source role should fail validation."""
        result = validate_transition("unknown-role", "overseer")
        assert not result.is_valid
        assert "Unknown source role" in result.errors[0]

    def test_unknown_target_role(self) -> None:
        """Unknown target role should fail validation."""
        result = validate_transition("overseer", "unknown-role")
        assert not result.is_valid
        assert "Unknown target role" in result.errors[0]

    def test_escalation_to_overseer_warning(self) -> None:
        """Escalating to Overseer should produce a warning."""
        result = validate_transition("core-platform", "overseer")
        assert result.is_valid
        assert len(result.warnings) > 0
        assert "Escalating to Overseer" in result.warnings[0]

    def test_transition_to_debug_warning(self) -> None:
        """Transitioning to Debug Agent should produce a warning."""
        result = validate_transition("core-platform", "debug-agent")
        assert result.is_valid
        assert any("Debug Agent" in w for w in result.warnings)

    def test_get_valid_targets(self) -> None:
        """Get valid targets should return correct list."""
        targets = get_valid_targets("ui-engineer")
        assert "overseer" in targets
        assert "debug-agent" in targets
        assert "core-platform" in targets

    def test_get_valid_targets_unknown_role(self) -> None:
        """Unknown role should return empty list."""
        targets = get_valid_targets("unknown")
        assert targets == []


class TestHandoffPayloadValidator:
    """Tests for handoff payload validation."""

    def test_valid_normal_payload(self) -> None:
        """Valid normal escalation payload."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="UI component failing to render",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert result.is_valid

    def test_valid_urgent_payload(self) -> None:
        """Valid urgent escalation payload."""
        payload = HandoffPayload(
            source_role="core-platform",
            target_role="overseer",
            reason="Backend service down",
            context_summary="Service crashed after update",
            escalation_level="urgent",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert result.is_valid

    def test_valid_critical_payload(self) -> None:
        """Valid critical escalation payload."""
        payload = HandoffPayload(
            source_role="release-engineer",
            target_role="overseer",
            reason="Release blocked by critical bug",
            context_summary="Production deployment failed",
            escalation_level="critical",
            blockers=["Database migration failed", "Rollback required"],
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert result.is_valid

    def test_missing_reason_fails(self) -> None:
        """Missing reason should fail validation."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert not result.is_valid
        assert any("reason" in e.lower() for e in result.errors)

    def test_missing_context_summary_urgent(self) -> None:
        """Missing context summary for urgent should fail."""
        payload = HandoffPayload(
            source_role="core-platform",
            target_role="overseer",
            reason="Service down",
            escalation_level="urgent",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert not result.is_valid
        assert any("context_summary" in e for e in result.errors)

    def test_missing_blockers_critical(self) -> None:
        """Missing blockers for critical should fail."""
        payload = HandoffPayload(
            source_role="release-engineer",
            target_role="overseer",
            reason="Release blocked",
            context_summary="Critical issue found",
            escalation_level="critical",
            blockers=[],
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert not result.is_valid
        assert any("blockers" in e for e in result.errors)

    def test_invalid_escalation_level(self) -> None:
        """Invalid escalation level should fail."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="Bug found",
            escalation_level="super-critical",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert not result.is_valid
        assert "Invalid escalation level" in result.errors[0]

    def test_task_id_format_warning(self) -> None:
        """Invalid task ID format should produce warning."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="Bug in task",
            task_id="invalid-task",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert result.is_valid  # Warnings don't fail validation
        assert any("Task ID format" in w for w in result.warnings)

    def test_valid_task_id_format(self) -> None:
        """Valid task ID format should pass."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="Bug in task",
            task_id="TASK-0001",
        )
        validator = HandoffPayloadValidator()
        result = validator.validate(payload)
        assert result.is_valid
        assert not any("Task ID" in w for w in result.warnings)


class TestCrossRoleProtocol:
    """Tests for the main protocol coordinator."""

    def test_validate_complete_handoff(self) -> None:
        """Validate a complete handoff operation."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="Component crash on load",
            task_id="TASK-1234",
        )
        result = validate_handoff(payload)
        assert result.is_valid

    def test_create_handoff(self) -> None:
        """Create and validate a handoff."""
        payload, result = create_handoff(
            source_role="core-platform",
            target_role="debug-agent",
            reason="Service timeout",
            task_id="TASK-0001",
        )
        assert isinstance(payload, HandoffPayload)
        assert result.is_valid
        assert payload.source_role == "core-platform"
        assert payload.target_role == "debug-agent"

    def test_create_invalid_handoff(self) -> None:
        """Create handoff with invalid transition."""
        _payload, result = create_handoff(
            source_role="ui-engineer",
            target_role="engine-engineer",  # Invalid direct transition
            reason="Need engine help",
        )
        assert not result.is_valid
        assert any("Invalid transition" in e for e in result.errors)

    def test_get_escalation_path_build_failure(self) -> None:
        """Get escalation path for build failure."""
        path = get_escalation_path("ui-engineer", "build_failure")
        assert "debug-agent" in path
        assert "build-tooling" in path

    def test_get_escalation_path_removes_current(self) -> None:
        """Escalation path should not include current role."""
        path = get_escalation_path("debug-agent", "build_failure")
        assert "debug-agent" not in path

    def test_get_all_roles(self) -> None:
        """Get information about all roles."""
        protocol = CrossRoleProtocol()
        roles = protocol.get_all_roles()
        assert len(roles) == 8
        assert all("name" in r for r in roles)
        assert all("id" in r for r in roles)
        assert all("valid_targets" in r for r in roles)


class TestHandoffPayloadSerialization:
    """Tests for HandoffPayload serialization."""

    def test_to_dict(self) -> None:
        """Convert payload to dictionary."""
        payload = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            reason="Bug found",
            task_id="TASK-0001",
        )
        data = payload.to_dict()
        assert data["source_role"] == "ui-engineer"
        assert data["target_role"] == "debug-agent"
        assert data["reason"] == "Bug found"
        assert data["task_id"] == "TASK-0001"

    def test_from_dict(self) -> None:
        """Create payload from dictionary."""
        data = {
            "source_role": "core-platform",
            "target_role": "overseer",
            "reason": "Escalation needed",
            "escalation_level": "urgent",
            "context_summary": "Service issues",
        }
        payload = HandoffPayload.from_dict(data)
        assert payload.source_role == "core-platform"
        assert payload.target_role == "overseer"
        assert payload.escalation_level == "urgent"

    def test_roundtrip(self) -> None:
        """Test serialize and deserialize."""
        original = HandoffPayload(
            source_role="engine-engineer",
            target_role="debug-agent",
            reason="Model loading failed",
            task_id="TASK-9999",
            artifacts=["error.log", "stack.txt"],
            metadata={"model": "f5-tts"},
        )
        data = original.to_dict()
        restored = HandoffPayload.from_dict(data)

        assert restored.source_role == original.source_role
        assert restored.target_role == original.target_role
        assert restored.reason == original.reason
        assert restored.artifacts == original.artifacts
        assert restored.metadata == original.metadata
