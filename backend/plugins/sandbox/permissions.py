"""
Plugin Permission Enforcement System.

Phase 4 Enhancement: Hardened permission enforcement for subprocess
isolation model. Implements:
    - Hierarchical permission checking
    - Capability-based access control
    - Permission guards with audit logging
    - Runtime permission queries
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission grant levels."""

    DENIED = 0
    READ_ONLY = 1
    WRITE = 2
    FULL = 3


class PermissionCategory(Enum):
    """Standard permission categories."""

    AUDIO = "audio"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    UI = "ui"
    SETTINGS = "settings"
    HOST_API = "host_api"
    ENGINE = "engine"
    PROCESS = "process"


@dataclass
class PermissionCheck:
    """Result of a permission check."""

    granted: bool
    permission: str
    level: PermissionLevel
    reason: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/audit."""
        return {
            "granted": self.granted,
            "permission": self.permission,
            "level": self.level.name,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


@dataclass
class PermissionAuditEntry:
    """Audit log entry for permission checks."""

    plugin_id: str
    permission: str
    granted: bool
    reason: str
    timestamp: float
    method: Optional[str] = None
    params_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "permission": self.permission,
            "granted": self.granted,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "method": self.method,
            "params_hash": self.params_hash,
        }


class PermissionAuditor:
    """
    Audit logger for permission checks.

    Records all permission checks for security auditing and
    compliance reporting.
    """

    def __init__(self, max_entries: int = 10000):
        self._entries: List[PermissionAuditEntry] = []
        self._max_entries = max_entries
        self._denied_count: Dict[str, int] = {}

    def record(self, entry: PermissionAuditEntry) -> None:
        """Record a permission check."""
        self._entries.append(entry)

        # Track denied permissions per plugin
        if not entry.granted:
            key = f"{entry.plugin_id}:{entry.permission}"
            self._denied_count[key] = self._denied_count.get(key, 0) + 1

        # Trim old entries if needed
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries // 2:]

        # Log denied permissions
        if not entry.granted:
            logger.warning(
                f"Permission denied: {entry.plugin_id} -> {entry.permission} "
                f"({entry.reason})"
            )

    def get_entries(
        self,
        plugin_id: Optional[str] = None,
        since: Optional[float] = None,
        granted: Optional[bool] = None,
    ) -> List[PermissionAuditEntry]:
        """Query audit entries with filters."""
        entries = self._entries

        if plugin_id:
            entries = [e for e in entries if e.plugin_id == plugin_id]

        if since is not None:
            entries = [e for e in entries if e.timestamp >= since]

        if granted is not None:
            entries = [e for e in entries if e.granted == granted]

        return entries

    def get_denial_counts(self, plugin_id: Optional[str] = None) -> Dict[str, int]:
        """Get permission denial counts."""
        if plugin_id:
            prefix = f"{plugin_id}:"
            return {
                k.split(":", 1)[1]: v
                for k, v in self._denied_count.items()
                if k.startswith(prefix)
            }
        return dict(self._denied_count)

    def clear(self) -> None:
        """Clear audit log."""
        self._entries.clear()
        self._denied_count.clear()


# Global auditor instance
_global_auditor = PermissionAuditor()


def get_auditor() -> PermissionAuditor:
    """Get the global permission auditor."""
    return _global_auditor


class PermissionEnforcer:
    """
    Hardened permission enforcement with hierarchical checking.

    Supports:
        - Category.action permission format (e.g., "audio.playback")
        - Wildcard permissions (e.g., "audio.*")
        - Permission levels (denied, read_only, write, full)
        - Policy overrides
        - Audit logging
    """

    def __init__(
        self,
        plugin_id: str,
        permissions: Dict[str, Any],
        auditor: Optional[PermissionAuditor] = None,
    ):
        self.plugin_id = plugin_id
        self._raw_permissions = permissions
        self._auditor = auditor or _global_auditor
        self._cache: Dict[str, PermissionCheck] = {}

        # Parse and normalize permissions
        self._parsed = self._parse_permissions(permissions)

        # Track runtime state
        self._elevated = False
        self._temporary_grants: Set[str] = set()

    def _parse_permissions(
        self, permissions: Dict[str, Any]
    ) -> Dict[str, PermissionLevel]:
        """
        Parse permission config into normalized form.

        Handles various formats:
            - Boolean: {"audio": true} -> audio.* = FULL
            - Dict with enabled: {"audio": {"enabled": true}} -> audio.* = FULL
            - Dict with specific actions: {"audio": {"playback": true, "record": false}}
            - Level strings: {"audio": {"playback": "read_only"}}
        """
        parsed: Dict[str, PermissionLevel] = {}

        if not permissions:
            return parsed

        for category, value in permissions.items():
            if isinstance(value, bool):
                # Boolean grants/denies entire category
                level = PermissionLevel.FULL if value else PermissionLevel.DENIED
                parsed[f"{category}.*"] = level

            elif isinstance(value, dict):
                # Check for 'enabled' flag
                enabled = value.get("enabled", False)
                if enabled:
                    parsed[f"{category}.*"] = PermissionLevel.FULL

                # Process specific actions
                for action, action_value in value.items():
                    if action == "enabled":
                        continue

                    if isinstance(action_value, bool):
                        level = (
                            PermissionLevel.FULL
                            if action_value
                            else PermissionLevel.DENIED
                        )
                    elif isinstance(action_value, str):
                        level = self._parse_level(action_value)
                    elif isinstance(action_value, dict):
                        # Nested dict - check for 'level' or 'enabled'
                        if "level" in action_value:
                            level = self._parse_level(action_value["level"])
                        elif action_value.get("enabled", False):
                            level = PermissionLevel.FULL
                        else:
                            level = PermissionLevel.DENIED
                    else:
                        level = PermissionLevel.DENIED

                    parsed[f"{category}.{action}"] = level

            elif isinstance(value, str):
                # String level for entire category
                parsed[f"{category}.*"] = self._parse_level(value)

        return parsed

    def _parse_level(self, level_str: str) -> PermissionLevel:
        """Parse a permission level string."""
        level_map = {
            "denied": PermissionLevel.DENIED,
            "read": PermissionLevel.READ_ONLY,
            "read_only": PermissionLevel.READ_ONLY,
            "write": PermissionLevel.WRITE,
            "full": PermissionLevel.FULL,
        }
        return level_map.get(level_str.lower(), PermissionLevel.DENIED)

    def check(
        self,
        permission: str,
        required_level: PermissionLevel = PermissionLevel.FULL,
        audit_method: Optional[str] = None,
    ) -> PermissionCheck:
        """
        Check if a permission is granted.

        Args:
            permission: The permission string (e.g., "audio.playback")
            required_level: Minimum required level
            audit_method: Optional method name for audit logging

        Returns:
            PermissionCheck with result details
        """
        # Check cache
        cache_key = f"{permission}:{required_level.value}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # Log to auditor even for cached results
            self._log_check(cached, audit_method)
            return cached

        # Check temporary grants
        if permission in self._temporary_grants:
            result = PermissionCheck(
                granted=True,
                permission=permission,
                level=PermissionLevel.FULL,
                reason="Temporary grant active",
            )
            self._log_check(result, audit_method)
            return result

        # Parse permission
        parts = permission.split(".")
        if len(parts) < 2:
            result = PermissionCheck(
                granted=False,
                permission=permission,
                level=PermissionLevel.DENIED,
                reason="Invalid permission format",
            )
            self._log_check(result, audit_method)
            return result

        category = parts[0]
        action = parts[1]

        # Check specific permission first
        granted_level = self._parsed.get(permission)

        # Fall back to category wildcard
        if granted_level is None:
            granted_level = self._parsed.get(f"{category}.*")

        # Fall back to denied
        if granted_level is None:
            granted_level = PermissionLevel.DENIED

        # Check if granted level meets required level
        granted = granted_level.value >= required_level.value

        reason = (
            f"Granted at level {granted_level.name}"
            if granted
            else f"Required {required_level.name}, got {granted_level.name}"
        )

        result = PermissionCheck(
            granted=granted,
            permission=permission,
            level=granted_level,
            reason=reason,
        )

        # Cache result
        self._cache[cache_key] = result

        # Log to auditor
        self._log_check(result, audit_method)

        return result

    def require(
        self,
        permission: str,
        required_level: PermissionLevel = PermissionLevel.FULL,
    ) -> None:
        """
        Require a permission, raising PermissionError if not granted.

        Args:
            permission: The permission string
            required_level: Minimum required level

        Raises:
            PermissionError: If permission is not granted
        """
        check = self.check(permission, required_level)
        if not check.granted:
            raise PermissionError(
                f"Permission denied: {permission} - {check.reason}"
            )

    def has(self, permission: str) -> bool:
        """Simple boolean check for permission."""
        return self.check(permission).granted

    def get_level(self, permission: str) -> PermissionLevel:
        """Get the granted level for a permission."""
        return self.check(permission).level

    def list_granted(self) -> List[str]:
        """List all granted permissions."""
        return [
            perm
            for perm, level in self._parsed.items()
            if level != PermissionLevel.DENIED
        ]

    def list_categories(self) -> List[str]:
        """List all permission categories with any grants."""
        categories: Set[str] = set()
        for perm, level in self._parsed.items():
            if level != PermissionLevel.DENIED:
                category = perm.split(".")[0]
                categories.add(category)
        return list(categories)

    def grant_temporary(self, permission: str) -> None:
        """
        Grant a temporary permission (e.g., for elevated operations).

        Note: Temporary grants should be used sparingly and
        revoked as soon as possible.
        """
        self._temporary_grants.add(permission)
        self._cache.clear()  # Invalidate cache
        logger.info(f"Temporary permission granted: {self.plugin_id} -> {permission}")

    def revoke_temporary(self, permission: str) -> None:
        """Revoke a temporary permission."""
        self._temporary_grants.discard(permission)
        self._cache.clear()  # Invalidate cache
        logger.info(f"Temporary permission revoked: {self.plugin_id} -> {permission}")

    def revoke_all_temporary(self) -> None:
        """Revoke all temporary permissions."""
        self._temporary_grants.clear()
        self._cache.clear()

    def _log_check(
        self, result: PermissionCheck, method: Optional[str]
    ) -> None:
        """Log permission check to auditor."""
        entry = PermissionAuditEntry(
            plugin_id=self.plugin_id,
            permission=result.permission,
            granted=result.granted,
            reason=result.reason,
            timestamp=result.timestamp,
            method=method,
        )
        self._auditor.record(entry)


def permission_guard(
    permission: str,
    required_level: PermissionLevel = PermissionLevel.FULL,
) -> Callable:
    """
    Decorator for permission-guarded methods.

    Usage:
        @permission_guard("audio.playback")
        async def play_audio(self, ...):
            ...

    The decorated method must have access to an enforcer via:
        - self.enforcer (attribute)
        - self._context.enforcer (nested attribute)
        - enforcer kwarg
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Find the enforcer
            enforcer: Optional[PermissionEnforcer] = None

            if args:
                self = args[0]
                if hasattr(self, "enforcer"):
                    enforcer = self.enforcer
                elif hasattr(self, "_context") and hasattr(self._context, "enforcer"):
                    enforcer = self._context.enforcer

            if enforcer is None:
                enforcer = kwargs.get("enforcer")

            if enforcer is None:
                raise RuntimeError(
                    f"No enforcer available for permission check: {permission}"
                )

            # Check permission
            enforcer.require(permission, required_level)

            # Call the guarded function
            return await func(*args, **kwargs)

        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__

        return wrapper

    return decorator


