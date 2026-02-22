"""
Graceful Degradation System

Provides graceful degradation when services are unavailable or degraded.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DegradationLevel(Enum):
    """Degradation levels."""

    NONE = "none"  # Full functionality
    MINIMAL = "minimal"  # Minimal functionality
    LIMITED = "limited"  # Limited functionality
    DEGRADED = "degraded"  # Degraded functionality
    OFFLINE = "offline"  # Offline mode


class GracefulDegradation:
    """
    Graceful degradation handler.

    Provides fallback behavior when services are unavailable.
    """

    def __init__(self, name: str):
        """
        Initialize graceful degradation handler.

        Args:
            name: Handler name
        """
        self.name = name
        self.level = DegradationLevel.NONE
        self.fallbacks: dict[DegradationLevel, Callable] = {}

    def set_level(self, level: DegradationLevel):
        """
        Set degradation level.

        Args:
            level: Degradation level
        """
        if level != self.level:
            logger.info(
                f"Graceful degradation '{self.name}': Level changed from "
                f"{self.level.value} to {level.value}"
            )
            self.level = level

    def register_fallback(
        self,
        level: DegradationLevel,
        fallback_func: Callable,
    ):
        """
        Register fallback function for degradation level.

        Args:
            level: Degradation level
            fallback_func: Fallback function
        """
        self.fallbacks[level] = fallback_func

    async def execute(self, primary_func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with graceful degradation.

        Args:
            primary_func: Primary function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result or fallback result
        """
        # Try primary function first
        try:
            if asyncio.iscoroutinefunction(primary_func):
                result: T = await primary_func(*args, **kwargs)
                return result
            else:
                result = primary_func(*args, **kwargs)
                return cast(T, result)
        except Exception as e:
            logger.warning(
                f"Primary function failed in '{self.name}': {e}. "
                f"Attempting fallback (level: {self.level.value})"
            )

            # Try fallback based on current level
            fallback = self.fallbacks.get(self.level)
            if fallback:
                try:
                    if asyncio.iscoroutinefunction(fallback):
                        fb_result: T = await fallback(*args, **kwargs)
                        return fb_result
                    else:
                        return cast(T, fallback(*args, **kwargs))
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback also failed in '{self.name}': {fallback_error}",
                        exc_info=True,
                    )
                    raise

            # No fallback available, raise original error
            raise


def graceful_degradation(
    name: str,
    fallback_func: Callable | None = None,
    level: DegradationLevel = DegradationLevel.DEGRADED,
):
    """
    Decorator for graceful degradation.

    Args:
        name: Degradation handler name
        fallback_func: Optional fallback function
        level: Degradation level
    """
    handler = GracefulDegradation(name)
    if fallback_func:
        handler.register_fallback(level, fallback_func)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await handler.execute(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(handler.execute(func, *args, **kwargs))

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
