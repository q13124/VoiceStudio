"""
Unit tests for the license checker module.

Tests SPDX license validation, compatibility checking, and
dependency license analysis.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from backend.plugins.supply_chain.license_checker import (  # Database; Enums; Main class; Data classes; Convenience functions
    COMPATIBILITY_MATRIX,
    SPDX_LICENSES,
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

# =============================================================================
# LicenseCategory Tests
# =============================================================================


class TestLicenseCategory:
    """Tests for LicenseCategory enum."""

    def test_all_categories_defined(self):
        """All expected categories should be defined."""
        assert hasattr(LicenseCategory, "PERMISSIVE")
        assert hasattr(LicenseCategory, "COPYLEFT_WEAK")
        assert hasattr(LicenseCategory, "COPYLEFT_STRONG")
        assert hasattr(LicenseCategory, "PROPRIETARY")
        assert hasattr(LicenseCategory, "PUBLIC_DOMAIN")
        assert hasattr(LicenseCategory, "UNKNOWN")

    def test_category_values(self):
        """Categories should have expected string values."""
        assert LicenseCategory.PERMISSIVE.value == "permissive"
        assert LicenseCategory.COPYLEFT_STRONG.value == "copyleft_strong"
        assert LicenseCategory.PUBLIC_DOMAIN.value == "public_domain"


# =============================================================================
# CompatibilityLevel Tests
# =============================================================================


class TestCompatibilityLevel:
    """Tests for CompatibilityLevel enum."""

    def test_all_levels_defined(self):
        """All expected levels should be defined."""
        assert hasattr(CompatibilityLevel, "COMPATIBLE")
        assert hasattr(CompatibilityLevel, "COMPATIBLE_WITH_NOTICE")
        assert hasattr(CompatibilityLevel, "INCOMPATIBLE")
        assert hasattr(CompatibilityLevel, "UNKNOWN")
        assert hasattr(CompatibilityLevel, "REQUIRES_REVIEW")

    def test_level_values(self):
        """Levels should have expected string values."""
        assert CompatibilityLevel.COMPATIBLE.value == "compatible"
        assert CompatibilityLevel.INCOMPATIBLE.value == "incompatible"


# =============================================================================
# LicenseInfo Tests
# =============================================================================


class TestLicenseInfo:
    """Tests for LicenseInfo dataclass."""

    def test_basic_creation(self):
        """Should create with just SPDX ID."""
        info = LicenseInfo(spdx_id="MIT")
        assert info.spdx_id == "MIT"
        assert info.name == "MIT License"  # Auto-populated
        assert info.category == LicenseCategory.PERMISSIVE
        assert info.osi_approved is True
        assert info.copyleft is False

    def test_unknown_license(self):
        """Unknown license should have UNKNOWN category."""
        info = LicenseInfo(spdx_id="Some-Unknown-License")
        assert info.spdx_id == "Some-Unknown-License"
        assert info.category == LicenseCategory.UNKNOWN
        assert info.osi_approved is False

    def test_copyleft_license(self):
        """Copyleft licenses should be marked correctly."""
        info = LicenseInfo(spdx_id="GPL-3.0-only")
        assert info.copyleft is True
        assert info.category == LicenseCategory.COPYLEFT_STRONG

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        info = LicenseInfo(spdx_id="Apache-2.0", url="https://apache.org/licenses")
        d = info.to_dict()
        assert d["spdx_id"] == "Apache-2.0"
        assert d["category"] == "permissive"
        assert d["osi_approved"] is True
        assert d["url"] == "https://apache.org/licenses"

    def test_from_dict(self):
        """Should create from dictionary."""
        data = {
            "spdx_id": "BSD-3-Clause",
            "name": "BSD 3-Clause",
            "category": "permissive",
            "osi_approved": True,
            "copyleft": False,
        }
        info = LicenseInfo.from_dict(data)
        assert info.spdx_id == "BSD-3-Clause"
        assert info.category == LicenseCategory.PERMISSIVE


# =============================================================================
# DependencyLicense Tests
# =============================================================================


class TestDependencyLicense:
    """Tests for DependencyLicense dataclass."""

    def test_basic_creation(self):
        """Should create with package info."""
        dep = DependencyLicense(
            package_name="requests",
            package_version="2.28.0",
            license_id="Apache-2.0",
        )
        assert dep.package_name == "requests"
        assert dep.package_version == "2.28.0"
        assert dep.license_id == "Apache-2.0"
        assert dep.license_info is not None
        assert dep.license_info.category == LicenseCategory.PERMISSIVE

    def test_detected_from(self):
        """Should track detection source."""
        dep = DependencyLicense(
            package_name="flask",
            package_version="2.0.0",
            license_id="BSD-3-Clause",
            detected_from="sbom",
        )
        assert dep.detected_from == "sbom"

    def test_to_dict(self):
        """Should convert to dictionary."""
        dep = DependencyLicense(
            package_name="numpy",
            package_version="1.24.0",
            license_id="BSD-3-Clause",
        )
        d = dep.to_dict()
        assert d["package_name"] == "numpy"
        assert d["package_version"] == "1.24.0"
        assert d["license_id"] == "BSD-3-Clause"
        assert "license_info" in d


# =============================================================================
# CompatibilityIssue Tests
# =============================================================================


class TestCompatibilityIssue:
    """Tests for CompatibilityIssue dataclass."""

    def test_basic_creation(self):
        """Should create with dependency and level."""
        dep = DependencyLicense("pkg", "1.0", "GPL-3.0-only")
        issue = CompatibilityIssue(
            dependency=dep,
            level=CompatibilityLevel.INCOMPATIBLE,
            reason="GPL incompatible with MIT",
        )
        assert issue.level == CompatibilityLevel.INCOMPATIBLE
        assert "GPL incompatible" in issue.reason

    def test_with_recommendation(self):
        """Should include recommendation."""
        dep = DependencyLicense("pkg", "1.0", "GPL-3.0-only")
        issue = CompatibilityIssue(
            dependency=dep,
            level=CompatibilityLevel.INCOMPATIBLE,
            reason="License conflict",
            recommendation="Replace dependency",
        )
        assert issue.recommendation == "Replace dependency"

    def test_to_dict(self):
        """Should convert to dictionary."""
        dep = DependencyLicense("pkg", "1.0", "LGPL-3.0-only")
        issue = CompatibilityIssue(
            dependency=dep,
            level=CompatibilityLevel.COMPATIBLE_WITH_NOTICE,
            reason="Needs attribution",
        )
        d = issue.to_dict()
        assert d["level"] == "compatible_with_notice"
        assert "dependency" in d


# =============================================================================
# LicenseCheckResult Tests
# =============================================================================


class TestLicenseCheckResult:
    """Tests for LicenseCheckResult dataclass."""

    def test_basic_creation(self):
        """Should create with plugin info."""
        result = LicenseCheckResult(
            plugin_id="my-plugin",
            plugin_license="MIT",
        )
        assert result.plugin_id == "my-plugin"
        assert result.plugin_license == "MIT"
        assert result.passed is True
        assert len(result.issues) == 0

    def test_has_incompatible(self):
        """Should detect incompatible issues."""
        dep = DependencyLicense("pkg", "1.0", "GPL-3.0-only")
        issue = CompatibilityIssue(
            dependency=dep,
            level=CompatibilityLevel.INCOMPATIBLE,
            reason="Test",
        )
        result = LicenseCheckResult(
            plugin_id="my-plugin",
            plugin_license="MIT",
            issues=[issue],
        )
        assert result.has_incompatible is True

    def test_has_copyleft(self):
        """Should detect copyleft dependencies."""
        dep = DependencyLicense("pkg", "1.0", "LGPL-3.0-only")
        result = LicenseCheckResult(
            plugin_id="my-plugin",
            plugin_license="MIT",
            dependencies=[dep],
        )
        assert result.has_copyleft is True

    def test_requires_review(self):
        """Should detect review requirements."""
        dep = DependencyLicense("pkg", "1.0", "Unknown")
        issue = CompatibilityIssue(
            dependency=dep,
            level=CompatibilityLevel.REQUIRES_REVIEW,
            reason="Test",
        )
        result = LicenseCheckResult(
            plugin_id="my-plugin",
            plugin_license="MIT",
            issues=[issue],
        )
        assert result.requires_review is True

    def test_to_dict(self):
        """Should convert to dictionary."""
        result = LicenseCheckResult(
            plugin_id="my-plugin",
            plugin_license="Apache-2.0",
            warnings=["Test warning"],
        )
        d = result.to_dict()
        assert d["plugin_id"] == "my-plugin"
        assert d["plugin_license"] == "Apache-2.0"
        assert "Test warning" in d["warnings"]
        assert "has_incompatible" in d

    def test_to_json(self):
        """Should convert to JSON."""
        result = LicenseCheckResult(
            plugin_id="my-plugin",
            plugin_license="MIT",
        )
        j = result.to_json()
        data = json.loads(j)
        assert data["plugin_id"] == "my-plugin"

    def test_save(self):
        """Should save to file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.json"
            result = LicenseCheckResult(
                plugin_id="my-plugin",
                plugin_license="MIT",
            )
            result.save(path)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["plugin_id"] == "my-plugin"


