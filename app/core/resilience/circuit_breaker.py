"""
Circuit Breaker Pattern Implementation

Provides circuit breaker functionality to prevent cascading failures.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from enum import Enum
from functools import wraps
from threading import Lock
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation.

    Prevents cascading failures by:
    - Opening circuit after failure threshold
    - Rejecting requests when open
    - Testing recovery in half-open state
    - Closing circuit when service recovers
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 2,
        name: str | None = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting recovery
            success_threshold: Number of successes in half-open to close circuit
            name: Optional name for circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.name = name or "default"

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.last_success_time: float | None = None

        self.lock = Lock()

        # Statistics
        self.total_requests = 0
        self.total_failures = 0
        self.total_rejections = 0
        self.total_successes = 0

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.timeout

    def _record_failure(self):
        """Record a failure."""
        with self.lock:
            self.failure_count += 1
            self.total_failures += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                # Failed in half-open, open circuit
                logger.warning(
                    f"Circuit breaker '{self.name}': Failed in half-open state, opening circuit"
                )
                self.state = CircuitState.OPEN
                self.success_count = 0
            elif self.failure_count >= self.failure_threshold:
                # Threshold reached, open circuit
                logger.warning(
                    f"Circuit breaker '{self.name}': Failure threshold reached ({self.failure_count}), "
                    f"opening circuit"
                )
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()

    def _record_success(self):
        """Record a success."""
        with self.lock:
            self.success_count += 1
            self.total_successes += 1
            self.last_success_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.success_threshold:
                    # Enough successes, close circuit
                    logger.info(
                        f"Circuit breaker '{self.name}': Success threshold reached ({self.success_count}), "
                        f"closing circuit"
                    )
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def _check_state(self):
        """Check and update circuit breaker state."""
        with self.lock:
            if self.state == CircuitState.OPEN and self._should_attempt_recovery():
                logger.info(
                    f"Circuit breaker '{self.name}': Timeout passed, entering half-open state"
                )
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If function fails
        """
        self._check_state()

        with self.lock:
            self.total_requests += 1

            if self.state == CircuitState.OPEN:
                self.total_rejections += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable. Try again later."
                )

        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Record success
            self._record_success()
            return cast(T, result)

        except Exception:
            # Record failure
            self._record_failure()
            raise

    def reset(self):
        """Manually reset circuit breaker to closed state."""
        with self.lock:
            logger.info(f"Circuit breaker '{self.name}': Manually reset")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        with self.lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_requests": self.total_requests,
                "total_failures": self.total_failures,
                "total_successes": self.total_successes,
                "total_rejections": self.total_rejections,
                "last_failure_time": self.last_failure_time,
                "last_success_time": self.last_success_time,
            }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""

    ...


# Global circuit breaker registry
_circuit_breakers: dict[str, CircuitBreaker] = {}
_breakers_lock = Lock()


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    success_threshold: int = 2,
) -> CircuitBreaker:
    """
    Get or create a circuit breaker.

    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Time before attempting recovery
        success_threshold: Number of successes to close

    Returns:
        Circuit breaker instance
    """
    with _breakers_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                timeout=timeout,
                success_threshold=success_threshold,
                name=name,
            )
        return _circuit_breakers[name]


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    success_threshold: int = 2,
):
    """
    Decorator for circuit breaker pattern.

    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Time before attempting recovery
        success_threshold: Number of successes to close
    """
    breaker = get_circuit_breaker(
        name=name,
        failure_threshold=failure_threshold,
        timeout=timeout,
        success_threshold=success_threshold,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            return await breaker.call(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # For sync functions, run in event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(breaker.call(func, *args, **kwargs))

        if asyncio.iscoroutinefunction(func):
            return cast(Callable[..., T], async_wrapper)
        else:
            return sync_wrapper

    return decorator
