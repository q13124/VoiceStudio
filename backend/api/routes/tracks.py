"""
Timeline Tracks and Clips Management Routes

CRUD operations for audio tracks and clips in projects.
"""

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models import ApiOk
from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/tracks", tags=["tracks"])


class AudioClip(BaseModel):
    id: str
    name: str
    profile_id: str
    audio_id: str
    audio_url: str
    duration_seconds: float
    start_time: float
    engine: Optional[str] = None
    quality_score: Optional[float] = None


class AudioTrack(BaseModel):
    id: str
    name: str
    project_id: str
    clips: List[AudioClip] = []
    track_number: int
    engine: Optional[str] = None


class TrackCreateRequest(BaseModel):
    name: str
    engine: Optional[str] = None


class TrackUpdateRequest(BaseModel):
    name: Optional[str] = None
    engine: Optional[str] = None


class ClipCreateRequest(BaseModel):
    name: str
    profile_id: str
    audio_id: str
    audio_url: str
    duration_seconds: float
    start_time: float
    engine: Optional[str] = None
    quality_score: Optional[float] = None


class ClipUpdateRequest(BaseModel):
    name: Optional[str] = None
    start_time: Optional[float] = None


# In-memory storage (replace with database in production)
_tracks: dict[str, AudioTrack] = {}
_clips: dict[str, AudioClip] = {}
_MAX_TRACKS = 1000  # Maximum number of tracks
_MAX_CLIPS = 10000  # Maximum number of clips


def _cleanup_old_tracks():
    """
    Clean up old tracks and clips from storage to prevent memory accumulation.

    Removes tracks/clips beyond MAX_TRACKS/MAX_CLIPS (oldest first based on
    track creation order).
    """
    # If tracks exceed limit, remove oldest (by track number)
    if len(_tracks) > _MAX_TRACKS:
        sorted_tracks = sorted(
            _tracks.items(),
            key=lambda x: x[1].track_number,
        )
        excess = len(_tracks) - _MAX_TRACKS
        for track_key, track in sorted_tracks[:excess]:
            # Delete all clips in this track
            for clip in track.clips:
                if clip.id in _clips:
                    del _clips[clip.id]
            del _tracks[track_key]
        logger.info(f"Cleaned up {excess} old tracks from storage")

    # If clips exceed limit, remove oldest (by track order)
    if len(_clips) > _MAX_CLIPS:
        # Sort clips by their track's track_number
        clip_track_map = {}
        for track_key, track in _tracks.items():
            for clip in track.clips:
                clip_track_map[clip.id] = track.track_number

        sorted_clips = sorted(
            _clips.items(),
            key=lambda x: clip_track_map.get(x[0], 999999),
        )
        excess = len(_clips) - _MAX_CLIPS
        for clip_id, clip in sorted_clips[:excess]:
            # Remove clip from its track
            for track in _tracks.values():
                if clip in track.clips:
                    track.clips.remove(clip)
                    break
            del _clips[clip_id]
        logger.info(f"Cleaned up {excess} old clips from storage")


def _get_track_key(project_id: str, track_id: str) -> str:
    """Generate a unique key for track storage."""
    return f"{project_id}:{track_id}"


@router.get("", response_model=List[AudioTrack])
@cache_response(ttl=30)  # Cache for 30 seconds (tracks may change frequently)
def list_tracks(project_id: str) -> List[AudioTrack]:
    """List all tracks for a project."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")

        project_tracks = [
            track for track in _tracks.values() if track.project_id == project_id
        ]
        # Sort by track number
        project_tracks.sort(key=lambda t: t.track_number)

        logger.info(f"Listed {len(project_tracks)} tracks for project: {project_id}")
        return project_tracks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error listing tracks for project {project_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to list tracks: {str(e)}")


@router.get("/{track_id}", response_model=AudioTrack)
@cache_response(ttl=60)  # Cache for 60 seconds (track info is relatively static)
def get_track(project_id: str, track_id: str) -> AudioTrack:
    """Get a specific track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")

        track_key = _get_track_key(project_id, track_id)
        if track_key not in _tracks:
            logger.warning(f"Track not found: {track_id} in project: {project_id}")
            raise HTTPException(status_code=404, detail="Track not found")

        logger.info(f"Retrieved track: {track_id} from project: {project_id}")
        return _tracks[track_key]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting track {track_id} from project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to get track: {str(e)}")