# =============================================================================
# SPDX License Database Tests
# =============================================================================


class TestSPDXDatabase:
    """Tests for the SPDX license database."""

    def test_common_licenses_present(self):
        """Common licenses should be in database."""
        common = ["MIT", "Apache-2.0", "GPL-3.0-only", "BSD-3-Clause", "LGPL-3.0-only"]
        for lic in common:
            assert lic in SPDX_LICENSES, f"Missing license: {lic}"

    def test_license_has_required_fields(self):
        """Each license should have required fields."""
        for spdx_id, info in SPDX_LICENSES.items():
            assert "name" in info, f"{spdx_id} missing name"
            assert "category" in info, f"{spdx_id} missing category"
            assert "osi_approved" in info, f"{spdx_id} missing osi_approved"
            assert "copyleft" in info, f"{spdx_id} missing copyleft"

    def test_permissive_not_copyleft(self):
        """Permissive licenses should not be copyleft."""
        for spdx_id, info in SPDX_LICENSES.items():
            if info["category"] == LicenseCategory.PERMISSIVE:
                assert info["copyleft"] is False, f"{spdx_id} is permissive but marked copyleft"

    def test_copyleft_strong_is_copyleft(self):
        """Strong copyleft licenses should be marked as copyleft."""
        for spdx_id, info in SPDX_LICENSES.items():
            if info["category"] == LicenseCategory.COPYLEFT_STRONG:
                assert info["copyleft"] is True, f"{spdx_id} is strong copyleft but not marked"


