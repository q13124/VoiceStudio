"""
API Endpoint Performance Monitoring Middleware

Tracks response times, error rates, and provides comprehensive
API endpoint performance monitoring.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


@dataclass
class EndpointMetrics:
    """Metrics for an API endpoint."""

    path: str
    method: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    avg_time: float = 0.0
    total_request_size: int = 0
    total_response_size: int = 0
    avg_request_size: float = 0.0
    avg_response_size: float = 0.0
    errors: int = 0
    error_rate: float = 0.0
    status_codes: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    last_called: datetime | None = None
    # Timing history for percentile calculations (last 1000 requests)
    _timing_history: list[float] = field(default_factory=list)
    _max_history_size: int = 1000

    def update(
        self,
        execution_time: float,
        request_size: int = 0,
        response_size: int = 0,
        status_code: int = 200,
    ):
        """Update metrics with new request data (enhanced)."""
        self.call_count += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = self.total_time / self.call_count
        self.total_request_size += request_size
        self.total_response_size += response_size
        self.avg_request_size = self.total_request_size / self.call_count
        self.avg_response_size = self.total_response_size / self.call_count
        self.status_codes[status_code] += 1
        self.last_called = datetime.now()

        # Store timing for percentile calculations
        self._timing_history.append(execution_time)
        if len(self._timing_history) > self._max_history_size:
            self._timing_history = self._timing_history[-self._max_history_size:]

        # Update error rate
        if status_code >= 400:
            self.errors += 1
        self.error_rate = self.errors / self.call_count if self.call_count > 0 else 0.0

    def get_percentiles(self) -> dict[str, float]:
        """Get percentile statistics for response times."""
        if not self._timing_history:
            return {}

        sorted_times = sorted(self._timing_history)
        n = len(sorted_times)

        return {
            "p50": sorted_times[n // 2] if n > 0 else 0.0,
            "p95": sorted_times[int(n * 0.95)] if n > 0 else 0.0,
            "p99": sorted_times[int(n * 0.99)] if n > 0 else 0.0,
        }


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring API endpoint performance.

    Tracks:
    - Response times
    - Request/response sizes
    - Error rates
    - Status codes
    - Endpoint statistics
    """

    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        track_request_size: bool = True,
        track_response_size: bool = True,
        slow_threshold_seconds: float = 1.0,
        warn_on_slow: bool = True,
    ):
        """
        Initialize performance monitoring middleware (enhanced).

        Args:
            app: ASGI application
            enabled: Whether monitoring is enabled
            track_request_size: Whether to track request sizes
            track_response_size: Whether to track response sizes
            slow_threshold_seconds: Threshold for slow endpoint warnings
            warn_on_slow: Whether to log warnings for slow endpoints
        """
        super().__init__(app)
        self.enabled = enabled
        self.track_request_size = track_request_size
        self.track_response_size = track_response_size
        self.slow_threshold_seconds = slow_threshold_seconds
        self.warn_on_slow = warn_on_slow
        self._metrics: dict[str, EndpointMetrics] = {}
        self._lock = None

        # Import threading lock
        try:
            from threading import Lock

            self._lock = Lock()
        except ImportError:
            logger.warning("Threading not available, metrics may not be thread-safe")

    def _get_endpoint_key(self, path: str, method: str) -> str:
        """Get unique key for endpoint."""
        return f"{method}:{path}"

    def _get_request_size(self, request: Request) -> int:
        """Get request size in bytes."""
        if not self.track_request_size:
            return 0

        size = 0
        # Headers size (approximate)
        for key, value in request.headers.items():
            size += len(key.encode()) + len(value.encode())

        # Query params size (approximate)
        if request.url.query:
            size += len(request.url.query.encode())

        # Body size (if available)
        if hasattr(request, "_body"):
            body = getattr(request, "_body", b"")
            if body:
                size += len(body)

        return size

    def _get_response_size(self, response: Response) -> int:
        """Get response size in bytes."""
        if not self.track_response_size:
            return 0

        size = 0
        # Headers size (approximate)
        for key, value in response.headers.items():
            size += len(key.encode()) + len(value.encode())

        # Body size (if available)
        if hasattr(response, "body"):
            body = getattr(response, "body", b"")
            if body:
                size += len(body)

        return size

    async def dispatch(self, request: Request, call_next):
        """Process request and track performance metrics."""
        if not self.enabled:
            return await call_next(request)

        # Skip monitoring for certain paths
        if request.url.path.startswith("/docs") or request.url.path.startswith(
            "/redoc"
        ):
            return await call_next(request)

        start_time = time.perf_counter()
        endpoint_key = self._get_endpoint_key(request.url.path, request.method)
        request_size = self._get_request_size(request)

        try:
            response = await call_next(request)
            execution_time = time.perf_counter() - start_time
            response_size = self._get_response_size(response)
            status_code = response.status_code

            # Update metrics
            if self._lock:
                with self._lock:
                    self._update_metrics(
                        endpoint_key,
                        request.url.path,
                        request.method,
                        execution_time,
                        request_size,
                        response_size,
                        status_code,
                    )
            else:
                self._update_metrics(
                    endpoint_key,
                    request.url.path,
                    request.method,
                    execution_time,
                    request_size,
                    response_size,
                    status_code,
                )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{execution_time:.4f}"
            response.headers["X-Endpoint"] = endpoint_key

            # Warn on slow endpoints
            if (
                self.warn_on_slow
                and execution_time > self.slow_threshold_seconds
            ):
                logger.warning(
                    f"Slow endpoint detected: {endpoint_key} took "
                    f"{execution_time:.3f}s (threshold: "
                    f"{self.slow_threshold_seconds}s)"
                )

            return response
        except Exception:
            execution_time = time.perf_counter() - start_time
            status_code = 500

            # Update metrics with error
            if self._lock:
                with self._lock:
                    self._update_metrics(
                        endpoint_key,
                        request.url.path,
                        request.method,
                        execution_time,
                        request_size,
                        0,
                        status_code,
                    )
            else:
                self._update_metrics(
                    endpoint_key,
                    request.url.path,
                    request.method,
                    execution_time,
                    request_size,
                    0,
                    status_code,
                )

            raise

    def _update_metrics(
        self,
        endpoint_key: str,
        path: str,
        method: str,
        execution_time: float,
        request_size: int,
        response_size: int,
        status_code: int,
    ):
        """Update metrics for an endpoint."""
        if endpoint_key not in self._metrics:
            self._metrics[endpoint_key] = EndpointMetrics(path=path, method=method)

        self._metrics[endpoint_key].update(
            execution_time, request_size, response_size, status_code
        )

    def get_metrics(self, endpoint: str | None = None) -> dict[str, Any]:
        """
        Get performance metrics.

        Args:
            endpoint: Optional endpoint key to get metrics for

        Returns:
            Metrics dictionary
        """
        if endpoint:
            if endpoint in self._metrics:
                return self._serialize_metrics(self._metrics[endpoint])
            return {}

        # Return all metrics
        return {
            key: self._serialize_metrics(metrics)
            for key, metrics in self._metrics.items()
        }

    def get_stats(self) -> dict[str, Any]:
        """Get overall statistics."""
        if not self._metrics:
            return {
                "enabled": self.enabled,
                "total_endpoints": 0,
                "total_requests": 0,
                "total_time": 0.0,
            }

        total_requests = sum(m.call_count for m in self._metrics.values())
        total_time = sum(m.total_time for m in self._metrics.values())
        total_errors = sum(m.errors for m in self._metrics.values())

        # Top endpoints by total time
        top_by_time = sorted(
            self._metrics.items(),
            key=lambda x: x[1].total_time,
            reverse=True,
        )[:10]

        # Top endpoints by call count
        top_by_calls = sorted(
            self._metrics.items(),
            key=lambda x: x[1].call_count,
            reverse=True,
        )[:10]

        # Top endpoints by average time
        top_by_avg = sorted(
            self._metrics.items(),
            key=lambda x: x[1].avg_time,
            reverse=True,
        )[:10]

        # Top endpoints by error rate
        top_by_errors = sorted(
            self._metrics.items(),
            key=lambda x: x[1].error_rate,
            reverse=True,
        )[:10]

        return {
            "enabled": self.enabled,
            "total_endpoints": len(self._metrics),
            "total_requests": total_requests,
            "total_time": total_time,
            "total_time_seconds": total_time,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0.0,
            "top_by_total_time": [
                {
                    "endpoint": key,
                    "path": metrics.path,
                    "method": metrics.method,
                    "calls": metrics.call_count,
                    "total_time": metrics.total_time,
                    "avg_time": metrics.avg_time,
                }
                for key, metrics in top_by_time
            ],
            "top_by_calls": [
                {
                    "endpoint": key,
                    "path": metrics.path,
                    "method": metrics.method,
                    "calls": metrics.call_count,
                    "avg_time": metrics.avg_time,
                }
                for key, metrics in top_by_calls
            ],
            "top_by_avg_time": [
                {
                    "endpoint": key,
                    "path": metrics.path,
                    "method": metrics.method,
                    "calls": metrics.call_count,
                    "avg_time": metrics.avg_time,
                }
                for key, metrics in top_by_avg
            ],
            "top_by_error_rate": [
                {
                    "endpoint": key,
                    "path": metrics.path,
                    "method": metrics.method,
                    "calls": metrics.call_count,
                    "error_rate": metrics.error_rate,
                    "errors": metrics.errors,
                }
                for key, metrics in top_by_errors
            ],
        }

    def _serialize_metrics(self, metrics: EndpointMetrics) -> dict[str, Any]:
        """Serialize metrics to dictionary (enhanced with percentiles)."""
        percentiles = metrics.get_percentiles()
        return {
            "path": metrics.path,
            "method": metrics.method,
            "call_count": metrics.call_count,
            "total_time": metrics.total_time,
            "avg_time": metrics.avg_time,
            "min_time": metrics.min_time if metrics.min_time != float("inf") else 0.0,
            "max_time": metrics.max_time,
            "p50": percentiles.get("p50", 0.0),
            "p95": percentiles.get("p95", 0.0),
            "p99": percentiles.get("p99", 0.0),
            "total_request_size": metrics.total_request_size,
            "total_response_size": metrics.total_response_size,
            "avg_request_size": metrics.avg_request_size,
            "avg_response_size": metrics.avg_response_size,
            "errors": metrics.errors,
            "error_rate": metrics.error_rate,
            "status_codes": dict(metrics.status_codes),
            "last_called": (
                metrics.last_called.isoformat() if metrics.last_called else None
            ),
        }

    def reset(self):
        """Reset all metrics."""
        if self._lock:
            with self._lock:
                self._metrics.clear()
        else:
            self._metrics.clear()
        logger.info("Performance monitoring metrics reset")

    def enable(self):
        """Enable monitoring."""
        self.enabled = True
        logger.info("Performance monitoring enabled")

    def disable(self):
        """Disable monitoring."""
        self.enabled = False
        logger.info("Performance monitoring disabled")


# Global middleware instance
_performance_middleware: PerformanceMonitoringMiddleware | None = None


def get_performance_middleware() -> PerformanceMonitoringMiddleware | None:
    """Get the global performance monitoring middleware instance."""
    return _performance_middleware


def setup_performance_monitoring(app: ASGIApp, enabled: bool = True):
    """
    Setup performance monitoring middleware.

    Args:
        app: FastAPI application
        enabled: Whether monitoring is enabled
    """
    global _performance_middleware
    _performance_middleware = PerformanceMonitoringMiddleware(app, enabled=enabled)
    return _performance_middleware
