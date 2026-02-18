"""
Test Data Management

Provides test data fixtures and helpers for integration tests.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Test data directory
TEST_DATA_DIR = project_root / "tests" / "test_data"


class TestDataManager:
    """Manages test data for integration tests."""

    def __init__(self):
        """Initialize test data manager."""
        self.test_data_dir = TEST_DATA_DIR
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def generate_test_audio(
        self,
        duration_seconds: float = 1.0,
        sample_rate: int = 22050,
        frequency: float = 440.0,
    ) -> np.ndarray:
        """
        Generate test audio signal.

        Args:
            duration_seconds: Duration in seconds
            sample_rate: Sample rate in Hz
            frequency: Frequency in Hz

        Returns:
            Audio array
        """
        t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
        audio = np.sin(2 * np.pi * frequency * t)
        audio = audio * 0.5
        return audio.astype(np.float32)

    def create_test_profile_data(self) -> dict[str, Any]:
        """Create test profile data."""
        return {
            "name": "Test Profile",
            "description": "Test profile for integration testing",
            "engine": "xtts_v2",
            "quality_mode": "standard",
        }

    def create_test_project_data(self) -> dict[str, Any]:
        """Create test project data."""
        return {
            "name": "Test Project",
            "description": "Test project for integration testing",
        }

    def create_test_synthesis_data(self, profile_id: str) -> dict[str, Any]:
        """Create test synthesis data."""
        return {
            "profile_id": profile_id,
            "text": "Hello, this is a test synthesis.",
            "engine": "xtts_v2",
            "language": "en",
        }

    def create_test_batch_data(self) -> dict[str, Any]:
        """Create test batch job data."""
        return {
            "name": "Test Batch Job",
            "items": [
                {"text": "First item", "profile_id": "test-profile"},
                {"text": "Second item", "profile_id": "test-profile"},
                {"text": "Third item", "profile_id": "test-profile"},
            ],
        }

    def save_test_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
        filename: str,
    ) -> Path:
        """
        Save test audio to file.

        Args:
            audio: Audio array
            sample_rate: Sample rate
            filename: Filename

        Returns:
            Path to saved file
        """
        try:
            import soundfile as sf

            audio_dir = self.test_data_dir / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            file_path = audio_dir / filename
            sf.write(str(file_path), audio, sample_rate)

            return file_path

        except ImportError:
            logger.warning("soundfile not available, cannot save audio")
            return Path()

    def load_test_audio(self, filename: str) -> tuple | None:
        """
        Load test audio from file.

        Args:
            filename: Filename

        Returns:
            Tuple of (audio, sample_rate) or None
        """
        try:
            import soundfile as sf

            file_path = self.test_data_dir / "audio" / filename
            if not file_path.exists():
                return None

            audio, sample_rate = sf.read(str(file_path))
            return audio, sample_rate

        except ImportError:
            logger.warning("soundfile not available, cannot load audio")
            return None
        except Exception as e:
            logger.warning(f"Failed to load audio: {e}")
            return None

    def cleanup_test_data(self):
        """Cleanup test data files."""
        try:
            audio_dir = self.test_data_dir / "audio"
            if audio_dir.exists():
                for file in audio_dir.glob("*.wav"):
                    file.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup test data: {e}")


# Pytest fixtures
@pytest.fixture
def test_data_manager():
    """Provide test data manager fixture."""
    manager = TestDataManager()
    yield manager
    manager.cleanup_test_data()


@pytest.fixture
def test_audio():
    """Provide test audio fixture."""
    manager = TestDataManager()
    return manager.generate_test_audio(duration_seconds=2.0, sample_rate=24000)


@pytest.fixture
def test_profile_data():
    """Provide test profile data fixture."""
    manager = TestDataManager()
    return manager.create_test_profile_data()


@pytest.fixture
def test_project_data():
    """Provide test project data fixture."""
    manager = TestDataManager()
    return manager.create_test_project_data()


@pytest.fixture
def test_synthesis_data(test_profile_data):
    """Provide test synthesis data fixture."""
    manager = TestDataManager()
    # Note: profile_id would normally come from created profile
    return manager.create_test_synthesis_data(profile_id="test-profile-id")


@pytest.fixture
def test_batch_data():
    """Provide test batch data fixture."""
    manager = TestDataManager()
    return manager.create_test_batch_data()

