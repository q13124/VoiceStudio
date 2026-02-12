"""
Timeline Tracks and Clips Management Routes

CRUD operations for audio tracks and clips in projects.
Uses TrackStore for persistent, disk-backed storage.
Integrates ArtifactRefCounter for audio artifact lifecycle management.
Supports undo/redo via EditHistory.
"""

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..deps import (
    TrackStoreDep,
    ArtifactRefCounterDep,
    EditHistoryDep,
    get_track_store_dep,
    get_ref_counter_dep,
    get_edit_history_dep,
)
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


# TrackStore is now used for persistent storage
# Legacy in-memory dicts removed - use TrackStoreDep dependency instead


def _track_dict_to_model(track_data: dict) -> AudioTrack:
    """Convert track dict from store to AudioTrack model."""
    clips = []
    for clip_data in track_data.get("clips", []):
        clips.append(AudioClip(
            id=clip_data.get("id", ""),
            name=clip_data.get("name", ""),
            profile_id=clip_data.get("profile_id", ""),
            audio_id=clip_data.get("audio_id", ""),
            audio_url=clip_data.get("audio_url", ""),
            duration_seconds=clip_data.get("duration_seconds", 0.0),
            start_time=clip_data.get("start_time", 0.0),
            engine=clip_data.get("engine"),
            quality_score=clip_data.get("quality_score"),
        ))
    return AudioTrack(
        id=track_data.get("id", ""),
        name=track_data.get("name", ""),
        project_id=track_data.get("project_id", ""),
        clips=clips,
        track_number=track_data.get("track_number", 0),
        engine=track_data.get("engine"),
    )


