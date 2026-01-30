"""
Agent Identity System

Provides unique identification, role declaration, lifecycle tracking,
and version pinning for agents.
"""

import hashlib
import platform
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AgentRole(str, Enum):
    """Declared roles for agents."""
    
    CODER = "Coder"
    TESTER = "Tester"
    SUPPORT = "Support"
    UPDATER = "Updater"
    DATA_IMPORTER = "DataImporter"
    OVERSEER = "Overseer"
    REVIEWER = "Reviewer"
    BUILDER = "Builder"
    DEBUGGER = "Debugger"
    
    @classmethod
    def from_string(cls, value: str) -> Optional["AgentRole"]:
        """Parse role from string."""
        value_lower = value.lower().strip()
        for role in cls:
            if role.value.lower() == value_lower:
                return role
        return None


class AgentState(str, Enum):
    """Lifecycle states for agents."""
    
    CREATED = "Created"
    RUNNING = "Running"
    PAUSED = "Paused"
    AWAITING_APPROVAL = "AwaitingApproval"
    COMPLETED = "Completed"
    QUARANTINED = "Quarantined"
    TERMINATED = "Terminated"
    
    def can_transition_to(self, target: "AgentState") -> bool:
        """Check if transition to target state is valid."""
        valid_transitions = {
            AgentState.CREATED: {AgentState.RUNNING, AgentState.TERMINATED},
            AgentState.RUNNING: {
                AgentState.PAUSED,
                AgentState.AWAITING_APPROVAL,
                AgentState.COMPLETED,
                AgentState.QUARANTINED,
                AgentState.TERMINATED,
            },
            AgentState.PAUSED: {AgentState.RUNNING, AgentState.TERMINATED},
            AgentState.AWAITING_APPROVAL: {
                AgentState.RUNNING,
                AgentState.PAUSED,
                AgentState.QUARANTINED,
                AgentState.TERMINATED,
            },
            AgentState.COMPLETED: set(),  # Terminal state
            AgentState.QUARANTINED: {AgentState.TERMINATED},
            AgentState.TERMINATED: set(),  # Terminal state
        }
        return target in valid_transitions.get(self, set())


@dataclass
class AgentIdentity:
    """
    Unique identity for an agent instance.
    
    Attributes:
        agent_id: UUID unique to this run
        machine_id: Hardware fingerprint of the machine
        user_id: Identifier for the user running the agent
        role: Declared role of the agent
        state: Current lifecycle state
        config_hash: Hash of prompt/tools/policy configuration
        created_at: Timestamp when agent was created
        correlation_id: ID for cross-layer tracing
        parent_agent_id: ID of parent agent if this is a subagent
        session_id: Session identifier for grouping related agents
    """
    
    agent_id: str
    machine_id: str
    user_id: str
    role: AgentRole
    state: AgentState = AgentState.CREATED
    config_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    correlation_id: str = ""
    parent_agent_id: Optional[str] = None
    session_id: str = ""
    
    def __post_init__(self):
        """Initialize computed fields."""
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    @classmethod
    def create(
        cls,
        role: AgentRole,
        user_id: str,
        config: Optional[dict] = None,
        parent_agent_id: Optional[str] = None,
    ) -> "AgentIdentity":
        """
        Factory method to create a new agent identity.
        
        Args:
            role: The role this agent will perform
            user_id: Identifier for the user
            config: Optional configuration dict to hash
            parent_agent_id: Optional parent agent ID for subagents
            
        Returns:
            A new AgentIdentity instance
        """
        agent_id = str(uuid.uuid4())
        machine_id = cls._get_machine_id()
        config_hash = cls._hash_config(config) if config else ""
        
        return cls(
            agent_id=agent_id,
            machine_id=machine_id,
            user_id=user_id,
            role=role,
            config_hash=config_hash,
            parent_agent_id=parent_agent_id,
        )
    
    @staticmethod
    def _get_machine_id() -> str:
        """
        Generate a machine fingerprint.
        
        Uses platform info to create a stable identifier.
        """
        components = [
            platform.node(),
            platform.system(),
            platform.machine(),
            platform.processor(),
        ]
        fingerprint = "|".join(components)
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
    
    @staticmethod
    def _hash_config(config: dict) -> str:
        """Hash a configuration dictionary."""
        import json
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def transition_to(self, new_state: AgentState) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: The target state
            
        Returns:
            True if transition succeeded, False otherwise
        """
        if self.state.can_transition_to(new_state):
            self.state = new_state
            return True
        return False
    
    def is_active(self) -> bool:
        """Check if agent is in an active (non-terminal) state."""
        return self.state in {
            AgentState.CREATED,
            AgentState.RUNNING,
            AgentState.PAUSED,
            AgentState.AWAITING_APPROVAL,
        }
    
    def is_terminal(self) -> bool:
        """Check if agent is in a terminal state."""
        return self.state in {
            AgentState.COMPLETED,
            AgentState.QUARANTINED,
            AgentState.TERMINATED,
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "machine_id": self.machine_id,
            "user_id": self.user_id,
            "role": self.role.value,
            "state": self.state.value,
            "config_hash": self.config_hash,
            "created_at": self.created_at.isoformat(),
            "correlation_id": self.correlation_id,
            "parent_agent_id": self.parent_agent_id,
            "session_id": self.session_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AgentIdentity":
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            machine_id=data["machine_id"],
            user_id=data["user_id"],
            role=AgentRole(data["role"]),
            state=AgentState(data["state"]),
            config_hash=data.get("config_hash", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            correlation_id=data.get("correlation_id", ""),
            parent_agent_id=data.get("parent_agent_id"),
            session_id=data.get("session_id", ""),
        )
