from __future__ import annotations
import os
from pydantic import Field, ConfigDict, BaseModel


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_default=True, frozen=False)

    # Existing settings...
    metrics_enabled: bool = Field(
        default=False,
        description="Enable server-side audio metrics (LUFS, clip%, DC, silence, etc.)",
    )
    metrics_timeout_sec: int = Field(default=20, ge=1, le=120)
    metrics_ffmpeg_path: str | None = Field(
        default=None, description="Optional explicit ffmpeg path"
    )
    metrics_ffprobe_path: str | None = Field(
        default=None, description="Optional explicit ffprobe path"
    )

    # --- Prometheus /metrics (HTTP) ---
    prom_enabled: bool = Field(
        default=False, description="Expose Prometheus /metrics for FastAPI"
    )
    prom_endpoint: str = Field(
        default="/metrics", description="Path for HTTP metrics endpoint"
    )
    prom_instrument_app: bool = Field(
        default=True, description="Instrument requests, latency histograms, etc."
    )
    prom_group_paths: bool = Field(
        default=True, description="Group dynamic path params (e.g., /v1/generate/{id})"
    )
    prom_latency_buckets_ms: str = Field(
        default="5,10,25,50,100,250,500,1000,2500,5000,10000",
        description="Comma-separated histogram buckets in milliseconds",
    )

    # --- GPU telemetry (docs only; exporter runs sidecar/daemonset) ---
    dcgm_exporter_enabled: bool = Field(
        default=False, description="Documented integration only; not used by app"
    )

    # FFmpeg paths for post-processing
    ffmpeg_path: str | None = Field(
        default=None, description="Optional explicit path to ffmpeg"
    )
    ffprobe_path: str | None = Field(
        default=None, description="Optional explicit path to ffprobe"
    )

    # A/B Testing persistence
    ab_persist_enabled: bool = Field(
        default=False, description="Persist /v1/ab/summary results"
    )
    db_url: str | None = Field(
        default=None, description="SQLAlchemy URL (e.g., sqlite:///./app.db or postgresql://user:pass@host/db)"
    )
    db_use_postgres: bool = Field(
        default=False, description="Use PostgreSQL instead of SQLite (auto-detected from DB_URL)"
    )

    # Nightly Evaluation Ingest
    evals_ingest_enabled: bool = Field(
        default=False, description="Enable POST /v1/evals/ingest endpoint"
    )
    evals_ingest_token: str | None = Field(
        default=None, description="Bearer token required for ingest"
    )

    @classmethod
    def from_env(cls):
        """Load settings from environment variables"""
        db_url = os.getenv("DB_URL")
        db_use_postgres = False
        if db_url:
            db_use_postgres = db_url.startswith(("postgresql://", "postgresql+psycopg://"))
        
        return cls(
            metrics_enabled=os.getenv("METRICS_ENABLED", "false").lower() == "true",
            metrics_timeout_sec=int(os.getenv("METRICS_TIMEOUT_SEC", "20")),
            metrics_ffmpeg_path=os.getenv("METRICS_FFMPEG_PATH"),
            metrics_ffprobe_path=os.getenv("METRICS_FFPROBE_PATH"),
            prom_enabled=os.getenv("PROM_ENABLED", "false").lower() == "true",
            prom_endpoint=os.getenv("PROM_ENDPOINT", "/metrics"),
            prom_instrument_app=os.getenv("PROM_INSTRUMENT_APP", "true").lower()
            == "true",
            prom_group_paths=os.getenv("PROM_GROUP_PATHS", "true").lower() == "true",
            prom_latency_buckets_ms=os.getenv(
                "PROM_LATENCY_BUCKETS_MS", "5,10,25,50,100,250,500,1000,2500,5000,10000"
            ),
            dcgm_exporter_enabled=os.getenv("DCGM_EXPORTER_ENABLED", "false").lower()
            == "true",
            ffmpeg_path=os.getenv("FFMPEG_PATH"),
            ffprobe_path=os.getenv("FFPROBE_PATH"),
            ab_persist_enabled=os.getenv("AB_PERSIST_ENABLED", "false").lower()
            == "true",
            db_url=db_url,
            db_use_postgres=db_use_postgres,
            evals_ingest_enabled=os.getenv("EVALS_INGEST_ENABLED", "false").lower()
            == "true",
            evals_ingest_token=os.getenv("EVALS_INGEST_TOKEN"),
        )


def get_settings() -> Settings:
    """Get settings instance, reloading from environment each time"""
    return Settings.from_env()


# For backward compatibility, keep the global instance
settings = get_settings()
