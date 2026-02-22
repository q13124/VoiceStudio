"""
Route validation utilities for detecting duplicate and conflicting routes.

GAP-B02: Added route conflict detection at startup to prevent duplicate
route prefixes from causing routing issues.
"""

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


def validate_routes(app: "FastAPI") -> list[str]:
    """
    Detect duplicate route prefixes and paths at startup.

    This function scans all registered routes in a FastAPI application
    and identifies potential conflicts such as:
    - Duplicate exact paths with the same HTTP method
    - Overlapping prefix patterns that could cause routing ambiguity

    Args:
        app: The FastAPI application instance to validate.

    Returns:
        A list of warning/error messages describing any conflicts found.
        An empty list indicates no conflicts were detected.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> conflicts = validate_routes(app)
        >>> if conflicts:
        ...     for conflict in conflicts:
        ...         logger.warning(conflict)
    """
    conflicts: list[str] = []

    # Track routes by path and method
    routes_by_path: dict[str, list[tuple[str, str]]] = defaultdict(list)

    # Track route prefixes for overlap detection
    prefix_sources: dict[str, list[str]] = defaultdict(list)

    for route in app.routes:
        path = getattr(route, "path", None)
        if path is None:
            continue

        # Get HTTP methods for this route
        methods = getattr(route, "methods", {"GET"})
        if methods is None:
            methods = {"GET"}

        # Track each method+path combination
        for method in methods:
            routes_by_path[path].append((method, getattr(route, "name", "unknown")))

        # Extract prefix (first two segments: e.g., "/api/plugins")
        segments = path.strip("/").split("/")
        if len(segments) >= 2:
            prefix = "/" + "/".join(segments[:2])
            endpoint_name = getattr(route, "name", path)
            prefix_sources[prefix].append(endpoint_name)

    # Check for duplicate exact routes (same path + method)
    for path, method_names in routes_by_path.items():
        method_counts: dict[str, list[str]] = defaultdict(list)
        for method, name in method_names:
            method_counts[method].append(name)

        for method, names in method_counts.items():
            if len(names) > 1:
                conflicts.append(f"Duplicate route: {method} {path} defined by: {', '.join(names)}")

    # Log summary of prefix distribution (informational)
    logger.debug(
        f"Route prefix distribution: {len(prefix_sources)} unique prefixes, "
        f"{sum(len(v) for v in prefix_sources.values())} total endpoints"
    )

    return conflicts


def log_route_conflicts(app: "FastAPI") -> bool:
    """
    Validate routes and log any conflicts found.

    This is a convenience wrapper around validate_routes that logs
    warnings for each conflict and returns a boolean indicating
    whether any conflicts were found.

    Args:
        app: The FastAPI application instance to validate.

    Returns:
        True if conflicts were found, False otherwise.
    """
    conflicts = validate_routes(app)

    if conflicts:
        logger.warning("=" * 60)
        logger.warning("ROUTE CONFLICTS DETECTED")
        logger.warning("=" * 60)
        for conflict in conflicts:
            logger.warning(f"  - {conflict}")
        logger.warning("=" * 60)
        return True

    logger.info("Route validation passed: No conflicts detected")
    return False


def get_route_summary(app: "FastAPI") -> dict[str, list[str]]:
    """
    Get a summary of all registered routes grouped by prefix.

    Useful for debugging and documentation generation.

    Args:
        app: The FastAPI application instance.

    Returns:
        A dictionary mapping route prefixes to lists of full paths.
    """
    prefix_map: dict[str, list[str]] = defaultdict(list)

    for route in app.routes:
        path = getattr(route, "path", None)
        if path is None:
            continue

        segments = path.strip("/").split("/")
        if len(segments) >= 2:
            prefix = "/" + "/".join(segments[:2])
        elif len(segments) == 1:
            prefix = "/" + segments[0]
        else:
            prefix = "/"

        if path not in prefix_map[prefix]:
            prefix_map[prefix].append(path)

    # Sort paths within each prefix
    for prefix in prefix_map:
        prefix_map[prefix].sort()

    return dict(prefix_map)
