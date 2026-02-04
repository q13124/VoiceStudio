"""
Release Manager

Manages release channels for agent configuration.
Supports stable/beta/nightly channels with rollback capability.
"""

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .manifest_signer import ManifestSigner, SignedManifest


class ReleaseChannel(str, Enum):
    """Release channels for agent configuration."""
    
    STABLE = "stable"
    BETA = "beta"
    NIGHTLY = "nightly"


class BundleType(str, Enum):
    """Types of configuration bundles."""
    
    PROMPT_TEMPLATE = "prompt_template"
    TOOL_DEFINITION = "tool_definition"
    POLICY_BUNDLE = "policy_bundle"


@dataclass
class ReleaseBundle:
    """
    A release bundle containing signed configuration.
    
    Attributes:
        bundle_id: Unique identifier
        bundle_type: Type of bundle
        name: Human-readable name
        version: Semantic version
        channel: Release channel
        signed_manifest: Cryptographic signature
        content: The actual configuration content
        created_at: When the bundle was created
        changelog: Description of changes
        is_active: Whether this is the active version
    """
    
    bundle_id: str
    bundle_type: BundleType
    name: str
    version: str
    channel: ReleaseChannel
    signed_manifest: SignedManifest
    content: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    changelog: str = ""
    is_active: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "bundle_id": self.bundle_id,
            "bundle_type": self.bundle_type.value,
            "name": self.name,
            "version": self.version,
            "channel": self.channel.value,
            "signed_manifest": self.signed_manifest.to_dict(),
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "changelog": self.changelog,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ReleaseBundle":
        """Create from dictionary."""
        return cls(
            bundle_id=data["bundle_id"],
            bundle_type=BundleType(data["bundle_type"]),
            name=data["name"],
            version=data["version"],
            channel=ReleaseChannel(data["channel"]),
            signed_manifest=SignedManifest.from_dict(data["signed_manifest"]),
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            changelog=data.get("changelog", ""),
            is_active=data.get("is_active", False),
        )


