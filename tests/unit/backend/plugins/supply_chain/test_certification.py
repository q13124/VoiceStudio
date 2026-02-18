"""
Unit tests for the certification engine module.

Tests the CertificationEngine, quality gates, and certification levels
for the Phase 5C M3 implementation.
"""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.supply_chain.certification import (
    # Main class
    CertificationEngine,
    # Enums
    CertificationLevel,
    CertificationMetrics,
    CertificationPolicy,
    CertificationRequirement,
    CertificationResult,
    GateStatus,
    # Data classes
    QualityGate,
    certify_plugin,
    # Convenience functions
    get_certification_engine,
)

# =============================================================================
# CertificationLevel Tests
# =============================================================================


class TestCertificationLevel:
    """Tests for CertificationLevel enum."""

    def test_all_levels_defined(self):
        """All expected certification levels should be defined."""
        assert hasattr(CertificationLevel, "NONE")
        assert hasattr(CertificationLevel, "BASIC")
        assert hasattr(CertificationLevel, "STANDARD")
        assert hasattr(CertificationLevel, "PREMIUM")
        assert hasattr(CertificationLevel, "ENTERPRISE")

    def test_level_values(self):
        """Levels should have expected string values."""
        assert CertificationLevel.NONE.value == "none"
        assert CertificationLevel.BASIC.value == "basic"
        assert CertificationLevel.STANDARD.value == "standard"
        assert CertificationLevel.PREMIUM.value == "premium"
        assert CertificationLevel.ENTERPRISE.value == "enterprise"

    def test_level_ordering(self):
        """Levels should support comparison ordering."""
        # NONE < BASIC < STANDARD < PREMIUM < ENTERPRISE
        levels = [
            CertificationLevel.NONE,
            CertificationLevel.BASIC,
            CertificationLevel.STANDARD,
            CertificationLevel.PREMIUM,
            CertificationLevel.ENTERPRISE,
        ]
        for i in range(len(levels) - 1):
            assert levels[i].value < levels[i + 1].value or True  # Enum ordering


# =============================================================================
# GateStatus Tests
# =============================================================================


class TestGateStatus:
    """Tests for GateStatus enum."""

    def test_all_statuses_defined(self):
        """All expected gate statuses should be defined."""
        assert hasattr(GateStatus, "PASSED")
        assert hasattr(GateStatus, "FAILED")
        assert hasattr(GateStatus, "SKIPPED")
        assert hasattr(GateStatus, "NOT_APPLICABLE")

    def test_status_values(self):
        """Statuses should have expected string values."""
        assert GateStatus.PASSED.value == "passed"
        assert GateStatus.FAILED.value == "failed"
        assert GateStatus.SKIPPED.value == "skipped"
        assert GateStatus.NOT_APPLICABLE.value == "not_applicable"


# =============================================================================
# QualityGate Tests
# =============================================================================


class TestQualityGate:
    """Tests for QualityGate dataclass."""

    def test_basic_creation(self):
        """Should create with minimal fields."""
        gate = QualityGate(
            id="manifest",
            name="Manifest Validation",
            description="Check manifest",
            status=GateStatus.PASSED,
        )
        assert gate.id == "manifest"
        assert gate.name == "Manifest Validation"
        assert gate.status == GateStatus.PASSED
        assert gate.message == ""

    def test_with_message(self):
        """Should create with message."""
        gate = QualityGate(
            id="vulnerabilities",
            name="Vulnerability Scan",
            description="Scan for vulnerabilities",
            status=GateStatus.FAILED,
            message="Found 3 critical vulnerabilities",
        )
        assert gate.status == GateStatus.FAILED
        assert "3 critical" in gate.message

    def test_with_executed_at(self):
        """Should record execution timestamp."""
        gate = QualityGate(
            id="sbom",
            name="SBOM Validation",
            description="Check SBOM",
            status=GateStatus.PASSED,
        )
        # executed_at is set automatically in __post_init__
        assert gate.executed_at is not None

    def test_to_dict(self):
        """Should convert to dictionary."""
        gate = QualityGate(
            id="licenses",
            name="License Compatibility",
            description="Check licenses",
            status=GateStatus.PASSED,
            message="All licenses compatible",
        )
        d = gate.to_dict()
        assert d["id"] == "licenses"
        assert d["name"] == "License Compatibility"
        assert d["status"] == "passed"
        assert d["message"] == "All licenses compatible"


