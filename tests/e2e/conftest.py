"""
E2E Test Configuration and Fixtures.

Provides pytest fixtures for end-to-end testing including:
- Application session management
- Backend availability checks
- Screenshot capture on failure
- Test data generation
"""

import logging
import os
import sys
from pathlib import Path
from typing import Generator, Optional

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.e2e.framework.base import E2EConfig, E2ETestBase
from tests.e2e.framework.session import (
    SessionConfig,
    SessionManager,
    MockSessionManager,
    create_session_manager,
)
from tests.e2e.framework.helpers import (
    ScreenshotHelper,
    TestDataHelper,
    PerformanceTimer,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


def pytest_addoption(parser):
    """Add E2E-specific command line options."""
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to VoiceStudio application executable"
    )
    parser.addoption(
        "--backend-url",
        action="store",
        default="http://localhost:8000",
        help="Backend API URL"
    )
    parser.addoption(
        "--winappdriver-url",
        action="store",
        default="http://127.0.0.1:4723",
        help="WinAppDriver URL"
    )
    parser.addoption(
        "--use-mock-driver",
        action="store_true",
        default=False,
        help="Use mock driver instead of real WinAppDriver"
    )
    parser.addoption(
        "--capture-screenshots",
        action="store_true",
        default=True,
        help="Capture screenshots on test failure"
    )
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run E2E tests"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "requires_app: mark test as requiring the application"
    )
    config.addinivalue_line(
        "markers", "requires_backend: mark test as requiring the backend"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "wizard: mark test as a wizard workflow test"
    )
    config.addinivalue_line(
        "markers", "synthesis: mark test as a synthesis workflow test"
    )
    config.addinivalue_line(
        "markers", "project: mark test as a project workflow test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance benchmark test"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as a UI automation test"
    )


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def e2e_config(request) -> E2EConfig:
    """Provide E2E configuration."""
    config = E2EConfig.from_env()
    
    # Override with command line options
    if app_path := request.config.getoption("--app-path"):
        config.app_path = Path(app_path)
    if backend_url := request.config.getoption("--backend-url"):
        config.backend_url = backend_url
        
    return config


@pytest.fixture(scope="session")
def session_config(e2e_config, request) -> SessionConfig:
    """Provide session configuration."""
    winappdriver_url = request.config.getoption("--winappdriver-url")
    
    return SessionConfig(
        app_path=str(e2e_config.app_path.absolute()),
        winappdriver_url=winappdriver_url
    )


# =============================================================================
# Session Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def session_manager(session_config, request) -> SessionManager:
    """
    Provide session manager for the test session.
    
    Uses mock driver if --use-mock-driver is specified or
    if WinAppDriver is not available.
    """
    use_mock = request.config.getoption("--use-mock-driver")
    
    if use_mock:
        logger.info("Using mock driver")
        return MockSessionManager(session_config)
    
    manager = SessionManager(session_config)
    
    # Check if WinAppDriver is available
    if not manager.is_winappdriver_running():
        logger.warning(
            "WinAppDriver not running. Attempting to start..."
        )
        if not manager.start_winappdriver():
            logger.warning("Could not start WinAppDriver. Using mock driver.")
            return MockSessionManager(session_config)
    
    yield manager
    
    # Cleanup
    manager.stop_winappdriver()


@pytest.fixture(scope="function")
def app_session(session_manager, session_config, request):
    """
    Provide an application session for each test.
    
    Creates a new session and closes it after the test.
    Captures screenshots on failure if configured.
    """
    driver = None
    
    try:
        driver = session_manager.create_session(session_config)
        
        # Wait for app to be ready
        if not session_manager.wait_for_app_ready():
            pytest.skip("Application did not become ready")
        
        yield driver
        
    except Exception as e:
        logger.error(f"Session error: {e}")
        raise
        
    finally:
        # Capture screenshot on failure
        if request.node.rep_call and request.node.rep_call.failed:
            if request.config.getoption("--capture-screenshots"):
                screenshot_helper = ScreenshotHelper(
                    Path(".buildlogs/e2e/screenshots")
                )
                screenshot_helper.capture_on_failure(
                    driver, request.node.name
                )
        
        session_manager.close_session()


@pytest.fixture
def mock_session():
    """Provide a mock session for testing without real app."""
    manager = MockSessionManager()
    driver = manager.create_session()
    yield driver
    manager.close_session()


# =============================================================================
# Backend Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def backend_available(e2e_config) -> bool:
    """Check if backend is available for the test session."""
    import requests
    
    try:
        response = requests.get(
            f"{e2e_config.backend_url}/health",
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture
def require_backend(backend_available):
    """Skip test if backend is not available."""
    if not backend_available:
        pytest.skip("Backend not available")


@pytest.fixture
def api_client(e2e_config, backend_available):
    """Provide an API client for backend interactions."""
    import requests
    
    if not backend_available:
        pytest.skip("Backend not available")
    
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.session = requests.Session()
        
        def get(self, path: str, **kwargs):
            return self.session.get(f"{self.base_url}{path}", **kwargs)
        
        def post(self, path: str, **kwargs):
            return self.session.post(f"{self.base_url}{path}", **kwargs)
        
        def put(self, path: str, **kwargs):
            return self.session.put(f"{self.base_url}{path}", **kwargs)
        
        def delete(self, path: str, **kwargs):
            return self.session.delete(f"{self.base_url}{path}", **kwargs)
    
    return APIClient(e2e_config.backend_url)


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def test_data() -> TestDataHelper:
    """Provide test data helper."""
    return TestDataHelper()


@pytest.fixture
def unique_name(test_data):
    """Generate a unique name for test artifacts."""
    return test_data.unique_name("E2ETest")


@pytest.fixture
def sample_text(test_data):
    """Provide sample text for synthesis testing."""
    return test_data.sample_text()


@pytest.fixture
def sample_project_config(test_data):
    """Provide sample project configuration."""
    return test_data.sample_project_config()


@pytest.fixture
def sample_voice_profile(test_data):
    """Provide sample voice profile data."""
    return test_data.sample_voice_profile()


# =============================================================================
# Screenshot Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def screenshot_helper(e2e_config) -> ScreenshotHelper:
    """Provide screenshot helper."""
    return ScreenshotHelper(e2e_config.screenshot_dir)


@pytest.fixture
def capture_screenshot(screenshot_helper, app_session):
    """Provide function to capture screenshots during test."""
    def _capture(name: str):
        return screenshot_helper.capture(app_session, name)
    return _capture


# =============================================================================
# Performance Fixtures
# =============================================================================


@pytest.fixture
def performance_timer():
    """Provide performance timer for measuring test operations."""
    return PerformanceTimer


@pytest.fixture
def timer():
    """Provide a started timer for the test."""
    timer = PerformanceTimer("Test")
    timer.start()
    yield timer
    timer.stop()


# =============================================================================
# Hooks
# =============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot on failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle E2E markers."""
    skip_e2e = pytest.mark.skip(
        reason="E2E tests skipped (use --run-e2e to run)"
    )
    skip_slow = pytest.mark.skip(
        reason="Slow tests skipped (use --run-slow to run)"
    )
    
    for item in items:
        # Skip E2E tests if not explicitly requested
        if "e2e" in item.keywords:
            if not config.getoption("--run-e2e", default=False):
                # Don't skip by default for E2E test directory
                pass
        
        # Add timeout for slow tests
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.timeout(300))
