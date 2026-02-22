"""
Pytest configuration for resilience tests.

Provides fixtures for testing plugin system resilience under
various failure scenarios.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


@pytest.fixture
def temp_plugin_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for plugin tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_plugin_manifest() -> dict[str, Any]:
    """Create a mock plugin manifest."""
    return {
        "id": "test-resilience-plugin",
        "name": "Resilience Test Plugin",
        "version": "1.0.0",
        "description": "Plugin for resilience testing",
        "author": "Test",
        "capabilities": [
            {
                "name": "test_capability",
                "description": "Test capability",
            }
        ],
        "permissions": ["audio.read"],
    }


@pytest.fixture
def mock_process() -> MagicMock:
    """Create a mock subprocess for plugin process simulation."""
    process = MagicMock()
    process.pid = 12345
    process.returncode = None
    process.stdin = MagicMock()
    process.stdout = MagicMock()
    process.stderr = MagicMock()
    process.wait = AsyncMock(return_value=0)
    process.kill = MagicMock()
    process.terminate = MagicMock()
    return process


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Markers for different resilience test categories
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "crash: tests for crash recovery scenarios")
    config.addinivalue_line("markers", "oom: tests for out-of-memory scenarios")
    config.addinivalue_line("markers", "ipc_timeout: tests for IPC timeout scenarios")
    config.addinivalue_line("markers", "concurrent: tests for concurrent load scenarios")
    config.addinivalue_line("markers", "slow: tests that take longer to run")
