"""
Safe Zones

Defines protected paths and resources that agents must never modify.
Provides automatic rollback when safe zone violations occur.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set


class SafeZoneType(str, Enum):
    """Types of safe zones."""
    
    FILESYSTEM = "Filesystem"
    REGISTRY = "Registry"
    NETWORK = "Network"
    PROCESS = "Process"


class ViolationAction(str, Enum):
    """Actions to take on safe zone violation."""
    
    WARN = "Warn"
    DENY = "Deny"
    QUARANTINE = "Quarantine"
    QUARANTINE_AND_ALERT = "QuarantineAndAlert"
    QUARANTINE_AND_ROLLBACK = "QuarantineAndRollback"


@dataclass
class SafeZone:
    """
    Definition of a protected safe zone.
    
    Attributes:
        zone_type: Type of safe zone
        pattern: Pattern to match (path, registry key, etc.)
        description: Human-readable description
        action: Action to take on violation
        enabled: Whether the zone is active
    """
    
    zone_type: SafeZoneType
    pattern: str
    description: str = ""
    action: ViolationAction = ViolationAction.QUARANTINE_AND_ALERT
    enabled: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "zone_type": self.zone_type.value,
            "pattern": self.pattern,
            "description": self.description,
            "action": self.action.value,
            "enabled": self.enabled,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SafeZone":
        """Create from dictionary."""
        return cls(
            zone_type=SafeZoneType(data["zone_type"]),
            pattern=data["pattern"],
            description=data.get("description", ""),
            action=ViolationAction(data.get("action", "QuarantineAndAlert")),
            enabled=data.get("enabled", True),
        )


@dataclass
class SafeZoneViolation:
    """
    Record of a safe zone violation.
    
    Attributes:
        timestamp: When the violation occurred
        agent_id: ID of the violating agent
        zone: The violated safe zone
        attempted_resource: What the agent tried to access
        tool_name: Tool that triggered the violation
        action_taken: What action was taken
    """
    
    timestamp: datetime
    agent_id: str
    zone: SafeZone
    attempted_resource: str
    tool_name: str
    action_taken: ViolationAction
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "zone": self.zone.to_dict(),
            "attempted_resource": self.attempted_resource,
            "tool_name": self.tool_name,
            "action_taken": self.action_taken.value,
        }


class SafeZoneManager:
    """
    Manages safe zones and checks for violations.
    """
    
    # Default safe zones for Windows
    DEFAULT_SAFE_ZONES = [
        SafeZone(
            zone_type=SafeZoneType.FILESYSTEM,
            pattern="${PROGRAMFILES}/**",
            description="Program Files directory",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.FILESYSTEM,
            pattern="${PROGRAMFILES(X86)}/**",
            description="Program Files (x86) directory",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.FILESYSTEM,
            pattern="${WINDIR}/**",
            description="Windows directory",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.FILESYSTEM,
            pattern="${APPDATA}/Microsoft/Windows/Start Menu/Programs/Startup/**",
            description="User startup folder",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.FILESYSTEM,
            pattern="${PROGRAMDATA}/Microsoft/Windows/Start Menu/Programs/Startup/**",
            description="System startup folder",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.REGISTRY,
            pattern="HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            description="System startup registry key",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.REGISTRY,
            pattern="HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            description="User startup registry key",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
        SafeZone(
            zone_type=SafeZoneType.REGISTRY,
            pattern="HKLM\\SYSTEM\\CurrentControlSet\\Services/**",
            description="Windows services registry",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        ),
    ]
    
    def __init__(
        self,
        custom_zones: Optional[List[SafeZone]] = None,
        on_violation: Optional[Callable[[SafeZoneViolation], None]] = None,
        include_defaults: bool = True,
    ):
        """
        Initialize the safe zone manager.
        
        Args:
            custom_zones: Additional safe zones to protect
            on_violation: Callback when violation occurs
            include_defaults: Whether to include default safe zones
        """
        self._zones: List[SafeZone] = []
        self._on_violation = on_violation
        self._violations: List[SafeZoneViolation] = []
        
        # Add default zones
        if include_defaults:
            self._zones.extend(self.DEFAULT_SAFE_ZONES)
        
        # Add custom zones
        if custom_zones:
            self._zones.extend(custom_zones)
        
        # Cache expanded patterns
        self._expanded_patterns: Dict[str, str] = {}
        self._expand_all_patterns()
    
    def _expand_env_vars(self, pattern: str) -> str:
        """Expand environment variables in a pattern."""
        if pattern in self._expanded_patterns:
            return self._expanded_patterns[pattern]
        
        result = pattern
        
        # Common environment variables
        env_vars = {
            "PROGRAMFILES": os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            "PROGRAMFILES(X86)": os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
            "WINDIR": os.environ.get("WINDIR", "C:\\Windows"),
            "APPDATA": os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming")),
            "PROGRAMDATA": os.environ.get("PROGRAMDATA", "C:\\ProgramData"),
            "USERPROFILE": os.environ.get("USERPROFILE", os.path.expanduser("~")),
            "TEMP": os.environ.get("TEMP", "C:\\Temp"),
            "PROJECT_ROOT": os.environ.get("PROJECT_ROOT", os.getcwd()),
        }
        
        for var, value in env_vars.items():
            result = result.replace(f"${{{var}}}", value)
        
        self._expanded_patterns[pattern] = result
        return result
    
    def _expand_all_patterns(self) -> None:
        """Pre-expand all zone patterns."""
        for zone in self._zones:
            self._expand_env_vars(zone.pattern)
    
    def _match_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches a glob-like pattern."""
        import fnmatch
        
        expanded = self._expand_env_vars(pattern)
        
        # Normalize paths
        resource = resource.replace("\\", "/")
        expanded = expanded.replace("\\", "/")
        
        # Handle ** for recursive matching
        if "**" in expanded:
            # Convert to regex
            regex_pattern = expanded.replace("**", ".*")
            regex_pattern = regex_pattern.replace("*", "[^/]*")
            regex_pattern = f"^{regex_pattern}$"
            return bool(re.match(regex_pattern, resource, re.IGNORECASE))
        else:
            return fnmatch.fnmatch(resource.lower(), expanded.lower())
    
    def check(
        self,
        agent_id: str,
        resource: str,
        tool_name: str,
        zone_type: SafeZoneType = SafeZoneType.FILESYSTEM,
    ) -> Optional[SafeZoneViolation]:
        """
        Check if accessing a resource violates any safe zone.
        
        Args:
            agent_id: ID of the agent
            resource: Resource being accessed (path, key, etc.)
            tool_name: Tool performing the access
            zone_type: Type of safe zone to check
            
        Returns:
            Violation record if violated, None otherwise
        """
        for zone in self._zones:
            if not zone.enabled:
                continue
            
            if zone.zone_type != zone_type:
                continue
            
            if self._match_pattern(resource, zone.pattern):
                violation = SafeZoneViolation(
                    timestamp=datetime.now(),
                    agent_id=agent_id,
                    zone=zone,
                    attempted_resource=resource,
                    tool_name=tool_name,
                    action_taken=zone.action,
                )
                
                self._violations.append(violation)
                
                if self._on_violation:
                    self._on_violation(violation)
                
                return violation
        
        return None
    
    def check_path(
        self,
        agent_id: str,
        path: str,
        tool_name: str,
    ) -> Optional[SafeZoneViolation]:
        """Check if a filesystem path violates safe zones."""
        return self.check(
            agent_id=agent_id,
            resource=str(path),
            tool_name=tool_name,
            zone_type=SafeZoneType.FILESYSTEM,
        )
    
    def check_registry(
        self,
        agent_id: str,
        key: str,
        tool_name: str,
    ) -> Optional[SafeZoneViolation]:
        """Check if a registry key violates safe zones."""
        return self.check(
            agent_id=agent_id,
            resource=key,
            tool_name=tool_name,
            zone_type=SafeZoneType.REGISTRY,
        )
    
    def add_zone(self, zone: SafeZone) -> None:
        """Add a new safe zone."""
        self._zones.append(zone)
        self._expand_env_vars(zone.pattern)
    
    def remove_zone(self, pattern: str) -> bool:
        """Remove a safe zone by pattern."""
        for i, zone in enumerate(self._zones):
            if zone.pattern == pattern:
                del self._zones[i]
                return True
        return False
    
    def enable_zone(self, pattern: str) -> bool:
        """Enable a safe zone by pattern."""
        for zone in self._zones:
            if zone.pattern == pattern:
                zone.enabled = True
                return True
        return False
    
    def disable_zone(self, pattern: str) -> bool:
        """Disable a safe zone by pattern."""
        for zone in self._zones:
            if zone.pattern == pattern:
                zone.enabled = False
                return True
        return False
    
    def get_zones(
        self,
        zone_type: Optional[SafeZoneType] = None,
        enabled_only: bool = True,
    ) -> List[SafeZone]:
        """Get safe zones with optional filtering."""
        zones = self._zones
        
        if zone_type:
            zones = [z for z in zones if z.zone_type == zone_type]
        
        if enabled_only:
            zones = [z for z in zones if z.enabled]
        
        return zones
    
    def get_violations(
        self,
        agent_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SafeZoneViolation]:
        """Get recorded violations."""
        violations = self._violations
        
        if agent_id:
            violations = [v for v in violations if v.agent_id == agent_id]
        
        if since:
            violations = [v for v in violations if v.timestamp >= since]
        
        return violations[-limit:]
    
    def get_stats(self) -> dict:
        """Get safe zone statistics."""
        return {
            "total_zones": len(self._zones),
            "enabled_zones": len([z for z in self._zones if z.enabled]),
            "by_type": {
                t.value: len([z for z in self._zones if z.zone_type == t and z.enabled])
                for t in SafeZoneType
            },
            "total_violations": len(self._violations),
        }
