"""
Integration Test Configuration

Provides shared fixtures and configuration for integration tests.
"""

import logging
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_base_url():
    """Provide API base URL."""
    return "http://localhost:8000/api"


@pytest.fixture(scope="session")
def test_timeout():
    """Provide test timeout in seconds."""
    return 60.0


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Setup code here if needed
    yield
    # Cleanup code here if needed

