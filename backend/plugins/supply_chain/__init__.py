"""
Supply Chain Security for VoiceStudio Plugins.

Phase 5B Enhancement: Provides supply chain security features including:
    - SBOM (Software Bill of Materials) generation
    - Vulnerability scanning
    - Build provenance
    - Signature verification
    - License compliance

Phase 5C M3 Enhancement: Adds plugin certification engine:
    - Automated quality gates (manifest, SBOM, licenses, vulnerabilities, signature, provenance)
    - Certification levels (none, basic, standard, premium, enterprise)
    - Certificate generation with unique IDs
    - Certification policy configuration

This module helps ensure plugin integrity and security through:
    - CycloneDX SBOM generation for dependency tracking
    - Dependency vulnerability scanning via pip-audit/grype
    - Build provenance metadata for .vspkg packages
    - Key rotation and local keystore management
    - SPDX license validation
    - Automated certification workflow
"""

from .audit import (
    AuditCategory,
    AuditEvent,
    AuditEventType,
    AuditLogger,
    AuditQuery,
    AuditSeverity,
    AuditSummary,
    get_default_audit_logger,
    log_crash,
    log_installation,
    log_plugin_event,
    log_signature_verification,
    log_uninstallation,
    log_vulnerability_scan,
)
from .certification import (
    CertificationEngine,
    CertificationLevel,
    CertificationMetrics,
    CertificationPolicy,
    CertificationRequirement,
    CertificationResult,
    GateStatus,
    QualityGate,
    certify_plugin,
    get_certification_engine,
)
from .license_checker import (
    CompatibilityIssue,
    CompatibilityLevel,
    DependencyLicense,
    LicenseCategory,
    LicenseChecker,
    LicenseCheckResult,
    LicenseInfo,
    check_license_compatibility,
    get_allowed_licenses,
    list_known_licenses,
    validate_spdx_license,
)
from .packager import (
    PackageConfig,
    PackageFormat,
    PackageManifest,
    PackagePhase,
    PackageProgress,
    PackageResult,
    PluginPackager,
    extract_package_manifest,
    extract_package_sbom,
    pack_plugin,
)
from .provenance import (
    BuilderInfo,
    BuildType,
    InputArtifact,
    Provenance,
    ProvenanceGenerator,
    ProvenanceVersion,
    SourceInfo,
    generate_provenance,
    load_provenance,
    verify_provenance_digest,
)
from .sbom import (
    SBOM,
    Component,
    ComponentType,
    License,
    SBOMFormat,
    SBOMGenerator,
    generate_sbom,
    load_sbom,
)
from .signer import (
    KeyEntry,
    KeyMetadata,
    KeyStatus,
    Keystore,
    PackageSigner,
    Signature,
    SignatureAlgorithm,
    check_signing_available,
    create_keystore,
    load_keystore,
    sign_package,
    verify_package,
)
from .vuln_scanner import (
    ScannerType,
    ScanResult,
    Severity,
    Vulnerability,
    VulnerabilityScanner,
    check_scanner_availability,
    scan_plugin,
    scan_sbom,
)

__all__ = [
    # SBOM
    "SBOM",
    "AuditCategory",
    "AuditEvent",
    "AuditEventType",
    # Audit
    "AuditLogger",
    "AuditQuery",
    "AuditSeverity",
    "AuditSummary",
    "BuildType",
    "BuilderInfo",
    # Certification (Phase 5C M3)
    "CertificationEngine",
    "CertificationLevel",
    "CertificationMetrics",
    "CertificationPolicy",
    "CertificationRequirement",
    "CertificationResult",
    "CompatibilityIssue",
    "CompatibilityLevel",
    "Component",
    "ComponentType",
    "DependencyLicense",
    "GateStatus",
    "InputArtifact",
    "KeyEntry",
    "KeyMetadata",
    "KeyStatus",
    # Signer
    "Keystore",
    "License",
    "LicenseCategory",
    "LicenseCheckResult",
    # License Checker
    "LicenseChecker",
    "LicenseInfo",
    "PackageConfig",
    "PackageFormat",
    "PackageManifest",
    "PackagePhase",
    "PackageProgress",
    "PackageResult",
    "PackageSigner",
    # Packager
    "PluginPackager",
    # Provenance
    "Provenance",
    "ProvenanceGenerator",
    "ProvenanceVersion",
    "QualityGate",
    "SBOMFormat",
    "SBOMGenerator",
    "ScanResult",
    "ScannerType",
    "Severity",
    "Signature",
    "SignatureAlgorithm",
    "SourceInfo",
    "Vulnerability",
    # Vulnerability Scanner
    "VulnerabilityScanner",
    "certify_plugin",
    "check_license_compatibility",
    "check_scanner_availability",
    "check_signing_available",
    "create_keystore",
    "extract_package_manifest",
    "extract_package_sbom",
    "generate_provenance",
    "generate_sbom",
    "get_allowed_licenses",
    "get_certification_engine",
    "get_default_audit_logger",
    "list_known_licenses",
    "load_keystore",
    "load_provenance",
    "load_sbom",
    "log_crash",
    "log_installation",
    "log_plugin_event",
    "log_signature_verification",
    "log_uninstallation",
    "log_vulnerability_scan",
    "pack_plugin",
    "scan_plugin",
    "scan_sbom",
    "sign_package",
    "validate_spdx_license",
    "verify_package",
    "verify_provenance_digest",
]
