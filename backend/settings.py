"""
VoiceStudio Backend Settings

Centralizes all configuration values with environment variable overrides.
This module provides a single source of truth for configuration across the backend.

Usage:
    from backend.settings import config

    # Access configuration
    db_path = config.database.sqlite_path
    timeout = config.timeouts.shutdown

    # Or import specific configs
    from backend.settings import DatabaseConfig, ServerConfig
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


def _detect_portable_mode() -> bool:
    """
    Detect portable mode: if a 'portable.flag' file exists next to the
    running script (or in the repo/install root), all data paths resolve
    relative to that root instead of %AppData%/%ProgramData%.
    """
    # Check multiple candidate locations (installed vs dev)
    candidates = [
        Path(__file__).resolve().parent.parent / "portable.flag",  # repo root
        Path(__file__).resolve().parent / "portable.flag",  # backend/
        Path(os.getcwd()) / "portable.flag",  # cwd
    ]
    return any(c.exists() for c in candidates)


_PORTABLE_MODE = _detect_portable_mode()


def _portable_root() -> Path:
    """Return the portable data root (repo/install root)."""
    return Path(__file__).resolve().parent.parent


def _get_env_str(key: str, default: str) -> str:
    """Get string from environment variable."""
    return os.getenv(key, default)


def _get_env_int(key: str, default: int) -> int:
    """Get integer from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _get_env_list(key: str, default: list[str], separator: str = ",") -> list[str]:
    """Get list from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration."""

    sqlite_path: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_DB_PATH",
            (
                str(_portable_root() / "data" / "voicestudio.db")
                if _PORTABLE_MODE
                else "data/voicestudio.db"
            ),
        )
    )
    connection_timeout: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_DB_TIMEOUT", 30.0)
    )
    max_connections: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_DB_MAX_CONNECTIONS", 10)
    )


@dataclass(frozen=True)
class ServerConfig:
    """Server configuration."""

    host: str = field(default_factory=lambda: _get_env_str("VOICESTUDIO_HOST", "localhost"))
    port: int = field(default_factory=lambda: _get_env_int("VOICESTUDIO_PORT", 8000))
    api_prefix: str = field(default_factory=lambda: _get_env_str("VOICESTUDIO_API_PREFIX", "/api"))
    cors_origins: list[str] = field(
        default_factory=lambda: _get_env_list(
            "VOICESTUDIO_CORS_ORIGINS", ["http://localhost:3000", "http://localhost:8000"]
        )
    )
    debug: bool = field(default_factory=lambda: _get_env_bool("VOICESTUDIO_DEBUG", False))

    @property
    def base_url(self) -> str:
        """Get the base URL for the server."""
        return f"http://{self.host}:{self.port}"

    @property
    def api_url(self) -> str:
        """Get the full API URL."""
        return f"{self.base_url}{self.api_prefix}"


@dataclass(frozen=True)
class TimeoutConfig:
    """Timeout configuration values."""

    shutdown: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_SHUTDOWN_TIMEOUT", 30.0)
    )
    engine_stop: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_ENGINE_STOP_TIMEOUT", 10.0)
    )
    engine_recovery: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_ENGINE_RECOVERY_TIMEOUT", 60.0)
    )
    health_check: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_HEALTH_CHECK_TIMEOUT", 5.0)
    )
    lifecycle_orchestrator: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_LIFECYCLE_TIMEOUT", 5.0)
    )
    gpu_status: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_GPU_STATUS_TIMEOUT", 5.0)
    )
    database_check: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_DB_CHECK_TIMEOUT", 3.0)
    )
    disk_check: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_DISK_CHECK_TIMEOUT", 2.0)
    )
    memory_check: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_MEMORY_CHECK_TIMEOUT", 2.0)
    )
    engine_check: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_ENGINE_CHECK_TIMEOUT", 10.0)
    )
    dependency_scan: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_DEPENDENCY_SCAN_TIMEOUT", 120.0)
    )


@dataclass(frozen=True)
class AudioConfig:
    """Audio processing configuration."""

    default_sample_rate: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_SAMPLE_RATE", 22050)
    )
    high_quality_sample_rate: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_HQ_SAMPLE_RATE", 44100)
    )
    internal_sample_rate: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_INTERNAL_SAMPLE_RATE", 16000)
    )
    default_channels: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_AUDIO_CHANNELS", 1)
    )
    default_bit_depth: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_BIT_DEPTH", 16)
    )


