"""
Project Domain Events.

Task 3.1.3: Events for project lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from backend.domain.events.base import DomainEvent


@dataclass
class ProjectCreated(DomainEvent):
    """Event raised when a project is created."""
    
    project_id: str = ""
    name: str = ""
    created_by: Optional[str] = None
    
    def __post_init__(self):
        self.aggregate_id = self.project_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "created_by": self.created_by,
        }


@dataclass
class ProjectUpdated(DomainEvent):
    """Event raised when a project is updated."""
    
    project_id: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        self.aggregate_id = self.project_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "changes": self.changes,
            "updated_by": self.updated_by,
        }


@dataclass
class ProjectDeleted(DomainEvent):
    """Event raised when a project is deleted."""
    
    project_id: str = ""
    name: str = ""
    deleted_by: Optional[str] = None
    
    def __post_init__(self):
        self.aggregate_id = self.project_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "deleted_by": self.deleted_by,
        }


@dataclass
class ProjectStatusChanged(DomainEvent):
    """Event raised when project status changes."""
    
    project_id: str = ""
    old_status: str = ""
    new_status: str = ""
    
    def __post_init__(self):
        self.aggregate_id = self.project_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
        }