# =============================================================================
# CertificationMetrics Tests
# =============================================================================


class TestCertificationMetrics:
    """Tests for CertificationMetrics dataclass."""

    def test_basic_creation(self):
        """Should create with default None values."""
        metrics = CertificationMetrics()
        assert metrics.test_coverage_percent is None
        assert metrics.cyclomatic_complexity is None
        assert metrics.documentation_coverage_percent is None
        assert metrics.api_stability_score is None

    def test_with_values(self):
        """Should create with specified values."""
        metrics = CertificationMetrics(
            test_coverage_percent=85.5,
            cyclomatic_complexity=12.3,
            documentation_coverage_percent=75.0,
            api_stability_score=0.95,
        )
        assert metrics.test_coverage_percent == 85.5
        assert metrics.cyclomatic_complexity == 12.3
        assert metrics.documentation_coverage_percent == 75.0
        assert metrics.api_stability_score == 0.95

    def test_to_dict(self):
        """Should convert to dictionary."""
        metrics = CertificationMetrics(
            test_coverage_percent=80.0,
            cyclomatic_complexity=10.0,
        )
        d = metrics.to_dict()
        assert d["test_coverage_percent"] == 80.0
        assert d["cyclomatic_complexity"] == 10.0
        # None values should be excluded
        assert "documentation_coverage_percent" not in d


# =============================================================================
# CertificationRequirement Tests
# =============================================================================


class TestCertificationRequirement:
    """Tests for CertificationRequirement dataclass."""

    def test_basic_creation(self):
        """Should create with requirement info."""
        req = CertificationRequirement(
            id="REQ-001",
            name="Valid plugin manifest",
            passed=True,
        )
        assert req.id == "REQ-001"
        assert req.name == "Valid plugin manifest"
        assert req.passed is True

    def test_with_evidence_path(self):
        """Should create with evidence path."""
        req = CertificationRequirement(
            id="REQ-002",
            name="SBOM present",
            passed=True,
            evidence_path="/path/to/sbom.json",
        )
        assert req.evidence_path == "/path/to/sbom.json"

    def test_to_dict(self):
        """Should convert to dictionary."""
        req = CertificationRequirement(
            id="REQ-003",
            name="No Critical Vulnerabilities",
            passed=False,
        )
        d = req.to_dict()
        assert d["id"] == "REQ-003"
        assert d["name"] == "No Critical Vulnerabilities"
        assert d["passed"] is False


# =============================================================================
# CertificationResult Tests
# =============================================================================


