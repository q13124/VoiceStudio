"""
Kill Switch

Emergency controls for agent governance.
Provides per-agent, per-machine, and global kill switches.
"""

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set


class KillSwitchLevel(str, Enum):
    """Levels of kill switch activation."""
    
    AGENT = "Agent"           # Stop specific agent
    SESSION = "Session"       # Stop all agents in a session
    MACHINE = "Machine"       # Stop all agents on this machine
    USER = "User"             # Stop all agents for a user
    GLOBAL = "Global"         # Stop everything


class KillSwitchState(str, Enum):
    """State of a kill switch."""
    
    INACTIVE = "Inactive"     # Normal operation
    ACTIVE = "Active"         # Kill switch engaged
    PENDING = "Pending"       # Waiting for confirmation


@dataclass
class KillSwitchActivation:
    """
    Record of a kill switch activation.
    
    Attributes:
        activation_id: Unique identifier
        level: Level of the kill switch
        target_id: ID of the target (agent, machine, user, or "*" for global)
        activated_at: When activated
        activated_by: Who activated it
        reason: Reason for activation
        deactivated_at: When deactivated (if applicable)
        deactivated_by: Who deactivated it
    """
    
    activation_id: str
    level: KillSwitchLevel
    target_id: str
    activated_at: datetime
    activated_by: str
    reason: str
    deactivated_at: Optional[datetime] = None
    deactivated_by: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        """Check if the activation is still active."""
        return self.deactivated_at is None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "activation_id": self.activation_id,
            "level": self.level.value,
            "target_id": self.target_id,
            "activated_at": self.activated_at.isoformat(),
            "activated_by": self.activated_by,
            "reason": self.reason,
            "deactivated_at": self.deactivated_at.isoformat() if self.deactivated_at else None,
            "deactivated_by": self.deactivated_by,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "KillSwitchActivation":
        """Create from dictionary."""
        return cls(
            activation_id=data["activation_id"],
            level=KillSwitchLevel(data["level"]),
            target_id=data["target_id"],
            activated_at=datetime.fromisoformat(data["activated_at"]),
            activated_by=data["activated_by"],
            reason=data["reason"],
            deactivated_at=(
                datetime.fromisoformat(data["deactivated_at"])
                if data.get("deactivated_at")
                else None
            ),
            deactivated_by=data.get("deactivated_by"),
        )


