"""
Engine Manifest Loader
Loads and validates engine manifest files
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_engine_manifest(manifest_path: str) -> dict[str, Any]:
    """
    Load and validate an engine manifest file.

    Args:
        manifest_path: Path to engine.manifest.json file

    Returns:
        Dictionary containing manifest data

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        ValueError: If manifest is invalid
    """
    manifest_file = Path(manifest_path)

    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_file, encoding="utf-8") as f:
        manifest = json.load(f)

    # Validate required fields
    required_fields = ["engine_id", "name", "type", "version", "entry_point", "dependencies"]

    for field in required_fields:
        if field not in manifest:
            raise ValueError(f"Manifest missing required field: {field}")

    # Expand environment variables in model paths
    if "model_paths" in manifest:
        for key, path in manifest["model_paths"].items():
            manifest["model_paths"][key] = os.path.expandvars(path)

    logger.info(f"Loaded manifest: {manifest['engine_id']} v{manifest['version']}")
    return manifest


def find_engine_manifests(engines_root: str = "engines") -> dict[str, str]:
    """
    Find all engine manifest files.

    Args:
        engines_root: Root directory containing engine manifests

    Returns:
        Dictionary mapping engine_id to manifest file path
    """
    manifests = {}
    engines_dir = Path(engines_root)

    if not engines_dir.exists():
        logger.warning(f"Engines directory not found: {engines_root}")
        return manifests

    # Search for engine.manifest.json files
    for manifest_file in engines_dir.rglob("engine.manifest.json"):
        try:
            manifest = load_engine_manifest(str(manifest_file))
            engine_id = manifest["engine_id"]
            manifests[engine_id] = str(manifest_file)
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_file}: {e}")

    logger.info(f"Found {len(manifests)} engine manifests")
    return manifests


def get_engine_entry_point(manifest: dict[str, Any]) -> str | None:
    """
    Get the entry point class path from manifest, normalized to module:class format.

    Args:
        manifest: Engine manifest dictionary

    Returns:
        Entry point string in "module:class" format for lazy loading.
        Supports both formats:
        - "app.core.engines.xtts_engine:XTTSEngine" (already normalized)
        - "app.core.engines.xtts_engine.XTTSEngine" (dot-separated, will be converted)
    """
    entry_point = manifest.get("entry_point")
    if not entry_point:
        return None

    # Already in module:class format
    if ":" in entry_point:
        return entry_point

    # Convert dot-separated format to module:class format
    # e.g., "app.core.engines.xtts_engine.XTTSEngine" -> "app.core.engines.xtts_engine:XTTSEngine"
    parts = entry_point.rsplit(".", 1)
    if len(parts) == 2:
        return f"{parts[0]}:{parts[1]}"

    # Fallback: return as-is if we can't parse it
    return entry_point


def get_engine_config_schema(manifest: dict[str, Any]) -> dict[str, Any]:
    """
    Get the configuration schema from manifest.

    Args:
        manifest: Engine manifest dictionary

    Returns:
        Configuration schema dictionary
    """
    return manifest.get("config_schema", {})


def validate_engine_requirements(manifest: dict[str, Any]) -> dict[str, bool]:
    """
    Validate if system meets engine requirements.

    Args:
        manifest: Engine manifest dictionary

    Returns:
        Dictionary with validation results
    """
    import importlib.util
    import sys

    results = {"python_version": True, "dependencies": True, "device": True}

    # Check Python version requirement
    if "python_version" in manifest:
        required_version = manifest["python_version"]
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if isinstance(required_version, str):
            # Parse version requirement (e.g., ">=3.10")
            if required_version.startswith(">="):
                min_version = tuple(map(int, required_version[2:].split(".")))
                current_version_tuple = (sys.version_info.major, sys.version_info.minor)
                results["python_version"] = current_version_tuple >= min_version
            else:
                results["python_version"] = current_version == required_version

    # Check dependencies
    if "dependencies" in manifest:
        deps = manifest["dependencies"]
        if isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, str):
                    # Extract package name (handle version specifiers)
                    package_name = dep.split(">=")[0].split("==")[0].split("<=")[0].strip()
                    spec = importlib.util.find_spec(package_name)
                    if spec is None:
                        results["dependencies"] = False
                        break

    # Check device requirements
    if "device_requirements" in manifest:
        reqs = manifest["device_requirements"]

        # Check GPU requirement
        if reqs.get("gpu") == "required":
            try:
                import torch

                results["device"] = torch.cuda.is_available()
            except ImportError:
                results["device"] = False
        elif reqs.get("gpu") == "optional":
            try:
                import torch

                results["device"] = torch.cuda.is_available() if torch.cuda.is_available() else True
            except ImportError:
                results["device"] = True

        # Check VRAM requirement
        if "vram_gb" in reqs:
            try:
                import torch

                if torch.cuda.is_available():
                    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    required_vram = reqs["vram_gb"]
                    results["device"] = vram_gb >= required_vram
                else:
                    results["device"] = False
            except (ImportError, Exception):
                results["device"] = False

    return results
