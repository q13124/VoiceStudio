"""
Overseer Tools Package

Provides automation for Overseer governance tasks:
- Ledger parsing and validation
- Gate status tracking
- Handoff management
- Report generation

NOTE: Most overseer modules are currently uncommitted.
This __init__.py makes the package importable to prevent ModuleNotFoundError.
Full imports will be enabled when the modules are committed.
"""

# Try to import from models if it exists
try:
    from .models import (
        AgentIdentity,
        AgentRole,
        AgentState,
        Category,
        Gate,
        GateStatus,
        HandoffRecord,
        LedgerEntry,
        LedgerState,
        Severity,
    )
    _HAS_MODELS = True
except ImportError:
    _HAS_MODELS = False

# Try to import other modules if they exist
try:
    from .ledger_parser import LedgerParser
    _HAS_LEDGER_PARSER = True
except ImportError:
    _HAS_LEDGER_PARSER = False

try:
    from .gate_tracker import GateTracker
    _HAS_GATE_TRACKER = True
except ImportError:
    _HAS_GATE_TRACKER = False

try:
    from .handoff_manager import HandoffManager
    _HAS_HANDOFF_MANAGER = True
except ImportError:
    _HAS_HANDOFF_MANAGER = False

try:
    from .report_engine import ReportEngine
    _HAS_REPORT_ENGINE = True
except ImportError:
    _HAS_REPORT_ENGINE = False

__version__ = "1.0.0"

# Only export what successfully imported
if _HAS_MODELS:
    __all__ = [
        "AgentIdentity",
        "AgentRole",
        "AgentState",
        "Category",
        "Gate",
        "GateStatus",
        "HandoffRecord",
        "LedgerEntry",
        "LedgerState",
        "Severity",
    ]
    if _HAS_LEDGER_PARSER:
        __all__.append("LedgerParser")
    if _HAS_GATE_TRACKER:
        __all__.append("GateTracker")
    if _HAS_HANDOFF_MANAGER:
        __all__.append("HandoffManager")
    if _HAS_REPORT_ENGINE:
        __all__.append("ReportEngine")
else:
    __all__ = []

