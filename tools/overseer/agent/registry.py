"""
Agent Registry

Tracks all agent instances, their states, and provides lookup functionality.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .identity import AgentIdentity, AgentRole, AgentState


class AgentRegistry:
    """
    Central registry for tracking all agent instances.
    
    Thread-safe registry that maintains agent state and provides
    persistence to disk.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the registry.
        
        Args:
            storage_path: Optional path for persistent storage.
                         Defaults to %APPDATA%/VoiceStudio/agent_registry.json
        """
        self._agents: Dict[str, AgentIdentity] = {}
        self._lock = threading.RLock()
        
        if storage_path:
            self._storage_path = storage_path
        else:
            import os
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._storage_path = Path(appdata) / "VoiceStudio" / "agent_registry.json"
        
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()
    
    def _load(self) -> None:
        """Load registry from disk."""
        if self._storage_path.exists():
            try:
                data = json.loads(self._storage_path.read_text(encoding="utf-8"))
                for agent_data in data.get("agents", []):
                    try:
                        agent = AgentIdentity.from_dict(agent_data)
                        self._agents[agent.agent_id] = agent
                    except (KeyError, ValueError):
                        continue  # Skip malformed entries
            except (json.JSONDecodeError, IOError):
                pass  # Start with empty registry
    
    def _save(self) -> None:
        """Save registry to disk."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "agents": [agent.to_dict() for agent in self._agents.values()],
        }
        self._storage_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
    
    def register(self, agent: AgentIdentity) -> None:
        """
        Register a new agent.
        
        Args:
            agent: The agent identity to register
            
        Raises:
            ValueError: If agent ID already exists
        """
        with self._lock:
            if agent.agent_id in self._agents:
                raise ValueError(f"Agent {agent.agent_id} already registered")
            self._agents[agent.agent_id] = agent
            self._save()
    
    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: The agent ID to unregister
            
        Returns:
            True if agent was found and removed, False otherwise
        """
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                self._save()
                return True
            return False
    
    def get(self, agent_id: str) -> Optional[AgentIdentity]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The agent ID to look up
            
        Returns:
            The agent identity, or None if not found
        """
        with self._lock:
            return self._agents.get(agent_id)
    
    def update_state(self, agent_id: str, new_state: AgentState) -> bool:
        """
        Update an agent's state.
        
        Args:
            agent_id: The agent ID to update
            new_state: The new state
            
        Returns:
            True if update succeeded, False otherwise
        """
        with self._lock:
            agent = self._agents.get(agent_id)
            if agent and agent.transition_to(new_state):
                self._save()
                return True
            return False
    
    def get_by_role(self, role: AgentRole) -> List[AgentIdentity]:
        """Get all agents with a specific role."""
        with self._lock:
            return [a for a in self._agents.values() if a.role == role]
    
    def get_by_state(self, state: AgentState) -> List[AgentIdentity]:
        """Get all agents in a specific state."""
        with self._lock:
            return [a for a in self._agents.values() if a.state == state]
    
    def get_active(self) -> List[AgentIdentity]:
        """Get all active (non-terminal) agents."""
        with self._lock:
            return [a for a in self._agents.values() if a.is_active()]
    
    def get_by_session(self, session_id: str) -> List[AgentIdentity]:
        """Get all agents in a session."""
        with self._lock:
            return [a for a in self._agents.values() if a.session_id == session_id]
    
    def get_by_user(self, user_id: str) -> List[AgentIdentity]:
        """Get all agents for a user."""
        with self._lock:
            return [a for a in self._agents.values() if a.user_id == user_id]

    def list_all(self) -> List[AgentIdentity]:
        """Return all registered agents."""
        with self._lock:
            return list(self._agents.values())
    
    def get_by_machine(self, machine_id: str) -> List[AgentIdentity]:
        """Get all agents on a machine."""
        with self._lock:
            return [a for a in self._agents.values() if a.machine_id == machine_id]
    
    def get_children(self, parent_agent_id: str) -> List[AgentIdentity]:
        """Get all child agents of a parent."""
        with self._lock:
            return [
                a for a in self._agents.values()
                if a.parent_agent_id == parent_agent_id
            ]
    
    def quarantine(self, agent_id: str) -> bool:
        """
        Quarantine an agent immediately.
        
        Args:
            agent_id: The agent to quarantine
            
        Returns:
            True if quarantine succeeded
        """
        return self.update_state(agent_id, AgentState.QUARANTINED)
    
    def terminate(self, agent_id: str) -> bool:
        """
        Terminate an agent.
        
        Args:
            agent_id: The agent to terminate
            
        Returns:
            True if termination succeeded
        """
        return self.update_state(agent_id, AgentState.TERMINATED)
    
    def terminate_all_on_machine(self, machine_id: str) -> int:
        """
        Terminate all agents on a machine (kill switch).
        
        Args:
            machine_id: The machine ID
            
        Returns:
            Number of agents terminated
        """
        count = 0
        with self._lock:
            for agent in list(self._agents.values()):
                if agent.machine_id == machine_id and agent.is_active():
                    if agent.transition_to(AgentState.TERMINATED):
                        count += 1
            if count > 0:
                self._save()
        return count
    
    def cleanup_terminal(self, older_than_hours: int = 24) -> int:
        """
        Remove terminal agents older than specified hours.
        
        Args:
            older_than_hours: Age threshold in hours
            
        Returns:
            Number of agents cleaned up
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        
        count = 0
        with self._lock:
            to_remove = []
            for agent_id, agent in self._agents.items():
                if agent.is_terminal() and agent.created_at < cutoff:
                    to_remove.append(agent_id)
            
            for agent_id in to_remove:
                del self._agents[agent_id]
                count += 1
            
            if count > 0:
                self._save()
        
        return count
    
    def get_stats(self) -> dict:
        """Get registry statistics."""
        with self._lock:
            by_state = {}
            by_role = {}
            
            for agent in self._agents.values():
                by_state[agent.state.value] = by_state.get(agent.state.value, 0) + 1
                by_role[agent.role.value] = by_role.get(agent.role.value, 0) + 1
            
            return {
                "total": len(self._agents),
                "active": len([a for a in self._agents.values() if a.is_active()]),
                "terminal": len([a for a in self._agents.values() if a.is_terminal()]),
                "by_state": by_state,
                "by_role": by_role,
            }
    
    def __len__(self) -> int:
        """Return number of registered agents."""
        with self._lock:
            return len(self._agents)
    
    def __contains__(self, agent_id: str) -> bool:
        """Check if agent ID is registered."""
        with self._lock:
            return agent_id in self._agents
