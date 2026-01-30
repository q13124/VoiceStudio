"""
Test that all Overseer modules can be imported.

Prevents ModuleNotFoundError from breaking CLI commands.
These tests act as smoke tests for the overseer package structure.
"""

from pathlib import Path


def test_overseer_package_imports():
    """Test basic overseer package imports."""
    from tools.overseer import (
        LedgerEntry,
        LedgerState,
        Severity,
        Gate,
        GateStatus,
    )
    
    assert LedgerState.DONE is not None
    assert Severity.S0_BLOCKER is not None
    assert Gate.A is not None
    assert GateStatus.GREEN is not None


def test_overseer_agent_imports():
    """Test agent governance imports."""
    from tools.overseer.models import AgentIdentity, AgentRole, AgentState
    
    assert AgentRole.OVERSEER is not None
    assert AgentRole.DEBUGGER is not None
    assert AgentState.ACTIVE is not None
    
    # Verify we can create an identity
    identity = AgentIdentity(role=AgentRole.OVERSEER, role_id="0")
    assert identity.is_active() is False  # Should be INITIALIZING


def test_overseer_cli_imports():
    """Test CLI module imports."""
    from tools.overseer.cli import main
    
    assert main.main is not None
    assert callable(main.main)


def test_overseer_issues_imports():
    """Test issues system imports."""
    from tools.overseer.issues import (
        IssueStore,
        record_issue,
        query_issues,
    )
    from tools.overseer.issues.store import IssueStore as DirectIssueStore
    
    assert IssueStore is not None
    assert record_issue is not None
    assert query_issues is not None
    assert DirectIssueStore is not None


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
    from tools.overseer.agent.identity import AgentRole, AgentIdentity, AgentState
    
    # Verify all roles are defined
    assert AgentRole.OVERSEER
    assert AgentRole.REVIEWER
    assert AgentRole.BUILDER
    assert AgentRole.CODER
    assert AgentRole.DEBUGGER
    assert AgentRole.UNKNOWN
    
    # Verify all states are defined
    assert AgentState.INITIALIZING
    assert AgentState.ACTIVE
    assert AgentState.IDLE
    assert AgentState.SUSPENDED
    assert AgentState.ERROR


def test_agent_role_mapping():
    """Test role mapping functions."""
    from tools.overseer.agent.role_mapping import voicestudio_role_to_agent
    from tools.overseer.agent.identity import AgentRole
    
    # Test all VoiceStudio roles map correctly
    assert voicestudio_role_to_agent(0) == AgentRole.OVERSEER
    assert voicestudio_role_to_agent(1) == AgentRole.REVIEWER
    assert voicestudio_role_to_agent(2) == AgentRole.BUILDER
    assert voicestudio_role_to_agent(7) == AgentRole.DEBUGGER
    assert voicestudio_role_to_agent("debug-agent") == AgentRole.DEBUGGER
    assert voicestudio_role_to_agent("overseer") == AgentRole.OVERSEER
