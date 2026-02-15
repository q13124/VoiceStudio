"""Application queries package."""

from backend.application.queries.base import Query, QueryHandler, QueryResult
from backend.application.queries.project_queries import (
    GetProject,
    ListProjects,
    SearchProjects,
)
from backend.application.queries.voice_queries import (
    GetVoiceProfile,
    ListVoiceProfiles,
)

__all__ = [
    "GetProject",
    "GetVoiceProfile",
    "ListProjects",
    "ListVoiceProfiles",
    "Query",
    "QueryHandler",
    "QueryResult",
    "SearchProjects",
]
