"""
Multi-Speaker Dubbing Routes

Phase 10.2: Expose MultiSpeakerDubbingService via REST API.
Provides endpoints for speaker diarization, voice assignment,
and background audio preservation.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/multi-speaker-dubbing", tags=["multi-speaker-dubbing"])


# --- Request/Response Models ---


class DiarizationRequest(BaseModel):
    """Request for speaker diarization."""
    audio_id: str = Field(..., description="Audio file ID")
    max_speakers: int = Field(10, ge=2, le=50, description="Maximum number of speakers")
    min_segment_duration: float = Field(0.5, description="Minimum segment duration in seconds")


class SpeakerSegment(BaseModel):
    """A speaker segment from diarization."""
    speaker_id: str
    start_time: float
    end_time: float
    confidence: float


class DiarizationResponse(BaseModel):
    """Response for speaker diarization."""
    project_id: str
    audio_id: str
    speaker_count: int
    segments: list[SpeakerSegment]
    total_duration: float


class VoiceAssignment(BaseModel):
    """Voice assignment for a speaker."""
    speaker_id: str
    target_voice_id: str
    pitch_shift: float = Field(0.0, ge=-12.0, le=12.0)


class VoiceAssignmentRequest(BaseModel):
    """Request for voice assignments."""
    project_id: str
    assignments: list[VoiceAssignment]


class VoiceAssignmentResponse(BaseModel):
    """Response for voice assignments."""
    project_id: str
    assignments_applied: int


class DubbingRequest(BaseModel):
    """Request for multi-speaker dubbing."""
    project_id: str
    preserve_background: bool = Field(True, description="Preserve background audio")
    normalize_loudness: bool = Field(True, description="Normalize speaker loudness")
    crossfade_duration: float = Field(0.1, description="Crossfade between segments")


class DubbingResponse(BaseModel):
    """Response for dubbing generation."""
    output_audio_id: str
    segments_processed: int
    speakers_dubbed: int
    background_preserved: bool


class ProjectInfo(BaseModel):
    """Dubbing project information."""
    project_id: str
    audio_id: str
    status: str
    speaker_count: int
    voice_assignments: dict[str, str]
    created_at: str


# --- API Endpoints ---


@router.post("/diarize", response_model=DiarizationResponse)
async def diarize_speakers(request: DiarizationRequest):
    """
    Perform speaker diarization on audio.

    Phase 10.2.1: Automatic speaker diarization.

    Args:
        request: Diarization parameters

    Returns:
        Speaker segments with timing
    """
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()
        result = await service.diarize(
            audio_id=request.audio_id,
            max_speakers=request.max_speakers,
            min_segment_duration=request.min_segment_duration,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Speaker diarization failed")
            )

        segments = [
            SpeakerSegment(
                speaker_id=s["speaker_id"],
                start_time=s["start_time"],
                end_time=s["end_time"],
                confidence=s.get("confidence", 0.0),
            )
            for s in result.get("segments", [])
        ]

        return DiarizationResponse(
            project_id=result["project_id"],
            audio_id=request.audio_id,
            speaker_count=result.get("speaker_count", 0),
            segments=segments,
            total_duration=result.get("total_duration", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speaker diarization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Speaker diarization failed: {e!s}"
        ) from e


@router.post("/assign-voices", response_model=VoiceAssignmentResponse)
async def assign_voices(request: VoiceAssignmentRequest):
    """
    Assign target voices to speakers.

    Phase 10.2.2: Per-speaker voice assignment.

    Args:
        request: Voice assignments for speakers

    Returns:
        Assignment confirmation
    """
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()

        assignments = [
            {
                "speaker_id": a.speaker_id,
                "target_voice_id": a.target_voice_id,
                "pitch_shift": a.pitch_shift,
            }
            for a in request.assignments
        ]

        result = await service.assign_voices(
            project_id=request.project_id,
            assignments=assignments,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Voice assignment failed")
            )

        return VoiceAssignmentResponse(
            project_id=request.project_id,
            assignments_applied=result.get("assignments_applied", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice assignment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Voice assignment failed: {e!s}"
        ) from e


@router.post("/generate", response_model=DubbingResponse)
async def generate_dubbing(request: DubbingRequest):
    """
    Generate dubbed audio with all voice assignments.

    Phase 10.2.3: Background audio preservation.

    Args:
        request: Dubbing generation parameters

    Returns:
        Output audio ID
    """
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()
        result = await service.generate(
            project_id=request.project_id,
            preserve_background=request.preserve_background,
            normalize_loudness=request.normalize_loudness,
            crossfade_duration=request.crossfade_duration,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Dubbing generation failed")
            )

        return DubbingResponse(
            output_audio_id=result["output_audio_id"],
            segments_processed=result.get("segments_processed", 0),
            speakers_dubbed=result.get("speakers_dubbed", 0),
            background_preserved=request.preserve_background,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dubbing generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Dubbing generation failed: {e!s}"
        ) from e


@router.get("/projects", response_model=list[ProjectInfo])
async def list_projects():
    """List all dubbing projects."""
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()
        projects = service.list_projects()

        return [
            ProjectInfo(
                project_id=p["project_id"],
                audio_id=p["audio_id"],
                status=p.get("status", "unknown"),
                speaker_count=p.get("speaker_count", 0),
                voice_assignments=p.get("voice_assignments", {}),
                created_at=p.get("created_at", ""),
            )
            for p in projects
        ]

    except Exception as e:
        logger.error(f"Failed to list projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list projects: {e!s}"
        ) from e


@router.get("/projects/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """Get dubbing project details."""
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()
        project = service.get_project(project_id)

        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project '{project_id}' not found"
            )

        return ProjectInfo(
            project_id=project["project_id"],
            audio_id=project["audio_id"],
            status=project.get("status", "unknown"),
            speaker_count=project.get("speaker_count", 0),
            voice_assignments=project.get("voice_assignments", {}),
            created_at=project.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get project: {e!s}"
        ) from e


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a dubbing project."""
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()
        success = service.delete_project(project_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Project '{project_id}' not found"
            )

        return {"success": True, "message": f"Project '{project_id}' deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete project: {e!s}"
        ) from e


@router.get("/projects/{project_id}/speakers")
async def get_project_speakers(project_id: str):
    """Get speakers detected in a project."""
    try:
        from backend.services.multi_speaker_dubbing import get_multi_speaker_dubbing_service

        service = get_multi_speaker_dubbing_service()
        speakers = service.get_project_speakers(project_id)

        if speakers is None:
            raise HTTPException(
                status_code=404,
                detail=f"Project '{project_id}' not found"
            )

        return {"project_id": project_id, "speakers": speakers}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get speakers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get speakers: {e!s}"
        ) from e
