"""
Resilience Module

Provides error recovery, retry logic, circuit breakers, health checks, and graceful degradation.
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    circuit_breaker,
    get_circuit_breaker,
)
from .graceful_degradation import (
    DegradationLevel,
    GracefulDegradation,
    graceful_degradation,
)
from .health_check import (
    HealthChecker,
    HealthCheckResult,
    HealthStatus,
    create_simple_check,
    get_health_checker,
)
from .retry import (
    NonRetryableError,
    RetryableError,
    RetryStrategy,
    is_retryable_error,
    retry,
    retry_with_backoff,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    # Circuit Breaker
    "CircuitState",
    # Graceful Degradation
    "DegradationLevel",
    "GracefulDegradation",
    "HealthCheckResult",
    "HealthChecker",
    # Health Check
    "HealthStatus",
    "NonRetryableError",
    # Retry
    "RetryStrategy",
    "RetryableError",
    "circuit_breaker",
    "create_simple_check",
    "get_circuit_breaker",
    "get_health_checker",
    "graceful_degradation",
    "is_retryable_error",
    "retry",
    "retry_with_backoff",
]

