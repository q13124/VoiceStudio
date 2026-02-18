"""
Test Utilities and Helpers
Provides common utilities and helpers for VoiceStudio Quantum+ test suite.
"""

from __future__ import annotations

import json
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

logger = logging.getLogger(__name__)


class TestDataManager:
    """Manages test data creation and cleanup."""

    def __init__(self, base_dir: Path | None = None):
        """
        Initialize test data manager.

        Args:
            base_dir: Base directory for test data (defaults to temp directory)
        """
        if base_dir is None:
            self.base_dir = Path(tempfile.mkdtemp(prefix="voicestudio_test_"))
        else:
            self.base_dir = Path(base_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)

        self.created_paths: list[Path] = []

    def create_file(self, relative_path: str, content: str = "") -> Path:
        """
        Create a test file.

        Args:
            relative_path: Relative path from base directory
            content: File content

        Returns:
            Path to created file
        """
        file_path = self.base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        self.created_paths.append(file_path)
        return file_path

    def create_json_file(self, relative_path: str, data: dict[str, Any]) -> Path:
        """
        Create a JSON test file.

        Args:
            relative_path: Relative path from base directory
            data: JSON data

        Returns:
            Path to created file
        """
        file_path = self.base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.created_paths.append(file_path)
        return file_path

    def create_directory(self, relative_path: str) -> Path:
        """
        Create a test directory.

        Args:
            relative_path: Relative path from base directory

        Returns:
            Path to created directory
        """
        dir_path = self.base_dir / relative_path
        dir_path.mkdir(parents=True, exist_ok=True)
        self.created_paths.append(dir_path)
        return dir_path

    def cleanup(self):
        """Clean up all created test data."""
        try:
            if self.base_dir.exists() and str(self.base_dir).startswith(
                tempfile.gettempdir()
            ):
                shutil.rmtree(self.base_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup test data: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class MockBackendClient:
    """Mock backend client for testing."""

    def __init__(self):
        """Initialize mock backend client."""
        self.responses: dict[str, Any] = {}
        self.requests: list[dict[str, Any]] = []

    def set_response(self, endpoint: str, response: Any, status_code: int = 200):
        """
        Set mock response for an endpoint.

        Args:
            endpoint: API endpoint
            response: Response data
            status_code: HTTP status code
        """
        self.responses[endpoint] = {"data": response, "status_code": status_code}

    def get_response(self, endpoint: str) -> dict[str, Any] | None:
        """
        Get mock response for an endpoint.

        Args:
            endpoint: API endpoint

        Returns:
            Response data or None
        """
        return self.responses.get(endpoint)

    def record_request(self, method: str, endpoint: str, data: Any = None):
        """
        Record a request for verification.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
        """
        self.requests.append({"method": method, "endpoint": endpoint, "data": data})

    def clear_requests(self):
        """Clear recorded requests."""
        self.requests.clear()

    def get_requests(self) -> list[dict[str, Any]]:
        """Get all recorded requests."""
        return self.requests.copy()


class TestAssertions:
    """Enhanced test assertions for VoiceStudio."""

    @staticmethod
    def assert_file_exists(file_path: Path, message: str | None = None):
        """
        Assert that a file exists.

        Args:
            file_path: Path to file
            message: Optional error message
        """
        assert file_path.exists(), message or f"File does not exist: {file_path}"

    @staticmethod
    def assert_file_not_exists(file_path: Path, message: str | None = None):
        """
        Assert that a file does not exist.

        Args:
            file_path: Path to file
            message: Optional error message
        """
        assert not file_path.exists(), message or f"File should not exist: {file_path}"

    @staticmethod
    def assert_directory_exists(dir_path: Path, message: str | None = None):
        """
        Assert that a directory exists.

        Args:
            dir_path: Path to directory
            message: Optional error message
        """
        assert dir_path.exists() and dir_path.is_dir(), (
            message or f"Directory does not exist: {dir_path}"
        )

    @staticmethod
    def assert_valid_json(file_path: Path, message: str | None = None):
        """
        Assert that a file contains valid JSON.

        Args:
            file_path: Path to JSON file
            message: Optional error message
        """
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise AssertionError(message or f"Invalid JSON in {file_path}: {e}")

    @staticmethod
    def assert_dict_contains(
        data: dict[str, Any], keys: list[str], message: str | None = None
    ):
        """
        Assert that a dictionary contains specified keys.

        Args:
            data: Dictionary to check
            keys: List of required keys
            message: Optional error message
        """
        missing_keys = [key for key in keys if key not in data]
        assert not missing_keys, (
            message or f"Missing keys in dictionary: {missing_keys}"
        )


def create_mock_engine(
    engine_name: str = "test_engine",
    supports_batch: bool = True,
    supports_cache: bool = True,
) -> Mock:
    """
    Create a mock engine for testing.

    Args:
        engine_name: Name of the engine
        supports_batch: Whether engine supports batch processing
        supports_cache: Whether engine supports caching

    Returns:
        Mock engine object
    """
    mock_engine = Mock()
    mock_engine.name = engine_name
    mock_engine.supports_batch = supports_batch
    mock_engine.supports_cache = supports_cache
    mock_engine.initialize = Mock(return_value=True)
    mock_engine.cleanup = Mock()
    mock_engine.synthesize = AsyncMock(return_value="test_output.wav")
    mock_engine.batch_synthesize = (
        AsyncMock(return_value=["output1.wav", "output2.wav"])
        if supports_batch
        else None
    )
    return mock_engine


def create_mock_api_response(
    data: Any, status_code: int = 200, headers: dict[str, str] | None = None
) -> Mock:
    """
    Create a mock API response.

    Args:
        data: Response data
        status_code: HTTP status code
        headers: Optional response headers

    Returns:
        Mock response object
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json = Mock(return_value=data)
    mock_response.text = json.dumps(data) if isinstance(data, dict) else str(data)
    mock_response.headers = headers or {}
    mock_response.raise_for_status = Mock()
    return mock_response


def create_temp_audio_file(
    duration_seconds: float = 1.0, sample_rate: int = 22050
) -> Path:
    """
    Create a temporary audio file for testing.

    Args:
        duration_seconds: Duration in seconds
        sample_rate: Sample rate

    Returns:
        Path to temporary audio file
    """
    import numpy as np
    import soundfile as sf

    temp_dir = Path(tempfile.mkdtemp())
    audio_file = temp_dir / "test_audio.wav"

    # Generate simple sine wave
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    audio_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)

    sf.write(str(audio_file), audio_data, sample_rate)
    return audio_file


def cleanup_temp_files(*file_paths: Path):
    """
    Clean up temporary files.

    Args:
        *file_paths: Paths to files/directories to clean up
    """
    for path in file_paths:
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")

