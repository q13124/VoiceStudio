"""
Pytest configuration and fixtures for sentinel workflow tests.

This module provides fixtures for:
- Backend server startup/shutdown
- Sentinel runner initialization
- Test audio fixture management
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.proof_runs.sentinel_audio_workflow import (
    ARTIFACTS_DIR,
    DEFAULT_API_BASE,
    SENTINEL_FIXTURE_PATH,
    ReproPacket,
    SentinelRunner,
)

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Register custom markers for sentinel tests."""
    config.addinivalue_line(
        "markers", "sentinel: marks tests as sentinel workflow tests"
    )
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests (quick validation)"
    )
    config.addinivalue_line(
        "markers", "backend_required: marks tests that require backend server"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def api_base() -> str:
    """Get API base URL from environment or use default."""
    return os.environ.get("VOICESTUDIO_API_BASE", DEFAULT_API_BASE)


@pytest.fixture(scope="session")
def fixture_path() -> Path:
    """Get path to sentinel audio fixture."""
    path = Path(os.environ.get(
        "VOICESTUDIO_SENTINEL_FIXTURE",
        str(PROJECT_ROOT / SENTINEL_FIXTURE_PATH)
    ))
    return path


@pytest.fixture
def artifacts_dir(tmp_path: Path) -> Path:
    """
    Get path for test artifacts.

    Uses function-scoped tmp_path for test isolation by default.
    Set VOICESTUDIO_KEEP_ARTIFACTS=true to use the real artifacts directory.
    """
    if os.environ.get("VOICESTUDIO_KEEP_ARTIFACTS"):
        # Use real artifacts dir if keeping artifacts
        path = PROJECT_ROOT / ARTIFACTS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path
    else:
        # Use temp dir for test isolation (function-scoped)
        artifacts = tmp_path / "sentinel_runs"
        artifacts.mkdir(parents=True, exist_ok=True)
        return artifacts


@pytest.fixture(scope="session")
def backend_available(api_base: str) -> bool:
    """Check if backend server is available."""
    import httpx

    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{api_base}/api/monitoring/health")
            return response.status_code == 200
    except Exception:
        return False


@pytest.fixture
def sentinel_runner(
    api_base: str,
    fixture_path: Path,
    artifacts_dir: Path
) -> SentinelRunner:
    """Create a fresh SentinelRunner instance for each test."""
    return SentinelRunner(
        api_base=api_base,
        fixture_path=fixture_path,
        artifacts_dir=artifacts_dir,
    )


@pytest.fixture
async def completed_run(
    sentinel_runner: SentinelRunner,
    backend_available: bool,
) -> ReproPacket | None:
    """
    Execute a complete sentinel run.

    Returns None if backend is not available.
    """
    if not backend_available:
        pytest.skip("Backend server not available")
        return None

    return await sentinel_runner.run()


# -----------------------------------------------------------------------------
# Test Data Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_health_response() -> dict:
    """Sample health check response for schema testing."""
    return {
        "status": "healthy",
        "timestamp": "2026-02-12T10:00:00Z",
        "uptime_seconds": 3600.5,
        "version": "1.0.0",
        "checks": [
            {
                "component": "database",
                "status": "healthy",
                "message": "Connected",
                "latency_ms": 5.2,
            }
        ],
    }


@pytest.fixture
def sample_upload_response() -> dict:
    """Sample upload response for schema testing."""
    return {
        "id": "abc123",
        "filename": "test.wav",
        "path": "/data/audio/abc123.wav",
        "original_path": "/data/originals/test.wav",
        "canonical_path": "/data/audio/abc123.wav",
        "size": 44100,
        "original_size": 44100,
        "content_type": "audio/wav",
        "detected_format": "wav",
        "converted": False,
    }


@pytest.fixture
def sample_tts_response() -> dict:
    """Sample TTS response for schema testing."""
    return {
        "audio_id": "synth_123",
        "audio_url": "/api/audio/synth_123/download",
        "duration": 2.5,
        "quality_score": 0.85,
        "quality_metrics": {
            "mos_score": 4.2,
            "similarity": 0.9,
            "naturalness": 0.88,
            "snr_db": 35.5,
            "artifact_score": 0.05,
            "has_clicks": False,
            "has_distortion": False,
        },
    }