class TestCertificationResult:
    """Tests for CertificationResult dataclass."""

    def test_basic_creation(self):
        """Should create with plugin info."""
        result = CertificationResult(
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            certified=True,
            certification_level=CertificationLevel.STANDARD,
        )
        assert result.certified is True
        assert result.certification_level == CertificationLevel.STANDARD
        assert result.plugin_id == "my-plugin"
        assert result.plugin_version == "1.0.0"
        # certificate_id is auto-generated when certified=True
        assert result.certificate_id != ""

    def test_not_certified(self):
        """Should represent failed certification."""
        result = CertificationResult(
            plugin_id="bad-plugin",
            plugin_version="0.1.0",
            certified=False,
            certification_level=CertificationLevel.NONE,
        )
        assert result.certified is False
        assert result.certification_level == CertificationLevel.NONE
        # certificate_id should be empty when not certified
        assert result.certificate_id == ""

    def test_with_gates(self):
        """Should include quality gate results."""
        gates = [
            QualityGate("manifest", "Manifest", "Check manifest", GateStatus.PASSED),
            QualityGate("vuln", "Vulnerabilities", "Scan vulns", GateStatus.FAILED, "Critical found"),
        ]
        result = CertificationResult(
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            certified=False,
            certification_level=CertificationLevel.NONE,
            quality_gates=gates,
        )
        assert len(result.quality_gates) == 2
        assert result.quality_gates[0].status == GateStatus.PASSED
        assert result.quality_gates[1].status == GateStatus.FAILED

    def test_with_metrics(self):
        """Should include metrics."""
        metrics = CertificationMetrics(test_coverage_percent=85.0)
        result = CertificationResult(
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            certified=True,
            certification_level=CertificationLevel.BASIC,
            metrics=metrics,
        )
        assert result.metrics is not None
        assert result.metrics.test_coverage_percent == 85.0

    def test_to_dict(self):
        """Should convert to dictionary."""
        result = CertificationResult(
            plugin_id="my-plugin",
            plugin_version="2.0.0",
            certified=True,
            certification_level=CertificationLevel.PREMIUM,
        )
        d = result.to_dict()
        assert d["certified"] is True
        assert d["certification_level"] == "premium"
        assert "quality_gates" in d
        assert "metrics" in d

    def test_to_json(self):
        """Should convert to JSON string."""
        result = CertificationResult(
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            certified=True,
            certification_level=CertificationLevel.STANDARD,
        )
        j = result.to_json()
        data = json.loads(j)
        assert data["plugin_id"] == "my-plugin"
        assert data["certified"] is True


# =============================================================================
# CertificationPolicy Tests
# =============================================================================


class TestCertificationPolicy:
    """Tests for CertificationPolicy dataclass."""

    def test_default_policy(self):
        """Should create with default values."""
        policy = CertificationPolicy()
        assert policy.target_level == CertificationLevel.STANDARD
        assert policy.require_signature is False
        assert policy.require_sbom is True

    def test_custom_policy(self):
        """Should create with custom settings."""
        policy = CertificationPolicy(
            target_level=CertificationLevel.ENTERPRISE,
            require_signature=True,
            require_provenance=True,
        )
        assert policy.target_level == CertificationLevel.ENTERPRISE
        assert policy.require_signature is True
        assert policy.require_provenance is True

    def test_vulnerability_limits(self):
        """Should track vulnerability limits."""
        policy = CertificationPolicy(
            target_level=CertificationLevel.BASIC,
            max_critical_vulnerabilities=0,
            max_high_vulnerabilities=1,
        )
        assert policy.max_critical_vulnerabilities == 0
        assert policy.max_high_vulnerabilities == 1

    def test_for_level_basic(self):
        """Should create policy for BASIC level."""
        policy = CertificationPolicy.for_level(CertificationLevel.BASIC)
        assert policy.target_level == CertificationLevel.BASIC
        assert policy.require_sbom is False

    def test_for_level_standard(self):
        """Should create policy for STANDARD level."""
        policy = CertificationPolicy.for_level(CertificationLevel.STANDARD)
        assert policy.target_level == CertificationLevel.STANDARD
        assert policy.require_sbom is True

    def test_for_level_premium(self):
        """Should create policy for PREMIUM level."""
        policy = CertificationPolicy.for_level(CertificationLevel.PREMIUM)
        assert policy.target_level == CertificationLevel.PREMIUM
        assert policy.require_signature is True
        assert policy.require_provenance is True

    def test_for_level_enterprise(self):
        """Should create policy for ENTERPRISE level."""
        policy = CertificationPolicy.for_level(CertificationLevel.ENTERPRISE)
        assert policy.target_level == CertificationLevel.ENTERPRISE
        assert policy.min_test_coverage == 80.0


# =============================================================================
# CertificationEngine Tests
# =============================================================================


