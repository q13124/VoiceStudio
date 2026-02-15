"""
Secure Secrets Management.

Task 2.4.3: Secure credential storage and retrieval.
Environment-aware secrets vault with encryption at rest.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SecretEntry:
    """A secret entry."""
    key: str
    value: str
    created_at: datetime
    updated_at: datetime
    description: str = ""
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class SecretsVault:
    """
    Secure secrets management vault.

    Priority order for secret lookup:
    1. Environment variables
    2. Encrypted vault file
    3. Default values (if provided)

    Features:
    - Encrypted storage at rest
    - Environment variable integration
    - Secret rotation support
    - Audit logging
    """

    def __init__(
        self,
        vault_path: Path | None = None,
        encryption_service: Any | None = None,
    ):
        """
        Initialize secrets vault.

        Args:
            vault_path: Path to encrypted vault file
            encryption_service: Encryption service for vault file
        """
        self._vault_path = vault_path or Path("config/.secrets.vault")
        self._encryption = encryption_service
        self._cache: dict[str, SecretEntry] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Load vault if not already loaded."""
        if not self._loaded:
            self._load_vault()
            self._loaded = True

    def _load_vault(self) -> None:
        """Load secrets from encrypted vault."""
        if not self._vault_path.exists():
            logger.debug("Vault file does not exist, starting empty")
            return

        try:
            encrypted_data = self._vault_path.read_bytes()

            if self._encryption:
                from .encryption import EncryptedData
                encrypted = EncryptedData.from_bytes(encrypted_data)
                decrypted = self._encryption.decrypt(encrypted)
                data = json.loads(decrypted.decode("utf-8"))
            else:
                # Fallback: assume plain JSON (development only)
                logger.warning("Vault loaded without encryption (dev mode)")
                data = json.loads(encrypted_data.decode("utf-8"))

            for key, entry_data in data.items():
                self._cache[key] = SecretEntry(
                    key=key,
                    value=entry_data["value"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    updated_at=datetime.fromisoformat(entry_data["updated_at"]),
                    description=entry_data.get("description", ""),
                    tags=entry_data.get("tags", []),
                )

            logger.info(f"Loaded {len(self._cache)} secrets from vault")

        except Exception as e:
            logger.error(f"Failed to load vault: {e}")

    def _save_vault(self) -> None:
        """Save secrets to encrypted vault."""
        data = {}

        for key, entry in self._cache.items():
            data[key] = {
                "value": entry.value,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "description": entry.description,
                "tags": entry.tags,
            }

        try:
            json_data = json.dumps(data, indent=2).encode("utf-8")

            if self._encryption:
                encrypted = self._encryption.encrypt(json_data)
                self._vault_path.parent.mkdir(parents=True, exist_ok=True)
                self._vault_path.write_bytes(encrypted.to_bytes())
            else:
                # Fallback: plain JSON (development only)
                logger.warning("Vault saved without encryption (dev mode)")
                self._vault_path.parent.mkdir(parents=True, exist_ok=True)
                self._vault_path.write_bytes(json_data)

            logger.debug("Vault saved successfully")

        except Exception as e:
            logger.error(f"Failed to save vault: {e}")
            raise

    def get(
        self,
        key: str,
        default: str | None = None,
        required: bool = False,
    ) -> str | None:
        """
        Get a secret value.

        Priority:
        1. Environment variable (uppercase key)
        2. Vault entry
        3. Default value

        Args:
            key: Secret key
            default: Default value if not found
            required: Raise error if not found

        Returns:
            Secret value or default
        """
        # Check environment first
        env_key = key.upper().replace(".", "_").replace("-", "_")
        env_value = os.environ.get(env_key)

        if env_value:
            return env_value

        # Check vault
        self._ensure_loaded()

        if key in self._cache:
            return self._cache[key].value

        # Use default or raise
        if required and default is None:
            raise KeyError(f"Required secret not found: {key}")

        return default

    def set(
        self,
        key: str,
        value: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """
        Set a secret value.

        Args:
            key: Secret key
            value: Secret value
            description: Optional description
            tags: Optional tags for categorization
        """
        self._ensure_loaded()

        now = datetime.now()

        if key in self._cache:
            entry = self._cache[key]
            entry.value = value
            entry.updated_at = now
            if description:
                entry.description = description
            if tags:
                entry.tags = tags
        else:
            self._cache[key] = SecretEntry(
                key=key,
                value=value,
                created_at=now,
                updated_at=now,
                description=description,
                tags=tags or [],
            )

        self._save_vault()
        logger.info(f"Secret stored: {key}")

    def delete(self, key: str) -> bool:
        """
        Delete a secret.

        Args:
            key: Secret key

        Returns:
            True if deleted, False if not found
        """
        self._ensure_loaded()

        if key in self._cache:
            del self._cache[key]
            self._save_vault()
            logger.info(f"Secret deleted: {key}")
            return True

        return False

    def list_keys(self, tag: str | None = None) -> list[str]:
        """
        List all secret keys.

        Args:
            tag: Optional tag filter

        Returns:
            List of secret keys
        """
        self._ensure_loaded()

        if tag:
            return [k for k, v in self._cache.items() if tag in v.tags]

        return list(self._cache.keys())

    def rotate(self, key: str, new_value: str) -> str | None:
        """
        Rotate a secret value.

        Args:
            key: Secret key
            new_value: New secret value

        Returns:
            Old value for backup purposes
        """
        self._ensure_loaded()

        old_value = None

        if key in self._cache:
            old_value = self._cache[key].value
            self._cache[key].value = new_value
            self._cache[key].updated_at = datetime.now()
        else:
            self.set(key, new_value)

        self._save_vault()
        logger.info(f"Secret rotated: {key}")

        return old_value

    def get_metadata(self, key: str) -> dict | None:
        """
        Get secret metadata (without value).

        Args:
            key: Secret key

        Returns:
            Metadata dict or None
        """
        self._ensure_loaded()

        if key not in self._cache:
            return None

        entry = self._cache[key]
        return {
            "key": entry.key,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "description": entry.description,
            "tags": entry.tags,
        }


# Common secret keys
class SecretKeys:
    """Standard secret key names."""

    # Database
    DB_PASSWORD = "database.password"
    DB_CONNECTION_STRING = "database.connection_string"

    # API Keys
    ELEVENLABS_API_KEY = "api.elevenlabs"
    OPENAI_API_KEY = "api.openai"
    HF_TOKEN = "api.huggingface"

    # Encryption
    MASTER_KEY = "encryption.master_key"

    # Session
    SESSION_SECRET = "session.secret"
    JWT_SECRET = "jwt.secret"


# Global vault instance
_vault: SecretsVault | None = None


def get_secrets_vault() -> SecretsVault:
    """Get or create the global secrets vault."""
    global _vault
    if _vault is None:
        try:
            from .encryption import get_encryption_service
            encryption = get_encryption_service()
        except ImportError:
            encryption = None
        _vault = SecretsVault(encryption_service=encryption)
    return _vault


def get_secret(key: str, default: str | None = None) -> str | None:
    """Convenience function to get a secret."""
    return get_secrets_vault().get(key, default)
