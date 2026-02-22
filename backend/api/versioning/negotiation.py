"""
API Version Negotiation.

Task 3.4.2: Content negotiation for API versions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api.versioning.router import ApiVersion


@dataclass
class VersionInfo:
    """Resolved version information."""

    version: ApiVersion
    source: str  # "header", "url", "default"
    is_deprecated: bool = False


class ApiVersionNegotiator:
    """
    Negotiates API version from request.

    Priority:
    1. URL path (/api/v1/...)
    2. Accept header (application/vnd.voicestudio.v1+json)
    3. X-API-Version header
    4. Default to latest
    """

    ACCEPT_PATTERN = re.compile(r"application/vnd\.voicestudio\.v(\d+)\+json")

    def __init__(self, default_version: ApiVersion | None = None):
        """
        Initialize negotiator.

        Args:
            default_version: Default version if not specified
        """
        self._default = default_version or ApiVersion.latest()

    def negotiate(self, request: Request) -> VersionInfo:
        """
        Determine API version from request.

        Args:
            request: FastAPI request

        Returns:
            VersionInfo with resolved version
        """
        # Check URL path first
        version = self._from_url(request.url.path)
        if version:
            return VersionInfo(version=version, source="url")

        # Check Accept header
        accept = request.headers.get("Accept", "")
        version = self._from_accept(accept)
        if version:
            return VersionInfo(version=version, source="header")

        # Check X-API-Version header
        api_version = request.headers.get("X-API-Version", "")
        version = ApiVersion.from_string(api_version)
        if version:
            return VersionInfo(version=version, source="header")

        # Use default
        return VersionInfo(version=self._default, source="default")

    def _from_url(self, path: str) -> ApiVersion | None:
        """Extract version from URL path."""
        match = re.search(r"/api/(v\d+)/", path)
        if match:
            return ApiVersion.from_string(match.group(1))
        return None

    def _from_accept(self, accept: str) -> ApiVersion | None:
        """Extract version from Accept header."""
        match = self.ACCEPT_PATTERN.search(accept)
        if match:
            return ApiVersion.from_string(f"v{match.group(1)}")
        return None


class VersionNegotiationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add version info to request state.
    """

    def __init__(self, app, negotiator: ApiVersionNegotiator | None = None):
        super().__init__(app)
        self._negotiator = negotiator or ApiVersionNegotiator()

    async def dispatch(self, request: Request, call_next):
        """Add version info to request."""
        version_info = self._negotiator.negotiate(request)

        # Store in request state
        request.state.api_version = version_info.version
        request.state.version_source = version_info.source

        response: Response = await call_next(request)

        # Add version to response headers
        response.headers["X-API-Version"] = version_info.version.value

        return response
