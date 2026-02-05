"""
API Versioning Module - Version negotiation and compatibility.

Features:
- API version headers (X-API-Version, X-Min-Version)
- Version negotiation for client compatibility
- Deprecation warnings
- Version-aware routing
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from functools import wraps
from typing import Callable, Dict, List, Optional, Tuple

from fastapi import Header, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class APIVersion(str, Enum):
    """Supported API versions."""

    V1_0 = "1.0"
    V1_1 = "1.1"

    @property
    def tuple(self) -> Tuple[int, int]:
        """Get version as tuple."""
        parts = self.value.split(".")
        return (int(parts[0]), int(parts[1]))

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, APIVersion):
            return NotImplemented
        return self.tuple >= other.tuple

    def __le__(self, other: object) -> bool:
        if not isinstance(other, APIVersion):
            return NotImplemented
        return self.tuple <= other.tuple

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, APIVersion):
            return NotImplemented
        return self.tuple > other.tuple

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, APIVersion):
            return NotImplemented
        return self.tuple < other.tuple


# Current API version
CURRENT_VERSION = APIVersion.V1_0
MIN_SUPPORTED_VERSION = APIVersion.V1_0

# Version header names
HEADER_API_VERSION = "X-API-Version"
HEADER_MIN_VERSION = "X-Min-Version"
HEADER_DEPRECATED = "X-Deprecated"
HEADER_SUNSET = "X-Sunset-Date"


@dataclass
class VersionInfo:
    """Version information for an endpoint or feature."""

    introduced: APIVersion
    deprecated: Optional[APIVersion] = None
    sunset_date: Optional[date] = None
    replacement: Optional[str] = None

    @property
    def is_deprecated(self) -> bool:
        return self.deprecated is not None

    @property
    def is_sunset(self) -> bool:
        if self.sunset_date is None:
            return False
        return date.today() >= self.sunset_date


@dataclass
class NegotiatedVersion:
    """Result of version negotiation."""

    version: APIVersion
    requested: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class VersionNegotiator:
    """Handles API version negotiation."""

    @staticmethod
    def parse_version(version_str: str) -> Optional[APIVersion]:
        """Parse version string to APIVersion enum."""
        if not version_str:
            return None

        # Normalize version string
        version_str = version_str.strip().lower()
        if version_str.startswith("v"):
            version_str = version_str[1:]

        # Try exact match
        try:
            return APIVersion(version_str)
        except ValueError:
            pass

        # Try with minor version defaulted
        if "." not in version_str:
            try:
                return APIVersion(f"{version_str}.0")
            except ValueError:
                pass

        return None

    @staticmethod
    def negotiate(
        requested: Optional[str] = None,
        accept_header: Optional[str] = None,  # Reserved for future use
    ) -> NegotiatedVersion:
        """
        Negotiate API version based on request headers.

        Args:
            requested: Explicit version from X-API-Version header
            accept_header: Accept header (reserved for future use)

        Returns:
            NegotiatedVersion with resolved version and any warnings
        """
        # Future: parse accept_header for version preferences
        _ = accept_header

        result = NegotiatedVersion(version=CURRENT_VERSION, requested=requested)

        if requested:
            parsed = VersionNegotiator.parse_version(requested)
            if parsed:
                if parsed < MIN_SUPPORTED_VERSION:
                    result.warnings.append(
                        f"Requested version {requested} is below minimum "
                        f"supported version {MIN_SUPPORTED_VERSION.value}"
                    )
                    result.version = MIN_SUPPORTED_VERSION
                elif parsed > CURRENT_VERSION:
                    result.warnings.append(
                        f"Requested version {requested} is newer than "
                        f"current version {CURRENT_VERSION.value}"
                    )
                    result.version = CURRENT_VERSION
                else:
                    result.version = parsed
            else:
                result.warnings.append(
                    f"Invalid version format: {requested}. "
                    f"Using {CURRENT_VERSION.value}"
                )

        return result


class VersioningMiddleware(BaseHTTPMiddleware):
    """Middleware to add version headers to responses."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Negotiate version from request
        requested = request.headers.get(HEADER_API_VERSION)
        negotiated = VersionNegotiator.negotiate(requested)

        # Store in request state for handlers
        request.state.api_version = negotiated.version
        request.state.version_warnings = negotiated.warnings

        # Call handler
        response = await call_next(request)

        # Add version headers to response
        response.headers[HEADER_API_VERSION] = CURRENT_VERSION.value
        response.headers[HEADER_MIN_VERSION] = MIN_SUPPORTED_VERSION.value

        # Add warnings as header if any
        if negotiated.warnings:
            response.headers["X-API-Warnings"] = "; ".join(negotiated.warnings)

        return response


def get_api_version(
    x_api_version: Optional[str] = Header(None, alias=HEADER_API_VERSION),
) -> APIVersion:
    """
    FastAPI dependency to get negotiated API version.

    Usage:
        @app.get("/endpoint")
        async def endpoint(version: APIVersion = Depends(get_api_version)):
            if version >= APIVersion.V1_1:
                # New behavior
                pass
    """
    negotiated = VersionNegotiator.negotiate(x_api_version)
    return negotiated.version


def deprecated(
    since: APIVersion,
    sunset_date: Optional[date] = None,
    replacement: Optional[str] = None,
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator to mark endpoint as deprecated.

    Args:
        since: Version when deprecated
        sunset_date: Date when endpoint will be removed
        replacement: Path to replacement endpoint
        message: Custom deprecation message

    Usage:
        @app.get("/old-endpoint")
        @deprecated(since=APIVersion.V1_1, replacement="/new-endpoint")
        async def old_endpoint():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get response from original function
            result = await func(*args, **kwargs)

            # Log deprecation warning
            warn = message or f"Endpoint deprecated since API v{since.value}"
            if replacement:
                warn += f". Use {replacement} instead"
            if sunset_date:
                warn += f". Will be removed on {sunset_date.isoformat()}"

            logger.warning(
                "Deprecated endpoint called: %s - %s",
                func.__name__,
                warn,
            )

            return result

        # Store deprecation info on function for introspection
        setattr(
            wrapper,
            "_deprecated_info",
            VersionInfo(
                introduced=APIVersion.V1_0,
                deprecated=since,
                sunset_date=sunset_date,
                replacement=replacement,
            ),
        )

        return wrapper
    return decorator


def requires_version(min_version: APIVersion) -> Callable:
    """
    Decorator to require minimum API version.

    Args:
        min_version: Minimum version required

    Usage:
        @app.get("/new-endpoint")
        @requires_version(APIVersion.V1_1)
        async def new_endpoint():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get version from request state
            version = getattr(request.state, "api_version", CURRENT_VERSION)

            if version < min_version:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "version_required",
                        "message": (
                            f"This endpoint requires API version "
                            f"{min_version.value} or higher"
                        ),
                        "current_version": version.value,
                        "required_version": min_version.value,
                    },
                )

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


def add_versioning_to_app(app) -> None:
    """
    Add versioning middleware and configuration to FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(VersioningMiddleware)

    # Add version info to OpenAPI schema
    app.openapi_tags = app.openapi_tags or []
    app.openapi_tags.append({
        "name": "versioning",
        "description": (
            f"API Version: {CURRENT_VERSION.value}. "
            f"Minimum supported: {MIN_SUPPORTED_VERSION.value}."
        ),
    })


def get_version_headers() -> Dict[str, str]:
    """Get standard version headers for responses."""
    return {
        HEADER_API_VERSION: CURRENT_VERSION.value,
        HEADER_MIN_VERSION: MIN_SUPPORTED_VERSION.value,
    }
