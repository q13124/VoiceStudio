"""
Resilience tests for plugin crash recovery.

Tests that the plugin system correctly handles and recovers from
various crash scenarios.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.sandbox.crash_recovery import (
    BackoffConfig,
    CircuitBreaker,
    CircuitState,
    CrashEvent,
    CrashRecoveryManager,
    PluginState,
    RecoveryConfig,
    RestartPolicy,
)


class TestRestartPolicies:
    """Tests for different restart policies."""

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_never_restart_policy(self):
        """Test that NEVER policy prevents restarts."""
        config = RecoveryConfig(restart_policy=RestartPolicy.NEVER)
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

        # Simulate crash - should not allow restart
        result = await manager.on_crash(exit_code=1, error_message="Simulated crash")

        # NEVER policy should prevent restart
        assert result is False
        assert manager.can_restart is False

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_always_restart_policy(self):
        """Test that ALWAYS policy allows restart."""
        restart_called = False

        async def restart_callback():
            nonlocal restart_called
            restart_called = True
            return True

        config = RecoveryConfig(
            restart_policy=RestartPolicy.ALWAYS,
            max_restarts=10,
            backoff=BackoffConfig(initial_delay_sec=0.01),  # Fast for test
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
            restart_callback=restart_callback,
        )

        # Should allow restart
        assert manager.can_restart is True

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_on_crash_policy_triggers_restart(self):
        """Test ON_CRASH policy triggers restart on error exit."""
        restart_called = False

        async def restart_callback():
            nonlocal restart_called
            restart_called = True
            return True

        config = RecoveryConfig(
            restart_policy=RestartPolicy.ON_CRASH,
            max_restarts=10,
            backoff=BackoffConfig(initial_delay_sec=0.01),
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
            restart_callback=restart_callback,
        )

        # Trigger crash
        result = await manager.on_crash(exit_code=1, error_message="Error")

        # Should attempt restart
        assert result is True


class TestMaxRestarts:
    """Tests for maximum restart limits."""

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_respects_max_restarts(self):
        """Test that max_restarts limit is respected."""
        restart_count = 0

        async def restart_callback():
            nonlocal restart_count
            restart_count += 1
            return True

        config = RecoveryConfig(
            restart_policy=RestartPolicy.ALWAYS,
            max_restarts=3,
            restart_window_sec=3600,
            backoff=BackoffConfig(initial_delay_sec=0.01),
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
            restart_callback=restart_callback,
        )

        # First 3 crashes should allow restart
        for i in range(3):
            await manager.on_crash(exit_code=1, error_message=f"Crash {i+1}")
            await asyncio.sleep(0.05)  # Wait for restart to complete

        # After 3 crashes, should not allow more restarts
        assert manager.can_restart is False

    @pytest.mark.crash
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_restart_window_resets_count(self):
        """Test that restart count resets after window expires."""
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ALWAYS,
            max_restarts=2,
            restart_window_sec=0.5,  # Short window for fast test
            backoff=BackoffConfig(initial_delay_sec=0.01),
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

        # Exhaust restarts
        for i in range(2):
            await manager.on_crash(exit_code=1, error_message=f"Crash {i+1}")

        # Should not allow restart
        assert manager.can_restart is False

        # Wait for window to expire
        await asyncio.sleep(0.6)

        # Recent crash count should be 0 now
        assert manager.recent_crash_count == 0


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""

    @pytest.mark.crash
    def test_circuit_starts_closed(self):
        """Test circuit starts in closed state."""
        breaker = CircuitBreaker(
            threshold=3,
            reset_timeout_sec=60.0,
        )
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.crash
    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        breaker = CircuitBreaker(
            threshold=3,
            reset_timeout_sec=60.0,
        )

        # Record failures
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitState.OPEN

    @pytest.mark.crash
    def test_circuit_allows_when_closed(self):
        """Test requests allowed when circuit closed."""
        breaker = CircuitBreaker(
            threshold=3,
            reset_timeout_sec=60.0,
        )

        assert breaker.allows_request is True

    @pytest.mark.crash
    def test_circuit_blocks_when_open(self):
        """Test requests blocked when circuit open."""
        breaker = CircuitBreaker(
            threshold=1,
            reset_timeout_sec=60.0,
        )

        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        assert breaker.allows_request is False

    @pytest.mark.crash
    def test_circuit_half_open_after_timeout(self):
        """Test circuit goes half-open after reset timeout."""
        breaker = CircuitBreaker(
            threshold=1,
            reset_timeout_sec=0.1,  # Very short timeout
        )

        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

        # Wait for reset timeout
        time.sleep(0.15)

        # Next state check should transition to half-open
        assert breaker.state == CircuitState.HALF_OPEN
        assert breaker.allows_request is True

    @pytest.mark.crash
    def test_circuit_closes_on_success_in_half_open(self):
        """Test circuit closes on success in half-open state."""
        breaker = CircuitBreaker(
            threshold=1,
            reset_timeout_sec=0.1,
        )

        # Open the circuit
        breaker.record_failure()

        # Wait and transition to half-open
        time.sleep(0.15)
        _ = breaker.state  # Triggers check

        # Record success
        breaker.record_success()

        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.crash
    def test_circuit_reopens_on_failure_in_half_open(self):
        """Test circuit reopens on failure in half-open state."""
        breaker = CircuitBreaker(
            threshold=1,
            reset_timeout_sec=0.1,
        )

        # Open the circuit
        breaker.record_failure()

        # Wait and transition to half-open
        time.sleep(0.15)
        _ = breaker.state  # Triggers check

        # Record another failure
        breaker.record_failure()

        assert breaker.state == CircuitState.OPEN


class TestExponentialBackoff:
    """Tests for exponential backoff in restart delays."""

    @pytest.mark.crash
    def test_initial_delay(self):
        """Test initial delay is correct."""
        config = BackoffConfig(
            initial_delay_sec=1.0,
            max_delay_sec=60.0,
            multiplier=2.0,
            jitter_factor=0.0,  # No jitter for predictable tests
        )

        delay = config.calculate_delay(attempt=0)
        assert delay == 1.0

    @pytest.mark.crash
    def test_delay_increases_exponentially(self):
        """Test delay increases exponentially."""
        config = BackoffConfig(
            initial_delay_sec=1.0,
            max_delay_sec=60.0,
            multiplier=2.0,
            jitter_factor=0.0,
        )

        assert config.calculate_delay(attempt=0) == 1.0
        assert config.calculate_delay(attempt=1) == 2.0
        assert config.calculate_delay(attempt=2) == 4.0
        assert config.calculate_delay(attempt=3) == 8.0

    @pytest.mark.crash
    def test_delay_capped_at_max(self):
        """Test delay is capped at maximum."""
        config = BackoffConfig(
            initial_delay_sec=1.0,
            max_delay_sec=10.0,
            multiplier=2.0,
            jitter_factor=0.0,
        )

        # After many attempts, should hit max
        delay = config.calculate_delay(attempt=10)
        assert delay == 10.0

    @pytest.mark.crash
    def test_jitter_adds_randomness(self):
        """Test jitter adds randomness to delay."""
        config = BackoffConfig(
            initial_delay_sec=10.0,
            max_delay_sec=60.0,
            multiplier=2.0,
            jitter_factor=0.5,  # 50% jitter
        )

        delays = [config.calculate_delay(attempt=0) for _ in range(20)]

        # Should have some variation
        assert len(set(delays)) > 1

        # All should be within jitter range (50% = 5 to 15)
        for d in delays:
            assert 5.0 <= d <= 15.0


class TestStatePreservation:
    """Tests for plugin state preservation across restarts."""

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_state_snapshot_captured_on_crash(self):
        """Test state snapshot is captured on crash."""
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ALWAYS,
            preserve_state=True,
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

        # Crash with state snapshot
        state_snapshot = {
            "invocation_context": {"session_id": "123"},
            "user_data": {"preference": "dark"},
            "capabilities_state": {"audio": {"volume": 0.8}},
        }

        await manager.on_crash(
            exit_code=1,
            error_message="Crash with state",
            state_snapshot=state_snapshot,
        )

        # Verify state was preserved
        preserved = manager.preserved_state
        assert preserved is not None
        assert preserved.user_data["preference"] == "dark"

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_state_cleared_after_restore(self):
        """Test state can be cleared after restore."""
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ALWAYS,
            preserve_state=True,
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

        # Preserve state manually
        await manager.preserve_state(user_data={"key": "value"})

        # Verify state exists
        restored = await manager.restore_state()
        assert restored is not None

        # Clear state
        await manager.clear_state()

        # State should be cleared
        assert manager.preserved_state is None


class TestCrashEventHistory:
    """Tests for crash event history tracking."""

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_crash_history_recorded(self):
        """Test crash events are recorded in history."""
        manager = CrashRecoveryManager(plugin_id="test-plugin")

        for i in range(5):
            await manager.on_crash(
                exit_code=i + 1,
                error_message=f"Error {i+1}",
            )

        history = manager.crash_history
        assert len(history) == 5
        assert history[-1].exit_code == 5

    @pytest.mark.crash
    @pytest.mark.asyncio
    async def test_crash_statistics(self):
        """Test crash statistics calculation."""
        manager = CrashRecoveryManager(plugin_id="test-plugin")

        # Record some crashes
        for i in range(5):
            await manager.on_crash(
                exit_code=1,
                error_message="Error",
            )

        stats = manager.get_stats()
        assert stats["crash_count"] == 5
        assert "circuit_state" in stats
        assert "config" in stats


class TestCrashEventDataclass:
    """Tests for CrashEvent dataclass."""

    @pytest.mark.crash
    def test_crash_event_creation(self):
        """Test CrashEvent creation."""
        event = CrashEvent(
            plugin_id="test-plugin",
            timestamp=datetime.now(),
            exit_code=1,
            error_message="Test error",
        )

        assert event.plugin_id == "test-plugin"
        assert event.exit_code == 1
        assert event.error_message == "Test error"

    @pytest.mark.crash
    def test_crash_event_serialization(self):
        """Test CrashEvent to/from dict."""
        event = CrashEvent(
            plugin_id="test-plugin",
            timestamp=datetime.now(),
            exit_code=1,
            error_message="Test error",
            restart_attempted=True,
        )

        data = event.to_dict()
        restored = CrashEvent.from_dict(data)

        assert restored.plugin_id == event.plugin_id
        assert restored.exit_code == event.exit_code
        assert restored.restart_attempted == event.restart_attempted


class TestPluginStateDataclass:
    """Tests for PluginState dataclass."""

    @pytest.mark.crash
    def test_plugin_state_creation(self):
        """Test PluginState creation."""
        state = PluginState(
            plugin_id="test-plugin",
            last_active=datetime.now(),
            user_data={"key": "value"},
        )

        assert state.plugin_id == "test-plugin"
        assert state.user_data["key"] == "value"

    @pytest.mark.crash
    def test_plugin_state_serialization(self):
        """Test PluginState to/from dict."""
        state = PluginState(
            plugin_id="test-plugin",
            last_active=datetime.now(),
            user_data={"key": "value"},
            capabilities_state={"audio": {"volume": 0.5}},
        )

        data = state.to_dict()
        restored = PluginState.from_dict(data)

        assert restored.plugin_id == state.plugin_id
        assert restored.user_data == state.user_data
