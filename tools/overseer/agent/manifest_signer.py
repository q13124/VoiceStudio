"""
Manifest Signer

Signs and verifies manifests for prompt templates, tool definitions,
and policy bundles to ensure integrity and authenticity.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms."""

    HMAC_SHA256 = "HMAC-SHA256"
    HMAC_SHA512 = "HMAC-SHA512"


@dataclass
class SignedManifest:
    """
    A cryptographically signed manifest.

    Attributes:
        manifest_type: Type of manifest (prompt_template, tool_definition, policy_bundle)
        name: Name of the manifest
        version: Semantic version
        content_hash: SHA-256 hash of the content
        signature: Cryptographic signature
        algorithm: Algorithm used for signing
        signed_at: When the manifest was signed
        signed_by: Who signed it
        metadata: Additional metadata
    """

    manifest_type: str
    name: str
    version: str
    content_hash: str
    signature: str
    algorithm: SignatureAlgorithm
    signed_at: datetime
    signed_by: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "manifest_type": self.manifest_type,
            "name": self.name,
            "version": self.version,
            "content_hash": self.content_hash,
            "signature": self.signature,
            "algorithm": self.algorithm.value,
            "signed_at": self.signed_at.isoformat(),
            "signed_by": self.signed_by,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SignedManifest:
        """Create from dictionary."""
        return cls(
            manifest_type=data["manifest_type"],
            name=data["name"],
            version=data["version"],
            content_hash=data["content_hash"],
            signature=data["signature"],
            algorithm=SignatureAlgorithm(data["algorithm"]),
            signed_at=datetime.fromisoformat(data["signed_at"]),
            signed_by=data["signed_by"],
            metadata=data.get("metadata", {}),
        )


class ManifestSigner:
    """
    Signs and verifies manifests using HMAC.

    Uses a secret key stored securely to sign manifests.
    Verification ensures manifests haven't been tampered with.
    """

    def __init__(
        self,
        key_path: Path | None = None,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
    ):
        """
        Initialize the signer.

        Args:
            key_path: Path to the signing key file.
                     If not exists, a new key will be generated.
            algorithm: Signature algorithm to use.
        """
        if key_path:
            self._key_path = key_path
        else:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._key_path = Path(appdata) / "VoiceStudio" / ".signing_key"

        self._key_path.parent.mkdir(parents=True, exist_ok=True)
        self._algorithm = algorithm
        self._key = self._load_or_generate_key()

    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate a new one."""
        if self._key_path.exists():
            return self._key_path.read_bytes()
        else:
            # Generate a new 256-bit key
            key = os.urandom(32)
            self._key_path.write_bytes(key)

            # Set restrictive permissions on Unix-like systems
            try:
                os.chmod(self._key_path, 0o600)
            except (AttributeError, OSError):
                pass  # Windows or permission error

            return key

    def _compute_content_hash(self, content: Any) -> str:
        """Compute SHA-256 hash of content."""
        if isinstance(content, dict):
            content_bytes = json.dumps(content, sort_keys=True).encode("utf-8")
        elif isinstance(content, str):
            content_bytes = content.encode("utf-8")
        elif isinstance(content, bytes):
            content_bytes = content
        else:
            content_bytes = str(content).encode("utf-8")

        return hashlib.sha256(content_bytes).hexdigest()

    def _compute_signature(
        self,
        manifest_type: str,
        name: str,
        version: str,
        content_hash: str,
    ) -> str:
        """Compute HMAC signature."""
        # Create message to sign
        message = f"{manifest_type}:{name}:{version}:{content_hash}".encode()

        # Choose hash function based on algorithm
        if self._algorithm == SignatureAlgorithm.HMAC_SHA512:
            hash_func = hashlib.sha512
        else:
            hash_func = hashlib.sha256

        # Compute HMAC
        signature = hmac.new(self._key, message, hash_func).hexdigest()
        return signature

    def sign(
        self,
        manifest_type: str,
        name: str,
        version: str,
        content: Any,
        signed_by: str,
        metadata: dict[str, Any] | None = None,
    ) -> SignedManifest:
        """
        Sign a manifest.

        Args:
            manifest_type: Type of manifest
            name: Name of the manifest
            version: Semantic version
            content: Content to sign
            signed_by: Identity of the signer
            metadata: Additional metadata

        Returns:
            Signed manifest
        """
        content_hash = self._compute_content_hash(content)
        signature = self._compute_signature(manifest_type, name, version, content_hash)

        return SignedManifest(
            manifest_type=manifest_type,
            name=name,
            version=version,
            content_hash=content_hash,
            signature=signature,
            algorithm=self._algorithm,
            signed_at=datetime.now(),
            signed_by=signed_by,
            metadata=metadata or {},
        )

    def verify(
        self,
        signed_manifest: SignedManifest,
        content: Any | None = None,
    ) -> tuple[bool, str]:
        """
        Verify a signed manifest.

        Args:
            signed_manifest: The signed manifest to verify
            content: Optional content to verify hash against

        Returns:
            Tuple of (is_valid, reason)
        """
        # Verify algorithm matches
        if signed_manifest.algorithm != self._algorithm:
            return False, f"Algorithm mismatch: expected {self._algorithm.value}, got {signed_manifest.algorithm.value}"

        # Verify content hash if content provided
        if content is not None:
            computed_hash = self._compute_content_hash(content)
            if computed_hash != signed_manifest.content_hash:
                return False, "Content hash mismatch - content may have been modified"

        # Verify signature
        expected_signature = self._compute_signature(
            signed_manifest.manifest_type,
            signed_manifest.name,
            signed_manifest.version,
            signed_manifest.content_hash,
        )

        if not hmac.compare_digest(expected_signature, signed_manifest.signature):
            return False, "Signature verification failed - manifest may have been tampered with"

        return True, "Signature valid"

    def verify_content(self, signed_manifest: SignedManifest, content: Any) -> tuple[bool, str]:
        """Verify both signature and content."""
        return self.verify(signed_manifest, content)

    def rotate_key(self) -> None:
        """
        Rotate the signing key.

        WARNING: This will invalidate all existing signatures.
        """
        import shutil

        # Backup old key
        if self._key_path.exists():
            backup_path = self._key_path.with_suffix(".key.bak")
            shutil.copy2(self._key_path, backup_path)

        # Generate new key
        self._key = os.urandom(32)
        self._key_path.write_bytes(self._key)

        try:
            os.chmod(self._key_path, 0o600)
        # Best effort - failure is acceptable here
        except (AttributeError, OSError):
            pass

    def export_public_data(self) -> dict:
        """
        Export public data about the signer (not the key itself).

        Returns:
            Dictionary with signer metadata
        """
        # Compute a fingerprint of the key (for verification without exposing the key)
        fingerprint = hashlib.sha256(self._key).hexdigest()[:16]

        return {
            "algorithm": self._algorithm.value,
            "key_fingerprint": fingerprint,
            "key_path": str(self._key_path),
        }
