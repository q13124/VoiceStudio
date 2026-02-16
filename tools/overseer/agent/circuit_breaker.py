"""
Circuit Breaker

Implements circuit breaker pattern for agent governance.
Auto-quarantines agents on repeated failures or denied actions.
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class CircuitState(str, Enum):
    """State of a circuit breaker."""

    CLOSED = "Closed"         # Normal operation
    OPEN = "Open"             # Tripped, blocking actions
    HALF_OPEN = "HalfOpen"    # Testing if recovery is possible


@dataclass
class CircuitConfig:
    """
    Configuration for a circuit breaker.

    Attributes:
        denied_action_threshold: Number of denied actions to trigger trip
        denied_action_window_minutes: Time window for denied action counting
        failure_threshold: Number of failures to trigger trip
        failure_window_minutes: Time window for failure counting
        initial_delay_seconds: Initial backoff delay
        max_delay_seconds: Maximum backoff delay
        backoff_multiplier: Multiplier for exponential backoff
        recovery_timeout_seconds: Time before attempting recovery
    """

    denied_action_threshold: int = 3
    denied_action_window_minutes: int = 5
    failure_threshold: int = 5
    failure_window_minutes: int = 10
    initial_delay_seconds: float = 5.0
    max_delay_seconds: float = 300.0
    backoff_multiplier: float = 2.0
    recovery_timeout_seconds: float = 60.0

    @classmethod
    def from_policy(cls, policy_config: dict) -> CircuitConfig:
        """Create from policy configuration."""
        cb_config = policy_config.get("circuit_breaker", {})
        backoff = cb_config.get("backoff", {})

        return cls(
            denied_action_threshold=cb_config.get("denied_action_threshold", 3),
            denied_action_window_minutes=cb_config.get("denied_action_window_minutes", 5),
            failure_threshold=cb_config.get("failure_threshold", 5),
            failure_window_minutes=cb_config.get("failure_window_minutes", 10),
            initial_delay_seconds=backoff.get("initial_delay_seconds", 5.0),
            max_delay_seconds=backoff.get("max_delay_seconds", 300.0),
            backoff_multiplier=backoff.get("multiplier", 2.0),
        )


@dataclass
class CircuitEvent:
    """An event tracked by the circuit breaker."""

    timestamp: datetime
    event_type: str  # "denied" or "failure"
    tool_name: str
    reason: str = ""


class CircuitBreaker:
    """
    Circuit breaker for an individual agent.

    Tracks denied actions and failures, triggering quarantine
    when thresholds are exceeded.
    """

    def __init__(
        self,
        agent_id: str,
        config: CircuitConfig | None = None,
        on_trip: Callable[[str, str], None] | None = None,
        on_reset: Callable[[str], None] | None = None,
    ):
        """
        Initialize a circuit breaker.

        Args:
            agent_id: ID of the agent this breaker protects
            config: Circuit breaker configuration
            on_trip: Callback when circuit trips (agent_id, reason)
            on_reset: Callback when circuit resets (agent_id)
        """
        self._agent_id = agent_id
        self._config = config or CircuitConfig()
        self._on_trip = on_trip
        self._on_reset = on_reset

        self._state = CircuitState.CLOSED
        self._events: deque[CircuitEvent] = deque()
        self._trip_count = 0
        self._current_delay = self._config.initial_delay_seconds
        self._last_trip_time: datetime | None = None
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._check_recovery()
            return self._state

    @property
    def agent_id(self) -> str:
        """Get the agent ID."""
        return self._agent_id

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking)."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal)."""
        return self.state == CircuitState.CLOSED

    @property
    def trip_count(self) -> int:
        """Get number of times circuit has tripped."""
        return self._trip_count

    @property
    def time_until_recovery(self) -> timedelta | None:
        """Get time until recovery attempt."""
        with self._lock:
            if self._state != CircuitState.OPEN or self._last_trip_time is None:
                return None

            recovery_at = self._last_trip_time + timedelta(seconds=self._current_delay)
            remaining = recovery_at - datetime.now()

            return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def record_denied(self, tool_name: str, reason: str = "") -> bool:
        """
        Record a denied action.

        Args:
            tool_name: Name of the denied tool
            reason: Reason for denial

        Returns:
            True if circuit tripped as a result
        """
        event = CircuitEvent(
            timestamp=datetime.now(),
            event_type="denied",
            tool_name=tool_name,
            reason=reason,
        )

        with self._lock:
            self._events.append(event)
            self._cleanup_old_events()

            if self._should_trip_on_denials():
                self._trip(f"Exceeded denial threshold: {self._count_recent_denials()} denials")
                return True

        return False

    def record_failure(self, tool_name: str, reason: str = "") -> bool:
        """
        Record a failure.

        Args:
            tool_name: Name of the failed tool
            reason: Reason for failure

        Returns:
            True if circuit tripped as a result
        """
        event = CircuitEvent(
            timestamp=datetime.now(),
            event_type="failure",
            tool_name=tool_name,
            reason=reason,
        )

        with self._lock:
            self._events.append(event)
            self._cleanup_old_events()

            if self._should_trip_on_failures():
                self._trip(f"Exceeded failure threshold: {self._count_recent_failures()} failures")
                return True

        return False

    def record_success(self) -> None:
        """Record a successful action (helps recovery)."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._reset()

    def force_trip(self, reason: str) -> None:
        """Force the circuit to trip."""
        with self._lock:
            self._trip(reason)

    def force_reset(self) -> None:
        """Force the circuit to reset."""
        with self._lock:
            self._reset()

    def _cleanup_old_events(self) -> None:
        """Remove events outside the tracking window."""
        # Use the larger of the two windows
        max_window = max(
            self._config.denied_action_window_minutes,
            self._config.failure_window_minutes,
        )
        cutoff = datetime.now() - timedelta(minutes=max_window)

        while self._events and self._events[0].timestamp < cutoff:
            self._events.popleft()

    def _count_recent_denials(self) -> int:
        """Count recent denied actions."""
        cutoff = datetime.now() - timedelta(
            minutes=self._config.denied_action_window_minutes
        )
        return sum(
            1 for e in self._events
            if e.event_type == "denied" and e.timestamp >= cutoff
        )

    def _count_recent_failures(self) -> int:
        """Count recent failures."""
        cutoff = datetime.now() - timedelta(
            minutes=self._config.failure_window_minutes
        )
        return sum(
            1 for e in self._events
            if e.event_type == "failure" and e.timestamp >= cutoff
        )

    def _should_trip_on_denials(self) -> bool:
        """Check if denial threshold exceeded."""
        return (
            self._state == CircuitState.CLOSED
            and self._count_recent_denials() >= self._config.denied_action_threshold
        )

    def _should_trip_on_failures(self) -> bool:
        """Check if failure threshold exceeded."""
        return (
            self._state == CircuitState.CLOSED
            and self._count_recent_failures() >= self._config.failure_threshold
        )

    def _trip(self, reason: str) -> None:
        """Trip the circuit."""
        self._state = CircuitState.OPEN
        self._trip_count += 1
        self._last_trip_time = datetime.now()

        # Exponential backoff
        self._current_delay = min(
            self._current_delay * self._config.backoff_multiplier,
            self._config.max_delay_seconds,
        )

        if self._on_trip:
            self._on_trip(self._agent_id, reason)

    def _reset(self) -> None:
        """Reset the circuit."""
        self._state = CircuitState.CLOSED
        self._current_delay = self._config.initial_delay_seconds
        self._events.clear()

        if self._on_reset:
            self._on_reset(self._agent_id)

    def _check_recovery(self) -> None:
        """Check if it's time to attempt recovery."""
        if self._state != CircuitState.OPEN:
            return

        if self._last_trip_time is None:
            return

        elapsed = (datetime.now() - self._last_trip_time).total_seconds()

        if elapsed >= self._current_delay:
            self._state = CircuitState.HALF_OPEN

    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "agent_id": self._agent_id,
                "state": self._state.value,
                "trip_count": self._trip_count,
                "recent_denials": self._count_recent_denials(),
                "recent_failures": self._count_recent_failures(),
                "current_delay_seconds": self._current_delay,
                "time_until_recovery": (
                    self.time_until_recovery.total_seconds()
                    if self.time_until_recovery
                    else None
                ),
            }


