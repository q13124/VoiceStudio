"""
Pytest configuration and fixtures for UI tests.
"""

import os
import subprocess
import time
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.windows import WindowsOptions

# Configuration
WINAPPDRIVER_URL = "http://127.0.0.1:4723"
WINAPPDRIVER_PATH = (
    r"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
)
IMPLICIT_WAIT = 10  # seconds
EXPLICIT_WAIT = 30  # seconds

# Application path (update to match your build location)
PROJECT_ROOT = Path(__file__).parent.parent.parent
APP_PATH = (
    PROJECT_ROOT
    / "src"
    / "VoiceStudio.App"
    / "bin"
    / "Debug"
    / "net8.0-windows10.0.19041.0"
    / "VoiceStudioApp.exe"
)


def is_winappdriver_running() -> bool:
    """Check if WinAppDriver is running."""
    try:
        import requests

        response = requests.get(f"{WINAPPDRIVER_URL}/status", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_winappdriver():
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


@pytest.fixture(scope="session")
def winappdriver_service():
    """Ensure WinAppDriver is running before tests."""
    if not is_winappdriver_running():
        if not start_winappdriver():
            pytest.skip(
                "WinAppDriver is not running and could not be started. Please start WinAppDriver manually."
            )
    yield
    # Cleanup if needed


@pytest.fixture(scope="function")
def driver(winappdriver_service):
    """Create and configure Appium WebDriver for Windows application."""
    if not APP_PATH.exists():
        pytest.skip(
            f"Application not found at {APP_PATH}. Please build the application first."
        )

    options = WindowsOptions()
    options.app = str(APP_PATH)
    options.platform_name = "Windows"

    # Create driver
    driver = webdriver.Remote(command_executor=WINAPPDRIVER_URL, options=options)

    # Set implicit wait
    driver.implicitly_wait(IMPLICIT_WAIT)

    yield driver

    # Cleanup
    try:
        driver.quit()
    except:
        ...


@pytest.fixture(scope="function")
def app_launched(driver):
    """Ensure application is launched and ready."""
    # Wait for main window to be available
    try:
        main_window = driver.find_element("accessibility id", "MainWindow_Root")
        return main_window
    except:
        # If main window not found, application may still be loading
        time.sleep(2)
        main_window = driver.find_element("accessibility id", "MainWindow_Root")
        return main_window
