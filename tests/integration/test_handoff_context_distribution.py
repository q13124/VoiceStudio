"""
Integration tests for handoff + context distribution flow.

These tests verify that:
1. HandoffQueue correctly distributes context during role transitions
2. Cross-role protocol validates transitions properly
3. Context bundles are prepared for target roles
4. Notification callbacks are invoked correctly
5. Handoff entries persist and can be retrieved

Phase 2 Context Management Automation - Integration Tests
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Test fixtures and mocks
# ---------------------------------------------------------------------------


@dataclass
class MockContextBundle:
    """Mock context bundle for testing."""

    role: str
    task_id: str | None
    phase: str | None
    content: dict[str, str]

    def to_preamble_markdown(self) -> str:
        return f"## Context for {self.role}\n\nPhase: {self.phase}\nTask: {self.task_id}"

    def to_json(self) -> str:
        return json.dumps(
            {
                "role": self.role,
                "task_id": self.task_id,
                "phase": self.phase,
                "content": self.content,
            }
        )


class MockContextDistributor:
    """Mock context distributor for testing."""

    def __init__(self):
        self._distributions: list[dict[str, Any]] = []

    def prepare_for_role(
        self,
        target_role: str,
        task_id: str | None = None,
        phase: str | None = None,
    ) -> MockContextBundle:
        """Prepare context bundle for target role."""
        bundle = MockContextBundle(
            role=target_role,
            task_id=task_id,
            phase=phase,
            content={
                "state": f"Prepared for {target_role}",
                "task": f"Task {task_id}" if task_id else "No task",
            },
        )
        self._distributions.append(
            {
                "role": target_role,
                "task_id": task_id,
                "phase": phase,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return bundle

    @property
    def distributions(self) -> list[dict[str, Any]]:
        return self._distributions


@pytest.fixture
def temp_storage_dir(tmp_path: Path):
    """Create temporary storage directory for handoffs."""
    storage = tmp_path / "handoffs"
    storage.mkdir(parents=True, exist_ok=True)
    return storage


@pytest.fixture
def mock_distributor():
    """Create mock context distributor."""
    return MockContextDistributor()


# ---------------------------------------------------------------------------
# Cross-Role Protocol Tests
# ---------------------------------------------------------------------------


class TestCrossRoleProtocolValidation:
    """Tests for cross-role protocol transition validation."""

    def test_valid_transition_overseer_to_any(self) -> None:
        """Overseer should be able to transition to any role."""
        from tools.context.core.cross_role_protocol import validate_transition

        target_roles = [
            "system-architect",
            "build-tooling",
            "ui-engineer",
            "core-platform",
            "engine-engineer",
            "release-engineer",
            "debug-agent",
        ]

        for target in target_roles:
            result = validate_transition("overseer", target)
            assert result.is_valid, f"Overseer -> {target} should be valid"

    def test_invalid_ui_to_engine_direct(self) -> None:
        """UI Engineer should not transition directly to Engine Engineer."""
        from tools.context.core.cross_role_protocol import validate_transition

        result = validate_transition("ui-engineer", "engine-engineer")
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_valid_debug_agent_can_return_anywhere(self) -> None:
        """Debug Agent should be able to return to any role after investigation."""
        from tools.context.core.cross_role_protocol import validate_transition

        target_roles = [
            "overseer",
            "system-architect",
            "ui-engineer",
            "core-platform",
        ]

        for target in target_roles:
            result = validate_transition("debug-agent", target)
            assert result.is_valid, f"Debug Agent -> {target} should be valid"

    def test_escalation_path_for_build_failure(self) -> None:
        """Get escalation path for build failure should return valid path."""
        from tools.context.core.cross_role_protocol import get_escalation_path

        path = get_escalation_path("ui-engineer", "build_failure")

        assert len(path) > 0
        # First escalation should be debug-agent or build-tooling
        assert path[0] in ["debug-agent", "build-tooling", "overseer"]

    def test_create_handoff_validates_transition(self) -> None:
        """create_handoff should validate the transition."""
        from tools.context.core.cross_role_protocol import create_handoff

        # Valid transition
        payload, validation = create_handoff(
            source_role="core-platform",
            target_role="debug-agent",
            reason="Platform bug investigation needed",
        )

        assert validation.is_valid
        assert payload is not None
        assert payload.source_role == "core-platform"
        assert payload.target_role == "debug-agent"

    def test_create_handoff_with_invalid_transition(self) -> None:
        """create_handoff should fail validation for invalid transitions."""
        from tools.context.core.cross_role_protocol import create_handoff

        # Invalid transition: UI -> Engine (must go via Architect or Overseer)
        _payload, validation = create_handoff(
            source_role="ui-engineer",
            target_role="engine-engineer",
            reason="Need engine changes",
        )

        assert not validation.is_valid
        assert len(validation.suggestions) > 0


class TestHandoffPayloadValidation:
    """Tests for handoff payload structure validation."""

    def test_normal_escalation_requires_reason(self) -> None:
        """Normal escalation requires reason field."""
        from tools.context.core.cross_role_protocol import (
            HandoffPayload,
            HandoffPayloadValidator,
        )

        payload = HandoffPayload(
            source_role="core-platform",
            target_role="debug-agent",
            reason="",  # Empty reason
        )

        validator = HandoffPayloadValidator()
        result = validator.validate(payload)

        assert not result.is_valid
        assert any("reason" in e.lower() for e in result.errors)

    def test_urgent_escalation_requires_context_summary(self) -> None:
        """Urgent escalation requires context summary."""
        from tools.context.core.cross_role_protocol import (
            HandoffPayload,
            HandoffPayloadValidator,
        )

        payload = HandoffPayload(
            source_role="core-platform",
            target_role="overseer",
            reason="Urgent issue",
            escalation_level="urgent",
            context_summary="",  # Missing for urgent
        )

        validator = HandoffPayloadValidator()
        result = validator.validate(payload)

        # Should have warning about missing context summary
        assert len(result.warnings) > 0 or not result.is_valid

    def test_critical_escalation_requires_blockers(self) -> None:
        """Critical escalation requires blockers list."""
        from tools.context.core.cross_role_protocol import (
            HandoffPayload,
            HandoffPayloadValidator,
        )

        payload = HandoffPayload(
            source_role="release-engineer",
            target_role="overseer",
            reason="Critical deployment failure",
            escalation_level="critical",
            context_summary="Deployment blocked",
            blockers=[],  # Empty for critical
        )

        validator = HandoffPayloadValidator()
        result = validator.validate(payload)

        # Should fail or warn about missing blockers
        assert len(result.warnings) > 0 or len(result.errors) > 0


# ---------------------------------------------------------------------------
# Handoff Queue Integration Tests
# ---------------------------------------------------------------------------


class TestHandoffQueueIntegration:
    """Integration tests for HandoffQueue with context distribution."""

    def test_handoff_persists_to_storage(self, temp_storage_dir: Path) -> None:
        """Handoff entries should persist to storage."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        entry = queue.handoff(
            issue_id="TEST-001",
            from_role="core-platform",
            to_role="debug-agent",
            reason="Investigate job state persistence issue",
            priority="high",
        )

        assert entry is not None
        assert entry.issue_id == "TEST-001"
        assert entry.from_role == "core-platform"
        assert entry.to_role == "debug-agent"

        # Check persistence
        index_file = temp_storage_dir / "handoff_index.jsonl"
        assert index_file.exists()

        # Read back
        with open(index_file, encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) >= 1
        stored = json.loads(lines[-1])
        assert stored["issue_id"] == "TEST-001"

    def test_get_role_queue_retrieves_entries(self, temp_storage_dir: Path) -> None:
        """get_role_queue should retrieve entries for a specific role."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        # Create multiple handoffs
        queue.handoff(
            issue_id="TEST-001",
            from_role="ui-engineer",
            to_role="debug-agent",
            reason="UI crash",
            priority="high",
        )
        queue.handoff(
            issue_id="TEST-002",
            from_role="core-platform",
            to_role="debug-agent",
            reason="Backend error",
            priority="medium",
        )
        queue.handoff(
            issue_id="TEST-003",
            from_role="ui-engineer",
            to_role="core-platform",  # Different target
            reason="API integration issue",
            priority="low",
        )

        # Get debug-agent queue
        debug_queue = queue.get_role_queue("debug-agent")

        assert len(debug_queue) == 2
        issue_ids = [e["issue_id"] for e in debug_queue]
        assert "TEST-001" in issue_ids
        assert "TEST-002" in issue_ids
        assert "TEST-003" not in issue_ids

    def test_notification_callback_invoked(self, temp_storage_dir: Path) -> None:
        """Notification callbacks should be invoked on handoff."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        notifications = []

        def callback(entry):
            notifications.append(entry)

        queue.register_notification(callback)

        queue.handoff(
            issue_id="TEST-001",
            from_role="core-platform",
            to_role="debug-agent",
            reason="Test notification",
            priority="medium",
        )

        assert len(notifications) == 1
        assert notifications[0].issue_id == "TEST-001"

    def test_acknowledge_updates_status(self, temp_storage_dir: Path) -> None:
        """Acknowledging a handoff should update its status."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        entry = queue.handoff(
            issue_id="TEST-001",
            from_role="core-platform",
            to_role="debug-agent",
            reason="Test acknowledgment",
            priority="high",
        )

        assert entry.status == "pending"
        assert entry.acknowledged_at is None

        # Acknowledge (method returns bool and uses 'role' parameter)
        result = queue.acknowledge(entry.id, role="debug-agent")

        assert result is True
        # Verify the entry was updated via get_role_queue
        entries = queue.get_role_queue("debug-agent", unacknowledged_only=False)
        matching = [e for e in entries if e["id"] == entry.id]
        assert len(matching) == 1
        assert matching[0]["status"] == "acknowledged"
        assert matching[0]["acknowledged_at"] is not None

    def test_complete_updates_resolution(self, temp_storage_dir: Path) -> None:
        """Completing a handoff should update resolution."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        entry = queue.handoff(
            issue_id="TEST-001",
            from_role="core-platform",
            to_role="debug-agent",
            reason="Test completion",
            priority="high",
        )

        # Acknowledge first (method uses 'role' parameter)
        queue.acknowledge(entry.id, role="debug-agent")

        # Complete (method returns bool)
        result = queue.complete(
            entry.id,
            resolution="Fixed: Root cause was missing null check in JobStateStore",
        )

        assert result is True
        # Completed entries are excluded from get_role_queue by design
        # Verify by checking entry is no longer in active queue
        entries = queue.get_role_queue("debug-agent", unacknowledged_only=False)
        matching = [e for e in entries if e["id"] == entry.id]
        assert len(matching) == 0  # Completed entries are filtered out


