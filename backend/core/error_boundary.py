# Copyright (c) VoiceStudio. All rights reserved.
# Licensed under the MIT License.

"""
Centralized error handling for VoiceStudio Python backend.

This module provides error boundary utilities that make logging the default path,
replacing bare except blocks with tracked, logged error handling.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ErrorResult(Generic[T]):
    """Result of an operation that may fail."""

    success: bool
    value: T | None = None
    error: Exception | None = None
    error_message: str | None = None

    @classmethod
    def ok(cls, value: T) -> "ErrorResult[T]":
        """Create a successful result."""
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: Exception, message: str | None = None) -> "ErrorResult[T]":
        """Create a failed result."""
        return cls(
            success=False,
            error=error,
            error_message=message or str(error),
        )

    def get_or_default(self, default: T) -> T:
        """Get the value or return the default."""
        return self.value if self.success and self.value is not None else default

    def get_or_raise(self) -> T:
        """Get the value or raise the stored exception."""
        if self.success:
            return self.value  # type: ignore
        raise self.error or RuntimeError(self.error_message or "Unknown error")


def try_execute(
    action: Callable[[], T],
    fallback: T,
    context: str = "",
    *,
    log_level: int = logging.WARNING,
    include_traceback: bool = True,
) -> T:
    """
    Execute an action with automatic logging on failure.

    Args:
        action: The callable to execute.
        fallback: The fallback value to return on failure.
        context: Optional context string for the error message.
        log_level: The logging level to use (default: WARNING).
        include_traceback: Whether to include traceback in logs (default: True).

    Returns:
        The result of the action, or the fallback value on failure.

    Example:
        >>> result = try_execute(
        ...     lambda: parse_config(path),
        ...     fallback={},
        ...     context="loading config"
        ... )
    """
    try:
        return action()
    except Exception as e:
        message = f"{context} failed: {e}" if context else f"Operation failed: {e}"
        logger.log(
            log_level,
            message,
            exc_info=include_traceback,
            extra={
                "exception_type": type(e).__name__,
                "context": context,
            },
        )
        return fallback


async def try_execute_async(
    action: Callable[[], Any],
    fallback: T,
    context: str = "",
    *,
    log_level: int = logging.WARNING,
    include_traceback: bool = True,
) -> T:
    """
    Execute an async action with automatic logging on failure.

    Args:
        action: The async callable to execute.
        fallback: The fallback value to return on failure.
        context: Optional context string for the error message.
        log_level: The logging level to use (default: WARNING).
        include_traceback: Whether to include traceback in logs (default: True).

    Returns:
        The result of the action, or the fallback value on failure.

    Example:
        >>> result = await try_execute_async(
        ...     lambda: fetch_data(url),
        ...     fallback=None,
        ...     context="fetching data"
        ... )
    """
    try:
        result = action()
        if asyncio.iscoroutine(result):
            return await result
        return result
    except Exception as e:
        message = f"{context} failed: {e}" if context else f"Operation failed: {e}"
        logger.log(
            log_level,
            message,
            exc_info=include_traceback,
            extra={
                "exception_type": type(e).__name__,
                "context": context,
            },
        )
        return fallback


def capture(
    action: Callable[[], T],
    context: str = "",
    *,
    log_level: int = logging.WARNING,
    include_traceback: bool = True,
) -> ErrorResult[T]:
    """
    Capture the result of an operation that may fail.

    Args:
        action: The callable to execute.
        context: Optional context string for the error message.
        log_level: The logging level to use (default: WARNING).
        include_traceback: Whether to include traceback in logs (default: True).

    Returns:
        An ErrorResult containing either the value or the error.

    Example:
        >>> result = capture(
        ...     lambda: parse_config(path),
        ...     context="loading config"
        ... )
        >>> if result.success:
        ...     config = result.value
        ... else:
        ...     print(f"Failed: {result.error_message}")
    """
    try:
        return ErrorResult.ok(action())
    except Exception as e:
        message = f"{context} failed: {e}" if context else f"Operation failed: {e}"
        logger.log(
            log_level,
            message,
            exc_info=include_traceback,
            extra={
                "exception_type": type(e).__name__,
                "context": context,
            },
        )
        return ErrorResult.fail(e, message)


def error_boundary(
    fallback: T = None,  # type: ignore
    context: str | None = None,
    log_level: int = logging.WARNING,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that wraps a function with error boundary handling.

    Args:
        fallback: The fallback value to return on failure.
        context: Optional context string for the error message.
        log_level: The logging level to use (default: WARNING).

    Returns:
        A decorator function.

    Example:
        >>> @error_boundary(fallback=[], context="loading items")
        ... def load_items():
        ...     return json.load(open("items.json"))
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            ctx = context or f"{func.__module__}.{func.__name__}"
            try:
                return func(*args, **kwargs)
            except Exception as e:
                message = f"{ctx} failed: {e}"
                logger.log(
                    log_level,
                    message,
                    exc_info=True,
                    extra={
                        "exception_type": type(e).__name__,
                        "context": ctx,
                        "function": func.__name__,
                    },
                )
                return fallback

        return wrapper

    return decorator


def async_error_boundary(
    fallback: T = None,  # type: ignore
    context: str | None = None,
    log_level: int = logging.WARNING,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that wraps an async function with error boundary handling.

    Args:
        fallback: The fallback value to return on failure.
        context: Optional context string for the error message.
        log_level: The logging level to use (default: WARNING).

    Returns:
        A decorator function.

    Example:
        >>> @async_error_boundary(fallback=None, context="fetching data")
        ... async def fetch_data(url):
        ...     async with aiohttp.ClientSession() as session:
        ...         return await session.get(url)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            ctx = context or f"{func.__module__}.{func.__name__}"
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                message = f"{ctx} failed: {e}"
                logger.log(
                    log_level,
                    message,
                    exc_info=True,
                    extra={
                        "exception_type": type(e).__name__,
                        "context": ctx,
                        "function": func.__name__,
                    },
                )
                return fallback

        return wrapper

    return decorator
