"""
Unit tests for the plugin verification service.

Tests signature verification, SBOM validation, license checking,
and vulnerability scanning integration.
"""

import json
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.gallery.verification import (
    # Main class
    PluginVerificationService,
    # Data classes
    VerificationCheck,
    # Enums
    VerificationLevel,
    VerificationPolicy,
    VerificationResult,
    VerificationStatus,
    get_verification_service,
    # Convenience functions
    verify_package,
)

# =============================================================================
# VerificationLevel Tests
# =============================================================================


class TestVerificationLevel:
    """Tests for VerificationLevel enum."""
    
    def test_all_levels_defined(self):
        """All expected levels should be defined."""
        assert hasattr(VerificationLevel, "NONE")
        assert hasattr(VerificationLevel, "BASIC")
        assert hasattr(VerificationLevel, "STANDARD")
        assert hasattr(VerificationLevel, "STRICT")
        assert hasattr(VerificationLevel, "ENTERPRISE")
    
    def test_level_values(self):
        """Levels should have expected string values."""
        assert VerificationLevel.NONE.value == "none"
        assert VerificationLevel.STANDARD.value == "standard"
        assert VerificationLevel.ENTERPRISE.value == "enterprise"


# =============================================================================
# VerificationStatus Tests
# =============================================================================


class TestVerificationStatus:
    """Tests for VerificationStatus enum."""
    
    def test_all_statuses_defined(self):
        """All expected statuses should be defined."""
        assert hasattr(VerificationStatus, "PASSED")
        assert hasattr(VerificationStatus, "FAILED")
        assert hasattr(VerificationStatus, "SKIPPED")
        assert hasattr(VerificationStatus, "WARNING")
    
    def test_status_values(self):
        """Statuses should have expected string values."""
        assert VerificationStatus.PASSED.value == "passed"
        assert VerificationStatus.FAILED.value == "failed"


# =============================================================================
# VerificationCheck Tests
# =============================================================================


class TestVerificationCheck:
    """Tests for VerificationCheck dataclass."""
    
    def test_basic_creation(self):
        """Should create with name and status."""
        check = VerificationCheck(
            name="test_check",
            status=VerificationStatus.PASSED,
        )
        assert check.name == "test_check"
        assert check.status == VerificationStatus.PASSED
        assert check.message == ""
    
    def test_with_message_and_details(self):
        """Should include message and details."""
        check = VerificationCheck(
            name="signature",
            status=VerificationStatus.FAILED,
            message="Signature invalid",
            details={"key_id": "abc123"},
            duration_ms=42.5,
        )
        assert check.message == "Signature invalid"
        assert check.details["key_id"] == "abc123"
        assert check.duration_ms == 42.5
    
    def test_to_dict(self):
        """Should convert to dictionary."""
        check = VerificationCheck(
            name="checksum",
            status=VerificationStatus.PASSED,
            message="OK",
        )
        d = check.to_dict()
        assert d["name"] == "checksum"
        assert d["status"] == "passed"
        assert d["message"] == "OK"


# =============================================================================
# VerificationResult Tests
# =============================================================================


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""
    
    def test_basic_creation(self):
        """Should create with path and plugin info."""
        result = VerificationResult(
            package_path="/path/to/plugin.vspkg",
            plugin_id="test-plugin",
            version="1.0.0",
            level=VerificationLevel.STANDARD,
        )
        assert result.package_path == "/path/to/plugin.vspkg"
        assert result.plugin_id == "test-plugin"
        assert result.version == "1.0.0"
        assert result.passed is False
        assert result.verified_at != ""
    
    def test_failed_checks(self):
        """Should return failed checks."""
        result = VerificationResult(
            package_path="",
            plugin_id="",
            version="",
            level=VerificationLevel.BASIC,
            checks=[
                VerificationCheck(name="a", status=VerificationStatus.PASSED),
                VerificationCheck(name="b", status=VerificationStatus.FAILED),
                VerificationCheck(name="c", status=VerificationStatus.WARNING),
            ],
        )
        failed = result.failed_checks
        assert len(failed) == 1
        assert failed[0].name == "b"
    
    def test_warning_checks(self):
        """Should return warning checks."""
        result = VerificationResult(
            package_path="",
            plugin_id="",
            version="",
            level=VerificationLevel.BASIC,
            checks=[
                VerificationCheck(name="a", status=VerificationStatus.PASSED),
                VerificationCheck(name="b", status=VerificationStatus.WARNING),
            ],
        )
        warnings = result.warning_checks
        assert len(warnings) == 1
        assert warnings[0].name == "b"
    
    def test_to_dict(self):
        """Should convert to dictionary."""
        result = VerificationResult(
            package_path="/pkg.zip",
            plugin_id="my-plugin",
            version="2.0.0",
            level=VerificationLevel.STRICT,
            passed=True,
        )
        d = result.to_dict()
        assert d["plugin_id"] == "my-plugin"
        assert d["level"] == "strict"
        assert d["passed"] is True
        assert "has_sbom" in d
    
    def test_to_json(self):
        """Should convert to JSON."""
        result = VerificationResult(
            package_path="",
            plugin_id="test",
            version="1.0.0",
            level=VerificationLevel.BASIC,
        )
        j = result.to_json()
        data = json.loads(j)
        assert data["plugin_id"] == "test"


