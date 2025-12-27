"""
Pytest configuration and fixtures for quality features integration tests.
"""

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from api.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_profile_id():
    """Sample profile ID for testing."""
    return "test-profile-123"

@pytest.fixture
def sample_reference_audio_id():
    """Sample reference audio ID for testing."""
    return "test-audio-123"

@pytest.fixture
def sample_test_text():
    """Sample test text for synthesis."""
    return "This is a test sentence for quality testing."

