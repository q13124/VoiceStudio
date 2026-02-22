"""
Unit tests for plugin crash recovery system.

Phase 5D M4: Crash recovery, auto-restart with exponential backoff,
and state preservation.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
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
    get_all_recovery_stats,
    get_recovery_manager,
    remove_recovery_manager,
)


class TestRestartPolicy:
    """Tests for RestartPolicy enum."""

    def test_all_policies_defined(self) -> None:
        """All restart policies should be defined."""
        policies = [p.value for p in RestartPolicy]
        assert "never" in policies
        assert "always" in policies
        assert "on_crash" in policies
        assert "on_error" in policies


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_all_states_defined(self) -> None:
        """All circuit states should be defined."""
        states = [s.value for s in CircuitState]
        assert "closed" in states
        assert "open" in states
        assert "half_open" in states


class TestBackoffConfig:
    """Tests for BackoffConfig dataclass."""

    def test_default_values(self) -> None:
        """Should have reasonable default values."""
        config = BackoffConfig()
        assert config.initial_delay_sec == 1.0
        assert config.max_delay_sec == 300.0
        assert config.multiplier == 2.0
        assert config.jitter_factor == 0.1

    def test_calculate_delay_first_attempt(self) -> None:
        """First attempt should have initial delay."""
        config = BackoffConfig(initial_delay_sec=1.0, jitter_factor=0.0)
        delay = config.calculate_delay(0)
        assert delay == 1.0

    def test_calculate_delay_exponential(self) -> None:
        """Delay should increase exponentially."""
        config = BackoffConfig(
            initial_delay_sec=1.0,
            multiplier=2.0,
            jitter_factor=0.0,
        )
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(3) == 8.0

    def test_calculate_delay_max_cap(self) -> None:
        """Delay should be capped at max."""
        config = BackoffConfig(
            initial_delay_sec=1.0,
            max_delay_sec=10.0,
            multiplier=2.0,
            jitter_factor=0.0,
        )
        delay = config.calculate_delay(10)
        assert delay == 10.0

    def test_calculate_delay_with_jitter(self) -> None:
        """Delay should vary with jitter."""
        config = BackoffConfig(
            initial_delay_sec=10.0,
            jitter_factor=0.1,
        )
        delays = [config.calculate_delay(0) for _ in range(10)]
        # With jitter, not all delays should be identical
        assert len(set(delays)) > 1
        # All delays should be within jitter range
        for d in delays:
            assert 9.0 <= d <= 11.0


class TestCrashEvent:
    """Tests for CrashEvent dataclass."""

    def test_to_dict(self) -> None:
        """Should convert to dictionary."""
        event = CrashEvent(
            plugin_id="test-plugin",
            timestamp=datetime(2025, 1, 15, 12, 0, 0),
            exit_code=1,
            error_message="Test error",
        )
        data = event.to_dict()
        assert data["plugin_id"] == "test-plugin"
        assert data["exit_code"] == 1
        assert data["error_message"] == "Test error"
        assert "2025-01-15" in data["timestamp"]

    def test_from_dict(self) -> None:
        """Should create from dictionary."""
        data = {
            "plugin_id": "test-plugin",
            "timestamp": "2025-01-15T12:00:00",
            "exit_code": 1,
            "error_message": "Test error",
        }
        event = CrashEvent.from_dict(data)
        assert event.plugin_id == "test-plugin"
        assert event.exit_code == 1


class TestPluginState:
    """Tests for PluginState dataclass."""

    def test_to_dict(self) -> None:
        """Should convert to dictionary."""
        state = PluginState(
            plugin_id="test-plugin",
            last_active=datetime(2025, 1, 15, 12, 0, 0),
            user_data={"key": "value"},
        )
        data = state.to_dict()
        assert data["plugin_id"] == "test-plugin"
        assert data["user_data"] == {"key": "value"}

    def test_from_dict(self) -> None:
        """Should create from dictionary."""
        data = {
            "plugin_id": "test-plugin",
            "last_active": "2025-01-15T12:00:00",
            "user_data": {"key": "value"},
            "invocation_context": {},
            "capabilities_state": {},
        }
        state = PluginState.from_dict(data)
        assert state.plugin_id == "test-plugin"
        assert state.user_data == {"key": "value"}


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_initial_state_closed(self) -> None:
        """Circuit should start closed."""
        breaker = CircuitBreaker()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.allows_request
        assert not breaker.is_open

    def test_record_success(self) -> None:
        """Success should keep circuit closed."""
        breaker = CircuitBreaker()
        breaker.record_success()
        assert breaker.state == CircuitState.CLOSED

    def test_record_failure_threshold(self) -> None:
        """Should open after threshold failures."""
        breaker = CircuitBreaker(threshold=3)
        breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED
        breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        assert breaker.is_open
        assert not breaker.allows_request

    def test_reset_after_timeout(self) -> None:
        """Should reset to half-open after timeout."""
        breaker = CircuitBreaker(threshold=1, reset_timeout_sec=0.1)
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

        # Wait for reset
        import time

        time.sleep(0.15)
        assert breaker.state == CircuitState.HALF_OPEN
        assert breaker.allows_request

    def test_success_closes_circuit(self) -> None:
        """Success after half-open should close circuit."""
        breaker = CircuitBreaker(threshold=1, reset_timeout_sec=0.0)
        breaker.record_failure()
        breaker._check_reset()  # Force half-open
        breaker.record_success()
        assert breaker.state == CircuitState.CLOSED


class TestRecoveryConfig:
    """Tests for RecoveryConfig dataclass."""

    def test_default_values(self) -> None:
        """Should have reasonable default values."""
        config = RecoveryConfig()
        assert config.restart_policy == RestartPolicy.ON_CRASH
        assert config.max_restarts == 5
        assert config.preserve_state is True


class TestCrashRecoveryManager:
    """Tests for CrashRecoveryManager class."""

    @pytest.fixture
    def manager(self, tmp_path: Path) -> CrashRecoveryManager:
        """Create a recovery manager for testing."""
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ON_CRASH,
            max_restarts=3,
            restart_window_sec=60.0,
            state_dir=tmp_path,
        )
        return CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

    def test_initialization(self, manager: CrashRecoveryManager) -> None:
        """Manager should initialize correctly."""
        assert manager.plugin_id == "test-plugin"
        assert manager.crash_count == 0
        assert manager.can_restart

    @pytest.mark.asyncio
    async def test_on_crash_records_event(self, manager: CrashRecoveryManager) -> None:
        """Should record crash event."""
        # No restart callback, so it won't actually restart
        await manager.on_crash(exit_code=1, error_message="Test crash")

        assert manager.crash_count == 1
        assert len(manager.crash_history) == 1
        assert manager.crash_history[0].exit_code == 1

    @pytest.mark.asyncio
    async def test_on_crash_preserves_state(self, manager: CrashRecoveryManager) -> None:
        """Should preserve state snapshot."""
        state_snapshot = {"user_data": {"key": "value"}}
        await manager.on_crash(state_snapshot=state_snapshot)

        assert manager.preserved_state is not None
        assert manager.preserved_state.user_data == {"key": "value"}

    @pytest.mark.asyncio
    async def test_on_crash_triggers_restart(self, manager: CrashRecoveryManager) -> None:
        """Should trigger restart callback."""
        restart_mock = AsyncMock(return_value=True)
        manager.set_restart_callback(restart_mock)

        # Use a very short backoff for testing
        manager._config.backoff.initial_delay_sec = 0.01

        result = await manager.on_crash(exit_code=1)
        assert result is True

        # Wait for restart to complete
        await asyncio.sleep(0.1)
        restart_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_max_restarts_exceeded(self, tmp_path: Path) -> None:
        """Should not restart after max restarts exceeded."""
        # Create a new manager with max_restarts=2 and no circuit breaker
        # interference (high threshold)
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ON_CRASH,
            max_restarts=2,
            restart_window_sec=60.0,
            state_dir=tmp_path,
            circuit_breaker_threshold=100,  # High to avoid interference
        )
        manager = CrashRecoveryManager(
            plugin_id="test-max-restarts",
            config=config,
        )

        # First crash - can still restart (1 < 2)
        await manager.on_crash(exit_code=1)
        assert manager.recent_crash_count == 1
        # can_restart checks recent_crash_count >= max_restarts
        # 1 >= 2 is False, so can_restart should still be True
        assert manager.can_restart

        # Second crash - can_restart becomes False (2 >= 2)
        await manager.on_crash(exit_code=1)
        assert manager.recent_crash_count == 2
        assert not manager.can_restart  # 2 >= 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, tmp_path: Path) -> None:
        """Should open circuit breaker after failures."""
        # Create a new manager with low circuit breaker threshold
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ON_CRASH,
            max_restarts=100,  # High to avoid interference
            restart_window_sec=60.0,
            state_dir=tmp_path,
            circuit_breaker_threshold=2,
        )
        manager = CrashRecoveryManager(
            plugin_id="test-circuit-breaker",
            config=config,
        )

        await manager.on_crash(exit_code=1)
        assert not manager._circuit_breaker.is_open  # 1 failure

        await manager.on_crash(exit_code=1)
        # Circuit should be open after 2 failures (threshold=2)
        assert manager._circuit_breaker.is_open
        assert not manager.can_restart

    @pytest.mark.asyncio
    async def test_preserve_state(self, manager: CrashRecoveryManager) -> None:
        """Should preserve state."""
        await manager.preserve_state(
            invocation_context={"context": "value"},
            user_data={"user": "data"},
        )

        assert manager.preserved_state is not None
        assert manager.preserved_state.invocation_context == {"context": "value"}
        assert manager.preserved_state.user_data == {"user": "data"}

    @pytest.mark.asyncio
    async def test_restore_state(self, manager: CrashRecoveryManager) -> None:
        """Should restore preserved state."""
        await manager.preserve_state(user_data={"key": "value"})

        state = await manager.restore_state()
        assert state is not None
        assert state.user_data == {"key": "value"}

    @pytest.mark.asyncio
    async def test_clear_state(self, manager: CrashRecoveryManager, tmp_path: Path) -> None:
        """Should clear preserved state."""
        await manager.preserve_state(user_data={"key": "value"})
        await manager.clear_state()

        assert manager.preserved_state is None

    def test_reset(self, manager: CrashRecoveryManager) -> None:
        """Should reset recovery state."""
        manager._crash_history = [CrashEvent("test", datetime.now(), 1)]
        manager.reset()

        assert manager.crash_count == 0
        assert len(manager.crash_history) == 0

    @pytest.mark.asyncio
    async def test_cancel_pending_restart(self, manager: CrashRecoveryManager) -> None:
        """Should cancel pending restart."""
        restart_mock = AsyncMock(return_value=True)
        manager.set_restart_callback(restart_mock)
        manager._config.backoff.initial_delay_sec = 5.0

        await manager.on_crash(exit_code=1)
        await manager.cancel_pending_restart()

        # Wait a bit - restart should not have been called
        await asyncio.sleep(0.1)
        restart_mock.assert_not_called()

    def test_get_stats(self, manager: CrashRecoveryManager) -> None:
        """Should return recovery statistics."""
        stats = manager.get_stats()

        assert stats["plugin_id"] == "test-plugin"
        assert stats["crash_count"] == 0
        assert "can_restart" in stats
        assert "circuit_state" in stats

    @pytest.mark.asyncio
    async def test_state_persistence(self, manager: CrashRecoveryManager, tmp_path: Path) -> None:
        """Should persist state to disk."""
        await manager.preserve_state(user_data={"key": "value"})

        state_file = tmp_path / "test-plugin_state.json"
        assert state_file.exists()

        data = json.loads(state_file.read_text())
        assert data["user_data"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_crash_history_persistence(
        self, manager: CrashRecoveryManager, tmp_path: Path
    ) -> None:
        """Should persist crash history to disk."""
        await manager.on_crash(exit_code=1, error_message="Test")

        history_file = tmp_path / "test-plugin_crashes.json"
        assert history_file.exists()

        data = json.loads(history_file.read_text())
        assert len(data) == 1
        assert data[0]["exit_code"] == 1

    @pytest.mark.asyncio
    async def test_load_crash_history(self, tmp_path: Path) -> None:
        """Should load crash history from disk."""
        # Create history file
        history_file = tmp_path / "test-plugin_crashes.json"
        history_data = [
            {
                "plugin_id": "test-plugin",
                "timestamp": "2025-01-15T12:00:00",
                "exit_code": 1,
                "error_message": "Test",
            }
        ]
        history_file.write_text(json.dumps(history_data))

        config = RecoveryConfig(state_dir=tmp_path)
        manager = CrashRecoveryManager("test-plugin", config)
        await manager.load_crash_history()

        assert manager.crash_count == 1

    def test_policy_never_blocks_restart(self) -> None:
        """NEVER policy should block restarts."""
        config = RecoveryConfig(restart_policy=RestartPolicy.NEVER)
        manager = CrashRecoveryManager("test-plugin", config)

        assert not manager.can_restart


class TestGlobalRegistry:
    """Tests for global recovery manager registry."""

    def test_get_recovery_manager(self) -> None:
        """Should create and cache managers."""
        manager1 = get_recovery_manager("plugin-1")
        manager2 = get_recovery_manager("plugin-1")

        assert manager1 is manager2

    def test_remove_recovery_manager(self) -> None:
        """Should remove managers from registry."""
        get_recovery_manager("plugin-to-remove")
        remove_recovery_manager("plugin-to-remove")

        # Getting again should create new instance
        manager = get_recovery_manager("plugin-to-remove")
        assert manager.crash_count == 0

    def test_get_all_recovery_stats(self) -> None:
        """Should return stats for all managers."""
        get_recovery_manager("plugin-stats-1")
        get_recovery_manager("plugin-stats-2")

        stats = get_all_recovery_stats()
        assert "plugin-stats-1" in stats
        assert "plugin-stats-2" in stats

    @pytest.fixture(autouse=True)
    def cleanup_registry(self) -> None:
        """Clean up registry after each test."""
        yield
        # Clean up test plugins
        for plugin_id in [
            "plugin-1",
            "plugin-to-remove",
            "plugin-stats-1",
            "plugin-stats-2",
        ]:
            remove_recovery_manager(plugin_id)


class TestRestartWithBackoff:
    """Integration tests for restart with backoff."""

    @pytest.mark.asyncio
    async def test_successful_restart_resets_circuit(self) -> None:
        """Successful restart should reset circuit breaker."""
        config = RecoveryConfig(
            backoff=BackoffConfig(initial_delay_sec=0.01),
            circuit_breaker_threshold=3,
        )
        manager = CrashRecoveryManager("backoff-test", config)

        restart_mock = AsyncMock(return_value=True)
        manager.set_restart_callback(restart_mock)

        # Trigger crash and wait for restart
        await manager.on_crash(exit_code=1)
        await asyncio.sleep(0.1)

        # Circuit should be closed after successful restart
        assert manager._circuit_breaker.state == CircuitState.CLOSED

        # Cleanup
        remove_recovery_manager("backoff-test")

    @pytest.mark.asyncio
    async def test_failed_restart_increases_backoff(self) -> None:
        """Failed restart should trigger another attempt with longer backoff."""
        config = RecoveryConfig(
            backoff=BackoffConfig(
                initial_delay_sec=0.01,
                multiplier=2.0,
            ),
            circuit_breaker_threshold=5,
        )
        manager = CrashRecoveryManager("backoff-fail-test", config)

        restart_mock = AsyncMock(return_value=False)
        manager.set_restart_callback(restart_mock)

        # Trigger crash
        await manager.on_crash(exit_code=1)
        await asyncio.sleep(0.1)

        # Circuit breaker should have recorded the failure
        assert manager._circuit_breaker._failure_count >= 1

        # Cleanup
        remove_recovery_manager("backoff-fail-test")
