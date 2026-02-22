"""
Application configuration module for VoiceStudio.

Centralizes configuration for ports, URLs, timeouts, and other app settings.
Follows local-first principle with environment variable overrides.

Environment Variables:
    VOICESTUDIO_API_HOST: API host (default: localhost)
    VOICESTUDIO_API_PORT: API port (default: 8000)
    VOICESTUDIO_WS_PORT: WebSocket port (default: 8001)
    VOICESTUDIO_HEALTH_CHECK_INTERVAL: Health check interval in ms (default: 5000)
    VOICESTUDIO_RECONNECT_DELAY: Reconnect delay in ms (default: 3000)
    VOICESTUDIO_REQUEST_TIMEOUT: Request timeout in ms (default: 30000)
    VOICESTUDIO_DEBUG: Enable debug mode (default: false)

Examples:
    >>> get_api_host()
    'localhost'

    >>> get_api_url()
    'http://localhost:8000'

    >>> get_timeout("request")
    30.0
"""

from __future__ import annotations

import os
from typing import Any


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


# =============================================================================
# API Configuration
# =============================================================================


def get_api_host() -> str:
    """
    Get the API host address.

    Returns:
        API host (default: localhost)
    """
    return os.getenv("VOICESTUDIO_API_HOST", "localhost")


def get_api_port() -> int:
    """
    Get the API port.

    Returns:
        API port (default: 8000)
    """
    return _get_env_int("VOICESTUDIO_API_PORT", 8000)


def get_websocket_port() -> int:
    """
    Get the WebSocket port.

    Returns:
        WebSocket port (default: 8001)
    """
    return _get_env_int("VOICESTUDIO_WS_PORT", 8001)


def get_api_url() -> str:
    """
    Get the full API base URL.

    Returns:
        API URL (e.g., http://localhost:8000)
    """
    return f"http://{get_api_host()}:{get_api_port()}"


def get_websocket_url() -> str:
    """
    Get the WebSocket URL.

    Returns:
        WebSocket URL (e.g., ws://localhost:8001)
    """
    return f"ws://{get_api_host()}:{get_websocket_port()}"


# =============================================================================
# Timing Configuration
# =============================================================================


def get_health_check_interval_ms() -> int:
    """
    Get health check interval in milliseconds.

    Returns:
        Health check interval (default: 5000ms)
    """
    return _get_env_int("VOICESTUDIO_HEALTH_CHECK_INTERVAL", 5000)


def get_reconnect_delay_ms() -> int:
    """
    Get reconnect delay in milliseconds.

    Returns:
        Reconnect delay (default: 3000ms)
    """
    return _get_env_int("VOICESTUDIO_RECONNECT_DELAY", 3000)


def get_request_timeout_ms() -> int:
    """
    Get request timeout in milliseconds.

    Returns:
        Request timeout (default: 30000ms)
    """
    return _get_env_int("VOICESTUDIO_REQUEST_TIMEOUT", 30000)


def get_timeout(timeout_type: str) -> float:
    """
    Get timeout value in seconds.

    Args:
        timeout_type: Type of timeout (request, connect, read, synthesis, transcription)

    Returns:
        Timeout in seconds
    """
    timeouts = {
        "request": _get_env_float("VOICESTUDIO_REQUEST_TIMEOUT_SEC", 30.0),
        "connect": _get_env_float("VOICESTUDIO_CONNECT_TIMEOUT_SEC", 10.0),
        "read": _get_env_float("VOICESTUDIO_READ_TIMEOUT_SEC", 60.0),
        "synthesis": _get_env_float("VOICESTUDIO_SYNTHESIS_TIMEOUT_SEC", 120.0),
        "transcription": _get_env_float("VOICESTUDIO_TRANSCRIPTION_TIMEOUT_SEC", 300.0),
    }
    return timeouts.get(timeout_type.lower(), 30.0)


# =============================================================================
# Retry Configuration
# =============================================================================


def get_max_retries() -> int:
    """
    Get maximum retry count for operations.

    Returns:
        Max retries (default: 3)
    """
    return _get_env_int("VOICESTUDIO_MAX_RETRIES", 3)


def get_retry_delay_ms() -> int:
    """
    Get delay between retries in milliseconds.

    Returns:
        Retry delay (default: 1000ms)
    """
    return _get_env_int("VOICESTUDIO_RETRY_DELAY", 1000)


# =============================================================================
# Buffer and Size Configuration
# =============================================================================


def get_buffer_size() -> int:
    """
    Get default buffer size in bytes.

    Returns:
        Buffer size (default: 4096)
    """
    return _get_env_int("VOICESTUDIO_BUFFER_SIZE", 4096)


def get_chunk_size() -> int:
    """
    Get audio chunk size in samples.

    Returns:
        Chunk size (default: 4000)
    """
    return _get_env_int("VOICESTUDIO_CHUNK_SIZE", 4000)


def get_max_file_size_mb() -> int:
    """
    Get maximum file size in megabytes.

    Returns:
        Max file size (default: 100MB)
    """
    return _get_env_int("VOICESTUDIO_MAX_FILE_SIZE_MB", 100)


def get_max_backup_size_mb() -> int:
    """
    Get maximum backup size in megabytes.

    Returns:
        Max backup size (default: 500MB)
    """
    return _get_env_int("VOICESTUDIO_MAX_BACKUP_SIZE_MB", 500)


# =============================================================================
# Debug and Feature Flags
# =============================================================================


def is_debug_mode() -> bool:
    """
    Check if debug mode is enabled.

    Returns:
        True if debug mode is enabled
    """
    return _get_env_bool("VOICESTUDIO_DEBUG", False)


def is_telemetry_enabled() -> bool:
    """
    Check if telemetry is enabled (opt-in only).

    Returns:
        True if telemetry is enabled
    """
    return _get_env_bool("VOICESTUDIO_TELEMETRY_ENABLED", False)


# =============================================================================
# All Configuration (for export/debugging)
# =============================================================================


def get_all_config() -> dict[str, Any]:
    """
    Get all configuration values.

    Returns:
        Dictionary of all configuration values
    """
    return {
        "api": {
            "host": get_api_host(),
            "port": get_api_port(),
            "websocket_port": get_websocket_port(),
            "url": get_api_url(),
            "websocket_url": get_websocket_url(),
        },
        "timing": {
            "health_check_interval_ms": get_health_check_interval_ms(),
            "reconnect_delay_ms": get_reconnect_delay_ms(),
            "request_timeout_ms": get_request_timeout_ms(),
            "timeouts": {
                "request": get_timeout("request"),
                "connect": get_timeout("connect"),
                "read": get_timeout("read"),
                "synthesis": get_timeout("synthesis"),
                "transcription": get_timeout("transcription"),
            },
        },
        "retry": {
            "max_retries": get_max_retries(),
            "retry_delay_ms": get_retry_delay_ms(),
        },
        "buffers": {
            "buffer_size": get_buffer_size(),
            "chunk_size": get_chunk_size(),
            "max_file_size_mb": get_max_file_size_mb(),
            "max_backup_size_mb": get_max_backup_size_mb(),
        },
        "flags": {
            "debug": is_debug_mode(),
            "telemetry": is_telemetry_enabled(),
        },
    }
