"""
At-Rest Encryption Module.

Task 2.4.1: AES-256 encryption for sensitive data.
Provides encryption/decryption for files and data at rest.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants
SALT_SIZE = 32
NONCE_SIZE = 16
KEY_SIZE = 32  # 256 bits
TAG_SIZE = 16
ITERATIONS = 100000


@dataclass
class EncryptedData:
    """Encrypted data container."""
    ciphertext: bytes
    salt: bytes
    nonce: bytes
    tag: bytes

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        return (
            len(self.salt).to_bytes(1, "big") + self.salt +
            len(self.nonce).to_bytes(1, "big") + self.nonce +
            len(self.tag).to_bytes(1, "big") + self.tag +
            self.ciphertext
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> EncryptedData:
        """Deserialize from bytes."""
        pos = 0

        salt_len = data[pos]
        pos += 1
        salt = data[pos:pos + salt_len]
        pos += salt_len

        nonce_len = data[pos]
        pos += 1
        nonce = data[pos:pos + nonce_len]
        pos += nonce_len

        tag_len = data[pos]
        pos += 1
        tag = data[pos:pos + tag_len]
        pos += tag_len

        ciphertext = data[pos:]

        return cls(
            ciphertext=ciphertext,
            salt=salt,
            nonce=nonce,
            tag=tag,
        )


class EncryptionService:
    """
    At-rest encryption service using AES-256-GCM.

    Features:
    - AES-256-GCM encryption
    - PBKDF2 key derivation
    - Authenticated encryption
    - File encryption support
    """

    def __init__(self, master_key: bytes | None = None):
        """
        Initialize encryption service.

        Args:
            master_key: Optional master key (32 bytes).
                       If not provided, uses environment variable.
        """
        self._master_key = master_key or self._get_master_key()

    def _get_master_key(self) -> bytes:
        """Get master key from environment or generate one."""
        key_env = os.environ.get("VOICESTUDIO_ENCRYPTION_KEY")

        if key_env:
            return base64.b64decode(key_env)

        # Generate and warn
        logger.warning(
            "No encryption key found. Generating temporary key. "
            "Set VOICESTUDIO_ENCRYPTION_KEY for persistence."
        )
        return secrets.token_bytes(KEY_SIZE)

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master key and salt."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            self._master_key,
            salt,
            ITERATIONS,
            dklen=KEY_SIZE,
        )

    def encrypt(self, plaintext: bytes | str) -> EncryptedData:
        """
        Encrypt data.

        Args:
            plaintext: Data to encrypt

        Returns:
            EncryptedData containing ciphertext and metadata
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")

        # Generate salt and nonce
        salt = secrets.token_bytes(SALT_SIZE)
        nonce = secrets.token_bytes(NONCE_SIZE)

        # Derive key
        key = self._derive_key(salt)

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)

            # Split ciphertext and tag (GCM appends tag)
            return EncryptedData(
                ciphertext=ciphertext[:-TAG_SIZE],
                salt=salt,
                nonce=nonce,
                tag=ciphertext[-TAG_SIZE:],
            )

        except ImportError:
            # Fallback: Use simple XOR with HMAC (less secure but works)
            logger.warning("cryptography not available, using fallback encryption")
            return self._fallback_encrypt(plaintext, salt, nonce, key)

    def decrypt(self, encrypted: EncryptedData) -> bytes:
        """
        Decrypt data.

        Args:
            encrypted: EncryptedData to decrypt

        Returns:
            Decrypted plaintext bytes
        """
        key = self._derive_key(encrypted.salt)

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            aesgcm = AESGCM(key)
            # Reconstruct ciphertext with tag
            full_ciphertext = encrypted.ciphertext + encrypted.tag
            return aesgcm.decrypt(encrypted.nonce, full_ciphertext, None)

        except ImportError:
            return self._fallback_decrypt(encrypted, key)

    def _fallback_encrypt(
        self,
        plaintext: bytes,
        salt: bytes,
        nonce: bytes,
        key: bytes,
    ) -> EncryptedData:
        """Fallback encryption using XOR and HMAC."""
        # Generate keystream
        keystream = self._generate_keystream(key, nonce, len(plaintext))

        # XOR encryption
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, keystream, strict=False))

        # Generate authentication tag
        tag = hmac.new(key, ciphertext, hashlib.sha256).digest()[:TAG_SIZE]

        return EncryptedData(
            ciphertext=ciphertext,
            salt=salt,
            nonce=nonce,
            tag=tag,
        )

    def _fallback_decrypt(self, encrypted: EncryptedData, key: bytes) -> bytes:
        """Fallback decryption."""
        # Verify tag
        expected_tag = hmac.new(
            key, encrypted.ciphertext, hashlib.sha256
        ).digest()[:TAG_SIZE]

        if not hmac.compare_digest(expected_tag, encrypted.tag):
            raise ValueError("Authentication failed")

        # Generate keystream
        keystream = self._generate_keystream(
            key, encrypted.nonce, len(encrypted.ciphertext)
        )

        # XOR decryption
        return bytes(a ^ b for a, b in zip(encrypted.ciphertext, keystream, strict=False))

    def _generate_keystream(
        self,
        key: bytes,
        nonce: bytes,
        length: int,
    ) -> bytes:
        """Generate keystream for fallback encryption."""
        keystream = b""
        counter = 0

        while len(keystream) < length:
            block = hashlib.sha256(
                key + nonce + counter.to_bytes(4, "big")
            ).digest()
            keystream += block
            counter += 1

        return keystream[:length]

    def encrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Encrypt a file.

        Args:
            input_path: Path to file to encrypt
            output_path: Path to write encrypted file
        """
        plaintext = input_path.read_bytes()
        encrypted = self.encrypt(plaintext)
        output_path.write_bytes(encrypted.to_bytes())
        logger.info(f"Encrypted file: {input_path} -> {output_path}")

    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Decrypt a file.

        Args:
            input_path: Path to encrypted file
            output_path: Path to write decrypted file
        """
        encrypted_bytes = input_path.read_bytes()
        encrypted = EncryptedData.from_bytes(encrypted_bytes)
        plaintext = self.decrypt(encrypted)
        output_path.write_bytes(plaintext)
        logger.info(f"Decrypted file: {input_path} -> {output_path}")

    def encrypt_string(self, text: str) -> str:
        """
        Encrypt a string and return base64-encoded result.

        Args:
            text: Text to encrypt

        Returns:
            Base64-encoded encrypted data
        """
        encrypted = self.encrypt(text)
        return base64.b64encode(encrypted.to_bytes()).decode("ascii")

    def decrypt_string(self, encoded: str) -> str:
        """
        Decrypt a base64-encoded string.

        Args:
            encoded: Base64-encoded encrypted data

        Returns:
            Decrypted text
        """
        encrypted_bytes = base64.b64decode(encoded)
        encrypted = EncryptedData.from_bytes(encrypted_bytes)
        return self.decrypt(encrypted).decode("utf-8")


# Global instance
_encryption: EncryptionService | None = None


def get_encryption_service() -> EncryptionService:
    """Get or create the global encryption service."""
    global _encryption
    if _encryption is None:
        _encryption = EncryptionService()
    return _encryption