@router.get("", response_model=List[AudioTrack])
@cache_response(ttl=30)  # Cache for 30 seconds (tracks may change frequently)
def list_tracks(
    project_id: str,
    track_store: TrackStoreDep,
) -> List[AudioTrack]:
    """List all tracks for a project."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Get tracks from persistent store
        track_data_list = track_store.list_tracks(project_id)
        project_tracks = [_track_dict_to_model(t) for t in track_data_list]

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
def get_track(
    project_id: str,
    track_id: str,
    track_store: TrackStoreDep,
) -> AudioTrack:
    """Get a specific track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")

        track_data = track_store.get_track(project_id, track_id)
        if track_data is None:
            logger.warning(f"Track not found: {track_id} in project: {project_id}")
            raise HTTPException(status_code=404, detail="Track not found")

        logger.info(f"Retrieved track: {track_id} from project: {project_id}")
        return _track_dict_to_model(track_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting track {track_id} from project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to get track: {str(e)}")


@router.post("", response_model=AudioTrack)
def create_track(
    project_id: str,
    req: TrackCreateRequest,
    track_store: TrackStoreDep,
) -> AudioTrack:
    """Create a new track in a project."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not req.name or not req.name.strip():
            raise HTTPException(status_code=400, detail="Track name is required")

        # Get existing tracks to determine track number
        existing_tracks = track_store.list_tracks(project_id)
        track_number = (
            max(
                [t.get("track_number", 0) for t in existing_tracks],
                default=0,
            )
            + 1
        )

        track_id = str(uuid.uuid4())

        track_data = {
            "id": track_id,
            "name": req.name.strip(),
            "project_id": project_id,
            "clips": [],
            "track_number": track_number,
            "engine": req.engine,
        }

        # Save to persistent store
        track_store.save_track(project_id, track_data)

        logger.info(f"Created track: {track_id} ({req.name}) in project: {project_id}")
        return _track_dict_to_model(track_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error creating track in project {project_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to create track: {str(e)}")


@router.put("/{track_id}", response_model=AudioTrack)
def update_track(
    project_id: str,
    track_id: str,
    req: TrackUpdateRequest,
    track_store: TrackStoreDep,
) -> AudioTrack:
    """Update an existing track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")
        if req.name is not None and (not req.name or not req.name.strip()):
            raise HTTPException(status_code=400, detail="Track name cannot be empty")

        track_data = track_store.get_track(project_id, track_id)
        if track_data is None:
            logger.warning(
                f"Track not found for update: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        # Apply updates
        updates = {}
        if req.name is not None:
            updates["name"] = req.name.strip()
        if req.engine is not None:
            updates["engine"] = req.engine

        updated_track = track_store.update_track(project_id, track_id, updates)

        logger.info(f"Updated track: {track_id} in project: {project_id}")
        return _track_dict_to_model(updated_track)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating track {track_id} in project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to update track: {str(e)}")


@router.delete("/{track_id}", response_model=ApiOk)
def delete_track(
    project_id: str,
    track_id: str,
    track_store: TrackStoreDep,
    ref_counter: ArtifactRefCounterDep,
) -> ApiOk:
    """Delete a track and all its clips."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")

        track_data = track_store.get_track(project_id, track_id)
        if track_data is None:
            logger.warning(
                f"Track not found for deletion: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        clip_count = len(track_data.get("clips", []))

        # Decrement reference counts for all audio artifacts in clips
        for clip in track_data.get("clips", []):
            audio_id = clip.get("audio_id")
            clip_id = clip.get("id")
            if audio_id and clip_id:
                ref_counter.decrement(audio_id, clip_id)

        # Delete the track from persistent store
        track_store.delete_track(project_id, track_id)

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
def create_clip(
    project_id: str,
    track_id: str,
    req: ClipCreateRequest,
    track_store: TrackStoreDep,
    ref_counter: ArtifactRefCounterDep,
) -> AudioClip:
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

        track_data = track_store.get_track(project_id, track_id)
        if track_data is None:
            logger.warning(
                f"Track not found for clip creation: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        clip_id = str(uuid.uuid4())
        clip_data = {
            "id": clip_id,
            "name": req.name.strip(),
            "profile_id": req.profile_id,
            "audio_id": req.audio_id,
            "audio_url": req.audio_url,
            "duration_seconds": req.duration_seconds,
            "start_time": req.start_time,
            "engine": req.engine,
            "quality_score": req.quality_score,
        }

        # Add clip to track's clips list
        clips = track_data.get("clips", [])
        clips.append(clip_data)
        track_store.update_track(project_id, track_id, {"clips": clips})

        # Increment reference count for the audio artifact
        ref_counter.increment(req.audio_id, clip_id)

        clip = AudioClip(**clip_data)

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
    project_id: str,
    track_id: str,
    clip_id: str,
    req: ClipUpdateRequest,
    track_store: TrackStoreDep,
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

        track_data = track_store.get_track(project_id, track_id)
        if track_data is None:
            logger.warning(
                f"Track not found for clip update: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        clips = track_data.get("clips", [])
        clip_data = next((c for c in clips if c.get("id") == clip_id), None)

        if not clip_data:
            logger.warning(f"Clip not found for update: {clip_id} in track: {track_id}")
            raise HTTPException(status_code=404, detail="Clip not found")

        # Apply updates to clip
        if req.name is not None:
            clip_data["name"] = req.name.strip()
        if req.start_time is not None:
            clip_data["start_time"] = req.start_time

        # Save updated clips list
        track_store.update_track(project_id, track_id, {"clips": clips})

        logger.info(
            f"Updated clip: {clip_id} in track: {track_id} of project: {project_id}"
        )
        return AudioClip(**clip_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating clip {clip_id} in track {track_id} of project {project_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to update clip: {str(e)}")


@router.delete("/{track_id}/clips/{clip_id}", response_model=ApiOk)
def delete_clip(
    project_id: str,
    track_id: str,
    clip_id: str,
    track_store: TrackStoreDep,
    ref_counter: ArtifactRefCounterDep,
) -> ApiOk:
    """Delete a clip from a track."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")
        if not track_id or not track_id.strip():
            raise HTTPException(status_code=400, detail="Track ID is required")
        if not clip_id or not clip_id.strip():
            raise HTTPException(status_code=400, detail="Clip ID is required")

        track_data = track_store.get_track(project_id, track_id)
        if track_data is None:
            logger.warning(
                f"Track not found for clip deletion: {track_id} in project: {project_id}"
            )
            raise HTTPException(status_code=404, detail="Track not found")

        clips = track_data.get("clips", [])
        clip_data = next((c for c in clips if c.get("id") == clip_id), None)

        if not clip_data:
            logger.warning(
                f"Clip not found for deletion: {clip_id} in track: {track_id}"
            )
            raise HTTPException(status_code=404, detail="Clip not found")

        # Decrement reference count for the audio artifact
        audio_id = clip_data.get("audio_id")
        if audio_id:
            ref_counter.decrement(audio_id, clip_id)

        # Remove clip from list and save
        clips = [c for c in clips if c.get("id") != clip_id]
        track_store.update_track(project_id, track_id, {"clips": clips})

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


# Undo/Redo endpoints
class UndoRedoResponse(BaseModel):
    """Response model for undo/redo operations."""
    success: bool
    description: Optional[str] = None
    can_undo: bool = False
    can_redo: bool = False


# Store EditHistory instances per project for undo/redo functionality
_project_histories: dict[str, "EditHistoryDep"] = {}


def _get_project_history(project_id: str) -> "EditHistoryDep":
    """Get or create EditHistory for a project."""
    from backend.services.edit_history import EditHistory
    if project_id not in _project_histories:
        _project_histories[project_id] = EditHistory()
    return _project_histories[project_id]


@router.post("/undo", response_model=UndoRedoResponse)
def undo_track_edit(
    project_id: str,
) -> UndoRedoResponse:
    """Undo the most recent track/clip edit."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")

        history = _get_project_history(project_id)
        description = history.undo()

        if description is None:
            return UndoRedoResponse(
                success=False,
                description="Nothing to undo",
                can_undo=history.can_undo(),
                can_redo=history.can_redo(),
            )

        logger.info(f"Undo in project {project_id}: {description}")
        return UndoRedoResponse(
            success=True,
            description=description,
            can_undo=history.can_undo(),
            can_redo=history.can_redo(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during undo in project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to undo: {str(e)}")


@router.post("/redo", response_model=UndoRedoResponse)
def redo_track_edit(
    project_id: str,
) -> UndoRedoResponse:
    """Redo the most recently undone track/clip edit."""
    try:
        if not project_id or not project_id.strip():
            raise HTTPException(status_code=400, detail="Project ID is required")

        history = _get_project_history(project_id)
        description = history.redo()

        if description is None:
            return UndoRedoResponse(
                success=False,
                description="Nothing to redo",
                can_undo=history.can_undo(),
                can_redo=history.can_redo(),
            )

        logger.info(f"Redo in project {project_id}: {description}")
        return UndoRedoResponse(
            success=True,
            description=description,
            can_undo=history.can_undo(),
            can_redo=history.can_redo(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during redo in project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to redo: {str(e)}")
