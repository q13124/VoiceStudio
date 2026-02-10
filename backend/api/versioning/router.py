"""
Versioned API Router.

Task 3.4.1: Version-aware API routing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute


class ApiVersion(Enum):
    """Supported API versions."""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"  # Task 3.4.1: API versioning v3 with breaking changes
    
    @classmethod
    def from_string(cls, value: str) -> Optional["ApiVersion"]:
        """Parse version from string."""
        value = value.lower().strip()
        for version in cls:
            if version.value == value:
                return version
        return None
    
    @classmethod
    def latest(cls) -> "ApiVersion":
        """Get the latest version."""
        return cls.V3


@dataclass
class VersionedRoute:
    """A route with version information."""
    path: str
    method: str
    handler: Callable
    versions: List[ApiVersion]
    deprecated_in: Optional[ApiVersion] = None
    removed_in: Optional[ApiVersion] = None
    replacement: Optional[str] = None


class VersionedAPIRouter:
    """
    API router with version management.
    
    Features:
    - Multiple API versions
    - Automatic version negotiation
    - Deprecation tracking
    - Version-specific handlers
    """
    
    def __init__(self, prefix: str = "/api"):
        """
        Initialize versioned router.
        
        Args:
            prefix: Base API prefix
        """
        self._prefix = prefix
        self._routes: Dict[str, VersionedRoute] = {}
        self._version_routers: Dict[ApiVersion, APIRouter] = {}
        
        # Create routers for each version
        for version in ApiVersion:
            self._version_routers[version] = APIRouter(
                prefix=f"{prefix}/{version.value}"
            )
    
    def route(
        self,
        path: str,
        methods: List[str],
        versions: Optional[List[ApiVersion]] = None,
        deprecated_in: Optional[ApiVersion] = None,
        removed_in: Optional[ApiVersion] = None,
        replacement: Optional[str] = None,
    ) -> Callable:
        """
        Decorator to register a versioned route.
        
        Args:
            path: Route path
            methods: HTTP methods
            versions: API versions (default: all)
            deprecated_in: Version where deprecated
            removed_in: Version where removed
            replacement: Path to replacement endpoint
        """
        versions = versions or list(ApiVersion)
        
        def decorator(handler: Callable) -> Callable:
            for method in methods:
                route_key = f"{method.upper()}:{path}"
                
                self._routes[route_key] = VersionedRoute(
                    path=path,
                    method=method.upper(),
                    handler=handler,
                    versions=versions,
                    deprecated_in=deprecated_in,
                    removed_in=removed_in,
                    replacement=replacement,
                )
                
                # Register with appropriate version routers
                for version in versions:
                    if removed_in and version.value >= removed_in.value:
                        continue
                    
                    router = self._version_routers[version]
                    router.add_api_route(
                        path,
                        handler,
                        methods=[method],
                        deprecated=deprecated_in is not None and version.value >= deprecated_in.value,
                    )
            
            return handler
        
        return decorator
    
    def get(
        self,
        path: str,
        versions: Optional[List[ApiVersion]] = None,
        **kwargs,
    ) -> Callable:
        """Register a GET route."""
        return self.route(path, ["GET"], versions, **kwargs)
    
    def post(
        self,
        path: str,
        versions: Optional[List[ApiVersion]] = None,
        **kwargs,
    ) -> Callable:
        """Register a POST route."""
        return self.route(path, ["POST"], versions, **kwargs)
    
    def put(
        self,
        path: str,
        versions: Optional[List[ApiVersion]] = None,
        **kwargs,
    ) -> Callable:
        """Register a PUT route."""
        return self.route(path, ["PUT"], versions, **kwargs)
    
    def delete(
        self,
        path: str,
        versions: Optional[List[ApiVersion]] = None,
        **kwargs,
    ) -> Callable:
        """Register a DELETE route."""
        return self.route(path, ["DELETE"], versions, **kwargs)
    
    def patch(
        self,
        path: str,
        versions: Optional[List[ApiVersion]] = None,
        **kwargs,
    ) -> Callable:
        """Register a PATCH route."""
        return self.route(path, ["PATCH"], versions, **kwargs)
    
    def get_router(self, version: ApiVersion) -> APIRouter:
        """Get the FastAPI router for a version."""
        return self._version_routers[version]
    
    def get_all_routers(self) -> List[APIRouter]:
        """Get all version routers."""
        return list(self._version_routers.values())
    
    def get_route_info(self) -> List[Dict[str, Any]]:
        """Get information about all routes."""
        return [
            {
                "path": route.path,
                "method": route.method,
                "versions": [v.value for v in route.versions],
                "deprecated_in": route.deprecated_in.value if route.deprecated_in else None,
                "removed_in": route.removed_in.value if route.removed_in else None,
                "replacement": route.replacement,
            }
            for route in self._routes.values()
        ]