@router.post("", response_model=AudioTrack)
def create_track(project_id: str, req: TrackCreateRequest) -> AudioTrack:
    """Create a new track in a project."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not req.name or not req.name.strip():
            raise HTTPException(status_code=400, detail="Track name is required")

        # Get existing tracks to determine track number
        existing_tracks = [
            track for track in _tracks.values() if track.project_id == project_id
        ]
        track_number = (
            max(
                [t.track_number for t in existing_tracks],
                default=0,
            )
            + 1
        )

        track_id = str(uuid.uuid4())
        track_key = _get_track_key(project_id, track_id)

        track = AudioTrack(
            id=track_id,
            name=req.name.strip(),
            project_id=project_id,
            clips=[],
            track_number=track_number,
            engine=req.engine,
        )

        _tracks[track_key] = track

        # Clean up old tracks if needed
        if len(_tracks) > _MAX_TRACKS:
            _cleanup_old_tracks()

        logger.info(f"Created track: {track_id} ({req.name}) in project: {project_id}")
        return track
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error creating track in project {project_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to create track: {str(e)}")


@router.put("/{track_id}", response_model=AudioTrack)
def update_track(project_id: str, track_id: str, req: TrackUpdateRequest) -> AudioTrack:
    """Update an existing track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")
        if req.name is not None and (not req.name or not req.name.strip()):
            raise HTTPException(status_code=400, detail="Track name cannot be empty")

        track_key = _get_track_key(project_id, track_id)
        if track_key not in _tracks:
            logger.warning(
                f"Track not found for update: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        track = _tracks[track_key]

        if req.name is not None:
            track.name = req.name.strip()
        if req.engine is not None:
            track.engine = req.engine

        logger.info(f"Updated track: {track_id} in project: {project_id}")
        return track
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating track {track_id} in project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to update track: {str(e)}")


@router.delete("/{track_id}", response_model=ApiOk)
def delete_track(project_id: str, track_id: str) -> ApiOk:
    """Delete a track and all its clips."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")

        track_key = _get_track_key(project_id, track_id)
        if track_key not in _tracks:
            logger.warning(
                f"Track not found for deletion: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        track = _tracks[track_key]
        clip_count = len(track.clips)

        # Delete all clips in this track
        for clip in track.clips:
            if clip.id in _clips:
                del _clips[clip.id]

        del _tracks[track_key]
        logger.info(
            f"Deleted track: {track_id} with {clip_count} clips from project: {project_id}"
        )
        return ApiOk()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting track {track_id} from project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to delete track: {str(e)}")


# Clip endpoints
@router.post("/{track_id}/clips", response_model=AudioClip)
def create_clip(project_id: str, track_id: str, req: ClipCreateRequest) -> AudioClip:
    """Add a clip to a track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")
        if not req.name or not req.name.strip():
            raise HTTPException(status_code=400, detail="Clip name is required")
        if not req.profile_id or not req.profile_id.strip():
            raise HTTPException(status_code=400, detail="Profile ID is required")
        if not req.audio_id or not req.audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")
        if req.duration_seconds < 0:
            raise HTTPException(status_code=400, detail="Duration cannot be negative")
        if req.start_time < 0:
            raise HTTPException(status_code=400, detail="Start time cannot be negative")

        track_key = _get_track_key(project_id, track_id)
        if track_key not in _tracks:
            logger.warning(
                f"Track not found for clip creation: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        track = _tracks[track_key]

        clip_id = str(uuid.uuid4())
        clip = AudioClip(
            id=clip_id,
            name=req.name.strip(),
            profile_id=req.profile_id,
            audio_id=req.audio_id,
            audio_url=req.audio_url,
            duration_seconds=req.duration_seconds,
            start_time=req.start_time,
            engine=req.engine,
            quality_score=req.quality_score,
        )

        track.clips.append(clip)
        _clips[clip_id] = clip

        # Clean up old clips if needed
        if len(_clips) > _MAX_CLIPS:
            _cleanup_old_tracks()

        logger.info(
            f"Added clip: {clip_id} ({req.name}) to track: {track_id} in project: {project_id}"
        )
        return clip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error creating clip in track {track_id} of project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to create clip: {str(e)}")


@router.put("/{track_id}/clips/{clip_id}", response_model=AudioClip)
def update_clip(
    project_id: str, track_id: str, clip_id: str, req: ClipUpdateRequest
) -> AudioClip:
    """Update a clip in a track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")
        if not clip_id or not clip_id.strip():
            raise HTTPException(status_code=400, detail="Clip ID is required")
        if req.name is not None and (not req.name or not req.name.strip()):
            raise HTTPException(status_code=400, detail="Clip name cannot be empty")
        if req.start_time is not None and req.start_time < 0:
            raise HTTPException(status_code=400, detail="Start time cannot be negative")

        track_key = _get_track_key(project_id, track_id)
        if track_key not in _tracks:
            logger.warning(
                f"Track not found for clip update: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        track = _tracks[track_key]
        clip = next((c for c in track.clips if c.id == clip_id), None)

        if not clip:
            logger.warning(f"Clip not found for update: {clip_id} in track: {track_id}")
            raise HTTPException(status_code=404, detail="Clip not found")

        if req.name is not None:
            clip.name = req.name.strip()
        if req.start_time is not None:
            clip.start_time = req.start_time

        logger.info(
            f"Updated clip: {clip_id} in track: {track_id} of project: {project_id}"
        )
        return clip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating clip {clip_id} in track {track_id} of project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to update clip: {str(e)}")


@router.delete("/{track_id}/clips/{clip_id}", response_model=ApiOk)
def delete_clip(project_id: str, track_id: str, clip_id: str) -> ApiOk:
    """Delete a clip from a track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")
        if not clip_id or not clip_id.strip():
            raise HTTPException(status_code=400, detail="Clip ID is required")

        track_key = _get_track_key(project_id, track_id)
        if track_key not in _tracks:
            logger.warning(
                f"Track not found for clip deletion: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        track = _tracks[track_key]
        clip = next((c for c in track.clips if c.id == clip_id), None)

        if not clip:
            logger.warning(
                f"Clip not found for deletion: {clip_id} in track: {track_id}"
            )
            raise HTTPException(status_code=404, detail="Clip not found")

        track.clips.remove(clip)
        if clip_id in _clips:
            del _clips[clip_id]

        logger.info(
            f"Deleted clip: {clip_id} from track: {track_id} in project: {project_id}"
        )
        return ApiOk()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting clip {clip_id} from track {track_id} of project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to delete clip: {str(e)}")
