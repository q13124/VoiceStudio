"""
Policy Engine for Plugin Governance.

Phase 4 Enhancement: Evaluates plugin policies and determines
what actions and permissions are allowed.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .models import (
    PermissionCap,
    PluginPolicy,
    PolicyAction,
    PolicyConfig,
    PolicyRule,
    TrustLevel,
)

logger = logging.getLogger(__name__)


# Permission level values for comparison
PERMISSION_LEVELS = {
    "denied": 0,
    "read_only": 1,
    "write": 2,
    "full": 3,
}


@dataclass
class PolicyDecision:
    """
    Result of a policy evaluation for a plugin.

    Contains the decision and any modifications to apply.
    """

    # Core decision
    plugin_id: str
    allowed: bool
    action: PolicyAction

    # Trust assessment
    trust_level: TrustLevel

    # Effective permissions
    denied_permissions: Set[str] = field(default_factory=set)
    permission_caps: Dict[str, str] = field(default_factory=dict)  # pattern -> max_level

    # Restrictions
    allow_network: bool = True
    allow_subprocess: bool = False
    allow_filesystem_external: bool = False

    # Audit trail
    applied_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: str = ""

    # Metadata
    requires_review: bool = False
    review_reason: Optional[str] = None

    def is_permission_denied(self, permission: str) -> bool:
        """Check if a permission is denied by policy."""
        # Check exact match
        if permission in self.denied_permissions:
            return True

        # Check category wildcard
        category = permission.split(".")[0] if "." in permission else permission
        return f"{category}.*" in self.denied_permissions

    def get_permission_cap(self, permission: str) -> Optional[str]:
        """Get the cap level for a permission, if any."""
        # Check exact match
        if permission in self.permission_caps:
            return self.permission_caps[permission]

        # Check category wildcard
        category = permission.split(".")[0] if "." in permission else permission
        wildcard = f"{category}.*"
        if wildcard in self.permission_caps:
            return self.permission_caps[wildcard]

        return None

    def apply_cap(self, permission: str, requested_level: str) -> str:
        """
        Apply permission caps to a requested level.

        Returns the effective level after caps are applied.
        """
        cap = self.get_permission_cap(permission)
        if not cap:
            return requested_level

        # Get numeric values
        cap_value = PERMISSION_LEVELS.get(cap, 0)
        requested_value = PERMISSION_LEVELS.get(requested_level, 0)

        # Return the lower of the two
        if requested_value <= cap_value:
            return requested_level
        else:
            return cap

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/API."""
        return {
            "plugin_id": self.plugin_id,
            "allowed": self.allowed,
            "action": self.action.value,
            "trust_level": self.trust_level.value,
            "denied_permissions": list(self.denied_permissions),
            "permission_caps": dict(self.permission_caps),
            "allow_network": self.allow_network,
            "allow_subprocess": self.allow_subprocess,
            "allow_filesystem_external": self.allow_filesystem_external,
            "applied_rules": self.applied_rules,
            "warnings": self.warnings,
            "requires_review": self.requires_review,
            "review_reason": self.review_reason,
        }


