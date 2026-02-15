"""Security module for VoiceStudio backend."""

from backend.security.auth_audit import AuthAuditLogger, AuthEvent
from backend.security.encryption import EncryptedData, EncryptionService
from backend.security.file_scanner import FileScanner, ScanResult
from backend.security.key_rotation import APIKey, KeyRotationService
from backend.security.path_validator import PathValidationError, PathValidator
from backend.security.pii_detector import PIIDetector, PIIMatch
from backend.security.rbac import Permission, RBACService, Role
from backend.security.secrets_vault import SecretKeys, SecretsVault, get_secret
from backend.security.session import Session, SessionManager
from backend.security.tls import TLSConfig, enforce_tls

__all__ = [
    "APIKey",
    "AuthAuditLogger",
    "AuthEvent",
    "EncryptedData",
    "EncryptionService",
    "FileScanner",
    "KeyRotationService",
    "PIIDetector",
    "PIIMatch",
    "PathValidationError",
    "PathValidator",
    "Permission",
    "RBACService",
    "Role",
    "ScanResult",
    "SecretKeys",
    "SecretsVault",
    "Session",
    "SessionManager",
    "TLSConfig",
    "enforce_tls",
    "get_secret",
]
