"""
Tests for Plugin Resource Monitor.

Phase 5A: Validates resource monitoring and enforcement functionality.
"""

import asyncio
import os
import sys
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(
    0, str(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "backend"))
)

from backend.plugins.sandbox.resource_monitor import (
    PSUTIL_AVAILABLE,
    ResourceLimits,
    ResourceMonitor,
    ResourceMonitorRegistry,
    ResourceSnapshot,
    ViolationAction,
    ViolationEvent,
    ViolationType,
    get_resource_monitor_registry,
)


class TestResourceLimits:
    """Tests for ResourceLimits configuration."""

    def test_default_limits(self):
        """Test default values for resource limits."""
        limits = ResourceLimits()

        assert limits.max_memory_mb is None
        assert limits.max_cpu_percent is None
        assert limits.soft_memory_mb is None
        assert limits.soft_cpu_percent is None
        assert limits.memory_grace_period_sec == 5.0
        assert limits.cpu_grace_period_sec == 10.0
        assert limits.check_interval_sec == 2.0

    def test_auto_soft_limits(self):
        """Test that soft limits are auto-calculated at 80% of hard limits."""
        limits = ResourceLimits(
            max_memory_mb=100,
            max_cpu_percent=80,
        )

        assert limits.soft_memory_mb == 80  # 80% of 100
        assert limits.soft_cpu_percent == 64  # 80% of 80

    def test_explicit_soft_limits(self):
        """Test that explicit soft limits override auto-calculation."""
        limits = ResourceLimits(
            max_memory_mb=100,
            soft_memory_mb=50,
            max_cpu_percent=80,
            soft_cpu_percent=40,
        )

        assert limits.soft_memory_mb == 50
        assert limits.soft_cpu_percent == 40


class TestResourceSnapshot:
    """Tests for ResourceSnapshot data structure."""

    def test_snapshot_to_dict(self):
        """Test snapshot serialization."""
        import time

        ts = time.time()

        snapshot = ResourceSnapshot(
            timestamp=ts,
            memory_mb=256.789,
            memory_percent=25.5,
            cpu_percent=50.123,
            num_threads=4,
            status="running",
        )

        data = snapshot.to_dict()

        assert data["timestamp"] == ts
        assert data["memory_mb"] == 256.79  # Rounded
        assert data["memory_percent"] == 25.5
        assert data["cpu_percent"] == 50.12  # Rounded
        assert data["num_threads"] == 4
        assert data["status"] == "running"


class TestViolationEvent:
    """Tests for ViolationEvent data structure."""

    def test_violation_to_dict(self):
        """Test violation event serialization."""
        import time

        ts = time.time()

        event = ViolationEvent(
            violation_type=ViolationType.MEMORY_HARD,
            action=ViolationAction.TERMINATE,
            timestamp=ts,
            current_value=512.5,
            limit_value=256,
            grace_remaining_sec=0.0,
            plugin_id="test-plugin",
            pid=12345,
        )

        data = event.to_dict()

        assert data["violation_type"] == "memory_hard"
        assert data["action"] == "terminate"
        assert data["timestamp"] == ts
        assert data["current_value"] == 512.5
        assert data["limit_value"] == 256
        assert data["grace_remaining_sec"] == 0.0
        assert data["plugin_id"] == "test-plugin"
        assert data["pid"] == 12345


