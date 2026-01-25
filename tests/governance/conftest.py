"""
Pytest fixtures for governance tests.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Add the tools/overseer path to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "overseer"))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def agent_identity():
    """Create a test agent identity."""
    from agent.identity import AgentIdentity, AgentRole
    
    return AgentIdentity.create(
        role=AgentRole.CODER,
        user_id="test_user",
        config={"test": True},
    )


@pytest.fixture
def agent_registry(temp_dir: Path):
    """Create a test agent registry."""
    from agent.registry import AgentRegistry
    
    return AgentRegistry(storage_path=temp_dir / "registry.json")


@pytest.fixture
def audit_store(temp_dir: Path):
    """Create a test audit store."""
    from agent.audit_store import AuditStore
    
    return AuditStore(storage_dir=temp_dir / "audit")


@pytest.fixture
def audit_logger(audit_store):
    """Create a test audit logger."""
    from agent.audit_logger import AuditLogger
    
    return AuditLogger(store=audit_store)


@pytest.fixture
def policy_engine(temp_dir: Path):
    """Create a test policy engine with the base policy."""
    import shutil
    from agent.policy_engine import PolicyEngine
    from agent.policy_loader import PolicyLoader
    
    # Copy base policy to temp directory
    policies_dir = temp_dir / "policies"
    policies_dir.mkdir(parents=True, exist_ok=True)
    
    source_policy = Path(__file__).parent.parent.parent / "tools" / "overseer" / "agent" / "policies" / "base_policy.yaml"
    if source_policy.exists():
        shutil.copy(source_policy, policies_dir / "base_policy.yaml")
    
    loader = PolicyLoader(policies_dir=policies_dir)
    return PolicyEngine(policy_name="base_policy", loader=loader)


@pytest.fixture
def tool_gateway(policy_engine, audit_logger):
    """Create a test tool gateway."""
    from agent.tool_gateway import ToolGateway
    
    return ToolGateway(policy_engine=policy_engine, audit_logger=audit_logger)


@pytest.fixture
def circuit_breaker_manager():
    """Create a test circuit breaker manager."""
    from agent.circuit_breaker import CircuitBreakerManager, CircuitConfig
    
    config = CircuitConfig(
        denied_action_threshold=3,
        denied_action_window_minutes=5,
        failure_threshold=5,
        failure_window_minutes=10,
    )
    return CircuitBreakerManager(config=config)


@pytest.fixture
def kill_switch(temp_dir: Path):
    """Create a test kill switch."""
    from agent.kill_switch import KillSwitch
    
    return KillSwitch(storage_path=temp_dir / "kill_switches.json")


@pytest.fixture
def safe_zone_manager():
    """Create a test safe zone manager."""
    from agent.safe_zones import SafeZoneManager
    
    return SafeZoneManager(include_defaults=True)


@pytest.fixture
def approval_manager(temp_dir: Path):
    """Create a test approval manager."""
    from agent.approval_manager import ApprovalManager
    
    return ApprovalManager(storage_path=temp_dir / "approvals")


@pytest.fixture
def manifest_signer(temp_dir: Path):
    """Create a test manifest signer."""
    from agent.manifest_signer import ManifestSigner
    
    return ManifestSigner(key_path=temp_dir / ".signing_key")


@pytest.fixture
def release_manager(temp_dir: Path, manifest_signer):
    """Create a test release manager."""
    from agent.release_manager import ReleaseManager
    
    return ReleaseManager(
        storage_path=temp_dir / "releases",
        signer=manifest_signer,
    )
