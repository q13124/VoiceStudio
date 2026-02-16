"""
Version Manifest System

Hash-addressed storage for prompt templates, tool definitions, and policy bundles.
Supports rollback to last-known-good configuration.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class ManifestType(str, Enum):
    """Types of manifests that can be stored."""

    PROMPT_TEMPLATE = "prompt_template"
    TOOL_DEFINITION = "tool_definition"
    POLICY_BUNDLE = "policy_bundle"


class ReleaseChannel(str, Enum):
    """Release channels for manifests."""

    STABLE = "stable"
    BETA = "beta"
    NIGHTLY = "nightly"


@dataclass
class ManifestEntry:
    """
    A versioned manifest entry.

    Attributes:
        manifest_type: Type of manifest
        version: Semantic version string
        channel: Release channel
        content_hash: SHA-256 hash of content
        created_at: Creation timestamp
        previous_version: Previous version for rollback
        previous_hash: Hash of previous version
        description: Human-readable description
        content_path: Path to the actual content file
    """

    manifest_type: ManifestType
    version: str
    channel: ReleaseChannel
    content_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    previous_version: str | None = None
    previous_hash: str | None = None
    description: str = ""
    content_path: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "manifest_type": self.manifest_type.value,
            "version": self.version,
            "channel": self.channel.value,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
            "previous_version": self.previous_version,
            "previous_hash": self.previous_hash,
            "description": self.description,
            "content_path": self.content_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ManifestEntry:
        """Create from dictionary."""
        return cls(
            manifest_type=ManifestType(data["manifest_type"]),
            version=data["version"],
            channel=ReleaseChannel(data["channel"]),
            content_hash=data["content_hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            previous_version=data.get("previous_version"),
            previous_hash=data.get("previous_hash"),
            description=data.get("description", ""),
            content_path=data.get("content_path"),
        )


class VersionManifestStore:
    """
    Hash-addressed storage for version manifests.

    Stores content by hash and maintains version history for rollback.
    """

    def __init__(self, base_path: Path | None = None):
        """
        Initialize the manifest store.

        Args:
            base_path: Base path for storage. Defaults to tools/overseer/agent/manifests/
        """
        if base_path:
            self._base_path = base_path
        else:
            self._base_path = Path(__file__).parent / "manifests"

        self._base_path.mkdir(parents=True, exist_ok=True)

        # Subdirectories for each type
        self._type_paths = {
            ManifestType.PROMPT_TEMPLATE: self._base_path / "prompt_templates",
            ManifestType.TOOL_DEFINITION: self._base_path / "tool_definitions",
            ManifestType.POLICY_BUNDLE: self._base_path / "policy_bundles",
        }

        for path in self._type_paths.values():
            path.mkdir(parents=True, exist_ok=True)

        # Index file
        self._index_path = self._base_path / "manifest_index.json"
        self._index: dict[str, ManifestEntry] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load the manifest index from disk."""
        if self._index_path.exists():
            try:
                data = json.loads(self._index_path.read_text(encoding="utf-8"))
                for key, entry_data in data.get("manifests", {}).items():
                    self._index[key] = ManifestEntry.from_dict(entry_data)
            # Best effort - failure is acceptable here
            except (OSError, json.JSONDecodeError):
                pass

    def _save_index(self) -> None:
        """Save the manifest index to disk."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "manifests": {k: v.to_dict() for k, v in self._index.items()},
        }
        self._index_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )

    @staticmethod
    def _compute_hash(content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    def _get_content_path(self, manifest_type: ManifestType, content_hash: str) -> Path:
        """Get the storage path for content."""
        return self._type_paths[manifest_type] / f"{content_hash[:16]}.json"

    def _make_key(self, manifest_type: ManifestType, name: str, channel: ReleaseChannel) -> str:
        """Create a lookup key for a manifest."""
        return f"{manifest_type.value}:{name}:{channel.value}"

    def store(
        self,
        manifest_type: ManifestType,
        name: str,
        version: str,
        content: dict,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
        description: str = "",
    ) -> ManifestEntry:
        """
        Store a new manifest version.

        Args:
            manifest_type: Type of manifest
            name: Unique name for this manifest
            version: Semantic version string
            content: The content to store
            channel: Release channel
            description: Human-readable description

        Returns:
            The created manifest entry
        """
        # Serialize and hash content
        content_bytes = json.dumps(content, sort_keys=True, indent=2).encode("utf-8")
        content_hash = self._compute_hash(content_bytes)

        # Get previous version info
        key = self._make_key(manifest_type, name, channel)
        previous_entry = self._index.get(key)

        # Store content file
        content_path = self._get_content_path(manifest_type, content_hash)
        content_path.write_bytes(content_bytes)

        # Create manifest entry
        entry = ManifestEntry(
            manifest_type=manifest_type,
            version=version,
            channel=channel,
            content_hash=content_hash,
            description=description,
            content_path=str(content_path),
            previous_version=previous_entry.version if previous_entry else None,
            previous_hash=previous_entry.content_hash if previous_entry else None,
        )

        # Update index
        self._index[key] = entry
        self._save_index()

        return entry

    def get(
        self,
        manifest_type: ManifestType,
        name: str,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
    ) -> ManifestEntry | None:
        """
        Get a manifest entry.

        Args:
            manifest_type: Type of manifest
            name: Manifest name
            channel: Release channel

        Returns:
            The manifest entry, or None if not found
        """
        key = self._make_key(manifest_type, name, channel)
        return self._index.get(key)

    def get_content(self, entry: ManifestEntry) -> dict | None:
        """
        Get the content for a manifest entry.

        Args:
            entry: The manifest entry

        Returns:
            The parsed content, or None if not found
        """
        if not entry.content_path:
            return None

        content_path = Path(entry.content_path)
        if not content_path.exists():
            return None

        try:
            return json.loads(content_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def get_by_hash(self, content_hash: str) -> dict | None:
        """
        Get content by its hash (for any type).

        Args:
            content_hash: The content hash

        Returns:
            The parsed content, or None if not found
        """
        for manifest_type in ManifestType:
            content_path = self._get_content_path(manifest_type, content_hash)
            if content_path.exists():
                try:
                    return json.loads(content_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
        return None

    def rollback(
        self,
        manifest_type: ManifestType,
        name: str,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
    ) -> ManifestEntry | None:
        """
        Rollback to the previous version.

        Args:
            manifest_type: Type of manifest
            name: Manifest name
            channel: Release channel

        Returns:
            The previous manifest entry, or None if rollback not possible
        """
        key = self._make_key(manifest_type, name, channel)
        current = self._index.get(key)

        if not current or not current.previous_hash:
            return None

        # Find the previous entry by hash
        previous_content = self.get_by_hash(current.previous_hash)
        if not previous_content:
            return None

        # Restore previous version
        previous_entry = ManifestEntry(
            manifest_type=manifest_type,
            version=current.previous_version or "0.0.0",
            channel=channel,
            content_hash=current.previous_hash,
            content_path=str(self._get_content_path(manifest_type, current.previous_hash)),
            description=f"Rolled back from {current.version}",
        )

        self._index[key] = previous_entry
        self._save_index()

        return previous_entry

    def list_versions(
        self,
        manifest_type: ManifestType,
        name: str,
    ) -> list[ManifestEntry]:
        """
        List all versions of a manifest across channels.

        Args:
            manifest_type: Type of manifest
            name: Manifest name

        Returns:
            List of manifest entries
        """
        results = []
        for channel in ReleaseChannel:
            key = self._make_key(manifest_type, name, channel)
            if key in self._index:
                results.append(self._index[key])
        return results

    def get_all(self, manifest_type: ManifestType | None = None) -> list[ManifestEntry]:
        """
        Get all manifest entries.

        Args:
            manifest_type: Optional filter by type

        Returns:
            List of manifest entries
        """
        if manifest_type:
            return [e for e in self._index.values() if e.manifest_type == manifest_type]
        return list(self._index.values())