@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
class TestResourceMonitor:
    """Tests for ResourceMonitor functionality."""

    @pytest.fixture
    def mock_process(self):
        """Create a mock psutil.Process."""
        process = MagicMock()
        process.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)  # 100 MB
        process.memory_percent.return_value = 10.0
        process.cpu_percent.return_value = 25.0
        process.num_threads.return_value = 2
        process.status.return_value = "running"
        return process

    @pytest.fixture
    def monitor_with_mock(self, mock_process):
        """Create a monitor with mocked process."""
        limits = ResourceLimits(
            max_memory_mb=256,
            max_cpu_percent=80,
            check_interval_sec=0.1,
        )

        monitor = ResourceMonitor(
            plugin_id="test-plugin",
            pid=12345,
            limits=limits,
        )

        # Replace the process handle with mock
        monitor._process = mock_process

        return monitor

    def test_monitor_initialization(self, monitor_with_mock):
        """Test monitor initializes correctly."""
        assert monitor_with_mock.plugin_id == "test-plugin"
        assert monitor_with_mock.pid == 12345
        assert monitor_with_mock.limits.max_memory_mb == 256
        assert not monitor_with_mock.is_monitoring

    def test_get_current_usage(self, monitor_with_mock, mock_process):
        """Test getting current resource usage."""
        # Configure mock for oneshot context
        mock_process.oneshot.return_value.__enter__ = MagicMock()
        mock_process.oneshot.return_value.__exit__ = MagicMock()

        snapshot = monitor_with_mock.get_current_usage()

        assert snapshot is not None
        assert snapshot.memory_mb == 100.0
        assert snapshot.cpu_percent == 25.0
        assert snapshot.num_threads == 2
        assert snapshot.status == "running"

    @pytest.mark.asyncio
    async def test_monitor_start_stop(self, monitor_with_mock):
        """Test starting and stopping the monitor."""
        # Start
        await monitor_with_mock.start()
        assert monitor_with_mock.is_monitoring

        # Let it run briefly
        await asyncio.sleep(0.05)

        # Stop
        await monitor_with_mock.stop()
        assert not monitor_with_mock.is_monitoring

    @pytest.mark.asyncio
    async def test_violation_callback(self, monitor_with_mock, mock_process):
        """Test that violation callbacks are fired."""
        # Set up mock to exceed memory limit
        mock_process.oneshot.return_value.__enter__ = MagicMock()
        mock_process.oneshot.return_value.__exit__ = MagicMock()
        mock_process.memory_info.return_value = MagicMock(
            rss=300 * 1024 * 1024  # 300 MB, exceeds 256 limit
        )

        violations = []

        async def on_violation(event: ViolationEvent):
            violations.append(event)

        monitor_with_mock.on_violation(on_violation)

        # Check resources manually (simulating monitor loop)
        await monitor_with_mock._check_resources()

        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.MEMORY_HARD
        assert violations[0].action == ViolationAction.WARN  # First warning has grace period

    def test_average_cpu_calculation(self, monitor_with_mock):
        """Test CPU average calculation from snapshots."""
        import time

        # Add some snapshots
        for cpu in [20.0, 30.0, 40.0, 50.0]:
            monitor_with_mock._snapshots.append(
                ResourceSnapshot(
                    timestamp=time.time(),
                    memory_mb=100,
                    memory_percent=10.0,
                    cpu_percent=cpu,
                    num_threads=2,
                    status="running",
                )
            )

        # Average should be 35.0
        assert monitor_with_mock.average_cpu_percent == 35.0

    def test_peak_memory_calculation(self, monitor_with_mock):
        """Test peak memory calculation from snapshots."""
        import time

        # Add some snapshots
        for mem in [100.0, 200.0, 150.0, 180.0]:
            monitor_with_mock._snapshots.append(
                ResourceSnapshot(
                    timestamp=time.time(),
                    memory_mb=mem,
                    memory_percent=10.0,
                    cpu_percent=25.0,
                    num_threads=2,
                    status="running",
                )
            )

        # Peak should be 200.0
        assert monitor_with_mock.peak_memory_mb == 200.0


