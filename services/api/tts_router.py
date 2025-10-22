from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pathlib import Path
import tempfile

from services.settings import settings
from services.metrics.audio_metrics_new import compute_audio_metrics
from services.models.audio_metrics import AudioMetrics
from services.models.output_chain import OutputChain
from services.models.ab_summary import (
    ABSummaryRequest,
    ABSummaryResponse,
    EngineStats,
    ABRating,
)

router = APIRouter()


class TTSRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    text: str = Field(min_length=1)
    language: str | None = None
    profile: str | None = None
    # Optional chain (existing)
    # output_chain: OutputChain | None = None


class TTSItem(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str
    engine: str
    url: str
    metrics: AudioMetrics | None = None  # <-- additive


class TTSResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    items: list[TTSItem]


def generate_audio_somehow(req: TTSRequest) -> list[dict]:
    """Mock audio generation for testing purposes"""
    import base64
    import math
    import struct
    import io

    # Generate a simple sine wave as mock audio
    sample_rate = 22050
    duration = max(0.2, min(10.0, len(req.text) / 20.0))
    tone = 440.0
    samples = int(sample_rate * duration)

    # Generate PCM data
    pcm_data = bytearray()
    for n in range(samples):
        pcm_data += struct.pack(
            "<h", int(32767 * 0.1 * math.sin(2 * math.pi * tone * (n / sample_rate)))
        )

    # Convert to WAV format
    byte_rate = sample_rate * 2
    block_align = 2
    riff = io.BytesIO()
    riff.write(b"RIFF")
    riff.write(struct.pack("<I", 36 + len(pcm_data)))
    riff.write(b"WAVEfmt ")
    riff.write(
        struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, byte_rate, block_align, 16)
    )
    riff.write(b"data")
    riff.write(struct.pack("<I", len(pcm_data)))
    riff.write(pcm_data)
    wav_bytes = riff.getvalue()

    # Create data URL
    b64_data = base64.b64encode(wav_bytes).decode("ascii")
    url = f"data:audio/wav;base64,{b64_data}"

    return [
        {
            "id": "mock_item_1",
            "engine": "mock_engine",
            "url": url,
            "wav_bytes": wav_bytes,
        }
    ]


@router.post("/v1/generate", response_model=TTSResponse)
def generate_tts(req: TTSRequest) -> TTSResponse:
    """
    Existing behavior preserved. When metrics are enabled, compute and attach.
    """
    # 1) Your existing generation — returns a list of (id, engine, wav_bytes or wav_path, url)
    # For illustration we assume you produce bytes and url after storage:
    generated: list[dict] = generate_audio_somehow(req)  # <-- your existing function

    items: list[TTSItem] = []
    for g in generated:
        m: AudioMetrics | None = None

        if settings.metrics_enabled:
            try:
                # We need a real WAV path to analyze:
                if "wav_path" in g and g["wav_path"]:
                    wav_path = Path(g["wav_path"])
                else:
                    # Dump bytes to a temp file
                    with tempfile.NamedTemporaryFile(
                        suffix=".wav", delete=False
                    ) as tmp:
                        tmp.write(g["wav_bytes"])
                        wav_path = Path(tmp.name)
                m = compute_audio_metrics(wav_path)
            except Exception:
                m = None

        items.append(TTSItem(id=g["id"], engine=g["engine"], url=g["url"], metrics=m))

    return TTSResponse(items=items)
