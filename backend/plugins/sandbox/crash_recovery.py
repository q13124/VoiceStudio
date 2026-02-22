"""
Plugin Crash Recovery System.

Phase 5D M4: Crash recovery, auto-restart with exponential backoff,
and state preservation.

Provides:
- Automatic restart on crash with configurable policies
- Exponential backoff for repeated failures
- State preservation and restoration
- Crash history tracking
- Circuit breaker pattern for failing plugins
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


class RestartPolicy(str, Enum):
    """Policy for automatic restarts."""

    NEVER = "never"
    ALWAYS = "always"
    ON_CRASH = "on_crash"
    ON_ERROR = "on_error"


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting restarts
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class BackoffConfig:
    """Exponential backoff configuration."""

    initial_delay_sec: float = 1.0
    max_delay_sec: float = 300.0  # 5 minutes
    multiplier: float = 2.0
    jitter_factor: float = 0.1  # 10% jitter

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        import random

        delay = min(
            self.initial_delay_sec * (self.multiplier**attempt),
            self.max_delay_sec,
        )

        # Add jitter
        jitter = delay * self.jitter_factor
        delay = delay + random.uniform(-jitter, jitter)

        return max(0, delay)


@dataclass
class CrashEvent:
    """Record of a crash event."""

    plugin_id: str
    timestamp: datetime
    exit_code: int | None
    error_message: str | None = None
    state_snapshot: dict[str, Any] | None = None
    restart_attempted: bool = False
    restart_succeeded: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "timestamp": self.timestamp.isoformat(),
            "exit_code": self.exit_code,
            "error_message": self.error_message,
            "state_snapshot": self.state_snapshot,
            "restart_attempted": self.restart_attempted,
            "restart_succeeded": self.restart_succeeded,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CrashEvent:
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            exit_code=data.get("exit_code"),
            error_message=data.get("error_message"),
            state_snapshot=data.get("state_snapshot"),
            restart_attempted=data.get("restart_attempted", False),
            restart_succeeded=data.get("restart_succeeded", False),
        )


@dataclass
class PluginState:
    """Preserved state for a plugin."""

    plugin_id: str
    last_active: datetime | None = None
    invocation_context: dict[str, Any] = field(default_factory=dict)
    user_data: dict[str, Any] = field(default_factory=dict)
    capabilities_state: dict[str, Any] = field(default_factory=dict)
    checkpoint_data: bytes | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "plugin_id": self.plugin_id,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "invocation_context": self.invocation_context,
            "user_data": self.user_data,
            "capabilities_state": self.capabilities_state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginState:
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            last_active=(
                datetime.fromisoformat(data["last_active"]) if data.get("last_active") else None
            ),
            invocation_context=data.get("invocation_context", {}),
            user_data=data.get("user_data", {}),
            capabilities_state=data.get("capabilities_state", {}),
        )


@dataclass
class RecoveryConfig:
    """Configuration for crash recovery behavior."""

    restart_policy: RestartPolicy = RestartPolicy.ON_CRASH
    max_restarts: int = 5
    restart_window_sec: float = 300.0  # 5 minutes
    backoff: BackoffConfig = field(default_factory=BackoffConfig)
    preserve_state: bool = True
    state_dir: Path | None = None
    circuit_breaker_threshold: int = 3
    circuit_breaker_reset_sec: float = 60.0


class CircuitBreaker:
    """Circuit breaker for crash recovery."""

    def __init__(
        self,
        threshold: int = 3,
        reset_timeout_sec: float = 60.0,
    ):
        self._threshold = threshold
        self._reset_timeout_sec = reset_timeout_sec
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._last_success_time: float = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        self._check_reset()
        return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking)."""
        return self.state == CircuitState.OPEN

    @property
    def allows_request(self) -> bool:
        """Check if a request is allowed."""
        state = self.state
        return state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def record_success(self) -> None:
        """Record a successful operation."""
        self._last_success_time = time.time()
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Record a failed operation."""
        self._last_failure_time = time.time()
        self._failure_count += 1

        if self._failure_count >= self._threshold:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self._failure_count} failures")

    def _check_reset(self) -> None:
        """Check if circuit should reset to half-open."""
        if self._state == CircuitState.OPEN:
            time_since_failure = time.time() - self._last_failure_time
            if time_since_failure >= self._reset_timeout_sec:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker moved to half-open state")


class CrashRecoveryManager:
    """
    Manages crash recovery for a plugin.

    Provides automatic restart with exponential backoff,
    state preservation, and crash history tracking.
    """

    def __init__(
        self,
        plugin_id: str,
        config: RecoveryConfig | None = None,
        restart_callback: Callable[[], Awaitable[bool]] | None = None,
    ):
        """
        Initialize the crash recovery manager.

        Args:
            plugin_id: Plugin identifier
            config: Recovery configuration
            restart_callback: Async function to call for restart
        """
        self._plugin_id = plugin_id
        self._config = config or RecoveryConfig()
        self._restart_callback = restart_callback

        self._crash_history: list[CrashEvent] = []
        self._restart_attempts: list[float] = []  # Timestamps
        self._preserved_state: PluginState | None = None
        self._circuit_breaker = CircuitBreaker(
            threshold=self._config.circuit_breaker_threshold,
            reset_timeout_sec=self._config.circuit_breaker_reset_sec,
        )
        self._lock = asyncio.Lock()
        self._restart_task: asyncio.Task | None = None

        # Initialize state directory
        if self._config.state_dir:
            self._config.state_dir.mkdir(parents=True, exist_ok=True)

    @property
    def plugin_id(self) -> str:
        """Get plugin ID."""
        return self._plugin_id

    @property
    def crash_count(self) -> int:
        """Get total crash count."""
        return len(self._crash_history)

    @property
    def recent_crash_count(self) -> int:
        """Get count of crashes within the restart window."""
        cutoff = datetime.now() - timedelta(seconds=self._config.restart_window_sec)
        return sum(1 for c in self._crash_history if c.timestamp > cutoff)

    @property
    def can_restart(self) -> bool:
        """Check if restart is allowed based on policy and limits."""
        if self._config.restart_policy == RestartPolicy.NEVER:
            return False

        if not self._circuit_breaker.allows_request:
            return False

        return not self.recent_crash_count >= self._config.max_restarts

    @property
    def preserved_state(self) -> PluginState | None:
        """Get the preserved state for this plugin."""
        return self._preserved_state

    @property
    def crash_history(self) -> list[CrashEvent]:
        """Get crash history."""
        return self._crash_history.copy()

    async def on_crash(
        self,
        exit_code: int | None = None,
        error_message: str | None = None,
        state_snapshot: dict[str, Any] | None = None,
    ) -> bool:
        """
        Handle a crash event.

        Args:
            exit_code: Process exit code
            error_message: Error message if available
            state_snapshot: State at time of crash

        Returns:
            True if restart was initiated, False otherwise
        """
        async with self._lock:
            # Record crash event
            event = CrashEvent(
                plugin_id=self._plugin_id,
                timestamp=datetime.now(),
                exit_code=exit_code,
                error_message=error_message,
                state_snapshot=state_snapshot,
            )
            self._crash_history.append(event)
            self._circuit_breaker.record_failure()

            logger.warning(
                f"Plugin {self._plugin_id} crashed: "
                f"exit_code={exit_code}, message={error_message}"
            )

            # Preserve state if enabled
            if self._config.preserve_state and state_snapshot:
                self._preserved_state = PluginState(
                    plugin_id=self._plugin_id,
                    last_active=datetime.now(),
                    invocation_context=state_snapshot.get("invocation_context", {}),
                    user_data=state_snapshot.get("user_data", {}),
                    capabilities_state=state_snapshot.get("capabilities_state", {}),
                )
                await self._save_state()

            # Save crash history
            await self._save_crash_history()

            # Check if we should restart
            if not self.can_restart:
                logger.info(
                    f"Plugin {self._plugin_id} will not be restarted: "
                    f"policy={self._config.restart_policy}, "
                    f"recent_crashes={self.recent_crash_count}, "
                    f"max={self._config.max_restarts}, "
                    f"circuit={self._circuit_breaker.state}"
                )
                return False

            # Schedule restart with backoff
            event.restart_attempted = True
            self._restart_task = asyncio.create_task(
                self._schedule_restart(len(self._restart_attempts))
            )

            return True

    async def _schedule_restart(self, attempt: int) -> bool:
        """
        Schedule a restart with exponential backoff.

        Args:
            attempt: Restart attempt number

        Returns:
            True if restart succeeded, False otherwise
        """
        delay = self._config.backoff.calculate_delay(attempt)
        logger.info(
            f"Scheduling restart for {self._plugin_id} in {delay:.2f}s " f"(attempt {attempt + 1})"
        )

        await asyncio.sleep(delay)

        # Double-check we can still restart
        if not self._circuit_breaker.allows_request:
            logger.warning(f"Restart cancelled for {self._plugin_id}: circuit breaker open")
            return False

        # Execute restart
        if self._restart_callback:
            try:
                success = await self._restart_callback()
                self._restart_attempts.append(time.time())

                if success:
                    self._circuit_breaker.record_success()
                    logger.info(f"Plugin {self._plugin_id} restarted successfully")

                    # Update last crash event
                    if self._crash_history:
                        self._crash_history[-1].restart_succeeded = True

                    return True
                else:
                    self._circuit_breaker.record_failure()
                    logger.warning(f"Plugin {self._plugin_id} restart failed")
                    return False

            except Exception as e:
                self._circuit_breaker.record_failure()
                logger.error(f"Error restarting {self._plugin_id}: {e}")
                return False
        else:
            logger.warning(f"No restart callback configured for {self._plugin_id}")
            return False

    def set_restart_callback(self, callback: Callable[[], Awaitable[bool]]) -> None:
        """Set the restart callback function."""
        self._restart_callback = callback

    async def preserve_state(
        self,
        invocation_context: dict[str, Any] | None = None,
        user_data: dict[str, Any] | None = None,
        capabilities_state: dict[str, Any] | None = None,
    ) -> None:
        """
        Preserve plugin state for recovery.

        Args:
            invocation_context: Current invocation context
            user_data: User data to preserve
            capabilities_state: Capability states to preserve
        """
        self._preserved_state = PluginState(
            plugin_id=self._plugin_id,
            last_active=datetime.now(),
            invocation_context=invocation_context or {},
            user_data=user_data or {},
            capabilities_state=capabilities_state or {},
        )
        await self._save_state()

    async def restore_state(self) -> PluginState | None:
        """
        Restore preserved state.

        Returns:
            The preserved state if available
        """
        if self._preserved_state:
            return self._preserved_state

        # Try loading from disk
        await self._load_state()
        return self._preserved_state

    async def clear_state(self) -> None:
        """Clear preserved state."""
        self._preserved_state = None

        if self._config.state_dir:
            state_file = self._config.state_dir / f"{self._plugin_id}_state.json"
            if state_file.exists():
                state_file.unlink()

    def reset(self) -> None:
        """Reset recovery state (clear history, reset circuit breaker)."""
        self._crash_history = []
        self._restart_attempts = []
        self._circuit_breaker = CircuitBreaker(
            threshold=self._config.circuit_breaker_threshold,
            reset_timeout_sec=self._config.circuit_breaker_reset_sec,
        )

    async def cancel_pending_restart(self) -> None:
        """Cancel any pending restart."""
        if self._restart_task and not self._restart_task.done():
            self._restart_task.cancel()
            try:
                await self._restart_task
            except asyncio.CancelledError:
                pass
            self._restart_task = None

    def get_stats(self) -> dict[str, Any]:
        """Get recovery statistics."""
        return {
            "plugin_id": self._plugin_id,
            "crash_count": self.crash_count,
            "recent_crash_count": self.recent_crash_count,
            "restart_attempts": len(self._restart_attempts),
            "can_restart": self.can_restart,
            "circuit_state": self._circuit_breaker.state.value,
            "has_preserved_state": self._preserved_state is not None,
            "config": {
                "restart_policy": self._config.restart_policy.value,
                "max_restarts": self._config.max_restarts,
                "restart_window_sec": self._config.restart_window_sec,
            },
        }

    async def _save_state(self) -> None:
        """Save preserved state to disk."""
        if not self._config.state_dir or not self._preserved_state:
            return

        state_file = self._config.state_dir / f"{self._plugin_id}_state.json"
        try:
            state_file.write_text(json.dumps(self._preserved_state.to_dict(), indent=2))
        except Exception as e:
            logger.error(f"Failed to save state for {self._plugin_id}: {e}")

    async def _load_state(self) -> None:
        """Load preserved state from disk."""
        if not self._config.state_dir:
            return

        state_file = self._config.state_dir / f"{self._plugin_id}_state.json"
        if not state_file.exists():
            return

        try:
            data = json.loads(state_file.read_text())
            self._preserved_state = PluginState.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load state for {self._plugin_id}: {e}")

    async def _save_crash_history(self) -> None:
        """Save crash history to disk."""
        if not self._config.state_dir:
            return

        history_file = self._config.state_dir / f"{self._plugin_id}_crashes.json"
        try:
            data = [e.to_dict() for e in self._crash_history[-100:]]  # Keep last 100
            history_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save crash history for {self._plugin_id}: {e}")

    async def load_crash_history(self) -> None:
        """Load crash history from disk."""
        if not self._config.state_dir:
            return

        history_file = self._config.state_dir / f"{self._plugin_id}_crashes.json"
        if not history_file.exists():
            return

        try:
            data = json.loads(history_file.read_text())
            self._crash_history = [CrashEvent.from_dict(e) for e in data]
        except Exception as e:
            logger.error(f"Failed to load crash history for {self._plugin_id}: {e}")


# Global recovery manager registry
_recovery_managers: dict[str, CrashRecoveryManager] = {}


def get_recovery_manager(
    plugin_id: str,
    config: RecoveryConfig | None = None,
) -> CrashRecoveryManager:
    """
    Get or create a recovery manager for a plugin.

    Args:
        plugin_id: Plugin identifier
        config: Optional recovery configuration

    Returns:
        CrashRecoveryManager instance
    """
    if plugin_id not in _recovery_managers:
        _recovery_managers[plugin_id] = CrashRecoveryManager(
            plugin_id=plugin_id,
            config=config,
        )
    return _recovery_managers[plugin_id]


def remove_recovery_manager(plugin_id: str) -> None:
    """Remove a recovery manager from the registry."""
    _recovery_managers.pop(plugin_id, None)


def get_all_recovery_stats() -> dict[str, dict[str, Any]]:
    """Get stats for all registered recovery managers."""
    return {pid: mgr.get_stats() for pid, mgr in _recovery_managers.items()}
