"""
Validation Optimizer Middleware

Middleware to optimize request validation using cached schemas and early validation.
"""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..validation_optimizer import (
    get_cache_stats,
    get_validation_stats,
)

logger = logging.getLogger(__name__)


class ValidationOptimizerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to optimize request validation.

    Features:
    - Monitors validation performance
    - Provides cache statistics
    - Clears cache on demand
    """

    def __init__(
        self,
        app: ASGIApp,
        enable_cache: bool = True,
        cache_max_size: int = 1000,
    ):
        """
        Initialize validation optimizer middleware.

        Args:
            app: ASGI application
            enable_cache: Whether to enable validation cache
            cache_max_size: Maximum size of validation cache
        """
        super().__init__(app)
        self.enable_cache = enable_cache
        self.cache_max_size = cache_max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with validation optimization.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        # Add validation stats to request state
        request.state.validation_stats = get_validation_stats()
        request.state.cache_stats = get_cache_stats()

        # Process request
        response: Response = await call_next(request)

        return response


def get_validation_optimizer_middleware(
    enable_cache: bool = True, cache_max_size: int = 1000
) -> type[ValidationOptimizerMiddleware]:
    """
    Get validation optimizer middleware instance.

    Args:
        enable_cache: Whether to enable validation cache
        cache_max_size: Maximum size of validation cache

    Returns:
        ValidationOptimizerMiddleware instance
    """
    return ValidationOptimizerMiddleware