class PermissionRegistry:
    """
    Registry of all available permissions.

    Used for documentation, validation, and UI generation.
    """

    def __init__(self):
        self._permissions: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        permission: str,
        description: str,
        category: Optional[PermissionCategory] = None,
        requires_trust: bool = False,
        default_level: PermissionLevel = PermissionLevel.DENIED,
    ) -> None:
        """Register a permission."""
        self._permissions[permission] = {
            "description": description,
            "category": category.value if category else permission.split(".")[0],
            "requires_trust": requires_trust,
            "default_level": default_level.name,
        }

    def get(self, permission: str) -> Optional[Dict[str, Any]]:
        """Get permission info."""
        return self._permissions.get(permission)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all registered permissions."""
        return dict(self._permissions)

    def list_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """List permissions by category."""
        return {
            k: v for k, v in self._permissions.items() if v["category"] == category
        }

    def validate(self, permissions: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a permission configuration.

        Returns:
            Tuple of (valid, list of error messages)
        """
        errors: List[str] = []

        # Parse permissions to check validity
        for category, value in permissions.items():
            if isinstance(value, dict):
                for action in value:
                    if action == "enabled":
                        continue
                    perm = f"{category}.{action}"
                    if perm not in self._permissions and f"{category}.*" not in self._permissions:
                        errors.append(f"Unknown permission: {perm}")

        return len(errors) == 0, errors