# =============================================================================
# Compatibility Matrix Tests
# =============================================================================


class TestCompatibilityMatrix:
    """Tests for the compatibility matrix."""

    def test_permissive_with_permissive(self):
        """Permissive + permissive should be compatible."""
        key = (LicenseCategory.PERMISSIVE, LicenseCategory.PERMISSIVE)
        assert COMPATIBILITY_MATRIX[key] == CompatibilityLevel.COMPATIBLE

    def test_permissive_with_strong_copyleft(self):
        """Permissive + strong copyleft should be incompatible."""
        key = (LicenseCategory.PERMISSIVE, LicenseCategory.COPYLEFT_STRONG)
        assert COMPATIBILITY_MATRIX[key] == CompatibilityLevel.INCOMPATIBLE

    def test_copyleft_strong_with_permissive(self):
        """Strong copyleft + permissive should be compatible."""
        key = (LicenseCategory.COPYLEFT_STRONG, LicenseCategory.PERMISSIVE)
        assert COMPATIBILITY_MATRIX[key] == CompatibilityLevel.COMPATIBLE

    def test_matrix_is_populated(self):
        """Matrix should have entries for common combinations."""
        # Check that main category pairs are defined
        categories = [
            LicenseCategory.PERMISSIVE,
            LicenseCategory.COPYLEFT_WEAK,
            LicenseCategory.COPYLEFT_STRONG,
            LicenseCategory.PUBLIC_DOMAIN,
            LicenseCategory.PROPRIETARY,
        ]
        for proj in categories:
            for dep in categories:
                key = (proj, dep)
                assert key in COMPATIBILITY_MATRIX, f"Missing matrix entry: {key}"


