"""
Pytest configuration and fixtures for VoiceStudio Quantum+ test suite.
Provides shared fixtures and test utilities for all test modules.

Enhanced with:
- Comprehensive test markers
- Configuration management
- Output directory organization
- Test reporting hooks
"""

# Standard path setup - MUST be first
import sys
from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, Generator, Any, List, Optional

# Add project root to path (single canonical location)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

OUTPUT_DIR = project_root / ".buildlogs" / "tests"
RESULTS_DIR = OUTPUT_DIR / "results"
COVERAGE_DIR = OUTPUT_DIR / "coverage"


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and output directories."""
    # Register custom markers
    markers = [
        "unit: marks tests as unit tests",
        "integration: marks tests as integration tests",
        "e2e: marks tests as end-to-end tests",
        "ui: marks tests as UI tests",
        "performance: marks tests as performance tests",
        "contract: marks tests as contract tests",
        "slow: marks tests as slow (> 10s)",
        "smoke: marks tests as smoke tests",
        "regression: marks tests as regression tests",
        "flaky: marks tests as potentially flaky",
        "backend: marks tests as backend tests",
        "engine: marks tests as engine tests",
        "audio: marks tests as audio processing tests",
        "api: marks tests as API tests",
        "skip_ci: marks tests to skip in CI",
        "requires_backend: marks tests that require running backend",
        "requires_gpu: marks tests that require GPU",
        "requires_model: marks tests that require model download",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )
    parser.addoption(
        "--run-flaky",
        action="store_true",
        default=False,
        help="Run flaky tests",
    )
    parser.addoption(
        "--skip-backend",
        action="store_true",
        default=False,
        help="Skip tests requiring backend",
    )
    parser.addoption(
        "--test-report",
        action="store_true",
        default=False,
        help="Generate test report JSON",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on options."""
    skip_slow = pytest.mark.skip(reason="Need --run-slow option to run")
    skip_flaky = pytest.mark.skip(reason="Need --run-flaky option to run")
    skip_backend = pytest.mark.skip(reason="Skipped with --skip-backend")
    skip_ci = pytest.mark.skip(reason="Skipped in CI")
    
    in_ci = os.environ.get("CI", "false").lower() == "true"
    
    for item in items:
        if "slow" in item.keywords and not config.getoption("--run-slow"):
            item.add_marker(skip_slow)
        if "flaky" in item.keywords and not config.getoption("--run-flaky"):
            item.add_marker(skip_flaky)
        if "requires_backend" in item.keywords and config.getoption("--skip-backend"):
            item.add_marker(skip_backend)
        if "skip_ci" in item.keywords and in_ci:
            item.add_marker(skip_ci)


# =============================================================================
# Test Result Collection
# =============================================================================

