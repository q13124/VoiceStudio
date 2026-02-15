"""
Rate Limiting Middleware.

Task 2.2.4: Rate limiting with sliding window.
Protects APIs from abuse and ensures fair usage.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    # Default limits
    requests_per_minute: int = 60
    requests_per_hour: int = 1000

    # Burst allowance
    burst_size: int = 10

    # Key extraction
    key_func: Callable[[Request], str] | None = None

    # Paths to exclude
    excluded_paths: list[str] = field(default_factory=lambda: [
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
    ])

    # Paths with custom limits
    path_limits: dict[str, int] = field(default_factory=lambda: {
        "/api/v1/synthesize": 10,  # 10 per minute for heavy operations
        "/api/v1/clone": 5,  # 5 per minute for cloning
    })


@dataclass
class RateLimitState:
    """State for a rate limit key."""
    requests: list[float] = field(default_factory=list)
    last_cleanup: float = field(default_factory=time.time)


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter.

    Features:
    - Sliding window algorithm (more accurate than fixed window)
    - Per-client tracking
    - Configurable limits per endpoint
    - Memory-efficient cleanup
    """

    def __init__(self, config: RateLimitConfig | None = None):
        self.config = config or RateLimitConfig()

        # State per client key
        self._states: dict[str, RateLimitState] = defaultdict(RateLimitState)

        # Lock for thread safety
        self._lock = asyncio.Lock()

    def _get_key(self, request: Request) -> str:
        """Extract rate limit key from request."""
        if self.config.key_func:
            return self.config.key_func(request)

        # Default: use client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"

    def _get_limit(self, path: str) -> int:
        """Get rate limit for a path."""
        # Check custom limits
        for pattern, limit in self.config.path_limits.items():
            if path.startswith(pattern):
                return limit

        return self.config.requests_per_minute

    async def check_rate_limit(
        self,
        request: Request,
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.

        Returns:
            (allowed, remaining, reset_seconds) tuple
        """
        path = request.url.path

        # Skip excluded paths
        for excluded in self.config.excluded_paths:
            if path.startswith(excluded):
                return True, -1, 0

        key = self._get_key(request)
        limit = self._get_limit(path)
        window = 60  # 1 minute window

        async with self._lock:
            now = time.time()
            state = self._states[key]

            # Cleanup old entries
            cutoff = now - window
            state.requests = [t for t in state.requests if t > cutoff]

            # Check limit
            if len(state.requests) >= limit:
                # Rate limited
                oldest = min(state.requests) if state.requests else now
                reset_time = int(oldest + window - now) + 1

                return False, 0, reset_time

            # Allow request
            state.requests.append(now)
            remaining = limit - len(state.requests)

            # Calculate reset time
            if state.requests:
                oldest = min(state.requests)
                reset_time = int(oldest + window - now) + 1
            else:
                reset_time = window

            return True, remaining, reset_time

    async def cleanup(self) -> int:
        """
        Clean up expired entries.

        Returns:
            Number of keys cleaned up
        """
        async with self._lock:
            now = time.time()
            expired_keys = []

            for key, state in self._states.items():
                # Remove keys with no recent requests
                if not state.requests or max(state.requests) < now - 3600:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._states[key]

            return len(expired_keys)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.

    Adds rate limit headers and returns 429 when exceeded.
    """

    def __init__(
        self,
        app,
        config: RateLimitConfig | None = None,
    ):
        super().__init__(app)
        self.limiter = SlidingWindowRateLimiter(config)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Handle request with rate limiting."""
        allowed, remaining, reset = await self.limiter.check_rate_limit(request)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {request.client.host if request.client else 'unknown'} "
                f"on {request.url.path}"
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after": reset,
                },
                headers={
                    "Retry-After": str(reset),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + reset),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        if remaining >= 0:
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset)

        return response


# Decorator for route-specific limits
def rate_limit(
    requests_per_minute: int = 60,
    key_func: Callable[[Request], str] | None = None,
):
    """
    Decorator for route-specific rate limits.

    Usage:
        @app.get("/api/heavy")
        @rate_limit(requests_per_minute=10)
        async def heavy_operation():
            ...
    """
    _limiter = SlidingWindowRateLimiter(RateLimitConfig(
        requests_per_minute=requests_per_minute,
        key_func=key_func,
    ))

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            allowed, _remaining, reset = await _limiter.check_rate_limit(request)

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"},
                    headers={"Retry-After": str(reset)},
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