# =============================================================================
# LicenseChecker Tests
# =============================================================================


class TestLicenseChecker:
    """Tests for LicenseChecker class."""

    def test_create_checker(self):
        """Should create with default settings."""
        checker = LicenseChecker()
        assert LicenseCategory.PERMISSIVE in checker.allowed_categories
        assert len(checker.blocked_licenses) == 0

    def test_create_with_blocked_licenses(self):
        """Should create with blocked licenses."""
        checker = LicenseChecker(blocked_licenses={"AGPL-3.0-only"})
        assert "AGPL-3.0-only" in checker.blocked_licenses

    def test_is_valid_spdx(self):
        """Should validate known SPDX IDs."""
        checker = LicenseChecker()
        assert checker.is_valid_spdx("MIT") is True
        assert checker.is_valid_spdx("Apache-2.0") is True
        assert checker.is_valid_spdx("Not-A-License") is False

    def test_get_license_info(self):
        """Should get license information."""
        checker = LicenseChecker()
        info = checker.get_license_info("BSD-3-Clause")
        assert info.spdx_id == "BSD-3-Clause"
        assert info.category == LicenseCategory.PERMISSIVE

    def test_get_category(self):
        """Should get license category."""
        checker = LicenseChecker()
        assert checker.get_category("MIT") == LicenseCategory.PERMISSIVE
        assert checker.get_category("GPL-3.0-only") == LicenseCategory.COPYLEFT_STRONG
        assert checker.get_category("Unknown") == LicenseCategory.UNKNOWN

    def test_is_copyleft(self):
        """Should detect copyleft licenses."""
        checker = LicenseChecker()
        assert checker.is_copyleft("GPL-3.0-only") is True
        assert checker.is_copyleft("LGPL-3.0-only") is True
        assert checker.is_copyleft("MIT") is False
        assert checker.is_copyleft("Apache-2.0") is False

    def test_is_copyleft_heuristic(self):
        """Should use heuristic for unknown copyleft."""
        checker = LicenseChecker()
        # Unknown GPL variant should be detected
        assert checker.is_copyleft("GPL-2.0-custom") is True

    def test_check_compatibility_permissive(self):
        """Permissive licenses should be compatible."""
        checker = LicenseChecker()
        result = checker.check_compatibility("MIT", "Apache-2.0")
        assert result == CompatibilityLevel.COMPATIBLE

    def test_check_compatibility_copyleft(self):
        """Should detect copyleft incompatibility."""
        checker = LicenseChecker()
        result = checker.check_compatibility("MIT", "GPL-3.0-only")
        assert result == CompatibilityLevel.INCOMPATIBLE

    def test_check_compatibility_unknown(self):
        """Unknown licenses should return UNKNOWN level."""
        checker = LicenseChecker()
        result = checker.check_compatibility("MIT", "Unknown-License")
        assert result == CompatibilityLevel.UNKNOWN

    def test_check_plugin_all_permissive(self):
        """Plugin with all permissive deps should pass."""
        checker = LicenseChecker()
        deps = [
            DependencyLicense("requests", "2.28.0", "Apache-2.0"),
            DependencyLicense("flask", "2.0.0", "BSD-3-Clause"),
            DependencyLicense("click", "8.0.0", "BSD-3-Clause"),
        ]
        result = checker.check_plugin("my-plugin", "MIT", deps)
        assert result.passed is True
        assert len(result.issues) == 0

    def test_check_plugin_with_copyleft(self):
        """Plugin with copyleft dep should fail for permissive project."""
        checker = LicenseChecker()
        deps = [
            DependencyLicense("requests", "2.28.0", "Apache-2.0"),
            DependencyLicense("gpl-lib", "1.0.0", "GPL-3.0-only"),
        ]
        result = checker.check_plugin("my-plugin", "MIT", deps)
        assert result.passed is False
        assert result.has_incompatible is True
        assert len(result.issues) >= 1

    def test_check_plugin_blocked_license(self):
        """Should block specified licenses."""
        checker = LicenseChecker(blocked_licenses={"AGPL-3.0-only"})
        deps = [
            DependencyLicense("agpl-lib", "1.0.0", "AGPL-3.0-only"),
        ]
        result = checker.check_plugin("my-plugin", "MIT", deps)
        assert result.passed is False
        assert any("blocked" in i.reason.lower() for i in result.issues)

    def test_check_plugin_warns_on_unknown_license(self):
        """Should warn about unknown licenses."""
        checker = LicenseChecker()
        deps = [
            DependencyLicense("unknown-pkg", "1.0.0", "Unknown-License-123"),
        ]
        result = checker.check_plugin("my-plugin", "MIT", deps)
        assert any("unrecognized" in w.lower() for w in result.warnings)

    def test_check_plugin_warns_on_copyleft(self):
        """Should warn about copyleft dependencies."""
        checker = LicenseChecker()
        deps = [
            DependencyLicense("lgpl-lib", "1.0.0", "LGPL-3.0-only"),
        ]
        result = checker.check_plugin("my-plugin", "GPL-3.0-only", deps)
        # GPL project can use LGPL, but should warn
        assert any("copyleft" in w.lower() for w in result.warnings)

    def test_check_plugin_category_not_allowed(self):
        """Should reject categories not in allowed list."""
        checker = LicenseChecker(allowed_categories={LicenseCategory.PERMISSIVE})
        deps = [
            DependencyLicense("lgpl-lib", "1.0.0", "LGPL-3.0-only"),
        ]
        result = checker.check_plugin("my-plugin", "MIT", deps)
        assert result.passed is False
        assert any("not allowed" in i.reason.lower() for i in result.issues)

    def test_check_sbom(self):
        """Should check licenses from SBOM file."""
        with TemporaryDirectory() as tmpdir:
            # Create test SBOM
            sbom_path = Path(tmpdir) / "sbom.json"
            sbom_data = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "components": [
                    {
                        "name": "requests",
                        "version": "2.28.0",
                        "licenses": [{"license": {"id": "Apache-2.0"}}],
                    },
                    {
                        "name": "flask",
                        "version": "2.0.0",
                        "licenses": [{"license": {"id": "BSD-3-Clause"}}],
                    },
                ],
            }
            sbom_path.write_text(json.dumps(sbom_data))

            checker = LicenseChecker()
            result = checker.check_sbom("my-plugin", "MIT", sbom_path)

            assert result.passed is True
            assert len(result.dependencies) == 2
            assert result.dependencies[0].detected_from == "sbom"

    def test_check_sbom_file_not_found(self):
        """Should raise error if SBOM not found."""
        checker = LicenseChecker()
        with pytest.raises(FileNotFoundError):
            checker.check_sbom("my-plugin", "MIT", Path("/nonexistent/sbom.json"))

    def test_check_sbom_with_name_license(self):
        """Should handle licenses with name instead of id."""
        with TemporaryDirectory() as tmpdir:
            sbom_path = Path(tmpdir) / "sbom.json"
            sbom_data = {
                "components": [
                    {
                        "name": "pkg",
                        "version": "1.0.0",
                        "licenses": [{"license": {"name": "MIT License"}}],
                    },
                ],
            }
            sbom_path.write_text(json.dumps(sbom_data))

            checker = LicenseChecker()
            result = checker.check_sbom("my-plugin", "MIT", sbom_path)

            assert len(result.dependencies) == 1
            # Name won't match SPDX exactly, so it will warn
            assert result.dependencies[0].license_id == "MIT License"

    def test_custom_compatibility(self):
        """Should use custom compatibility rules."""
        checker = LicenseChecker(
            custom_compatibility={
                ("MIT", "Custom-License"): CompatibilityLevel.COMPATIBLE,
            }
        )
        result = checker.check_compatibility("MIT", "Custom-License")
        assert result == CompatibilityLevel.COMPATIBLE


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_validate_spdx_license_valid(self):
        """Should validate known SPDX licenses."""
        is_valid, info = validate_spdx_license("MIT")
        assert is_valid is True
        assert info is not None
        assert info.spdx_id == "MIT"

    def test_validate_spdx_license_invalid(self):
        """Should reject unknown licenses."""
        is_valid, info = validate_spdx_license("Not-A-License")
        assert is_valid is False
        assert info is None

    def test_check_license_compatibility(self):
        """Should check compatibility for multiple licenses."""
        result = check_license_compatibility(
            "MIT",
            ["Apache-2.0", "BSD-3-Clause", "GPL-3.0-only"],
        )
        assert result["Apache-2.0"] == CompatibilityLevel.COMPATIBLE
        assert result["BSD-3-Clause"] == CompatibilityLevel.COMPATIBLE
        assert result["GPL-3.0-only"] == CompatibilityLevel.INCOMPATIBLE

    def test_get_allowed_licenses_default(self):
        """Should get permissive + public domain by default."""
        allowed = get_allowed_licenses()
        assert "MIT" in allowed
        assert "Apache-2.0" in allowed
        assert "CC0-1.0" in allowed
        assert "GPL-3.0-only" not in allowed

    def test_get_allowed_licenses_custom(self):
        """Should get licenses for specified categories."""
        allowed = get_allowed_licenses([LicenseCategory.COPYLEFT_STRONG])
        assert "GPL-3.0-only" in allowed
        assert "MIT" not in allowed

    def test_list_known_licenses(self):
        """Should list all known licenses."""
        licenses = list_known_licenses()
        assert len(licenses) > 0
        # Check structure
        lic = licenses[0]
        assert "spdx_id" in lic
        assert "name" in lic
        assert "category" in lic