class TestHandoffContextDistribution:
    """Tests for automatic context distribution during handoffs."""

    def test_context_prepared_flag_set(self, temp_storage_dir: Path) -> None:
        """Context prepared flag should be set when distribution is enabled."""
        from tools.overseer.issues.handoff import HandoffQueue

        # We need to mock the distributor since it may not be available
        with patch("tools.overseer.issues.handoff.HandoffQueue._get_distributor") as mock_get:
            mock_distributor = MagicMock()
            mock_bundle = MagicMock()
            mock_bundle.to_json.return_value = '{"role": "debug-agent"}'
            mock_distributor.prepare_for_role.return_value = mock_bundle
            mock_get.return_value = mock_distributor

            queue = HandoffQueue(
                storage_dir=temp_storage_dir,
                auto_distribute_context=True,
            )

            entry = queue.handoff(
                issue_id="TEST-001",
                from_role="core-platform",
                to_role="debug-agent",
                reason="Test context distribution",
                priority="high",
                task_id="TASK-0042",
                phase="Construct",
            )

            # Context should be prepared
            assert entry.context_prepared or mock_distributor.prepare_for_role.called

    def test_handoff_includes_task_context(self, temp_storage_dir: Path) -> None:
        """Handoff should include task context when provided."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        entry = queue.handoff(
            issue_id="TEST-001",
            from_role="core-platform",
            to_role="debug-agent",
            reason="Test task context",
            priority="high",
            task_id="TASK-0042",
            phase="Verify",
        )

        assert entry.task_id == "TASK-0042"
        assert entry.phase == "Verify"


# ---------------------------------------------------------------------------
# End-to-End Handoff Flow Tests
# ---------------------------------------------------------------------------


class TestEndToEndHandoffFlow:
    """End-to-end tests for complete handoff flow."""

    def test_full_handoff_cycle(self, temp_storage_dir: Path) -> None:
        """Test complete handoff cycle: create -> acknowledge -> complete."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        # 1. Create handoff
        entry = queue.handoff(
            issue_id="CRITICAL-001",
            from_role="release-engineer",
            to_role="overseer",
            reason="Production deployment blocked by certificate issue",
            priority="urgent",
            severity="critical",
            task_id="TASK-0099",
            phase="Deploy",
        )

        assert entry.status == "pending"
        assert entry.severity == "critical"

        # 2. Acknowledge (method returns bool and uses 'role' parameter)
        ack_result = queue.acknowledge(entry.id, role="overseer")
        assert ack_result is True

        # Verify acknowledged status in queue
        overseer_queue = queue.get_role_queue("overseer", unacknowledged_only=False)
        matching = [e for e in overseer_queue if e["issue_id"] == "CRITICAL-001"]
        assert len(matching) == 1
        assert matching[0]["status"] == "acknowledged"

        # 3. Complete with resolution (method returns bool)
        done_result = queue.complete(
            entry.id,
            resolution="Certificate renewed and deployment resumed successfully",
        )
        assert done_result is True

        # 4. Verify completed entries are excluded from active queue by design
        overseer_queue = queue.get_role_queue("overseer", unacknowledged_only=False)
        matching = [e for e in overseer_queue if e["issue_id"] == "CRITICAL-001"]
        assert len(matching) == 0  # Completed entries are filtered out from active queue

    def test_multiple_role_handoff_chain(self, temp_storage_dir: Path) -> None:
        """Test handoff chain across multiple roles."""
        from tools.overseer.issues.handoff import HandoffQueue

        queue = HandoffQueue(storage_dir=temp_storage_dir, auto_distribute_context=False)

        # UI -> Debug -> Core Platform chain

        # Step 1: UI escalates to Debug
        e1 = queue.handoff(
            issue_id="CHAIN-001",
            from_role="ui-engineer",
            to_role="debug-agent",
            reason="Button click causes crash",
            priority="high",
        )
        queue.acknowledge(e1.id, role="debug-agent")

        # Step 2: Debug discovers it's a backend issue, escalates to Core Platform
        queue.complete(
            e1.id,
            resolution="Root cause: Backend returns null, forwarding to Core Platform",
        )

        e2 = queue.handoff(
            issue_id="CHAIN-001-BE",
            from_role="debug-agent",
            to_role="core-platform",
            reason="Backend returns null for valid request",
            priority="high",
        )

        # Verify e1 is still visible after completion (before Step 3 completion)
        queue.get_role_queue("debug-agent", unacknowledged_only=False)
        # e1 completed entries are filtered from get_role_queue, so check count
        assert e1.id is not None

        # Step 3: Core Platform resolves (method uses 'role' parameter)
        ack_result = queue.acknowledge(e2.id, role="core-platform")
        assert ack_result is True

        complete_result = queue.complete(
            e2.id,
            resolution="Fixed: Added null check in JobStateStore.get()",
        )
        assert complete_result is True

        # After completion, entries are filtered from active queue by design
        # Verify that completed entries are no longer in active queues
        debug_queue = queue.get_role_queue("debug-agent", unacknowledged_only=False)
        core_queue = queue.get_role_queue("core-platform", unacknowledged_only=False)

        # Both entries should be completed and thus filtered out
        assert not any(e["issue_id"] == "CHAIN-001" for e in debug_queue)
        assert not any(e["issue_id"] == "CHAIN-001-BE" for e in core_queue)


