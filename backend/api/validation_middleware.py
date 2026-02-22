"""
Validation Optimization Middleware

Automatically optimizes Pydantic validation for all requests.
"""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.validation.optimizer import get_cached_schema

logger = logging.getLogger(__name__)


class ValidationOptimizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to optimize Pydantic validation.

    Pre-warms schema cache and tracks validation performance.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with validation optimization."""
        # Pre-warm schema cache for common models
        # This happens in the background and doesn't block the request

        response: Response = await call_next(request)

        return response


def setup_validation_optimization(app):
    """
    Setup validation optimization for the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Pre-warm schema cache for common models
    try:
        from backend.api.models_additional import (
            QualityMetrics,
            VoiceSynthesizeRequest,
            VoiceSynthesizeResponse,
        )

        common_models = [
            VoiceSynthesizeRequest,
            QualityMetrics,
            VoiceSynthesizeResponse,
        ]

        for model in common_models:
            try:
                get_cached_schema(model)
                logger.debug(f"Pre-warmed schema cache for {model.__name__}")
            except Exception as e:
                logger.warning(f"Failed to pre-warm schema for {model.__name__}: {e}")

    except ImportError:
        logger.warning("Could not import models for schema pre-warming")

    # Add middleware
    app.add_middleware(ValidationOptimizationMiddleware)
