"""
VoiceStudio — Voice Engine Router Service

Purpose
-------
Unifies multiple TTS/VC engines behind one smart FastAPI service that:
- Selects the best engine for a job (language, quality, load, history)
- Provides a deterministic fallback chain
- Exposes a single /tts endpoint (sync or async job mode)
- Surfaces health/metrics and A/B testing hooks

Design Notes
------------
- Engine adapters conform to a common Protocol (see EngineProtocol)
- Registry can be backed by the plugin system; a simple in-process registry is provided here
- Quality prediction + historical learning are stubbed but shaped for drop-in models
- Config read from voicestudio.yaml if present, with safe defaults

TODO (follow-ups)
-----------------
- Wire to real plugin registry + hot-reload
- Replace stubs with actual adapters (XTTS, OpenVoice, RVC, Coqui, Tortoise)
- Persist telemetry + quality history in DB (SQLite/PG) via TelemetryService
- Add background job queue and WebSocket progress (or reuse existing runtime queue)
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Protocol, Tuple

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from services.api.ab_summary import (
    ABSummaryRequest,
    ABSummaryResponse,
    aggregate_ab_ratings,
)

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

DEFAULT_PORT = int(os.getenv("VOICE_ROUTER_PORT", "5090"))
DEFAULT_HOST = os.getenv("VOICE_ROUTER_HOST", "127.0.0.1")


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore", validate_default=True, frozen=False)

    # Audio metrics settings
    metrics_enabled: bool = Field(
        default=False,
        description="Enable server-side audio metrics (LUFS, clip%, DC, silence, etc.)",
    )
    metrics_timeout_sec: int = Field(default=20, ge=1, le=120)
    metrics_ffmpeg_path: Optional[str] = Field(
        default=None, description="Optional explicit ffmpeg path"
    )
    metrics_ffprobe_path: Optional[str] = Field(
        default=None, description="Optional explicit ffprobe path"
    )

    class Config:
        env_prefix = ""  # e.g., METRICS_ENABLED=true
        case_sensitive = False


settings = Settings()


@dataclass
class RouterConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    models_dir: Path = Path(
        os.getenv("ULTRACLONE_MODELS", r"C:\ProgramData\UltraClone\models")
    )
    cache_dir: Path = Path(
        os.getenv("ULTRACLONE_CACHE", r"%APPDATA%\UltraClone\cache").replace(
            "%APPDATA%", os.getenv("APPDATA", "")
        )
    )
    quality_preference: Dict[str, int] = None
    fallback_order: List[str] = None

    def __post_init__(self):
        if self.quality_preference is None:
            self.quality_preference = {"quality": 3, "balanced": 2, "fast": 1}
        if self.fallback_order is None:
            self.fallback_order = ["xtts", "openvoice", "coqui", "tortoise", "rvc"]


def load_config() -> RouterConfig:
    cfg_paths = [
        Path("voicestudio.yaml"),
        Path("config") / "voicestudio.yaml",
        (
            Path(os.getenv("VOICESTUDIO_CONFIG", ""))
            if os.getenv("VOICESTUDIO_CONFIG")
            else None
        ),
    ]
    for p in cfg_paths:
        if p and p.exists() and yaml is not None:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            router = data.get("router", {})
            return RouterConfig(
                host=router.get("host", DEFAULT_HOST),
                port=int(router.get("port", DEFAULT_PORT)),
                models_dir=Path(router.get("models_dir", RouterConfig.models_dir)),
                cache_dir=Path(router.get("cache_dir", RouterConfig.cache_dir)),
                quality_preference=router.get("quality_preference"),
                fallback_order=router.get("fallback_order"),
            )
    return RouterConfig()


CONFIG = load_config()

QualityTier = Literal["fast", "balanced", "quality"]


class EngineProtocol(Protocol):
    id: str
    languages: List[str]
    quality: List[QualityTier]

    def healthy(self) -> bool: ...
    def current_load(self) -> float: ...
    def supports(self, language: str, tier: QualityTier) -> bool: ...
    def tts(self, *, text: str, voice_profile: Dict, params: Dict) -> bytes: ...


class XTTSAdapter:
    id = "xtts"
    languages = ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru", "ar"]
    quality = ["fast", "balanced", "quality"]

    def __init__(self):
        self._load = 0.15

    def healthy(self) -> bool:
        return True

    def current_load(self) -> float:
        return self._load

    def supports(self, language: str, tier: QualityTier) -> bool:
        return language in self.languages and tier in self.quality

    def tts(self, *, text: str, voice_profile: Dict, params: Dict) -> bytes:
        import math, struct

        sr = int(params.get("sample_rate", 22050))
        dur = max(0.2, min(10.0, len(text) / 20.0))
        tone = 440.0
        samples = int(sr * dur)
        buf = bytearray()
        for n in range(samples):
            buf += struct.pack(
                "<h", int(32767 * 0.1 * math.sin(2 * math.pi * tone * (n / sr)))
            )
        return _pcm16_to_wav(bytes(buf), sr)


class OpenVoiceAdapter(XTTSAdapter):
    id = "openvoice"
    languages = ["en", "es", "fr", "de", "it", "pt"]

    def __init__(self):
        super().__init__()
        self._load = 0.25


class CoquiAdapter(XTTSAdapter):
    id = "coqui"
    languages = ["en", "es", "fr", "de"]

    def __init__(self):
        super().__init__()
        self._load = 0.35


class TortoiseAdapter(XTTSAdapter):
    id = "tortoise"
    languages = ["en"]

    def __init__(self):
        super().__init__()
        self._load = 0.6


class RVCAdapter(XTTSAdapter):
    id = "rvc"
    languages = ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"]

    def __init__(self):
        super().__init__()
        self._load = 0.4


def _pcm16_to_wav(pcm: bytes, sample_rate: int) -> bytes:
    import io, struct

    byte_rate = sample_rate * 2
    block_align = 2
    riff = io.BytesIO()
    riff.write(b"RIFF")
    riff.write(struct.pack("<I", 36 + len(pcm)))
    riff.write(b"WAVEfmt ")
    riff.write(
        struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, byte_rate, block_align, 16)
    )
    riff.write(b"data")
    riff.write(struct.pack("<I", len(pcm)))
    riff.write(pcm)
    return riff.getvalue()


class EngineRegistry:
    def __init__(self, adapters: Optional[List[EngineProtocol]] = None):
        self._adapters: Dict[str, EngineProtocol] = {}
        for a in adapters or [
            XTTSAdapter(),
            OpenVoiceAdapter(),
            CoquiAdapter(),
            TortoiseAdapter(),
            RVCAdapter(),
        ]:
            self._adapters[a.id] = a

    def list(self) -> List[str]:
        return list(self._adapters.keys())

    def get(self, engine_id: str) -> EngineProtocol:
        if engine_id not in self._adapters:
            raise KeyError(engine_id)
        return self._adapters[engine_id]

    def discover(self) -> Dict[str, Dict]:
        return {
            k: {
                "healthy": v.healthy(),
                "load": v.current_load(),
                "languages": v.languages,
                "quality": v.quality,
            }
            for k, v in self._adapters.items()
        }


REGISTRY = EngineRegistry()


class QualityPredictor:
    def estimate(
        self, engine_id: str, *, text: str, language: str, tier: QualityTier
    ) -> float:
        base = 0.7
        if engine_id == "xtts":
            base += 0.1 if language != "en" else 0.05
        if engine_id == "tortoise" and tier == "quality" and language == "en":
            base += 0.15
        if engine_id == "rvc" and tier == "quality":
            base += 0.12
        return min(1.0, base)


class Telemetry:
    def record_job(
        self,
        *,
        engine_id: str,
        latency_ms: int,
        ok: bool,
        score: Optional[float] = None,
    ) -> None:
        # TODO: Implement telemetry recording to database
        pass


PREDICTOR = QualityPredictor()
TELEM = Telemetry()


class VoiceEngineRouter:
    def __init__(self, registry: EngineRegistry, cfg: RouterConfig):
        self.r = registry
        self.cfg = cfg

    def fallback_chain(self) -> List[str]:
        return list(self.cfg.fallback_order)

    def select_engine(
        self, *, text: str, language: str, tier: QualityTier
    ) -> Tuple[str, List[str]]:
        candidates: List[EngineProtocol] = []
        for engine_id in self.r.list():
            e = self.r.get(engine_id)
            if e.healthy() and e.supports(language, tier):
                candidates.append(e)

        if not candidates:
            for eid in self.fallback_chain():
                if self.r.get(eid).healthy():
                    return eid, [eid]
            raise HTTPException(status_code=503, detail="No healthy engines available")

        scored: List[Tuple[float, EngineProtocol]] = []
        tier_w = self.cfg.quality_preference.get(tier, 1)
        for e in candidates:
            q = PREDICTOR.estimate(e.id, text=text, language=language, tier=tier)
            load_bonus = 1.0 - min(1.0, max(0.0, e.current_load()))
            score = (q * 0.6) + (load_bonus * 0.3) + (tier_w * 0.1)
            scored.append((score, e))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]
        return best.id, [e.id for _, e in scored]

    def generate(
        self, *, engine_id: str, text: str, voice_profile: Dict, params: Dict
    ) -> bytes:
        return self.r.get(engine_id).tts(
            text=text, voice_profile=voice_profile, params=params
        )


ROUTER = VoiceEngineRouter(REGISTRY, CONFIG)


class TTSRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    text: str = Field(..., min_length=1)
    language: str = Field("en")
    quality: QualityTier = Field("balanced")
    voice_profile: Dict = Field(default_factory=dict)
    params: Dict = Field(default_factory=dict)
    mode: Literal["sync", "async"] = Field("sync")

    @validator("language")
    def lang_lower(cls, v: str) -> str:
        return v.lower()


class AudioMetrics(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    lufs: float | None = Field(default=None, description="Integrated loudness (I, dB)")
    lra: float | None = Field(default=None, description="Loudness range (dB)")
    true_peak: float | None = Field(default=None, description="True peak (dBTP)")
    clip_pct: float | None = Field(
        default=None, ge=0.0, le=100.0, description="% clipped (approx/derived)"
    )
    dc_offset: float | None = Field(default=None, ge=0.0, description="DC offset %FS")
    head_ms: int | None = Field(default=None, ge=0, description="Head silence (ms)")
    tail_ms: int | None = Field(default=None, ge=0, description="Tail silence (ms)")


class MetricsThresholds(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    lufs: Dict[str, float] = Field(
        default_factory=lambda: {"target": -23.0, "warnDelta": 3.0}
    )
    clip_pct: Dict[str, float] = Field(
        default_factory=lambda: {"warn": 0.1, "fail": 1.0}
    )
    dc_offset: Dict[str, float] = Field(
        default_factory=lambda: {"warn": 0.5, "fail": 1.0}
    )
    head_ms: Dict[str, float] = Field(
        default_factory=lambda: {"warn": 120, "fail": 250}
    )
    tail_ms: Dict[str, float] = Field(
        default_factory=lambda: {"warn": 150, "fail": 300}
    )


# Default thresholds for audio quality assessment
DEFAULT_THRESHOLDS = MetricsThresholds()


class TTSItem(BaseModel):
    id: str
    engine: str
    url: str  # wav url
    metrics: Optional[AudioMetrics] = None  # additive, optional


class TTSResponse(BaseModel):
    items: List[TTSItem]
    engine: str
    tried_order: List[str]
    result_b64_wav: Optional[str] = None
    job_id: Optional[str] = None


app = FastAPI(
    title="VoiceStudio Voice Engine Router", version="1.0.0", openapi_version="3.1.0"
)


@app.get("/health")
def health():
    return {"ok": True, "engines": REGISTRY.discover()}


@app.get("/metrics/thresholds")
def get_metrics_thresholds():
    """Get current audio quality thresholds"""
    return DEFAULT_THRESHOLDS.dict()


@app.post("/metrics/thresholds")
def update_metrics_thresholds(thresholds: MetricsThresholds):
    """Update audio quality thresholds"""
    global DEFAULT_THRESHOLDS
    DEFAULT_THRESHOLDS = thresholds
    return {"message": "Thresholds updated successfully"}


@app.post("/tts", response_model=TTSResponse)
async def tts(req: TTSRequest, bg: BackgroundTasks):
    engine_id, tried = ROUTER.select_engine(
        text=req.text, language=req.language, tier=req.quality
    )

    if req.mode == "async":
        job_id = f"job_{abs(hash(json.dumps(req.dict())))%10_000_000}"

        def _work():
            try:
                ROUTER.generate(
                    engine_id=engine_id,
                    text=req.text,
                    voice_profile=req.voice_profile,
                    params=req.params,
                )
                TELEM.record_job(engine_id=engine_id, latency_ms=0, ok=True)
            except Exception:
                TELEM.record_job(engine_id=engine_id, latency_ms=0, ok=False)

        bg.add_task(_work)
        return TTSResponse(engine=engine_id, tried_order=tried, job_id=job_id)

    audio = ROUTER.generate(
        engine_id=engine_id,
        text=req.text,
        voice_profile=req.voice_profile,
        params=req.params,
    )
    b64 = base64.b64encode(audio).decode("ascii")
    TELEM.record_job(engine_id=engine_id, latency_ms=0, ok=True)
    return TTSResponse(engine=engine_id, tried_order=tried, result_b64_wav=b64)


class ABTestRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    text: str
    language: str = "en"
    quality: QualityTier = "balanced"
    engines: Optional[List[str]] = None


class ABTestResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    candidates: List[str]
    results: Dict[str, str]


@app.post("/abtest", response_model=ABTestResponse)
async def abtest(req: ABTestRequest):
    best, order = ROUTER.select_engine(
        text=req.text, language=req.language, tier=req.quality
    )
    candidates = req.engines or order[:2]
    res: Dict[str, str] = {}
    for eid in candidates:
        try:
            data = ROUTER.generate(
                engine_id=eid, text=req.text, voice_profile={}, params={}
            )
            res[eid] = base64.b64encode(data).decode("ascii")
        except Exception:
            res[eid] = ""
    return ABTestResponse(candidates=candidates, results=res)


@app.post("/v1/ab/summary", response_model=ABSummaryResponse)
async def ab_summary(req: ABSummaryRequest):
    """
    Aggregate A/B test ratings and return per-engine statistics.

    Example payload:
    {
        "ratings": [
            {"item_id": "xtts_1", "score": 4.5, "winner": true},
            {"item_id": "coqui_1", "score": 3.2, "winner": false},
            {"item_id": "xtts_2", "score": 4.8, "winner": true}
        ],
        "test_id": "test_001"
    }
    """
    return aggregate_ab_ratings(req.ratings)


if __name__ == "__main__":
    uvicorn.run(app, host=CONFIG.host, port=CONFIG.port, log_level="info")