class TestResourceMonitorRegistry:
    """Tests for ResourceMonitorRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry."""
        return ResourceMonitorRegistry()

    @pytest.mark.asyncio
    async def test_create_monitor(self, registry):
        """Test creating a monitor through the registry."""
        limits = ResourceLimits(max_memory_mb=256)

        with patch("backend.plugins.sandbox.resource_monitor.psutil") as mock_psutil:
            mock_psutil.Process.return_value = MagicMock()

            monitor = await registry.create_monitor(
                plugin_id="test-plugin",
                pid=12345,
                limits=limits,
                auto_start=False,  # Don't actually start monitoring
            )

            assert monitor is not None
            assert monitor.plugin_id == "test-plugin"
            assert "test-plugin" in registry.monitors

    @pytest.mark.asyncio
    async def test_stop_monitor(self, registry):
        """Test stopping a monitor through the registry."""
        limits = ResourceLimits(max_memory_mb=256)

        with patch("backend.plugins.sandbox.resource_monitor.psutil") as mock_psutil:
            mock_psutil.Process.return_value = MagicMock()

            await registry.create_monitor(
                plugin_id="test-plugin",
                pid=12345,
                limits=limits,
                auto_start=False,
            )

            await registry.stop_monitor("test-plugin")

            assert "test-plugin" not in registry.monitors

    @pytest.mark.asyncio
    async def test_stop_all(self, registry):
        """Test stopping all monitors."""
        limits = ResourceLimits(max_memory_mb=256)

        with patch("backend.plugins.sandbox.resource_monitor.psutil") as mock_psutil:
            mock_psutil.Process.return_value = MagicMock()

            await registry.create_monitor("plugin-1", 1001, limits, auto_start=False)
            await registry.create_monitor("plugin-2", 1002, limits, auto_start=False)

            assert len(registry.monitors) == 2

            await registry.stop_all()

            assert len(registry.monitors) == 0

    @pytest.mark.asyncio
    async def test_get_all_violations(self, registry):
        """Test aggregating violations from all monitors."""
        limits = ResourceLimits(max_memory_mb=256)

        with patch("backend.plugins.sandbox.resource_monitor.psutil") as mock_psutil:
            mock_psutil.Process.return_value = MagicMock()

            monitor = await registry.create_monitor(
                plugin_id="test-plugin",
                pid=12345,
                limits=limits,
                auto_start=False,
            )

            # Manually add a violation
            import time

            monitor._violations.append(
                ViolationEvent(
                    violation_type=ViolationType.MEMORY_SOFT,
                    action=ViolationAction.WARN,
                    timestamp=time.time(),
                    current_value=200.0,
                    limit_value=204.8,
                    grace_remaining_sec=0,
                    plugin_id="test-plugin",
                    pid=12345,
                )
            )

            all_violations = registry.get_all_violations()

            assert "test-plugin" in all_violations
            assert len(all_violations["test-plugin"]) == 1


class TestGlobalRegistry:
    """Tests for global registry singleton."""

    def test_global_registry_singleton(self):
        """Test that get_resource_monitor_registry returns the same instance."""
        registry1 = get_resource_monitor_registry()
        registry2 = get_resource_monitor_registry()

        assert registry1 is registry2


class TestResourceMonitorIntegration:
    """Integration tests for resource monitoring with runner."""

    @pytest.mark.asyncio
    async def test_resource_limits_config_to_limits(self):
        """Test that RunnerConfig resource limits convert to ResourceLimits correctly."""
        from pathlib import Path

        from backend.plugins.sandbox.runner import RunnerConfig

        config = RunnerConfig(
            plugin_id="test-plugin",
            plugin_path=Path("/tmp/test"),
            entry_module="test",
            max_memory_mb=512,
            max_cpu_percent=75,
            resource_check_interval_sec=1.0,
            memory_grace_period_sec=3.0,
            cpu_grace_period_sec=8.0,
        )

        # Build limits as runner would
        limits = ResourceLimits(
            max_memory_mb=config.max_memory_mb,
            max_cpu_percent=config.max_cpu_percent,
            check_interval_sec=config.resource_check_interval_sec,
            memory_grace_period_sec=config.memory_grace_period_sec,
            cpu_grace_period_sec=config.cpu_grace_period_sec,
        )

        assert limits.max_memory_mb == 512
        assert limits.max_cpu_percent == 75
        assert limits.soft_memory_mb == 409  # 80% of 512
        assert limits.soft_cpu_percent == 60  # 80% of 75
        assert limits.check_interval_sec == 1.0
        assert limits.memory_grace_period_sec == 3.0
        assert limits.cpu_grace_period_sec == 8.0
