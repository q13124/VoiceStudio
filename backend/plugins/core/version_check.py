"""
Plugin Version Compatibility Enforcement (Phase 12.2.3)

Enforces min_app_version and version compatibility ranges
from plugin manifests to prevent compatibility issues.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Current application version
APP_VERSION = "1.0.1"


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse a semver-like version string into a tuple of ints."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str.strip())
    if not match:
        return (0, 0, 0)
    return tuple(int(g) for g in match.groups())


def version_satisfies(version: str, constraint: str) -> bool:
    """
    Check if a version satisfies a constraint.

    Supports: >=, <=, >, <, ==, ~= (compatible release)
    """
    constraint = constraint.strip()

    if constraint.startswith(">="):
        return parse_version(version) >= parse_version(constraint[2:])
    elif constraint.startswith("<="):
        return parse_version(version) <= parse_version(constraint[2:])
    elif constraint.startswith(">"):
        return parse_version(version) > parse_version(constraint[1:])
    elif constraint.startswith("<"):
        return parse_version(version) < parse_version(constraint[1:])
    elif constraint.startswith("=="):
        return parse_version(version) == parse_version(constraint[2:])
    elif constraint.startswith("~="):
        # Compatible release (e.g., ~=1.0 means >=1.0, <2.0)
        target = parse_version(constraint[2:])
        current = parse_version(version)
        return current >= target and current[0] == target[0]
    else:
        return parse_version(version) == parse_version(constraint)


def check_plugin_compatibility(
    manifest: Dict[str, Any],
    app_version: str = APP_VERSION,
) -> Dict[str, Any]:
    """
    Check if a plugin is compatible with the current app version.

    Args:
        manifest: Plugin manifest dictionary.
        app_version: Current application version.

    Returns:
        Compatibility check result.
    """
    result: Dict[str, Any] = {
        "compatible": True,
        "plugin_id": manifest.get("engine_id", manifest.get("name", "unknown")),
        "plugin_version": manifest.get("version", "0.0.0"),
        "app_version": app_version,
        "warnings": [],
        "errors": [],
    }

    # Check min_app_version
    min_version = manifest.get("min_app_version", "")
    if min_version:
        if not version_satisfies(app_version, f">={min_version}"):
            result["compatible"] = False
            result["errors"].append(
                f"Requires app version >= {min_version}, current is {app_version}"
            )

    # Check max_app_version
    max_version = manifest.get("max_app_version", "")
    if max_version:
        if not version_satisfies(app_version, f"<={max_version}"):
            result["compatible"] = False
            result["errors"].append(
                f"Maximum supported app version is {max_version}, current is {app_version}"
            )

    # Check Python dependency versions
    deps = manifest.get("dependencies", {})
    python_deps = deps.get("python", [])
    for dep in python_deps:
        # Just log for now -- actual checking would use pkg_resources
        if ">=" in dep or "<=" in dep:
            result["warnings"].append(f"Dependency version constraint: {dep}")

    return result


def check_all_plugins(
    manifests: List[Dict[str, Any]],
    app_version: str = APP_VERSION,
) -> Dict[str, Any]:
    """Check compatibility of all plugins."""
    results = []
    incompatible = []

    for manifest in manifests:
        check = check_plugin_compatibility(manifest, app_version)
        results.append(check)
        if not check["compatible"]:
            incompatible.append(check["plugin_id"])

    return {
        "total": len(results),
        "compatible": len(results) - len(incompatible),
        "incompatible": len(incompatible),
        "incompatible_ids": incompatible,
        "details": results,
    }
