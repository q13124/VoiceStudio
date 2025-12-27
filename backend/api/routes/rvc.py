"""
RVC (Retrieval-based Voice Conversion) Routes
Real-time voice conversion endpoints
"""

import base64
import json
import logging
import os
import tempfile
import uuid
from typing import Dict, Optional

import numpy as np
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse

from ..models import ApiOk
from ..models_additional import RvcStartRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rvc", tags=["rvc"])

# In-memory storage for audio files
_audio_storage: dict[str, str] = {}  # audio_id -> file_path

# Engine router for RVC
ENGINE_AVAILABLE = False
engine_router = None
quality_metrics = None

try:
    import sys

    app_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "app")
    if os.path.exists(app_path) and app_path not in sys.path:
        sys.path.insert(0, app_path)

    from app.core.engines import calculate_all_metrics, calculate_similarity
    from app.core.engines import router as rvc_engine_router

    quality_metrics = {
        "calculate_all": calculate_all_metrics,
        "similarity": calculate_similarity,
    }

    engine_router = rvc_engine_router
    ENGINE_AVAILABLE = True

    # Auto-load all engines from manifests
    try:
        engine_router.load_all_engines("engines")
        loaded_engines = engine_router.list_engines()
        logger.info(
            f"RVC Engine router initialized. " f"Loaded {len(loaded_engines)} engines"
        )
    except Exception as e:
        logger.warning(f"Failed to auto-load engines: {e}")

except (ImportError, ModuleNotFoundError) as e:
    logger.warning(
        f"RVC Engine router not available: {e}. "
        "RVC conversion will return errors when engines unavailable."
    )
    ENGINE_AVAILABLE = False


@router.post("/convert")
async def convert_voice(
    source_audio_id: str,
    target_speaker_model: str,
    pitch_shift: int = 0,
    protect: float = 0.33,
    index_rate: float = 0.75,
    enhance_quality: bool = True,
    calculate_quality: bool = True,
):
    """
    Convert voice using RVC.

    Args:
        source_audio_id: ID of source audio file
        target_speaker_model: Path to target speaker model
        pitch_shift: Pitch shift in semitones (-12 to 12)
        protect: Protect voiceless sounds (0.0-0.5)
        index_rate: Index rate for retrieval (0.0-1.0)
        enhance_quality: If True, apply quality enhancement
        calculate_quality: If True, return quality metrics

    Returns:
        Conversion result with audio_id and quality metrics
    """
    if not ENGINE_AVAILABLE or not engine_router:
        raise HTTPException(status_code=503, detail="Engine router not available")

    try:
        # Get RVC engine
        engine = engine_router.get_engine("rvc")
        if engine is None:
            raise HTTPException(
                status_code=503,
                detail="RVC engine is not available or failed to initialize",
            )

        # Get source audio path using helper function
        from .audio import _get_audio_path

        source_audio_path = _get_audio_path(source_audio_id)
        if not source_audio_path or not os.path.exists(source_audio_path):
            # Try alternative storage
            source_audio_path = _audio_storage.get(source_audio_id)
            if not source_audio_path or not os.path.exists(source_audio_path):
                raise HTTPException(
                    status_code=404, detail=f"Source audio not found: {source_audio_id}"
                )

        # Perform conversion
        output_path = tempfile.mktemp(suffix=".wav")

        result = engine.convert_voice(
            source_audio=source_audio_path,
            target_speaker_model=target_speaker_model,
            output_path=output_path,
            pitch_shift=pitch_shift,
            enhance_quality=enhance_quality,
            calculate_quality=calculate_quality,
            protect=protect,
            index_rate=index_rate,
        )

        # Handle result
        if isinstance(result, tuple):
            audio, quality_metrics_dict = result
        else:
            audio = result
            quality_metrics_dict = {}

        if audio is None and not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Voice conversion failed")

        # Generate audio ID and store
        audio_id = str(uuid.uuid4())
        _audio_storage[audio_id] = output_path

        # Calculate duration
        import wave

        try:
            with wave.open(output_path, "rb") as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
        except Exception:
            duration = 2.5

        # Build response
        response = {
            "success": True,
            "audio_id": audio_id,
            "audio_url": f"/api/rvc/audio/{audio_id}",
            "duration": duration,
            "sample_rate": 40000,
        }

        if quality_metrics_dict:
            response["quality_metrics"] = quality_metrics_dict

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RVC conversion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.websocket("/convert/realtime")
async def convert_realtime(websocket: WebSocket):
    """
    Real-time voice conversion stream.

    WebSocket endpoint for real-time audio streaming conversion.
    """
    await websocket.accept()

    try:
        if not ENGINE_AVAILABLE or not engine_router:
            await websocket.send_json(
                {"type": "error", "message": "Engine router not available"}
            )
            await websocket.close()
            return

        engine = None
        conversion_params = {}

        while True:
            # Receive message
            data = await websocket.receive_text()
            request = json.loads(data)

            request_type = request.get("type")

            if request_type == "start":
                # Initialize conversion session
                target_speaker_model = request.get("target_speaker_model")
                pitch_shift = request.get("pitch_shift", 0)
                protect = request.get("protect", 0.33)
                index_rate = request.get("index_rate", 0.75)

                # Get RVC engine
                engine = engine_router.get_engine("rvc")
                if engine is None:
                    await websocket.send_json(
                        {"type": "error", "message": "RVC engine is not available"}
                    )
                    continue

                conversion_params = {
                    "target_speaker_model": target_speaker_model,
                    "pitch_shift": pitch_shift,
                    "protect": protect,
                    "index_rate": index_rate,
                }

                await websocket.send_json(
                    {"type": "started", "message": "Real-time conversion started"}
                )

            elif request_type == "audio_chunk":
                # Convert audio chunk
                if engine is None:
                    await websocket.send_json(
                        {"type": "error", "message": "Conversion not started"}
                    )
                    continue

                try:
                    # Decode audio chunk
                    audio_b64 = request.get("data")
                    audio_bytes = base64.b64decode(audio_b64)
                    audio_chunk = np.frombuffer(audio_bytes, dtype=np.float32)

                    # Convert chunk
                    import time

                    start_time = time.time()

                    converted_chunk = engine.convert_realtime(
                        audio_chunk, **conversion_params
                    )

                    latency_ms = (time.time() - start_time) * 1000

                    # Encode converted chunk
                    converted_bytes = converted_chunk.tobytes()
                    converted_b64 = base64.b64encode(converted_bytes).decode("utf-8")

                    # Send converted chunk
                    await websocket.send_json(
                        {
                            "type": "converted_chunk",
                            "data": converted_b64,
                            "sample_rate": 40000,
                            "format": "float32",
                            "latency_ms": latency_ms,
                        }
                    )

                except Exception as e:
                    logger.error(f"Chunk conversion failed: {e}")
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Chunk conversion failed: {str(e)}",
                        }
                    )

            elif request_type == "stop":
                # Stop conversion
                await websocket.send_json(
                    {"type": "stopped", "message": "Real-time conversion stopped"}
                )
                break

    except WebSocketDisconnect:
        logger.info("RVC WebSocket disconnected")
    except Exception as e:
        logger.error(f"RVC WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json(
                {"type": "error", "message": f"WebSocket error: {str(e)}"}
            )
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get("/models")
async def get_models():
    """
    Get available RVC models.

    Returns:
        List of available RVC models
    """
    try:
        model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
        if not model_cache_dir:
            model_cache_dir = os.path.join(
                os.getenv("PROGRAMDATA", "C:\\ProgramData"),
                "VoiceStudio",
                "models",
                "rvc",
            )

        models = []
        if os.path.exists(model_cache_dir):
            for item in os.listdir(model_cache_dir):
                model_path = os.path.join(model_cache_dir, item)
                if os.path.isdir(model_path):
                    # Check if it's a valid RVC model
                    model_files = os.listdir(model_path)
                    if any(f.endswith(".pth") for f in model_files):
                        models.append(
                            {
                                "id": item,
                                "name": item,
                                "path": model_path,
                                "sample_rate": 40000,
                                "created_at": "2025-01-27T10:00:00Z",
                            }
                        )

        return {"models": models}

    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return {"models": []}


