"""
Project Management Routes

CRUD operations for projects.
"""

import logging
import os
import shutil
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
from ..exceptions import ProjectNotFoundException
from ..error_handling import ErrorCodes
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..models import ApiOk
from ..optimization import cache_response, get_pagination_params, PaginationParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    voice_profile_ids: List[str] = []


class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    voice_profile_ids: Optional[List[str]] = None


# In-memory storage (replace with database in production)
_projects: dict[str, Project] = {}
_MAX_PROJECTS = 500  # Maximum number of projects
_project_timestamps: dict[str, float] = {}  # project_id -> creation_time


def _cleanup_old_projects():
    """
    Clean up old projects from storage to prevent memory accumulation.

    Removes projects beyond MAX_PROJECTS (oldest first based on creation time).
    """
    if len(_projects) > _MAX_PROJECTS:
        # Sort by creation time (oldest first)
        sorted_projects = sorted(
            _project_timestamps.items(),
            key=lambda x: x[1],
        )
        excess = len(_projects) - _MAX_PROJECTS
        for project_id, _ in sorted_projects[:excess]:
            if project_id in _projects:
                del _projects[project_id]
            if project_id in _project_timestamps:
                del _project_timestamps[project_id]
        logger.info(f"Cleaned up {excess} old projects from storage")


# Project audio storage directory
PROJECTS_DIR = os.path.join(os.path.expanduser("~"), ".voicestudio", "projects")


def _ensure_project_dir(project_id: str) -> str:
    """Ensure project directory exists and return its path."""
    project_dir = os.path.join(PROJECTS_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(os.path.join(project_dir, "audio"), exist_ok=True)
    return project_dir


@router.get("")
@cache_response(ttl=60)  # Cache for 60 seconds
def list_projects(request: Request) -> dict:
    """
    List all projects with pagination.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 1000)
    """
    try:
        # Get pagination parameters
        pagination = get_pagination_params(request, default_page_size=50)
        
        # Get all projects
        all_projects = list(_projects.values())
        
        # Paginate
        result = pagination.paginate(all_projects)
        
        return result
    except Exception as e:
        logger.error(f"Failed to list projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to list projects: {str(e)}"
        ) from e


@router.get("/{project_id}", response_model=Project)
@cache_response(ttl=300)  # Cache for 5 minutes
def get_project(project_id: str) -> Project:
    """Get a specific project."""
    try:
        if project_id not in _projects:
            raise HTTPException(status_code=404, detail="Project not found")
        return _projects[project_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get project: {str(e)}"
        ) from e


@router.post("", response_model=Project)
def create_project(req: ProjectCreateRequest) -> Project:
    """Create a new project."""
    try:
        # Validate input
        if not req.name or not req.name.strip():
            raise HTTPException(
                status_code=400, detail="Project name is required and cannot be empty"
            )

        import uuid
        from datetime import datetime

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        project = Project(
            id=project_id,
            name=req.name.strip(),
            description=req.description.strip() if req.description else None,
            created_at=now,
            updated_at=now,
            voice_profile_ids=[],
        )

        _projects[project_id] = project
        _project_timestamps[project_id] = time.time()

        # Clean up old projects if needed
        if len(_projects) > _MAX_PROJECTS:
            _cleanup_old_projects()

        # Create project directory structure
        try:
            _ensure_project_dir(project_id)
        except Exception as dir_error:
            logger.warning(
                f"Failed to create project directory for {project_id}: {dir_error}"
            )
            # Continue - directory creation failure shouldn't prevent project creation

        logger.info(f"Created project: {project_id} - {project.name}")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to create project: {str(e)}"
        ) from e


@router.put("/{project_id}", response_model=Project)
def update_project(project_id: str, req: ProjectUpdateRequest) -> Project:
    """Update an existing project."""
    try:
        if project_id not in _projects:
            raise HTTPException(status_code=404, detail="Project not found")

        # Validate input
        if req.name is not None and (not req.name or not req.name.strip()):
            raise HTTPException(status_code=400, detail="Project name cannot be empty")

        from datetime import datetime

        project = _projects[project_id]

        if req.name is not None:
            project.name = req.name.strip()
        if req.description is not None:
            project.description = req.description.strip() if req.description else None
        if req.voice_profile_ids is not None:
            project.voice_profile_ids = req.voice_profile_ids

        project.updated_at = datetime.utcnow().isoformat()
        _projects[project_id] = project
        logger.info(f"Updated project: {project_id} - {project.name}")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to update project: {str(e)}"
        ) from e


@router.delete("/{project_id}", response_model=ApiOk)
def delete_project(project_id: str) -> ApiOk:
    """Delete a project."""
    try:
        if project_id not in _projects:
            raise HTTPException(status_code=404, detail="Project not found")

        # Attempt to delete project directory (non-critical if it fails)
        try:
            project_dir = os.path.join(PROJECTS_DIR, project_id)
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
                logger.debug(f"Deleted project directory: {project_dir}")
        except Exception as dir_error:
            logger.warning(
                f"Failed to delete project directory for {project_id}: {dir_error}"
            )
            # Continue - directory deletion failure shouldn't prevent project deletion

        del _projects[project_id]
        if project_id in _project_timestamps:
            del _project_timestamps[project_id]
        logger.info(f"Deleted project: {project_id}")
        return ApiOk()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {str(e)}"
        ) from e


class ProjectAudioFileResponse(BaseModel):
    filename: str
    url: str
    size: int
    modified: str


