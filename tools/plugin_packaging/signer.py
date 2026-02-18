"""
VoiceStudio Plugin Signer.

Phase 4 Enhancement: Signs .vspkg packages with cryptographic signatures.

Note: This implementation uses Ed25519 for signing, which is:
- Faster than RSA
- More secure than ECDSA with same key size
- Deterministic (no random nonce needed)
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Signature schema version
SIGNATURE_VERSION = "1.0.0"


@dataclass
class SignatureInfo:
    """Signature metadata."""
    version: str
    algorithm: str
    signed_at: str
    signer_id: str
    public_key: str
    signature: str
    checksums_hash: str
    files_hash: str
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SignatureInfo:
        """Create from dictionary."""
        return cls(
            version=data.get("version", SIGNATURE_VERSION),
            algorithm=data.get("algorithm", "ed25519"),
            signed_at=data.get("signed_at", ""),
            signer_id=data.get("signer_id", ""),
            public_key=data.get("public_key", ""),
            signature=data.get("signature", ""),
            checksums_hash=data.get("checksums_hash", ""),
            files_hash=data.get("files_hash", ""),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "algorithm": self.algorithm,
            "signed_at": self.signed_at,
            "signer_id": self.signer_id,
            "public_key": self.public_key,
            "signature": self.signature,
            "checksums_hash": self.checksums_hash,
            "files_hash": self.files_hash,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class SignResult:
    """Result of signing operation."""
    success: bool
    signature_info: SignatureInfo | None = None
    package_path: Path | None = None
    error: str | None = None


class PluginSigner:
    """
    Signs .vspkg packages with cryptographic signatures.
    
    Security Model:
    - Uses Ed25519 for efficient, secure signing
    - Signs the CHECKSUMS.sha256 file hash (which contains all file hashes)
    - Also includes a hash of the file list for integrity
    - Stores signature in SIGNATURE.json inside the package
    
    Key Management:
    - Private key should be stored securely (not in repo)
    - Public key is embedded in the signature for verification
    - Signer ID helps identify the signing authority
    """
    
    def __init__(self, signer_id: str = "voicestudio-official"):
        """
        Initialize signer.
        
        Args:
            signer_id: Identifier for the signer
        """
        self._signer_id = signer_id
        self._private_key: bytes | None = None
        self._public_key: bytes | None = None
    
    def load_key_pair(
        self,
        private_key_path: Path | None = None,
        public_key_path: Path | None = None,
        private_key_bytes: bytes | None = None,
        public_key_bytes: bytes | None = None,
    ) -> bool:
        """
        Load signing key pair.
        
        Args:
            private_key_path: Path to private key file
            public_key_path: Path to public key file
            private_key_bytes: Raw private key bytes
            public_key_bytes: Raw public key bytes
            
        Returns:
            True if keys loaded successfully
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
                Ed25519PublicKey,
            )
            
            # Load private key
            if private_key_bytes:
                self._private_key = private_key_bytes
            elif private_key_path and private_key_path.exists():
                key_data = private_key_path.read_bytes()
                # Try to load as PEM
                try:
                    private_key = serialization.load_pem_private_key(key_data, password=None)
                    self._private_key = private_key.private_bytes(
                        encoding=serialization.Encoding.Raw,
                        format=serialization.PrivateFormat.Raw,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                except Exception as e:
                    # GAP-PY-001: Try as raw bytes fallback
                    logger.debug(f"Key parse failed, using raw bytes: {e}")
                    self._private_key = key_data
            
            # Load or derive public key
            if public_key_bytes:
                self._public_key = public_key_bytes
            elif public_key_path and public_key_path.exists():
                self._public_key = public_key_path.read_bytes()
            elif self._private_key:
                # Derive from private key
                private_key = Ed25519PrivateKey.from_private_bytes(self._private_key)
                self._public_key = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            
            return self._private_key is not None and self._public_key is not None
            
        except ImportError:
            logger.error("cryptography library required for signing")
            return False
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            return False
    
    def generate_key_pair(self) -> tuple[bytes, bytes] | None:
        """
        Generate a new Ed25519 key pair.
        
        Returns:
            Tuple of (private_key, public_key) bytes, or None on failure
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            
            private_key = Ed25519PrivateKey.generate()
            
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            
            public_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            
            self._private_key = private_bytes
            self._public_key = public_bytes
            
            return (private_bytes, public_bytes)
            
        except ImportError:
            logger.error("cryptography library required for key generation")
            return None
        except Exception as e:
            logger.error(f"Failed to generate keys: {e}")
            return None
    
    def sign_package(self, package_path: Path) -> SignResult:
        """
        Sign a .vspkg package.
        
        Args:
            package_path: Path to the package file
            
        Returns:
            Sign result with status and details
        """
        if not self._private_key or not self._public_key:
            return SignResult(
                success=False,
                error="No signing keys loaded",
            )
        
        if not package_path.exists():
            return SignResult(
                success=False,
                error=f"Package not found: {package_path}",
            )
        
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            
            # Read package contents
            with zipfile.ZipFile(package_path, "r") as zf:
                # Get checksums file
                if "CHECKSUMS.sha256" not in zf.namelist():
                    return SignResult(
                        success=False,
                        error="Package missing CHECKSUMS.sha256",
                    )
                
                checksums_data = zf.read("CHECKSUMS.sha256")
                checksums_hash = hashlib.sha256(checksums_data).hexdigest()
                
                # Hash the file list
                files = sorted(zf.namelist())
                files_hash = hashlib.sha256(
                    "\n".join(files).encode("utf-8")
                ).hexdigest()
            
            # Create message to sign
            message = f"{checksums_hash}:{files_hash}".encode()
            
            # Sign the message
            private_key = Ed25519PrivateKey.from_private_bytes(self._private_key)
            signature = private_key.sign(message)
            
            # Create signature info
            sig_info = SignatureInfo(
                version=SIGNATURE_VERSION,
                algorithm="ed25519",
                signed_at=datetime.now().isoformat(),
                signer_id=self._signer_id,
                public_key=base64.b64encode(self._public_key).decode("ascii"),
                signature=base64.b64encode(signature).decode("ascii"),
                checksums_hash=checksums_hash,
                files_hash=files_hash,
            )
            
            # Add signature to package
            # Create a new package with the signature
            temp_path = package_path.with_suffix(".tmp")
            
            with zipfile.ZipFile(package_path, "r") as zf_read:
                with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf_write:
                    # Copy existing files (except old signature)
                    for item in zf_read.infolist():
                        if item.filename == "SIGNATURE.json":
                            continue
                        data = zf_read.read(item.filename)
                        zf_write.writestr(item, data)
                    
                    # Add new signature
                    zf_write.writestr("SIGNATURE.json", sig_info.to_json())
            
            # Replace original with signed version
            temp_path.replace(package_path)
            
            logger.info(f"Signed package: {package_path}")
            
            return SignResult(
                success=True,
                signature_info=sig_info,
                package_path=package_path,
            )
            
        except ImportError:
            return SignResult(
                success=False,
                error="cryptography library required for signing",
            )
        except Exception as e:
            logger.error(f"Failed to sign package: {e}")
            return SignResult(
                success=False,
                error=str(e),
            )
    
    def save_keys(
        self,
        private_key_path: Path,
        public_key_path: Path,
        format: str = "raw",
    ) -> bool:
        """
        Save key pair to files.
        
        Args:
            private_key_path: Path for private key
            public_key_path: Path for public key
            format: Key format ('raw' or 'pem')
            
        Returns:
            True if saved successfully
        """
        if not self._private_key or not self._public_key:
            return False
        
        try:
            if format == "raw":
                private_key_path.write_bytes(self._private_key)
                public_key_path.write_bytes(self._public_key)
            elif format == "pem":
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                    Ed25519PrivateKey,
                )
                
                private_key = Ed25519PrivateKey.from_private_bytes(self._private_key)
                
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                public_pem = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
                
                private_key_path.write_bytes(private_pem)
                public_key_path.write_bytes(public_pem)
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save keys: {e}")
            return False