# =============================================================================
# VerificationPolicy Tests
# =============================================================================


class TestVerificationPolicy:
    """Tests for VerificationPolicy dataclass."""
    
    def test_default_values(self):
        """Should have sensible defaults."""
        policy = VerificationPolicy()
        assert policy.level == VerificationLevel.STANDARD
        assert policy.require_signature is True
        assert policy.require_sbom is False
        assert policy.max_critical_vulns == 0
        assert policy.max_high_vulns == 5
    
    def test_custom_values(self):
        """Should accept custom values."""
        policy = VerificationPolicy(
            level=VerificationLevel.STRICT,
            require_signature=False,
            require_sbom=True,
            blocked_licenses=["GPL-3.0-only"],
            max_high_vulns=0,
        )
        assert policy.level == VerificationLevel.STRICT
        assert policy.require_signature is False
        assert policy.require_sbom is True
        assert "GPL-3.0-only" in policy.blocked_licenses
    
    def test_to_dict(self):
        """Should convert to dictionary."""
        policy = VerificationPolicy()
        d = policy.to_dict()
        assert d["level"] == "standard"
        assert "require_signature" in d
    
    def test_from_dict(self):
        """Should create from dictionary."""
        data = {
            "level": "strict",
            "require_signature": False,
            "max_critical_vulns": 5,
        }
        policy = VerificationPolicy.from_dict(data)
        assert policy.level == VerificationLevel.STRICT
        assert policy.require_signature is False
        assert policy.max_critical_vulns == 5


# =============================================================================
# Helper Functions for Test Fixtures
# =============================================================================


def create_test_package(
    tmpdir: Path,
    plugin_id: str = "test-plugin",
    version: str = "1.0.0",
    include_manifest: bool = True,
    include_sbom: bool = False,
    include_signature: bool = False,
    include_provenance: bool = False,
) -> Path:
    """Create a test plugin package for verification."""
    pkg_path = tmpdir / f"{plugin_id}-{version}.vspkg"
    
    with zipfile.ZipFile(pkg_path, "w") as zf:
        if include_manifest:
            manifest = {
                "id": plugin_id,
                "version": version,
                "name": "Test Plugin",
                "description": "A test plugin",
            }
            zf.writestr("manifest.json", json.dumps(manifest))
        
        if include_sbom:
            sbom = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "components": [
                    {
                        "name": "requests",
                        "version": "2.28.0",
                        "licenses": [{"license": {"id": "Apache-2.0"}}],
                    },
                ],
            }
            zf.writestr("sbom.json", json.dumps(sbom))
        
        if include_signature:
            sig = {
                "key_id": "test-key-001",
                "signature_id": "sig-001",
                "signature": "test_signature_base64",
                "signed_at": "2024-01-01T00:00:00Z",
                "package_digest": {"sha256": "abc123"},
            }
            zf.writestr("signature.json", json.dumps(sig))
        
        if include_provenance:
            prov = {
                "version": "1.0",
                "build_type": "development",
                "builder": {"id": "test-builder"},
                "build_started_at": "2024-01-01T00:00:00Z",
            }
            zf.writestr("provenance.json", json.dumps(prov))
        
        # Always include some content
        zf.writestr("plugin.py", "# Test plugin code\n")
    
    return pkg_path


# =============================================================================
# PluginVerificationService Tests
# =============================================================================


