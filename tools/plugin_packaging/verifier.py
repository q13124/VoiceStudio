"""
VoiceStudio Plugin Verifier.

Phase 4 Enhancement: Verifies .vspkg package integrity and signatures.

Verification Levels:
1. STRUCTURE - Package has required files
2. CHECKSUMS - All file checksums match
3. SIGNATURE - Cryptographic signature is valid (if present)
4. TRUSTED - Signature is from a trusted signer
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .format import REQUIRED_FILES, VSPKGFormat, VSPKGManifest
from .signer import SignatureInfo

logger = logging.getLogger(__name__)


class VerificationLevel(Enum):
    """Verification level achieved."""
    NONE = "none"
    STRUCTURE = "structure"
    CHECKSUMS = "checksums"
    SIGNATURE = "signature"
    TRUSTED = "trusted"


class VerificationStatus(Enum):
    """Overall verification status."""
    VALID = "valid"
    INVALID = "invalid"
    UNSIGNED = "unsigned"
    UNTRUSTED = "untrusted"


@dataclass
class VerificationResult:
    """Result of package verification."""
    status: VerificationStatus
    level: VerificationLevel
    package_path: Path | None = None
    manifest: VSPKGManifest | None = None
    signature_info: SignatureInfo | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if package passed basic validation."""
        return self.status in (
            VerificationStatus.VALID,
            VerificationStatus.UNSIGNED,
            VerificationStatus.UNTRUSTED,
        )
    
    @property
    def is_signed(self) -> bool:
        """Check if package has a valid signature."""
        return self.level in (
            VerificationLevel.SIGNATURE,
            VerificationLevel.TRUSTED,
        )
    
    @property
    def is_trusted(self) -> bool:
        """Check if signature is from a trusted signer."""
        return self.level == VerificationLevel.TRUSTED


