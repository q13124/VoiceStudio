"""
Voice Effects and Realtime Voice Changer Routes

Phase 9.3: Expose RealtimeVoiceChangerService via REST API.
Provides endpoints for voice effects, presets, and hotkey management.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice-effects", tags=["voice-effects"])


# --- Request/Response Models ---


class ApplyEffectRequest(BaseModel):
    """Request to apply voice effect."""

    audio_id: str = Field(..., description="Audio ID to process")
    effect_id: str = Field(..., description="Effect preset ID or custom effect")
    parameters: dict[str, Any] | None = Field(None, description="Custom effect parameters")


class ApplyEffectResponse(BaseModel):
    """Response for applied effect."""

    output_audio_id: str
    effect_id: str
    processing_time_ms: float


class EffectPreset(BaseModel):
    """Voice effect preset."""

    id: str
    name: str
    category: str
    description: str
    parameters: dict[str, Any]


class HotkeyConfig(BaseModel):
    """Hotkey configuration for voice switching."""

    hotkey: str = Field(..., description="Hotkey combination (e.g., 'ctrl+1')")
    effect_id: str = Field(..., description="Effect preset to activate")
    enabled: bool = Field(True)


class RealtimeSessionRequest(BaseModel):
    """Request to start realtime voice changer session."""

    input_device: str | None = Field(None, description="Input audio device name")
    output_device: str | None = Field(None, description="Output audio device name")
    effect_id: str | None = Field(None, description="Initial effect preset")
    latency_mode: str = Field("balanced", description="Latency mode: low, balanced, high_quality")


class RealtimeSessionResponse(BaseModel):
    """Response for realtime session."""

    session_id: str
    status: str
    latency_ms: float


# --- API Endpoints ---


@router.get("/presets", response_model=list[EffectPreset])
async def list_effect_presets():
    """
    List all available voice effect presets.

    Phase 9.3.3: Voice effect library.

    Returns:
        List of effect presets organized by category
    """
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        presets = service.list_presets()

        return [
            EffectPreset(
                id=p["id"],
                name=p["name"],
                category=p.get("category", "custom"),
                description=p.get("description", ""),
                parameters=p.get("parameters", {}),
            )
            for p in presets
        ]

    except Exception as e:
        logger.error(f"Failed to list presets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list presets: {e!s}") from e


@router.get("/presets/{preset_id}", response_model=EffectPreset)
async def get_effect_preset(preset_id: str):
    """Get details of a specific effect preset."""
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        preset = service.get_preset(preset_id)

        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")

        return EffectPreset(
            id=preset["id"],
            name=preset["name"],
            category=preset.get("category", "custom"),
            description=preset.get("description", ""),
            parameters=preset.get("parameters", {}),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get preset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get preset: {e!s}") from e


@router.post("/apply", response_model=ApplyEffectResponse)
async def apply_voice_effect(request: ApplyEffectRequest):
    """
    Apply voice effect to audio.

    Args:
        request: Effect application parameters

    Returns:
        Processed audio ID
    """
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        result = await service.apply_effect(
            audio_id=request.audio_id,
            effect_id=request.effect_id,
            parameters=request.parameters,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500, detail=result.get("error", "Effect application failed")
            )

        return ApplyEffectResponse(
            output_audio_id=result["output_audio_id"],
            effect_id=request.effect_id,
            processing_time_ms=result.get("processing_time_ms", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Effect application failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Effect application failed: {e!s}") from e


@router.get("/categories")
async def list_effect_categories():
    """List effect preset categories."""
    return {
        "categories": [
            {"id": "pitch", "name": "Pitch Effects", "icon": "music_note"},
            {"id": "character", "name": "Character Voices", "icon": "person"},
            {"id": "environment", "name": "Environment", "icon": "landscape"},
            {"id": "creative", "name": "Creative Effects", "icon": "auto_awesome"},
            {"id": "custom", "name": "Custom", "icon": "tune"},
        ]
    }


# --- Hotkey Management ---


@router.get("/hotkeys", response_model=list[HotkeyConfig])
async def list_hotkeys():
    """
    List configured hotkeys for voice switching.

    Phase 9.3.5: Hotkey voice switching.
    """
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        hotkeys = service.list_hotkeys()

        return [
            HotkeyConfig(
                hotkey=h["hotkey"],
                effect_id=h["effect_id"],
                enabled=h.get("enabled", True),
            )
            for h in hotkeys
        ]

    except Exception as e:
        logger.error(f"Failed to list hotkeys: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list hotkeys: {e!s}") from e


@router.post("/hotkeys")
async def set_hotkey(config: HotkeyConfig):
    """Configure a hotkey for voice switching."""
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        success = service.set_hotkey(
            hotkey=config.hotkey,
            effect_id=config.effect_id,
            enabled=config.enabled,
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to configure hotkey")

        return {"success": True, "message": f"Hotkey '{config.hotkey}' configured"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set hotkey: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to set hotkey: {e!s}") from e


@router.delete("/hotkeys/{hotkey}")
async def remove_hotkey(hotkey: str):
    """Remove a configured hotkey."""
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        success = service.remove_hotkey(hotkey)

        if not success:
            raise HTTPException(status_code=404, detail=f"Hotkey '{hotkey}' not found")

        return {"success": True, "message": f"Hotkey '{hotkey}' removed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove hotkey: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to remove hotkey: {e!s}") from e


# --- Realtime Session Management ---


@router.post("/realtime/start", response_model=RealtimeSessionResponse)
async def start_realtime_session(request: RealtimeSessionRequest):
    """
    Start a realtime voice changer session.

    Phase 9.3.2: Low-latency RVC pipeline.
    """
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        result = await service.start_realtime_session(
            input_device=request.input_device,
            output_device=request.output_device,
            effect_id=request.effect_id,
            latency_mode=request.latency_mode,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=500, detail=result.get("error", "Failed to start realtime session")
            )

        return RealtimeSessionResponse(
            session_id=result["session_id"],
            status="active",
            latency_ms=result.get("latency_ms", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start realtime session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to start realtime session: {e!s}"
        ) from e


@router.post("/realtime/{session_id}/stop")
async def stop_realtime_session(session_id: str):
    """Stop a realtime voice changer session."""
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        success = await service.stop_realtime_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

        return {"success": True, "message": f"Session '{session_id}' stopped"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop realtime session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to stop realtime session: {e!s}"
        ) from e


@router.post("/realtime/{session_id}/effect")
async def change_realtime_effect(session_id: str, effect_id: str):
    """Change the active effect in a realtime session."""
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        success = await service.change_effect(session_id, effect_id)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Session '{session_id}' not found or effect change failed"
            )

        return {"success": True, "effect_id": effect_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change effect: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to change effect: {e!s}") from e


@router.get("/audio-devices")
async def list_audio_devices():
    """List available audio input/output devices."""
    try:
        from backend.voice.synthesis.realtime_voice_changer import get_realtime_voice_changer

        service = get_realtime_voice_changer()
        devices = service.list_audio_devices()

        return devices

    except Exception as e:
        logger.error(f"Failed to list audio devices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list audio devices: {e!s}") from e
