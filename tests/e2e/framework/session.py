"""
Session Management for E2E Tests.

Provides session management for WinAppDriver and application lifecycle.
"""

import logging
import os
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

logger = logging.getLogger(__name__)


# =============================================================================
# Session Configuration
# =============================================================================


@dataclass
class SessionConfig:
    """Configuration for WinAppDriver session."""
    
    # Application
    app_path: str
    app_arguments: str = ""
    
    # WinAppDriver
    winappdriver_url: str = "http://127.0.0.1:4723"
    
    # Capabilities
    platform_name: str = "Windows"
    device_name: str = "WindowsPC"
    
    # Timeouts
    implicit_wait: float = 10.0
    command_timeout: float = 120.0
    new_command_timeout: float = 120.0
    
    # Debug
    debug_connect_to_running_app: bool = False
    
    def to_capabilities(self) -> Dict[str, Any]:
        """Convert to WinAppDriver capabilities dict."""
        caps = {
            "platformName": self.platform_name,
            "deviceName": self.device_name,
            "newCommandTimeout": self.new_command_timeout,
        }
        
        if self.debug_connect_to_running_app:
            # Connect to already running app
            caps["appTopLevelWindow"] = self._get_app_window_handle()
        else:
            # Launch new app
            caps["app"] = self.app_path
            if self.app_arguments:
                caps["appArguments"] = self.app_arguments
        
        return caps
    
    def _get_app_window_handle(self) -> str:
        """Get window handle for running app (for debugging)."""
        # This would use pywinauto or similar to find the window
        raise NotImplementedError("Debug connection not implemented")


# =============================================================================
# Session Manager
# =============================================================================


