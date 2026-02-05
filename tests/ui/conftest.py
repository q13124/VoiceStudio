"""
Pytest configuration and fixtures for UI tests.

Enhanced with:
- Screenshot capture on test failure
- Environment variable support for application path
- Retry utilities for flaky element lookups
- Structured output directories
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytest
from appium import webdriver
from appium.options.windows import WindowsOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# =============================================================================
# Configuration
# =============================================================================

WINAPPDRIVER_URL = os.getenv("WINAPPDRIVER_URL", "http://127.0.0.1:4723")
WINAPPDRIVER_PATH = os.getenv(
    "WINAPPDRIVER_PATH",
    r"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
)
IMPLICIT_WAIT = int(os.getenv("UI_TEST_IMPLICIT_WAIT", "10"))  # seconds
EXPLICIT_WAIT = int(os.getenv("UI_TEST_EXPLICIT_WAIT", "30"))  # seconds

# Application path - check environment variable first
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / ".buildlogs" / "ui_tests"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

# Try environment variable, then fallback to build paths
APP_PATH_ENV = os.getenv("VS_APP_PATH")
if APP_PATH_ENV:
    APP_PATH = Path(APP_PATH_ENV)
else:
    # Try multiple possible locations
    POSSIBLE_PATHS = [
        PROJECT_ROOT / ".buildlogs" / "publish" / "VoiceStudio.App.exe",
        PROJECT_ROOT / "src" / "VoiceStudio.App" / "bin" / "Debug" 
        / "net8.0-windows10.0.19041.0" / "VoiceStudio.App.exe",
        PROJECT_ROOT / "src" / "VoiceStudio.App" / "bin" / "Release"
        / "net8.0-windows10.0.19041.0" / "win-x64" / "publish" / "VoiceStudio.App.exe",
    ]
    APP_PATH = next((p for p in POSSIBLE_PATHS if p.exists()), POSSIBLE_PATHS[0])


# =============================================================================
# Setup
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and output directories."""
    # Register custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "flaky: marks tests as potentially flaky")
    config.addinivalue_line("markers", "smoke: marks tests as smoke tests")
    config.addinivalue_line("markers", "navigation: marks tests as navigation tests")
    config.addinivalue_line("markers", "panel: marks tests as panel functionality tests")
    
    # Ensure output directories exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Utility Functions
# =============================================================================

def is_winappdriver_running() -> bool:
    """Check if WinAppDriver is running."""
    try:
        import requests
        response = requests.get(f"{WINAPPDRIVER_URL}/status", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def start_winappdriver() -> bool:
    """Start WinAppDriver service."""
    if is_winappdriver_running():
        return True

    try:
        if os.path.exists(WINAPPDRIVER_PATH):
            subprocess.Popen(
                [WINAPPDRIVER_PATH],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Wait for WinAppDriver to start
            for _ in range(10):
                time.sleep(1)
                if is_winappdriver_running():
                    return True
        return False
    except Exception as e:
        print(f"Failed to start WinAppDriver: {e}")
        return False


def capture_screenshot(driver, name: str) -> Optional[Path]:
    """Capture a screenshot and save to the screenshots directory."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename
        driver.save_screenshot(str(filepath))
        print(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return None


def find_element_with_retry(driver, by: str, value: str, retries: int = 3, 
                            delay: float = 1.0):
    """Find an element with retry logic for flaky lookups."""
    last_exception = None
    for attempt in range(retries):
        try:
            return driver.find_element(by, value)
        except NoSuchElementException as e:
            last_exception = e
            if attempt < retries - 1:
                time.sleep(delay)
    raise last_exception


def wait_for_element(driver, automation_id: str, timeout: int = EXPLICIT_WAIT):
    """Wait for an element to be present and visible."""
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(
            EC.presence_of_element_located(("accessibility id", automation_id))
        )
        return element
    except TimeoutException:
        raise TimeoutException(f"Element '{automation_id}' not found within {timeout}s")


def wait_for_panel_load(driver, panel_id: str, timeout: int = EXPLICIT_WAIT):
    """Wait for a panel to fully load."""
    element = wait_for_element(driver, panel_id, timeout)
    # Additional wait for content to render
    time.sleep(0.5)
    return element


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def winappdriver_service():
    """Ensure WinAppDriver is running before tests."""
    if not is_winappdriver_running():
        if not start_winappdriver():
            pytest.skip(
                "WinAppDriver is not running and could not be started. "
                "Please start WinAppDriver manually."
            )
    yield
    # Cleanup if needed


@pytest.fixture(scope="function")
def driver(winappdriver_service, request):
    """Create and configure Appium WebDriver for Windows application."""
    if not APP_PATH.exists():
        pytest.skip(
            f"Application not found at {APP_PATH}. Please build the application first. "
            f"Set VS_APP_PATH environment variable to override."
        )

    options = WindowsOptions()
    options.app = str(APP_PATH)
    options.platform_name = "Windows"

    # Create driver
    driver = webdriver.Remote(command_executor=WINAPPDRIVER_URL, options=options)

    # Set implicit wait
    driver.implicitly_wait(IMPLICIT_WAIT)

    yield driver

    # Capture screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name.replace("::", "_").replace("[", "_").replace("]", "_")
        capture_screenshot(driver, f"FAILED_{test_name}")

    # Cleanup
    try:
        driver.quit()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test result for screenshot on failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="function")
def app_launched(driver):
    """Ensure application is launched and ready."""
    # Wait for main window to be available
    try:
        main_window = wait_for_element(driver, "MainWindow_Root", timeout=30)
        return main_window
    except TimeoutException:
        # If main window not found, application may still be loading
        time.sleep(2)
        try:
            main_window = driver.find_element("accessibility id", "MainWindow_Root")
            return main_window
        except NoSuchElementException:
            pytest.fail("Application failed to launch - MainWindow_Root not found")


@pytest.fixture
def screenshot(driver):
    """Fixture to capture screenshots on demand."""
    def _capture(name: str):
        return capture_screenshot(driver, name)
    return _capture


@pytest.fixture
def navigate_to_panel(driver, app_launched):
    """Fixture to navigate to a specific panel."""
    def _navigate(panel_button_id: str, panel_view_id: str, timeout: int = EXPLICIT_WAIT):
        try:
            button = find_element_with_retry(
                driver, "accessibility id", panel_button_id
            )
            button.click()
            time.sleep(0.5)
            return wait_for_panel_load(driver, panel_view_id, timeout)
        except Exception as e:
            raise AssertionError(
                f"Failed to navigate to panel. Button: {panel_button_id}, "
                f"View: {panel_view_id}. Error: {e}"
            )
    return _navigate


@pytest.fixture
def retry_action():
    """Fixture for retrying flaky actions."""
    def _retry(action, retries: int = 3, delay: float = 1.0, on_fail=None):
        last_exception = None
        for attempt in range(retries):
            try:
                return action()
            except Exception as e:
                last_exception = e
                if on_fail:
                    on_fail(attempt, e)
                if attempt < retries - 1:
                    time.sleep(delay)
        raise last_exception
    return _retry


# =============================================================================
# Session Info
# =============================================================================

def pytest_report_header(config):
    """Add custom header info to test report."""
    return [
        f"VoiceStudio UI Tests",
        f"  App Path: {APP_PATH}",
        f"  WinAppDriver: {WINAPPDRIVER_URL}",
        f"  Screenshots: {SCREENSHOT_DIR}",
    ]
