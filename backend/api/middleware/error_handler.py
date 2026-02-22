"""
Engine Error Handler Middleware

GAP-I09: Provides consistent HTTP status code mapping for engine errors.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)

# Import EngineError and EngineErrorCode from the engine layer
try:
    from app.core.engines.base import EngineError, EngineErrorCode

    HAS_ENGINE_ERROR = True
except ImportError:
    HAS_ENGINE_ERROR = False
    EngineError = None
    EngineErrorCode = None
    logger.warning("EngineError not available; error handler middleware will be limited")


# GAP-I09: Map EngineErrorCode to HTTP status codes
ENGINE_ERROR_TO_HTTP: dict[str, int] = {
    # Client errors (4xx)
    "INVALID_INPUT": 400,
    "UNSUPPORTED_TASK": 400,
    "VALIDATION_FAILED": 422,
    "MODEL_NOT_FOUND": 404,
    "ENGINE_NOT_FOUND": 404,
    "CANCELLED": 499,  # Client Closed Request (nginx convention)
    # Server errors (5xx)
    "INTERNAL": 500,
    "GPU_OOM": 503,
    "RESOURCE_EXHAUSTED": 503,
    "ENGINE_UNHEALTHY": 503,
    "INITIALIZATION_FAILED": 503,
    "BUSY": 503,
    "TIMEOUT": 504,
}

# Default status code for unknown error codes
DEFAULT_ERROR_STATUS = 500


class EngineErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches EngineError exceptions and converts them
    to appropriate HTTP responses with consistent status codes.

    GAP-I09: Ensures all engine errors are mapped to consistent HTTP codes.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            return self._handle_exception(request, exc)

    def _handle_exception(self, request: Request, exc: Exception) -> Response:
        """Handle an exception and return an appropriate HTTP response."""

        # Handle EngineError specifically
        if HAS_ENGINE_ERROR and isinstance(exc, EngineError):
            return self._handle_engine_error(request, exc)

        # Let other exceptions propagate (handled by FastAPI's default handler)
        raise exc

    def _handle_engine_error(self, request: Request, error: EngineError) -> JSONResponse:
        """
        Convert an EngineError to a JSON response with appropriate status code.

        Args:
            request: The incoming request
            error: The EngineError exception

        Returns:
            JSONResponse with error details and mapped status code
        """
        error_code_name = error.code.name
        status_code = ENGINE_ERROR_TO_HTTP.get(error_code_name, DEFAULT_ERROR_STATUS)

        # Build response body
        response_body: dict[str, Any] = {
            "error": error_code_name,
            "message": error.message,
            "status_code": status_code,
        }

        # Include details if present (but sanitize for security)
        if error.details:
            # Only include safe details, not internal stack traces
            safe_details = {
                k: v
                for k, v in error.details.items()
                if k not in ("stack_trace", "internal_state", "credentials")
            }
            if safe_details:
                response_body["details"] = safe_details

        # Log the error with appropriate level
        if status_code >= 500:
            logger.error(
                "Engine error [%s] on %s %s: %s",
                error_code_name,
                request.method,
                request.url.path,
                error.message,
                exc_info=error.cause if error.cause else error,
            )
        else:
            logger.warning(
                "Engine error [%s] on %s %s: %s",
                error_code_name,
                request.method,
                request.url.path,
                error.message,
            )

        return JSONResponse(status_code=status_code, content=response_body)


def get_http_status_for_engine_error(error_code: str | Any) -> int:
    """
    Get the HTTP status code for an engine error code.

    Args:
        error_code: Either an EngineErrorCode enum value or a string code name

    Returns:
        HTTP status code (int)
    """
    if hasattr(error_code, "name"):
        code_name = error_code.name
    else:
        code_name = str(error_code)

    return ENGINE_ERROR_TO_HTTP.get(code_name, DEFAULT_ERROR_STATUS)
