"""
Test that all Overseer modules can be imported.

Prevents ModuleNotFoundError from breaking CLI commands.
These tests act as smoke tests for the overseer package structure.
"""

import sys
from pathlib import Path

# Add project root to path BEFORE any tools imports to avoid shadowing
# by the test directory structure (tests/unit/tools/overseer/)
_project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def test_overseer_package_imports():
    """Test basic overseer package imports."""
    from tools.overseer import (
        Gate,
        GateStatus,
        LedgerState,
        Severity,
    )

    assert LedgerState.DONE is not None
    assert Severity.S0_BLOCKER is not None
    assert Gate.A is not None
    # GateStatus is a dataclass with is_green property, not a constant
    status = GateStatus(gate=Gate.A, total_entries=1, done_entries=1)
    assert status.is_green is True


def test_overseer_agent_imports():
    """Test agent governance imports."""
    from tools.overseer.agent.identity import AgentIdentity, AgentRole, AgentState

    assert AgentRole.OVERSEER is not None
    assert AgentRole.DEBUGGER is not None
    assert AgentState.RUNNING is not None  # API uses RUNNING, not ACTIVE

    # Verify we can create an identity using the class factory
    identity = AgentIdentity.create(role=AgentRole.OVERSEER, user_id="test")
    assert identity.state == AgentState.CREATED  # Initial state is CREATED


def test_overseer_cli_imports():
    """Test CLI module imports."""
    from tools.overseer.cli import main

    assert main.main is not None
    assert callable(main.main)


def test_overseer_issues_imports():
    """Test issues system imports."""
    from tools.overseer.issues import (
        Issue,
        IssuePriority,
        IssueSeverity,
        IssueStatus,
    )

    # Verify enum values exist (per actual API)
    assert IssuePriority.HIGH is not None
    assert IssueSeverity.CRITICAL is not None
    assert IssueStatus.NEW is not None  # API uses NEW, not OPEN
    assert Issue is not None


def test_overseer_agent_package_exists():
    """Verify agent package has __init__.py (prevents regression)."""
    project_root = Path(__file__).parents[4]
    agent_init = project_root / "tools" / "overseer" / "agent" / "__init__.py"

    assert agent_init.exists(), "tools/overseer/agent/__init__.py missing (would break imports!)"


def test_critical_packages_have_init():
    """Verify package structure for critical modules."""
    project_root = Path(__file__).parents[4]

    critical_packages = [
        "tools/overseer",
        "tools/overseer/agent",
        "tools/overseer/issues",
        "tools/overseer/cli",
        "tools/context",
        "tools/context/sources",
        "tools/onboarding",
        "tools/onboarding/core",
    ]

    missing = []
    for pkg in critical_packages:
        init_file = project_root / pkg / "__init__.py"
        if not init_file.exists():
            missing.append(pkg)

    assert not missing, f"Missing __init__.py in: {', '.join(missing)}"


def test_agent_identity_module():
    """Test agent.identity module can be imported (regression test for missing __init__.py)."""
    from tools.overseer.agent.identity import AgentRole, AgentState

    # Verify all roles are defined (per actual API)
    assert AgentRole.OVERSEER
    assert AgentRole.REVIEWER
    assert AgentRole.BUILDER
    assert AgentRole.CODER
    assert AgentRole.DEBUGGER
    assert AgentRole.TESTER
    assert AgentRole.SUPPORT

    # Verify all states are defined (per actual API)
    assert AgentState.CREATED
    assert AgentState.RUNNING
    assert AgentState.PAUSED
    assert AgentState.AWAITING_APPROVAL
    assert AgentState.COMPLETED
    assert AgentState.QUARANTINED
    assert AgentState.TERMINATED


def test_agent_role_mapping():
    """Test role mapping functions."""
    from tools.overseer.agent.identity import AgentRole
    from tools.overseer.agent.role_mapping import role_to_agent_role

    # Test all VoiceStudio roles map correctly
    assert role_to_agent_role(0) == AgentRole.OVERSEER
    assert role_to_agent_role(1) == AgentRole.REVIEWER
    assert role_to_agent_role(2) == AgentRole.BUILDER
    assert role_to_agent_role(7) == AgentRole.DEBUGGER
    assert role_to_agent_role("debug-agent") == AgentRole.DEBUGGER
    assert role_to_agent_role("overseer") == AgentRole.OVERSEER
