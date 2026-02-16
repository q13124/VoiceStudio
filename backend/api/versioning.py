"""
API Versioning Infrastructure

Provides version prefix routing and version negotiation for the VoiceStudio API.

Supported versions:
- V1: Legacy API (deprecated, sunset 2026-06-01)
- V2: Stable API
- V3: Current API with StandardResponse envelope format

Usage:
    from backend.api.versioning import create_v3_router, APIVersion

    # Create a v3 router (recommended for new endpoints)
    router = create_v3_router(
        prefix="/voices",
        tags=["voices"],
    )

    # Register a v3 endpoint using StandardResponse
    @router.get("/")
    async def list_voices():
        return success_response(data=voices, message="Voices retrieved")

For legacy support:
    from backend.api.versioning import create_v1_router, create_v2_router
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from functools import wraps

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)


class APIVersion(str, Enum):
    """Supported API versions."""

    V1 = "v1"
    V2 = "v2"
    V3 = "v3"

    @classmethod
    def current(cls) -> APIVersion:
        """Return the current (latest) API version."""
        return cls.V3

    @classmethod
    def default(cls) -> APIVersion:
        """Return the default API version for unversioned requests."""
        return cls.V1

    @classmethod
    def supported(cls) -> set[APIVersion]:
        """Return set of all supported versions."""
        return {cls.V1, cls.V2, cls.V3}

    @classmethod
    def deprecated(cls) -> set[APIVersion]:
        """Return set of deprecated versions (still supported but will be removed)."""
        return {cls.V1}


# Version-related headers
VERSION_HEADER = "X-API-Version"
DEPRECATION_HEADER = "X-API-Deprecated"
SUNSET_HEADER = "Sunset"

# Aliases for main.py compatibility
HEADER_API_VERSION = VERSION_HEADER
HEADER_MIN_VERSION = "X-API-Min-Version"

# Version constants
CURRENT_VERSION = APIVersion.V3
MIN_SUPPORTED_VERSION = APIVersion.V1

# Deprecation dates for v1 endpoints
V1_DEPRECATION_DATE = "2026-06-01"  # Phase out v1 by this date


class VersionNegotiator:
    """
    Version negotiation handler for API requests.

    Handles version detection, validation, and compatibility checking.
    """

    def __init__(
        self,
        current_version: APIVersion = CURRENT_VERSION,
        min_version: APIVersion = MIN_SUPPORTED_VERSION,
    ):
        self.current_version = current_version
        self.min_version = min_version

    def negotiate(self, request: Request) -> APIVersion:
        """Negotiate API version from request."""
        return get_version_from_request(request)

    def is_supported(self, version: APIVersion) -> bool:
        """Check if a version is supported."""
        return version in APIVersion.supported()

    def get_headers(self, version: APIVersion) -> dict[str, str]:
        """Get version headers for response."""
        return get_version_headers(version)


def get_version_headers(
    version: APIVersion,
    is_deprecated: bool = False,
    sunset: str | None = None,
) -> dict[str, str]:
    """
    Get version-related headers for a response.

    Args:
        version: The API version used
        is_deprecated: Whether this endpoint is deprecated
        sunset: Sunset date for deprecated endpoints

    Returns:
        Dict of headers to add to response
    """
    headers = {
        HEADER_API_VERSION: version.value,
        HEADER_MIN_VERSION: MIN_SUPPORTED_VERSION.value,
    }

    if is_deprecated:
        headers[DEPRECATION_HEADER] = "true"
        if sunset:
            headers[SUNSET_HEADER] = sunset

    return headers


def get_api_version_prefix(version: APIVersion) -> str:
    """Get the URL prefix for a given API version."""
    return f"/api/{version.value}"


def create_versioned_router(
    prefix: str,
    tags: list[str] | None = None,
    versions: list[APIVersion] | None = None,
) -> APIRouter:
    """
    Create an APIRouter with version prefixing.

    Args:
        prefix: The base prefix (e.g., "/health")
        tags: OpenAPI tags for documentation
        versions: List of API versions to support (defaults to [V1, V2])

    Returns:
        APIRouter configured with version prefixes
    """
    if versions is None:
        versions = list(APIVersion.supported())

    # For now, create router with the default version prefix
    # Full versioning will require more complex routing
    default_version = APIVersion.default()
    full_prefix = f"{get_api_version_prefix(default_version)}{prefix}"

    return APIRouter(
        prefix=full_prefix,
        tags=tags or [],
    )


def create_v2_router(
    prefix: str,
    tags: list[str] | None = None,
) -> APIRouter:
    """
    Create an APIRouter specifically for v2 endpoints.

    Args:
        prefix: The base prefix (e.g., "/health")
        tags: OpenAPI tags for documentation

    Returns:
        APIRouter configured with /api/v2 prefix
    """
    full_prefix = f"/api/v2{prefix}"
    return APIRouter(prefix=full_prefix, tags=tags or [])


def create_v3_router(
    prefix: str,
    tags: list[str] | None = None,
) -> APIRouter:
    """
    Create an APIRouter specifically for v3 endpoints.

    V3 endpoints use the StandardResponse envelope format.

    Args:
        prefix: The base prefix (e.g., "/voices")
        tags: OpenAPI tags for documentation

    Returns:
        APIRouter configured with /api/v3 prefix
    """
    full_prefix = f"/api/v3{prefix}"
    return APIRouter(prefix=full_prefix, tags=tags or [])


def create_v1_router(
    prefix: str,
    tags: list[str] | None = None,
) -> APIRouter:
    """
    Create an APIRouter specifically for v1 endpoints.

    Args:
        prefix: The base prefix (e.g., "/health")
        tags: OpenAPI tags for documentation

    Returns:
        APIRouter configured with /api/v1 prefix
    """
    full_prefix = f"/api/v1{prefix}"
    return APIRouter(prefix=full_prefix, tags=tags or [])


def deprecated(
    sunset: str | None = None,
    alternative: str | None = None,
    message: str | None = None,
) -> Callable:
    """
    Mark an endpoint as deprecated.

    Adds deprecation headers to the response.

    Args:
        sunset: ISO 8601 date when the endpoint will be removed
        alternative: URL of the replacement endpoint
        message: Custom deprecation message

    Example:
        @router.get("/old-endpoint")
        @deprecated(sunset="2026-03-01", alternative="/api/v2/new-endpoint")
        async def old_endpoint():
            return {"data": "old"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the response from the actual function
            response = await func(*args, **kwargs)

            # Add deprecation headers
            # Note: This requires the endpoint to return a Response object
            # or use a middleware approach
            return response

        # Store deprecation metadata for middleware/response handling
        wrapper._deprecated = True
        wrapper._deprecation_sunset = sunset
        wrapper._deprecation_alternative = alternative
        wrapper._deprecation_message = message or "This endpoint is deprecated"

        return wrapper
    return decorator


def get_version_from_request(request: Request) -> APIVersion:
    """
    Extract API version from request.

    Checks (in order):
    1. URL path prefix (/api/v1/, /api/v2/)
    2. X-API-Version header
    3. Falls back to default version

    Args:
        request: The FastAPI request object

    Returns:
        The determined API version
    """
    # Check URL path
    path = request.url.path
    for version in APIVersion:
        if path.startswith(f"/api/{version.value}/"):
            return version

    # Check header
    version_header = request.headers.get(VERSION_HEADER)
    if version_header:
        try:
            return APIVersion(version_header.lower())
        except ValueError:
            logger.warning(f"Invalid API version in header: {version_header}")

    # Default
    return APIVersion.default()


def add_version_headers(
    response_headers: dict[str, str],
    version: APIVersion,
    is_deprecated: bool = False,
    sunset: str | None = None,
) -> None:
    """
    Add version-related headers to a response.

    Args:
        response_headers: Headers dict to modify
        version: The API version used
        is_deprecated: Whether this endpoint is deprecated
        sunset: Sunset date for deprecated endpoints
    """
    response_headers[VERSION_HEADER] = version.value

    if is_deprecated:
        response_headers[DEPRECATION_HEADER] = "true"
        if sunset:
            response_headers[SUNSET_HEADER] = sunset


# Registry for tracking versioned endpoints
_versioned_endpoints: dict[str, dict[APIVersion, str]] = {}


def register_endpoint_version(
    endpoint_id: str,
    version: APIVersion,
    path: str,
) -> None:
    """Register an endpoint version for tracking."""
    if endpoint_id not in _versioned_endpoints:
        _versioned_endpoints[endpoint_id] = {}
    _versioned_endpoints[endpoint_id][version] = path


def get_endpoint_versions(endpoint_id: str) -> dict[APIVersion, str]:
    """Get all versions of a specific endpoint."""
    return _versioned_endpoints.get(endpoint_id, {})


def get_all_versioned_endpoints() -> dict[str, dict[APIVersion, str]]:
    """Get all registered versioned endpoints."""
    return dict(_versioned_endpoints)
