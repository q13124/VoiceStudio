"""
Video Face Enhancement API Routes.

D.2 Enhancement: REST API for frame-by-frame face enhancement.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video/enhance", tags=["video", "face-enhancement"])


# ============================================================================
# Request/Response Models
# ============================================================================


class EnhanceRequest(BaseModel):
    """Face enhancement request."""
    input_path: str
    output_path: str
    mode: str = "lip_sync"  # lip_sync, expression, restoration, deaging, composite
    quality: str = "standard"  # preview, standard, high, ultra
    audio_path: Optional[str] = None


class EnhanceResponse(BaseModel):
    """Face enhancement response."""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Job status response."""
    job_id: str
    status: str
    progress: float
    frames_processed: int
    total_frames: int
    output_path: Optional[str] = None
    error: Optional[str] = None


class FaceDetectionRequest(BaseModel):
    """Face detection request."""
    image_path: str


class FaceRegionResponse(BaseModel):
    """Face region response."""
    x: int
    y: int
    width: int
    height: int
    confidence: float


# ============================================================================
# Enhancement Endpoints
# ============================================================================


@router.post("/start", response_model=EnhanceResponse)
async def start_enhancement(request: EnhanceRequest):
    """
    Start a face enhancement job.
    
    Args:
        request: Enhancement request
        
    Returns:
        Job information
    """
    try:
        from backend.services.video_face_enhancer import (
            EnhancementMode,
            QualityPreset,
            get_video_face_enhancer,
        )
        
        enhancer = get_video_face_enhancer()
        
        # Parse mode
        try:
            mode = EnhancementMode(request.mode)
        except ValueError:
            mode = EnhancementMode.LIP_SYNC
        
        # Parse quality
        try:
            quality = QualityPreset(request.quality)
        except ValueError:
            quality = QualityPreset.STANDARD
        
        # Create job
        job = await enhancer.create_job(
            input_path=request.input_path,
            output_path=request.output_path,
            mode=mode,
            quality=quality,
            audio_path=request.audio_path,
        )
        
        # Start processing in background
        import asyncio
        asyncio.create_task(enhancer.process_job(job.job_id))
        
        return EnhanceResponse(
            job_id=job.job_id,
            status=job.status,
            message=f"Enhancement job started with {job.total_frames} frames",
        )
        
    except Exception as e:
        logger.error(f"Failed to start enhancement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of an enhancement job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status
    """
    try:
        from backend.services.video_face_enhancer import get_video_face_enhancer
        
        enhancer = get_video_face_enhancer()
        job = enhancer.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            frames_processed=job.frames_processed,
            total_frames=job.total_frames,
            output_path=job.output_path if job.status == "completed" else None,
            error=job.error,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel/{job_id}")
async def cancel_job(job_id: str) -> Dict[str, Any]:
    """
    Cancel an enhancement job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Cancellation result
    """
    try:
        from backend.services.video_face_enhancer import get_video_face_enhancer
        
        enhancer = get_video_face_enhancer()
        success = await enhancer.cancel_job(job_id)
        
        return {
            "success": success,
            "job_id": job_id,
            "message": "Job cancelled" if success else "Failed to cancel job",
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs():
    """List all enhancement jobs."""
    try:
        from backend.services.video_face_enhancer import get_video_face_enhancer
        
        enhancer = get_video_face_enhancer()
        jobs = enhancer.list_jobs()
        
        return [
            JobStatusResponse(
                job_id=job.job_id,
                status=job.status,
                progress=job.progress,
                frames_processed=job.frames_processed,
                total_frames=job.total_frames,
                output_path=job.output_path if job.status == "completed" else None,
                error=job.error,
            )
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Face Detection Endpoints
# ============================================================================


@router.post("/detect-faces", response_model=List[FaceRegionResponse])
async def detect_faces(request: FaceDetectionRequest):
    """
    Detect faces in an image.
    
    Args:
        request: Detection request with image path
        
    Returns:
        List of detected face regions
    """
    try:
        import cv2
        import numpy as np
        
        from backend.services.video_face_enhancer import get_video_face_enhancer
        
        # Load image
        image = cv2.imread(request.image_path)
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        
        enhancer = get_video_face_enhancer()
        faces = await enhancer.detect_faces(image)
        
        return [
            FaceRegionResponse(
                x=face.x,
                y=face.y,
                width=face.width,
                height=face.height,
                confidence=face.confidence,
            )
            for face in faces
        ]
        
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=503, detail="OpenCV not available")
    except Exception as e:
        logger.error(f"Face detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Capability Endpoints
# ============================================================================


@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """
    Get video enhancement capabilities.
    
    Returns:
        Available modes, quality presets, and requirements
    """
    # Check for available dependencies
    opencv_available = False
    ffmpeg_available = False
    
    try:
        import cv2
        opencv_available = True
    except ImportError:
        # ALLOWED: OpenCV is optional - continue with opencv_available=False
        logger.debug("OpenCV not available for video enhancement")
    
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        ffmpeg_available = result.returncode == 0
    except Exception as e:
        # ALLOWED: ffmpeg check may fail - continue with ffmpeg_available=False
        logger.debug(f"FFmpeg availability check failed: {e}")
    
    return {
        "modes": [
            {"id": "lip_sync", "name": "Lip Sync", "description": "Enhance lip movements for dubbing"},
            {"id": "expression", "name": "Expression", "description": "Enhance facial expressions"},
            {"id": "restoration", "name": "Restoration", "description": "Face restoration and upscaling"},
            {"id": "deaging", "name": "De-aging", "description": "Age reduction effect"},
            {"id": "composite", "name": "Composite", "description": "Face compositing"},
        ],
        "quality_presets": [
            {"id": "preview", "name": "Preview", "description": "Fast, lower quality"},
            {"id": "standard", "name": "Standard", "description": "Balanced quality and speed"},
            {"id": "high", "name": "High", "description": "High quality output"},
            {"id": "ultra", "name": "Ultra", "description": "Maximum quality"},
        ],
        "dependencies": {
            "opencv": opencv_available,
            "ffmpeg": ffmpeg_available,
        },
        "supported_formats": ["mp4", "avi", "mov", "mkv"],
        "max_resolution": "4K (3840x2160)",
    }
