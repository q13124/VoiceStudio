"""
VoiceStudio TTS API Router with Audio Metrics Integration
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pathlib import Path
import tempfile
import base64
import uuid

from services.api.voice_engine_router import settings, AudioMetrics, ROUTER, REGISTRY
from services.audio.metrics import compute_audio_metrics

router = APIRouter()

class TTSRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    text: str = Field(min_length=1)
    language: str | None = None
    profile: str | None = None
    quality: str = Field(default="balanced")
    voice_profile: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)

class TTSItem(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str
    engine: str
    url: str
    metrics: AudioMetrics | None = None   # <-- additive

class TTSResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    items: list[TTSItem]

def generate_audio_somehow(req: TTSRequest) -> list[dict]:
    """Generate audio using the voice engine router"""
    try:
        # Select engine and generate audio
        engine_id, tried_order = ROUTER.select_engine(
            text=req.text, 
            language=req.language or "en", 
            tier=req.quality
        )
        
        # Generate audio bytes
        audio_bytes = ROUTER.generate(
            engine_id=engine_id,
            text=req.text,
            voice_profile=req.voice_profile,
            params=req.params
        )
        
        # Create a unique ID and URL for the audio
        audio_id = str(uuid.uuid4())
        audio_url = f"/audio/{audio_id}.wav"
        
        return [{
            "id": audio_id,
            "engine": engine_id,
            "wav_bytes": audio_bytes,
            "url": audio_url,
            "tried_order": tried_order
        }]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

@router.post("/v1/generate", response_model=TTSResponse)
def generate_tts(req: TTSRequest) -> TTSResponse:
    """
    Generate TTS with optional audio metrics analysis.
    When metrics are enabled, compute and attach professional audio analysis.
    """
    # 1) Generate audio using existing router
    generated: list[dict] = generate_audio_somehow(req)

    items: list[TTSItem] = []
    for g in generated:
        m: AudioMetrics | None = None

        if settings.metrics_enabled:
            try:
                # We need a real WAV path to analyze:
                if "wav_path" in g and g["wav_path"]:
                    wav_path = Path(g["wav_path"])
                else:
                    # Dump bytes to a temp file for analysis
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp.write(g["wav_bytes"])
                        wav_path = Path(tmp.name)
                    
                    try:
                        m = compute_audio_metrics(wav_path)
                    finally:
                        # Clean up temp file
                        try:
                            wav_path.unlink()
                        except Exception:
                            pass
            except Exception:
                m = None

        items.append(TTSItem(
            id=g["id"],
            engine=g["engine"],
            url=g["url"],
            metrics=m
        ))

    return TTSResponse(items=items)

@router.get("/v1/engines")
def list_engines():
    """List available TTS engines and their capabilities"""
    return REGISTRY.discover()

@router.get("/v1/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engines": len(REGISTRY.list()),
        "metrics_enabled": settings.metrics_enabled
    }
