"""Tests for Overseer domain entities."""

from datetime import datetime

import pytest

from tools.overseer.domain.entities import (
    BugInvestigationSession,
    InvestigationState,
    IssueReport,
    IssueStatus,
    StateTransition,
)
from tools.overseer.domain.value_objects import (
    CodeLocation,
    FileChange,
    Fix,
    Resolution,
    RootCause,
    RootCauseCategory,
    ValidationResult,
)


class TestIssueReport:
    """Tests for IssueReport entity."""

    def test_can_resolve_requires_root_cause(self):
        """Issue can only be resolved if root cause identified."""
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.ACKNOWLEDGED,
            affected_components=["backend/api"],
            symptoms="Route returns 500",
        )

        # Without root cause, cannot resolve
        assert not issue.can_resolve()

        # With root cause, can resolve
        issue.root_cause = RootCause(
            category=RootCauseCategory.CODE_LOGIC,
            location=CodeLocation(file="backend/api/routes/voice.py", line=123),
            description="Null pointer exception",
            evidence_paths=["backend.log"],
            confidence=0.95,
        )
        assert issue.can_resolve()

    def test_apply_resolution_updates_status(self):
        """Applying resolution updates status and records transition."""
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.ROOT_CAUSE_FOUND,
            affected_components=["backend"],
            symptoms="Error",
            root_cause=RootCause(
                category=RootCauseCategory.CODE_LOGIC,
                location=CodeLocation(file="test.py"),
                description="Bug",
                evidence_paths=[],
                confidence=0.9,
            ),
        )

        resolution = Resolution(
            fix=Fix(
                issue_id="ISS-001",
                file_changes=[FileChange(path="test.py", content="fixed", change_type="modify", rationale="Fix bug")],
                rationale="Fixed null check",
                estimated_risk="low",
            ),
            validation=ValidationResult(
                passed=True,
                build_success=True,
                tests_passed=10,
                tests_failed=0,
                gate_status="GREEN",
                errors=[],
                proof_artifacts=["proof.json"],
                executed_at=datetime.now(),
            ),
            applied_at=datetime.now(),
            applied_by="debug-agent",
        )

        issue.apply_resolution(resolution)

        assert issue.status == IssueStatus.RESOLVED
        assert issue.resolution is not None
        assert len(issue.state_history) > 0

    def test_cannot_resolve_without_root_cause(self):
        """Cannot apply resolution without root cause."""
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.ACKNOWLEDGED,
            affected_components=["backend"],
            symptoms="Error",
        )

        resolution = Resolution(
            fix=Fix(issue_id="ISS-001", file_changes=[], rationale="", estimated_risk="low"),
            validation=ValidationResult(True, True, 0, 0, "GREEN", [], [], datetime.now()),
            applied_at=datetime.now(),
            applied_by="test",
        )

        with pytest.raises(ValueError, match="root cause not identified"):
            issue.apply_resolution(resolution)

    def test_escalate_updates_status_and_history(self):
        """Escalating issue updates status and records transition."""
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.INVESTIGATING,
            affected_components=["storage"],
            symptoms="Data corruption",
        )

        issue.escalate(to_role="core-platform", reason="Requires storage expertise")

        assert issue.status == IssueStatus.ESCALATED
        assert len(issue.state_history) == 1
        assert "core-platform" in issue.state_history[0].reason


class TestBugInvestigationSession:
    """Tests for BugInvestigationSession entity."""

    def test_create_generates_unique_session_id(self):
        """Creating session generates unique ID."""
        session1 = BugInvestigationSession.create("ISS-001")
        session2 = BugInvestigationSession.create("ISS-002")

        assert session1.session_id != session2.session_id
        assert session1.session_id.startswith("INV-")

    def test_add_hypothesis_transitions_state(self):
        """Adding hypothesis transitions from CREATED to INVESTIGATING."""
        session = BugInvestigationSession.create("ISS-001")
        assert session.current_state == InvestigationState.CREATED

        from tools.overseer.domain.value_objects import Hypothesis
        session.add_hypothesis(Hypothesis(description="Race condition suspected"))

        assert session.current_state == InvestigationState.INVESTIGATING
        assert len(session.hypotheses) == 1

    def test_identify_root_cause_transitions_state(self):
        """Identifying root cause transitions to ROOT_CAUSE_IDENTIFIED."""
        session = BugInvestigationSession.create("ISS-001")

        root_cause = RootCause(
            category=RootCauseCategory.RACE_CONDITION,
            location=CodeLocation(file="test.py"),
            description="Concurrent access without lock",
            evidence_paths=["log.txt"],
            confidence=0.9,
        )

        session.identify_root_cause(root_cause)

        assert session.current_state == InvestigationState.ROOT_CAUSE_IDENTIFIED
        assert session.root_cause == root_cause

    def test_conclude_requires_root_cause(self):
        """Cannot conclude investigation without root cause."""
        session = BugInvestigationSession.create("ISS-001")

        with pytest.raises(ValueError, match="root cause not identified"):
            session.conclude()

    def test_abandon_adds_evidence_and_marks_state(self):
        """Abandoning investigation records reason and updates state."""
        session = BugInvestigationSession.create("ISS-001")

        session.abandon(reason="Requires System Architect involvement")

        assert session.current_state == InvestigationState.ABANDONED
        assert session.completed_at is not None
        assert len(session.evidence) == 1
        assert "abandoned" in session.evidence[0].description.lower()


class TestStateTransition:
    """Tests for StateTransition."""

    def test_records_transition(self):
        """State transition records from/to status."""
        transition = StateTransition(
            from_status="new",
            to_status="acknowledged",
            at=datetime.now(),
            by="debug-agent",
            reason="Investigation started",
        )

        assert transition.from_status == "new"
        assert transition.to_status == "acknowledged"
        assert transition.by == "debug-agent"