class TestResultCollector:
    """Collects test results for reporting."""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def add_result(
        self,
        name: str,
        outcome: str,
        duration: float,
        markers: List[str],
        error: Optional[str] = None,
    ):
        self.results.append({
            "name": name,
            "outcome": outcome,
            "duration": duration,
            "markers": markers,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_summary(self) -> Dict:
        passed = sum(1 for r in self.results if r["outcome"] == "passed")
        failed = sum(1 for r in self.results if r["outcome"] == "failed")
        skipped = sum(1 for r in self.results if r["outcome"] == "skipped")
        
        return {
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": passed / len(self.results) * 100 if self.results else 0,
            "total_duration": sum(r["duration"] for r in self.results),
        }
    
    def save_report(self, filepath: Path):
        report = {
            "generated_at": datetime.now().isoformat(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "summary": self.get_summary(),
            "results": self.results,
        }
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)


_collector = TestResultCollector()


@pytest.fixture(scope="session", autouse=True)
def test_session_setup(request):
    """Session-level setup and teardown."""
    _collector.start_time = datetime.now()
    yield
    _collector.end_time = datetime.now()
    
    if request.config.getoption("--test-report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = RESULTS_DIR / f"test_report_{timestamp}.json"
        _collector.save_report(report_path)
        print(f"\nTest report saved: {report_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect test results."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        markers = [m.name for m in item.iter_markers()]
        _collector.add_result(
            name=item.nodeid,
            outcome=report.outcome,
            duration=report.duration,
            markers=markers,
            error=str(report.longrepr) if report.failed else None,
        )


def pytest_report_header(config):
    """Add custom header to test report."""
    return [
        "VoiceStudio Test Suite",
        f"  Output: {OUTPUT_DIR}",
        f"  Python: {sys.version.split()[0]}",
    ]


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Return the project root directory."""
    return project_root


@pytest.fixture(scope="session")
def test_data_dir(project_root_path: Path) -> Path:
    """Return the test data directory."""
    return project_root_path / "tests" / "test_data"


@pytest.fixture(scope="function")
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test files."""
    return tmp_path


@pytest.fixture(scope="session")
def sample_audio_path(test_data_dir: Path) -> Path:
    """Return path to sample audio file for testing."""
    audio_path = test_data_dir / "audio" / "sample.wav"
    if not audio_path.exists():
        # Create placeholder if doesn't exist
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Sample audio not found at {audio_path}, tests may fail")
    return audio_path


@pytest.fixture(scope="session")
def sample_profile_data(test_data_dir: Path) -> dict:
    """Return sample voice profile data for testing."""
    return {
        "id": "test-profile-1",
        "name": "Test Profile",
        "language": "en",
        "gender": "neutral",
        "age": "adult"
    }


@pytest.fixture(scope="function")
def mock_backend_url() -> str:
    """Return mock backend URL for testing."""
    return "http://localhost:8000"


@pytest.fixture(scope="function", autouse=True)
def reset_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment variables before each test."""
    # Clear any test-specific environment variables
    test_vars = ["VOICESTUDIO_TEST_MODE", "VOICESTUDIO_DEBUG"]
    for var in test_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture(scope="function")
def caplog_context(caplog: pytest.LogCaptureFixture) -> Generator[None, None, None]:
    """Provide logging context for tests."""
    with caplog.at_level(logging.DEBUG):
        yield


# Import test utilities (lazy import to avoid circular dependencies)
try:
    from tests.test_utils import (
        TestDataManager,
        MockBackendClient,
        TestAssertions,
        create_mock_engine,
        create_mock_api_response,
        create_temp_audio_file,
        cleanup_temp_files,
    )
except ImportError:
    # Fallback if test_utils not available
    TestDataManager = None
    MockBackendClient = None
    TestAssertions = None
    create_mock_engine = None
    create_mock_api_response = None
    create_temp_audio_file = None
    cleanup_temp_files = None


@pytest.fixture(scope="function")
def test_data_manager(temp_dir: Path):
    """Provide test data manager for test file creation."""
    if TestDataManager is None:
        pytest.skip("TestDataManager not available")
    manager = TestDataManager(base_dir=temp_dir)
    yield manager
    manager.cleanup()


@pytest.fixture(scope="function")
def mock_backend_client():
    """Provide mock backend client for testing."""
    if MockBackendClient is None:
        pytest.skip("MockBackendClient not available")
    return MockBackendClient()


@pytest.fixture(scope="function")
def test_assertions():
    """Provide enhanced test assertions."""
    if TestAssertions is None:
        pytest.skip("TestAssertions not available")
    return TestAssertions()


@pytest.fixture(scope="function")
def mock_engine():
    """Provide mock engine for testing."""
    if create_mock_engine is None:
        pytest.skip("create_mock_engine not available")
    return create_mock_engine()


@pytest.fixture(scope="function")
def temp_audio_file():
    """Provide temporary audio file for testing."""
    if create_temp_audio_file is None or cleanup_temp_files is None:
        pytest.skip("Audio file utilities not available")
    audio_file = create_temp_audio_file()
    yield audio_file
    cleanup_temp_files(audio_file.parent)


# Markers for test categorization
pytest_plugins = []

