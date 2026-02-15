"""
API Deprecation Management.

Task 3.4.3: Deprecation notices and sunset headers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api.versioning.router import ApiVersion

logger = logging.getLogger(__name__)


@dataclass
class DeprecationNotice:
    """A deprecation notice for an endpoint."""
    path: str
    method: str
    deprecated_in: ApiVersion
    sunset_date: datetime | None = None
    replacement: str | None = None
    message: str | None = None


@dataclass
class VersionSunset:
    """Sunset information for an API version."""
    version: ApiVersion
    sunset_date: datetime
    announcement_date: datetime
    migration_guide: str | None = None


class DeprecationManager:
    """
    Manages API deprecations and sunset schedules.

    Features:
    - Track deprecated endpoints
    - Version sunset dates
    - Deprecation headers
    - Usage warnings
    """

    def __init__(self):
        self._deprecations: dict[str, DeprecationNotice] = {}
        self._version_sunsets: dict[ApiVersion, VersionSunset] = {}
        self._usage_counts: dict[str, int] = {}

    def deprecate_endpoint(
        self,
        path: str,
        method: str,
        deprecated_in: ApiVersion,
        sunset_date: datetime | None = None,
        replacement: str | None = None,
        message: str | None = None,
    ) -> None:
        """
        Register a deprecated endpoint.

        Args:
            path: Endpoint path
            method: HTTP method
            deprecated_in: Version where deprecated
            sunset_date: When endpoint will be removed
            replacement: Path to replacement endpoint
            message: Custom deprecation message
        """
        key = f"{method.upper()}:{path}"

        self._deprecations[key] = DeprecationNotice(
            path=path,
            method=method.upper(),
            deprecated_in=deprecated_in,
            sunset_date=sunset_date,
            replacement=replacement,
            message=message,
        )

        logger.info(f"Registered deprecation: {key}")

    def set_version_sunset(
        self,
        version: ApiVersion,
        sunset_date: datetime,
        migration_guide: str | None = None,
    ) -> None:
        """
        Set sunset date for an API version.

        Args:
            version: API version
            sunset_date: When version will be removed
            migration_guide: URL to migration guide
        """
        self._version_sunsets[version] = VersionSunset(
            version=version,
            sunset_date=sunset_date,
            announcement_date=datetime.now(),
            migration_guide=migration_guide,
        )

        logger.info(f"Version {version.value} sunset: {sunset_date}")

    def get_deprecation(
        self,
        path: str,
        method: str,
    ) -> DeprecationNotice | None:
        """Get deprecation notice for an endpoint."""
        key = f"{method.upper()}:{path}"
        return self._deprecations.get(key)

    def get_version_sunset(
        self,
        version: ApiVersion,
    ) -> VersionSunset | None:
        """Get sunset info for a version."""
        return self._version_sunsets.get(version)

    def is_deprecated(self, path: str, method: str) -> bool:
        """Check if an endpoint is deprecated."""
        key = f"{method.upper()}:{path}"
        return key in self._deprecations

    def is_version_sunset(self, version: ApiVersion) -> bool:
        """Check if a version is past its sunset date."""
        sunset = self._version_sunsets.get(version)
        if sunset:
            return datetime.now() >= sunset.sunset_date
        return False

    def get_deprecation_headers(
        self,
        path: str,
        method: str,
    ) -> dict[str, str]:
        """
        Get HTTP headers for deprecation.

        Returns headers like:
        - Deprecation: true
        - Sunset: Wed, 01 Jan 2025 00:00:00 GMT
        - Link: </api/v2/new-endpoint>; rel="successor-version"
        """
        headers = {}

        notice = self.get_deprecation(path, method)
        if notice:
            headers["Deprecation"] = "true"

            if notice.sunset_date:
                headers["Sunset"] = notice.sunset_date.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )

            if notice.replacement:
                headers["Link"] = f'<{notice.replacement}>; rel="successor-version"'

        return headers

    def record_usage(self, path: str, method: str) -> None:
        """Record usage of a deprecated endpoint."""
        key = f"{method.upper()}:{path}"
        if key in self._deprecations:
            self._usage_counts[key] = self._usage_counts.get(key, 0) + 1

    def get_usage_stats(self) -> dict[str, int]:
        """Get usage counts for deprecated endpoints."""
        return self._usage_counts.copy()

    def list_deprecations(self) -> list[DeprecationNotice]:
        """List all deprecated endpoints."""
        return list(self._deprecations.values())

    def list_upcoming_sunsets(
        self,
        days: int = 30,
    ) -> list[DeprecationNotice]:
        """List endpoints with sunset dates in the next N days."""
        cutoff = datetime.now() + timedelta(days=days)

        return [
            notice for notice in self._deprecations.values()
            if notice.sunset_date and notice.sunset_date <= cutoff
        ]


class DeprecationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add deprecation headers.
    """

    def __init__(self, app, manager: DeprecationManager | None = None):
        super().__init__(app)
        self._manager = manager or DeprecationManager()

    async def dispatch(self, request: Request, call_next):
        """Add deprecation headers to response."""
        response: Response = await call_next(request)

        # Get deprecation headers
        path = request.url.path
        method = request.method

        headers = self._manager.get_deprecation_headers(path, method)

        for name, value in headers.items():
            response.headers[name] = value

        # Record usage
        if headers:
            self._manager.record_usage(path, method)

        return response


# Global deprecation manager
_manager: DeprecationManager | None = None


def get_deprecation_manager() -> DeprecationManager:
    """Get or create the global deprecation manager."""
    global _manager
    if _manager is None:
        _manager = DeprecationManager()
    return _manager