class KillSwitch:
    """
    Emergency kill switch system for agent governance.
    
    Provides multiple levels of emergency stop:
    - Agent: Stop a specific agent
    - Session: Stop all agents in a session
    - Machine: Stop all agents on this machine
    - User: Stop all agents for a user
    - Global: Stop everything
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        on_activate: Optional[Callable[[KillSwitchActivation], None]] = None,
        on_deactivate: Optional[Callable[[KillSwitchActivation], None]] = None,
    ):
        """
        Initialize the kill switch system.
        
        Args:
            storage_path: Path for persistent storage
            on_activate: Callback when kill switch is activated
            on_deactivate: Callback when kill switch is deactivated
        """
        if storage_path:
            self._storage_path = storage_path
        else:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._storage_path = Path(appdata) / "VoiceStudio" / "kill_switches.json"
        
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._on_activate = on_activate
        self._on_deactivate = on_deactivate
        
        # Active kill switches
        self._activations: Dict[str, KillSwitchActivation] = {}
        self._lock = threading.RLock()
        
        # Quick lookup indexes
        self._by_level: Dict[KillSwitchLevel, Set[str]] = {
            level: set() for level in KillSwitchLevel
        }
        
        # Load persisted state
        self._load()
    
    def _load(self) -> None:
        """Load persisted kill switch state."""
        if not self._storage_path.exists():
            return
        
        try:
            data = json.loads(self._storage_path.read_text(encoding="utf-8"))
            for activation_data in data.get("activations", []):
                try:
                    activation = KillSwitchActivation.from_dict(activation_data)
                    if activation.is_active:
                        self._activations[activation.activation_id] = activation
                        self._by_level[activation.level].add(activation.target_id)
                except (KeyError, ValueError):
                    continue
        except (json.JSONDecodeError, IOError):
            pass
    
    def _save(self) -> None:
        """Save kill switch state to disk."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "activations": [
                a.to_dict() for a in self._activations.values()
            ],
        }
        self._storage_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
    
    def _generate_id(self) -> str:
        """Generate a unique activation ID."""
        import uuid
        return str(uuid.uuid4())
    
    def activate(
        self,
        level: KillSwitchLevel,
        target_id: str,
        activated_by: str,
        reason: str,
    ) -> KillSwitchActivation:
        """
        Activate a kill switch.
        
        Args:
            level: Level of the kill switch
            target_id: ID of the target
            activated_by: Who is activating
            reason: Reason for activation
            
        Returns:
            The activation record
        """
        with self._lock:
            activation = KillSwitchActivation(
                activation_id=self._generate_id(),
                level=level,
                target_id=target_id,
                activated_at=datetime.now(),
                activated_by=activated_by,
                reason=reason,
            )
            
            self._activations[activation.activation_id] = activation
            self._by_level[level].add(target_id)
            self._save()
            
            if self._on_activate:
                self._on_activate(activation)
            
            return activation
    
    def deactivate(
        self,
        activation_id: str,
        deactivated_by: str,
    ) -> bool:
        """
        Deactivate a kill switch.
        
        Args:
            activation_id: ID of the activation to deactivate
            deactivated_by: Who is deactivating
            
        Returns:
            True if deactivated, False if not found
        """
        with self._lock:
            activation = self._activations.get(activation_id)
            if activation is None or not activation.is_active:
                return False
            
            activation.deactivated_at = datetime.now()
            activation.deactivated_by = deactivated_by
            
            # Check if there are other active activations for this target
            other_active = any(
                a.is_active and a.target_id == activation.target_id and a.level == activation.level
                for a in self._activations.values()
                if a.activation_id != activation_id
            )
            
            if not other_active:
                self._by_level[activation.level].discard(activation.target_id)
            
            self._save()
            
            if self._on_deactivate:
                self._on_deactivate(activation)
            
            return True
    
    def deactivate_all(
        self,
        level: Optional[KillSwitchLevel] = None,
        deactivated_by: str = "system",
    ) -> int:
        """
        Deactivate all kill switches.
        
        Args:
            level: Optional level filter
            deactivated_by: Who is deactivating
            
        Returns:
            Number of deactivations
        """
        count = 0
        with self._lock:
            for activation in list(self._activations.values()):
                if activation.is_active:
                    if level is None or activation.level == level:
                        activation.deactivated_at = datetime.now()
                        activation.deactivated_by = deactivated_by
                        self._by_level[activation.level].discard(activation.target_id)
                        
                        if self._on_deactivate:
                            self._on_deactivate(activation)
                        
                        count += 1
            
            if count > 0:
                self._save()
        
        return count
    
    def is_blocked(
        self,
        agent_id: str,
        session_id: Optional[str] = None,
        machine_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[KillSwitchActivation]:
        """
        Check if an agent is blocked by any kill switch.
        
        Args:
            agent_id: Agent ID to check
            session_id: Optional session ID
            machine_id: Optional machine ID
            user_id: Optional user ID
            
        Returns:
            The blocking activation if blocked, None otherwise
        """
        with self._lock:
            # Check in order of severity
            
            # Global kill switch
            if "*" in self._by_level[KillSwitchLevel.GLOBAL]:
                for a in self._activations.values():
                    if a.is_active and a.level == KillSwitchLevel.GLOBAL:
                        return a
            
            # Machine-level
            if machine_id and machine_id in self._by_level[KillSwitchLevel.MACHINE]:
                for a in self._activations.values():
                    if a.is_active and a.level == KillSwitchLevel.MACHINE and a.target_id == machine_id:
                        return a
            
            # User-level
            if user_id and user_id in self._by_level[KillSwitchLevel.USER]:
                for a in self._activations.values():
                    if a.is_active and a.level == KillSwitchLevel.USER and a.target_id == user_id:
                        return a
            
            # Session-level
            if session_id and session_id in self._by_level[KillSwitchLevel.SESSION]:
                for a in self._activations.values():
                    if a.is_active and a.level == KillSwitchLevel.SESSION and a.target_id == session_id:
                        return a
            
            # Agent-level
            if agent_id in self._by_level[KillSwitchLevel.AGENT]:
                for a in self._activations.values():
                    if a.is_active and a.level == KillSwitchLevel.AGENT and a.target_id == agent_id:
                        return a
            
            return None
    
    def kill_agent(self, agent_id: str, activated_by: str, reason: str) -> KillSwitchActivation:
        """Convenience method to kill a specific agent."""
        return self.activate(KillSwitchLevel.AGENT, agent_id, activated_by, reason)
    
    def kill_session(self, session_id: str, activated_by: str, reason: str) -> KillSwitchActivation:
        """Convenience method to kill all agents in a session."""
        return self.activate(KillSwitchLevel.SESSION, session_id, activated_by, reason)
    
    def kill_machine(self, machine_id: str, activated_by: str, reason: str) -> KillSwitchActivation:
        """Convenience method to kill all agents on a machine."""
        return self.activate(KillSwitchLevel.MACHINE, machine_id, activated_by, reason)
    
    def kill_all(self, activated_by: str, reason: str) -> KillSwitchActivation:
        """Convenience method to activate global kill switch."""
        return self.activate(KillSwitchLevel.GLOBAL, "*", activated_by, reason)
    
    def get_active_activations(
        self,
        level: Optional[KillSwitchLevel] = None,
    ) -> List[KillSwitchActivation]:
        """Get all active activations."""
        with self._lock:
            activations = [a for a in self._activations.values() if a.is_active]
            
            if level:
                activations = [a for a in activations if a.level == level]
            
            return activations
    
    def get_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[KillSwitchActivation]:
        """Get activation history."""
        with self._lock:
            activations = list(self._activations.values())
            
            if start_date:
                activations = [a for a in activations if a.activated_at >= start_date]
            
            if end_date:
                activations = [a for a in activations if a.activated_at <= end_date]
            
            # Sort by activation time, newest first
            activations.sort(key=lambda a: a.activated_at, reverse=True)
            
            return activations[:limit]
    
    def is_global_kill_active(self) -> bool:
        """Check if global kill switch is active."""
        return "*" in self._by_level[KillSwitchLevel.GLOBAL]
    
    def get_stats(self) -> dict:
        """Get kill switch statistics."""
        with self._lock:
            active_by_level = {
                level.value: len(targets)
                for level, targets in self._by_level.items()
            }
            
            return {
                "global_kill_active": self.is_global_kill_active(),
                "total_active": sum(1 for a in self._activations.values() if a.is_active),
                "total_historical": len(self._activations),
                "active_by_level": active_by_level,
            }
