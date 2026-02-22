"""
OpenTelemetry Tracing Middleware — Phase 5.1.1

Provides distributed tracing integration using OpenTelemetry SDK.
Implements ADR-013 tracing architecture with local-first export options.

Features:
- Automatic span creation for HTTP requests
- Trace context propagation via W3C Trace Context headers
- Integration with correlation_id.py for ID consistency
- Local OTLP/JSON file export (no cloud required)
- Performance-optimized sampling

See ADR-013 for architecture decisions.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# OpenTelemetry imports with graceful fallback
try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SpanExporter,
        SpanExportResult,
    )
    from opentelemetry.trace import SpanKind, Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    TracerProvider = None
    SpanExporter = None

# OTLP exporter (optional, Phase 7 Sprint 2)
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )

    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False
    OTLPSpanExporter = None

# Local imports
from backend.platform.telemetry.telemetry import get_telemetry_service

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Environment-based configuration
_env_tracing = os.environ.get("VOICESTUDIO_TRACING_ENABLED", "true")
TRACING_ENABLED = _env_tracing.lower() == "true"
TRACING_SERVICE_NAME = os.environ.get("VOICESTUDIO_SERVICE_NAME", "voicestudio.backend")
_env_rate = os.environ.get("VOICESTUDIO_TRACE_SAMPLE_RATE", "1.0")
TRACING_SAMPLE_RATE = float(_env_rate)
TRACING_EXPORT_DIR = os.environ.get("VOICESTUDIO_TRACE_EXPORT_DIR", ".buildlogs/traces")

# Headers for trace propagation
TRACE_PARENT_HEADER = "traceparent"
TRACE_STATE_HEADER = "tracestate"
X_TRACE_ID_HEADER = "X-Trace-ID"
X_SPAN_ID_HEADER = "X-Span-ID"

# Paths to skip for tracing
SKIP_PATHS = frozenset(
    [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/healthz",
        "/ready",
        "/metrics",
        "/favicon.ico",
    ]
)


# =============================================================================
# Local File Exporter (No External Dependencies)
# =============================================================================

if TYPE_CHECKING:
    from opentelemetry.sdk.trace.export import SpanExporter as _ExporterBase
else:
    _ExporterBase = SpanExporter if OPENTELEMETRY_AVAILABLE else object


class LocalFileSpanExporter(_ExporterBase):
    """
    Exports spans to local JSON files for offline analysis.

    Consistent with local-first architecture - no cloud dependencies.
    """

    def __init__(self, export_dir: str = TRACING_EXPORT_DIR):
        self.export_dir = export_dir
        self._ensure_export_dir()

    def _ensure_export_dir(self) -> None:
        """Create export directory if it doesn't exist."""
        from pathlib import Path

        Path(self.export_dir).mkdir(parents=True, exist_ok=True)

    def export(self, spans) -> SpanExportResult:
        """Export spans to JSON file."""
        import json
        from datetime import datetime
        from pathlib import Path

        if not spans:
            return SpanExportResult.SUCCESS

        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            filepath = Path(self.export_dir) / f"trace-{timestamp}.json"

            span_data = []
            for span in spans:
                parent_id = None
                if span.parent:
                    parent_id = format(span.parent.span_id, "016x")
                span_data.append(
                    {
                        "trace_id": format(span.context.trace_id, "032x"),
                        "span_id": format(span.context.span_id, "016x"),
                        "parent_span_id": parent_id,
                        "name": span.name,
                        "start_time": span.start_time,
                        "end_time": span.end_time,
                        "status": span.status.status_code.name,
                        "attributes": dict(span.attributes or {}),
                    }
                )

            with open(filepath, "w") as f:
                json.dump({"spans": span_data, "exported_at": timestamp}, f, indent=2)

            return SpanExportResult.SUCCESS

        except Exception as e:
            logger.error(f"Failed to export spans to file: {e}")
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        """Clean shutdown."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush (no-op for file exporter)."""
        return True


# =============================================================================
# Tracer Configuration
# =============================================================================

_tracer_provider: TracerProvider | None = None
_tracer = None


def get_tracer():
    """Get the configured OpenTelemetry tracer."""
    global _tracer
    if _tracer is None and OPENTELEMETRY_AVAILABLE:
        _tracer = trace.get_tracer(TRACING_SERVICE_NAME)
    return _tracer


