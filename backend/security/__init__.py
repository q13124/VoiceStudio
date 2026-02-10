"""Security module for VoiceStudio backend."""

from backend.security.key_rotation import KeyRotationService, APIKey
from backend.security.rbac import RBACService, Role, Permission
from backend.security.session import SessionManager, Session
from backend.security.auth_audit import AuthAuditLogger, AuthEvent
from backend.security.file_scanner import FileScanner, ScanResult
from backend.security.path_validator import PathValidator, PathValidationError
from backend.security.tls import TLSConfig, enforce_tls
from backend.security.pii_detector import PIIDetector, PIIMatch
from backend.security.encryption import EncryptionService, EncryptedData
from backend.security.secrets_vault import SecretsVault, SecretKeys, get_secret

__all__ = [
    "KeyRotationService", "APIKey",
    "RBACService", "Role", "Permission",
    "SessionManager", "Session",
    "AuthAuditLogger", "AuthEvent",
    "FileScanner", "ScanResult",
    "PathValidator", "PathValidationError",
    "TLSConfig", "enforce_tls",
    "PIIDetector", "PIIMatch",
    "EncryptionService", "EncryptedData",
    "SecretsVault", "SecretKeys", "get_secret",
]
