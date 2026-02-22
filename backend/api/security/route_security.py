"""
Route Security Configuration

GAP-CRIT-004: Centralized route security policy for VoiceStudio.

This module defines which route groups require authentication and provides
middleware for applying security policies consistently.

Security Levels:
    - PUBLIC: No authentication required (health, version)
    - OPTIONAL: Auth checked if enabled (most user-facing routes)
    - REQUIRED: Always requires authentication (admin, training)
"""

from __future__ import annotations

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for route protection."""

    PUBLIC = "public"  # No auth required
    OPTIONAL = "optional"  # Auth if enabled
    REQUIRED = "required"  # Always requires auth


# Route security matrix: defines security level per route prefix
ROUTE_SECURITY_MATRIX: dict[str, SecurityLevel] = {
    # Public routes - no auth ever
    "/api/health": SecurityLevel.PUBLIC,
    "/api/v2/health": SecurityLevel.PUBLIC,
    "/api/version": SecurityLevel.PUBLIC,
    "/metrics": SecurityLevel.PUBLIC,
    "/": SecurityLevel.PUBLIC,
    # Optional auth - protected if auth is enabled
    "/api/voice": SecurityLevel.OPTIONAL,
    "/api/voice-browser": SecurityLevel.OPTIONAL,
    "/api/profiles": SecurityLevel.OPTIONAL,
    "/api/projects": SecurityLevel.OPTIONAL,
    "/api/timeline": SecurityLevel.OPTIONAL,
    "/api/engines": SecurityLevel.OPTIONAL,
    "/api/jobs": SecurityLevel.OPTIONAL,
    "/api/audio": SecurityLevel.OPTIONAL,
    "/api/rvc": SecurityLevel.OPTIONAL,
    "/api/pipeline": SecurityLevel.OPTIONAL,
    "/api/plugins": SecurityLevel.OPTIONAL,
    "/api/integrations": SecurityLevel.OPTIONAL,
    "/api/feedback": SecurityLevel.OPTIONAL,
    "/api/realtime": SecurityLevel.OPTIONAL,
    # Required auth - always needs authentication
    "/api/training": SecurityLevel.REQUIRED,
    "/api/admin": SecurityLevel.REQUIRED,
    "/api/api-keys": SecurityLevel.REQUIRED,
    "/api/settings": SecurityLevel.REQUIRED,
}


# Sensitive operations that always require auth (even if route is OPTIONAL)
SENSITIVE_OPERATIONS: set[str] = {
    "POST /api/voice/clone",
    "DELETE /api/profiles",
    "DELETE /api/projects",
    "POST /api/training/start",
    "POST /api/training/export",
    "POST /api/training/import",
}


def get_security_level(path: str) -> SecurityLevel:
    """
    Determine security level for a given path.

    Args:
        path: The request path (e.g., "/api/voice/synthesize")

    Returns:
        SecurityLevel for the path
    """
    # Check exact match first
    if path in ROUTE_SECURITY_MATRIX:
        return ROUTE_SECURITY_MATRIX[path]

    # Check prefix matches (longest match first)
    sorted_prefixes = sorted(ROUTE_SECURITY_MATRIX.keys(), key=len, reverse=True)

    for prefix in sorted_prefixes:
        if path.startswith(prefix):
            return ROUTE_SECURITY_MATRIX[prefix]

    # Default to optional auth
    return SecurityLevel.OPTIONAL


def is_sensitive_operation(method: str, path: str) -> bool:
    """
    Check if a specific operation is marked as sensitive.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path

    Returns:
        True if the operation requires special security consideration
    """
    operation = f"{method.upper()} {path}"

    # Check exact match
    if operation in SENSITIVE_OPERATIONS:
        return True

    # Check prefix matches for sensitive operations
    for sensitive_op in SENSITIVE_OPERATIONS:
        op_method, op_path = sensitive_op.split(" ", 1)
        if method.upper() == op_method and path.startswith(op_path):
            return True

    return False


def log_security_decision(path: str, level: SecurityLevel, authenticated: bool):
    """Log security decision for audit purposes."""
    logger.debug(
        f"Security decision: path={path}, level={level.value}, " f"authenticated={authenticated}"
    )


# Security dependencies for use in routes


async def require_auth_for_training():
    """
    Dependency that requires authentication for training routes.

    This is a placeholder that should be replaced with actual auth logic
    when authentication is fully implemented.
    """
    # The actual auth check is delegated to the middleware
    return True


async def require_auth_for_admin():
    """
    Dependency that requires authentication for admin routes.
    """
    return True


def get_route_security_matrix_report() -> dict:
    """
    Generate a report of the security matrix for documentation.

    Returns:
        Dictionary containing the security matrix report
    """
    report = {
        "public_routes": [],
        "optional_auth_routes": [],
        "required_auth_routes": [],
        "sensitive_operations": list(SENSITIVE_OPERATIONS),
    }

    for path, level in ROUTE_SECURITY_MATRIX.items():
        if level == SecurityLevel.PUBLIC:
            report["public_routes"].append(path)
        elif level == SecurityLevel.OPTIONAL:
            report["optional_auth_routes"].append(path)
        elif level == SecurityLevel.REQUIRED:
            report["required_auth_routes"].append(path)

    return report