class PluginVerifier:
    """
    Verifies .vspkg package integrity and signatures.
    
    Verification Process:
    1. Check package structure (required files present)
    2. Verify all file checksums match CHECKSUMS.sha256
    3. If signed, verify cryptographic signature
    4. If trusted signers configured, check if signature is trusted
    """
    
    def __init__(self, trusted_signers: list[str] | None = None):
        """
        Initialize verifier.
        
        Args:
            trusted_signers: List of trusted signer IDs
        """
        self._trusted_signers: set[str] = set(trusted_signers or [])
        self._trusted_public_keys: dict[str, bytes] = {}
    
    def add_trusted_signer(self, signer_id: str, public_key: bytes | None = None) -> None:
        """
        Add a trusted signer.
        
        Args:
            signer_id: Signer identifier
            public_key: Optional known public key
        """
        self._trusted_signers.add(signer_id)
        if public_key:
            self._trusted_public_keys[signer_id] = public_key
    
    def load_trusted_keys(self, keys_path: Path) -> int:
        """
        Load trusted public keys from a directory.
        
        Expects files named {signer_id}.pub containing raw public key bytes.
        
        Args:
            keys_path: Directory containing public key files
            
        Returns:
            Number of keys loaded
        """
        count = 0
        if keys_path.exists():
            for key_file in keys_path.glob("*.pub"):
                signer_id = key_file.stem
                try:
                    public_key = key_file.read_bytes()
                    self.add_trusted_signer(signer_id, public_key)
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to load key {key_file}: {e}")
        return count
    
    def verify(self, package_path: Path) -> VerificationResult:
        """
        Verify a .vspkg package.
        
        Args:
            package_path: Path to the package file
            
        Returns:
            Verification result with status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        
        if not package_path.exists():
            return VerificationResult(
                status=VerificationStatus.INVALID,
                level=VerificationLevel.NONE,
                errors=["Package file not found"],
            )
        
        # Level 1: Structure verification
        if not VSPKGFormat.is_valid_package(package_path):
            return VerificationResult(
                status=VerificationStatus.INVALID,
                level=VerificationLevel.NONE,
                package_path=package_path,
                errors=["Invalid package structure"],
            )
        
        # Read manifest
        manifest = VSPKGFormat.read_manifest(package_path)
        if not manifest:
            return VerificationResult(
                status=VerificationStatus.INVALID,
                level=VerificationLevel.NONE,
                package_path=package_path,
                errors=["Cannot read package manifest"],
            )
        
        # Level 2: Checksum verification
        checksum_result = self._verify_checksums(package_path)
        if checksum_result["errors"]:
            return VerificationResult(
                status=VerificationStatus.INVALID,
                level=VerificationLevel.STRUCTURE,
                package_path=package_path,
                manifest=manifest,
                errors=checksum_result["errors"],
                warnings=checksum_result["warnings"],
            )
        
        warnings.extend(checksum_result["warnings"])
        
        # Level 3: Signature verification
        signature_result = self._verify_signature(package_path)
        
        if not signature_result["has_signature"]:
            return VerificationResult(
                status=VerificationStatus.UNSIGNED,
                level=VerificationLevel.CHECKSUMS,
                package_path=package_path,
                manifest=manifest,
                warnings=warnings + ["Package is not signed"],
            )
        
        if signature_result["errors"]:
            return VerificationResult(
                status=VerificationStatus.INVALID,
                level=VerificationLevel.CHECKSUMS,
                package_path=package_path,
                manifest=manifest,
                signature_info=signature_result.get("signature_info"),
                errors=signature_result["errors"],
                warnings=warnings,
            )
        
        sig_info = signature_result["signature_info"]
        warnings.extend(signature_result["warnings"])
        
        # Level 4: Trust verification
        if sig_info and sig_info.signer_id in self._trusted_signers:
            # Check if we have a known public key
            if sig_info.signer_id in self._trusted_public_keys:
                known_key = self._trusted_public_keys[sig_info.signer_id]
                sig_key = base64.b64decode(sig_info.public_key)
                if known_key != sig_key:
                    return VerificationResult(
                        status=VerificationStatus.INVALID,
                        level=VerificationLevel.SIGNATURE,
                        package_path=package_path,
                        manifest=manifest,
                        signature_info=sig_info,
                        errors=["Public key mismatch for trusted signer"],
                        warnings=warnings,
                    )
            
            return VerificationResult(
                status=VerificationStatus.VALID,
                level=VerificationLevel.TRUSTED,
                package_path=package_path,
                manifest=manifest,
                signature_info=sig_info,
                warnings=warnings,
            )
        
        return VerificationResult(
            status=VerificationStatus.UNTRUSTED,
            level=VerificationLevel.SIGNATURE,
            package_path=package_path,
            manifest=manifest,
            signature_info=sig_info,
            warnings=warnings + [f"Signer '{sig_info.signer_id}' is not in trusted list"],
        )
    
    def _verify_checksums(self, package_path: Path) -> dict[str, Any]:
        """Verify all file checksums."""
        errors: list[str] = []
        warnings: list[str] = []
        
        try:
            stored_checksums = VSPKGFormat.read_checksums(package_path)
            if not stored_checksums:
                errors.append("No checksums found in package")
                return {"errors": errors, "warnings": warnings}
            
            with zipfile.ZipFile(package_path, "r") as zf:
                for name in zf.namelist():
                    # Skip metadata files
                    if name in ("MANIFEST.json", "CHECKSUMS.sha256", "SIGNATURE.json"):
                        continue
                    
                    # Skip directories
                    if name.endswith("/"):
                        continue
                    
                    if name not in stored_checksums:
                        warnings.append(f"File not in checksums: {name}")
                        continue
                    
                    # Calculate actual checksum
                    data = zf.read(name)
                    actual_hash = hashlib.sha256(data).hexdigest()
                    
                    if actual_hash != stored_checksums[name]:
                        errors.append(
                            f"Checksum mismatch: {name} "
                            f"(expected {stored_checksums[name][:16]}..., "
                            f"got {actual_hash[:16]}...)"
                        )
            
        except Exception as e:
            errors.append(f"Checksum verification failed: {e}")
        
        return {"errors": errors, "warnings": warnings}
    
    def _verify_signature(self, package_path: Path) -> dict[str, Any]:
        """Verify cryptographic signature."""
        result: dict[str, Any] = {
            "has_signature": False,
            "signature_info": None,
            "errors": [],
            "warnings": [],
        }
        
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                if "SIGNATURE.json" not in zf.namelist():
                    return result
                
                result["has_signature"] = True
                
                # Read signature
                sig_data = json.loads(zf.read("SIGNATURE.json").decode("utf-8"))
                sig_info = SignatureInfo.from_dict(sig_data)
                result["signature_info"] = sig_info
                
                # Check algorithm
                if sig_info.algorithm != "ed25519":
                    result["errors"].append(
                        f"Unsupported signature algorithm: {sig_info.algorithm}"
                    )
                    return result
                
                # Read and hash checksums
                checksums_data = zf.read("CHECKSUMS.sha256")
                checksums_hash = hashlib.sha256(checksums_data).hexdigest()
                
                if checksums_hash != sig_info.checksums_hash:
                    result["errors"].append("Checksums file has been modified")
                    return result
                
                # Verify files hash (excluding SIGNATURE.json as it was added after signing)
                files = sorted(f for f in zf.namelist() if f != "SIGNATURE.json")
                files_hash = hashlib.sha256(
                    "\n".join(files).encode("utf-8")
                ).hexdigest()
                
                if files_hash != sig_info.files_hash:
                    result["errors"].append("Package files have been modified")
                    return result
                
                # Verify cryptographic signature
                try:
                    from cryptography.exceptions import InvalidSignature
                    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                        Ed25519PublicKey,
                    )
                    
                    public_key_bytes = base64.b64decode(sig_info.public_key)
                    signature_bytes = base64.b64decode(sig_info.signature)
                    
                    public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
                    message = f"{checksums_hash}:{files_hash}".encode()
                    
                    public_key.verify(signature_bytes, message)
                    
                except InvalidSignature:
                    result["errors"].append("Invalid cryptographic signature")
                except ImportError:
                    result["warnings"].append(
                        "cryptography library not available - signature not cryptographically verified"
                    )
                except Exception as e:
                    result["errors"].append(f"Signature verification failed: {e}")
                    
        except Exception as e:
            result["errors"].append(f"Signature check failed: {e}")
        
        return result
    
    def verify_quick(self, package_path: Path) -> bool:
        """
        Quick verification - structure and checksums only.
        
        Args:
            package_path: Path to package
            
        Returns:
            True if basic verification passes
        """
        result = self.verify(package_path)
        return result.is_valid


def verify_package(
    package_path: str | Path,
    trusted_signers: list[str] | None = None,
) -> VerificationResult:
    """
    Convenience function to verify a package.
    
    Args:
        package_path: Path to the package
        trusted_signers: Optional list of trusted signer IDs
        
    Returns:
        Verification result
    """
    verifier = PluginVerifier(trusted_signers=trusted_signers)
    return verifier.verify(Path(package_path))
