"""
Voice Profile Queries.

Task 3.2.2: Queries for voice profile data retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from backend.application.queries.base import Query


@dataclass
class GetVoiceProfile(Query):
    """Query to get a single voice profile by ID."""
    
    profile_id: str = ""
    include_samples: bool = False


@dataclass
class ListVoiceProfiles(Query):
    """Query to list all voice profiles."""
    
    # Pagination
    page: int = 1
    page_size: int = 20
    
    # Sorting
    sort_by: str = "name"
    sort_desc: bool = False
    
    # Filters
    voice_type: Optional[str] = None
    language: Optional[str] = None
    is_trained: Optional[bool] = None


@dataclass
class SearchVoiceProfiles(Query):
    """Query to search voice profiles."""
    
    search_term: str = ""
    
    # Pagination
    page: int = 1
    page_size: int = 20
    
    # Filters
    language: Optional[str] = None


@dataclass
class GetVoicePresets(Query):
    """Query to get built-in voice presets."""
    
    language: Optional[str] = None
    gender: Optional[str] = None


@dataclass
class GetTrainingStatus(Query):
    """Query to get voice training status."""
    
    profile_id: str = ""


@dataclass
class GetCompatibleEngines(Query):
    """Query to get engines compatible with a voice profile."""
    
    profile_id: str = ""
