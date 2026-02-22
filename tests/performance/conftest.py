"""
Performance tests configuration.

Provides fixtures and configuration for performance testing.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "performance: marks tests as performance tests")


@pytest.fixture(scope="session")
def performance_config():
    """Performance test configuration."""
    return {
        "api_base_url": "http://localhost:8088",
        "timeout": 60,
        "concurrent_users": 10,
        "duration_seconds": 30,
    }
