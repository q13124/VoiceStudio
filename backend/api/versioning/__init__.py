"""
API Versioning System.

Task 3.4: API evolution with backward compatibility.
"""

from backend.api.versioning.router import VersionedAPIRouter
from backend.api.versioning.negotiation import ApiVersionNegotiator
from backend.api.versioning.deprecation import DeprecationManager

__all__ = [
    "VersionedAPIRouter",
    "ApiVersionNegotiator",
    "DeprecationManager",
]
