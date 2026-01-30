"""
Data models for Overseer tools.

Uses dataclasses for simplicity (no pydantic dependency required).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class LedgerState(str, Enum):
    """Valid ledger entry states."""

    OPEN = "OPEN"
    TRIAGE = "TRIAGE"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    FIXED_PENDING_PROOF = "FIXED_PENDING_PROOF"
    DONE = "DONE"
    WONT_FIX = "WONT_FIX"


class Severity(str, Enum):
    """Severity levels for ledger entries."""

    S0_BLOCKER = "S0 Blocker"
    S1_CRITICAL = "S1 Critical"
    S2_MAJOR = "S2 Major"
    S3_MINOR = "S3 Minor"
    S4_CHORE = "S4 Chore"

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """Parse severity from string, handling variations."""
        value_lower = value.lower().strip()
        if "s0" in value_lower or "blocker" in value_lower:
            return cls.S0_BLOCKER
        elif "s1" in value_lower or "critical" in value_lower:
            return cls.S1_CRITICAL
        elif "s2" in value_lower or "major" in value_lower:
            return cls.S2_MAJOR
        elif "s3" in value_lower or "minor" in value_lower:
            return cls.S3_MINOR
        elif "s4" in value_lower or "chore" in value_lower:
            return cls.S4_CHORE
        else:
            return cls.S2_MAJOR  # Default


class Gate(str, Enum):
    """Gate identifiers (A-H)."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"

    @classmethod
    def from_string(cls, value: str) -> Optional["Gate"]:
        """Parse gate from string."""
        value_upper = value.strip().upper()
        if value_upper in [g.value for g in cls]:
            return cls(value_upper)
        return None


class Category(str, Enum):
    """Valid categories for ledger entries."""

    BUILD = "BUILD"
    BOOT = "BOOT"
    UI = "UI"
    RUNTIME = "RUNTIME"
    ENGINE = "ENGINE"
    AUDIO = "AUDIO"
    STORAGE = "STORAGE"
    PLUGINS = "PLUGINS"
    PACKAGING = "PACKAGING"
    PERF = "PERF"
    SECURITY = "SECURITY"
    DOCS = "DOCS"
    RULES = "RULES"
    TEST = "TEST"  # Found in ledger

    @classmethod
    def from_string(cls, value: str) -> Optional["Category"]:
        """Parse category from string."""
        value_upper = value.strip().upper()
        try:
            return cls(value_upper)
        except ValueError:
            return None


@dataclass
class LedgerEntry:
    """Represents a single ledger entry."""

    id: str
    state: LedgerState
    severity: Severity
    gate: Gate
    owner_role: str
    categories: List[Category]
    title: str
    summary: Optional[str] = None
    reproduction: Optional[str] = None
    proof_run: Optional[str] = None
    evidence: Optional[str] = None
    introduced: Optional[datetime] = None
    last_verified: Optional[datetime] = None
    reviewer_role: Optional[str] = None
    raw_text: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """Check if entry has all required fields."""
        return all(
            [
                self.id,
                self.state,
                self.severity,
                self.gate,
                self.owner_role,
                self.categories,
                self.title,
            ]
        )

    @property
    def has_proof(self) -> bool:
        """Check if entry has proof run documented."""
        return bool(self.proof_run)

    @property
    def is_done(self) -> bool:
        """Check if entry is in DONE state."""
        return self.state == LedgerState.DONE


@dataclass
class GateStatus:
    """Status of a single gate."""

    gate: Gate
    total_entries: int = 0
    done_entries: int = 0
    open_entries: int = 0
    blocked_entries: int = 0
    in_progress_entries: int = 0
    entries: List[LedgerEntry] = field(default_factory=list)

    @property
    def completion_percent(self) -> float:
        """Calculate completion percentage."""
        if self.total_entries == 0:
            return 100.0
        return (self.done_entries / self.total_entries) * 100

    @property
    def is_green(self) -> bool:
        """Check if gate is fully complete (green)."""
        return self.total_entries > 0 and self.done_entries == self.total_entries

    @property
    def is_blocked(self) -> bool:
        """Check if gate has blockers."""
        return self.blocked_entries > 0

    @property
    def status_symbol(self) -> str:
        """Get status symbol for display (ASCII-safe for Windows console)."""
        if self.is_green:
            return "[PASS]"
        elif self.is_blocked:
            return "[BLOCK]"
        elif self.in_progress_entries > 0:
            return "[PROG]"
        elif self.open_entries > 0:
            return "[OPEN]"
        else:
            return "[N/A]"  # No entries


@dataclass
class HandoffRecord:
    """Represents a handoff file record."""

    ledger_id: str
    gate: Optional[Gate] = None
    owner_role: Optional[str] = None
    signoff_role: Optional[str] = None
    goal: Optional[str] = None
    outcome: Optional[str] = None
    files_changed: List[str] = field(default_factory=list)
    proof_commands: Optional[str] = None
    proof_output: Optional[str] = None
    file_path: Optional[str] = None
    status: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Check if handoff has minimum required fields."""
        return bool(self.ledger_id and self.gate)


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)


@dataclass
class LedgerSummary:
    """Summary statistics for the ledger."""

    total_entries: int = 0
    done_entries: int = 0
    open_entries: int = 0
    in_progress_entries: int = 0
    blocked_entries: int = 0
    by_severity: dict = field(default_factory=dict)
    by_gate: dict = field(default_factory=dict)
    by_category: dict = field(default_factory=dict)
    missing_proof: List[str] = field(default_factory=list)
    gate_statuses: List[GateStatus] = field(default_factory=list)

    @property
    def completion_percent(self) -> float:
        """Overall completion percentage."""
        if self.total_entries == 0:
            return 100.0
        return (self.done_entries / self.total_entries) * 100


# Agent governance models (re-export for Overseer tools)
from .agent.identity import AgentIdentity, AgentRole, AgentState  # noqa: E402,F401
