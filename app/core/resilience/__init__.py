"""
Resilience Module

Provides error recovery, retry logic, circuit breakers, health checks, and graceful degradation.
"""

from .retry import (
    RetryStrategy,
    RetryableError,
    NonRetryableError,
    is_retryable_error,
    retry_with_backoff,
    retry,
)

from .circuit_breaker import (
    CircuitState,
    CircuitBreaker,
    CircuitBreakerOpenError,
    get_circuit_breaker,
    circuit_breaker,
)

from .health_check import (
    HealthStatus,
    HealthCheckResult,
    HealthChecker,
    get_health_checker,
    create_simple_check,
)

from .graceful_degradation import (
    DegradationLevel,
    GracefulDegradation,
    graceful_degradation,
)

__all__ = [
    # Retry
    "RetryStrategy",
    "RetryableError",
    "NonRetryableError",
    "is_retryable_error",
    "retry_with_backoff",
    "retry",
    # Circuit Breaker
    "CircuitState",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "get_circuit_breaker",
    "circuit_breaker",
    # Health Check
    "HealthStatus",
    "HealthCheckResult",
    "HealthChecker",
    "get_health_checker",
    "create_simple_check",
    # Graceful Degradation
    "DegradationLevel",
    "GracefulDegradation",
    "graceful_degradation",
]

