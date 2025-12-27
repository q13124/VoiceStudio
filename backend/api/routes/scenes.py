"""
Scene Composition Routes

Endpoints for managing scenes - compositions of tracks, effects, and automation.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scenes", tags=["scenes"])

# In-memory scenes storage (replace with database in production)
_scenes: Dict[str, Dict] = {}


class SceneTrack(BaseModel):
    """A track in a scene."""

    id: str
    name: str
    track_number: int
    clips: List[Dict] = []  # Audio clips on this track
    effects: List[Dict] = []  # Effects applied to this track
    automation: List[Dict] = []  # Automation curves for this track


class Scene(BaseModel):
    """A scene composition."""

    id: str
    name: str
    description: Optional[str] = None
    project_id: str
    tracks: List[SceneTrack] = []
    master_effects: List[Dict] = []  # Master effects
    duration: float = 0.0  # Scene duration in seconds
    created: str  # ISO datetime string
    modified: str  # ISO datetime string
    tags: List[str] = []


class SceneCreateRequest(BaseModel):
    """Request to create a scene."""

    name: str
    description: Optional[str] = None
    project_id: str
    tags: List[str] = []


class SceneUpdateRequest(BaseModel):
    """Request to update a scene."""

    name: Optional[str] = None
    description: Optional[str] = None
    tracks: Optional[List[SceneTrack]] = None
    master_effects: Optional[List[Dict]] = None
    duration: Optional[float] = None
    tags: Optional[List[str]] = None


@router.get("", response_model=List[Scene])
@cache_response(ttl=30)  # Cache for 30 seconds (scenes may change)
async def get_scenes(
    project_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """Get all scenes, optionally filtered."""
    scenes = list(_scenes.values())

    if project_id:
        scenes = [s for s in scenes if s.get("project_id") == project_id]

    if search:
        search_lower = search.lower()
        scenes = [
            s
            for s in scenes
            if search_lower in s.get("name", "").lower()
            or search_lower in s.get("description", "").lower()
        ]

    # Sort by name
    scenes.sort(key=lambda s: s.get("name", ""))

    return [
        Scene(
            id=str(s.get("id", "")),
            name=str(s.get("name", "")),
            description=s.get("description"),
            project_id=str(s.get("project_id", "")),
            tracks=[
                SceneTrack(
                    id=str(t.get("id", "")),
                    name=str(t.get("name", "")),
                    track_number=t.get("track_number", 0),
                    clips=t.get("clips", []),
                    effects=t.get("effects", []),
                    automation=t.get("automation", []),
                )
                for t in s.get("tracks", [])
            ],
            master_effects=s.get("master_effects", []),
            duration=s.get("duration", 0.0),
            created=str(s.get("created", "")),
            modified=str(s.get("modified", "")),
            tags=s.get("tags", []),
        )
        for s in scenes
    ]


@router.get("/{scene_id}", response_model=Scene)
@cache_response(ttl=60)  # Cache for 60 seconds (scene info is relatively static)
async def get_scene(scene_id: str):
    """Get a specific scene."""
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene = _scenes[scene_id]
    return Scene(
        id=str(scene.get("id", "")),
        name=str(scene.get("name", "")),
        description=scene.get("description"),
        project_id=str(scene.get("project_id", "")),
        tracks=[
            SceneTrack(
                id=str(t.get("id", "")),
                name=str(t.get("name", "")),
                track_number=t.get("track_number", 0),
                clips=t.get("clips", []),
                effects=t.get("effects", []),
                automation=t.get("automation", []),
            )
            for t in scene.get("tracks", [])
        ],
        master_effects=scene.get("master_effects", []),
        duration=scene.get("duration", 0.0),
        created=str(scene.get("created", "")),
        modified=str(scene.get("modified", "")),
        tags=scene.get("tags", []),
    )


@router.post("", response_model=Scene)
async def create_scene(request: SceneCreateRequest):
    """Create a new scene."""
    import uuid

    scene_id = f"scene-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    scene = {
        "id": scene_id,
        "name": request.name,
        "description": request.description,
        "project_id": request.project_id,
        "tracks": [],
        "master_effects": [],
        "duration": 0.0,
        "created": now,
        "modified": now,
        "tags": request.tags,
    }

    _scenes[scene_id] = scene
    return Scene(
        id=scene_id,
        name=request.name,
        description=request.description,
        project_id=request.project_id,
        tracks=[],
        master_effects=[],
        duration=0.0,
        created=now,
        modified=now,
        tags=request.tags,
    )


@router.put("/{scene_id}", response_model=Scene)
async def update_scene(scene_id: str, request: SceneUpdateRequest):
    """Update a scene."""
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene = _scenes[scene_id].copy()

    if request.name is not None:
        scene["name"] = request.name
    if request.description is not None:
        scene["description"] = request.description
    if request.tracks is not None:
        scene["tracks"] = [
            {
                "id": t.id,
                "name": t.name,
                "track_number": t.track_number,
                "clips": t.clips,
                "effects": t.effects,
                "automation": t.automation,
            }
            for t in request.tracks
        ]
    if request.master_effects is not None:
        scene["master_effects"] = request.master_effects
    if request.duration is not None:
        scene["duration"] = request.duration
    if request.tags is not None:
        scene["tags"] = request.tags

    scene["modified"] = datetime.utcnow().isoformat()
    _scenes[scene_id] = scene

    return Scene(
        id=str(scene.get("id", "")),
        name=str(scene.get("name", "")),
        description=scene.get("description"),
        project_id=str(scene.get("project_id", "")),
        tracks=[
            SceneTrack(
                id=str(t.get("id", "")),
                name=str(t.get("name", "")),
                track_number=t.get("track_number", 0),
                clips=t.get("clips", []),
                effects=t.get("effects", []),
                automation=t.get("automation", []),
            )
            for t in scene.get("tracks", [])
        ],
        master_effects=scene.get("master_effects", []),
        duration=scene.get("duration", 0.0),
        created=str(scene.get("created", "")),
        modified=str(scene.get("modified", "")),
        tags=scene.get("tags", []),
    )


@router.delete("/{scene_id}")
async def delete_scene(scene_id: str):
    """Delete a scene."""
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail="Scene not found")

    del _scenes[scene_id]
    return {"success": True}


@router.post("/{scene_id}/tracks", response_model=Scene)
async def add_track_to_scene(scene_id: str, track: SceneTrack):
    """Add a track to a scene."""
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene = _scenes[scene_id].copy()

    track_dict = {
        "id": track.id,
        "name": track.name,
        "track_number": track.track_number,
        "clips": track.clips,
        "effects": track.effects,
        "automation": track.automation,
    }

    scene["tracks"].append(track_dict)
    # Sort tracks by track_number
    scene["tracks"].sort(key=lambda t: t.get("track_number", 0))

    scene["modified"] = datetime.utcnow().isoformat()
    _scenes[scene_id] = scene

    return Scene(
        id=str(scene.get("id", "")),
        name=str(scene.get("name", "")),
        description=scene.get("description"),
        project_id=str(scene.get("project_id", "")),
        tracks=[
            SceneTrack(
                id=str(t.get("id", "")),
                name=str(t.get("name", "")),
                track_number=t.get("track_number", 0),
                clips=t.get("clips", []),
                effects=t.get("effects", []),
                automation=t.get("automation", []),
            )
            for t in scene.get("tracks", [])
        ],
        master_effects=scene.get("master_effects", []),
        duration=scene.get("duration", 0.0),
        created=str(scene.get("created", "")),
        modified=str(scene.get("modified", "")),
        tags=scene.get("tags", []),
    )


@router.delete("/{scene_id}/tracks/{track_id}")
async def remove_track_from_scene(scene_id: str, track_id: str):
    """Remove a track from a scene."""
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene = _scenes[scene_id].copy()

    scene["tracks"] = [t for t in scene.get("tracks", []) if t.get("id") != track_id]

    scene["modified"] = datetime.utcnow().isoformat()
    _scenes[scene_id] = scene

    return {"success": True}


@router.post("/{scene_id}/apply")
async def apply_scene(scene_id: str, target_project_id: str):
    """Apply a scene to a project."""
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene = _scenes[scene_id]

    # In a real implementation, this would:
    # 1. Load the target project
    # 2. Apply all tracks, effects, and automation from the scene
    # 3. Save the updated project

    return {
        "success": True,
        "message": f"Scene '{scene.get('name')}' applied to project",
    }

