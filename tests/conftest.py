"""
Pytest configuration and fixtures for VoiceStudio Quantum+ test suite.
Provides shared fixtures and test utilities for all test modules.
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Generator, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))
sys.path.insert(0, str(project_root / "backend"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Return the project root directory."""
    return project_root


@pytest.fixture(scope="session")
def test_data_dir(project_root_path: Path) -> Path:
    """Return the test data directory."""
    return project_root_path / "tests" / "test_data"


@pytest.fixture(scope="function")
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test files."""
    return tmp_path


@pytest.fixture(scope="session")
def sample_audio_path(test_data_dir: Path) -> Path:
    """Return path to sample audio file for testing."""
    audio_path = test_data_dir / "audio" / "sample.wav"
    if not audio_path.exists():
        # Create placeholder if doesn't exist
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Sample audio not found at {audio_path}, tests may fail")
    return audio_path


@pytest.fixture(scope="session")
def sample_profile_data(test_data_dir: Path) -> dict:
    """Return sample voice profile data for testing."""
    return {
        "id": "test-profile-1",
        "name": "Test Profile",
        "language": "en",
        "gender": "neutral",
        "age": "adult"
    }


@pytest.fixture(scope="function")
def mock_backend_url() -> str:
    """Return mock backend URL for testing."""
    return "http://localhost:8000"


@pytest.fixture(scope="function", autouse=True)
def reset_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment variables before each test."""
    # Clear any test-specific environment variables
    test_vars = ["VOICESTUDIO_TEST_MODE", "VOICESTUDIO_DEBUG"]
    for var in test_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture(scope="function")
def caplog_context(caplog: pytest.LogCaptureFixture) -> Generator[None, None, None]:
    """Provide logging context for tests."""
    with caplog.at_level(logging.DEBUG):
        yield


# Import test utilities (lazy import to avoid circular dependencies)
try:
    from tests.test_utils import (
        TestDataManager,
        MockBackendClient,
        TestAssertions,
        create_mock_engine,
        create_mock_api_response,
        create_temp_audio_file,
        cleanup_temp_files,
    )
except ImportError:
    # Fallback if test_utils not available
    TestDataManager = None
    MockBackendClient = None
    TestAssertions = None
    create_mock_engine = None
    create_mock_api_response = None
    create_temp_audio_file = None
    cleanup_temp_files = None


@pytest.fixture(scope="function")
def test_data_manager(temp_dir: Path):
    """Provide test data manager for test file creation."""
    if TestDataManager is None:
        pytest.skip("TestDataManager not available")
    manager = TestDataManager(base_dir=temp_dir)
    yield manager
    manager.cleanup()


@pytest.fixture(scope="function")
def mock_backend_client():
    """Provide mock backend client for testing."""
    if MockBackendClient is None:
        pytest.skip("MockBackendClient not available")
    return MockBackendClient()


@pytest.fixture(scope="function")
def test_assertions():
    """Provide enhanced test assertions."""
    if TestAssertions is None:
        pytest.skip("TestAssertions not available")
    return TestAssertions()


@pytest.fixture(scope="function")
def mock_engine():
    """Provide mock engine for testing."""
    if create_mock_engine is None:
        pytest.skip("create_mock_engine not available")
    return create_mock_engine()


@pytest.fixture(scope="function")
def temp_audio_file():
    """Provide temporary audio file for testing."""
    if create_temp_audio_file is None or cleanup_temp_files is None:
        pytest.skip("Audio file utilities not available")
    audio_file = create_temp_audio_file()
    yield audio_file
    cleanup_temp_files(audio_file.parent)


# Markers for test categorization
pytest_plugins = []