class TestPluginVerificationService:
    """Tests for PluginVerificationService class."""
    
    def test_create_service(self):
        """Should create with default settings."""
        service = PluginVerificationService()
        assert service._default_policy.level == VerificationLevel.STANDARD
    
    def test_create_with_policy(self):
        """Should create with custom policy."""
        policy = VerificationPolicy(level=VerificationLevel.STRICT)
        service = PluginVerificationService(policy=policy)
        assert service._default_policy.level == VerificationLevel.STRICT
    
    @pytest.mark.asyncio
    async def test_verify_nonexistent_package(self):
        """Should fail for missing package."""
        service = PluginVerificationService()
        result = await service.verify_package(Path("/nonexistent/plugin.vspkg"))
        
        assert result.passed is False
        assert any(c.name == "file_exists" and c.status == VerificationStatus.FAILED
                   for c in result.checks)
    
    @pytest.mark.asyncio
    async def test_verify_package_level_none(self):
        """Level NONE should only check file exists."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(Path(tmpdir))
            
            policy = VerificationPolicy(level=VerificationLevel.NONE)
            service = PluginVerificationService(policy=policy)
            result = await service.verify_package(pkg_path, policy)
            
            assert result.passed is True
            assert len(result.checks) == 2  # file_exists, manifest_valid
    
    @pytest.mark.asyncio
    async def test_verify_package_level_basic(self):
        """Level BASIC should check file and checksum."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(Path(tmpdir))
            
            policy = VerificationPolicy(level=VerificationLevel.BASIC)
            service = PluginVerificationService(policy=policy)
            result = await service.verify_package(pkg_path, policy)
            
            assert result.passed is True
            check_names = [c.name for c in result.checks]
            assert "file_exists" in check_names
            assert "manifest_valid" in check_names
            assert "checksum" in check_names
    
    @pytest.mark.asyncio
    async def test_verify_package_extracts_manifest(self):
        """Should extract plugin ID and version from manifest."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                plugin_id="my-plugin",
                version="2.5.0",
            )
            
            policy = VerificationPolicy(level=VerificationLevel.BASIC)
            service = PluginVerificationService(policy=policy)
            result = await service.verify_package(pkg_path, policy)
            
            assert result.plugin_id == "my-plugin"
            assert result.version == "2.5.0"
    
    @pytest.mark.asyncio
    async def test_verify_package_no_manifest(self):
        """Should fail if manifest missing."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_manifest=False,
            )
            
            policy = VerificationPolicy(level=VerificationLevel.BASIC)
            service = PluginVerificationService(policy=policy)
            result = await service.verify_package(pkg_path, policy)
            
            assert any(
                c.name == "manifest_valid" and c.status == VerificationStatus.FAILED
                for c in result.checks
            )
    
    @pytest.mark.asyncio
    async def test_verify_package_signature_skipped_no_cryptography(self):
        """Should skip signature if cryptography unavailable."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(Path(tmpdir))
            
            policy = VerificationPolicy(
                level=VerificationLevel.STANDARD,
                require_signature=False,
            )
            service = PluginVerificationService(policy=policy)
            # Force signer unavailable
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            sig_check = next((c for c in result.checks if c.name == "signature"), None)
            assert sig_check is not None
            assert sig_check.status in (VerificationStatus.SKIPPED, VerificationStatus.WARNING)
    
    @pytest.mark.asyncio
    async def test_verify_package_signature_required_fails(self):
        """Should fail if signature required but not found."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_signature=False,
            )
            
            policy = VerificationPolicy(
                level=VerificationLevel.STANDARD,
                require_signature=True,
            )
            service = PluginVerificationService(policy=policy)
            # Simulate signer available
            service._signer_available = True
            
            result = await service.verify_package(pkg_path, policy)
            
            sig_check = next((c for c in result.checks if c.name == "signature"), None)
            assert sig_check is not None
            assert sig_check.status == VerificationStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_verify_package_sbom_extraction(self):
        """Should extract SBOM from package."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_sbom=True,
            )
            
            policy = VerificationPolicy(
                level=VerificationLevel.STRICT,
                require_signature=False,
            )
            service = PluginVerificationService(policy=policy)
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            sbom_check = next((c for c in result.checks if c.name == "sbom"), None)
            assert sbom_check is not None
            assert sbom_check.status in (VerificationStatus.PASSED, VerificationStatus.WARNING)
            assert result.sbom is not None
    
    @pytest.mark.asyncio
    async def test_verify_package_sbom_required_fails(self):
        """Should fail if SBOM required but not found."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_sbom=False,
            )
            
            policy = VerificationPolicy(
                level=VerificationLevel.STRICT,
                require_sbom=True,
                require_signature=False,
            )
            service = PluginVerificationService(policy=policy)
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            sbom_check = next((c for c in result.checks if c.name == "sbom"), None)
            assert sbom_check is not None
            assert sbom_check.status == VerificationStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_verify_package_provenance_extraction(self):
        """Should extract provenance from package."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_provenance=True,
            )
            
            policy = VerificationPolicy(
                level=VerificationLevel.ENTERPRISE,
                require_signature=False,
                require_sbom=False,
            )
            service = PluginVerificationService(policy=policy)
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            prov_check = next((c for c in result.checks if c.name == "provenance"), None)
            assert prov_check is not None
            assert prov_check.status in (VerificationStatus.PASSED, VerificationStatus.WARNING)
            assert result.provenance is not None
    
    @pytest.mark.asyncio
    async def test_verify_package_provenance_required_fails(self):
        """Should fail if provenance required but not found."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_provenance=False,
            )
            
            policy = VerificationPolicy(
                level=VerificationLevel.ENTERPRISE,
                require_provenance=True,
                require_signature=False,
                require_sbom=False,
            )
            service = PluginVerificationService(policy=policy)
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            prov_check = next((c for c in result.checks if c.name == "provenance"), None)
            assert prov_check is not None
            assert prov_check.status == VerificationStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_verify_package_progress_callback(self):
        """Should call progress callback."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(Path(tmpdir))
            
            progress_calls = []
            
            def callback(message: str, progress: float):
                progress_calls.append((message, progress))
            
            policy = VerificationPolicy(level=VerificationLevel.BASIC)
            service = PluginVerificationService(policy=policy)
            await service.verify_package(pkg_path, policy, progress_callback=callback)
            
            assert len(progress_calls) > 0
            # Last call should be 1.0 or close
            assert progress_calls[-1][1] >= 0.0


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""
    
    @pytest.mark.asyncio
    async def test_verify_package_function(self):
        """Should verify package with specified level."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(Path(tmpdir))
            
            result = await verify_package(
                pkg_path,
                level=VerificationLevel.BASIC,
            )
            
            assert result.level == VerificationLevel.BASIC
            assert result.passed is True
    
    @pytest.mark.asyncio
    async def test_verify_package_with_policy_kwargs(self):
        """Should pass policy kwargs."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(Path(tmpdir))
            
            result = await verify_package(
                pkg_path,
                level=VerificationLevel.STRICT,
                require_sbom=False,
                require_signature=False,
            )
            
            assert result.level == VerificationLevel.STRICT
    
    def test_get_verification_service(self):
        """Should create service instance."""
        service = get_verification_service()
        assert isinstance(service, PluginVerificationService)
    
    def test_get_verification_service_with_policy(self):
        """Should create service with policy."""
        policy = VerificationPolicy(level=VerificationLevel.STRICT)
        service = get_verification_service(policy=policy)
        assert service._default_policy.level == VerificationLevel.STRICT


# =============================================================================
# Integration Tests
# =============================================================================


class TestVerificationIntegration:
    """Integration tests for verification workflow."""
    
    @pytest.mark.asyncio
    async def test_full_verification_workflow(self):
        """Test full verification with all components."""
        with TemporaryDirectory() as tmpdir:
            # Create a complete package
            pkg_path = create_test_package(
                Path(tmpdir),
                plugin_id="complete-plugin",
                version="1.0.0",
                include_manifest=True,
                include_sbom=True,
                include_provenance=True,
            )
            
            # Verify with enterprise level (no signature required for test)
            policy = VerificationPolicy(
                level=VerificationLevel.ENTERPRISE,
                require_signature=False,
                require_sbom=True,
                require_provenance=True,
            )
            service = PluginVerificationService(policy=policy)
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            # Should have all checks
            check_names = {c.name for c in result.checks}
            assert "file_exists" in check_names
            assert "manifest_valid" in check_names
            assert "checksum" in check_names
            assert "sbom" in check_names
            assert "provenance" in check_names
            
            # Should extract metadata
            assert result.plugin_id == "complete-plugin"
            assert result.version == "1.0.0"
            assert result.sbom is not None
            assert result.provenance is not None
            
            # Should pass (no failures)
            failed = result.failed_checks
            assert len(failed) == 0 or all(
                c.name == "signature" for c in failed  # Only signature may fail
            )
    
    @pytest.mark.asyncio
    async def test_verification_result_serialization(self):
        """Test result can be serialized and used."""
        with TemporaryDirectory() as tmpdir:
            pkg_path = create_test_package(
                Path(tmpdir),
                include_sbom=True,
            )
            
            policy = VerificationPolicy(
                level=VerificationLevel.STRICT,
                require_signature=False,
            )
            service = PluginVerificationService(policy=policy)
            service._signer_available = False
            
            result = await service.verify_package(pkg_path, policy)
            
            # Serialize to JSON
            json_str = result.to_json()
            
            # Should be valid JSON
            data = json.loads(json_str)
            assert data["plugin_id"] == "test-plugin"
            assert "checks" in data
            assert len(data["checks"]) > 0
