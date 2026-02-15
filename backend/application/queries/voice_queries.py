"""
Voice Profile Queries.

Task 3.2.2: Queries for voice profile data retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass

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
    voice_type: str | None = None
    language: str | None = None
    is_trained: bool | None = None


@dataclass
class SearchVoiceProfiles(Query):
    """Query to search voice profiles."""

    search_term: str = ""

    # Pagination
    page: int = 1
    page_size: int = 20

    # Filters
    language: str | None = None


@dataclass
class GetVoicePresets(Query):
    """Query to get built-in voice presets."""

    language: str | None = None
    gender: str | None = None


@dataclass
class GetTrainingStatus(Query):
    """Query to get voice training status."""

    profile_id: str = ""


@dataclass
class GetCompatibleEngines(Query):
    """Query to get engines compatible with a voice profile."""

    profile_id: str = ""
