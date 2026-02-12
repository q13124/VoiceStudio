"""
Phase 9: Test Configuration
Task 9.1: Pytest configuration and fixtures.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Any
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Event Loop Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def test_assets_dir(project_root: Path) -> Path:
    """Get the test assets directory."""
    assets_dir = project_root / "tests" / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir


@pytest.fixture
def sample_audio_path(test_assets_dir: Path) -> Path:
    """Get a sample audio file path."""
    return test_assets_dir / "sample.wav"


# ============================================================================
# Engine Mock Fixtures (CI-friendly)
# ============================================================================

@pytest.fixture
def mock_tts_engine():
    """Create a mock TTS engine for CI testing."""
    try:
        from tests.fixtures.engines import MockEngineFactory
        return MockEngineFactory.create_xtts()
    except ImportError:
        pytest.skip("Engine fixtures not available")


@pytest.fixture
def mock_stt_engine():
    """Create a mock STT engine for CI testing."""
    try:
        from tests.fixtures.engines import MockEngineFactory
        return MockEngineFactory.create_whisper()
    except ImportError:
        pytest.skip("Engine fixtures not available")


@pytest.fixture
def mock_engine_service():
    """Create a mock engine service with all common engines for CI testing."""
    try:
        from tests.fixtures.engines import MockEngineService
        return MockEngineService.create_with_engines()
    except ImportError:
        pytest.skip("Engine fixtures not available")


@pytest.fixture
def mock_all_engines():
    """Create all mock engines for comprehensive CI testing."""
    try:
        from tests.fixtures.engines import MockEngineFactory
        return {
            "tts": MockEngineFactory.create_all_tts(),
            "stt": {"whisper": MockEngineFactory.create_whisper()},
            "quality": {"analyzer": MockEngineFactory.create_quality_analyzer()},
        }
    except ImportError:
        pytest.skip("Engine fixtures not available")


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_engine_config() -> dict[str, Any]:
    """Get mock engine configuration."""
    return {
        "engine_id": "test-engine",
        "name": "Test Engine",
        "version": "1.0.0",
        "capabilities": ["synthesis", "transcription"],
        "model_path": "/path/to/model",
    }


@pytest.fixture
def mock_synthesis_request() -> dict[str, Any]:
    """Get mock synthesis request."""
    return {
        "text": "Hello, this is a test.",
        "voice_id": "test-voice",
        "language": "en",
        "settings": {
            "speed": 1.0,
            "pitch": 1.0,
        },
    }


@pytest.fixture
def mock_project_data() -> dict[str, Any]:
    """Get mock project data."""
    return {
        "id": "test-project",
        "name": "Test Project",
        "created_at": "2025-01-01T00:00:00Z",
        "tracks": [],
        "settings": {},
    }


# ============================================================================
# Backend Fixtures
# ============================================================================

@pytest.fixture
def backend_config() -> dict[str, Any]:
    """Get backend configuration for testing."""
    return {
        "host": "127.0.0.1",
        "port": 8000,
        "debug": True,
        "log_level": "DEBUG",
    }


@pytest.fixture
async def test_client():
    """Create a test client for the FastAPI backend."""
    try:
        from httpx import AsyncClient, ASGITransport
        from backend.api.main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            yield client
    except ImportError:
        pytest.skip("httpx or backend not available")


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def test_db_path(temp_dir: Path) -> Path:
    """Get a test database path."""
    return temp_dir / "test.db"


@pytest.fixture
async def test_database(test_db_path: Path):
    """Create a test database."""
    # Create database tables
    # This would initialize the test database
    yield test_db_path
    
    # Cleanup
    if test_db_path.exists():
        test_db_path.unlink()


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def clean_env():
    """Fixture that restores environment after test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def test_env(clean_env):
    """Set up test environment variables."""
    os.environ["VOICESTUDIO_TEST"] = "1"
    os.environ["VOICESTUDIO_LOG_LEVEL"] = "DEBUG"
    return os.environ


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "engine: marks tests that require a voice engine"
    )


# ============================================================================
# Hooks
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Skip GPU tests if no GPU available
    skip_gpu = pytest.mark.skip(reason="GPU not available")
    
    try:
        import torch
        has_gpu = torch.cuda.is_available()
    except (ImportError, AttributeError):
        # AttributeError can occur with partial torch initialization (circular import)
        has_gpu = False
    
    for item in items:
        if "gpu" in item.keywords and not has_gpu:
            item.add_marker(skip_gpu)
