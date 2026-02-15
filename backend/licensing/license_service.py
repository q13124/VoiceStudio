"""
Phase 7: Licensing System
Task 7.3: License management for enterprise deployment.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """License types."""
    FREE = "free"
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"


class LicenseStatus(Enum):
    """License status."""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    REVOKED = "revoked"
    TRIAL = "trial"


@dataclass
class LicenseFeatures:
    """Features enabled by a license."""
    max_projects: int = -1  # -1 = unlimited
    max_voices: int = 3
    max_synthesis_minutes: int = 60
    batch_processing: bool = False
    cloud_sync: bool = False
    priority_support: bool = False
    api_access: bool = False
    commercial_use: bool = False
    offline_mode: bool = True
    advanced_effects: bool = False
    team_collaboration: bool = False
    custom_models: bool = False


@dataclass
class License:
    """License information."""
    license_key: str
    license_type: LicenseType
    status: LicenseStatus
    issued_to: str
    issued_at: datetime
    expires_at: datetime | None
    features: LicenseFeatures
    machine_id: str | None = None
    seats: int = 1
    activated_seats: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LicenseValidationResult:
    """Result of license validation."""
    valid: bool
    status: LicenseStatus
    message: str
    features: LicenseFeatures | None = None
    days_remaining: int | None = None


class LicenseService:
    """Service for managing licenses."""

    # Feature sets for each license type
    LICENSE_FEATURES = {
        LicenseType.FREE: LicenseFeatures(
            max_projects=3,
            max_voices=3,
            max_synthesis_minutes=60,
        ),
        LicenseType.PERSONAL: LicenseFeatures(
            max_projects=-1,
            max_voices=10,
            max_synthesis_minutes=-1,
            advanced_effects=True,
        ),
        LicenseType.PROFESSIONAL: LicenseFeatures(
            max_projects=-1,
            max_voices=-1,
            max_synthesis_minutes=-1,
            batch_processing=True,
            cloud_sync=True,
            api_access=True,
            commercial_use=True,
            advanced_effects=True,
            custom_models=True,
        ),
        LicenseType.ENTERPRISE: LicenseFeatures(
            max_projects=-1,
            max_voices=-1,
            max_synthesis_minutes=-1,
            batch_processing=True,
            cloud_sync=True,
            priority_support=True,
            api_access=True,
            commercial_use=True,
            advanced_effects=True,
            team_collaboration=True,
            custom_models=True,
        ),
        LicenseType.TRIAL: LicenseFeatures(
            max_projects=5,
            max_voices=5,
            max_synthesis_minutes=120,
            batch_processing=True,
            advanced_effects=True,
        ),
    }

    def __init__(
        self,
        license_path: Path | None = None,
        validation_url: str | None = None
    ):
        self._license_path = license_path or Path.home() / ".voicestudio/license.json"
        self._validation_url = validation_url
        self._current_license: License | None = None
        self._machine_id = self._generate_machine_id()

    @property
    def current_license(self) -> License | None:
        """Get current license."""
        return self._current_license

    @property
    def features(self) -> LicenseFeatures:
        """Get current license features."""
        if self._current_license and self._current_license.status == LicenseStatus.VALID:
            return self._current_license.features

        return self.LICENSE_FEATURES[LicenseType.FREE]

    async def load_license(self) -> License | None:
        """Load license from disk."""
        try:
            if not self._license_path.exists():
                return None

            data = json.loads(self._license_path.read_text())

            license = License(
                license_key=data["license_key"],
                license_type=LicenseType(data["license_type"]),
                status=LicenseStatus(data["status"]),
                issued_to=data["issued_to"],
                issued_at=datetime.fromisoformat(data["issued_at"]),
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                features=LicenseFeatures(**data.get("features", {})),
                machine_id=data.get("machine_id"),
                seats=data.get("seats", 1),
            )

            # Validate loaded license
            result = await self.validate_license(license.license_key)

            if result.valid:
                self._current_license = license
                return license

            return None

        except Exception as e:
            logger.error(f"Failed to load license: {e}")
            return None

    async def activate_license(
        self,
        license_key: str,
        user_email: str | None = None
    ) -> LicenseValidationResult:
        """Activate a license key."""
        try:
            # Validate the license key format
            if not self._validate_key_format(license_key):
                return LicenseValidationResult(
                    valid=False,
                    status=LicenseStatus.INVALID,
                    message="Invalid license key format"
                )

            # Parse license key
            license_info = self._parse_license_key(license_key)

            if not license_info:
                return LicenseValidationResult(
                    valid=False,
                    status=LicenseStatus.INVALID,
                    message="Unable to parse license key"
                )

            # Check online validation if URL provided
            if self._validation_url:
                online_result = await self._validate_online(license_key)
                if not online_result.valid:
                    return online_result

            # Create license object
            license_type = LicenseType(license_info.get("type", "personal"))

            license = License(
                license_key=license_key,
                license_type=license_type,
                status=LicenseStatus.VALID,
                issued_to=user_email or license_info.get("email", ""),
                issued_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=365),
                features=self.LICENSE_FEATURES[license_type],
                machine_id=self._machine_id,
            )

            # Save license
            await self._save_license(license)
            self._current_license = license

            return LicenseValidationResult(
                valid=True,
                status=LicenseStatus.VALID,
                message="License activated successfully",
                features=license.features,
                days_remaining=365,
            )

        except Exception as e:
            logger.error(f"License activation failed: {e}")
            return LicenseValidationResult(
                valid=False,
                status=LicenseStatus.INVALID,
                message=str(e)
            )

    async def validate_license(
        self,
        license_key: str | None = None
    ) -> LicenseValidationResult:
        """Validate a license key."""
        key = license_key or (self._current_license.license_key if self._current_license else None)

        if not key:
            return LicenseValidationResult(
                valid=False,
                status=LicenseStatus.INVALID,
                message="No license key provided"
            )

        try:
            # Check format
            if not self._validate_key_format(key):
                return LicenseValidationResult(
                    valid=False,
                    status=LicenseStatus.INVALID,
                    message="Invalid license key format"
                )

            # Check expiration
            if self._current_license and self._current_license.expires_at:
                if datetime.now() > self._current_license.expires_at:
                    return LicenseValidationResult(
                        valid=False,
                        status=LicenseStatus.EXPIRED,
                        message="License has expired"
                    )

                days_remaining = (self._current_license.expires_at - datetime.now()).days
            else:
                days_remaining = None

            # Online validation
            if self._validation_url:
                return await self._validate_online(key)

            return LicenseValidationResult(
                valid=True,
                status=LicenseStatus.VALID,
                message="License is valid",
                features=self.features,
                days_remaining=days_remaining,
            )

        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return LicenseValidationResult(
                valid=False,
                status=LicenseStatus.INVALID,
                message=str(e)
            )

    async def deactivate_license(self) -> bool:
        """Deactivate the current license."""
        try:
            if self._license_path.exists():
                self._license_path.unlink()

            self._current_license = None
            return True

        except Exception as e:
            logger.error(f"License deactivation failed: {e}")
            return False

    def check_feature(self, feature_name: str) -> bool:
        """Check if a feature is enabled by the current license."""
        features = self.features
        return getattr(features, feature_name, False)

    def _validate_key_format(self, key: str) -> bool:
        """Validate license key format."""
        # Expected format: XXXX-XXXX-XXXX-XXXX
        parts = key.split('-')
        if len(parts) != 4:
            return False

        return all(not (len(part) != 4 or not part.isalnum()) for part in parts)

    def _parse_license_key(self, key: str) -> dict[str, Any] | None:
        """Parse license key to extract information."""
        try:
            # Simple parsing - in production, use proper encryption
            parts = key.replace('-', '')

            # Extract type from first characters
            type_map = {
                'F': 'free',
                'P': 'personal',
                'R': 'professional',
                'E': 'enterprise',
                'T': 'trial',
            }

            license_type = type_map.get(parts[0], 'personal')

            return {
                "type": license_type,
                "checksum": parts[-4:],
            }

        except Exception:
            return None

    def _generate_machine_id(self) -> str:
        """Generate a unique machine identifier."""
        import platform
        import uuid

        components = [
            platform.node(),
            platform.machine(),
            str(uuid.getnode()),
        ]

        combined = '|'.join(components)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    async def _save_license(self, license: License) -> None:
        """Save license to disk."""
        self._license_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "license_key": license.license_key,
            "license_type": license.license_type.value,
            "status": license.status.value,
            "issued_to": license.issued_to,
            "issued_at": license.issued_at.isoformat(),
            "expires_at": license.expires_at.isoformat() if license.expires_at else None,
            "machine_id": license.machine_id,
            "seats": license.seats,
            "features": {
                "max_projects": license.features.max_projects,
                "max_voices": license.features.max_voices,
                "max_synthesis_minutes": license.features.max_synthesis_minutes,
                "batch_processing": license.features.batch_processing,
                "cloud_sync": license.features.cloud_sync,
                "priority_support": license.features.priority_support,
                "api_access": license.features.api_access,
                "commercial_use": license.features.commercial_use,
                "advanced_effects": license.features.advanced_effects,
                "team_collaboration": license.features.team_collaboration,
                "custom_models": license.features.custom_models,
            },
        }

        self._license_path.write_text(json.dumps(data, indent=2))

    async def _validate_online(self, license_key: str) -> LicenseValidationResult:
        """Validate license with online server."""
        # In production, this would make an HTTP request
        # For now, return valid
        return LicenseValidationResult(
            valid=True,
            status=LicenseStatus.VALID,
            message="License validated online",
            features=self.features,
        )
