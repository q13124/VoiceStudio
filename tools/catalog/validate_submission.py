#!/usr/bin/env python3
"""
Validate a plugin submission by fetching and validating the manifest.

Downloads the manifest from the provided URL, validates against schema,
and performs additional checks for catalog requirements.
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# Manifest schema validation
REQUIRED_FIELDS = [
    "id",
    "name",
    "version",
    "description",
    "author",
    "plugin_type",
    "category",
    "entry_point",
]

OPTIONAL_FIELDS = [
    "license",
    "homepage",
    "repository",
    "min_voicestudio_version",
    "max_voicestudio_version",
    "capabilities",
    "permissions",
    "dependencies",
    "configuration",
    "distribution",
    "catalog",
    "trust",
]

# Architectural plugin types (from plugin_type field in manifest)
VALID_PLUGIN_TYPES = [
    "backend_only",
    "frontend_only",
    "full_stack",
]

# Functional categories (from category field in manifest)
VALID_CATEGORIES = [
    "voice_synthesis",
    "speech_recognition",
    "audio_effects",
    "audio_analysis",
    "voice_conversion",
    "utilities",
]

VALID_PERMISSIONS = [
    "file_read",
    "file_write",
    "network_local",
    "network_internet",
    "system_info",
    "clipboard",
    "audio_capture",
    "audio_playback",
    "gpu_access",
    "subprocess",
]


def fetch_manifest(url: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Fetch manifest from URL."""
    try:
        with urlopen(url, timeout=30) as response:
            content = response.read().decode("utf-8")
            manifest = json.loads(content)
            return manifest, None
    except HTTPError as e:
        return None, f"HTTP error fetching manifest: {e.code} {e.reason}"
    except URLError as e:
        return None, f"URL error fetching manifest: {e.reason}"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in manifest: {e}"
    except Exception as e:
        return None, f"Error fetching manifest: {e}"


def validate_manifest_structure(manifest: Dict[str, Any]) -> List[str]:
    """Validate manifest structure and required fields."""
    errors = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
        elif not manifest[field]:
            errors.append(f"Empty required field: {field}")
    
    # Validate plugin type (architectural)
    plugin_type = manifest.get("plugin_type", "")
    if plugin_type and plugin_type not in VALID_PLUGIN_TYPES:
        errors.append(f"Invalid plugin_type: {plugin_type}. Must be one of: {', '.join(VALID_PLUGIN_TYPES)}")
    
    # Validate category (functional)
    category = manifest.get("category", "")
    if category and category not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {category}. Must be one of: {', '.join(VALID_CATEGORIES)}")
    
    # Validate version format
    version = manifest.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", version):
        errors.append(f"Invalid version format: {version}. Use semantic versioning")
    
    # Validate permissions
    permissions = manifest.get("permissions", [])
    if isinstance(permissions, list):
        for perm in permissions:
            if perm not in VALID_PERMISSIONS:
                errors.append(f"Unknown permission: {perm}")
    else:
        errors.append("permissions must be a list")
    
    # Validate author structure
    author = manifest.get("author", {})
    if isinstance(author, dict):
        if "name" not in author:
            errors.append("author.name is required")
    elif isinstance(author, str):
        # String author is acceptable for simple cases
        pass
    else:
        errors.append("author must be a string or object with name field")
    
    # Validate entry_point
    entry_point = manifest.get("entry_point", "")
    if entry_point and not entry_point.endswith(".py"):
        errors.append("entry_point must be a Python file (.py)")
    
    return errors


def validate_catalog_fields(manifest: Dict[str, Any]) -> List[str]:
    """Validate catalog-specific fields for marketplace submission."""
    errors = []
    warnings = []
    
    # Check for catalog metadata
    catalog = manifest.get("catalog", {})
    
    # Note: category is now a required top-level field, validated in validate_manifest_structure
    
    # Check for description length
    description = manifest.get("description", "")
    if len(description) < 20:
        warnings.append("Description is too short. Provide at least 20 characters")
    if len(description) > 500:
        warnings.append("Description exceeds 500 characters and may be truncated")
    
    # Check for screenshots (recommended)
    if "screenshots" not in catalog:
        warnings.append("Consider adding screenshots for better visibility")
    
    # Check for keywords
    if "keywords" not in catalog:
        warnings.append("Consider adding keywords for better discoverability")
    
    return errors