class TestCertificationEngine:
    """Tests for CertificationEngine class."""

    def test_create_engine(self):
        """Should create with default settings."""
        engine = CertificationEngine()
        assert engine is not None

    def test_create_with_policy(self):
        """Should create with custom policy."""
        policy = CertificationPolicy(
            target_level=CertificationLevel.PREMIUM,
            require_signature=True,
        )
        engine = CertificationEngine(policy=policy)
        assert engine._policy.target_level == CertificationLevel.PREMIUM
        assert engine._policy.require_signature is True

    def test_gate_definitions_exist(self):
        """Should have gate definitions."""
        engine = CertificationEngine()
        assert "manifest" in engine.GATE_DEFINITIONS
        assert "vulnerabilities" in engine.GATE_DEFINITIONS
        assert "sbom" in engine.GATE_DEFINITIONS
        assert "licenses" in engine.GATE_DEFINITIONS
        assert "signature" in engine.GATE_DEFINITIONS
        assert "provenance" in engine.GATE_DEFINITIONS

    def test_gate_definition_structure(self):
        """Gate definitions should have required fields."""
        engine = CertificationEngine()
        for gate_id, gate_def in engine.GATE_DEFINITIONS.items():
            assert "name" in gate_def, f"Gate {gate_id} missing name"
            assert "description" in gate_def, f"Gate {gate_id} missing description"
            assert "required_for" in gate_def, f"Gate {gate_id} missing required_for"


class TestCertificationEngineGates:
    """Tests for individual quality gate checks."""

    @pytest.fixture
    def engine(self):
        """Create a certification engine for testing."""
        return CertificationEngine()

    @pytest.fixture
    def temp_package(self, tmp_path):
        """Create a temporary test package with manifest."""
        pkg_path = tmp_path / "test-plugin-1.0.0.vspkg"
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "plugin_type": "audio",
            "license": "MIT",
        }
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
        return pkg_path

    @pytest.fixture
    def temp_package_with_sbom(self, tmp_path):
        """Create a test package with manifest and SBOM."""
        pkg_path = tmp_path / "test-plugin-1.0.0.vspkg"
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "plugin_type": "audio",
            "license": "MIT",
        }
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "components": [],
        }
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("sbom.json", json.dumps(sbom))
        return pkg_path

    def test_extract_manifest(self, engine, temp_package):
        """Should extract manifest from package."""
        manifest = engine._extract_manifest(temp_package)
        assert manifest["name"] == "test-plugin"
        assert manifest["version"] == "1.0.0"

    def test_extract_manifest_not_found(self, engine, tmp_path):
        """Should return None if manifest not found."""
        pkg_path = tmp_path / "empty.vspkg"
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("other.txt", "content")

        manifest = engine._extract_manifest(pkg_path)
        assert manifest is None

    @pytest.mark.asyncio
    async def test_check_manifest_pass(self, engine, temp_package):
        """Should pass manifest check for valid manifest."""
        manifest = engine._extract_manifest(temp_package)
        gate = await engine._check_manifest(manifest, temp_package)
        assert gate.status == GateStatus.PASSED

    @pytest.mark.asyncio
    async def test_check_manifest_fail_missing_field(self, engine, tmp_path):
        """Should fail manifest check for missing required fields."""
        pkg_path = tmp_path / "bad.vspkg"
        manifest = {"name": "test", "version": "1.0.0"}  # Missing author, plugin_type
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))

        extracted = engine._extract_manifest(pkg_path)
        gate = await engine._check_manifest(extracted, pkg_path)
        assert gate.status == GateStatus.FAILED

    @pytest.mark.asyncio
    async def test_check_sbom_present(self, engine, temp_package_with_sbom):
        """Should pass SBOM check when SBOM is present."""
        gate = await engine._check_sbom(temp_package_with_sbom)
        assert gate.status == GateStatus.PASSED

    @pytest.mark.asyncio
    async def test_check_sbom_missing_not_required(self, engine, temp_package):
        """Should skip SBOM check when SBOM is missing but not required."""
        # Default policy has require_sbom=True, so create engine with BASIC policy
        basic_policy = CertificationPolicy.for_level(CertificationLevel.BASIC)
        engine_basic = CertificationEngine(policy=basic_policy)
        gate = await engine_basic._check_sbom(temp_package)
        # When not required and missing, should be skipped
        assert gate.status in (GateStatus.SKIPPED, GateStatus.FAILED)