@dataclass(frozen=True)
class StorageConfig:
    """Storage paths configuration."""

    data_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_DATA_DIR",
            str(_portable_root() / "data") if _PORTABLE_MODE else "data",
        )
    )
    temp_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_TEMP_DIR",
            str(_portable_root() / "data" / "temp") if _PORTABLE_MODE else "data/temp",
        )
    )
    cache_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_CACHE_DIR",
            str(_portable_root() / "data" / "cache") if _PORTABLE_MODE else "data/cache",
        )
    )
    exports_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_EXPORTS_DIR",
            str(_portable_root() / "data" / "exports") if _PORTABLE_MODE else "data/exports",
        )
    )
    archive_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_ARCHIVE_DIR",
            str(_portable_root() / "data" / "archive") if _PORTABLE_MODE else "data/archive",
        )
    )
    models_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_MODELS_DIR",
            str(_portable_root() / "models") if _PORTABLE_MODE else "models",
        )
    )

    def ensure_directories(self) -> None:
        """Ensure all storage directories exist."""
        for path_str in [
            self.data_dir,
            self.temp_dir,
            self.cache_dir,
            self.exports_dir,
            self.archive_dir,
            self.models_dir,
        ]:
            Path(path_str).mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class EngineConfig:
    """Engine configuration."""

    default_batch_size: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_ENGINE_BATCH_SIZE", 1)
    )
    max_concurrent_engines: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_MAX_ENGINES", 3)
    )
    gpu_memory_fraction: float = field(
        default_factory=lambda: _get_env_float("VOICESTUDIO_GPU_MEMORY_FRACTION", 0.9)
    )
    enable_gpu: bool = field(default_factory=lambda: _get_env_bool("VOICESTUDIO_ENABLE_GPU", True))
    lazy_load_models: bool = field(
        default_factory=lambda: _get_env_bool("VOICESTUDIO_LAZY_LOAD_MODELS", True)
    )


@dataclass(frozen=True)
class SecurityConfig:
    """Security configuration."""

    require_auth: bool = field(
        default_factory=lambda: _get_env_bool("VOICESTUDIO_REQUIRE_AUTH", False)
    )
    api_key: str | None = field(default_factory=lambda: os.getenv("VOICESTUDIO_API_KEY"))
    rate_limit_requests: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_RATE_LIMIT", 100)
    )
    rate_limit_window: int = field(
        default_factory=lambda: _get_env_int("VOICESTUDIO_RATE_LIMIT_WINDOW", 60)
    )


@dataclass(frozen=True)
class HealthConfig:
    """Health check configuration (Phase 2A migration)."""

    enable_torch_check: bool = field(
        default_factory=lambda: _get_env_bool("VOICESTUDIO_HEALTH_ENABLE_TORCH", False)
    )
    safe_mode: bool = field(
        default_factory=lambda: _get_env_bool("VOICESTUDIO_HEALTH_SAFE_MODE", True)
    )


@dataclass(frozen=True)
class HuggingFaceConfig:
    """Hugging Face endpoint configuration (Phase 2A migration)."""

    endpoint: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_HF_ENDPOINT", "https://router.huggingface.co"
        )
    )
    inference_api_base: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_HF_INFERENCE_API_BASE",
            _get_env_str("VOICESTUDIO_HF_ENDPOINT", "https://router.huggingface.co"),
        )
    )


@dataclass(frozen=True)
class CorsConfig:
    """CORS configuration (Phase 2A migration)."""

    allowed_origins: str | None = field(default_factory=lambda: os.getenv("CORS_ALLOWED_ORIGINS"))
    environment: str = field(default_factory=lambda: _get_env_str("VOICESTUDIO_ENV", "development"))


@dataclass(frozen=True)
class Config:
    """Main configuration class that aggregates all config sections."""

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    engine: EngineConfig = field(default_factory=EngineConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    huggingface: HuggingFaceConfig = field(default_factory=HuggingFaceConfig)
    cors: CorsConfig = field(default_factory=CorsConfig)
    portable_mode: bool = field(default_factory=lambda: _PORTABLE_MODE)


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Get the application configuration (singleton).

    Returns:
        Config: The application configuration instance
    """
    return Config()


# Convenience access to the singleton config
config = get_config()


# Re-export individual configs for convenience
__all__ = [
    "AudioConfig",
    "Config",
    "CorsConfig",
    "DatabaseConfig",
    "EngineConfig",
    "HealthConfig",
    "HuggingFaceConfig",
    "SecurityConfig",
    "ServerConfig",
    "StorageConfig",
    "TimeoutConfig",
    "config",
    "get_config",
]
