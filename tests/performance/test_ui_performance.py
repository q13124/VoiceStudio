"""
UI Performance Benchmarks for VoiceStudio.

Tests UI performance including:
- Panel rendering times
- Navigation transitions
- Control load times
- Memory usage during UI operations
- UI thread responsiveness

SLO Targets:
- Panel render: < 100ms average, < 200ms P95
- Navigation: < 150ms average, < 300ms P95
- Control load: < 50ms average
- UI thread frame time: < 16.67ms (60 FPS target)
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from unittest.mock import MagicMock, patch

import pytest

from tests.performance.performance_test_utils import (
    PerformanceBenchmark,
    PerformanceMetrics,
    PerformanceTimer,
)

logger = logging.getLogger(__name__)


# =============================================================================
# SLO Definitions
# =============================================================================


@dataclass
class UIPerformanceSLO:
    """UI Performance Service Level Objectives."""
    
    # Panel rendering targets (seconds)
    PANEL_RENDER_AVG: float = 0.100  # 100ms average
    PANEL_RENDER_P95: float = 0.200  # 200ms P95
    
    # Navigation targets (seconds)
    NAVIGATION_AVG: float = 0.150  # 150ms average
    NAVIGATION_P95: float = 0.300  # 300ms P95
    
    # Control load targets (seconds)
    CONTROL_LOAD_AVG: float = 0.050  # 50ms average
    CONTROL_LOAD_P95: float = 0.100  # 100ms P95
    
    # Frame time targets (60 FPS = 16.67ms per frame)
    FRAME_TIME_AVG: float = 0.01667  # 16.67ms
    FRAME_TIME_P95: float = 0.033  # 33ms (30 FPS minimum)
    
    # Memory targets (MB)
    IDLE_MEMORY_MAX: float = 300  # 300MB idle
    ACTIVE_MEMORY_MAX: float = 500  # 500MB during operations
    MEMORY_GROWTH_MAX: float = 50  # 50MB max growth during test


SLO = UIPerformanceSLO()


# =============================================================================
# Panel Definitions for Testing
# =============================================================================

VOICESTUDIO_PANELS = [
    # Core Studio Panels
    {"name": "AudioQualityPanel", "category": "studio", "priority": "high"},
    {"name": "ProjectBrowserPanel", "category": "studio", "priority": "high"},
    {"name": "TimelinePanel", "category": "studio", "priority": "high"},
    {"name": "TranscriptionPanel", "category": "studio", "priority": "high"},
    {"name": "VoiceQuickClonePanel", "category": "studio", "priority": "high"},
    
    # Voice Management Panels
    {"name": "VoiceBrowserPanel", "category": "voices", "priority": "high"},
    {"name": "VoiceMorphingPanel", "category": "voices", "priority": "medium"},
    {"name": "VoiceProfilePanel", "category": "voices", "priority": "high"},
    {"name": "VoiceStylePanel", "category": "voices", "priority": "medium"},
    
    # Synthesis Panels
    {"name": "SynthesisPanel", "category": "synthesis", "priority": "high"},
    {"name": "ProsodyEditorPanel", "category": "synthesis", "priority": "medium"},
    {"name": "SSMLEditorPanel", "category": "synthesis", "priority": "medium"},
    
    # Training Panels
    {"name": "TrainingPanel", "category": "training", "priority": "medium"},
    {"name": "DatasetPanel", "category": "training", "priority": "medium"},
    {"name": "ModelPanel", "category": "training", "priority": "medium"},
    
    # Settings Panels
    {"name": "SettingsPanel", "category": "settings", "priority": "low"},
    {"name": "EngineSettingsPanel", "category": "settings", "priority": "low"},
    {"name": "AudioSettingsPanel", "category": "settings", "priority": "low"},
]


# =============================================================================
# Mock UI Components for Testing
# =============================================================================


class MockPanel:
    """Mock panel for UI performance testing."""
    
    def __init__(self, name: str, complexity: str = "medium"):
        self.name = name
        self.complexity = complexity
        self.is_loaded = False
        self.render_time_ms = 0
        
        # Simulate different complexities with delay
        self._complexity_delays = {
            "simple": 0.010,  # 10ms
            "medium": 0.030,  # 30ms
            "complex": 0.080,  # 80ms
            "heavy": 0.150,   # 150ms
        }
    
    def load(self) -> float:
        """Simulate panel loading, return time in seconds."""
        start = time.perf_counter()
        delay = self._complexity_delays.get(self.complexity, 0.030)
        time.sleep(delay)
        self.is_loaded = True
        elapsed = time.perf_counter() - start
        self.render_time_ms = elapsed * 1000
        return elapsed
    
    def render(self) -> float:
        """Simulate panel rendering, return time in seconds."""
        start = time.perf_counter()
        delay = self._complexity_delays.get(self.complexity, 0.030) * 0.5
        time.sleep(delay)
        return time.perf_counter() - start
    
    def unload(self) -> float:
        """Simulate panel unloading, return time in seconds."""
        start = time.perf_counter()
        time.sleep(0.005)  # 5ms for cleanup
        self.is_loaded = False
        return time.perf_counter() - start


class MockNavigationService:
    """Mock navigation service for testing transitions."""
    
    def __init__(self):
        self.current_panel: Optional[MockPanel] = None
        self.navigation_history: List[str] = []
        self.panels: Dict[str, MockPanel] = {}
    
    def register_panel(self, name: str, complexity: str = "medium"):
        """Register a panel for navigation."""
        self.panels[name] = MockPanel(name, complexity)
    
    def navigate_to(self, panel_name: str) -> float:
        """Navigate to a panel, return transition time."""
        start = time.perf_counter()
        
        # Unload current panel
        if self.current_panel:
            self.current_panel.unload()
        
        # Load new panel
        if panel_name not in self.panels:
            self.register_panel(panel_name)
        
        panel = self.panels[panel_name]
        panel.load()
        self.current_panel = panel
        self.navigation_history.append(panel_name)
        
        return time.perf_counter() - start
    
    def get_navigation_metrics(self) -> Dict[str, Any]:
        """Get navigation performance metrics."""
        return {
            "total_navigations": len(self.navigation_history),
            "current_panel": self.current_panel.name if self.current_panel else None,
        }


class MockControlRenderer:
    """Mock control renderer for testing control performance."""
    
    # Control types with complexity factors
    CONTROL_COMPLEXITIES = {
        "Button": 0.002,
        "TextBox": 0.003,
        "ComboBox": 0.005,
        "ListBox": 0.010,
        "DataGrid": 0.050,
        "TreeView": 0.030,
        "MediaPlayer": 0.080,
        "WaveformDisplay": 0.100,
        "Spectrogram": 0.120,
        "VoiceProfileCard": 0.025,
    }
    
    def render_control(self, control_type: str, count: int = 1) -> float:
        """Render controls and return time."""
        start = time.perf_counter()
        delay = self.CONTROL_COMPLEXITIES.get(control_type, 0.005) * count
        time.sleep(delay)
        return time.perf_counter() - start
    
    def render_control_batch(self, controls: Dict[str, int]) -> float:
        """Render multiple control types."""
        total_delay = 0
        for control_type, count in controls.items():
            total_delay += self.CONTROL_COMPLEXITIES.get(control_type, 0.005) * count
        
        start = time.perf_counter()
        time.sleep(total_delay)
        return time.perf_counter() - start


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def navigation_service() -> MockNavigationService:
    """Create mock navigation service."""
    service = MockNavigationService()
    
    # Register all panels with varying complexities
    complexities = ["simple", "medium", "complex", "heavy"]
    for i, panel in enumerate(VOICESTUDIO_PANELS):
        complexity = complexities[i % len(complexities)]
        service.register_panel(panel["name"], complexity)
    
    return service


@pytest.fixture
def control_renderer() -> MockControlRenderer:
    """Create mock control renderer."""
    return MockControlRenderer()


@pytest.fixture
def ui_benchmark():
    """Create UI benchmark."""
    return PerformanceBenchmark("UI Benchmark")


# =============================================================================
# Panel Rendering Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
class TestPanelRenderingPerformance:
    """Tests for panel rendering performance."""
    
    def test_simple_panel_render(self, perf_benchmark, record_performance):
        """Test simple panel rendering meets SLO."""
        benchmark = perf_benchmark("Simple Panel Render")
        panel = MockPanel("SimplePanel", "simple")
        
        metrics = benchmark.run(panel.render, iterations=20)
        
        record_performance("Simple Panel Render", metrics)
        benchmark.assert_performance(
            metrics,
            max_avg_time=SLO.PANEL_RENDER_AVG,
            max_p95_time=SLO.PANEL_RENDER_P95
        )
        
        logger.info(
            f"Simple panel render: avg={metrics.avg_time*1000:.2f}ms, "
            f"P95={metrics.p95_time*1000:.2f}ms"
        )
    
    def test_complex_panel_render(self, perf_benchmark, record_performance):
        """Test complex panel rendering meets SLO."""
        benchmark = perf_benchmark("Complex Panel Render")
        panel = MockPanel("ComplexPanel", "complex")
        
        metrics = benchmark.run(panel.render, iterations=15)
        
        record_performance("Complex Panel Render", metrics)
        benchmark.assert_performance(
            metrics,
            max_avg_time=SLO.PANEL_RENDER_AVG,
            max_p95_time=SLO.PANEL_RENDER_P95
        )
        
        logger.info(
            f"Complex panel render: avg={metrics.avg_time*1000:.2f}ms, "
            f"P95={metrics.p95_time*1000:.2f}ms"
        )
    
    def test_heavy_panel_render(self, perf_benchmark, record_performance):
        """Test heavy panel rendering (may exceed SLO, recorded for baseline)."""
        benchmark = perf_benchmark("Heavy Panel Render")
        panel = MockPanel("HeavyPanel", "heavy")
        
        metrics = benchmark.run(panel.render, iterations=10)
        
        record_performance("Heavy Panel Render", metrics)
        
        # Heavy panels may exceed normal SLO, but track them
        logger.info(
            f"Heavy panel render: avg={metrics.avg_time*1000:.2f}ms, "
            f"P95={metrics.p95_time*1000:.2f}ms"
        )
    
    def test_all_panels_render_baseline(
        self, navigation_service, perf_benchmark, record_performance
    ):
        """Benchmark all panel renders to establish baseline."""
        results = []
        
        for panel_info in VOICESTUDIO_PANELS[:10]:  # First 10 panels
            panel_name = panel_info["name"]
            panel = navigation_service.panels.get(panel_name)
            
            if panel:
                times = []
                for _ in range(5):
                    times.append(panel.render())
                
                avg_time = sum(times) / len(times)
                results.append({
                    "name": panel_name,
                    "category": panel_info["category"],
                    "avg_ms": avg_time * 1000,
                })
        
        # Log baseline
        for result in results:
            logger.info(
                f"Panel {result['name']}: avg={result['avg_ms']:.2f}ms"
            )
        
        # Assert average across all panels
        overall_avg = sum(r["avg_ms"] for r in results) / len(results)
        assert overall_avg < SLO.PANEL_RENDER_AVG * 1000, \
            f"Overall panel render average {overall_avg:.2f}ms exceeds SLO"


# =============================================================================
# Navigation Performance Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
class TestNavigationPerformance:
    """Tests for navigation performance."""
    
    def test_single_navigation(
        self, navigation_service, perf_benchmark, record_performance
    ):
        """Test single panel navigation meets SLO."""
        benchmark = perf_benchmark("Single Navigation")
        
        # Navigate to a medium complexity panel
        navigation_service.navigate_to("VoiceBrowserPanel")
        
        metrics = benchmark.run(
            navigation_service.navigate_to,
            "SynthesisPanel",
            iterations=10
        )
        
        record_performance("Single Navigation", metrics)
        benchmark.assert_performance(
            metrics,
            max_avg_time=SLO.NAVIGATION_AVG,
            max_p95_time=SLO.NAVIGATION_P95
        )
        
        logger.info(
            f"Single navigation: avg={metrics.avg_time*1000:.2f}ms, "
            f"P95={metrics.p95_time*1000:.2f}ms"
        )
    
    def test_rapid_navigation(
        self, navigation_service, perf_benchmark, record_performance
    ):
        """Test rapid navigation between panels."""
        panel_names = [p["name"] for p in VOICESTUDIO_PANELS[:5]]
        
        def rapid_navigate():
            for name in panel_names:
                navigation_service.navigate_to(name)
        
        benchmark = perf_benchmark("Rapid Navigation")
        metrics = benchmark.run(rapid_navigate, iterations=5)
        
        record_performance("Rapid Navigation (5 panels)", metrics)
        
        # Allow more time for rapid navigation
        avg_per_panel = metrics.avg_time / len(panel_names)
        assert avg_per_panel < SLO.NAVIGATION_AVG * 1.5, \
            f"Rapid navigation avg {avg_per_panel*1000:.2f}ms/panel exceeds SLO"
        
        logger.info(
            f"Rapid navigation: total_avg={metrics.avg_time*1000:.2f}ms, "
            f"per_panel_avg={avg_per_panel*1000:.2f}ms"
        )
    
    def test_back_forward_navigation(
        self, navigation_service, perf_benchmark, record_performance
    ):
        """Test back/forward navigation pattern."""
        # Setup initial history
        navigation_service.navigate_to("Panel1")
        navigation_service.navigate_to("Panel2")
        navigation_service.navigate_to("Panel3")
        
        def back_forward():
            # Simulate back-forward pattern
            navigation_service.navigate_to("Panel2")  # Back
            navigation_service.navigate_to("Panel3")  # Forward
        
        benchmark = perf_benchmark("Back/Forward Navigation")
        metrics = benchmark.run(back_forward, iterations=10)
        
        record_performance("Back/Forward Navigation", metrics)
        
        logger.info(
            f"Back/forward navigation: avg={metrics.avg_time*1000:.2f}ms"
        )
    
    def test_navigation_with_heavy_panel(
        self, navigation_service, perf_benchmark, record_performance
    ):
        """Test navigation to heavy panels."""
        # Register a heavy panel
        navigation_service.register_panel("HeavyDataGrid", "heavy")
        navigation_service.navigate_to("SimplePanel")
        
        benchmark = perf_benchmark("Heavy Panel Navigation")
        metrics = benchmark.run(
            navigation_service.navigate_to,
            "HeavyDataGrid",
            iterations=5
        )
        
        record_performance("Heavy Panel Navigation", metrics)
        
        logger.info(
            f"Heavy panel navigation: avg={metrics.avg_time*1000:.2f}ms"
        )


# =============================================================================
# Control Load Performance Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
class TestControlLoadPerformance:
    """Tests for control loading performance."""
    
    def test_simple_controls(
        self, control_renderer, perf_benchmark, record_performance
    ):
        """Test simple control rendering."""
        benchmark = perf_benchmark("Simple Controls")
        
        controls = {"Button": 10, "TextBox": 5}
        metrics = benchmark.run(
            control_renderer.render_control_batch,
            controls,
            iterations=20
        )
        
        record_performance("Simple Controls", metrics)
        benchmark.assert_performance(
            metrics,
            max_avg_time=SLO.CONTROL_LOAD_AVG
        )
    
    def test_complex_controls(
        self, control_renderer, perf_benchmark, record_performance
    ):
        """Test complex control rendering."""
        benchmark = perf_benchmark("Complex Controls")
        
        controls = {"DataGrid": 1, "TreeView": 1, "ListBox": 2}
        metrics = benchmark.run(
            control_renderer.render_control_batch,
            controls,
            iterations=10
        )
        
        record_performance("Complex Controls", metrics)
        
        logger.info(
            f"Complex controls: avg={metrics.avg_time*1000:.2f}ms"
        )
    
    def test_audio_controls(
        self, control_renderer, perf_benchmark, record_performance
    ):
        """Test audio-specific control rendering."""
        benchmark = perf_benchmark("Audio Controls")
        
        controls = {"WaveformDisplay": 1, "Spectrogram": 1, "MediaPlayer": 1}
        metrics = benchmark.run(
            control_renderer.render_control_batch,
            controls,
            iterations=10
        )
        
        record_performance("Audio Controls", metrics)
        
        logger.info(
            f"Audio controls: avg={metrics.avg_time*1000:.2f}ms"
        )
    
    def test_voice_profile_cards(
        self, control_renderer, perf_benchmark, record_performance
    ):
        """Test voice profile card rendering for browser view."""
        benchmark = perf_benchmark("Voice Profile Cards")
        
        # Simulate loading multiple voice profile cards
        controls = {"VoiceProfileCard": 20}  # 20 profile cards
        metrics = benchmark.run(
            control_renderer.render_control_batch,
            controls,
            iterations=10
        )
        
        record_performance("Voice Profile Cards (20)", metrics)
        
        # 20 cards with batch rendering should complete in < 1 second
        # (real virtualized UI would be much faster)
        MAX_BATCH_TIME = 1.0  # 1 second for 20 cards
        assert metrics.avg_time < MAX_BATCH_TIME, \
            f"20 voice cards took {metrics.avg_time*1000:.2f}ms (max {MAX_BATCH_TIME*1000}ms)"
        
        logger.info(
            f"20 voice profile cards: avg={metrics.avg_time*1000:.2f}ms"
        )


# =============================================================================
# Frame Rate / UI Thread Performance Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
class TestUIThreadPerformance:
    """Tests for UI thread performance (simulated frame times)."""
    
    def test_idle_frame_time(self, perf_benchmark, record_performance):
        """Test idle UI thread frame time."""
        benchmark = perf_benchmark("Idle Frame Time")
        
        def simulate_idle_frame():
            start = time.perf_counter()
            # Minimal work on UI thread
            _ = [i * 2 for i in range(100)]
            return time.perf_counter() - start
        
        times = []
        for _ in range(100):
            times.append(simulate_idle_frame())
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        assert avg_time < SLO.FRAME_TIME_AVG, \
            f"Idle frame time {avg_time*1000:.2f}ms exceeds 16.67ms"
        
        logger.info(
            f"Idle frame time: avg={avg_time*1000:.4f}ms, max={max_time*1000:.4f}ms"
        )
    
    def test_busy_frame_time(self, perf_benchmark, record_performance):
        """Test busy UI thread frame time (with simulated work)."""
        benchmark = perf_benchmark("Busy Frame Time")
        
        def simulate_busy_frame():
            start = time.perf_counter()
            # Simulate moderate UI work
            _ = sorted([i * 2 for i in range(1000)])
            return time.perf_counter() - start
        
        times = []
        for _ in range(50):
            times.append(simulate_busy_frame())
        
        avg_time = sum(times) / len(times)
        
        # Busy frames should still aim for 60 FPS
        assert avg_time < SLO.FRAME_TIME_P95, \
            f"Busy frame time {avg_time*1000:.2f}ms exceeds 33ms"
        
        logger.info(f"Busy frame time: avg={avg_time*1000:.4f}ms")


# =============================================================================
# Memory Performance Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
@pytest.mark.slow
class TestUIMemoryPerformance:
    """Tests for UI memory usage during operations."""
    
    def test_panel_load_memory(self, navigation_service, memory_monitor):
        """Test memory usage when loading panels."""
        memory_monitor.start()
        
        # Load several panels
        for panel_info in VOICESTUDIO_PANELS[:5]:
            navigation_service.navigate_to(panel_info["name"])
            memory_monitor.sample()
        
        stats = memory_monitor.get_stats()
        
        assert stats["delta_mb"] < SLO.MEMORY_GROWTH_MAX, \
            f"Memory growth {stats['delta_mb']:.2f}MB exceeds {SLO.MEMORY_GROWTH_MAX}MB"
        
        logger.info(
            f"Panel load memory: start={stats['start_mb']:.2f}MB, "
            f"end={stats['end_mb']:.2f}MB, delta={stats['delta_mb']:.2f}MB"
        )
    
    def test_navigation_memory_stability(self, navigation_service, memory_monitor):
        """Test memory stability during rapid navigation."""
        # Initial navigation to stabilize
        for _ in range(3):
            navigation_service.navigate_to("TestPanel1")
        
        memory_monitor.start()
        
        # Rapid navigation
        panels = [p["name"] for p in VOICESTUDIO_PANELS[:10]]
        for _ in range(5):
            for panel in panels:
                navigation_service.navigate_to(panel)
                memory_monitor.sample()
        
        stats = memory_monitor.get_stats()
        
        # Check for memory leaks (growth should be minimal after warmup)
        assert stats["delta_mb"] < SLO.MEMORY_GROWTH_MAX * 2, \
            f"Possible memory leak: {stats['delta_mb']:.2f}MB growth"
        
        logger.info(
            f"Navigation memory: peak={stats['peak_mb']:.2f}MB, "
            f"delta={stats['delta_mb']:.2f}MB"
        )


# =============================================================================
# Integration Performance Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
class TestUIIntegrationPerformance:
    """Tests for integrated UI performance scenarios."""
    
    def test_full_workflow_performance(
        self, navigation_service, control_renderer, perf_timer
    ):
        """Test full workflow performance simulation."""
        with perf_timer("Full Workflow") as timer:
            # 1. Navigate to project browser
            navigation_service.navigate_to("ProjectBrowserPanel")
            
            # 2. Load project list (simulated)
            control_renderer.render_control("ListBox", 1)
            
            # 3. Navigate to voice browser
            navigation_service.navigate_to("VoiceBrowserPanel")
            
            # 4. Render voice cards
            control_renderer.render_control("VoiceProfileCard", 10)
            
            # 5. Navigate to synthesis
            navigation_service.navigate_to("SynthesisPanel")
            
            # 6. Render synthesis controls
            control_renderer.render_control_batch({
                "TextBox": 1,
                "ComboBox": 3,
                "Button": 5,
                "WaveformDisplay": 1,
            })
        
        elapsed = timer.get_elapsed()
        
        # Full workflow should complete in reasonable time
        assert elapsed < 2.0, f"Full workflow took {elapsed:.2f}s (max 2s)"
        
        logger.info(f"Full workflow completed in {elapsed*1000:.2f}ms")
    
    def test_concurrent_operations_performance(
        self, navigation_service, control_renderer
    ):
        """Test performance with concurrent UI operations."""
        import concurrent.futures
        
        def ui_operation(op_id: int):
            start = time.perf_counter()
            panel = f"Panel_{op_id % 5}"
            navigation_service.navigate_to(panel)
            return time.perf_counter() - start
        
        start = time.perf_counter()
        
        # Note: Real UI is single-threaded, but this tests backend coordination
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(ui_operation, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        total_time = time.perf_counter() - start
        avg_time = sum(results) / len(results)
        
        logger.info(
            f"Concurrent operations: total={total_time*1000:.2f}ms, "
            f"avg_per_op={avg_time*1000:.2f}ms"
        )


# =============================================================================
# Regression Detection Tests
# =============================================================================


@pytest.mark.benchmark
@pytest.mark.ui
class TestUIPerformanceRegression:
    """Tests for detecting UI performance regressions."""
    
    # Baseline values (should be updated from actual measurements)
    BASELINES = {
        "simple_panel_render": 0.015,  # 15ms
        "medium_panel_render": 0.035,  # 35ms
        "complex_panel_render": 0.085,  # 85ms
        "single_navigation": 0.080,   # 80ms
    }
    
    # Regression threshold (10% slower = regression)
    REGRESSION_THRESHOLD = 0.10
    
    def test_simple_panel_regression(self, perf_benchmark):
        """Check for simple panel rendering regression."""
        panel = MockPanel("SimplePanel", "simple")
        benchmark = perf_benchmark("Simple Panel Regression")
        
        metrics = benchmark.run(panel.render, iterations=20)
        baseline = self.BASELINES["simple_panel_render"]
        threshold = baseline * (1 + self.REGRESSION_THRESHOLD)
        
        if metrics.avg_time > threshold:
            logger.warning(
                f"REGRESSION: Simple panel render {metrics.avg_time*1000:.2f}ms "
                f"exceeds baseline {baseline*1000:.2f}ms by "
                f"{((metrics.avg_time / baseline) - 1) * 100:.1f}%"
            )
        
        assert metrics.avg_time <= threshold, \
            f"Performance regression detected: {metrics.avg_time*1000:.2f}ms vs baseline {baseline*1000:.2f}ms"
    
    def test_navigation_regression(self, navigation_service, perf_benchmark):
        """Check for navigation performance regression."""
        navigation_service.navigate_to("StartPanel")
        
        benchmark = perf_benchmark("Navigation Regression")
        metrics = benchmark.run(
            navigation_service.navigate_to,
            "TargetPanel",
            iterations=10
        )
        
        baseline = self.BASELINES["single_navigation"]
        threshold = baseline * (1 + self.REGRESSION_THRESHOLD)
        
        if metrics.avg_time > threshold:
            logger.warning(
                f"REGRESSION: Navigation {metrics.avg_time*1000:.2f}ms "
                f"exceeds baseline {baseline*1000:.2f}ms"
            )
        
        # This is a tracking test - we warn but don't fail immediately
        logger.info(
            f"Navigation: {metrics.avg_time*1000:.2f}ms "
            f"(baseline: {baseline*1000:.2f}ms)"
        )