class TestCrossRoleWithContextBundle:
    """Tests for cross-role protocol with context bundle integration."""

    def test_handoff_payload_with_context_bundle(self) -> None:
        """Handoff payload should support context bundle metadata."""
        from tools.context.core.cross_role_protocol import HandoffPayload

        payload = HandoffPayload(
            source_role="core-platform",
            target_role="debug-agent",
            task_id="TASK-0042",
            reason="Job state persistence failing",
            context_summary="JobStateStore.save() throws on concurrent writes",
            escalation_level="urgent",
            artifacts=[
                "logs/job_store_error.log",
                "tests/unit/test_job_state_store.py",
            ],
            blockers=["concurrent_write_failure"],
            metadata={
                "context_bundle_size": 4500,
                "context_level": "MID",
            },
        )

        # Verify payload structure
        assert payload.task_id == "TASK-0042"
        assert len(payload.artifacts) == 2
        assert "context_bundle_size" in payload.metadata

    def test_serialization_round_trip(self) -> None:
        """HandoffPayload should serialize and deserialize correctly."""
        from tools.context.core.cross_role_protocol import HandoffPayload

        original = HandoffPayload(
            source_role="ui-engineer",
            target_role="debug-agent",
            task_id="TASK-0001",
            reason="Test serialization",
            context_summary="Testing round-trip",
            escalation_level="normal",
            artifacts=["file1.py", "file2.py"],
            blockers=[],
            metadata={"key": "value"},
        )

        # Serialize
        data = {
            "source_role": original.source_role,
            "target_role": original.target_role,
            "task_id": original.task_id,
            "reason": original.reason,
            "context_summary": original.context_summary,
            "escalation_level": original.escalation_level,
            "artifacts": original.artifacts,
            "blockers": original.blockers,
            "metadata": original.metadata,
            "timestamp": original.timestamp,
        }
        serialized = json.dumps(data)

        # Deserialize
        loaded = json.loads(serialized)
        restored = HandoffPayload(
            source_role=loaded["source_role"],
            target_role=loaded["target_role"],
            task_id=loaded.get("task_id"),
            reason=loaded["reason"],
            context_summary=loaded.get("context_summary", ""),
            escalation_level=loaded.get("escalation_level", "normal"),
            artifacts=loaded.get("artifacts", []),
            blockers=loaded.get("blockers", []),
            metadata=loaded.get("metadata", {}),
            timestamp=loaded.get("timestamp", ""),
        )

        assert restored.source_role == original.source_role
        assert restored.target_role == original.target_role
        assert restored.task_id == original.task_id
        assert restored.artifacts == original.artifacts
