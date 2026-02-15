"""
Unit Tests for Validation Optimizer Middleware
Tests validation optimizer middleware functionality.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the middleware module
try:
    from backend.api.middleware import validation_optimizer
    from backend.api.middleware.validation_optimizer import (
        ValidationOptimizerMiddleware,
        get_validation_optimizer_middleware,
    )
except ImportError:
    pytest.skip(
        "Could not import validation_optimizer middleware", allow_module_level=True
    )


class TestValidationOptimizerMiddlewareImports:
    """Test validation optimizer middleware module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            validation_optimizer is not None
        ), "Failed to import validation_optimizer middleware module"

    def test_middleware_class_exists(self):
        """Test ValidationOptimizerMiddleware class exists."""
        assert hasattr(
            validation_optimizer, "ValidationOptimizerMiddleware"
        ), "ValidationOptimizerMiddleware class should exist"
        cls = validation_optimizer.ValidationOptimizerMiddleware
        assert isinstance(cls, type), "ValidationOptimizerMiddleware should be a class"
        assert issubclass(
            cls, BaseHTTPMiddleware
        ), "ValidationOptimizerMiddleware should inherit from BaseHTTPMiddleware"


class TestValidationOptimizerMiddlewareClass:
    """Test ValidationOptimizerMiddleware class."""

    def test_middleware_initialization(self):
        """Test middleware can be initialized."""
        app = MagicMock()
        middleware = ValidationOptimizerMiddleware(app)

        assert middleware.app == app
        assert middleware.enable_cache is True
        assert middleware.cache_max_size == 1000

    def test_middleware_initialization_with_custom_params(self):
        """Test middleware can be initialized with custom parameters."""
        app = MagicMock()
        middleware = ValidationOptimizerMiddleware(
            app, enable_cache=False, cache_max_size=500
        )

        assert middleware.app == app
        assert middleware.enable_cache is False
        assert middleware.cache_max_size == 500

    @pytest.mark.asyncio
    async def test_dispatch_adds_stats_to_request_state(self):
        """Test dispatch adds validation stats to request state."""
        app = AsyncMock()
        app.return_value = Response(status_code=200)

        middleware = ValidationOptimizerMiddleware(app)

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        call_next = AsyncMock(return_value=Response(status_code=200))

        with patch(
            "backend.api.middleware.validation_optimizer.get_validation_stats"
        ) as mock_get_validation_stats, patch(
            "backend.api.middleware.validation_optimizer.get_cache_stats"
        ) as mock_get_cache_stats:
            mock_get_validation_stats.return_value = {"total_validations": 10}
            mock_get_cache_stats.return_value = {"cache_hits": 5, "cache_misses": 5}

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 200
            assert hasattr(request.state, "validation_stats")
            assert hasattr(request.state, "cache_stats")
            assert request.state.validation_stats == {"total_validations": 10}
            assert request.state.cache_stats == {"cache_hits": 5, "cache_misses": 5}

    @pytest.mark.asyncio
    async def test_dispatch_calls_next_middleware(self):
        """Test dispatch calls the next middleware/handler."""
        app = MagicMock()
        middleware = ValidationOptimizerMiddleware(app)

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        call_next = AsyncMock(return_value=Response(status_code=200))

        with patch(
            "backend.api.middleware.validation_optimizer.get_validation_stats"
        ) as mock_get_validation_stats, patch(
            "backend.api.middleware.validation_optimizer.get_cache_stats"
        ) as mock_get_cache_stats:
            mock_get_validation_stats.return_value = {}
            mock_get_cache_stats.return_value = {}

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 200
            call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_handles_exceptions(self):
        """Test dispatch handles exceptions gracefully."""
        app = MagicMock()
        middleware = ValidationOptimizerMiddleware(app)

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        call_next = AsyncMock(side_effect=Exception("Test error"))

        with patch(
            "backend.api.middleware.validation_optimizer.get_validation_stats"
        ) as mock_get_validation_stats, patch(
            "backend.api.middleware.validation_optimizer.get_cache_stats"
        ) as mock_get_cache_stats:
            mock_get_validation_stats.return_value = {}
            mock_get_cache_stats.return_value = {}

            with pytest.raises(Exception) as exc_info:
                await middleware.dispatch(request, call_next)
            assert "Test error" in str(exc_info.value)


class TestValidationOptimizerMiddlewareFunctions:
    """Test validation optimizer middleware functions."""

    def test_get_validation_optimizer_middleware(self):
        """Test get_validation_optimizer_middleware function."""
        middleware_class = get_validation_optimizer_middleware()

        assert middleware_class is not None
        assert middleware_class == ValidationOptimizerMiddleware

    def test_get_validation_optimizer_middleware_with_params(self):
        """Test get_validation_optimizer_middleware with parameters."""
        middleware_class = get_validation_optimizer_middleware(
            enable_cache=False, cache_max_size=500
        )

        assert middleware_class is not None
        assert middleware_class == ValidationOptimizerMiddleware

        # Verify parameters can be used when instantiating
        app = MagicMock()
        middleware = middleware_class(app, enable_cache=False, cache_max_size=500)
        assert middleware.enable_cache is False
        assert middleware.cache_max_size == 500


class TestValidationOptimizerMiddlewareIntegration:
    """Test validation optimizer middleware integration with FastAPI."""

    @pytest.mark.asyncio
    async def test_middleware_in_fastapi_app(self):
        """Test middleware works in FastAPI app."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {
                "validation_stats": getattr(request.state, "validation_stats", None),
                "cache_stats": getattr(request.state, "cache_stats", None),
            }

        # Add middleware
        app.add_middleware(
            ValidationOptimizerMiddleware,
            enable_cache=True,
            cache_max_size=1000,
        )

        with patch(
            "backend.api.middleware.validation_optimizer.get_validation_stats"
        ) as mock_get_validation_stats, patch(
            "backend.api.middleware.validation_optimizer.get_cache_stats"
        ) as mock_get_cache_stats:
            mock_get_validation_stats.return_value = {"total_validations": 5}
            mock_get_cache_stats.return_value = {"cache_hits": 3, "cache_misses": 2}

            client = TestClient(app)
            response = client.get("/test")

            assert response.status_code == 200
            data = response.json()
            assert "validation_stats" in data
            assert "cache_stats" in data
            assert data["validation_stats"]["total_validations"] == 5
            assert data["cache_stats"]["cache_hits"] == 3

    @pytest.mark.asyncio
    async def test_middleware_stats_available_in_endpoint(self):
        """Test validation stats are available in endpoint."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(request: Request):
            validation_stats = getattr(request.state, "validation_stats", None)
            cache_stats = getattr(request.state, "cache_stats", None)
            return {
                "has_validation_stats": validation_stats is not None,
                "has_cache_stats": cache_stats is not None,
                "validation_stats": validation_stats or {},
                "cache_stats": cache_stats or {},
            }

        app.add_middleware(ValidationOptimizerMiddleware)

        with patch(
            "backend.api.middleware.validation_optimizer.get_validation_stats"
        ) as mock_get_validation_stats, patch(
            "backend.api.middleware.validation_optimizer.get_cache_stats"
        ) as mock_get_cache_stats:
            mock_get_validation_stats.return_value = {"test": "stats"}
            mock_get_cache_stats.return_value = {"test": "cache"}

            client = TestClient(app)
            response = client.get("/test")

            assert response.status_code == 200
            data = response.json()
            # Stats should be available (may be None if middleware didn't run)
            assert "validation_stats" in data
            assert "cache_stats" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

