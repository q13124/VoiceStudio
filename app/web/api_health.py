from fastapi import APIRouter
from fastapi import FastAPI
from app.core.models.health import (
    HealthMetrics,
    HealthFFmpeg,
    HealthPostFx,
    HealthBuild,
)
from app.core.health.ffmpeg import ffmpeg_info, ffprobe_info
from services.settings import settings

router = APIRouter()


@router.get("/v1/health/metrics", response_model=HealthMetrics)
def health_metrics() -> HealthMetrics:
    fm = ffmpeg_info(getattr(settings, "ffmpeg_path", None))
    fp = ffprobe_info(getattr(settings, "ffprobe_path", None))

    postfx = HealthPostFx(
        available=fm.present,
        ffmpeg_used_by_default=False,  # we only use post-FX if user sets output_chain
    )

    build = HealthBuild(
        version=None,  # Could be set from environment or build info
        git_sha=None,
        build_time_utc=None,
    )

    return HealthMetrics(
        metrics_enabled=getattr(settings, "metrics_enabled", False),
        ffmpeg=HealthFFmpeg(present=fm.present, version=fm.version),
        ffprobe=HealthFFmpeg(present=fp.present, version=fp.version),
        postfx=postfx,
        openapi_version="3.1.0",
        build=build,
    )