# Global permission registry
_registry = PermissionRegistry()


def get_registry() -> PermissionRegistry:
    """Get the global permission registry."""
    return _registry


# Register standard VoiceStudio permissions
def _register_standard_permissions():
    """Register all standard VoiceStudio permissions."""
    registry = get_registry()

    # Audio permissions
    registry.register(
        "audio.playback",
        "Play audio through the host audio system",
        PermissionCategory.AUDIO,
    )
    registry.register(
        "audio.record",
        "Record audio from input devices",
        PermissionCategory.AUDIO,
        requires_trust=True,
    )
    registry.register(
        "audio.process",
        "Process audio data (apply effects, transforms)",
        PermissionCategory.AUDIO,
    )

    # Filesystem permissions
    registry.register(
        "filesystem.read",
        "Read files from plugin storage",
        PermissionCategory.FILESYSTEM,
    )
    registry.register(
        "filesystem.write",
        "Write files to plugin storage",
        PermissionCategory.FILESYSTEM,
    )
    registry.register(
        "filesystem.external",
        "Access files outside plugin sandbox",
        PermissionCategory.FILESYSTEM,
        requires_trust=True,
    )

    # Network permissions
    registry.register(
        "network.http",
        "Make HTTP/HTTPS requests",
        PermissionCategory.NETWORK,
    )
    registry.register(
        "network.websocket",
        "Establish WebSocket connections",
        PermissionCategory.NETWORK,
    )

    # UI permissions
    registry.register(
        "ui.notify",
        "Show notifications to the user",
        PermissionCategory.UI,
    )
    registry.register(
        "ui.dialog",
        "Display modal dialogs",
        PermissionCategory.UI,
    )
    registry.register(
        "ui.panel",
        "Create or update UI panels",
        PermissionCategory.UI,
    )

    # Settings permissions
    registry.register(
        "settings.read",
        "Read application settings",
        PermissionCategory.SETTINGS,
    )
    registry.register(
        "settings.write",
        "Write plugin-specific settings",
        PermissionCategory.SETTINGS,
    )

    # Host API permissions
    registry.register(
        "host_api.engine.invoke",
        "Invoke methods on other engines",
        PermissionCategory.HOST_API,
    )
    registry.register(
        "host_api.engine.list",
        "List available engines",
        PermissionCategory.HOST_API,
    )

    # Process permissions
    registry.register(
        "process.spawn",
        "Spawn subprocess commands",
        PermissionCategory.PROCESS,
        requires_trust=True,
    )


# Initialize standard permissions on module load
_register_standard_permissions()
