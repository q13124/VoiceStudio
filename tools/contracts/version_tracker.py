"""
Schema Version Tracker - Tracks OpenAPI schema versions and changes.

Features:
- Version history tracking
- Breaking change detection
- Schema comparison
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class SchemaVersion:
    """Represents a schema version."""
    
    version: str
    hash: str
    timestamp: str
    endpoint_count: int = 0
    schema_count: int = 0
    changes: List[str] = field(default_factory=list)
    breaking: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "hash": self.hash,
            "timestamp": self.timestamp,
            "endpoint_count": self.endpoint_count,
            "schema_count": self.schema_count,
            "changes": self.changes,
            "breaking": self.breaking,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaVersion":
        return cls(
            version=data.get("version", ""),
            hash=data.get("hash", ""),
            timestamp=data.get("timestamp", ""),
            endpoint_count=data.get("endpoint_count", 0),
            schema_count=data.get("schema_count", 0),
            changes=data.get("changes", []),
            breaking=data.get("breaking", False),
        )


@dataclass
class SchemaDiff:
    """Differences between two schema versions."""
    
    added_endpoints: List[str] = field(default_factory=list)
    removed_endpoints: List[str] = field(default_factory=list)
    modified_endpoints: List[str] = field(default_factory=list)
    added_schemas: List[str] = field(default_factory=list)
    removed_schemas: List[str] = field(default_factory=list)
    modified_schemas: List[str] = field(default_factory=list)
    
    @property
    def has_breaking_changes(self) -> bool:
        """Check if diff contains breaking changes."""
        # Removing endpoints or schemas is breaking
        return bool(self.removed_endpoints or self.removed_schemas)
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return bool(
            self.added_endpoints
            or self.removed_endpoints
            or self.modified_endpoints
            or self.added_schemas
            or self.removed_schemas
            or self.modified_schemas
        )
    
    def to_change_list(self) -> List[str]:
        """Convert diff to list of change descriptions."""
        changes = []
        
        for ep in self.added_endpoints:
            changes.append(f"Added endpoint: {ep}")
        for ep in self.removed_endpoints:
            changes.append(f"[BREAKING] Removed endpoint: {ep}")
        for ep in self.modified_endpoints:
            changes.append(f"Modified endpoint: {ep}")
        for schema in self.added_schemas:
            changes.append(f"Added schema: {schema}")
        for schema in self.removed_schemas:
            changes.append(f"[BREAKING] Removed schema: {schema}")
        for schema in self.modified_schemas:
            changes.append(f"Modified schema: {schema}")
        
        return changes


class VersionTracker:
    """
    Tracks OpenAPI schema versions and detects changes.
    
    Features:
    - Version history storage
    - Breaking change detection
    - Schema comparison
    """
    
    def __init__(
        self,
        history_file: Optional[Path] = None,
        max_history: int = 50,
    ):
        """
        Initialize version tracker.
        
        Args:
            history_file: Path to version history JSON file
            max_history: Maximum versions to keep in history
        """
        self._history_file = history_file or Path(".cursor/schema_versions.json")
        self._max_history = max_history
        self._versions: List[SchemaVersion] = []
        self._load_history()
    
    def _load_history(self) -> None:
        """Load version history from file."""
        if self._history_file.exists():
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._versions = [
                    SchemaVersion.from_dict(v)
                    for v in data.get("versions", [])
                ]
            except Exception as e:
                logger.warning("Failed to load version history: %s", e)
                self._versions = []
    
    def _save_history(self) -> None:
        """Save version history to file."""
        self._history_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {
                "versions": [v.to_dict() for v in self._versions[-self._max_history:]],
                "updated_at": datetime.now().isoformat(),
            }
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save version history: %s", e)
    
    def compute_hash(self, schema: Dict[str, Any]) -> str:
        """Compute hash of schema content."""
        # Normalize and hash
        content = json.dumps(schema, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def compare_schemas(
        self,
        old_schema: Dict[str, Any],
        new_schema: Dict[str, Any],
    ) -> SchemaDiff:
        """
        Compare two schemas and return differences.
        
        Args:
            old_schema: Previous schema version
            new_schema: Current schema version
        
        Returns:
            SchemaDiff with detected changes
        """
        diff = SchemaDiff()
        
        # Compare paths
        old_paths = set()
        new_paths = set()
        
        for path, methods in old_schema.get("paths", {}).items():
            for method in methods:
                if method in ["get", "post", "put", "delete", "patch"]:
                    old_paths.add(f"{method.upper()} {path}")
        
        for path, methods in new_schema.get("paths", {}).items():
            for method in methods:
                if method in ["get", "post", "put", "delete", "patch"]:
                    new_paths.add(f"{method.upper()} {path}")
        
        diff.added_endpoints = list(new_paths - old_paths)
        diff.removed_endpoints = list(old_paths - new_paths)
        
        # Compare schemas
        old_schemas = set(old_schema.get("components", {}).get("schemas", {}).keys())
        new_schemas = set(new_schema.get("components", {}).get("schemas", {}).keys())
        
        diff.added_schemas = list(new_schemas - old_schemas)
        diff.removed_schemas = list(old_schemas - new_schemas)
        
        # Check for modified schemas (common schemas with different content)
        common_schemas = old_schemas & new_schemas
        for name in common_schemas:
            old_def = old_schema.get("components", {}).get("schemas", {}).get(name, {})
            new_def = new_schema.get("components", {}).get("schemas", {}).get(name, {})
            if json.dumps(old_def, sort_keys=True) != json.dumps(new_def, sort_keys=True):
                diff.modified_schemas.append(name)
        
        return diff
    
    def track_version(
        self,
        schema_path: Path,
        version_override: Optional[str] = None,
    ) -> Optional[SchemaVersion]:
        """
        Track a new schema version.
        
        Args:
            schema_path: Path to OpenAPI schema
            version_override: Optional version string override
        
        Returns:
            SchemaVersion if tracked, None on error
        """
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception as e:
            logger.error("Failed to load schema: %s", e)
            return None
        
        # Extract version
        version = version_override or schema.get("info", {}).get("version", "unknown")
        schema_hash = self.compute_hash(schema)
        
        # Check if already tracked
        if self._versions and self._versions[-1].hash == schema_hash:
            logger.debug("Schema unchanged, not adding to history")
            return self._versions[-1]
        
        # Compute diff from previous
        changes = []
        breaking = False
        if self._versions:
            try:
                with open(schema_path, "r", encoding="utf-8") as f:
                    new_schema = json.load(f)
                
                # We need to load the previous schema
                # For now, compare based on current endpoints
                old_version = self._versions[-1]
                new_count = len(schema.get("paths", {}))
                
                if new_count < old_version.endpoint_count:
                    changes.append(f"Endpoints reduced from {old_version.endpoint_count} to {new_count}")
                    breaking = True
                elif new_count > old_version.endpoint_count:
                    changes.append(f"Endpoints increased from {old_version.endpoint_count} to {new_count}")
            # ALLOWED: bare except - Best effort version comparison
            except Exception:
                pass
        
        # Create version record
        endpoint_count = sum(
            1
            for methods in schema.get("paths", {}).values()
            for method in methods
            if method in ["get", "post", "put", "delete", "patch"]
        )
        schema_count = len(schema.get("components", {}).get("schemas", {}))
        
        version_record = SchemaVersion(
            version=version,
            hash=schema_hash,
            timestamp=datetime.now().isoformat(),
            endpoint_count=endpoint_count,
            schema_count=schema_count,
            changes=changes,
            breaking=breaking,
        )
        
        self._versions.append(version_record)
        self._save_history()
        
        logger.info(
            "Tracked schema version %s (hash: %s, endpoints: %d)",
            version,
            schema_hash,
            endpoint_count,
        )
        
        return version_record
    
    def get_latest(self) -> Optional[SchemaVersion]:
        """Get the latest tracked version."""
        return self._versions[-1] if self._versions else None
    
    def get_history(self, limit: int = 10) -> List[SchemaVersion]:
        """Get version history."""
        return self._versions[-limit:]
    
    def has_breaking_changes(
        self,
        since_version: Optional[str] = None,
    ) -> bool:
        """
        Check if there are breaking changes since a version.
        
        Args:
            since_version: Version to check from (or None for all)
        
        Returns:
            True if breaking changes detected
        """
        versions = self._versions
        
        if since_version:
            found = False
            filtered = []
            for v in versions:
                if found:
                    filtered.append(v)
                if v.version == since_version:
                    found = True
            versions = filtered
        
        return any(v.breaking for v in versions)


# Global tracker instance
_global_tracker: Optional[VersionTracker] = None


def get_version_tracker() -> VersionTracker:
    """Get or create global version tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = VersionTracker()
    return _global_tracker