class ReleaseManager:
    """
    Manages release channels and bundle deployment.
    
    Features:
    - Multiple release channels (stable/beta/nightly)
    - Signed bundles for integrity
    - Version history with rollback
    - Promotion between channels
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        signer: Optional[ManifestSigner] = None,
        max_history: int = 10,
    ):
        """
        Initialize the release manager.
        
        Args:
            storage_path: Base path for storing bundles
            signer: Manifest signer for signing bundles
            max_history: Maximum versions to keep per bundle
        """
        if storage_path:
            self._storage_path = storage_path
        else:
            self._storage_path = Path(__file__).parent / "releases"
        
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._signer = signer or ManifestSigner()
        self._max_history = max_history
        
        # Index of all bundles
        self._index_path = self._storage_path / "release_index.json"
        self._index: Dict[str, List[ReleaseBundle]] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        """Load the release index from disk."""
        if self._index_path.exists():
            try:
                data = json.loads(self._index_path.read_text(encoding="utf-8"))
                for key, bundle_list in data.get("bundles", {}).items():
                    self._index[key] = [
                        ReleaseBundle.from_dict(b) for b in bundle_list
                    ]
            # Best effort - failure is acceptable here
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_index(self) -> None:
        """Save the release index to disk."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "bundles": {
                key: [b.to_dict() for b in bundles]
                for key, bundles in self._index.items()
            },
        }
        self._index_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
    
    def _make_key(
        self,
        bundle_type: BundleType,
        name: str,
        channel: ReleaseChannel,
    ) -> str:
        """Create an index key."""
        return f"{bundle_type.value}:{name}:{channel.value}"
    
    def _generate_bundle_id(self) -> str:
        """Generate a unique bundle ID."""
        import uuid
        return str(uuid.uuid4())
    
    def publish(
        self,
        bundle_type: BundleType,
        name: str,
        version: str,
        content: Dict[str, Any],
        channel: ReleaseChannel = ReleaseChannel.NIGHTLY,
        changelog: str = "",
        signed_by: str = "system",
    ) -> ReleaseBundle:
        """
        Publish a new bundle.
        
        Args:
            bundle_type: Type of bundle
            name: Bundle name
            version: Semantic version
            content: Bundle content
            channel: Target release channel
            changelog: Description of changes
            signed_by: Identity of the publisher
            
        Returns:
            The published bundle
        """
        # Sign the content
        signed_manifest = self._signer.sign(
            manifest_type=bundle_type.value,
            name=name,
            version=version,
            content=content,
            signed_by=signed_by,
            metadata={
                "channel": channel.value,
                "changelog": changelog,
            },
        )
        
        # Create bundle
        bundle = ReleaseBundle(
            bundle_id=self._generate_bundle_id(),
            bundle_type=bundle_type,
            name=name,
            version=version,
            channel=channel,
            signed_manifest=signed_manifest,
            content=content,
            changelog=changelog,
            is_active=True,
        )
        
        # Add to index
        key = self._make_key(bundle_type, name, channel)
        if key not in self._index:
            self._index[key] = []
        
        # Deactivate previous active version
        for b in self._index[key]:
            b.is_active = False
        
        self._index[key].append(bundle)
        
        # Trim history
        if len(self._index[key]) > self._max_history:
            self._index[key] = self._index[key][-self._max_history:]
        
        # Save content to disk
        bundle_path = self._storage_path / bundle.bundle_id
        bundle_path.mkdir(parents=True, exist_ok=True)
        (bundle_path / "bundle.json").write_text(
            json.dumps(bundle.to_dict(), indent=2),
            encoding="utf-8"
        )
        (bundle_path / "content.json").write_text(
            json.dumps(content, indent=2),
            encoding="utf-8"
        )
        
        self._save_index()
        return bundle
    
    def get_active(
        self,
        bundle_type: BundleType,
        name: str,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
    ) -> Optional[ReleaseBundle]:
        """Get the active bundle for a type/name/channel."""
        key = self._make_key(bundle_type, name, channel)
        bundles = self._index.get(key, [])
        
        for bundle in reversed(bundles):
            if bundle.is_active:
                return bundle
        
        # Fallback to most recent if no active
        return bundles[-1] if bundles else None
    
    def get_version(
        self,
        bundle_type: BundleType,
        name: str,
        version: str,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
    ) -> Optional[ReleaseBundle]:
        """Get a specific version of a bundle."""
        key = self._make_key(bundle_type, name, channel)
        bundles = self._index.get(key, [])
        
        for bundle in bundles:
            if bundle.version == version:
                return bundle
        
        return None
    
    def get_history(
        self,
        bundle_type: BundleType,
        name: str,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
    ) -> List[ReleaseBundle]:
        """Get version history for a bundle."""
        key = self._make_key(bundle_type, name, channel)
        return list(self._index.get(key, []))
    
    def rollback(
        self,
        bundle_type: BundleType,
        name: str,
        channel: ReleaseChannel = ReleaseChannel.STABLE,
        to_version: Optional[str] = None,
    ) -> Optional[ReleaseBundle]:
        """
        Rollback to a previous version.
        
        Args:
            bundle_type: Type of bundle
            name: Bundle name
            channel: Release channel
            to_version: Specific version to rollback to.
                       If None, rollback to previous version.
            
        Returns:
            The now-active bundle, or None if rollback failed
        """
        key = self._make_key(bundle_type, name, channel)
        bundles = self._index.get(key, [])
        
        if len(bundles) < 2:
            return None  # Nothing to rollback to
        
        if to_version:
            # Find specific version
            target_idx = None
            for i, bundle in enumerate(bundles):
                if bundle.version == to_version:
                    target_idx = i
                    break
            
            if target_idx is None:
                return None
        else:
            # Rollback to previous
            target_idx = -2  # Second to last
        
        # Deactivate all and activate target
        for bundle in bundles:
            bundle.is_active = False
        
        bundles[target_idx].is_active = True
        self._save_index()
        
        return bundles[target_idx]
    
    def promote(
        self,
        bundle_type: BundleType,
        name: str,
        from_channel: ReleaseChannel,
        to_channel: ReleaseChannel,
        signed_by: str = "system",
    ) -> Optional[ReleaseBundle]:
        """
        Promote a bundle from one channel to another.
        
        Args:
            bundle_type: Type of bundle
            name: Bundle name
            from_channel: Source channel
            to_channel: Target channel
            signed_by: Identity of promoter
            
        Returns:
            The promoted bundle in the new channel
        """
        # Get active bundle from source channel
        source_bundle = self.get_active(bundle_type, name, from_channel)
        if source_bundle is None:
            return None
        
        # Re-publish to target channel
        return self.publish(
            bundle_type=bundle_type,
            name=name,
            version=source_bundle.version,
            content=source_bundle.content,
            channel=to_channel,
            changelog=f"Promoted from {from_channel.value}: {source_bundle.changelog}",
            signed_by=signed_by,
        )
    
    def verify_bundle(self, bundle: ReleaseBundle) -> bool:
        """Verify a bundle's signature."""
        is_valid, _ = self._signer.verify_content(
            bundle.signed_manifest,
            bundle.content,
        )
        return is_valid
    
    def list_bundles(
        self,
        bundle_type: Optional[BundleType] = None,
        channel: Optional[ReleaseChannel] = None,
        active_only: bool = False,
    ) -> List[ReleaseBundle]:
        """
        List all bundles with optional filtering.
        
        Args:
            bundle_type: Filter by type
            channel: Filter by channel
            active_only: Only return active bundles
            
        Returns:
            List of matching bundles
        """
        results = []
        
        for key, bundles in self._index.items():
            parts = key.split(":")
            key_type = BundleType(parts[0])
            key_channel = ReleaseChannel(parts[2])
            
            if bundle_type and key_type != bundle_type:
                continue
            
            if channel and key_channel != channel:
                continue
            
            for bundle in bundles:
                if active_only and not bundle.is_active:
                    continue
                results.append(bundle)
        
        return results
    
    def cleanup_old_bundles(self, keep_last: int = 5) -> int:
        """
        Clean up old bundle files.
        
        Args:
            keep_last: Number of versions to keep
            
        Returns:
            Number of bundles removed
        """
        removed = 0
        
        for key, bundles in self._index.items():
            if len(bundles) > keep_last:
                to_remove = bundles[:-keep_last]
                self._index[key] = bundles[-keep_last:]
                
                for bundle in to_remove:
                    bundle_path = self._storage_path / bundle.bundle_id
                    if bundle_path.exists():
                        shutil.rmtree(bundle_path)
                        removed += 1
        
        self._save_index()
        return removed
    
    def get_stats(self) -> dict:
        """Get release manager statistics."""
        by_type = {}
        by_channel = {}
        total_bundles = 0
        active_bundles = 0
        
        for key, bundles in self._index.items():
            parts = key.split(":")
            bundle_type = parts[0]
            channel = parts[2]
            
            by_type[bundle_type] = by_type.get(bundle_type, 0) + len(bundles)
            by_channel[channel] = by_channel.get(channel, 0) + len(bundles)
            
            total_bundles += len(bundles)
            active_bundles += sum(1 for b in bundles if b.is_active)
        
        return {
            "total_bundles": total_bundles,
            "active_bundles": active_bundles,
            "by_type": by_type,
            "by_channel": by_channel,
        }
