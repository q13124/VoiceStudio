"""
Policy Models for Plugin Governance.

Phase 4 Enhancement: Data models for policy configuration
including whitelist/blacklist rules, permission caps, and
trust levels.
"""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Set


class TrustLevel(IntEnum):
    """
    Plugin trust levels for policy evaluation.

    Higher values indicate more trust and fewer restrictions.
    """

    UNTRUSTED = 0  # Unknown source, maximum restrictions
    COMMUNITY = 1  # Community-contributed, moderate restrictions
    VERIFIED = 2  # Verified publisher, some restrictions
    OFFICIAL = 3  # Official VoiceStudio plugin, minimal restrictions
    SYSTEM = 4  # System plugin, no restrictions


class PolicyAction(Enum):
    """Actions a policy can take on a plugin."""

    ALLOW = "allow"  # Allow with specified permissions
    DENY = "deny"  # Block completely
    WARN = "warn"  # Allow but show warning
    REVIEW = "review"  # Require manual approval


@dataclass
class PermissionCap:
    """
    Permission cap that limits what plugins can request.

    Even if a plugin requests a permission, the cap can
    downgrade or deny it based on policy.
    """

    category: str  # e.g., "audio", "filesystem", "network"
    action: Optional[str] = None  # e.g., "record", None = all actions
    max_level: str = "denied"  # "denied", "read_only", "write", "full"
    reason: str = ""  # Reason for the cap

    @property
    def permission_pattern(self) -> str:
        """Get the permission pattern this cap applies to."""
        if self.action:
            return f"{self.category}.{self.action}"
        return f"{self.category}.*"


@dataclass
class PolicyRule:
    """
    A single policy rule for matching plugins.

    Rules can match by:
        - Plugin ID (exact or pattern)
        - Plugin source/publisher
        - Trust level
        - Version constraints
    """

    # Rule identification
    rule_id: str
    description: str = ""
    priority: int = 0  # Higher = evaluated first

    # Match criteria (all must match if specified)
    plugin_id: Optional[str] = None  # Exact match or glob pattern
    plugin_id_pattern: Optional[str] = None  # Regex pattern
    publisher: Optional[str] = None  # Publisher/author match
    source: Optional[str] = None  # Source URL pattern
    min_trust_level: Optional[TrustLevel] = None
    max_trust_level: Optional[TrustLevel] = None
    version_constraint: Optional[str] = None  # semver constraint

    # Action
    action: PolicyAction = PolicyAction.ALLOW

    # Permission modifications
    permission_caps: List[PermissionCap] = field(default_factory=list)
    denied_permissions: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)

    # Warnings/notes
    warning_message: Optional[str] = None
    notes: str = ""

    def matches_id(self, plugin_id: str) -> bool:
        """Check if this rule matches a plugin ID."""
        import fnmatch
        import re

        if self.plugin_id:
            # Exact match or glob pattern
            if fnmatch.fnmatch(plugin_id, self.plugin_id):
                return True

        if self.plugin_id_pattern:
            # Regex pattern
            if re.match(self.plugin_id_pattern, plugin_id):
                return True

        # If no ID criteria, match all
        return bool(not self.plugin_id and not self.plugin_id_pattern)

    def matches_trust(self, trust_level: TrustLevel) -> bool:
        """Check if this rule matches a trust level."""
        if self.min_trust_level is not None:
            if trust_level < self.min_trust_level:
                return False

        if self.max_trust_level is not None:
            if trust_level > self.max_trust_level:
                return False

        return True


@dataclass
class PluginPolicy:
    """
    Policy specific to a single plugin.

    Overrides default policy for a specific plugin.
    """

    plugin_id: str
    action: PolicyAction = PolicyAction.ALLOW
    trust_level: Optional[TrustLevel] = None

    # Permission overrides
    allowed_permissions: Optional[List[str]] = None  # If set, only these
    denied_permissions: List[str] = field(default_factory=list)
    permission_caps: List[PermissionCap] = field(default_factory=list)

    # Restrictions
    allow_network: bool = True
    allow_subprocess: bool = False
    allow_filesystem_external: bool = False

    # Notes
    notes: str = ""
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None


