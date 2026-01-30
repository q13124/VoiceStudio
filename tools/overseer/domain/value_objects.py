"""Domain value objects for debug workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class RootCauseCategory(str, Enum):
    """Categories of root causes."""
    
    CODE_LOGIC = "code_logic"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    RACE_CONDITION = "race_condition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MODEL_DRIFT = "model_drift"
    INTEGRATION_FAILURE = "integration_failure"
    DATA_CORRUPTION = "data_corruption"
    ENVIRONMENT = "environment"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CodeLocation:
    """Immutable code location reference."""
    
    file: str
    line: Optional[int] = None
    function: Optional[str] = None
    module: Optional[str] = None
    
    def __str__(self) -> str:
        if self.line and self.function:
            return f"{self.file}:{self.line} in {self.function}"
        elif self.line:
            return f"{self.file}:{self.line}"
        else:
            return self.file


@dataclass(frozen=True)
class RootCause:
    """Immutable root cause identification."""
    
    category: RootCauseCategory
    location: CodeLocation
    description: str
    evidence_paths: List[str]
    confidence: float  # 0.0 - 1.0
    technical_details: Optional[str] = None
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass(frozen=True)
class FileChange:
    """Immutable record of file modification."""
    
    path: str
    content: str
    change_type: str  # "modify", "create", "delete"
    rationale: str


@dataclass(frozen=True)
class Fix:
    """Immutable fix proposal."""
    
    issue_id: str
    file_changes: List[FileChange]
    rationale: str
    estimated_risk: str  # "low", "medium", "high", "critical"


@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result."""
    
    passed: bool
    build_success: bool
    tests_passed: int
    tests_failed: int
    gate_status: str
    errors: List[str]
    proof_artifacts: List[str]
    executed_at: datetime
    
    @property
    def is_valid(self) -> bool:
        return self.passed and self.build_success and self.tests_failed == 0


@dataclass(frozen=True)
class Resolution:
    """Immutable resolution record."""
    
    fix: Fix
    validation: ValidationResult
    applied_at: datetime
    applied_by: str
    pr_link: Optional[str] = None
    
    @classmethod
    def from_fix(cls, fix: Fix, validation: ValidationResult, applied_by: str = "debug-agent") -> Resolution:
        return cls(
            fix=fix,
            validation=validation,
            applied_at=datetime.now(),
            applied_by=applied_by,
        )


@dataclass(frozen=True)
class ResolutionLog:
    """
    Immutable record of bug resolution (value object).
    
    Complete structured summary per Debug Role specification.
    """
    
    issue_id: str
    resolved_at: datetime
    resolved_by: str
    root_cause: str
    fix_rationale: str
    discovery_process: str
    originator_analysis: str
    prevention_recommendations: List[str]
    validation_results: ValidationResult
    proof_artifacts: List[str]
    
    def to_markdown(self) -> str:
        """Format as Resolution Summary markdown per specification."""
        lines = [
            f"# Resolution Summary: {self.issue_id}",
            "",
            f"**Date:** {self.resolved_at.strftime('%Y-%m-%d')}",
            f"**Resolved By:** {self.resolved_by}",
            "",
            "---",
            "",
            "## 1. Cause of Bug",
            "",
            self.root_cause,
            "",
            "---",
            "",
            "## 2. Why Fix Works",
            "",
            self.fix_rationale,
            "",
            "---",
            "",
            "## 3. Discovery Process",
            "",
            self.discovery_process,
            "",
            "---",
            "",
            "## 4. Originator Analysis",
            "",
            self.originator_analysis,
            "",
            "---",
            "",
            "## 5. Prevention Recommendations",
            "",
        ]
        lines.extend([f"- {rec}" for rec in self.prevention_recommendations])
        lines.extend([
            "",
            "---",
            "",
            "## 6. Validation Results",
            "",
            f"- Build: {'SUCCESS' if self.validation_results.build_success else 'FAILURE'}",
            f"- Tests: {self.validation_results.tests_passed}/{self.validation_results.tests_passed + self.validation_results.tests_failed} passed",
            f"- Gate Status: {self.validation_results.gate_status}",
            "",
            "**Proof Artifacts**:",
        ])
        lines.extend([f"- `{artifact}`" for artifact in self.proof_artifacts])
        lines.append("")
        
        return "\n".join(lines)


@dataclass
class Hypothesis:
    """Investigation hypothesis to test."""
    
    description: str
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    tested: bool = False
    result: Optional[str] = None  # "confirmed", "refuted", "inconclusive"


@dataclass
class Evidence:
    """Evidence collected during investigation."""
    
    description: str
    source: str  # "log", "test", "code_review", "reproduction", etc.
    confidence: float  # 0.0 - 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    artifacts: List[str] = field(default_factory=list)