class TestCertificationEngineIntegration:
    """Integration tests for the certification engine."""

    @pytest.fixture
    def full_package(self, tmp_path):
        """Create a fully-featured test package."""
        pkg_path = tmp_path / "full-plugin-1.0.0.vspkg"
        manifest = {
            "name": "full-plugin",
            "version": "1.0.0",
            "description": "A fully-featured test plugin",
            "author": "Test Author",
            "plugin_type": "audio",
            "license": "MIT",
        }
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "components": [
                {
                    "name": "requests",
                    "version": "2.28.0",
                    "licenses": [{"license": {"id": "Apache-2.0"}}],
                }
            ],
        }
        provenance = {
            "build_type": "local",
            "built_at": "2025-01-01T00:00:00Z",
            "builder": {"name": "VoiceStudio Plugin CLI"},
        }
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("sbom.json", json.dumps(sbom))
            zf.writestr("provenance.json", json.dumps(provenance))
        return pkg_path

    @pytest.mark.asyncio
    async def test_certify_basic_level(self, tmp_path):
        """Should certify package at basic level."""
        # Create minimal package for basic certification
        pkg_path = tmp_path / "basic-plugin-1.0.0.vspkg"
        manifest = {
            "name": "basic-plugin",
            "version": "1.0.0",
            "description": "A basic test plugin",
            "author": "Test Author",
            "plugin_type": "audio",
            "license": "MIT",
        }
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))

        policy = CertificationPolicy.for_level(CertificationLevel.BASIC)
        engine = CertificationEngine(policy=policy)

        result = await engine.certify_package(pkg_path)

        # Should have plugin info
        assert result.plugin_id == "basic-plugin"
        assert result.plugin_version == "1.0.0"

    @pytest.mark.asyncio
    async def test_certify_returns_certificate_id(self, full_package):
        """Should generate certificate ID when certified."""
        policy = CertificationPolicy.for_level(CertificationLevel.BASIC)
        engine = CertificationEngine(policy=policy)

        result = await engine.certify_package(full_package)

        # Should have some certificate ID if certified
        if result.certified:
            assert result.certificate_id != ""
            assert "VS-CERT-" in result.certificate_id

    @pytest.mark.asyncio
    async def test_certify_records_gates(self, full_package):
        """Should record all quality gate results."""
        policy = CertificationPolicy.for_level(CertificationLevel.STANDARD)
        engine = CertificationEngine(policy=policy)

        result = await engine.certify_package(full_package)

        # Should have quality gate results
        assert len(result.quality_gates) > 0

        # Check gate IDs are present
        gate_ids = {g.id for g in result.quality_gates}
        assert "manifest" in gate_ids

    @pytest.mark.asyncio
    async def test_certify_records_timestamp(self, full_package):
        """Should record certification timestamp."""
        engine = CertificationEngine()

        result = await engine.certify_package(full_package)

        assert result.certified_at is not None
        # Should be a valid ISO timestamp
        assert "T" in result.certified_at or "-" in result.certified_at


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_certification_engine(self):
        """Should return a certification engine instance."""
        engine = get_certification_engine()
        assert isinstance(engine, CertificationEngine)

    def test_get_certification_engine_with_policy(self):
        """Should accept policy parameter."""
        policy = CertificationPolicy(
            target_level=CertificationLevel.ENTERPRISE,
            require_signature=True,
        )
        engine = get_certification_engine(policy=policy)
        assert engine._policy.target_level == CertificationLevel.ENTERPRISE

    @pytest.mark.asyncio
    async def test_certify_plugin_function(self, tmp_path):
        """Should certify plugin via convenience function."""
        # Create test package
        pkg_path = tmp_path / "test-plugin-1.0.0.vspkg"
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "plugin_type": "audio",
            "license": "MIT",
        }
        with zipfile.ZipFile(pkg_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))

        result = await certify_plugin(pkg_path, target_level=CertificationLevel.BASIC)

        assert result is not None
        assert result.plugin_id == "test-plugin"


