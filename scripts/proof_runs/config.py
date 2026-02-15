"""
Sentinel Configuration Module

Provides configuration management for the sentinel workflow runner
with environment variable overrides following VoiceStudio patterns.

Environment Variables:
    SENTINEL_API_BASE: API base URL (default: http://127.0.0.1:8000)
    SENTINEL_HEALTH_TIMEOUT: Health check timeout in seconds (default: 5.0)
    SENTINEL_UPLOAD_TIMEOUT: File upload timeout in seconds (default: 30.0)
    SENTINEL_SYNTH_TIMEOUT: Synthesis timeout in seconds (default: 120.0)
    SENTINEL_POLL_TIMEOUT: Job polling timeout in seconds (default: 180.0)
    SENTINEL_POLL_INTERVAL: Job polling interval in seconds (default: 2.0)
    SENTINEL_RETRY_COUNT: Maximum retry attempts (default: 3)
    SENTINEL_RETRY_DELAY: Initial retry delay in seconds (default: 1.0)
    SENTINEL_CIRCUIT_BREAKER_ENABLED: Enable circuit breaker (default: true)
    SENTINEL_CB_FAILURE_THRESHOLD: Failures before opening (default: 5)
    SENTINEL_CB_RECOVERY_TIMEOUT: Recovery timeout in seconds (default: 30.0)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


def _get_env_str(key: str, default: str) -> str:
    """Get string environment variable with default."""
    return os.environ.get(key, default)


def _get_env_int(key: str, default: int) -> int:
    """Get integer environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


@dataclass
class TimeoutConfig:
    """Timeout configuration for sentinel workflow steps."""
    health: float = 5.0
    upload: float = 30.0
    sync_synth: float = 120.0
    async_synth: float = 30.0
    poll_job: float = 180.0
    ab_test: float = 180.0
    eval: float = 60.0

    @classmethod
    def from_env(cls) -> TimeoutConfig:
        """Create configuration from environment variables."""
        return cls(
            health=_get_env_float("SENTINEL_HEALTH_TIMEOUT", 5.0),
            upload=_get_env_float("SENTINEL_UPLOAD_TIMEOUT", 30.0),
            sync_synth=_get_env_float("SENTINEL_SYNTH_TIMEOUT", 120.0),
            async_synth=_get_env_float("SENTINEL_ASYNC_SYNTH_TIMEOUT", 30.0),
            poll_job=_get_env_float("SENTINEL_POLL_TIMEOUT", 180.0),
            ab_test=_get_env_float("SENTINEL_AB_TEST_TIMEOUT", 180.0),
            eval=_get_env_float("SENTINEL_EVAL_TIMEOUT", 60.0),
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary keyed by step name."""
        return {
            "health": self.health,
            "upload": self.upload,
            "sync_synth": self.sync_synth,
            "async_synth": self.async_synth,
            "poll_job": self.poll_job,
            "ab_test": self.ab_test,
            "eval": self.eval,
        }


@dataclass
class RetryConfig:
    """Retry configuration for HTTP requests."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 10.0
    jitter_factor: float = 0.2

    @classmethod
    def from_env(cls) -> RetryConfig:
        """Create configuration from environment variables."""
        return cls(
            max_retries=_get_env_int("SENTINEL_RETRY_COUNT", 3),
            initial_delay=_get_env_float("SENTINEL_RETRY_DELAY", 1.0),
            max_delay=_get_env_float("SENTINEL_RETRY_MAX_DELAY", 10.0),
            jitter_factor=_get_env_float("SENTINEL_RETRY_JITTER", 0.2),
        )


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    enabled: bool = True
    failure_threshold: int = 5
    success_threshold: int = 2
    recovery_timeout: float = 30.0

    @classmethod
    def from_env(cls) -> CircuitBreakerConfig:
        """Create configuration from environment variables."""
        return cls(
            enabled=_get_env_bool("SENTINEL_CIRCUIT_BREAKER_ENABLED", True),
            failure_threshold=_get_env_int("SENTINEL_CB_FAILURE_THRESHOLD", 5),
            success_threshold=_get_env_int("SENTINEL_CB_SUCCESS_THRESHOLD", 2),
            recovery_timeout=_get_env_float("SENTINEL_CB_RECOVERY_TIMEOUT", 30.0),
        )


@dataclass
class SentinelConfig:
    """
    Complete configuration for the sentinel workflow runner.

    Usage:
        # Get default configuration with env overrides
        config = get_sentinel_config()

        # Create runner with config
        runner = SentinelRunner(
            api_base=config.api_base,
            fixture_path=config.fixture_path,
            ...
        )
    """
    # API settings
    api_base: str = "http://127.0.0.1:8000"

    # Paths
    fixture_path: Path = field(default_factory=lambda: Path("fixtures/audio/sentinel_16k_mono.wav"))
    artifacts_dir: Path = field(default_factory=lambda: Path("artifacts/sentinel_runs"))
    contracts_dir: Path = field(default_factory=lambda: Path("tests/sentinel/contracts"))

    # Nested configurations
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)

    # Polling settings
    poll_interval: float = 2.0

    # Logging
    verbose: bool = False
    json_logging: bool = False

    @classmethod
    def from_env(cls) -> SentinelConfig:
        """Create configuration from environment variables."""
        return cls(
            api_base=_get_env_str("SENTINEL_API_BASE",
                                  _get_env_str("VOICESTUDIO_API_BASE", "http://127.0.0.1:8000")),
            fixture_path=Path(_get_env_str("SENTINEL_FIXTURE_PATH", "fixtures/audio/sentinel_16k_mono.wav")),
            artifacts_dir=Path(_get_env_str("SENTINEL_ARTIFACTS_DIR", "artifacts/sentinel_runs")),
            contracts_dir=Path(_get_env_str("SENTINEL_CONTRACTS_DIR", "tests/sentinel/contracts")),
            timeouts=TimeoutConfig.from_env(),
            retry=RetryConfig.from_env(),
            circuit_breaker=CircuitBreakerConfig.from_env(),
            poll_interval=_get_env_float("SENTINEL_POLL_INTERVAL", 2.0),
            verbose=_get_env_bool("SENTINEL_VERBOSE", False),
            json_logging=_get_env_bool("SENTINEL_JSON_LOGGING",
                                       _get_env_bool("VOICESTUDIO_JSON_LOGGING", False)),
        )


@lru_cache(maxsize=1)
def get_sentinel_config() -> SentinelConfig:
    """
    Get the singleton sentinel configuration.

    Configuration is loaded once from environment variables and cached.

    Returns:
        SentinelConfig instance with environment variable overrides.
    """
    return SentinelConfig.from_env()


def reset_config_cache() -> None:
    """
    Reset the configuration cache.

    Useful for testing when environment variables change.
    """
    get_sentinel_config.cache_clear()
