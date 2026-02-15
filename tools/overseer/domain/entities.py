"""Domain entities for debug workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from tools.overseer.domain.value_objects import Evidence, Hypothesis, Resolution, RootCause


class InvestigationState(str, Enum):
    """State of bug investigation session."""

    CREATED = "created"
    INVESTIGATING = "investigating"
    HYPOTHESIS_TESTING = "hypothesis_testing"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    FIX_PROPOSED = "fix_proposed"
    VALIDATING = "validating"
    CONCLUDED = "concluded"
    ABANDONED = "abandoned"


class IssueStatus(str, Enum):
    """Status of issue report."""

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    ROOT_CAUSE_FOUND = "root_cause_found"
    FIX_APPLIED = "fix_applied"
    VALIDATING = "validating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


@dataclass
class StateTransition:
    """Record of status change."""

    from_status: str
    to_status: str
    at: datetime
    by: str
    reason: str | None = None


@dataclass
class IssueReport:
    """
    Domain entity representing a bug investigation.

    Encapsulates business rules for issue lifecycle:
    - Can only resolve if root cause identified
    - State transitions must be valid
    - Resolution requires validation
    """

    id: str
    correlation_id: str
    severity: str
    status: IssueStatus
    affected_components: list[str]
    symptoms: str
    root_cause: RootCause | None = None
    resolution: Resolution | None = None
    state_history: list[StateTransition] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def can_resolve(self) -> bool:
        """Business rule: can only resolve if root cause identified."""
        return (
            self.root_cause is not None
            and self.status != IssueStatus.RESOLVED
            and self.status != IssueStatus.CLOSED
        )

    def apply_resolution(self, resolution: Resolution) -> None:
        """Apply resolution and update status."""
        if not self.can_resolve():
            raise ValueError(f"Cannot resolve issue {self.id}: root cause not identified or already resolved")

        self.resolution = resolution
        self.status = IssueStatus.RESOLVED
        self.updated_at = datetime.now()
        self.state_history.append(
            StateTransition(
                from_status=self.status.value,
                to_status=IssueStatus.RESOLVED.value,
                at=datetime.now(),
                by="system",
                reason="Resolution applied",
            )
        )

    def escalate(self, to_role: str, reason: str) -> None:
        """Escalate issue to another role."""
        old_status = self.status
        self.status = IssueStatus.ESCALATED
        self.updated_at = datetime.now()
        self.state_history.append(
            StateTransition(
                from_status=old_status.value,
                to_status=IssueStatus.ESCALATED.value,
                at=datetime.now(),
                by="debug-agent",
                reason=f"Escalated to {to_role}: {reason}",
            )
        )


@dataclass
class BugInvestigationSession:
    """
    Domain entity tracking investigation workflow.

    Manages investigation state and evidence collection.
    """

    session_id: str
    issue_id: str
    started_at: datetime
    investigator: str
    hypotheses: list[Hypothesis] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    current_state: InvestigationState = InvestigationState.CREATED
    completed_at: datetime | None = None
    root_cause: RootCause | None = None

    @classmethod
    def create(cls, issue_id: str, investigator: str = "debug-agent") -> BugInvestigationSession:
        """Create new investigation session."""
        import uuid
        return cls(
            session_id=f"INV-{uuid.uuid4().hex[:8]}",
            issue_id=issue_id,
            started_at=datetime.now(),
            investigator=investigator,
        )

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Add hypothesis to test during investigation."""
        self.hypotheses.append(hypothesis)
        if self.current_state == InvestigationState.CREATED:
            self.current_state = InvestigationState.INVESTIGATING

    def record_evidence(self, evidence: Evidence) -> None:
        """Record evidence for/against hypotheses."""
        self.evidence.append(evidence)
        if self.current_state == InvestigationState.INVESTIGATING:
            self.current_state = InvestigationState.HYPOTHESIS_TESTING

    def identify_root_cause(self, root_cause: RootCause) -> None:
        """Conclude investigation with identified root cause."""
        self.root_cause = root_cause
        self.current_state = InvestigationState.ROOT_CAUSE_IDENTIFIED

    def conclude(self) -> None:
        """Mark investigation as concluded."""
        if self.root_cause is None:
            raise ValueError("Cannot conclude: root cause not identified")
        self.current_state = InvestigationState.CONCLUDED
        self.completed_at = datetime.now()

    def abandon(self, reason: str) -> None:
        """Abandon investigation (escalate or defer)."""
        self.current_state = InvestigationState.ABANDONED
        self.completed_at = datetime.now()
        self.evidence.append(
            Evidence(
                description=f"Investigation abandoned: {reason}",
                source="system",
                confidence=1.0,
            )
        )
