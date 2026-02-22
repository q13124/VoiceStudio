"""
Error Recovery Mechanisms

Provides automatic error recovery, retry logic, and fallback mechanisms for API operations.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, TypeVar

# Try to import resilience features
try:
    from app.core.resilience.circuit_breaker import CircuitBreaker, CircuitState
    from app.core.resilience.graceful_degradation import (
        DegradationLevel,
        GracefulDegradationHandler,
    )
    from app.core.resilience.retry import RetryConfig, RetryHelper, RetryStrategy

    HAS_RESILIENCE = True
except ImportError:
    HAS_RESILIENCE = False
    RetryHelper = None
    RetryStrategy = None
    RetryConfig = None
    CircuitBreaker = None
    CircuitState = None
    GracefulDegradationHandler = None
    DegradationLevel = None

# For type hints when imports are not available
if TYPE_CHECKING:
    from app.core.resilience.circuit_breaker import CircuitBreaker
    from app.core.resilience.graceful_degradation import GracefulDegradationHandler
    from app.core.resilience.retry import RetryConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorRecoveryManager:
    """Manages error recovery for API operations."""

    def __init__(self):
        """Initialize error recovery manager."""
        self.retry_helper = RetryHelper() if HAS_RESILIENCE and RetryHelper else None
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.degradation_handlers: dict[str, GracefulDegradationHandler] = {}

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker | None:
        """Get or create circuit breaker for a service."""
        if not HAS_RESILIENCE or not CircuitBreaker:
            return None

        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                name=service_name, failure_threshold=5, timeout=60.0
            )

        return self.circuit_breakers[service_name]

    def get_degradation_handler(self, operation_name: str) -> GracefulDegradationHandler | None:
        """Get or create graceful degradation handler for an operation."""
        if not HAS_RESILIENCE or not GracefulDegradationHandler:
            return None

        if operation_name not in self.degradation_handlers:
            handler = GracefulDegradationHandler(operation_name)
            self.degradation_handlers[operation_name] = handler

        return self.degradation_handlers[operation_name]

    def execute_with_recovery(
        self,
        func: Callable[[], T],
        service_name: str,
        operation_name: str,
        retry_config: RetryConfig | None = None,
        fallback: Callable[[], T] | None = None,
    ) -> T:
        """
        Execute function with error recovery mechanisms.

        Args:
            func: Function to execute
            service_name: Name of the service (for circuit breaker)
            operation_name: Name of the operation (for degradation)
            retry_config: Retry configuration
            fallback: Fallback function if operation fails

        Returns:
            Result of function execution
        """
        # Get circuit breaker
        circuit_breaker = self.get_circuit_breaker(service_name)

        # Get degradation handler
        degradation_handler = self.get_degradation_handler(operation_name)

        # Register fallback if provided
        if degradation_handler and fallback:
            degradation_handler.register_fallback(DegradationLevel.PARTIAL, fallback)

        # Execute with circuit breaker
        if circuit_breaker:
            try:
                return circuit_breaker.execute(func)
            except Exception as e:
                logger.warning(f"Circuit breaker triggered for {service_name}: {e}")
                # Try graceful degradation
                if degradation_handler and fallback:
                    try:
                        return degradation_handler.execute(fallback)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed for {operation_name}: {fallback_error}")
                        raise
                raise
        else:
            # Execute with retry if available
            if self.retry_helper and retry_config:
                return self.retry_helper.execute_with_retry(func, config=retry_config)
            else:
                # Direct execution
                return func()

    async def execute_with_recovery_async(
        self,
        func: Callable[[], Awaitable[T]],
        service_name: str,
        operation_name: str,
        retry_config: RetryConfig | None = None,
        fallback: Callable[[], Awaitable[T]] | None = None,
    ) -> T:
        """
        Execute async function with error recovery mechanisms.

        Args:
            func: Async function to execute
            service_name: Name of the service (for circuit breaker)
            operation_name: Name of the operation (for degradation)
            retry_config: Retry configuration
            fallback: Fallback async function if operation fails

        Returns:
            Result of function execution
        """
        # Get circuit breaker
        circuit_breaker = self.get_circuit_breaker(service_name)

        # Get degradation handler
        degradation_handler = self.get_degradation_handler(operation_name)

        # Register fallback if provided
        if degradation_handler and fallback:
            degradation_handler.register_fallback(DegradationLevel.PARTIAL, fallback)

        # Execute with circuit breaker
        if circuit_breaker:
            try:
                return await circuit_breaker.execute_async(func)
            except Exception as e:
                logger.warning(f"Circuit breaker triggered for {service_name}: {e}")
                # Try graceful degradation
                if degradation_handler and fallback:
                    try:
                        return await degradation_handler.execute_async(fallback)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed for {operation_name}: {fallback_error}")
                        raise
                raise
        else:
            # Execute with retry if available
            if self.retry_helper and retry_config:
                return await self.retry_helper.execute_with_retry_async(func, config=retry_config)
            else:
                # Direct execution
                return await func()


# Global error recovery manager
_error_recovery_manager: ErrorRecoveryManager | None = None


def get_error_recovery_manager() -> ErrorRecoveryManager:
    """Get or create global error recovery manager."""
    global _error_recovery_manager
    if _error_recovery_manager is None:
        _error_recovery_manager = ErrorRecoveryManager()
    return _error_recovery_manager


def with_error_recovery(
    service_name: str,
    operation_name: str | None = None,
    retry_config: RetryConfig | None = None,
    fallback: Callable | None = None,
):
    """
    Decorator for adding error recovery to functions.

    Args:
        service_name: Name of the service
        operation_name: Name of the operation (defaults to function name)
        retry_config: Retry configuration
        fallback: Fallback function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            manager = get_error_recovery_manager()
            op_name = operation_name or func.__name__
            return manager.execute_with_recovery(
                lambda: func(*args, **kwargs),
                service_name=service_name,
                operation_name=op_name,
                retry_config=retry_config,
                fallback=fallback,
            )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            manager = get_error_recovery_manager()
            op_name = operation_name or func.__name__
            return await manager.execute_with_recovery_async(
                lambda: func(*args, **kwargs),
                service_name=service_name,
                operation_name=op_name,
                retry_config=retry_config,
                fallback=fallback,
            )

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
