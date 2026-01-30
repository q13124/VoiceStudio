"""Tests for Overseer domain services."""

import pytest
from datetime import datetime

from tools.overseer.domain.entities import (
    IssueReport,
    IssueStatus,
    BugInvestigationSession,
)
from tools.overseer.domain.value_objects import (
    RootCause,
    RootCauseCategory,
    CodeLocation,
    Fix,
    FileChange,
    Hypothesis,
    Evidence,
)
from tools.overseer.domain.services import (
    DebugWorkflow,
    RootCauseAnalyzer,
)


class TestDebugWorkflow:
    """Tests for DebugWorkflow domain service."""
    
    def test_investigate_creates_session(self):
        """investigate() creates BugInvestigationSession."""
        workflow = DebugWorkflow()
        
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.NEW,
            affected_components=["backend"],
            symptoms="Error",
        )
        
        session = workflow.investigate(issue)
        
        assert session.issue_id == "ISS-001"
        assert session.current_state.value == "investigating"
    
    def test_validate_fix_requires_root_cause(self):
        """validate_fix() rejects fixes for issues without root cause."""
        workflow = DebugWorkflow()
        
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.ACKNOWLEDGED,
            affected_components=["backend/api"],
            symptoms="Error",
        )
        
        fix = Fix(
            issue_id="ISS-001",
            file_changes=[FileChange(path="backend/api/test.py", content="fixed", change_type="modify", rationale="")],
            rationale="Fix",
            estimated_risk="low",
        )
        
        result = workflow.validate_fix(issue, fix)
        
        assert not result.passed
        assert "root cause not identified" in result.errors[0]
    
    def test_validate_fix_checks_affected_components(self):
        """validate_fix() ensures file changes target affected components."""
        workflow = DebugWorkflow()
        
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.ROOT_CAUSE_FOUND,
            affected_components=["backend/api"],
            symptoms="Error",
            root_cause=RootCause(
                category=RootCauseCategory.CODE_LOGIC,
                location=CodeLocation(file="backend/api/voice.py"),
                description="Bug",
                evidence_paths=[],
                confidence=0.9,
            ),
        )
        
        # Fix targets unrelated file
        fix = Fix(
            issue_id="ISS-001",
            file_changes=[FileChange(path="frontend/ui/test.xaml", content="fixed", change_type="modify", rationale="")],
            rationale="Fix",
            estimated_risk="low",
        )
        
        result = workflow.validate_fix(issue, fix)
        
        assert not result.passed
        assert any("do not target affected components" in e for e in result.errors)
    
    def test_validate_fix_checks_risk_assessment(self):
        """validate_fix() flags underestimated risk for large changes."""
        workflow = DebugWorkflow()
        
        issue = IssueReport(
            id="ISS-001",
            correlation_id="corr-123",
            severity="high",
            status=IssueStatus.ROOT_CAUSE_FOUND,
            affected_components=["backend"],
            symptoms="Error",
            root_cause=RootCause(
                category=RootCauseCategory.CODE_LOGIC,
                location=CodeLocation(file="backend/test.py"),
                description="Bug",
                evidence_paths=[],
                confidence=0.9,
            ),
        )
        
        # Large change (6 files) marked as low risk
        fix = Fix(
            issue_id="ISS-001",
            file_changes=[
                FileChange(path=f"backend/file{i}.py", content="fixed", change_type="modify", rationale="")
                for i in range(6)
            ],
            rationale="Fix",
            estimated_risk="low",  # Underestimated
        )
        
        result = workflow.validate_fix(issue, fix)
        
        assert not result.passed
        assert any("underestimated" in e.lower() for e in result.errors)


class TestRootCauseAnalyzer:
    """Tests for RootCauseAnalyzer domain service."""
    
    def test_analyze_returns_none_without_evidence(self):
        """analyze() returns None if no evidence collected."""
        analyzer = RootCauseAnalyzer()
        
        session = BugInvestigationSession.create("ISS-001")
        
        result = analyzer.analyze(session)
        
        assert result is None
    
    def test_analyze_scores_hypotheses_by_evidence(self):
        """analyze() scores hypotheses based on supporting/contradicting evidence."""
        analyzer = RootCauseAnalyzer()
        
        session = BugInvestigationSession.create("ISS-001")
        
        # Hypothesis with strong support
        hyp1 = Hypothesis(
            description="Race condition in JobStateStore",
            supporting_evidence=["log1.txt", "log2.txt", "log3.txt"],
            contradicting_evidence=[],
        )
        session.add_hypothesis(hyp1)
        
        # Add evidence
        session.record_evidence(Evidence(description="backend/services/JobStateStore.py:45", source="log", confidence=0.9))
        
        result = analyzer.analyze(session)
        
        assert result is not None
        assert result.description == hyp1.description
        assert result.confidence >= 0.7
    
    def test_analyze_returns_none_for_low_confidence(self):
        """analyze() returns None if best hypothesis has <0.7 confidence."""
        analyzer = RootCauseAnalyzer()
        
        session = BugInvestigationSession.create("ISS-001")
        
        # Hypothesis with weak support
        hyp = Hypothesis(
            description="Maybe config issue",
            supporting_evidence=["one_log.txt"],
            contradicting_evidence=["other_log.txt", "test_result.txt"],
        )
        session.add_hypothesis(hyp)
        session.record_evidence(Evidence(description="Evidence", source="log", confidence=0.5))
        
        result = analyzer.analyze(session)
        
        # Low confidence, should return None
        assert result is None or result.confidence < 0.7
    
    def test_categorize_identifies_race_conditions(self):
        """_categorize() identifies race conditions from keywords."""
        analyzer = RootCauseAnalyzer()
        
        category = analyzer._categorize("Race condition during concurrent access to shared state")
        
        assert category == RootCauseCategory.RACE_CONDITION
    
    def test_categorize_identifies_dependency_issues(self):
        """_categorize() identifies dependency issues from keywords."""
        analyzer = RootCauseAnalyzer()
        
        category = analyzer._categorize("Incompatible library version causes import failure")
        
        assert category == RootCauseCategory.DEPENDENCY
