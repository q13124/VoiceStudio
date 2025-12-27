"""
Asset Library Routes

Endpoints for managing and browsing the asset library.
Supports audio files, voice profiles, presets, templates, and other assets.
"""

import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

try:
    from ..optimization import cache_response
except ImportError:

    def cache_response(ttl: int = 300):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/library", tags=["library"])

# In-memory storage (replace with database in production)
_assets: Dict[str, Dict] = {}
_asset_folders: Dict[str, Dict] = {}
_MAX_ASSETS = 5000  # Maximum number of assets
_MAX_FOLDERS = 500  # Maximum number of folders
_asset_timestamps: Dict[str, float] = {}  # asset_id -> creation_time
_folder_timestamps: Dict[str, float] = {}  # folder_id -> creation_time


def _cleanup_old_assets():
    """
    Clean up old assets and folders from storage.

    Removes items beyond MAX_ASSETS/MAX_FOLDERS (oldest first).
    """
    # Clean up assets
    if len(_assets) > _MAX_ASSETS:
        sorted_assets = sorted(
            _asset_timestamps.items(),
            key=lambda x: x[1],
        )
        excess = len(_assets) - _MAX_ASSETS
        for asset_id, _ in sorted_assets[:excess]:
            if asset_id in _assets:
                del _assets[asset_id]
            if asset_id in _asset_timestamps:
                del _asset_timestamps[asset_id]
        logger.info(f"Cleaned up {excess} old assets from storage")

    # Clean up folders
    if len(_asset_folders) > _MAX_FOLDERS:
        sorted_folders = sorted(
            _folder_timestamps.items(),
            key=lambda x: x[1],
        )
        excess = len(_asset_folders) - _MAX_FOLDERS
        for folder_id, _ in sorted_folders[:excess]:
            if folder_id in _asset_folders:
                del _asset_folders[folder_id]
            if folder_id in _folder_timestamps:
                del _folder_timestamps[folder_id]
        logger.info(f"Cleaned up {excess} old folders from storage")


class AssetType:
    """Asset type constants."""

    AUDIO = "audio"
    VOICE_PROFILE = "voice_profile"
    PRESET = "preset"
    TEMPLATE = "template"
    EFFECT = "effect"
    MACRO = "macro"
    IMAGE = "image"
    VIDEO = "video"
    OTHER = "other"


class LibraryAsset(BaseModel):
    """An asset in the library."""

    id: str
    name: str
    type: str  # AssetType
    path: str
    folder_id: Optional[str] = None
    tags: List[str] = []
    metadata: Dict = {}
    created: datetime
    modified: datetime
    size: int = 0
    duration: Optional[float] = None  # For audio/video
    thumbnail_url: Optional[str] = None


class LibraryFolder(BaseModel):
    """A folder in the library."""

    id: str
    name: str
    parent_id: Optional[str] = None
    path: str
    created: datetime
    modified: datetime
    asset_count: int = 0


class AssetSearchRequest(BaseModel):
    """Request to search assets."""

    query: Optional[str] = None
    asset_type: Optional[str] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


class AssetSearchResponse(BaseModel):
    """Response from asset search."""

    assets: List[LibraryAsset]
    total: int
    limit: int
    offset: int


@router.get("/folders", response_model=List[LibraryFolder])
@cache_response(ttl=60)  # Cache for 60 seconds (folders change moderately)
async def get_folders(
    parent_id: Optional[str] = Query(None, description="Parent folder ID")
):
    """Get all folders, optionally filtered by parent."""
    folders = []
    for folder_data in _asset_folders.values():
        if folder_data.get("parent_id") == parent_id:
            folders.append(LibraryFolder(**folder_data))
    return sorted(folders, key=lambda x: x.name)


@router.post("/folders", response_model=LibraryFolder)
async def create_folder(
    name: str, parent_id: Optional[str] = None, path: Optional[str] = None
):
    """Create a new folder."""
    folder_id = str(uuid.uuid4())

    if not path:
        if parent_id and parent_id in _asset_folders:
            parent_path = _asset_folders[parent_id]["path"]
            path = os.path.join(parent_path, name)
        else:
            path = os.path.join("data", "library", name)

    # Ensure directory exists
    os.makedirs(path, exist_ok=True)

    folder_data = {
        "id": folder_id,
        "name": name,
        "parent_id": parent_id,
        "path": path,
        "created": datetime.now(),
        "modified": datetime.now(),
        "asset_count": 0,
    }

    _asset_folders[folder_id] = folder_data
    _folder_timestamps[folder_id] = time.time()

    # Clean up old folders if needed
    if len(_asset_folders) > _MAX_FOLDERS:
        _cleanup_old_assets()

    logger.info(f"Created folder {folder_id}: {name}")

    return LibraryFolder(**folder_data)


