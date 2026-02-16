"""
E2E Test Base Classes.

Provides base test class and configuration for end-to-end testing
using WinAppDriver/FlaUI for UI automation.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class E2EConfig:
    """Configuration for E2E tests."""

    # Application paths
    app_path: Path = field(default_factory=lambda: Path(
        r"src\VoiceStudio.App\bin\x64\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe"
    ))
    app_name: str = "VoiceStudio"

    # WinAppDriver configuration
    winappdriver_path: Path = field(default_factory=lambda: Path(
        r"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
    ))
    winappdriver_url: str = "http://127.0.0.1:4723"

    # Backend configuration
    backend_url: str = "http://localhost:8000"

    # Timeouts (in seconds)
    app_startup_timeout: float = 30.0
    element_wait_timeout: float = 10.0
    action_timeout: float = 5.0
    backend_timeout: float = 10.0

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0

    # Artifact paths
    screenshot_dir: Path = field(default_factory=lambda: Path(
        ".buildlogs/e2e/screenshots"
    ))
    logs_dir: Path = field(default_factory=lambda: Path(
        ".buildlogs/e2e/logs"
    ))

    # Test data paths
    test_data_dir: Path = field(default_factory=lambda: Path(
        "tests/fixtures"
    ))

    def __post_init__(self):
        """Ensure directories exist."""
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> E2EConfig:
        """Create config from environment variables."""
        config = cls()

        if app_path := os.environ.get("VOICESTUDIO_APP_PATH"):
            config.app_path = Path(app_path)
        if backend_url := os.environ.get("VOICESTUDIO_BACKEND_URL"):
            config.backend_url = backend_url
        if winappdriver_url := os.environ.get("WINAPPDRIVER_URL"):
            config.winappdriver_url = winappdriver_url

        return config


# Default configuration
DEFAULT_CONFIG = E2EConfig.from_env()


# =============================================================================
# E2E Test Base Class
# =============================================================================


class E2ETestBase:
    """
    Base class for E2E tests.

    Provides:
    - Application session management
    - Screenshot capture on failure
    - Backend health verification
    - Element wait and interaction helpers

    Usage:
        class TestVoiceCloning(E2ETestBase):
            def test_clone_voice_workflow(self, app_session):
                # Use app_session to interact with UI
                main_window = app_session.find_element("MainWindow")
                ...
    """

    config: E2EConfig = DEFAULT_CONFIG
    _driver = None
    _winappdriver_process = None

    @classmethod
    def setup_class(cls):
        """Set up class-level resources."""
        cls.config = E2EConfig.from_env()

    @classmethod
    def teardown_class(cls):
        """Clean up class-level resources."""
        pass

    def setup_method(self, method):
        """Set up test method."""
        logger.info(f"Starting test: {method.__name__}")

    def teardown_method(self, method):
        """Clean up after test method."""
        logger.info(f"Finished test: {method.__name__}")

    # -------------------------------------------------------------------------
    # Backend Helpers
    # -------------------------------------------------------------------------

    def verify_backend_health(self) -> bool:
        """Check if backend is running and healthy."""
        import requests

        try:
            response = requests.get(
                f"{self.config.backend_url}/health",
                timeout=self.config.backend_timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Backend health check failed: {e}")
            return False

    def wait_for_backend(self, timeout: float | None = None) -> bool:
        """Wait for backend to become available."""

        timeout = timeout or self.config.backend_timeout
        start = time.time()

        while time.time() - start < timeout:
            if self.verify_backend_health():
                return True
            time.sleep(0.5)

        return False

    # -------------------------------------------------------------------------
    # Screenshot Helpers
    # -------------------------------------------------------------------------

    def capture_screenshot(self, name: str) -> Path | None:
        """Capture a screenshot and save to artifacts directory."""
        if self._driver is None:
            logger.warning("No driver available for screenshot")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.config.screenshot_dir / filename

        try:
            self._driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def capture_failure_screenshot(self, test_name: str) -> Path | None:
        """Capture screenshot on test failure."""
        return self.capture_screenshot(f"FAILED_{test_name}")

    # -------------------------------------------------------------------------
    # Wait Helpers
    # -------------------------------------------------------------------------

    def wait_for_element(
        self,
        locator: str,
        by: str = "automation_id",
        timeout: float | None = None
    ) -> Any:
        """Wait for an element to be present and visible."""
        timeout = timeout or self.config.element_wait_timeout
        start = time.time()

        while time.time() - start < timeout:
            try:
                element = self._find_element(locator, by)
                if element is not None:
                    return element
            # ALLOWED: bare except - Polling for element, retrying is expected
            except Exception:
                pass
            time.sleep(0.5)

        raise TimeoutError(f"Element not found: {locator} (by={by})")

    def wait_for_element_gone(
        self,
        locator: str,
        by: str = "automation_id",
        timeout: float | None = None
    ) -> bool:
        """Wait for an element to disappear."""
        timeout = timeout or self.config.element_wait_timeout
        start = time.time()

        while time.time() - start < timeout:
            try:
                element = self._find_element(locator, by)
                if element is None:
                    return True
            except Exception:
                return True
            time.sleep(0.5)

        return False

    def _find_element(self, locator: str, by: str = "automation_id") -> Any:
        """Find element by locator strategy."""
        if self._driver is None:
            raise RuntimeError("Driver not initialized")

        by_mapping = {
            "automation_id": "accessibility id",
            "name": "name",
            "class_name": "class name",
            "xpath": "xpath",
        }

        actual_by = by_mapping.get(by, by)
        return self._driver.find_element(actual_by, locator)

    # -------------------------------------------------------------------------
    # Application Helpers
    # -------------------------------------------------------------------------

    def verify_app_launched(self) -> bool:
        """Verify application has launched successfully."""
        try:
            # Wait for main window
            self.wait_for_element("MainWindow", timeout=self.config.app_startup_timeout)
            return True
        except TimeoutError:
            return False

    def close_all_dialogs(self):
        """Close any open dialogs."""
        dialog_locators = [
            "CloseButton",
            "CancelButton",
            "DismissButton",
        ]

        for locator in dialog_locators:
            try:
                element = self._find_element(locator)
                if element:
                    element.click()
                    time.sleep(0.5)
            # ALLOWED: bare except - Best effort cleanup, failure is acceptable
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Assertion Helpers
    # -------------------------------------------------------------------------

    def assert_element_visible(self, locator: str, by: str = "automation_id"):
        """Assert element is visible."""
        element = self._find_element(locator, by)
        assert element is not None, f"Element not visible: {locator}"
        assert element.is_displayed(), f"Element not displayed: {locator}"

    def assert_element_text(
        self,
        locator: str,
        expected_text: str,
        by: str = "automation_id"
    ):
        """Assert element has expected text."""
        element = self._find_element(locator, by)
        assert element is not None, f"Element not found: {locator}"
        actual_text = element.text
        assert expected_text in actual_text, \
            f"Expected '{expected_text}' but got '{actual_text}'"

    def assert_element_enabled(self, locator: str, by: str = "automation_id"):
        """Assert element is enabled."""
        element = self._find_element(locator, by)
        assert element is not None, f"Element not found: {locator}"
        assert element.is_enabled(), f"Element not enabled: {locator}"


# =============================================================================
# Pytest Markers
# =============================================================================


def e2e(func):
    """Mark a test as an E2E test."""
    return pytest.mark.e2e(func)


def requires_app(func):
    """Mark a test as requiring the application."""
    return pytest.mark.requires_app(func)


def requires_backend(func):
    """Mark a test as requiring the backend."""
    return pytest.mark.requires_backend(func)


def slow(func):
    """Mark a test as slow."""
    return pytest.mark.slow(func)
