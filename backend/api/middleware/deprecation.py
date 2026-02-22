"""
Deprecation Headers Middleware

Adds deprecation headers to legacy API endpoints to inform clients
about upcoming changes and encourage migration to newer versions.

Headers added:
- X-API-Deprecated: "true" if endpoint is deprecated
- Sunset: Date when endpoint will be removed (RFC 7231 format)
- Link: URL to replacement endpoint with rel="successor-version"
- Deprecation: RFC 8594 compliant deprecation date
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.api.versioning import (
    DEPRECATION_HEADER,
    SUNSET_HEADER,
)

logger = logging.getLogger(__name__)


# RFC 7231 date format for Sunset header
RFC_7231_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


class DeprecatedEndpoint:
    """Configuration for a deprecated endpoint."""

    def __init__(
        self,
        path_pattern: str,
        sunset_date: str | None = None,  # ISO 8601 format
        replacement: str | None = None,
        message: str | None = None,
        deprecated_since: str | None = None,  # ISO 8601 format
    ):
        self.path_pattern = path_pattern
        self.sunset_date = sunset_date
        self.replacement = replacement
        self.message = message or "This endpoint is deprecated"
        self.deprecated_since = deprecated_since

    def matches(self, path: str) -> bool:
        """Check if the path matches this deprecated endpoint."""
        # Simple prefix matching for now
        # Could be extended to support regex or path parameters
        if self.path_pattern.endswith("*"):
            return path.startswith(self.path_pattern[:-1])
        return path == self.path_pattern


# Registry of deprecated endpoints
# Add endpoints here as they become deprecated
DEPRECATED_ENDPOINTS: list[DeprecatedEndpoint] = [
    # Phase 2 API Contract Hardening: Mark v1 endpoints as deprecated
    DeprecatedEndpoint(
        path_pattern="/api/v1/*",
        sunset_date="2026-06-01",
        replacement="/api/v3/",
        message="v1 API is deprecated. Please migrate to v3 for StandardResponse format.",
        deprecated_since="2026-02-14",
    ),
]


def _format_sunset_date(iso_date: str) -> str:
    """Convert ISO 8601 date to RFC 7231 format for Sunset header."""
    try:
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime(RFC_7231_FORMAT)
    except (ValueError, TypeError):
        return iso_date


def _build_link_header(replacement: str, request: Request) -> str:
    """Build a Link header for the replacement endpoint."""
    # Build full URL for the replacement
    base = str(request.base_url).rstrip("/")
    full_url = f"{base}{replacement}"
    return f'<{full_url}>; rel="successor-version"'


class DeprecationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds deprecation headers to deprecated endpoints.

    This middleware:
    1. Checks if the request path matches any deprecated endpoints
    2. Adds appropriate deprecation headers to the response
    3. Logs deprecation warnings for monitoring
    """

    def __init__(
        self,
        app: ASGIApp,
        deprecated_endpoints: list[DeprecatedEndpoint] | None = None,
        log_deprecation_warnings: bool = True,
    ):
        super().__init__(app)
        self.deprecated_endpoints = deprecated_endpoints or DEPRECATED_ENDPOINTS
        self.log_deprecation_warnings = log_deprecation_warnings
        self._warning_counts: dict[str, int] = {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and add deprecation headers if needed."""
        path = request.url.path

        # Find matching deprecated endpoint
        deprecated = self._find_deprecated_endpoint(path)

        # Call the actual endpoint
        response: Response = await call_next(request)

        # Add deprecation headers if endpoint is deprecated
        if deprecated:
            self._add_deprecation_headers(response, deprecated, request)

            if self.log_deprecation_warnings:
                self._log_deprecation_warning(path, deprecated)

        return response

    def _find_deprecated_endpoint(self, path: str) -> DeprecatedEndpoint | None:
        """Find a deprecated endpoint configuration matching the path."""
        for endpoint in self.deprecated_endpoints:
            if endpoint.matches(path):
                return endpoint
        return None

    def _add_deprecation_headers(
        self,
        response: Response,
        deprecated: DeprecatedEndpoint,
        request: Request,
    ) -> None:
        """Add deprecation-related headers to the response."""
        # X-API-Deprecated header
        response.headers[DEPRECATION_HEADER] = "true"

        # Sunset header (RFC 7231 format)
        if deprecated.sunset_date:
            response.headers[SUNSET_HEADER] = _format_sunset_date(deprecated.sunset_date)

        # Deprecation header (RFC 8594)
        if deprecated.deprecated_since:
            response.headers["Deprecation"] = _format_sunset_date(deprecated.deprecated_since)

        # Link header with replacement
        if deprecated.replacement:
            response.headers["Link"] = _build_link_header(deprecated.replacement, request)

        # Custom deprecation message in a header (non-standard but useful)
        if deprecated.message:
            response.headers["X-Deprecation-Notice"] = deprecated.message

    def _log_deprecation_warning(
        self,
        path: str,
        deprecated: DeprecatedEndpoint,
    ) -> None:
        """Log a deprecation warning (rate-limited to avoid log spam)."""
        # Simple rate limiting: log first occurrence and then every 100 calls
        self._warning_counts[path] = self._warning_counts.get(path, 0) + 1
        count = self._warning_counts[path]

        if count == 1 or count % 100 == 0:
            logger.warning(
                f"Deprecated endpoint accessed: {path} "
                f"(calls: {count}, sunset: {deprecated.sunset_date})"
            )


def add_deprecation_to_response(
    response: Response,
    sunset_date: str | None = None,
    replacement: str | None = None,
    message: str | None = None,
    deprecated_since: str | None = None,
    request: Request | None = None,
) -> None:
    """
    Helper function to manually add deprecation headers to a response.

    Use this in individual endpoints for fine-grained deprecation control.

    Args:
        response: The FastAPI/Starlette response object
        sunset_date: ISO 8601 date when endpoint will be removed
        replacement: Path to the replacement endpoint
        message: Human-readable deprecation message
        deprecated_since: ISO 8601 date when endpoint was deprecated
        request: Optional request object for building full replacement URL

    Example:
        @router.get("/old-endpoint")
        async def old_endpoint(request: Request, response: Response):
            add_deprecation_to_response(
                response,
                sunset_date="2026-06-01",
                replacement="/api/v2/new-endpoint",
                message="Please use the new endpoint",
                request=request,
            )
            return {"data": "old"}
    """
    response.headers[DEPRECATION_HEADER] = "true"

    if sunset_date:
        response.headers[SUNSET_HEADER] = _format_sunset_date(sunset_date)

    if deprecated_since:
        response.headers["Deprecation"] = _format_sunset_date(deprecated_since)

    if replacement and request:
        response.headers["Link"] = _build_link_header(replacement, request)
    elif replacement:
        # Without request, just use the path
        response.headers["Link"] = f'<{replacement}>; rel="successor-version"'

    if message:
        response.headers["X-Deprecation-Notice"] = message


def register_deprecated_endpoint(
    path_pattern: str,
    sunset_date: str | None = None,
    replacement: str | None = None,
    message: str | None = None,
    deprecated_since: str | None = None,
) -> None:
    """
    Register an endpoint as deprecated.

    This adds the endpoint to the global registry, which will be picked up
    by the DeprecationMiddleware.

    Args:
        path_pattern: Path pattern to match (use * for wildcard)
        sunset_date: ISO 8601 date when endpoint will be removed
        replacement: Path to the replacement endpoint
        message: Human-readable deprecation message
        deprecated_since: ISO 8601 date when endpoint was deprecated

    Example:
        register_deprecated_endpoint(
            "/api/v1/voices/*",
            sunset_date="2026-12-01",
            replacement="/api/v2/voices/",
            message="v1 voices API is deprecated",
        )
    """
    endpoint = DeprecatedEndpoint(
        path_pattern=path_pattern,
        sunset_date=sunset_date,
        replacement=replacement,
        message=message,
        deprecated_since=deprecated_since,
    )
    DEPRECATED_ENDPOINTS.append(endpoint)
    logger.info(f"Registered deprecated endpoint: {path_pattern}")


def get_deprecated_endpoints() -> list[dict[str, Any]]:
    """Get list of all registered deprecated endpoints for monitoring."""
    return [
        {
            "path_pattern": ep.path_pattern,
            "sunset_date": ep.sunset_date,
            "replacement": ep.replacement,
            "message": ep.message,
            "deprecated_since": ep.deprecated_since,
        }
        for ep in DEPRECATED_ENDPOINTS
    ]
