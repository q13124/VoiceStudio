"""
Voice Browser Routes

Endpoints for browsing and discovering voice profiles, samples, and models.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from ..optimization import cache_response
except ImportError:

    def cache_response(ttl: int = 300):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice-browser", tags=["voice-browser"])

# In-memory voice catalog (replace with database in production)
_voice_catalog: Dict[str, Dict] = {}


class VoiceProfileSummary(BaseModel):
    """Summary of a voice profile for browsing."""

    id: str
    name: str
    description: Optional[str] = None
    language: str
    gender: Optional[str] = None
    age_range: Optional[str] = None
    quality_score: float
    sample_count: int
    tags: List[str] = []
    preview_audio_id: Optional[str] = None
    created: str  # ISO datetime string


class VoiceSearchRequest(BaseModel):
    """Request for voice search."""

    query: Optional[str] = None
    language: Optional[str] = None
    gender: Optional[str] = None
    min_quality_score: Optional[float] = None
    tags: List[str] = []
    limit: int = 50
    offset: int = 0


class VoiceSearchResponse(BaseModel):
    """Response from voice search."""

    voices: List[VoiceProfileSummary]
    total: int
    limit: int
    offset: int


@router.get("/voices", response_model=VoiceSearchResponse)
@cache_response(ttl=60)  # Cache for 60 seconds (voice searches change moderately)
async def search_voices(
    query: Optional[str] = None,
    language: Optional[str] = None,
    gender: Optional[str] = None,
    min_quality_score: Optional[float] = None,
    tags: Optional[str] = None,  # Comma-separated
    limit: int = 50,
    offset: int = 0,
):
    """Search and browse voice profiles."""
    voices = list(_voice_catalog.values())

    # Apply filters
    if query:
        query_lower = query.lower()
        voices = [
            v
            for v in voices
            if query_lower in v.get("name", "").lower()
            or query_lower in v.get("description", "").lower()
        ]

    if language:
        voices = [v for v in voices if v.get("language") == language]

    if gender:
        voices = [v for v in voices if v.get("gender") == gender]

    if min_quality_score is not None:
        voices = [v for v in voices if v.get("quality_score", 0.0) >= min_quality_score]

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        voices = [
            v for v in voices if any(tag in v.get("tags", []) for tag in tag_list)
        ]

    # Sort by quality score (descending)
    voices.sort(key=lambda v: v.get("quality_score", 0.0), reverse=True)

    # Paginate
    total = len(voices)
    voices = voices[offset : offset + limit]

    return VoiceSearchResponse(
        voices=[
            VoiceProfileSummary(
                id=str(v.get("id", "")),
                name=str(v.get("name", "")),
                description=v.get("description"),
                language=str(v.get("language", "")),
                gender=v.get("gender"),
                age_range=v.get("age_range"),
                quality_score=v.get("quality_score", 0.0),
                sample_count=v.get("sample_count", 0),
                tags=v.get("tags", []),
                preview_audio_id=v.get("preview_audio_id"),
                created=str(v.get("created", "")),
            )
            for v in voices
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/voices/{voice_id}", response_model=VoiceProfileSummary)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (individual voices change less frequently)
async def get_voice_summary(voice_id: str):
    """Get detailed summary of a voice profile."""
    if voice_id not in _voice_catalog:
        raise HTTPException(status_code=404, detail="Voice not found")

    v = _voice_catalog[voice_id]
    return VoiceProfileSummary(
        id=str(v.get("id", "")),
        name=str(v.get("name", "")),
        description=v.get("description"),
        language=str(v.get("language", "")),
        gender=v.get("gender"),
        age_range=v.get("age_range"),
        quality_score=v.get("quality_score", 0.0),
        sample_count=v.get("sample_count", 0),
        tags=v.get("tags", []),
        preview_audio_id=v.get("preview_audio_id"),
        created=str(v.get("created", "")),
    )


@router.get("/languages")
@cache_response(ttl=600)  # Cache for 10 minutes (languages are relatively static)
async def get_available_languages():
    """Get list of available languages in voice catalog."""
    languages = set()
    for v in _voice_catalog.values():
        lang = v.get("language")
        if lang:
            languages.add(lang)

    return {"languages": sorted(list(languages))}


@router.get("/tags")
async def get_available_tags():
    """Get list of available tags in voice catalog."""
    tags = set()
    for v in _voice_catalog.values():
        for tag in v.get("tags", []):
            tags.add(tag)

    return {"tags": sorted(list(tags))}
