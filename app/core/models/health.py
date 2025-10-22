"""
Health check models for VoiceStudio API
"""

from pydantic import Field
from app.core.models.base import StrictModel


class HealthFFmpeg(StrictModel):
    present: bool
    version: str | None = None


class HealthPostFx(StrictModel):
    available: bool = Field(description="True if ffmpeg detected for post-FX")
    ffmpeg_used_by_default: bool = False


class HealthBuild(StrictModel):
    version: str | None = None
    git_sha: str | None = None
    build_time_utc: str | None = None


class HealthMetrics(StrictModel):
    metrics_enabled: bool
    ffmpeg: HealthFFmpeg
    ffprobe: HealthFFmpeg
    postfx: HealthPostFx
    openapi_version: str
    build: HealthBuild | None = None