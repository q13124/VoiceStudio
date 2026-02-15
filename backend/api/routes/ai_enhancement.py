"""
AI Audio Enhancement Routes

Phase 9.4: Expose AIAudioEnhancementService via REST API.
Provides endpoints for one-click enhancement, voice isolation,
room reverb removal, and audio repair.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai-enhancement", tags=["ai-enhancement"])


# --- Request/Response Models ---


class EnhanceRequest(BaseModel):
    """Request for audio enhancement."""
    audio_id: str = Field(..., description="Audio ID to enhance")
    mode: str = Field("balanced", description="Enhancement mode: speech, music, balanced, podcast, broadcast")
    strength: float = Field(0.5, ge=0.0, le=1.0, description="Enhancement strength (0.0-1.0)")
    preset: str | None = Field(None, description="Optional preset name")


class EnhanceResponse(BaseModel):
    """Response for audio enhancement."""
    output_audio_id: str
    mode: str
    strength: float
    improvements: dict[str, float]


class VoiceIsolationRequest(BaseModel):
    """Request for voice isolation."""
    audio_id: str = Field(..., description="Audio ID to process")
    preserve_vocals: bool = Field(True, description="Keep vocals (True) or remove vocals (False)")


class VoiceIsolationResponse(BaseModel):
    """Response for voice isolation."""
    output_audio_id: str
    vocals_removed: bool
    separation_quality: float


class DeReverbRequest(BaseModel):
    """Request for room reverb removal."""
    audio_id: str = Field(..., description="Audio ID to process")
    strength: float = Field(0.7, ge=0.0, le=1.0, description="De-reverb strength")


class DeReverbResponse(BaseModel):
    """Response for de-reverb."""
    output_audio_id: str
    reverb_reduction_db: float
    estimated_rt60: float


class RepairRequest(BaseModel):
    """Request for audio repair."""
    audio_id: str = Field(..., description="Audio ID to repair")
    repair_clicks: bool = Field(True, description="Repair clicks and pops")
    repair_clipping: bool = Field(True, description="Repair clipping distortion")
    reduce_noise: bool = Field(False, description="Apply noise reduction")


class RepairResponse(BaseModel):
    """Response for audio repair."""
    output_audio_id: str
    clicks_repaired: int
    clipping_repaired_samples: int
    noise_reduction_db: float


class PresetInfo(BaseModel):
    """Enhancement preset information."""
    name: str
    description: str
    mode: str
    strength: float


# --- API Endpoints ---


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_audio(request: EnhanceRequest):
    """
    Apply one-click AI enhancement to audio.

    Phase 9.4.1: One-click enhancement with adaptive processing.
    Phase 9.4.2: Strength slider (0-100%).

    Args:
        request: Enhancement parameters

    Returns:
        Enhanced audio ID and improvement metrics
    """
    try:
        from backend.services.ai_audio_enhancement import get_ai_enhancement_service

        service = get_ai_enhancement_service()
        result = await service.enhance(
            audio_id=request.audio_id,
            mode=request.mode,
            strength=request.strength,
            preset=request.preset,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Enhancement failed")
            )

        return EnhanceResponse(
            output_audio_id=result["output_audio_id"],
            mode=result.get("mode", request.mode),
            strength=result.get("strength", request.strength),
            improvements=result.get("improvements", {}),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio enhancement failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Audio enhancement failed: {e!s}"
        ) from e


@router.post("/isolate-voice", response_model=VoiceIsolationResponse)
async def isolate_voice(request: VoiceIsolationRequest):
    """
    Isolate or remove voice from audio.

    Phase 9.4.3: AI-powered voice/music separation.

    Args:
        request: Voice isolation parameters

    Returns:
        Processed audio ID
    """
    try:
        from backend.services.ai_audio_enhancement import get_ai_enhancement_service

        service = get_ai_enhancement_service()
        result = await service.isolate_voice(
            audio_id=request.audio_id,
            preserve_vocals=request.preserve_vocals,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Voice isolation failed")
            )

        return VoiceIsolationResponse(
            output_audio_id=result["output_audio_id"],
            vocals_removed=not request.preserve_vocals,
            separation_quality=result.get("quality", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice isolation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Voice isolation failed: {e!s}"
        ) from e


@router.post("/de-reverb", response_model=DeReverbResponse)
async def remove_reverb(request: DeReverbRequest):
    """
    Remove room reverb from audio.

    Phase 9.4.4: Intelligent room reverb removal.

    Args:
        request: De-reverb parameters

    Returns:
        Processed audio ID
    """
    try:
        from backend.services.ai_audio_enhancement import get_ai_enhancement_service

        service = get_ai_enhancement_service()
        result = await service.remove_reverb(
            audio_id=request.audio_id,
            strength=request.strength,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "De-reverb failed")
            )

        return DeReverbResponse(
            output_audio_id=result["output_audio_id"],
            reverb_reduction_db=result.get("reverb_reduction_db", 0.0),
            estimated_rt60=result.get("estimated_rt60", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"De-reverb failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"De-reverb failed: {e!s}"
        ) from e


@router.post("/repair", response_model=RepairResponse)
async def repair_audio(request: RepairRequest):
    """
    Repair audio artifacts (clicks, clipping, noise).

    Phase 9.4.5: Click, pop, and clipping repair.

    Args:
        request: Repair parameters

    Returns:
        Repaired audio ID and repair stats
    """
    try:
        from backend.services.ai_audio_enhancement import get_ai_enhancement_service

        service = get_ai_enhancement_service()
        result = await service.repair(
            audio_id=request.audio_id,
            repair_clicks=request.repair_clicks,
            repair_clipping=request.repair_clipping,
            reduce_noise=request.reduce_noise,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Audio repair failed")
            )

        return RepairResponse(
            output_audio_id=result["output_audio_id"],
            clicks_repaired=result.get("clicks_repaired", 0),
            clipping_repaired_samples=result.get("clipping_repaired_samples", 0),
            noise_reduction_db=result.get("noise_reduction_db", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio repair failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Audio repair failed: {e!s}"
        ) from e


@router.get("/presets", response_model=list[PresetInfo])
async def list_presets():
    """List available enhancement presets."""
    try:
        from backend.services.ai_audio_enhancement import get_ai_enhancement_service

        service = get_ai_enhancement_service()
        presets = service.list_presets()

        return [
            PresetInfo(
                name=p["name"],
                description=p.get("description", ""),
                mode=p.get("mode", "balanced"),
                strength=p.get("strength", 0.5),
            )
            for p in presets
        ]

    except Exception as e:
        logger.error(f"Failed to list presets: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list presets: {e!s}"
        ) from e


@router.get("/modes")
async def list_modes():
    """List available enhancement modes."""
    return {
        "modes": [
            {"id": "speech", "name": "Speech", "description": "Optimized for voice clarity"},
            {"id": "music", "name": "Music", "description": "Preserves musical dynamics"},
            {"id": "balanced", "name": "Balanced", "description": "General-purpose enhancement"},
            {"id": "podcast", "name": "Podcast", "description": "Multi-speaker optimization"},
            {"id": "broadcast", "name": "Broadcast", "description": "Broadcast-ready processing"},
        ]
    }
