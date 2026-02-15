"""
Backend Integration Test Base Class.

Provides a standardized base class for backend integration tests with:
- Automatic database setup and teardown
- Test isolation via transaction rollback
- Enhanced test client with response tracking
- Common assertions and utilities
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import tempfile
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.integration.conftest import (
    IntegrationTestConfig,
    ResponseTracker,
    TestResponse,
    validate_error_response,
    validate_response_schema,
)

logger = logging.getLogger(__name__)


class IntegrationTestBase:
    """
    Base class for backend integration tests.

    Provides:
    - Automatic test isolation
    - Database transaction rollback
    - Enhanced API client
    - Common assertions

    Usage:
        class TestMyFeature(IntegrationTestBase):
            def test_something(self, test_client):
                response = test_client.get("/api/health")
                self.assert_success(response)
    """

    # Class-level configuration
    TEST_TIMEOUT = 30.0
    ENABLE_LOGGING = True
    VALIDATE_RESPONSES = True

    # ==========================================================================
    # Test Lifecycle
    # ==========================================================================

    @pytest.fixture(autouse=True)
    def setup_test_environment(self) -> Generator[None, None, None]:
        """Set up test environment before each test."""
        # Store original environment
        original_env = os.environ.copy()

        # Set test-specific environment variables
        os.environ["VOICESTUDIO_TEST_MODE"] = "1"
        os.environ["VOICESTUDIO_DISABLE_TELEMETRY"] = "1"
        os.environ["VOICESTUDIO_LOG_LEVEL"] = "WARNING"

        # Create temp directory for test artifacts
        self._temp_dir = tempfile.mkdtemp(prefix="vs_integration_test_")
        os.environ["VOICESTUDIO_TEST_TEMP"] = self._temp_dir

        # Initialize test state
        self._test_start_time = datetime.utcnow()
        self._test_artifacts: list[Path] = []

        yield

        # Cleanup
        self._cleanup_test_artifacts()

        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

    @pytest.fixture(autouse=True)
    def setup_logging(self) -> Generator[None, None, None]:
        """Configure logging for test execution."""
        if self.ENABLE_LOGGING:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        yield

    # ==========================================================================
    # Database Fixtures
    # ==========================================================================

    @pytest.fixture
    def test_db_path(self) -> Generator[Path, None, None]:
        """Provide a temporary database path for testing."""
        db_path = Path(self._temp_dir) / "test_db.sqlite"
        yield db_path
        # Cleanup handled by temp dir removal

    @pytest.fixture
    def mock_database(self, test_db_path: Path) -> Generator[MagicMock, None, None]:
        """
        Provide a mock database for tests that don't need real DB.

        For tests that need real database, use `real_database` fixture instead.
        """
        mock_db = MagicMock()
        mock_db.path = test_db_path
        mock_db.is_connected = True
        mock_db.execute = MagicMock(return_value=[])
        mock_db.commit = MagicMock()
        mock_db.rollback = MagicMock()
        yield mock_db

    @asynccontextmanager
    async def database_transaction(self, db: Any) -> AsyncGenerator[Any, None]:
        """
        Context manager for database transactions with automatic rollback.

        Usage:
            async with self.database_transaction(db) as conn:
                await conn.execute("INSERT INTO ...")
            # Automatically rolled back after test
        """
        try:
            yield db
        finally:
            if hasattr(db, 'rollback'):
                if asyncio.iscoroutinefunction(db.rollback):
                    await db.rollback()
                else:
                    db.rollback()

    # ==========================================================================
    # API Client Fixtures
    # ==========================================================================

    @pytest.fixture
    def api_config(self) -> IntegrationTestConfig:
        """Provide test configuration."""
        return IntegrationTestConfig(
            api_base_url="http://localhost:8000/api",
            api_version="1.0",
            timeout=self.TEST_TIMEOUT,
            retry_count=3,
            retry_delay=0.5,
            enable_logging=self.ENABLE_LOGGING,
            validate_responses=self.VALIDATE_RESPONSES,
        )

    @pytest.fixture
    def response_tracker(self) -> ResponseTracker:
        """Provide a fresh response tracker."""
        return ResponseTracker()

    # ==========================================================================
    # Assertions
    # ==========================================================================

    def assert_success(self, response: TestResponse, msg: str = "") -> None:
        """Assert response is successful (2xx status code)."""
        assert response.is_success, (
            f"Expected success, got {response.status_code}: {response.body}"
            + (f" - {msg}" if msg else "")
        )

    def assert_status(self, response: TestResponse, expected: int, msg: str = "") -> None:
        """Assert response has expected status code."""
        assert response.status_code == expected, (
            f"Expected {expected}, got {response.status_code}: {response.body}"
            + (f" - {msg}" if msg else "")
        )

    def assert_error(self, response: TestResponse, expected_status: int | None = None) -> None:
        """Assert response is an error and validate error format."""
        if expected_status:
            self.assert_status(response, expected_status)
        else:
            assert not response.is_success, f"Expected error, got success: {response.body}"
        validate_error_response(response)

    def assert_schema(self, response: TestResponse, required_fields: list[str]) -> None:
        """Assert response body contains required fields."""
        validate_response_schema(response, required_fields)

    def assert_latency(
        self,
        response: TestResponse,
        max_ms: float,
        msg: str = ""
    ) -> None:
        """Assert response latency is within acceptable range."""
        assert response.elapsed_ms <= max_ms, (
            f"Response took {response.elapsed_ms:.2f}ms, max allowed: {max_ms}ms"
            + (f" - {msg}" if msg else "")
        )

    def assert_api_version(self, response: TestResponse, expected: str | None = None) -> None:
        """Assert response contains expected API version header."""
        version = response.api_version
        if expected:
            assert version == expected, f"Expected version {expected}, got {version}"
        else:
            assert version is not None, "Missing API version header"

    # ==========================================================================
    # Test Utilities
    # ==========================================================================

    def create_test_artifact(self, name: str, content: str = "") -> Path:
        """Create a test artifact file that will be cleaned up after test."""
        artifact_path = Path(self._temp_dir) / name
        artifact_path.write_text(content)
        self._test_artifacts.append(artifact_path)
        return artifact_path

    def get_test_elapsed_time(self) -> float:
        """Get elapsed time since test started in seconds."""
        return (datetime.utcnow() - self._test_start_time).total_seconds()

    def skip_if_no_backend(self) -> None:
        """Skip test if backend is not available."""
        import requests
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code != 200:
                pytest.skip("Backend not healthy")
        except Exception:
            pytest.skip("Backend not available")

    def _cleanup_test_artifacts(self) -> None:
        """Clean up test artifacts."""
        import shutil

        # Remove individual artifacts
        for artifact in self._test_artifacts:
            try:
                if artifact.exists():
                    artifact.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove artifact {artifact}: {e}")

        # Remove temp directory
        if hasattr(self, '_temp_dir') and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except Exception as e:
                logger.warning(f"Failed to remove temp dir {self._temp_dir}: {e}")


class AsyncIntegrationTestBase(IntegrationTestBase):
    """
    Async version of IntegrationTestBase for async test methods.

    Usage:
        class TestAsyncFeature(AsyncIntegrationTestBase):
            @pytest.mark.asyncio
            async def test_something(self, test_client):
                response = await test_client.async_get("/api/health")
                self.assert_success(response)
    """

    @pytest.fixture
    def event_loop(self):
        """Create event loop for async tests."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    async def async_skip_if_no_backend(self) -> None:
        """Async version of skip_if_no_backend."""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session, session.get(
                "http://localhost:8000/api/health",
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                if response.status != 200:
                    pytest.skip("Backend not healthy")
        except Exception:
            pytest.skip("Backend not available")


# Marker for integration tests
integration = pytest.mark.integration
