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
from .identity import AgentIdentity, AgentRole, AgentState
from .registry import AgentRegistry
from .version_manifest import ManifestEntry, ManifestType, ReleaseChannel, VersionManifestStore

# Audit Logging
from .audit_store import AuditEntry, AuditStore
from .audit_logger import AuditLogger
from .replay_bundle import ReplayBundle, ReplayBundleGenerator

# Policy Engine
from .policy_loader import PolicyLoader, PolicyValidationError
from .policy_engine import PolicyEngine, PolicyDecision, PolicyResult

# Tool Gateway
from .tool_gateway import ToolGateway, GatewayResult

# Approval System
from .approval_manager import (
    ApprovalManager,
    ApprovalRequest,
    ApprovalRecord,
    ApprovalStatus,
)

# Circuit Breaker
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerManager,
    CircuitConfig,
    CircuitState,
)
from .anomaly_detector import (
    AnomalyDetector,
    AnomalyEvent,
    AnomalyType,
    AnomalySeverity,
)

# Kill Switch and Safe Zones
from .kill_switch import KillSwitch, KillSwitchLevel, KillSwitchActivation
from .safe_zones import SafeZoneManager, SafeZone, SafeZoneType, SafeZoneViolation

# Manifest Signing
from .manifest_signer import ManifestSigner, SignedManifest, SignatureAlgorithm
from .release_manager import ReleaseManager, ReleaseBundle, BundleType

__all__ = [
    # Identity
    "AgentIdentity",
    "AgentRole",
    "AgentState",
    "AgentRegistry",
    "ManifestEntry",
    "ManifestType",
    "ReleaseChannel",
    "VersionManifestStore",
    # Audit
    "AuditEntry",
    "AuditStore",
    "AuditLogger",
    "ReplayBundle",
    "ReplayBundleGenerator",
    # Policy
    "PolicyLoader",
    "PolicyValidationError",
    "PolicyEngine",
    "PolicyDecision",
    "PolicyResult",
    # Gateway
    "ToolGateway",
    "GatewayResult",
    # Approval
    "ApprovalManager",
    "ApprovalRequest",
    "ApprovalRecord",
    "ApprovalStatus",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerManager",
    "CircuitConfig",
    "CircuitState",
    "AnomalyDetector",
    "AnomalyEvent",
    "AnomalyType",
    "AnomalySeverity",
    # Kill Switch
    "KillSwitch",
    "KillSwitchLevel",
    "KillSwitchActivation",
    "SafeZoneManager",
    "SafeZone",
    "SafeZoneType",
    "SafeZoneViolation",
    # Manifest
    "ManifestSigner",
    "SignedManifest",
    "SignatureAlgorithm",
    "ReleaseManager",
    "ReleaseBundle",
    "BundleType",
]