def setup_tracing(
    service_name: str = TRACING_SERVICE_NAME,
    export_to_console: bool = False,
    export_to_file: bool = True,
) -> TracerProvider | None:
    """
    Initialize OpenTelemetry tracing.

    Args:
        service_name: Service name for trace attribution
        export_to_console: Whether to export spans to console (debug)
        export_to_file: Whether to export spans to local files

    Returns:
        TracerProvider instance or None if OpenTelemetry not available
    """
    global _tracer_provider, _tracer

    if not OPENTELEMETRY_AVAILABLE:
        logger.warning(
            "OpenTelemetry not available - tracing disabled. "
            "Install opentelemetry-sdk for full tracing support."
        )
        return None

    if not TRACING_ENABLED:
        logger.info("Tracing disabled via VOICESTUDIO_TRACING_ENABLED")
        return None

    if _tracer_provider is not None:
        return _tracer_provider

    # Create resource with service info
    env_name = os.environ.get("VOICESTUDIO_ENV", "development")
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            "service.version": "1.0.1",
            "deployment.environment": env_name,
        }
    )

    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add exporters
    if export_to_console:
        _tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    if export_to_file:
        _tracer_provider.add_span_processor(BatchSpanProcessor(LocalFileSpanExporter()))

    # Phase 7: Optional OTLP export when VOICESTUDIO_OTLP_ENDPOINT is set
    otlp_endpoint = os.environ.get("VOICESTUDIO_OTLP_ENDPOINT")
    if otlp_endpoint and OTLP_AVAILABLE and OTLPSpanExporter:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("OTLP trace export enabled: %s", otlp_endpoint)
        except Exception as e:
            logger.warning("OTLP exporter setup failed: %s", e)

    # Set as global provider
    trace.set_tracer_provider(_tracer_provider)
    _tracer = trace.get_tracer(service_name)

    logger.info(
        f"OpenTelemetry tracing initialized: service={service_name}, "
        f"console={export_to_console}, file={export_to_file}"
    )

    return _tracer_provider


def shutdown_tracing() -> None:
    """Shutdown tracing and flush pending spans."""
    global _tracer_provider, _tracer

    if _tracer_provider is not None:
        _tracer_provider.shutdown()
        _tracer_provider = None
        _tracer = None
        logger.info("OpenTelemetry tracing shut down")


# =============================================================================
# Traced Decorator
# =============================================================================


