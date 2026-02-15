"""
Telemetry Middleware — TASK-CP-003

Integrates TelemetryService with FastAPI for request tracing and metrics.
Works alongside PerformanceMonitoringMiddleware for comprehensive observability.

Features:
- Span-based request tracing with trace_id propagation
- Integration with TelemetryService metrics
- Request/response logging with structured format
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.services.telemetry import (
    SpanStatus,
    TelemetryService,
    get_telemetry_service,
)

logger = logging.getLogger(__name__)

# Header for trace ID propagation
TRACE_ID_HEADER = "X-Trace-ID"
SPAN_ID_HEADER = "X-Span-ID"


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request tracing and telemetry integration.

    Creates a span for each request, propagates trace IDs via headers,
    and records request metrics to the TelemetryService.
    """

    def __init__(
        self,
        app: ASGIApp,
        telemetry: TelemetryService | None = None,
        enabled: bool = True,
        skip_paths: list | None = None,
    ):
        """
        Initialize telemetry middleware.

        Args:
            app: ASGI application
            telemetry: TelemetryService instance (uses global if None)
            enabled: Whether telemetry is enabled
            skip_paths: Paths to skip tracing (e.g., /docs, /health)
        """
        super().__init__(app)
        self._telemetry = telemetry
        self.enabled = enabled
        self.skip_paths = skip_paths or ["/docs", "/redoc", "/openapi.json"]

    @property
    def telemetry(self) -> TelemetryService:
        if self._telemetry is None:
            self._telemetry = get_telemetry_service()
        return self._telemetry

    def _should_skip(self, path: str) -> bool:
        """Check if path should be skipped for tracing."""
        return any(path.startswith(skip) for skip in self.skip_paths)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with tracing."""
        if not self.enabled or self._should_skip(request.url.path):
            return await call_next(request)

        # Extract or generate trace ID
        trace_id = request.headers.get(TRACE_ID_HEADER, uuid.uuid4().hex[:16])
        span_name = f"{request.method} {request.url.path}"

        start_time = time.perf_counter()
        status_code = 500
        error_message = None

        try:
            with self.telemetry.trace(
                span_name,
                attributes={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.path": request.url.path,
                    "http.query": str(request.query_params),
                },
            ) as span:
                # Process request
                response = await call_next(request)
                status_code = response.status_code

                # Set span attributes
                span.set_attribute("http.status_code", status_code)

                if status_code >= 400:
                    span.set_status(
                        SpanStatus.ERROR if status_code >= 500 else SpanStatus.OK,
                        f"HTTP {status_code}",
                    )

                # Add trace headers to response
                response.headers[TRACE_ID_HEADER] = trace_id
                response.headers[SPAN_ID_HEADER] = span.span_id

                return response

        except Exception as e:
            error_message = str(e)
            raise

        finally:
            # Record metrics
            duration_seconds = time.perf_counter() - start_time
            self.telemetry.record_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_seconds=duration_seconds,
            )

            if error_message:
                self.telemetry.record_error("request_exception", request.url.path)


# Global middleware instance
_telemetry_middleware: TelemetryMiddleware | None = None


def get_telemetry_middleware() -> TelemetryMiddleware | None:
    """Get the global telemetry middleware instance."""
    return _telemetry_middleware


def setup_telemetry_middleware(
    app: ASGIApp,
    enabled: bool = True,
    telemetry: TelemetryService | None = None,
) -> TelemetryMiddleware:
    """
    Setup telemetry middleware on an ASGI app.

    Args:
        app: FastAPI application
        enabled: Whether telemetry is enabled
        telemetry: Optional TelemetryService instance

    Returns:
        TelemetryMiddleware instance
    """
    global _telemetry_middleware
    _telemetry_middleware = TelemetryMiddleware(app, telemetry=telemetry, enabled=enabled)
    return _telemetry_middleware