# =============================================================================
# Integration Tests
# =============================================================================


class TestLicenseCheckerIntegration:
    """Integration tests for license checking workflow."""

    def test_full_workflow(self):
        """Test full license checking workflow."""
        # Create checker with policy
        checker = LicenseChecker(
            allowed_categories={
                LicenseCategory.PERMISSIVE,
                LicenseCategory.PUBLIC_DOMAIN,
                LicenseCategory.COPYLEFT_WEAK,
            },
            blocked_licenses={"AGPL-3.0-only"},
        )

        # Define dependencies
        deps = [
            DependencyLicense("requests", "2.28.0", "Apache-2.0"),
            DependencyLicense("flask", "2.0.0", "BSD-3-Clause"),
            DependencyLicense("numpy", "1.24.0", "BSD-3-Clause"),
            DependencyLicense("lgpl-lib", "1.0.0", "LGPL-3.0-only"),
        ]

        # Check plugin
        result = checker.check_plugin("my-plugin", "MIT", deps)

        # Validate result
        assert result.passed is True  # All compatible
        assert len(result.dependencies) == 4
        assert result.has_copyleft is True  # LGPL is copyleft

        # Check for LGPL notice
        notices = [i for i in result.issues if i.level == CompatibilityLevel.COMPATIBLE_WITH_NOTICE]
        assert len(notices) >= 1

        # Save and reload result
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "license-report.json"
            result.save(path)

            data = json.loads(path.read_text())
            assert data["plugin_id"] == "my-plugin"
            assert data["passed"] is True