@router.get("/assets", response_model=AssetSearchResponse)
@cache_response(ttl=30)  # Cache for 30 seconds (asset searches change moderately)
async def search_assets(
    query: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),  # Comma-separated
    folder_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Search and filter assets."""
    filtered_assets = list(_assets.values())

    # Filter by folder
    if folder_id:
        filtered_assets = [
            a for a in filtered_assets if a.get("folder_id") == folder_id
        ]

    # Filter by type
    if asset_type:
        filtered_assets = [a for a in filtered_assets if a.get("type") == asset_type]

    # Filter by tags
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        filtered_assets = [
            a
            for a in filtered_assets
            if any(tag in a.get("tags", []) for tag in tag_list)
        ]

    # Filter by query (name search)
    if query:
        query_lower = query.lower()
        filtered_assets = [
            a for a in filtered_assets if query_lower in a.get("name", "").lower()
        ]

    # Sort by modified date (newest first)
    filtered_assets.sort(key=lambda x: x.get("modified", datetime.min), reverse=True)

    total = len(filtered_assets)
    paginated = filtered_assets[offset : offset + limit]

    return AssetSearchResponse(
        assets=[LibraryAsset(**asset) for asset in paginated],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/assets/{asset_id}", response_model=LibraryAsset)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (individual assets change less frequently)
async def get_asset(asset_id: str):
    """Get a specific asset."""
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail="Asset not found")

    return LibraryAsset(**_assets[asset_id])


@router.post("/assets", response_model=LibraryAsset)
async def create_asset(
    name: str,
    asset_type: str,
    path: str,
    folder_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
):
    """Create or register a new asset."""
    asset_id = str(uuid.uuid4())

    # Get file size if path exists
    size = 0
    if os.path.exists(path):
        size = os.path.getsize(path)

    asset_data = {
        "id": asset_id,
        "name": name,
        "type": asset_type,
        "path": path,
        "folder_id": folder_id,
        "tags": tags or [],
        "metadata": metadata or {},
        "created": datetime.now(),
        "modified": datetime.now(),
        "size": size,
        "duration": None,
        "thumbnail_url": None,
    }

    _assets[asset_id] = asset_data
    _asset_timestamps[asset_id] = time.time()

    # Clean up old assets if needed
    if len(_assets) > _MAX_ASSETS:
        _cleanup_old_assets()

    # Update folder asset count
    if folder_id and folder_id in _asset_folders:
        _asset_folders[folder_id]["asset_count"] += 1

    logger.info(f"Created asset {asset_id}: {name}")

    return LibraryAsset(**asset_data)


@router.put("/assets/{asset_id}", response_model=LibraryAsset)
async def update_asset(
    asset_id: str,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    folder_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
):
    """Update an asset."""
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset = _assets[asset_id]
    old_folder_id = asset.get("folder_id")

    # Update fields
    if name is not None:
        asset["name"] = name
    if tags is not None:
        asset["tags"] = tags
    if folder_id is not None:
        asset["folder_id"] = folder_id
    if metadata is not None:
        asset["metadata"].update(metadata)

    asset["modified"] = datetime.now()

    # Update folder counts
    if old_folder_id != folder_id:
        if old_folder_id and old_folder_id in _asset_folders:
            _asset_folders[old_folder_id]["asset_count"] = max(
                0, _asset_folders[old_folder_id]["asset_count"] - 1
            )
        if folder_id and folder_id in _asset_folders:
            _asset_folders[folder_id]["asset_count"] += 1

    logger.info(f"Updated asset {asset_id}")

    return LibraryAsset(**asset)


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset."""
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset = _assets[asset_id]
    folder_id = asset.get("folder_id")

    # Update folder count
    if folder_id and folder_id in _asset_folders:
        _asset_folders[folder_id]["asset_count"] = max(
            0, _asset_folders[folder_id]["asset_count"] - 1
        )

    del _assets[asset_id]

    logger.info(f"Deleted asset {asset_id}")

    return {"success": True, "message": "Asset deleted"}


@router.get("/types")
async def get_asset_types():
    """Get list of available asset types."""
    return {
        "types": [
            {"id": AssetType.AUDIO, "name": "Audio"},
            {"id": AssetType.VOICE_PROFILE, "name": "Voice Profile"},
            {"id": AssetType.PRESET, "name": "Preset"},
            {"id": AssetType.TEMPLATE, "name": "Template"},
            {"id": AssetType.EFFECT, "name": "Effect"},
            {"id": AssetType.MACRO, "name": "Macro"},
            {"id": AssetType.IMAGE, "name": "Image"},
            {"id": AssetType.VIDEO, "name": "Video"},
            {"id": AssetType.OTHER, "name": "Other"},
        ]
    }
