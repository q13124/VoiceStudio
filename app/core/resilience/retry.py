"""
Retry Logic with Exponential Backoff

Provides retry functionality with exponential backoff, jitter, and configurable strategies.
"""

from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry strategies."""

    NONE = "none"
    IMMEDIATE = "immediate"
    EXPONENTIAL = "exponential"
    FIXED = "fixed"
    LINEAR = "linear"


class RetryableError(Exception):
    """Base exception for retryable errors."""

    ...


class NonRetryableError(Exception):
    """Base exception for non-retryable errors."""

    ...


def is_retryable_error(exception: Exception) -> bool:
    """
    Determine if an exception is retryable.

    Args:
        exception: Exception to check

    Returns:
        True if exception is retryable
    """
    # Network-related errors
    if isinstance(exception, (ConnectionError, TimeoutError, OSError)):
        return True

    # HTTP errors that might be transient
    if hasattr(exception, "status_code"):
        status_code = exception.status_code
        # 429 (rate limit), 500, 502, 503, 504 are retryable
        if status_code in (429, 500, 502, 503, 504):
            return True

    # Check if exception has is_retryable attribute
    if hasattr(exception, "is_retryable"):
        return bool(exception.is_retryable)

    # RetryableError is always retryable
    if isinstance(exception, RetryableError):
        return True

    # NonRetryableError is never retryable
    if isinstance(exception, NonRetryableError):
        return False

    # Default: don't retry unknown errors
    return False


def calculate_delay(
    attempt: int,
    strategy: RetryStrategy,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    fixed_delay: float = 1.0,
) -> float:
    """
    Calculate delay for retry attempt.

    Args:
        attempt: Current attempt number (0-indexed)
        strategy: Retry strategy
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Multiplier for exponential strategy
        fixed_delay: Fixed delay for fixed strategy

    Returns:
        Delay in seconds
    """
    if strategy == RetryStrategy.NONE or strategy == RetryStrategy.IMMEDIATE:
        return 0.0
    elif strategy == RetryStrategy.EXPONENTIAL:
        delay = initial_delay * (multiplier**attempt)
        return min(delay, max_delay)
    elif strategy == RetryStrategy.FIXED:
        return fixed_delay
    elif strategy == RetryStrategy.LINEAR:
        delay = initial_delay * (attempt + 1)
        return min(delay, max_delay)
    else:
        return initial_delay


def add_jitter(delay: float, jitter_factor: float = 0.1) -> float:
    """
    Add random jitter to delay to prevent thundering herd.

    Args:
        delay: Base delay in seconds
        jitter_factor: Jitter factor (0.0 to 1.0)

    Returns:
        Delay with jitter
    """
    if delay <= 0:
        return 0.0

    jitter = delay * jitter_factor * random.random()
    return delay + jitter


async def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    fixed_delay: float = 1.0,
    jitter_factor: float = 0.1,
    retryable_exceptions: list[type] | None = None,
    on_retry: Callable[[int, Exception], None] | None = None,
    *args,
    **kwargs,
) -> T:
    """
    Execute function with retry logic and exponential backoff.

    Args:
        func: Function to execute
        max_attempts: Maximum number of attempts
        strategy: Retry strategy
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Multiplier for exponential strategy
        fixed_delay: Fixed delay for fixed strategy
        jitter_factor: Jitter factor (0.0 to 1.0)
        retryable_exceptions: List of retryable exception types
        on_retry: Optional callback on retry (attempt, exception)
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            result: T
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result
        except Exception as e:
            last_exception = e

            # Check if exception is retryable
            is_retryable = False
            if retryable_exceptions:
                is_retryable = isinstance(e, tuple(retryable_exceptions))
            else:
                is_retryable = is_retryable_error(e)

            # Don't retry if not retryable or last attempt
            if not is_retryable or attempt == max_attempts - 1:
                logger.error(f"Operation failed after {attempt + 1} attempts: {e!s}", exc_info=True)
                raise

            # Calculate delay
            delay = calculate_delay(
                attempt, strategy, initial_delay, max_delay, multiplier, fixed_delay
            )

            # Add jitter
            delay = add_jitter(delay, jitter_factor)

            # Call on_retry callback
            if on_retry:
                try:
                    if asyncio.iscoroutinefunction(on_retry):
                        await on_retry(attempt + 1, e)
                    else:
                        on_retry(attempt + 1, e)
                except Exception as callback_error:
                    logger.warning(f"Error in retry callback: {callback_error}")

            logger.warning(
                f"Attempt {attempt + 1}/{max_attempts} failed: {e!s}. "
                f"Retrying in {delay:.2f}s..."
            )

            # Wait before retry
            await asyncio.sleep(delay)

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Operation failed but no exception was captured")


def retry(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    fixed_delay: float = 1.0,
    jitter_factor: float = 0.1,
    retryable_exceptions: list[type] | None = None,
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        strategy: Retry strategy
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Multiplier for exponential strategy
        fixed_delay: Fixed delay for fixed strategy
        jitter_factor: Jitter factor (0.0 to 1.0)
        retryable_exceptions: List of retryable exception types
        on_retry: Optional callback on retry (attempt, exception)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: object, **kwargs: object) -> T:
            return await retry_with_backoff(
                func,
                max_attempts,
                strategy,
                initial_delay,
                max_delay,
                multiplier,
                fixed_delay,
                jitter_factor,
                retryable_exceptions,
                on_retry,
                *args,
                **kwargs,
            )

        @wraps(func)
        def sync_wrapper(*args: object, **kwargs: object) -> T:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(
                retry_with_backoff(
                    func,
                    max_attempts,
                    strategy,
                    initial_delay,
                    max_delay,
                    multiplier,
                    fixed_delay,
                    jitter_factor,
                    retryable_exceptions,
                    on_retry,
                    *args,
                    **kwargs,
                )
            )

        if asyncio.iscoroutinefunction(func):
            return cast(Callable[..., T], async_wrapper)
        else:
            return sync_wrapper

    return decorator
