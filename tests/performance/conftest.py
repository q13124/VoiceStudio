"""
Performance Test Configuration and Fixtures.

Provides fixtures for performance testing including:
- Performance benchmarks
- Load testing utilities
- Resource monitoring
- Report generation
"""

import json
import os
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest

from .performance_test_utils import (
    LoadTester,
    PerformanceBenchmark,
    PerformanceMetrics,
    PerformanceTimer,
)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / ".buildlogs" / "performance"
REPORT_DIR = OUTPUT_DIR / "reports"
BASELINES_FILE = OUTPUT_DIR / "baselines.json"


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (> 10s)")
    config.addinivalue_line("markers", "stress: marks tests as stress tests")
    config.addinivalue_line("markers", "load: marks tests as load tests")
    config.addinivalue_line("markers", "benchmark: marks tests as benchmarks")
    config.addinivalue_line("markers", "api: marks tests as API performance tests")
    config.addinivalue_line("markers", "engine: marks tests as engine performance tests")
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--perf-report",
        action="store_true",
        default=False,
        help="Generate performance report after tests",
    )
    parser.addoption(
        "--perf-baseline",
        action="store",
        default=None,
        help="Path to baseline file for comparison",
    )
    parser.addoption(
        "--save-baseline",
        action="store_true",
        default=False,
        help="Save results as new baseline",
    )


# =============================================================================
# Performance Report Collection
# =============================================================================

class PerformanceCollector:
    """Collects performance metrics during test run."""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def add_result(self, name: str, metrics: PerformanceMetrics, passed: bool = True):
        """Add a performance result."""
        self.results.append({
            "name": name,
            "passed": passed,
            "metrics": asdict(metrics),
            "timestamp": datetime.now().isoformat(),
        })
    
    def add_custom_result(self, name: str, elapsed: float, **kwargs):
        """Add a custom performance result."""
        self.results.append({
            "name": name,
            "elapsed": elapsed,
            "timestamp": datetime.now().isoformat(),
            **kwargs,
        })
    
    def generate_report(self) -> Dict:
        """Generate performance report."""
        successful = [r for r in self.results if r.get("passed", True)]
        failed = [r for r in self.results if not r.get("passed", True)]
        
        # Calculate summary statistics
        all_times = []
        for r in self.results:
            if "metrics" in r:
                all_times.append(r["metrics"]["avg_time"])
            elif "elapsed" in r:
                all_times.append(r["elapsed"])
        
        return {
            "generated_at": datetime.now().isoformat(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_tests": len(self.results),
            "passed": len(successful),
            "failed": len(failed),
            "summary": {
                "avg_time": sum(all_times) / len(all_times) if all_times else 0,
                "min_time": min(all_times) if all_times else 0,
                "max_time": max(all_times) if all_times else 0,
            },
            "results": self.results,
        }
    
    def save_report(self, filepath: Path):
        """Save report to file."""
        report = self.generate_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        return filepath


# Global collector instance
_collector = PerformanceCollector()


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def performance_collector():
    """Get the performance collector."""
    _collector.start_time = datetime.now()
    yield _collector
    _collector.end_time = datetime.now()


@pytest.fixture
def perf_timer():
    """Create a performance timer."""
    def _timer(name: str = "operation"):
        return PerformanceTimer(name)
    return _timer


@pytest.fixture
def perf_benchmark():
    """Create a performance benchmark."""
    def _benchmark(name: str):
        return PerformanceBenchmark(name)
    return _benchmark


@pytest.fixture
def load_tester():
    """Create a load tester."""
    def _tester(name: str = "load_test"):
        return LoadTester(name)
    return _tester


@pytest.fixture
def assert_performance():
    """Assert performance meets requirements."""
    def _assert(
        elapsed: float,
        max_time: float,
        name: str = "operation",
        record: bool = True,
    ):
        passed = elapsed <= max_time
        if record:
            _collector.add_custom_result(
                name=name,
                elapsed=elapsed,
                max_time=max_time,
                passed=passed,
            )
        assert passed, f"{name} took {elapsed:.3f}s (max: {max_time:.3f}s)"
    return _assert


@pytest.fixture
def record_performance():
    """Record performance metrics."""
    def _record(name: str, metrics: PerformanceMetrics, passed: bool = True):
        _collector.add_result(name, metrics, passed)
    return _record


@pytest.fixture
def baselines():
    """Load performance baselines."""
    if BASELINES_FILE.exists():
        with open(BASELINES_FILE) as f:
            return json.load(f)
    return {}


# =============================================================================
# Session Hooks
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def performance_report_session(request, performance_collector):
    """Generate performance report at end of session if requested."""
    yield
    
    if request.config.getoption("--perf-report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPORT_DIR / f"performance_report_{timestamp}.json"
        performance_collector.save_report(report_path)
        print(f"\nPerformance report saved to: {report_path}")
    
    if request.config.getoption("--save-baseline"):
        performance_collector.save_report(BASELINES_FILE)
        print(f"\nBaseline saved to: {BASELINES_FILE}")


# =============================================================================
# Resource Monitoring Fixtures
# =============================================================================

@pytest.fixture
def memory_monitor():
    """Monitor memory usage during test."""
    try:
        import psutil
        
        class MemoryMonitor:
            def __init__(self):
                self.process = psutil.Process()
                self.start_memory: Optional[float] = None
                self.peak_memory: float = 0
                self.samples: List[float] = []
            
            def start(self):
                self.start_memory = self.process.memory_info().rss / 1024 / 1024
                self.samples = [self.start_memory]
            
            def sample(self):
                current = self.process.memory_info().rss / 1024 / 1024
                self.samples.append(current)
                self.peak_memory = max(self.peak_memory, current)
            
            def get_stats(self) -> Dict:
                if not self.samples:
                    return {}
                return {
                    "start_mb": self.start_memory,
                    "end_mb": self.samples[-1] if self.samples else 0,
                    "peak_mb": self.peak_memory,
                    "delta_mb": (self.samples[-1] - self.start_memory) 
                        if self.start_memory else 0,
                }
        
        return MemoryMonitor()
    except ImportError:
        pytest.skip("psutil not available for memory monitoring")


@pytest.fixture
def cpu_monitor():
    """Monitor CPU usage during test."""
    try:
        import psutil
        
        class CPUMonitor:
            def __init__(self):
                self.process = psutil.Process()
                self.samples: List[float] = []
            
            def sample(self):
                self.samples.append(self.process.cpu_percent())
            
            def get_stats(self) -> Dict:
                if not self.samples:
                    return {}
                return {
                    "avg_percent": sum(self.samples) / len(self.samples),
                    "max_percent": max(self.samples),
                    "samples": len(self.samples),
                }
        
        return CPUMonitor()
    except ImportError:
        pytest.skip("psutil not available for CPU monitoring")


# =============================================================================
# Helper Functions
# =============================================================================

def pytest_report_header(config):
    """Add custom header info to test report."""
    return [
        "VoiceStudio Performance Tests",
        f"  Output: {OUTPUT_DIR}",
        f"  Reports: {REPORT_DIR}",
    ]
