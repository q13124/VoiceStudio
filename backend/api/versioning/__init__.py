"""
API Versioning System.

Task 3.4: API evolution with backward compatibility.
"""

from backend.api.versioning.router import VersionedAPIRouter
from backend.api.versioning.negotiation import ApiVersionNegotiator, VersionInfo
from backend.api.versioning.deprecation import DeprecationManager

# Re-export legacy versioning items for backward compatibility
# These are defined in backend/api/versioning.py (legacy module)
# but since the package takes precedence, we need to import and re-export
import importlib.util
import os

# Load the versioning.py module directly (sibling file)
_versioning_module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "versioning.py")
if os.path.exists(_versioning_module_path):
    _spec = importlib.util.spec_from_file_location("_versioning_legacy", _versioning_module_path)
    _versioning_legacy = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_versioning_legacy)
    
    # Import items from legacy module
    APIVersion = _versioning_legacy.APIVersion
    CURRENT_VERSION = _versioning_legacy.CURRENT_VERSION
    MIN_SUPPORTED_VERSION = _versioning_legacy.MIN_SUPPORTED_VERSION
    HEADER_API_VERSION = _versioning_legacy.HEADER_API_VERSION
    HEADER_MIN_VERSION = _versioning_legacy.HEADER_MIN_VERSION
    VERSION_HEADER = _versioning_legacy.VERSION_HEADER
    DEPRECATION_HEADER = _versioning_legacy.DEPRECATION_HEADER
    SUNSET_HEADER = _versioning_legacy.SUNSET_HEADER
    VersionNegotiator = _versioning_legacy.VersionNegotiator
    get_version_headers = _versioning_legacy.get_version_headers
    get_api_version_prefix = _versioning_legacy.get_api_version_prefix
    create_versioned_router = _versioning_legacy.create_versioned_router
    create_v1_router = _versioning_legacy.create_v1_router
    create_v2_router = _versioning_legacy.create_v2_router
    deprecated = _versioning_legacy.deprecated
    get_version_from_request = _versioning_legacy.get_version_from_request
    add_version_headers = _versioning_legacy.add_version_headers
    register_endpoint_version = _versioning_legacy.register_endpoint_version
    get_endpoint_versions = _versioning_legacy.get_endpoint_versions
    get_all_versioned_endpoints = _versioning_legacy.get_all_versioned_endpoints

__all__ = [
    "VersionedAPIRouter",
    "ApiVersionNegotiator",
    "DeprecationManager",
    # Legacy exports
    "APIVersion",
    "CURRENT_VERSION",
    "MIN_SUPPORTED_VERSION",
    "HEADER_API_VERSION",
    "HEADER_MIN_VERSION",
    "VERSION_HEADER",
    "DEPRECATION_HEADER",
    "SUNSET_HEADER",
    "VersionNegotiator",
    "get_version_headers",
    "get_api_version_prefix",
    "create_versioned_router",
    "create_v1_router",
    "create_v2_router",
    "deprecated",
    "get_version_from_request",
    "add_version_headers",
    "register_endpoint_version",
    "get_endpoint_versions",
    "get_all_versioned_endpoints",
]