class SessionManager:
    """
    Manages WinAppDriver sessions and application lifecycle.
    
    Usage:
        manager = SessionManager(config)
        
        with manager.session() as driver:
            # Use driver to interact with app
            driver.find_element("accessibility id", "MainWindow")
    """
    
    def __init__(self, config: Optional[SessionConfig] = None):
        """
        Initialize session manager.
        
        Args:
            config: Session configuration
        """
        self.config = config
        self._driver: Optional[Any] = None
        self._winappdriver_process: Optional[subprocess.Popen] = None
        self._app_process: Optional[psutil.Process] = None
    
    @property
    def driver(self) -> Any:
        """Get current driver instance."""
        if self._driver is None:
            raise RuntimeError("No active session")
        return self._driver
    
    @property
    def is_session_active(self) -> bool:
        """Check if session is currently active."""
        return self._driver is not None
    
    # -------------------------------------------------------------------------
    # WinAppDriver Management
    # -------------------------------------------------------------------------
    
    def is_winappdriver_running(self) -> bool:
        """Check if WinAppDriver is running."""
        if not HAS_PSUTIL:
            # Fallback: try to connect
            try:
                import requests
                response = requests.get(
                    f"{self.config.winappdriver_url if self.config else 'http://127.0.0.1:4723'}/status",
                    timeout=2
                )
                return response.status_code == 200
            except Exception:
                return False
        
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'WinAppDriver.exe':
                return True
        return False
    
    def start_winappdriver(
        self,
        path: str = r"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe",
        port: int = 4723
    ) -> bool:
        """
        Start WinAppDriver if not already running.
        
        Args:
            path: Path to WinAppDriver.exe
            port: Port to run on
            
        Returns:
            True if started successfully or already running
        """
        if self.is_winappdriver_running():
            logger.info("WinAppDriver already running")
            return True
        
        if not Path(path).exists():
            logger.error(f"WinAppDriver not found: {path}")
            return False
        
        try:
            self._winappdriver_process = subprocess.Popen(
                [path, f"127.0.0.1", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait for it to start
            time.sleep(2)
            
            if self._winappdriver_process.poll() is None:
                logger.info(f"WinAppDriver started on port {port}")
                return True
            else:
                logger.error("WinAppDriver failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start WinAppDriver: {e}")
            return False
    
    def stop_winappdriver(self):
        """Stop WinAppDriver if we started it."""
        if self._winappdriver_process:
            self._winappdriver_process.terminate()
            self._winappdriver_process = None
            logger.info("WinAppDriver stopped")
    
    # -------------------------------------------------------------------------
    # Session Management
    # -------------------------------------------------------------------------
    
    def create_session(self, config: Optional[SessionConfig] = None) -> Any:
        """
        Create a new WinAppDriver session.
        
        Args:
            config: Session configuration (uses default if not provided)
            
        Returns:
            WebDriver instance
        """
        config = config or self.config
        if config is None:
            raise ValueError("No session configuration provided")
        
        try:
            from appium import webdriver
            from appium.options.common import AppiumOptions
            
            options = AppiumOptions()
            for key, value in config.to_capabilities().items():
                options.set_capability(key, value)
            
            self._driver = webdriver.Remote(
                command_executor=config.winappdriver_url,
                options=options
            )
            
            self._driver.implicitly_wait(config.implicit_wait)
            logger.info("Session created successfully")
            
            return self._driver
            
        except ImportError:
            # Fallback for older appium-python-client versions
            from selenium import webdriver as selenium_webdriver
            
            self._driver = selenium_webdriver.Remote(
                command_executor=config.winappdriver_url,
                desired_capabilities=config.to_capabilities()
            )
            
            self._driver.implicitly_wait(config.implicit_wait)
            logger.info("Session created successfully (legacy mode)")
            
            return self._driver
    
    def close_session(self):
        """Close the current session."""
        if self._driver:
            try:
                self._driver.quit()
                logger.info("Session closed")
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
            finally:
                self._driver = None
    
    @contextmanager
    def session(self, config: Optional[SessionConfig] = None):
        """
        Context manager for session lifecycle.
        
        Usage:
            with manager.session() as driver:
                driver.find_element(...)
        """
        try:
            driver = self.create_session(config)
            yield driver
        finally:
            self.close_session()
    
    # -------------------------------------------------------------------------
    # Application Helpers
    # -------------------------------------------------------------------------
    
    def wait_for_app_ready(self, timeout: float = 30.0) -> bool:
        """
        Wait for application to be ready.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if app is ready
        """
        if not self._driver:
            return False
        
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                # Try to find main window
                self._driver.find_element("accessibility id", "MainWindow")
                return True
            except Exception:
                time.sleep(0.5)
        
        return False
    
    def restart_app(self) -> bool:
        """Restart the application."""
        self.close_session()
        time.sleep(1)
        self.create_session()
        return self.wait_for_app_ready()
    
    def close_app(self):
        """Close the application."""
        if self._driver:
            try:
                # Try graceful close first
                self._driver.find_element("accessibility id", "CloseButton").click()
                time.sleep(1)
            except Exception:
                pass
        
        self.close_session()


# =============================================================================
# Fixtures
# =============================================================================


def create_session_manager(
    app_path: str,
    winappdriver_url: str = "http://127.0.0.1:4723"
) -> SessionManager:
    """
    Create a session manager with the given configuration.
    
    Args:
        app_path: Path to application executable
        winappdriver_url: WinAppDriver URL
        
    Returns:
        Configured SessionManager
    """
    config = SessionConfig(
        app_path=app_path,
        winappdriver_url=winappdriver_url
    )
    return SessionManager(config)


# =============================================================================
# Mock Session for Testing
# =============================================================================


class MockDriver:
    """Mock driver for testing when WinAppDriver is not available."""
    
    def __init__(self):
        self._elements = {}
        self._implicit_wait = 0
    
    def find_element(self, by: str, value: str):
        """Mock find element."""
        return MockElement(value)
    
    def find_elements(self, by: str, value: str):
        """Mock find elements."""
        return [MockElement(value)]
    
    def implicitly_wait(self, seconds: float):
        """Set implicit wait."""
        self._implicit_wait = seconds
    
    def save_screenshot(self, path: str):
        """Mock save screenshot."""
        logger.info(f"Mock screenshot saved: {path}")
    
    def quit(self):
        """Mock quit."""
        logger.info("Mock driver quit")


class MockElement:
    """Mock element for testing."""
    
    def __init__(self, identifier: str):
        self.identifier = identifier
        self._text = f"Mock text for {identifier}"
        self._displayed = True
        self._enabled = True
    
    @property
    def text(self) -> str:
        return self._text
    
    def is_displayed(self) -> bool:
        return self._displayed
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def click(self):
        logger.info(f"Mock click: {self.identifier}")
    
    def send_keys(self, text: str):
        logger.info(f"Mock send_keys to {self.identifier}: {text}")
    
    def clear(self):
        logger.info(f"Mock clear: {self.identifier}")
    
    def get_attribute(self, name: str) -> str:
        return f"mock_{name}"


class MockSessionManager(SessionManager):
    """Mock session manager for testing without WinAppDriver."""
    
    def create_session(self, config: Optional[SessionConfig] = None) -> MockDriver:
        """Create mock session."""
        self._driver = MockDriver()
        logger.info("Mock session created")
        return self._driver
    
    def is_winappdriver_running(self) -> bool:
        """Always return True for mock."""
        return True
    
    def start_winappdriver(self, **kwargs) -> bool:
        """Mock start."""
        return True