class CircuitBreakerManager:
    """
    Manages circuit breakers for multiple agents.
    """

    def __init__(
        self,
        config: CircuitConfig | None = None,
        on_trip: Callable[[str, str], None] | None = None,
        on_reset: Callable[[str], None] | None = None,
    ):
        """
        Initialize the manager.

        Args:
            config: Default configuration for new breakers
            on_trip: Default callback when any circuit trips
            on_reset: Default callback when any circuit resets
        """
        self._config = config or CircuitConfig()
        self._on_trip = on_trip
        self._on_reset = on_reset
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_breaker(self, agent_id: str) -> CircuitBreaker:
        """Get or create a circuit breaker for an agent."""
        with self._lock:
            if agent_id not in self._breakers:
                self._breakers[agent_id] = CircuitBreaker(
                    agent_id=agent_id,
                    config=self._config,
                    on_trip=self._on_trip,
                    on_reset=self._on_reset,
                )
            return self._breakers[agent_id]

    def remove_breaker(self, agent_id: str) -> bool:
        """Remove a circuit breaker."""
        with self._lock:
            if agent_id in self._breakers:
                del self._breakers[agent_id]
                return True
            return False

    def is_agent_blocked(self, agent_id: str) -> bool:
        """Check if an agent is blocked by its circuit breaker."""
        breaker = self.get_breaker(agent_id)
        return breaker.is_open

    def trip_all(self, reason: str) -> int:
        """Trip all circuit breakers (emergency stop)."""
        count = 0
        with self._lock:
            for breaker in self._breakers.values():
                if breaker.is_closed:
                    breaker.force_trip(reason)
                    count += 1
        return count

    def reset_all(self) -> int:
        """Reset all circuit breakers."""
        count = 0
        with self._lock:
            for breaker in self._breakers.values():
                if not breaker.is_closed:
                    breaker.force_reset()
                    count += 1
        return count

    def get_tripped_agents(self) -> list[str]:
        """Get list of agents with tripped circuits."""
        with self._lock:
            return [
                agent_id for agent_id, breaker in self._breakers.items()
                if breaker.is_open
            ]

    def get_stats(self) -> dict:
        """Get statistics for all circuit breakers."""
        with self._lock:
            return {
                "total_breakers": len(self._breakers),
                "tripped": len(self.get_tripped_agents()),
                "breakers": {
                    agent_id: breaker.get_stats()
                    for agent_id, breaker in self._breakers.items()
                },
            }