class PolicyEngine:
    """
    Policy evaluation engine for plugin governance.

    Evaluates plugins against configured policies to determine
    if they should be loaded and what restrictions apply.
    """

    def __init__(self, config: Optional[PolicyConfig] = None):
        """
        Initialize the policy engine.

        Args:
            config: Policy configuration. If None, uses permissive defaults.
        """
        self._config = config or PolicyConfig()
        self._decision_cache: Dict[str, PolicyDecision] = {}

    @property
    def config(self) -> PolicyConfig:
        """Get the current policy configuration."""
        return self._config

    def update_config(self, config: PolicyConfig) -> None:
        """Update the policy configuration and clear cache."""
        self._config = config
        self._decision_cache.clear()
        logger.info(f"Policy config updated: {config.name}")

    def evaluate(
        self,
        plugin_id: str,
        manifest: Optional[Dict[str, Any]] = None,
        signature_valid: bool = False,
        publisher: Optional[str] = None,
        source: Optional[str] = None,
    ) -> PolicyDecision:
        """
        Evaluate a plugin against the policy.

        Args:
            plugin_id: The plugin's unique identifier
            manifest: The plugin's manifest data
            signature_valid: Whether the plugin has a valid signature
            publisher: The plugin's publisher/author
            source: The source URL of the plugin

        Returns:
            PolicyDecision with the evaluation result
        """
        manifest = manifest or {}

        # Create base decision
        decision = PolicyDecision(
            plugin_id=plugin_id,
            allowed=True,
            action=self._config.default_action,
            trust_level=self._config.default_trust_level,
        )

        # Step 1: Check blacklist (always takes precedence)
        if self._config.is_blacklisted(plugin_id):
            decision.allowed = False
            decision.action = PolicyAction.DENY
            decision.warnings.append("Plugin is blacklisted")
            decision.applied_rules.append("blacklist")
            logger.warning(f"Plugin {plugin_id} denied: blacklisted")
            return decision

        # Step 2: Check whitelist mode
        if self._config.whitelist_mode:
            if not self._config.is_whitelisted(plugin_id):
                decision.allowed = False
                decision.action = PolicyAction.DENY
                decision.warnings.append("Plugin not in whitelist (whitelist mode enabled)")
                decision.applied_rules.append("whitelist_mode")
                logger.warning(f"Plugin {plugin_id} denied: not whitelisted")
                return decision
            else:
                decision.applied_rules.append("whitelist")

        # Step 3: Check signature requirement
        if self._config.require_signature and not signature_valid:
            decision.allowed = False
            decision.action = PolicyAction.DENY
            decision.warnings.append("Plugin signature required but not valid")
            decision.applied_rules.append("require_signature")
            logger.warning(f"Plugin {plugin_id} denied: invalid signature")
            return decision

        # Step 4: Check manifest ID requirement
        if self._config.require_manifest_id:
            manifest_id = manifest.get("id")
            if not manifest_id:
                decision.allowed = False
                decision.action = PolicyAction.DENY
                decision.warnings.append("Plugin manifest must have 'id' field")
                decision.applied_rules.append("require_manifest_id")
                logger.warning(f"Plugin {plugin_id} denied: missing manifest id")
                return decision

        # Step 5: Determine trust level
        decision.trust_level = self._assess_trust(
            plugin_id=plugin_id,
            manifest=manifest,
            signature_valid=signature_valid,
            publisher=publisher,
            source=source,
        )

        # Step 6: Apply global permission restrictions
        for perm in self._config.global_denied_permissions:
            decision.denied_permissions.add(perm)
            decision.applied_rules.append(f"global_deny:{perm}")

        for cap in self._config.global_permission_caps:
            decision.permission_caps[cap.permission_pattern] = cap.max_level
            decision.applied_rules.append(f"global_cap:{cap.permission_pattern}")

        # Step 7: Apply matching rules
        matching_rules = self._config.get_matching_rules(
            plugin_id=plugin_id,
            trust_level=decision.trust_level,
            publisher=publisher,
        )

        for rule in matching_rules:
            self._apply_rule(decision, rule)

        # Step 8: Apply plugin-specific policy (highest precedence)
        plugin_policy = self._config.get_plugin_policy(plugin_id)
        if plugin_policy:
            self._apply_plugin_policy(decision, plugin_policy)

        # Step 9: Set final allowed status based on action
        if decision.action == PolicyAction.DENY:
            decision.allowed = False
        elif decision.action == PolicyAction.REVIEW:
            decision.allowed = False
            decision.requires_review = True
            decision.review_reason = "Policy requires manual review"
        elif decision.action == PolicyAction.WARN:
            decision.allowed = True
            if not decision.warnings:
                decision.warnings.append("Plugin allowed with warnings")

        # Log decision
        if decision.allowed:
            logger.info(
                f"Plugin {plugin_id} allowed (trust={decision.trust_level.name}, "
                f"rules={len(decision.applied_rules)})"
            )
        else:
            logger.warning(
                f"Plugin {plugin_id} denied (action={decision.action.value}, "
                f"warnings={decision.warnings})"
            )

        return decision

    def _assess_trust(
        self,
        plugin_id: str,
        manifest: Dict[str, Any],
        signature_valid: bool,
        publisher: Optional[str],
        source: Optional[str],
    ) -> TrustLevel:
        """Assess the trust level for a plugin."""
        # Check for system plugin using configurable prefix
        system_prefix = self._config.system_plugin_prefix
        if system_prefix and plugin_id.startswith(system_prefix):
            return TrustLevel.SYSTEM

        # Check for official plugin
        manifest_trust = manifest.get("trust", {})
        if manifest_trust.get("level") == "official" and signature_valid:
            return TrustLevel.OFFICIAL

        # Check for trusted publisher
        if publisher and publisher in self._config.trusted_publishers:
            return TrustLevel.VERIFIED

        # Check for trusted source
        if source:
            for trusted in self._config.trusted_sources:
                if source.startswith(trusted):
                    return TrustLevel.VERIFIED

        # Check for verified status in manifest
        if manifest_trust.get("verified") and signature_valid:
            return TrustLevel.VERIFIED

        # Check for signature (community minimum)
        if signature_valid:
            return TrustLevel.COMMUNITY

        # Default to untrusted
        return TrustLevel.UNTRUSTED

    def _apply_rule(self, decision: PolicyDecision, rule: PolicyRule) -> None:
        """Apply a policy rule to a decision."""
        decision.applied_rules.append(f"rule:{rule.rule_id}")

        # Apply action (most restrictive wins)
        if rule.action.value > decision.action.value:
            decision.action = rule.action

        # Add denied permissions
        for perm in rule.denied_permissions:
            decision.denied_permissions.add(perm)

        # Add permission caps
        for cap in rule.permission_caps:
            pattern = cap.permission_pattern
            existing = decision.permission_caps.get(pattern)
            if existing:
                # Use the more restrictive cap
                existing_value = PERMISSION_LEVELS.get(existing, 0)
                new_value = PERMISSION_LEVELS.get(cap.max_level, 0)
                if new_value < existing_value:
                    decision.permission_caps[pattern] = cap.max_level
            else:
                decision.permission_caps[pattern] = cap.max_level

        # Add warning if present
        if rule.warning_message:
            decision.warnings.append(rule.warning_message)

    def _apply_plugin_policy(
        self, decision: PolicyDecision, policy: PluginPolicy
    ) -> None:
        """Apply a plugin-specific policy to a decision."""
        decision.applied_rules.append(f"plugin_policy:{policy.plugin_id}")

        # Override action
        decision.action = policy.action

        # Override trust level if specified
        if policy.trust_level is not None:
            decision.trust_level = policy.trust_level

        # Add denied permissions
        for perm in policy.denied_permissions:
            decision.denied_permissions.add(perm)

        # Add permission caps
        for cap in policy.permission_caps:
            decision.permission_caps[cap.permission_pattern] = cap.max_level

        # Apply restrictions
        decision.allow_network = policy.allow_network
        decision.allow_subprocess = policy.allow_subprocess
        decision.allow_filesystem_external = policy.allow_filesystem_external

        # Add notes
        if policy.notes:
            decision.notes = policy.notes

    def check_permission(
        self,
        plugin_id: str,
        permission: str,
        requested_level: str = "full",
        decision: Optional[PolicyDecision] = None,
    ) -> tuple:
        """
        Check if a specific permission is allowed for a plugin.

        Args:
            plugin_id: The plugin's ID
            permission: The permission to check
            requested_level: The level being requested
            decision: Pre-computed decision (optional)

        Returns:
            Tuple of (allowed: bool, effective_level: str, reason: str)
        """
        if decision is None:
            decision = self._decision_cache.get(plugin_id)
            if decision is None:
                # Can't check without a decision
                return False, "denied", "No policy decision for plugin"

        # Check if permission is denied
        if decision.is_permission_denied(permission):
            return False, "denied", "Permission denied by policy"

        # Apply caps
        effective_level = decision.apply_cap(permission, requested_level)

        if effective_level == "denied":
            return False, "denied", "Permission capped to denied"

        return True, effective_level, "Allowed by policy"

    def cache_decision(self, plugin_id: str, decision: PolicyDecision) -> None:
        """Cache a decision for later permission checks."""
        self._decision_cache[plugin_id] = decision

    def clear_cache(self, plugin_id: Optional[str] = None) -> None:
        """Clear cached decisions."""
        if plugin_id:
            self._decision_cache.pop(plugin_id, None)
        else:
            self._decision_cache.clear()

    def get_cached_decision(self, plugin_id: str) -> Optional[PolicyDecision]:
        """Get a cached decision for a plugin."""
        return self._decision_cache.get(plugin_id)

    def add_to_whitelist(self, plugin_id: str) -> None:
        """Add a plugin to the whitelist."""
        self._config.add_to_whitelist(plugin_id)
        self.clear_cache(plugin_id)

    def add_to_blacklist(self, plugin_id: str) -> None:
        """Add a plugin to the blacklist."""
        self._config.add_to_blacklist(plugin_id)
        self.clear_cache(plugin_id)

    def remove_from_whitelist(self, plugin_id: str) -> None:
        """Remove a plugin from the whitelist."""
        self._config.remove_from_whitelist(plugin_id)
        self.clear_cache(plugin_id)

    def remove_from_blacklist(self, plugin_id: str) -> None:
        """Remove a plugin from the blacklist."""
        self._config.remove_from_blacklist(plugin_id)
        self.clear_cache(plugin_id)


# Global engine instance
_global_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine instance."""
    global _global_engine
    if _global_engine is None:
        _global_engine = PolicyEngine()
    return _global_engine


def set_policy_engine(engine: PolicyEngine) -> None:
    """Set the global policy engine instance."""
    global _global_engine
    _global_engine = engine
