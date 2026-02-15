"""
Agent Governance Module

Provides unified governance for development and runtime agents including:
- Agent identity and lifecycle management
- Policy-based access control
- Audit logging with replay capability
- Approval gates for high-risk actions
- Circuit breakers and kill switches
"""

# Identity and Registry
from .anomaly_detector import (
    AnomalyDetector,
    AnomalyEvent,
    AnomalySeverity,
    AnomalyType,
)

# Approval System
from .approval_manager import (
    ApprovalManager,
    ApprovalRecord,
    ApprovalRequest,
    ApprovalStatus,
)
from .audit_logger import AuditLogger

# Audit Logging
from .audit_store import AuditEntry, AuditStore

# Circuit Breaker
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerManager,
    CircuitConfig,
    CircuitState,
)
from .identity import AgentIdentity, AgentRole, AgentState

# Kill Switch and Safe Zones
from .kill_switch import KillSwitch, KillSwitchActivation, KillSwitchLevel

# Manifest Signing
from .manifest_signer import ManifestSigner, SignatureAlgorithm, SignedManifest
from .policy_engine import PolicyDecision, PolicyEngine, PolicyResult

# Policy Engine
from .policy_loader import PolicyLoader, PolicyValidationError
from .registry import AgentRegistry
from .release_manager import BundleType, ReleaseBundle, ReleaseManager
from .replay_bundle import ReplayBundle, ReplayBundleGenerator
from .safe_zones import SafeZone, SafeZoneManager, SafeZoneType, SafeZoneViolation

# Tool Gateway
from .tool_gateway import GatewayResult, ToolGateway
from .version_manifest import ManifestEntry, ManifestType, ReleaseChannel, VersionManifestStore

__all__ = [
    # Identity
    "AgentIdentity",
    "AgentRegistry",
    "AgentRole",
    "AgentState",
    "AnomalyDetector",
    "AnomalyEvent",
    "AnomalySeverity",
    "AnomalyType",
    # Approval
    "ApprovalManager",
    "ApprovalRecord",
    "ApprovalRequest",
    "ApprovalStatus",
    # Audit
    "AuditEntry",
    "AuditLogger",
    "AuditStore",
    "BundleType",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerManager",
    "CircuitConfig",
    "CircuitState",
    "GatewayResult",
    # Kill Switch
    "KillSwitch",
    "KillSwitchActivation",
    "KillSwitchLevel",
    "ManifestEntry",
    # Manifest
    "ManifestSigner",
    "ManifestType",
    "PolicyDecision",
    "PolicyEngine",
    # Policy
    "PolicyLoader",
    "PolicyResult",
    "PolicyValidationError",
    "ReleaseBundle",
    "ReleaseChannel",
    "ReleaseManager",
    "ReplayBundle",
    "ReplayBundleGenerator",
    "SafeZone",
    "SafeZoneManager",
    "SafeZoneType",
    "SafeZoneViolation",
    "SignatureAlgorithm",
    "SignedManifest",
    # Gateway
    "ToolGateway",
    "VersionManifestStore",
]