def traced(
    name: str | None = None,
    attributes: dict[str, Any] | None = None,
    kind: SpanKind | None = None,
):
    """
    Decorator to trace a function with OpenTelemetry.

    Falls back to TelemetryService tracing if OpenTelemetry not available.

    Example:
        @traced("synthesize_voice", {"engine": "xtts"})
        async def synthesize(text: str) -> bytes:
            ...
    """

    def decorator(func: Callable):
        import asyncio
        import functools

        span_name = name or func.__name__
        span_attributes = attributes or {}
        span_kind = kind or SpanKind.INTERNAL if OPENTELEMETRY_AVAILABLE else None

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()

            if tracer and OPENTELEMETRY_AVAILABLE:
                with tracer.start_as_current_span(
                    span_name,
                    kind=span_kind,
                    attributes=span_attributes,
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            else:
                # Fallback to TelemetryService
                telemetry = get_telemetry_service()
                with telemetry.trace(span_name, span_attributes):
                    return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()

            if tracer and OPENTELEMETRY_AVAILABLE:
                with tracer.start_as_current_span(
                    span_name,
                    kind=span_kind,
                    attributes=span_attributes,
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            else:
                # Fallback to TelemetryService
                telemetry = get_telemetry_service()
                with telemetry.trace(span_name, span_attributes):
                    return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# =============================================================================
# OpenTelemetry Tracing Middleware
# =============================================================================


class OpenTelemetryMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for OpenTelemetry distributed tracing.

    Features:
    - Automatic span creation for all HTTP requests
    - W3C Trace Context propagation
    - Integration with correlation ID middleware
    - Sampling support for high-volume scenarios
    - Graceful fallback when OpenTelemetry not available
    """

    def __init__(
        self,
        app: ASGIApp,
        service_name: str = TRACING_SERVICE_NAME,
        enabled: bool = True,
        skip_paths: frozenset | None = None,
        sample_rate: float = TRACING_SAMPLE_RATE,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.enabled = enabled and TRACING_ENABLED
        self.skip_paths = skip_paths or SKIP_PATHS
        self.sample_rate = sample_rate
        if OPENTELEMETRY_AVAILABLE:
            self._propagator = TraceContextTextMapPropagator()
        else:
            self._propagator = None

    def _should_skip(self, path: str) -> bool:
        """Check if path should be skipped for tracing."""
        return any(path.startswith(skip) for skip in self.skip_paths)

    def _should_sample(self) -> bool:
        """Determine if this request should be sampled."""
        if self.sample_rate >= 1.0:
            return True
        import random

        return random.random() < self.sample_rate

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with OpenTelemetry tracing."""
        # Skip if disabled or path excluded
        if not self.enabled or self._should_skip(request.url.path):
            response: Response = await call_next(request)
            return response

        # Skip based on sampling
        if not self._should_sample():
            response = await call_next(request)
            return response

        tracer = get_tracer()

        # Fallback to basic correlation if OpenTelemetry not available
        if not tracer or not OPENTELEMETRY_AVAILABLE:
            response = await call_next(request)
            return response

        # Extract trace context from incoming headers
        carrier = dict(request.headers)
        context = self._propagator.extract(carrier)

        # Create span name
        span_name = f"{request.method} {request.url.path}"

        # Get correlation ID from middleware (if available)
        correlation_id = getattr(request.state, "correlation_id", None)

        # Build attributes
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        span_attrs = {
            "http.method": request.method,
            "http.url": str(request.url),
            "http.route": request.url.path,
            "http.scheme": request.url.scheme,
            "http.host": request.url.hostname or "unknown",
            "http.user_agent": user_agent,
            "net.peer.ip": client_ip,
            "correlation_id": correlation_id or "none",
        }

        # Start span with extracted context
        with tracer.start_as_current_span(
            span_name,
            context=context,
            kind=SpanKind.SERVER,
            attributes=span_attrs,
        ) as span:
            # Store trace info for response headers
            trace_id = format(span.get_span_context().trace_id, "032x")
            span_id = format(span.get_span_context().span_id, "016x")

            # GAP-I08: Set trace/span IDs on request state for dependencies
            request.state.trace_id = trace_id
            request.state.span_id = span_id

            # GAP-I08: Set context vars for logging
            from backend.api.middleware.correlation_id import (
                reset_trace_context,
                set_trace_context,
            )

            trace_tokens = set_trace_context(trace_id, span_id)

            try:
                response = await call_next(request)

                # Set response attributes
                span.set_attribute("http.status_code", response.status_code)

                if response.status_code >= 500:
                    err_msg = f"HTTP {response.status_code}"
                    span.set_status(Status(StatusCode.ERROR, err_msg))
                elif response.status_code >= 400:
                    err_msg = f"Client error {response.status_code}"
                    span.set_status(Status(StatusCode.ERROR, err_msg))
                else:
                    span.set_status(Status(StatusCode.OK))

                # Add trace headers to response
                response.headers[X_TRACE_ID_HEADER] = trace_id
                response.headers[X_SPAN_ID_HEADER] = span_id

                return response

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            finally:
                # GAP-I08: Reset trace context vars
                reset_trace_context(*trace_tokens)


# =============================================================================
# Setup Helpers
# =============================================================================


def setup_opentelemetry_middleware(
    app: ASGIApp,
    service_name: str = TRACING_SERVICE_NAME,
    enabled: bool = True,
    export_to_console: bool = False,
    export_to_file: bool = True,
) -> OpenTelemetryMiddleware | None:
    """
    Setup OpenTelemetry tracing for a FastAPI application.

    Args:
        app: FastAPI application
        service_name: Service name for traces
        enabled: Whether tracing is enabled
        export_to_console: Export spans to console (debug)
        export_to_file: Export spans to local files

    Returns:
        OpenTelemetryMiddleware instance or None

    Example:
        app = FastAPI()
        setup_opentelemetry_middleware(app)
    """
    # Initialize tracing
    setup_tracing(
        service_name=service_name,
        export_to_console=export_to_console,
        export_to_file=export_to_file,
    )

    if not OPENTELEMETRY_AVAILABLE or not TRACING_ENABLED:
        return None

    middleware = OpenTelemetryMiddleware(
        app,
        service_name=service_name,
        enabled=enabled,
    )

    return middleware


@contextmanager
def trace_operation(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> Generator[Any, None, None]:
    """
    Context manager for tracing an operation.

    Automatically uses OpenTelemetry if available, falls back to
    TelemetryService.

    Example:
        with trace_operation("process_audio", {"file": "input.wav"}):
            process_file("input.wav")
    """
    tracer = get_tracer()

    if tracer and OPENTELEMETRY_AVAILABLE:
        with tracer.start_as_current_span(
            name,
            kind=SpanKind.INTERNAL,
            attributes=attributes or {},
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    else:
        # Fallback to TelemetryService
        telemetry = get_telemetry_service()
        with telemetry.trace(name, attributes):
            yield None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Constants
    "OPENTELEMETRY_AVAILABLE",
    "TRACING_ENABLED",
    "X_SPAN_ID_HEADER",
    "X_TRACE_ID_HEADER",
    "LocalFileSpanExporter",
    # Classes
    "OpenTelemetryMiddleware",
    # Tracing utilities
    "get_tracer",
    "setup_opentelemetry_middleware",
    # Setup functions
    "setup_tracing",
    "shutdown_tracing",
    "trace_operation",
    "traced",
]
