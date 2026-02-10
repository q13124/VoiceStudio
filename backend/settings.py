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

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List, Optional


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


def _get_env_list(key: str, default: List[str], separator: str = ",") -> List[str]:
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
            "VOICESTUDIO_DB_PATH", "data/voicestudio.db"
        )
    )
    connection_timeout: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_DB_TIMEOUT", 30.0
        )
    )
    max_connections: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_DB_MAX_CONNECTIONS", 10
        )
    )


@dataclass(frozen=True)
class ServerConfig:
    """Server configuration."""
    
    host: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_HOST", "localhost"
        )
    )
    port: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_PORT", 8000
        )
    )
    api_prefix: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_API_PREFIX", "/api"
        )
    )
    cors_origins: List[str] = field(
        default_factory=lambda: _get_env_list(
            "VOICESTUDIO_CORS_ORIGINS",
            ["http://localhost:3000", "http://localhost:8000"]
        )
    )
    debug: bool = field(
        default_factory=lambda: _get_env_bool(
            "VOICESTUDIO_DEBUG", False
        )
    )
    
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
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_SHUTDOWN_TIMEOUT", 30.0
        )
    )
    engine_stop: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_ENGINE_STOP_TIMEOUT", 10.0
        )
    )
    engine_recovery: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_ENGINE_RECOVERY_TIMEOUT", 60.0
        )
    )
    health_check: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_HEALTH_CHECK_TIMEOUT", 5.0
        )
    )
    lifecycle_orchestrator: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_LIFECYCLE_TIMEOUT", 5.0
        )
    )
    gpu_status: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_GPU_STATUS_TIMEOUT", 5.0
        )
    )
    database_check: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_DB_CHECK_TIMEOUT", 3.0
        )
    )
    disk_check: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_DISK_CHECK_TIMEOUT", 2.0
        )
    )
    memory_check: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_MEMORY_CHECK_TIMEOUT", 2.0
        )
    )
    engine_check: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_ENGINE_CHECK_TIMEOUT", 10.0
        )
    )
    dependency_scan: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_DEPENDENCY_SCAN_TIMEOUT", 120.0
        )
    )


@dataclass(frozen=True)
class AudioConfig:
    """Audio processing configuration."""
    
    default_sample_rate: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_SAMPLE_RATE", 22050
        )
    )
    high_quality_sample_rate: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_HQ_SAMPLE_RATE", 44100
        )
    )
    internal_sample_rate: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_INTERNAL_SAMPLE_RATE", 16000
        )
    )
    default_channels: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_AUDIO_CHANNELS", 1
        )
    )
    default_bit_depth: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_BIT_DEPTH", 16
        )
    )


@dataclass(frozen=True)
class StorageConfig:
    """Storage paths configuration."""
    
    data_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_DATA_DIR", "data"
        )
    )
    temp_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_TEMP_DIR", "data/temp"
        )
    )
    cache_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_CACHE_DIR", "data/cache"
        )
    )
    exports_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_EXPORTS_DIR", "data/exports"
        )
    )
    archive_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_ARCHIVE_DIR", "data/archive"
        )
    )
    models_dir: str = field(
        default_factory=lambda: _get_env_str(
            "VOICESTUDIO_MODELS_DIR", "models"
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
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_ENGINE_BATCH_SIZE", 1
        )
    )
    max_concurrent_engines: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_MAX_ENGINES", 3
        )
    )
    gpu_memory_fraction: float = field(
        default_factory=lambda: _get_env_float(
            "VOICESTUDIO_GPU_MEMORY_FRACTION", 0.9
        )
    )
    enable_gpu: bool = field(
        default_factory=lambda: _get_env_bool(
            "VOICESTUDIO_ENABLE_GPU", True
        )
    )
    lazy_load_models: bool = field(
        default_factory=lambda: _get_env_bool(
            "VOICESTUDIO_LAZY_LOAD_MODELS", True
        )
    )


@dataclass(frozen=True)
class SecurityConfig:
    """Security configuration."""
    
    require_auth: bool = field(
        default_factory=lambda: _get_env_bool(
            "VOICESTUDIO_REQUIRE_AUTH", False
        )
    )
    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("VOICESTUDIO_API_KEY")
    )
    rate_limit_requests: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_RATE_LIMIT", 100
        )
    )
    rate_limit_window: int = field(
        default_factory=lambda: _get_env_int(
            "VOICESTUDIO_RATE_LIMIT_WINDOW", 60
        )
    )


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
    "Config",
    "DatabaseConfig",
    "ServerConfig",
    "TimeoutConfig",
    "AudioConfig",
    "StorageConfig",
    "EngineConfig",
    "SecurityConfig",
    "config",
    "get_config",
]
