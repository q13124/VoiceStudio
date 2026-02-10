"""
Project Queries.

Task 3.2.2: Queries for project data retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from backend.application.queries.base import Query


@dataclass
class GetProject(Query):
    """Query to get a single project by ID."""
    
    project_id: str = ""
    include_clips: bool = False
    include_profiles: bool = False


@dataclass
class ListProjects(Query):
    """Query to list all projects."""
    
    # Pagination
    page: int = 1
    page_size: int = 20
    
    # Sorting
    sort_by: str = "updated_at"
    sort_desc: bool = True
    
    # Filters
    status: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class SearchProjects(Query):
    """Query to search projects."""
    
    search_term: str = ""
    
    # Pagination
    page: int = 1
    page_size: int = 20
    
    # Filters
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None


@dataclass
class GetProjectStats(Query):
    """Query to get project statistics."""
    
    project_id: str = ""


@dataclass
class GetRecentProjects(Query):
    """Query to get recently accessed projects."""
    
    limit: int = 10


@dataclass
class GetProjectHistory(Query):
    """Query to get project version history."""
    
    project_id: str = ""
    limit: int = 50
