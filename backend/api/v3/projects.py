"""
API v3 - Project Management Endpoints.

Task 3.4.1: Project CRUD with cursor-based pagination.
Phase 4A: Updated to use StandardResponse envelope format.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from .models import StandardResponse, paginated_response, success_response

router = APIRouter(prefix="/projects", tags=["projects"])
logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str | None:
    """Extract request ID from request state if available."""
    return getattr(request.state, "request_id", None)


# --- Request/Response Models ---

class TrackInfo(BaseModel):
    """Track information."""
    id: str
    name: str
    type: str = "audio"
    muted: bool = False
    solo: bool = False
    volume: float = 1.0
    clip_count: int = 0


class ProjectInfo(BaseModel):
    """Project information."""
    id: str
    name: str
    description: str | None = None
    created_at: str
    updated_at: str
    duration_seconds: float = 0.0
    track_count: int = 0
    sample_rate: int = 44100

    class Config:
        json_schema_extra = {
            "example": {
                "id": "proj_abc123",
                "name": "My Voice Project",
                "description": "A sample project",
                "created_at": "2026-02-09T12:00:00Z",
                "updated_at": "2026-02-09T15:30:00Z",
                "duration_seconds": 120.5,
                "track_count": 3,
                "sample_rate": 44100,
            }
        }


class ProjectDetail(ProjectInfo):
    """Detailed project information with tracks."""
    tracks: list[TrackInfo] = []


class ProjectListResponse(BaseModel):
    """Paginated project list (cursor-based)."""
    projects: list[ProjectInfo]
    cursor: str | None = None
    has_more: bool = False
    total_count: int | None = None


class CreateProjectRequest(BaseModel):
    """Request to create a project."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)


class UpdateProjectRequest(BaseModel):
    """Request to update a project."""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


# --- Endpoints ---

@router.get(
    "",
    response_model=StandardResponse[list[ProjectInfo]],
    summary="List projects",
    description="Get user's projects with cursor-based pagination.",
)
async def list_projects(
    request: Request,
    cursor: str | None = Query(None, description="Pagination cursor"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    sort_by: str = Query("updated_at", description="Sort field"),
    sort_desc: bool = Query(True, description="Sort descending"),
):
    """List all projects with StandardResponse envelope."""
    # Mock implementation
    projects = [
        ProjectInfo(
            id="proj_1",
            name="Sample Project",
            description="A demo project",
            created_at="2026-02-01T10:00:00Z",
            updated_at="2026-02-09T15:30:00Z",
            duration_seconds=60.0,
            track_count=2,
        ),
    ]

    return paginated_response(
        data=projects[:limit],
        has_more=len(projects) > limit,
        total_count=len(projects),
        page_size=limit,
        request_id=_get_request_id(request),
    )


@router.get(
    "/{project_id}",
    response_model=StandardResponse[ProjectDetail],
    summary="Get project details",
    description="Get detailed project information including tracks.",
)
async def get_project(request: Request, project_id: str):
    """Get project by ID with StandardResponse envelope."""
    # Mock implementation
    if project_id == "proj_1":
        project = ProjectDetail(
            id="proj_1",
            name="Sample Project",
            description="A demo project",
            created_at="2026-02-01T10:00:00Z",
            updated_at="2026-02-09T15:30:00Z",
            duration_seconds=60.0,
            track_count=2,
            tracks=[
                TrackInfo(id="track_1", name="Voice", type="audio"),
                TrackInfo(id="track_2", name="Background", type="audio"),
            ],
        )
        return success_response(
            data=project,
            message="Project retrieved",
            request_id=_get_request_id(request),
        )

    raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")


@router.post(
    "",
    response_model=StandardResponse[ProjectInfo],
    summary="Create project",
    description="Create a new project.",
)
async def create_project(request: Request, create_request: CreateProjectRequest):
    """Create a new project with StandardResponse envelope."""
    import uuid

    now = datetime.now().isoformat()

    project = ProjectInfo(
        id=f"proj_{uuid.uuid4().hex[:12]}",
        name=create_request.name,
        description=create_request.description,
        created_at=now,
        updated_at=now,
        sample_rate=create_request.sample_rate,
    )

    return success_response(
        data=project,
        message="Project created successfully",
        request_id=_get_request_id(request),
    )


@router.patch(
    "/{project_id}",
    response_model=StandardResponse[ProjectInfo],
    summary="Update project",
    description="Update project metadata.",
)
async def update_project(request: Request, project_id: str, update_request: UpdateProjectRequest):
    """Update a project with StandardResponse envelope."""
    # Mock implementation
    now = datetime.now().isoformat()

    project = ProjectInfo(
        id=project_id,
        name=update_request.name or "Updated Project",
        description=update_request.description,
        created_at="2026-02-01T10:00:00Z",
        updated_at=now,
    )

    return success_response(
        data=project,
        message="Project updated",
        request_id=_get_request_id(request),
    )


class DeleteProjectResult(BaseModel):
    """Result of project deletion."""
    project_id: str
    deleted: bool = True


@router.delete(
    "/{project_id}",
    response_model=StandardResponse[DeleteProjectResult],
    summary="Delete project",
    description="Delete a project and all its contents.",
)
async def delete_project(request: Request, project_id: str):
    """Delete a project with StandardResponse envelope."""
    result = DeleteProjectResult(project_id=project_id, deleted=True)
    return success_response(
        data=result,
        message="Project deleted",
        request_id=_get_request_id(request),
    )


@router.post(
    "/{project_id}/duplicate",
    response_model=StandardResponse[ProjectInfo],
    summary="Duplicate project",
    description="Create a copy of an existing project.",
)
async def duplicate_project(
    request: Request,
    project_id: str,
    new_name: str | None = Query(None, description="Name for the copy"),
):
    """Duplicate a project with StandardResponse envelope."""
    import uuid

    now = datetime.now().isoformat()

    project = ProjectInfo(
        id=f"proj_{uuid.uuid4().hex[:12]}",
        name=new_name or f"Copy of {project_id}",
        created_at=now,
        updated_at=now,
    )

    return success_response(
        data=project,
        message="Project duplicated successfully",
        request_id=_get_request_id(request),
    )


class ExportProjectResult(BaseModel):
    """Result of project export request."""
    project_id: str
    format: str
    status: str = "queued"
    download_url: str | None = None


@router.get(
    "/{project_id}/export",
    response_model=StandardResponse[ExportProjectResult],
    summary="Export project",
    description="Export project to a downloadable format.",
)
async def export_project(
    request: Request,
    project_id: str,
    format: str = Query("wav", description="Export format"),
):
    """Export project audio with StandardResponse envelope."""
    # Would trigger actual export
    result = ExportProjectResult(
        project_id=project_id,
        format=format,
        status="queued",
        download_url=f"/api/v3/projects/{project_id}/download",
    )

    return success_response(
        data=result,
        message="Export queued",
        request_id=_get_request_id(request),
    )