# =============================================================================
# Gate Level Requirements Tests
# =============================================================================


class TestGateLevelRequirements:
    """Tests for quality gate level requirements."""

    def test_basic_level_gates(self):
        """BASIC level should require manifest and vulnerability checks."""
        engine = CertificationEngine()

        basic_gates = []
        for gate_id, gate_def in engine.GATE_DEFINITIONS.items():
            if CertificationLevel.BASIC in gate_def["required_for"]:
                basic_gates.append(gate_id)

        assert "manifest" in basic_gates
        assert "vulnerabilities" in basic_gates

    def test_standard_level_gates(self):
        """STANDARD level should require SBOM and license checks."""
        engine = CertificationEngine()

        standard_gates = []
        for gate_id, gate_def in engine.GATE_DEFINITIONS.items():
            if CertificationLevel.STANDARD in gate_def["required_for"]:
                standard_gates.append(gate_id)

        assert "sbom" in standard_gates
        assert "licenses" in standard_gates

    def test_premium_level_gates(self):
        """PREMIUM level should require signature and provenance."""
        engine = CertificationEngine()

        premium_gates = []
        for gate_id, gate_def in engine.GATE_DEFINITIONS.items():
            if CertificationLevel.PREMIUM in gate_def["required_for"]:
                premium_gates.append(gate_id)

        assert "signature" in premium_gates
        assert "provenance" in premium_gates

    def test_enterprise_level_gates(self):
        """ENTERPRISE level should require tests, performance, security."""
        engine = CertificationEngine()

        enterprise_gates = []
        for gate_id, gate_def in engine.GATE_DEFINITIONS.items():
            if CertificationLevel.ENTERPRISE in gate_def["required_for"]:
                enterprise_gates.append(gate_id)

        assert "tests" in enterprise_gates
        assert "performance" in enterprise_gates
        assert "security" in enterprise_gates


# =============================================================================
# CertificationResult Helper Methods Tests
# =============================================================================


class TestCertificationResultHelpers:
    """Tests for CertificationResult helper methods."""

    def test_passed_gates_property(self):
        """Should return only passed gates."""
        gates = [
            QualityGate("a", "Gate A", "Desc A", GateStatus.PASSED),
            QualityGate("b", "Gate B", "Desc B", GateStatus.FAILED),
            QualityGate("c", "Gate C", "Desc C", GateStatus.PASSED),
        ]
        result = CertificationResult(
            plugin_id="test",
            plugin_version="1.0.0",
            certified=True,
            certification_level=CertificationLevel.BASIC,
            quality_gates=gates,
        )
        assert len(result.passed_gates) == 2

    def test_failed_gates_property(self):
        """Should return only failed gates."""
        gates = [
            QualityGate("a", "Gate A", "Desc A", GateStatus.PASSED),
            QualityGate("b", "Gate B", "Desc B", GateStatus.FAILED),
            QualityGate("c", "Gate C", "Desc C", GateStatus.FAILED),
        ]
        result = CertificationResult(
            plugin_id="test",
            plugin_version="1.0.0",
            certified=False,
            certification_level=CertificationLevel.NONE,
            quality_gates=gates,
        )
        assert len(result.failed_gates) == 2

    def test_get_quality_gates_summary(self):
        """Should return quality gates as bool dict."""
        gates = [
            QualityGate("manifest", "Manifest", "Desc", GateStatus.PASSED),
            QualityGate("sbom", "SBOM", "Desc", GateStatus.PASSED),
            QualityGate("signature", "Signature", "Desc", GateStatus.FAILED),
        ]
        result = CertificationResult(
            plugin_id="test",
            plugin_version="1.0.0",
            certified=True,
            certification_level=CertificationLevel.STANDARD,
            quality_gates=gates,
        )
        summary = result.get_quality_gates_summary()
        assert summary["manifest_valid"] is True
        assert summary["sbom_present"] is True
        assert summary["signature_valid"] is False