@dataclass
class PolicyConfig:
    """
    Complete policy configuration.

    Loaded from policy files and applied by the policy engine.
    """

    # Metadata
    version: str = "1.0"
    name: str = "default"
    description: str = ""

    # Global settings
    default_action: PolicyAction = PolicyAction.ALLOW
    default_trust_level: TrustLevel = TrustLevel.COMMUNITY
    require_signature: bool = False
    require_manifest_id: bool = True
    
    # System plugin identification
    system_plugin_prefix: str = "com.voicestudio."  # Plugins with this prefix are system-trusted

    # Global permission caps (applied to all plugins)
    global_permission_caps: List[PermissionCap] = field(default_factory=list)
    global_denied_permissions: List[str] = field(default_factory=list)

    # Whitelist/blacklist
    whitelist_mode: bool = False  # If True, only whitelisted plugins allowed
    whitelist: Set[str] = field(default_factory=set)
    blacklist: Set[str] = field(default_factory=set)

    # Rules (evaluated in priority order)
    rules: List[PolicyRule] = field(default_factory=list)

    # Per-plugin overrides
    plugin_policies: Dict[str, PluginPolicy] = field(default_factory=dict)

    # Trusted publishers
    trusted_publishers: Set[str] = field(default_factory=set)

    # Trusted sources
    trusted_sources: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Sort rules by priority."""
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def is_whitelisted(self, plugin_id: str) -> bool:
        """Check if a plugin is explicitly whitelisted."""
        return plugin_id in self.whitelist

    def is_blacklisted(self, plugin_id: str) -> bool:
        """Check if a plugin is explicitly blacklisted."""
        return plugin_id in self.blacklist

    def get_plugin_policy(self, plugin_id: str) -> Optional[PluginPolicy]:
        """Get the specific policy for a plugin if it exists."""
        return self.plugin_policies.get(plugin_id)

    def get_matching_rules(
        self,
        plugin_id: str,
        trust_level: TrustLevel,
        publisher: Optional[str] = None,
    ) -> List[PolicyRule]:
        """Get all rules that match a plugin."""
        matching = []
        for rule in self.rules:
            if not rule.matches_id(plugin_id):
                continue
            if not rule.matches_trust(trust_level):
                continue
            if rule.publisher and publisher and rule.publisher != publisher:
                continue
            matching.append(rule)
        return matching

    def add_to_whitelist(self, plugin_id: str) -> None:
        """Add a plugin to the whitelist."""
        self.whitelist.add(plugin_id)
        self.blacklist.discard(plugin_id)  # Remove from blacklist if present

    def add_to_blacklist(self, plugin_id: str) -> None:
        """Add a plugin to the blacklist."""
        self.blacklist.add(plugin_id)
        self.whitelist.discard(plugin_id)  # Remove from whitelist if present

    def remove_from_whitelist(self, plugin_id: str) -> None:
        """Remove a plugin from the whitelist."""
        self.whitelist.discard(plugin_id)

    def remove_from_blacklist(self, plugin_id: str) -> None:
        """Remove a plugin from the blacklist."""
        self.blacklist.discard(plugin_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "default_action": self.default_action.value,
            "default_trust_level": self.default_trust_level.value,
            "require_signature": self.require_signature,
            "require_manifest_id": self.require_manifest_id,
            "system_plugin_prefix": self.system_plugin_prefix,
            "global_permission_caps": [
                {
                    "category": cap.category,
                    "action": cap.action,
                    "max_level": cap.max_level,
                    "reason": cap.reason,
                }
                for cap in self.global_permission_caps
            ],
            "global_denied_permissions": list(self.global_denied_permissions),
            "whitelist_mode": self.whitelist_mode,
            "whitelist": list(self.whitelist),
            "blacklist": list(self.blacklist),
            "trusted_publishers": list(self.trusted_publishers),
            "trusted_sources": list(self.trusted_sources),
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "description": r.description,
                    "priority": r.priority,
                    "plugin_id": r.plugin_id,
                    "plugin_id_pattern": r.plugin_id_pattern,
                    "publisher": r.publisher,
                    "action": r.action.value,
                    "denied_permissions": r.denied_permissions,
                }
                for r in self.rules
            ],
            "plugin_policies": {
                pid: {
                    "action": p.action.value,
                    "denied_permissions": p.denied_permissions,
                    "allow_network": p.allow_network,
                    "allow_subprocess": p.allow_subprocess,
                    "notes": p.notes,
                }
                for pid, p in self.plugin_policies.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyConfig":
        """Create from dictionary."""
        config = cls(
            version=data.get("version", "1.0"),
            name=data.get("name", "default"),
            description=data.get("description", ""),
            default_action=PolicyAction(data.get("default_action", "allow")),
            default_trust_level=TrustLevel(data.get("default_trust_level", 1)),
            require_signature=data.get("require_signature", False),
            require_manifest_id=data.get("require_manifest_id", True),
            system_plugin_prefix=data.get("system_plugin_prefix", "com.voicestudio."),
            whitelist_mode=data.get("whitelist_mode", False),
            whitelist=set(data.get("whitelist", [])),
            blacklist=set(data.get("blacklist", [])),
            trusted_publishers=set(data.get("trusted_publishers", [])),
            trusted_sources=set(data.get("trusted_sources", [])),
        )

        # Parse global permission caps
        for cap_data in data.get("global_permission_caps", []):
            config.global_permission_caps.append(
                PermissionCap(
                    category=cap_data["category"],
                    action=cap_data.get("action"),
                    max_level=cap_data.get("max_level", "denied"),
                    reason=cap_data.get("reason", ""),
                )
            )

        config.global_denied_permissions = data.get("global_denied_permissions", [])

        # Parse rules
        for rule_data in data.get("rules", []):
            config.rules.append(
                PolicyRule(
                    rule_id=rule_data["rule_id"],
                    description=rule_data.get("description", ""),
                    priority=rule_data.get("priority", 0),
                    plugin_id=rule_data.get("plugin_id"),
                    plugin_id_pattern=rule_data.get("plugin_id_pattern"),
                    publisher=rule_data.get("publisher"),
                    action=PolicyAction(rule_data.get("action", "allow")),
                    denied_permissions=rule_data.get("denied_permissions", []),
                )
            )

        # Parse plugin policies
        for pid, policy_data in data.get("plugin_policies", {}).items():
            config.plugin_policies[pid] = PluginPolicy(
                plugin_id=pid,
                action=PolicyAction(policy_data.get("action", "allow")),
                denied_permissions=policy_data.get("denied_permissions", []),
                allow_network=policy_data.get("allow_network", True),
                allow_subprocess=policy_data.get("allow_subprocess", False),
                notes=policy_data.get("notes", ""),
            )

        # Sort rules by priority
        config.rules.sort(key=lambda r: r.priority, reverse=True)

        return config
