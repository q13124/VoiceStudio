"""Domain services for debug workflows."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import List, Optional

from tools.overseer.domain.entities import (
    BugInvestigationSession,
    InvestigationState,
    IssueReport,
    IssueStatus,
)
from tools.overseer.domain.value_objects import (
    CodeLocation,
    Evidence,
    Fix,
    Hypothesis,
    Resolution,
    RootCause,
    RootCauseCategory,
    ValidationResult,
)


class DebugWorkflow:
    """
    Domain service orchestrating debug investigation process.
    
    Implements business logic for systematic investigation.
    """
    
    def investigate(self, issue: IssueReport) -> BugInvestigationSession:
        """Start investigation workflow for issue."""
        session = BugInvestigationSession.create(
            issue_id=issue.id,
            investigator="debug-agent",
        )
        session.current_state = InvestigationState.INVESTIGATING
        return session
    
    def validate_fix(self, issue: IssueReport, proposed_fix: Fix) -> ValidationResult:
        """
        Validate proposed fix against business rules.
        
        Rules:
        - Fix must address root cause
        - File changes must be in affected components
        - Risk level must match change scope
        """
        errors = []
        
        if not issue.root_cause:
            errors.append("Cannot validate fix: root cause not identified")
        
        if not proposed_fix.file_changes:
            errors.append("Fix has no file changes")
        
        # Validate file changes target affected components
        affected_paths = set(issue.affected_components)
        changed_paths = {fc.path for fc in proposed_fix.file_changes}
        
        if not any(self._path_matches(changed, affected) for changed in changed_paths for affected in affected_paths):
            errors.append(f"File changes do not target affected components: {changed_paths} vs {affected_paths}")
        
        # Risk assessment
        if len(proposed_fix.file_changes) > 5 and proposed_fix.estimated_risk == "low":
            errors.append("Risk underestimated: >5 files changed but marked as low risk")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            passed=is_valid,
            build_success=is_valid,  # Actual build check happens in use case
            tests_passed=0,  # Actual test execution happens in use case
            tests_failed=0 if is_valid else 1,
            gate_status="unknown",
            errors=errors,
            proof_artifacts=[],
            executed_at=datetime.now(),
        )
    
    def _path_matches(self, changed: str, affected: str) -> bool:
        """Check if changed path relates to affected component."""
        # Simple containment check (can be enhanced with glob matching)
        return affected in changed or changed.startswith(affected)


class RootCauseAnalyzer:
    """
    Domain service for root cause analysis.
    
    Analyzes evidence to identify fundamental cause.
    """
    
    def analyze(self, session: BugInvestigationSession) -> Optional[RootCause]:
        """
        Analyze session evidence to identify root cause.
        
        Returns root cause if confidence >= 0.7, otherwise None.
        """
        if not session.evidence:
            return None
        
        # Score hypotheses by evidence
        scored = []
        for hyp in session.hypotheses:
            support = len(hyp.supporting_evidence)
            contradict = len(hyp.contradicting_evidence)
            score = (support - contradict) / (support + contradict + 1)
            scored.append((score, hyp))
        
        if not scored:
            return None
        
        # Best hypothesis
        best_score, best_hyp = max(scored, key=lambda x: x[0])
        
        if best_score < 0.7:
            return None  # Insufficient confidence
        
        # Extract code location from evidence
        location = self._extract_location(session.evidence)
        
        # Categorize root cause
        category = self._categorize(best_hyp.description)
        
        evidence_paths = [e.artifacts[0] for e in session.evidence if e.artifacts]
        
        return RootCause(
            category=category,
            location=location,
            description=best_hyp.description,
            evidence_paths=evidence_paths,
            confidence=best_score,
        )
    
    def _extract_location(self, evidence: List[Evidence]) -> CodeLocation:
        """Extract code location from evidence."""
        # Look for file/line references in evidence
        for e in evidence:
            if ":" in e.description and "/" in e.description:
                # Heuristic: "backend/api/routes/voice.py:123"
                parts = e.description.split()
                for part in parts:
                    if ":" in part and "/" in part:
                        file_line = part.split(":")
                        if len(file_line) == 2:
                            try:
                                return CodeLocation(file=file_line[0], line=int(file_line[1]))
                            except ValueError:
                                pass
        
        # Fallback: unknown location
        return CodeLocation(file="unknown")
    
    def _categorize(self, description: str) -> RootCauseCategory:
        """Categorize root cause by description keywords."""
        desc_lower = description.lower()
        
        if any(kw in desc_lower for kw in ["race", "concurr", "timing", "async"]):
            return RootCauseCategory.RACE_CONDITION
        elif any(kw in desc_lower for kw in ["config", "setting", "environment"]):
            return RootCauseCategory.CONFIGURATION
        elif any(kw in desc_lower for kw in ["depend", "library", "version", "compat"]):
            return RootCauseCategory.DEPENDENCY
        elif any(kw in desc_lower for kw in ["memory", "cpu", "gpu", "disk", "resource"]):
            return RootCauseCategory.RESOURCE_EXHAUSTION
        elif any(kw in desc_lower for kw in ["model", "inference", "quality", "drift"]):
            return RootCauseCategory.MODEL_DRIFT
        elif any(kw in desc_lower for kw in ["api", "endpoint", "integration", "ipc"]):
            return RootCauseCategory.INTEGRATION_FAILURE
        elif any(kw in desc_lower for kw in ["corrupt", "invalid data", "parse"]):
            return RootCauseCategory.DATA_CORRUPTION
        else:
            return RootCauseCategory.CODE_LOGIC