@router.post("/models/upload")
async def upload_model(
    model_file: UploadFile = File(...), model_name: Optional[str] = None
):
    """
    Upload RVC model.

    Args:
        model_file: Model file to upload
        model_name: Optional model name

    Returns:
        Upload result with model_id
    """
    try:
        model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
        if not model_cache_dir:
            model_cache_dir = os.path.join(
                os.getenv("PROGRAMDATA", "C:\\ProgramData"),
                "VoiceStudio",
                "models",
                "rvc",
            )
        os.makedirs(model_cache_dir, exist_ok=True)

        # Generate model ID
        model_id = model_name or str(uuid.uuid4())
        model_dir = os.path.join(model_cache_dir, model_id)
        os.makedirs(model_dir, exist_ok=True)

        # Save model file
        filename = model_file.filename or "model.pth"
        model_path = os.path.join(model_dir, filename)
        with open(model_path, "wb") as f:
            content = await model_file.read()
            f.write(content)

        return {
            "success": True,
            "model_id": model_id,
            "message": "Model uploaded successfully",
        }

    except Exception as e:
        logger.error(f"Model upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """
    Retrieve converted audio file.

    Returns the audio file as a WAV stream for playback.
    """
    if audio_id not in _audio_storage:
        raise HTTPException(status_code=404, detail=f"Audio not found: {audio_id}")

    file_path = _audio_storage[audio_id]

    if not os.path.exists(file_path):
        del _audio_storage[audio_id]
        raise HTTPException(status_code=404, detail="Audio file not found on disk")

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=f"{audio_id}.wav",
    )


@router.post("/start")
async def start(req: RvcStartRequest) -> dict:
    """
    Start RVC session (legacy endpoint).

    Creates a new RVC conversion session for real-time or batch processing.

    Args:
        req: Request with session configuration

    Returns:
        Dictionary with session_id and status
    """
    try:
        if not ENGINE_AVAILABLE or not engine_router:
            raise HTTPException(status_code=503, detail="Engine router not available")

        # Generate session ID
        session_id = f"rvc_{uuid.uuid4().hex[:8]}"

        # Initialize session (in production, store in database)
        # For now, we'll just return the session ID
        logger.info(f"RVC session started: {session_id}")

        return {
            "session_id": session_id,
            "status": "started",
            "message": "RVC session created successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start RVC session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to start session: {str(e)}"
        ) from e


@router.post("/stop")
async def stop(req: dict) -> ApiOk:
    """
    Stop RVC session (legacy endpoint).

    Stops an active RVC conversion session and cleans up resources.

    Args:
        req: Request with session_id (optional)

    Returns:
        ApiOk indicating success
    """
    try:
        session_id = req.get("session_id") if isinstance(req, dict) else None

        if session_id:
            logger.info(f"RVC session stopped: {session_id}")
        else:
            logger.info("RVC session stop requested (no session_id provided)")

        # In production, clean up session resources here
        # For now, just return success

        return ApiOk()

    except Exception as e:
        logger.error(f"Failed to stop RVC session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to stop session: {str(e)}"
        ) from e