def validate_trust_fields(manifest: Dict[str, Any]) -> List[str]:
    """Validate trust and security fields."""
    errors = []
    
    trust = manifest.get("trust", {})
    
    # Check signature if present
    if "signature" in trust:
        sig = trust["signature"]
        if not isinstance(sig, dict):
            errors.append("trust.signature must be an object")
        elif "algorithm" not in sig or "value" not in sig:
            errors.append("trust.signature requires algorithm and value fields")
    
    # Check checksum if present
    if "checksum" in trust:
        checksum = trust["checksum"]
        if not isinstance(checksum, dict):
            errors.append("trust.checksum must be an object")
        elif "algorithm" not in checksum or "value" not in checksum:
            errors.append("trust.checksum requires algorithm and value fields")
    
    return errors


def validate_distribution_fields(manifest: Dict[str, Any]) -> List[str]:
    """Validate distribution fields."""
    errors = []
    
    distribution = manifest.get("distribution", {})
    
    # Validate package format if specified
    if "format" in distribution:
        fmt = distribution["format"]
        if fmt not in ("vspkg", "zip", "source"):
            errors.append(f"Invalid distribution format: {fmt}")
    
    # Validate pricing if specified
    if "pricing" in distribution:
        pricing = distribution["pricing"]
        valid_pricing = ("free", "paid", "freemium", "subscription")
        if pricing not in valid_pricing:
            errors.append(f"Invalid pricing: {pricing}. Must be one of: {', '.join(valid_pricing)}")
    
    return errors


def validate_against_submission(
    manifest: Dict[str, Any],
    submission: Dict[str, Any]
) -> List[str]:
    """Cross-validate manifest against submission form data."""
    errors = []
    
    # Check ID matches
    manifest_id = manifest.get("id", "")
    submission_id = submission.get("plugin_id", "")
    if manifest_id and submission_id and manifest_id != submission_id:
        errors.append(f"Plugin ID mismatch: manifest has '{manifest_id}', submission has '{submission_id}'")
    
    # Check version matches
    manifest_version = manifest.get("version", "")
    submission_version = submission.get("version", "")
    if manifest_version and submission_version and manifest_version != submission_version:
        errors.append(f"Version mismatch: manifest has '{manifest_version}', submission has '{submission_version}'")
    
    # Check type matches
    manifest_type = manifest.get("plugin_type", "")
    submission_type = submission.get("plugin_type", "")
    if manifest_type and submission_type and manifest_type != submission_type.lower():
        errors.append(f"Plugin type mismatch: manifest has '{manifest_type}', submission has '{submission_type}'")
    
    return errors


def main():
    """Main entry point."""
    # Get submission data from environment
    submission_json = os.environ.get("SUBMISSION_DATA", "")
    
    if not submission_json:
        # Try reading from file
        submission_file = os.environ.get("SUBMISSION_FILE", "")
        if submission_file and Path(submission_file).exists():
            submission_json = Path(submission_file).read_text()
    
    if not submission_json:
        print("Error: No submission data provided", file=sys.stderr)
        sys.exit(1)
    
    try:
        submission = json.loads(submission_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid submission JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get manifest URL
    manifest_url = submission.get("manifest_url")
    if not manifest_url:
        print("Error: No manifest URL in submission", file=sys.stderr)
        sys.exit(1)
    
    # Fetch manifest
    manifest, fetch_error = fetch_manifest(manifest_url)
    if fetch_error:
        result = {
            "is_valid": False,
            "errors": [fetch_error],
            "warnings": [],
            "manifest": None,
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)
    
    # Collect all errors and warnings
    all_errors = []
    all_warnings = []
    
    # Validate manifest structure
    all_errors.extend(validate_manifest_structure(manifest))
    
    # Validate catalog fields
    all_errors.extend(validate_catalog_fields(manifest))
    
    # Validate trust fields
    all_errors.extend(validate_trust_fields(manifest))
    
    # Validate distribution fields
    all_errors.extend(validate_distribution_fields(manifest))
    
    # Cross-validate against submission
    all_errors.extend(validate_against_submission(manifest, submission))
    
    # Build result
    result = {
        "is_valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "manifest": manifest,
    }
    
    # Output JSON
    print(json.dumps(result, indent=2))
    
    # Exit with error if validation failed
    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
