"""
Real-Time Voice Converter Routes

Endpoints for real-time voice conversion and streaming.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/realtime-converter", tags=["realtime-converter"])

# In-memory converter sessions (replace with database in production)
_converter_sessions: Dict[str, Dict] = {}


class ConverterSession(BaseModel):
    """A real-time converter session."""

    session_id: str
    source_profile_id: str
    target_profile_id: str
    status: str  # active, paused, stopped
    created: str  # ISO datetime string


class ConverterStartRequest(BaseModel):
    """Request to start a converter session."""

    source_profile_id: str
    target_profile_id: str


class ConverterStartResponse(BaseModel):
    """Response from starting a converter session."""

    session_id: str
    message: str


class ConverterSessionListResponse(BaseModel):
    """Response from listing converter sessions."""

    sessions: List[ConverterSession]


@router.post("/start", response_model=ConverterStartResponse)
async def start_converter_session(request: ConverterStartRequest):
    """Start a new real-time converter session."""
    import uuid
    from datetime import datetime

    try:
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        session = {
            "session_id": session_id,
            "source_profile_id": request.source_profile_id,
            "target_profile_id": request.target_profile_id,
            "status": "active",
            "created": now,
        }

        _converter_sessions[session_id] = session
        logger.info(f"Started converter session: {session_id}")

        return ConverterStartResponse(
            session_id=session_id,
            message="Converter session started",
        )
    except Exception as e:
        logger.error(f"Failed to start converter session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start session: {str(e)}",
        ) from e


@router.get("", response_model=ConverterSessionListResponse)
@cache_response(ttl=5)  # Cache for 5 seconds (sessions change frequently)
async def list_converter_sessions():
    """List all converter sessions."""
    sessions = list(_converter_sessions.values())

    # Sort by created date (newest first)
    sessions.sort(key=lambda s: s.get("created", ""), reverse=True)

    return ConverterSessionListResponse(
        sessions=[
            ConverterSession(
                session_id=session["session_id"],
                source_profile_id=session["source_profile_id"],
                target_profile_id=session["target_profile_id"],
                status=session["status"],
                created=session["created"],
            )
            for session in sessions
        ]
    )


@router.get("/{session_id}", response_model=ConverterSession)
async def get_converter_session(session_id: str):
    """Get converter session status."""
    if session_id not in _converter_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _converter_sessions[session_id]
    return ConverterSession(
        session_id=session["session_id"],
        source_profile_id=session["source_profile_id"],
        target_profile_id=session["target_profile_id"],
        status=session["status"],
        created=session["created"],
    )


@router.post("/{session_id}/pause")
async def pause_converter_session(session_id: str):
    """Pause a converter session."""
    if session_id not in _converter_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    _converter_sessions[session_id]["status"] = "paused"
    logger.info(f"Paused converter session: {session_id}")
    return {"success": True}


@router.post("/{session_id}/resume")
async def resume_converter_session(session_id: str):
    """Resume a converter session."""
    if session_id not in _converter_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    _converter_sessions[session_id]["status"] = "active"
    logger.info(f"Resumed converter session: {session_id}")
    return {"success": True}


@router.post("/{session_id}/stop")
async def stop_converter_session(session_id: str):
    """Stop a converter session."""
    if session_id not in _converter_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    _converter_sessions[session_id]["status"] = "stopped"
    logger.info(f"Stopped converter session: {session_id}")
    return {"success": True}


@router.delete("/{session_id}")
async def delete_converter_session(session_id: str):
    """Delete a converter session."""
    if session_id not in _converter_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del _converter_sessions[session_id]
    logger.info(f"Deleted converter session: {session_id}")
    return {"success": True}


@router.websocket("/{session_id}/stream")
async def converter_stream(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time audio streaming."""
    if session_id not in _converter_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return

    await websocket.accept()
    logger.info(f"WebSocket connection opened for session: {session_id}")

    try:
        session = _converter_sessions[session_id]
        source_profile_id = session["source_profile_id"]
        target_profile_id = session["target_profile_id"]

        # Try to get RVC engine for voice conversion
        ENGINE_AVAILABLE = False
        engine_router = None

        try:
            import os
            import sys

            app_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "app")
            if os.path.exists(app_path) and app_path not in sys.path:
                sys.path.insert(0, app_path)

            from app.core.engines import router as engine_router

            ENGINE_AVAILABLE = True

            # Try to load engines
            try:
                engine_router.load_all_engines("engines")
            except Exception as e:
                logger.warning(f"Could not load engines for realtime conversion: {e}")
        except ImportError:
            logger.warning("Engine router not available for realtime conversion")
            ENGINE_AVAILABLE = False

        # Get RVC engine if available
        rvc_engine = None
        if ENGINE_AVAILABLE and engine_router:
            try:
                rvc_engine = engine_router.get_engine("rvc")
            except Exception as e:
                logger.debug(f"RVC engine not available: {e}")

        # Get target profile audio path
        from .profiles import _profiles

        target_profile_audio_path = None

        if target_profile_id in _profiles:
            target_profile = _profiles[target_profile_id]
            if target_profile.reference_audio_url:
                if not target_profile.reference_audio_url.startswith("http"):
                    target_profile_audio_path = target_profile.reference_audio_url

        if not target_profile_audio_path:
            # Try standard profile directory
            profile_dir = os.path.join(
                os.path.expanduser("~"), ".voicestudio", "profiles", target_profile_id
            )
            potential_paths = [
                os.path.join(profile_dir, "reference.wav"),
                os.path.join(profile_dir, "reference_audio.wav"),
            ]
            for path in potential_paths:
                if os.path.exists(path):
                    target_profile_audio_path = path
                    break

        # Process audio chunks
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()

            if (
                rvc_engine
                and target_profile_audio_path
                and os.path.exists(target_profile_audio_path)
            ):
                try:
                    # Convert audio chunk using RVC engine
                    import tempfile

                    import numpy as np

                    # Convert bytes to numpy array (assuming float32 PCM)
                    audio_chunk = np.frombuffer(data, dtype=np.float32)

                    # Save chunk to temporary file for RVC processing
                    with tempfile.NamedTemporaryFile(
                        suffix=".wav", delete=False
                    ) as tmp_input:
                        import soundfile as sf

                        sf.write(
                            tmp_input.name, audio_chunk, 40000
                        )  # RVC typically uses 40kHz

                        # Convert using RVC
                        with tempfile.NamedTemporaryFile(
                            suffix=".wav", delete=False
                        ) as tmp_output:
                            result = rvc_engine.convert_voice(
                                source_audio=tmp_input.name,
                                target_speaker_model=target_profile_audio_path,
                                output_path=tmp_output.name,
                                pitch_shift=0,
                                enhance_quality=False,
                                calculate_quality=False,
                            )

                            # Read converted audio
                            converted_audio, _ = sf.read(tmp_output.name)

                            # Send converted audio back
                            await websocket.send_bytes(
                                converted_audio.astype(np.float32).tobytes()
                            )

                            # Clean up temp files
                            try:
                                os.unlink(tmp_input.name)
                                os.unlink(tmp_output.name)
                            except:
                                ...
                except Exception as e:
                    logger.error(f"Failed to convert audio chunk: {e}", exc_info=True)
                    # Fallback: echo back original audio
                    await websocket.send_bytes(data)
            else:
                # No engine available or profile audio not found
                logger.error(
                    f"Realtime conversion not available for session {session_id}. "
                    f"Engine available: {rvc_engine is not None}, "
                    f"Profile audio: {target_profile_audio_path is not None}"
                )
                await websocket.close(
                    code=1003,  # Unsupported Data
                    reason=(
                        "Realtime conversion not available. "
                        "Engine or profile audio not found."
                    ),
                )
                return
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await websocket.close(code=1011, reason=str(e))
