"""
Smart Discovery Module for VoiceStudio
Intelligent engine and module discovery system

Compatible with:
- Python 3.10+
"""

import importlib.util
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Import manifest loader
try:
    from ..engines.manifest_loader import (
        find_engine_manifests,
        get_engine_entry_point,
        load_engine_manifest,
    )

    HAS_MANIFEST_LOADER = True
except ImportError:
    HAS_MANIFEST_LOADER = False
    logger.warning("Manifest loader not available")


class SmartDiscovery:
    """
    Smart Discovery for intelligent engine and module discovery.

    Supports:
    - Automatic engine discovery
    - Dependency validation
    - Health checking
    - Caching
    - Priority-based discovery
    - Filtering and sorting
    """

    def __init__(self, engines_root: str = "engines", cache_enabled: bool = True):
        """
        Initialize Smart Discovery.

        Args:
            engines_root: Root directory for engine discovery
            cache_enabled: Whether to enable discovery caching
        """
        self.engines_root = Path(engines_root)
        self.cache_enabled = cache_enabled
        self.discovery_cache: Dict[str, Any] = {}
        self.discovery_timestamp: Optional[str] = None

    def discover_engines(
        self,
        engine_type: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        require_dependencies: bool = True,
        check_health: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Discover engines with intelligent filtering.

        Args:
            engine_type: Optional engine type filter ("audio", "image", "video")
            capabilities: Optional list of required capabilities
            require_dependencies: Whether to filter out engines with missing dependencies
            check_health: Whether to perform health checks

        Returns:
            Dictionary mapping engine_id to discovery information
        """
        if not HAS_MANIFEST_LOADER:
            logger.error("Manifest loader not available")
            return {}

        # Check cache
        cache_key = f"{engine_type}_{capabilities}_{require_dependencies}_{check_health}"
        if (
            self.cache_enabled
            and cache_key in self.discovery_cache
            and self.discovery_timestamp
        ):
            logger.debug("Using cached discovery results")
            return self.discovery_cache[cache_key]

        # Find all manifests
        manifests = find_engine_manifests(str(self.engines_root))
        discovered_engines = {}

        for engine_id, manifest_path in manifests.items():
            try:
                manifest = load_engine_manifest(manifest_path)

                # Filter by type
                if engine_type and manifest.get("type") != engine_type:
                    continue

                # Filter by capabilities
                if capabilities:
                    engine_capabilities = manifest.get("capabilities", [])
                    if not all(cap in engine_capabilities for cap in capabilities):
                        continue

                # Check dependencies
                if require_dependencies:
                    if not self._check_dependencies(manifest):
                        logger.debug(
                            f"Engine {engine_id} filtered out due to missing dependencies"
                        )
                        continue

                # Health check
                health_status = None
                if check_health:
                    health_status = self._check_engine_health(manifest)

                # Build discovery info
                discovery_info = {
                    "engine_id": engine_id,
                    "manifest": manifest,
                    "manifest_path": manifest_path,
                    "health_status": health_status,
                    "discovered_at": datetime.utcnow().isoformat(),
                }

                discovered_engines[engine_id] = discovery_info

            except Exception as e:
                logger.warning(f"Failed to process engine {engine_id}: {e}")
                continue

        # Cache results
        if self.cache_enabled:
            self.discovery_cache[cache_key] = discovered_engines
            self.discovery_timestamp = datetime.utcnow().isoformat()

        logger.info(f"Discovered {len(discovered_engines)} engines")
        return discovered_engines

    def discover_by_capability(
        self, capability: str, engine_type: Optional[str] = None
    ) -> List[str]:
        """
        Discover engines by capability.

        Args:
            capability: Required capability (e.g., "voice_cloning", "text_to_speech")
            engine_type: Optional engine type filter

        Returns:
            List of engine IDs with the capability
        """
        engines = self.discover_engines(
            engine_type=engine_type, capabilities=[capability], require_dependencies=True
        )
        return list(engines.keys())

    def discover_best_engine(
        self,
        task_type: str,
        capabilities: Optional[List[str]] = None,
        quality_requirements: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Discover the best engine for a task.

        Args:
            task_type: Task type (e.g., "tts", "voice_cloning")
            capabilities: Optional required capabilities
            quality_requirements: Optional quality requirements

        Returns:
            Best engine ID or None
        """
        engines = self.discover_engines(
            engine_type="audio", capabilities=capabilities, require_dependencies=True
        )

        if not engines:
            return None

        # Score engines
        scored_engines = []
        for engine_id, info in engines.items():
            manifest = info["manifest"]
            score = 0.0

            # Base score from manifest quality features
            quality_features = manifest.get("quality_features", {})
            if "mos_estimate" in quality_features:
                mos_str = quality_features["mos_estimate"]
                try:
                    if "-" in mos_str:
                        mos_val = float(mos_str.split("-")[0])
                    else:
                        mos_val = float(mos_str)
                    score += mos_val * 0.4
                except (ValueError, AttributeError):
                    pass

            # Capability match
            engine_caps = manifest.get("capabilities", [])
            if task_type in engine_caps:
                score += 1.0

            # Quality requirements match
            if quality_requirements:
                if self._meets_quality_requirements(manifest, quality_requirements):
                    score += 0.5

            scored_engines.append((engine_id, score))

        # Sort by score
        scored_engines.sort(key=lambda x: x[1], reverse=True)

        if scored_engines:
            return scored_engines[0][0]

        return None

    def _check_dependencies(self, manifest: Dict[str, Any]) -> bool:
        """
        Check if engine dependencies are available.

        Args:
            manifest: Engine manifest

        Returns:
            True if all dependencies are available
        """
        dependencies = manifest.get("dependencies", {})
        if not dependencies:
            return True

        for dep_name, dep_version in dependencies.items():
            try:
                # Try to import the dependency
                spec = importlib.util.find_spec(dep_name)
                if spec is None:
                    logger.debug(f"Dependency {dep_name} not found")
                    return False
            except Exception as e:
                logger.debug(f"Failed to check dependency {dep_name}: {e}")
                return False

        return True

    def _check_engine_health(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check engine health status.

        Args:
            manifest: Engine manifest

        Returns:
            Dictionary with health status
        """
        health = {
            "status": "unknown",
            "dependencies_ok": False,
            "entry_point_ok": False,
            "errors": [],
        }

        # Check dependencies
        health["dependencies_ok"] = self._check_dependencies(manifest)

        # Check entry point
        entry_point = get_engine_entry_point(manifest)
        if entry_point:
            try:
                module_path, class_name = entry_point.rsplit(".", 1)
                spec = importlib.util.find_spec(module_path)
                if spec is not None:
                    health["entry_point_ok"] = True
                else:
                    health["errors"].append(f"Entry point module not found: {module_path}")
            except Exception as e:
                health["errors"].append(f"Entry point check failed: {str(e)}")

        # Overall status
        if health["dependencies_ok"] and health["entry_point_ok"]:
            health["status"] = "healthy"
        elif health["dependencies_ok"] or health["entry_point_ok"]:
            health["status"] = "degraded"
        else:
            health["status"] = "unhealthy"

        return health

    def _meets_quality_requirements(
        self, manifest: Dict[str, Any], requirements: Dict[str, Any]
    ) -> bool:
        """
        Check if engine meets quality requirements.

        Args:
            manifest: Engine manifest
            requirements: Quality requirements dictionary

        Returns:
            True if requirements are met
        """
        quality_features = manifest.get("quality_features", {})

        # Check MOS score
        if "min_mos_score" in requirements:
            min_mos = requirements["min_mos_score"]
            mos_estimate = quality_features.get("mos_estimate", "")
            try:
                if "-" in mos_estimate:
                    mos_val = float(mos_estimate.split("-")[0])
                else:
                    mos_val = float(mos_estimate)
                if mos_val < min_mos:
                    return False
            except (ValueError, AttributeError):
                return False

        # Check similarity
        if "min_similarity" in requirements:
            min_sim = requirements["min_similarity"]
            sim_text = quality_features.get("similarity_score", "").lower()
            sim_estimate = 0.0
            if "very_high" in sim_text or "ultra" in sim_text:
                sim_estimate = 0.90
            elif "high" in sim_text:
                sim_estimate = 0.85
            elif "medium" in sim_text:
                sim_estimate = 0.75
            if sim_estimate < min_sim:
                return False

        return True

    def get_discovery_summary(self) -> Dict[str, Any]:
        """
        Get summary of discovery results.

        Returns:
            Dictionary with discovery summary
        """
        all_engines = self.discover_engines(require_dependencies=False)

        summary = {
            "total_engines": len(all_engines),
            "by_type": {},
            "by_capability": {},
            "healthy_count": 0,
            "unhealthy_count": 0,
        }

        for engine_id, info in all_engines.items():
            manifest = info["manifest"]
            engine_type = manifest.get("type", "unknown")

            # Count by type
            if engine_type not in summary["by_type"]:
                summary["by_type"][engine_type] = 0
            summary["by_type"][engine_type] += 1

            # Count by capability
            capabilities = manifest.get("capabilities", [])
            for cap in capabilities:
                if cap not in summary["by_capability"]:
                    summary["by_capability"][cap] = 0
                summary["by_capability"][cap] += 1

            # Health status
            health = info.get("health_status", {})
            if health.get("status") == "healthy":
                summary["healthy_count"] += 1
            elif health.get("status") == "unhealthy":
                summary["unhealthy_count"] += 1

        return summary

    def clear_cache(self):
        """Clear discovery cache."""
        self.discovery_cache.clear()
        self.discovery_timestamp = None
        logger.info("Discovery cache cleared")

    def refresh_discovery(self):
        """Force refresh of discovery results."""
        self.clear_cache()
        return self.discover_engines()


def create_smart_discovery(
    engines_root: str = "engines", cache_enabled: bool = True
) -> SmartDiscovery:
    """
    Factory function to create a Smart Discovery instance.

    Args:
        engines_root: Root directory for engine discovery
        cache_enabled: Whether to enable discovery caching

    Returns:
        Initialized SmartDiscovery instance
    """
    return SmartDiscovery(engines_root=engines_root, cache_enabled=cache_enabled)

