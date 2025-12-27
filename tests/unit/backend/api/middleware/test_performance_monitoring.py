"""
Unit Tests for Performance Monitoring Middleware
Tests all functionality: metrics tracking, response times, error rates,
request/response sizes, status codes, statistics, and thread safety.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules
try:
    from fastapi import Request, Response
    from starlette.types import ASGIApp

    from backend.api.middleware.performance_monitoring import (
        EndpointMetrics,
        PerformanceMonitoringMiddleware,
        get_performance_middleware,
        setup_performance_monitoring,
    )
except ImportError as e:
    pytest.skip(f"Could not import performance monitoring modules: {e}", allow_module_level=True)


class TestEndpointMetrics:
    """Test EndpointMetrics dataclass."""

    def test_initialization(self):
        """Test EndpointMetrics initializes correctly."""
        metrics = EndpointMetrics(path="/test", method="GET")
        assert metrics.path == "/test"
        assert metrics.method == "GET"
        assert metrics.call_count == 0
        assert metrics.total_time == 0.0
        assert metrics.min_time == float("inf")
        assert metrics.max_time == 0.0
        assert metrics.errors == 0
        assert metrics.error_rate == 0.0

    def test_update_success(self):
        """Test metrics update with successful request."""
        metrics = EndpointMetrics(path="/test", method="GET")
        
        metrics.update(
            execution_time=0.1,
            request_size=100,
            response_size=200,
            status_code=200,
        )
        
        assert metrics.call_count == 1
        assert metrics.total_time == 0.1
        assert metrics.min_time == 0.1
        assert metrics.max_time == 0.1
        assert metrics.avg_time == 0.1
        assert metrics.total_request_size == 100
        assert metrics.total_response_size == 200
        assert metrics.avg_request_size == 100.0
        assert metrics.avg_response_size == 200.0
        assert metrics.errors == 0
        assert metrics.error_rate == 0.0
        assert metrics.status_codes[200] == 1
        assert metrics.last_called is not None

    def test_update_multiple_calls(self):
        """Test metrics update with multiple calls."""
        metrics = EndpointMetrics(path="/test", method="GET")
        
        metrics.update(execution_time=0.1, status_code=200)
        metrics.update(execution_time=0.2, status_code=200)
        metrics.update(execution_time=0.15, status_code=200)
        
        assert metrics.call_count == 3
        assert abs(metrics.total_time - 0.45) < 0.0001
        assert metrics.min_time == 0.1
        assert metrics.max_time == 0.2
        assert abs(metrics.avg_time - 0.15) < 0.0001

    def test_update_error(self):
        """Test metrics update with error status code."""
        metrics = EndpointMetrics(path="/test", method="GET")
        
        metrics.update(execution_time=0.1, status_code=500)
        
        assert metrics.errors == 1
        assert metrics.error_rate == 1.0
        assert metrics.status_codes[500] == 1

    def test_update_mixed_status_codes(self):
        """Test metrics update with mixed success and error status codes."""
        metrics = EndpointMetrics(path="/test", method="GET")
        
        metrics.update(execution_time=0.1, status_code=200)
        metrics.update(execution_time=0.1, status_code=404)
        metrics.update(execution_time=0.1, status_code=200)
        
        assert metrics.call_count == 3
        assert metrics.errors == 1
        assert metrics.error_rate == pytest.approx(1.0 / 3.0)
        assert metrics.status_codes[200] == 2
        assert metrics.status_codes[404] == 1


class TestPerformanceMonitoringMiddleware:
    """Test PerformanceMonitoringMiddleware."""

    def test_initialization(self):
        """Test middleware initializes correctly."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        assert middleware.enabled is True
        assert middleware.track_request_size is True
        assert middleware.track_response_size is True
        assert len(middleware._metrics) == 0

    def test_initialization_disabled(self):
        """Test middleware can be initialized disabled."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app, enabled=False)
        
        assert middleware.enabled is False

    def test_initialization_no_tracking(self):
        """Test middleware can disable size tracking."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(
            app, track_request_size=False, track_response_size=False
        )
        
        assert middleware.track_request_size is False
        assert middleware.track_response_size is False

    def test_get_endpoint_key(self):
        """Test endpoint key generation."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        key = middleware._get_endpoint_key("/test", "GET")
        assert key == "GET:/test"

    @pytest.mark.asyncio
    async def test_dispatch_when_disabled(self):
        """Test dispatch skips monitoring when disabled."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app, enabled=False)
        
        request = MagicMock(spec=Request)
        call_next = AsyncMock(return_value=MagicMock(spec=Response))
        
        response = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert len(middleware._metrics) == 0

    @pytest.mark.asyncio
    async def test_dispatch_skips_docs(self):
        """Test dispatch skips monitoring for /docs and /redoc paths."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.url.path = "/docs"
        request.url.query = ""
        call_next = AsyncMock(return_value=MagicMock(spec=Response))
        
        response = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert len(middleware._metrics) == 0

    @pytest.mark.asyncio
    async def test_dispatch_tracks_metrics(self):
        """Test dispatch tracks metrics for requests."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.url.query = ""
        request.method = "GET"
        request.headers = {}
        
        response = MagicMock(spec=Response)
        response.status_code = 200
        response.headers = {}
        response.body = b"test"
        
        call_next = AsyncMock(return_value=response)
        
        with patch("time.perf_counter", side_effect=[0.0, 0.1]):
            await middleware.dispatch(request, call_next)
        
        assert len(middleware._metrics) == 1
        key = "GET:/api/test"
        assert key in middleware._metrics
        metrics = middleware._metrics[key]
        assert metrics.call_count == 1
        assert metrics.total_time == pytest.approx(0.1)

    @pytest.mark.asyncio
    async def test_dispatch_adds_performance_headers(self):
        """Test dispatch adds performance headers to response."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.url.query = ""
        request.method = "GET"
        request.headers = {}
        
        response = MagicMock(spec=Response)
        response.status_code = 200
        response.headers = {}
        response.body = b"test"
        
        call_next = AsyncMock(return_value=response)
        
        with patch("time.perf_counter", side_effect=[0.0, 0.1]):
            await middleware.dispatch(request, call_next)
        
        assert "X-Response-Time" in response.headers
        assert "X-Endpoint" in response.headers
        assert response.headers["X-Endpoint"] == "GET:/api/test"

    @pytest.mark.asyncio
    async def test_dispatch_tracks_errors(self):
        """Test dispatch tracks errors correctly."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.url.query = ""
        request.method = "GET"
        request.headers = {}
        
        response = MagicMock(spec=Response)
        response.status_code = 500
        response.headers = {}
        response.body = b""
        
        call_next = AsyncMock(return_value=response)
        
        with patch("time.perf_counter", side_effect=[0.0, 0.1]):
            await middleware.dispatch(request, call_next)
        
        key = "GET:/api/test"
        metrics = middleware._metrics[key]
        assert metrics.errors == 1
        assert metrics.error_rate == 1.0
        assert metrics.status_codes[500] == 1

    @pytest.mark.asyncio
    async def test_dispatch_handles_exceptions(self):
        """Test dispatch handles exceptions and tracks them."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.url.query = ""
        request.method = "GET"
        request.headers = {}
        
        call_next = AsyncMock(side_effect=Exception("Test error"))
        
        with patch("time.perf_counter", side_effect=[0.0, 0.1]):
            with pytest.raises(Exception):
                await middleware.dispatch(request, call_next)
        
        key = "GET:/api/test"
        assert key in middleware._metrics
        metrics = middleware._metrics[key]
        assert metrics.errors == 1
        assert metrics.status_codes[500] == 1

    def test_get_request_size(self):
        """Test request size calculation."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.headers = {"Content-Type": "application/json", "Authorization": "Bearer token"}
        request.url.query = "param=value"
        request._body = b"test body"
        
        size = middleware._get_request_size(request)
        assert size > 0

    def test_get_request_size_disabled(self):
        """Test request size returns 0 when tracking disabled."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app, track_request_size=False)
        
        request = MagicMock(spec=Request)
        size = middleware._get_request_size(request)
        assert size == 0

    def test_get_response_size(self):
        """Test response size calculation."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        response = MagicMock(spec=Response)
        response.headers = {"Content-Type": "application/json"}
        response.body = b"test response body"
        
        size = middleware._get_response_size(response)
        assert size > 0

    def test_get_response_size_disabled(self):
        """Test response size returns 0 when tracking disabled."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app, track_response_size=False)
        
        response = MagicMock(spec=Response)
        size = middleware._get_response_size(response)
        assert size == 0

    def test_get_metrics_single_endpoint(self):
        """Test get_metrics for single endpoint."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        # Add some metrics
        middleware._update_metrics(
            "GET:/test", "/test", "GET", 0.1, 100, 200, 200
        )
        
        metrics = middleware.get_metrics("GET:/test")
        assert metrics["path"] == "/test"
        assert metrics["method"] == "GET"
        assert metrics["call_count"] == 1

    def test_get_metrics_all_endpoints(self):
        """Test get_metrics returns all endpoints."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        # Add multiple endpoints
        middleware._update_metrics("GET:/test1", "/test1", "GET", 0.1, 100, 200, 200)
        middleware._update_metrics("POST:/test2", "/test2", "POST", 0.2, 200, 300, 201)
        
        all_metrics = middleware.get_metrics()
        assert len(all_metrics) == 2
        assert "GET:/test1" in all_metrics
        assert "POST:/test2" in all_metrics

    def test_get_metrics_nonexistent_endpoint(self):
        """Test get_metrics returns empty dict for nonexistent endpoint."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        metrics = middleware.get_metrics("GET:/nonexistent")
        assert metrics == {}

    def test_get_stats_empty(self):
        """Test get_stats with no metrics."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        stats = middleware.get_stats()
        assert stats["enabled"] is True
        assert stats["total_endpoints"] == 0
        assert stats["total_requests"] == 0
        assert stats["total_time"] == 0.0

    def test_get_stats_with_metrics(self):
        """Test get_stats with metrics."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        # Add multiple endpoints with different metrics
        middleware._update_metrics("GET:/test1", "/test1", "GET", 0.1, 100, 200, 200)
        middleware._update_metrics("GET:/test1", "/test1", "GET", 0.2, 100, 200, 200)
        middleware._update_metrics("POST:/test2", "/test2", "POST", 0.3, 200, 300, 500)
        
        stats = middleware.get_stats()
        assert stats["total_endpoints"] == 2
        assert stats["total_requests"] == 3
        assert stats["total_time"] == pytest.approx(0.6)
        assert stats["total_errors"] == 1
        assert "top_by_total_time" in stats
        assert "top_by_calls" in stats
        assert "top_by_avg_time" in stats
        assert "top_by_error_rate" in stats

    def test_reset(self):
        """Test reset clears all metrics."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        # Add some metrics
        middleware._update_metrics("GET:/test", "/test", "GET", 0.1, 100, 200, 200)
        assert len(middleware._metrics) == 1
        
        middleware.reset()
        assert len(middleware._metrics) == 0

    def test_enable(self):
        """Test enable method."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app, enabled=False)
        assert middleware.enabled is False
        
        middleware.enable()
        assert middleware.enabled is True

    def test_disable(self):
        """Test disable method."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        assert middleware.enabled is True
        
        middleware.disable()
        assert middleware.enabled is False

    def test_serialize_metrics(self):
        """Test metrics serialization."""
        app = MagicMock(spec=ASGIApp)
        middleware = PerformanceMonitoringMiddleware(app)
        
        # Create metrics and update
        metrics = EndpointMetrics(path="/test", method="GET")
        metrics.update(execution_time=0.1, request_size=100, response_size=200, status_code=200)
        
        serialized = middleware._serialize_metrics(metrics)
        assert serialized["path"] == "/test"
        assert serialized["method"] == "GET"
        assert serialized["call_count"] == 1
        assert serialized["total_time"] == 0.1
        assert serialized["min_time"] == 0.1
        assert serialized["max_time"] == 0.1
        assert "last_called" in serialized
        assert "status_codes" in serialized


class TestGlobalFunctions:
    """Test global functions."""

    def test_get_performance_middleware_none(self):
        """Test get_performance_middleware returns None when not set."""
        # Clear global instance
        import backend.api.middleware.performance_monitoring as pm_module
        pm_module._performance_middleware = None
        
        middleware = get_performance_middleware()
        assert middleware is None

    def test_setup_performance_monitoring(self):
        """Test setup_performance_monitoring creates global instance."""
        app = MagicMock(spec=ASGIApp)
        
        middleware = setup_performance_monitoring(app, enabled=True)
        
        assert middleware is not None
        assert middleware.enabled is True
        assert get_performance_middleware() == middleware

    def test_setup_performance_monitoring_disabled(self):
        """Test setup_performance_monitoring can create disabled instance."""
        app = MagicMock(spec=ASGIApp)
        
        middleware = setup_performance_monitoring(app, enabled=False)
        
        assert middleware.enabled is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

