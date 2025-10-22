"""
Prometheus instrumentation for VoiceStudio Voice Engine Router
"""

from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram, Gauge, Info
import time

# Custom metrics for voice engine router
TTS_REQUESTS_TOTAL = Counter(
    "voicestudio_tts_requests_total",
    "Total number of TTS requests",
    ["engine", "language", "quality", "status"],
)

TTS_REQUEST_DURATION = Histogram(
    "voicestudio_tts_request_duration_seconds",
    "Duration of TTS requests",
    ["engine", "language", "quality"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

ENGINE_LOAD = Gauge(
    "voicestudio_engine_load_ratio", "Current load ratio of voice engines", ["engine"]
)

ENGINE_HEALTH = Gauge(
    "voicestudio_engine_health",
    "Health status of voice engines (1=healthy, 0=unhealthy)",
    ["engine"],
)

AUDIO_METRICS_LUFS = Histogram(
    "voicestudio_audio_lufs",
    "Audio LUFS measurements",
    ["engine"],
    buckets=[-30, -25, -23, -20, -18, -16, -14, -12, -10],
)

AUDIO_METRICS_CLIP_PCT = Histogram(
    "voicestudio_audio_clip_percentage",
    "Audio clipping percentage",
    ["engine"],
    buckets=[0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0],
)

VOICESTUDIO_INFO = Info("voicestudio_info", "VoiceStudio system information")


def setup_prometheus_instrumentation(app):
    """Setup Prometheus instrumentation for FastAPI app"""

    # Set system info
    VOICESTUDIO_INFO.info(
        {
            "version": "1.0.0",
            "component": "voice_engine_router",
            "description": "VoiceStudio Voice Engine Router with multi-engine support",
        }
    )

    # Create instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/docs", "/openapi.json"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="voicestudio_requests_inprogress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.add(metrics.default())

    # Instrument the app
    instrumentator.instrument(app)
    instrumentator.expose(app)

    return instrumentator


def record_engine_metrics(engine_id: str, load: float, healthy: bool):
    """Record engine-specific metrics"""
    ENGINE_LOAD.labels(engine=engine_id).set(load)
    ENGINE_HEALTH.labels(engine=engine_id).set(1 if healthy else 0)


def record_audio_metrics(engine_id: str, metrics_data: dict):
    """Record audio quality metrics"""
    if metrics_data.get("lufs") is not None:
        AUDIO_METRICS_LUFS.labels(engine=engine_id).observe(metrics_data["lufs"])

    if metrics_data.get("clip_pct") is not None:
        AUDIO_METRICS_CLIP_PCT.labels(engine=engine_id).observe(
            metrics_data["clip_pct"]
        )


def record_tts_duration(engine_id: str, language: str, quality: str, duration: float):
    """Record TTS request duration"""
    TTS_REQUEST_DURATION.labels(
        engine=engine_id, language=language, quality=quality
    ).observe(duration)


def setup_prometheus(app):
    """Setup Prometheus instrumentation for FastAPI app"""
    return setup_prometheus_instrumentation(app)