class SaveAudioRequest(BaseModel):
    audio_id: str
    filename: Optional[str] = None


@router.post("/{project_id}/audio/save", response_model=ProjectAudioFileResponse)
def save_audio_to_project(
    project_id: str, req: SaveAudioRequest
) -> ProjectAudioFileResponse:
    """
    Save an audio file to a project directory.

    Args:
        project_id: Project ID
        req: Request body with audio_id and optional filename

    Returns:
        ProjectAudioFileResponse with file information
    """
    if project_id not in _projects:
        raise HTTPException(
            status_code=404,
            detail=f"Project '{project_id}' not found. Please check the project ID and try again.",
        )

    audio_id = req.audio_id
    filename = req.filename

    # Import audio storage from voice routes
    from .voice import _audio_storage

    if audio_id not in _audio_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Audio file with ID '{audio_id}' not found. The audio may have expired or been removed.",
        )

    source_path = _audio_storage[audio_id]
    if not os.path.exists(source_path):
        raise HTTPException(
            status_code=404,
            detail=f"Audio file at path '{source_path}' no longer exists on disk. The file may have been deleted.",
        )

    try:
        # Ensure project directory exists
        project_dir = _ensure_project_dir(project_id)
        audio_dir = os.path.join(project_dir, "audio")

        # Generate filename if not provided
        if not filename:
            filename = f"{audio_id}.wav"
        elif not filename.endswith(".wav"):
            filename = f"{filename}.wav"

        # Validate filename doesn't contain invalid characters
        invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
        if any(char in filename for char in invalid_chars):
            raise HTTPException(
                status_code=400,
                detail=f"Filename '{filename}' contains invalid characters. Please use a valid filename.",
            )

        # Save audio file to project directory
        dest_path = os.path.join(audio_dir, filename)
        try:
            shutil.copy2(source_path, dest_path)
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied when saving audio to '{dest_path}'. Please check directory permissions.",
            )
        except OSError as e:
            if "No space left" in str(e) or "disk full" in str(e).lower():
                raise HTTPException(
                    status_code=507,
                    detail="Disk full. Please free up space and try again.",
                )
            raise HTTPException(
                status_code=500, detail=f"Failed to save audio file: {str(e)}"
            )

        # Get file stats
        try:
            file_stat = os.stat(dest_path)
        except OSError as e:
            logger.error(f"Failed to get file stats for {dest_path}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve file information after save.",
            )

        logger.info(f"Saved audio {audio_id} to project {project_id}: {dest_path}")

        return ProjectAudioFileResponse(
            filename=filename,
            url=f"/api/projects/{project_id}/audio/{filename}",
            size=file_stat.st_size,
            modified=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error saving audio to project {project_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while saving the audio file: {str(e)}",
        )


class ProjectAudioFile(BaseModel):
    filename: str
    url: str
    size: int
    modified: str


@router.get("/{project_id}/audio", response_model=List[ProjectAudioFile])
@cache_response(ttl=60)  # Cache for 60 seconds (audio file lists change moderately)
def list_project_audio(project_id: str) -> List[ProjectAudioFile]:
    """List all audio files in a project."""
    try:
        if project_id not in _projects:
            raise HTTPException(
                status_code=404,
                detail=f"Project '{project_id}' not found. Please check the project ID and try again.",
            )

        project_dir = _ensure_project_dir(project_id)
        project_dir = _ensure_project_dir(project_id)
        audio_dir = os.path.join(project_dir, "audio")

        if not os.path.exists(audio_dir):
            return []

        audio_files = []
        try:
            for filename in os.listdir(audio_dir):
                if filename.endswith((".wav", ".mp3", ".flac")):
                    file_path = os.path.join(audio_dir, filename)
                    try:
                        file_stat = os.stat(file_path)
                        audio_files.append(
                            ProjectAudioFile(
                                filename=filename,
                                url=f"/api/projects/{project_id}/audio/{filename}",
                                size=file_stat.st_size,
                                modified=datetime.fromtimestamp(
                                    file_stat.st_mtime
                                ).isoformat(),
                            )
                        )
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Failed to get stats for file {file_path}: {e}")
                        # Continue with other files instead of failing completely
                        continue
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied when accessing audio directory '{audio_dir}'. Please check directory permissions.",
            )
        except OSError as e:
            logger.error(f"Failed to list audio files in {audio_dir}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to list audio files: {str(e)}"
            )

        return audio_files
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error listing audio files for project {project_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while listing audio files: {str(e)}",
        )


@router.get("/{project_id}/audio/{filename}")
def get_project_audio(project_id: str, filename: str):
    """Get an audio file from a project."""
    try:
        if project_id not in _projects:
            raise HTTPException(
                status_code=404,
                detail=f"Project '{project_id}' not found. Please check the project ID and try again.",
            )

        # Validate filename to prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename. Directory traversal is not allowed.",
            )
        project_dir = _ensure_project_dir(project_id)
        audio_dir = os.path.join(project_dir, "audio")
        file_path = os.path.join(audio_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Audio file '{filename}' not found in project '{project_id}'. The file may have been deleted.",
            )

        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=400, detail=f"Path '{filename}' is not a file."
            )

        try:
            return FileResponse(file_path, media_type="audio/wav")
        except Exception as e:
            logger.error(f"Failed to serve file {file_path}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to serve audio file: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error getting audio file {filename} from project {project_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while retrieving the audio file: {str(e)}",
        )
