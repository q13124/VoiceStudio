"""
Unit tests for Vulnerability Scanner.

Tests the VulnerabilityScanner, ScanResult, Vulnerability, and related classes.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.supply_chain.vuln_scanner import (
    ScannerType,
    ScanResult,
    Severity,
    Vulnerability,
    VulnerabilityScanner,
    check_scanner_availability,
    scan_plugin,
    scan_sbom,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a temporary plugin directory."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    # Create requirements.txt
    (plugin_dir / "requirements.txt").write_text("requests==2.28.0\npydantic==2.0.0\n")

    return plugin_dir


@pytest.fixture
def sample_sbom(tmp_path):
    """Create a sample SBOM file."""
    sbom_path = tmp_path / "sbom.json"
    sbom_data = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "components": [
            {"name": "requests", "version": "2.28.0", "type": "library"},
            {"name": "pydantic", "version": "2.0.0", "type": "library"},
        ],
    }
    sbom_path.write_text(json.dumps(sbom_data))
    return sbom_path


@pytest.fixture
def sample_vulnerability():
    """Create a sample vulnerability."""
    return Vulnerability(
        id="CVE-2023-12345",
        package="requests",
        installed_version="2.28.0",
        fixed_version="2.28.1",
        severity=Severity.HIGH,
        title="HTTP Request Smuggling",
        description="A vulnerability in HTTP request handling.",
        cvss_score=7.5,
        references=["https://nvd.nist.gov/vuln/detail/CVE-2023-12345"],
        aliases=["GHSA-xxxx-yyyy-zzzz"],
    )


# =============================================================================
# Test Severity Enum
# =============================================================================


class TestSeverity:
    """Tests for Severity enum."""

    def test_all_severities_defined(self):
        """Test that all severity levels are defined."""
        expected = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]
        for name in expected:
            assert hasattr(Severity, name)

    def test_from_cvss_critical(self):
        """Test CVSS to severity conversion for critical."""
        assert Severity.from_cvss(9.0) == Severity.CRITICAL
        assert Severity.from_cvss(10.0) == Severity.CRITICAL

    def test_from_cvss_high(self):
        """Test CVSS to severity conversion for high."""
        assert Severity.from_cvss(7.0) == Severity.HIGH
        assert Severity.from_cvss(8.9) == Severity.HIGH

    def test_from_cvss_medium(self):
        """Test CVSS to severity conversion for medium."""
        assert Severity.from_cvss(4.0) == Severity.MEDIUM
        assert Severity.from_cvss(6.9) == Severity.MEDIUM

    def test_from_cvss_low(self):
        """Test CVSS to severity conversion for low."""
        assert Severity.from_cvss(0.1) == Severity.LOW
        assert Severity.from_cvss(3.9) == Severity.LOW

    def test_from_cvss_unknown(self):
        """Test CVSS to severity conversion for unknown."""
        assert Severity.from_cvss(0.0) == Severity.UNKNOWN

    def test_from_string(self):
        """Test parsing severity from string."""
        assert Severity.from_string("critical") == Severity.CRITICAL
        assert Severity.from_string("HIGH") == Severity.HIGH
        assert Severity.from_string("Medium") == Severity.MEDIUM
        assert Severity.from_string("low") == Severity.LOW
        assert Severity.from_string("invalid") == Severity.UNKNOWN


# =============================================================================
# Test Vulnerability
# =============================================================================


class TestVulnerability:
    """Tests for Vulnerability dataclass."""

    def test_basic_creation(self, sample_vulnerability):
        """Test creating a vulnerability."""
        vuln = sample_vulnerability

        assert vuln.id == "CVE-2023-12345"
        assert vuln.package == "requests"
        assert vuln.severity == Severity.HIGH
        assert vuln.cvss_score == 7.5

    def test_to_dict(self, sample_vulnerability):
        """Test converting vulnerability to dictionary."""
        data = sample_vulnerability.to_dict()

        assert data["id"] == "CVE-2023-12345"
        assert data["severity"] == "high"
        assert data["cvss_score"] == 7.5

    def test_from_dict(self):
        """Test creating vulnerability from dictionary."""
        data = {
            "id": "CVE-2023-99999",
            "package": "flask",
            "installed_version": "2.0.0",
            "fixed_version": "2.0.1",
            "severity": "critical",
            "title": "Critical Bug",
            "description": "A critical security issue",
            "cvss_score": 9.8,
            "references": ["https://example.com"],
            "aliases": ["GHSA-abcd-1234"],
        }

        vuln = Vulnerability.from_dict(data)

        assert vuln.id == "CVE-2023-99999"
        assert vuln.severity == Severity.CRITICAL
        assert len(vuln.references) == 1


# =============================================================================
# Test ScanResult
# =============================================================================


class TestScanResult:
    """Tests for ScanResult dataclass."""

    def test_basic_creation(self, sample_vulnerability):
        """Test creating a scan result."""
        result = ScanResult(
            scanner=ScannerType.PIP_AUDIT,
            scanned_at="2025-01-01T00:00:00",
            target="/path/to/plugin",
            vulnerabilities=[sample_vulnerability],
            packages_scanned=10,
            scan_duration_ms=500,
            success=True,
        )

        assert result.scanner == ScannerType.PIP_AUDIT
        assert result.success is True
        assert result.vulnerability_count == 1

    def test_severity_counts(self):
        """Test severity counting."""
        vulns = [
            Vulnerability(id="1", package="a", installed_version="1.0", fixed_version=None, severity=Severity.CRITICAL, title=""),
            Vulnerability(id="2", package="b", installed_version="1.0", fixed_version=None, severity=Severity.CRITICAL, title=""),
            Vulnerability(id="3", package="c", installed_version="1.0", fixed_version=None, severity=Severity.HIGH, title=""),
            Vulnerability(id="4", package="d", installed_version="1.0", fixed_version=None, severity=Severity.MEDIUM, title=""),
            Vulnerability(id="5", package="e", installed_version="1.0", fixed_version=None, severity=Severity.LOW, title=""),
        ]

        result = ScanResult(
            scanner=ScannerType.PIP_AUDIT,
            scanned_at="2025-01-01",
            target="/path",
            vulnerabilities=vulns,
            packages_scanned=5,
            scan_duration_ms=100,
            success=True,
        )

        assert result.critical_count == 2
        assert result.high_count == 1
        assert result.medium_count == 1
        assert result.low_count == 1

    def test_filter_by_severity(self, sample_vulnerability):
        """Test filtering vulnerabilities by severity."""
        vulns = [
            Vulnerability(id="1", package="a", installed_version="1.0", fixed_version=None, severity=Severity.CRITICAL, title=""),
            Vulnerability(id="2", package="b", installed_version="1.0", fixed_version=None, severity=Severity.HIGH, title=""),
            Vulnerability(id="3", package="c", installed_version="1.0", fixed_version=None, severity=Severity.LOW, title=""),
        ]

        result = ScanResult(
            scanner=ScannerType.PIP_AUDIT,
            scanned_at="2025-01-01",
            target="/path",
            vulnerabilities=vulns,
            packages_scanned=3,
            scan_duration_ms=100,
            success=True,
        )

        high_and_above = result.filter_by_severity(Severity.HIGH)
        assert len(high_and_above) == 2

        critical_only = result.filter_by_severity(Severity.CRITICAL)
        assert len(critical_only) == 1

    def test_to_dict(self, sample_vulnerability):
        """Test converting scan result to dictionary."""
        result = ScanResult(
            scanner=ScannerType.PIP_AUDIT,
            scanned_at="2025-01-01T00:00:00",
            target="/path/to/plugin",
            vulnerabilities=[sample_vulnerability],
            packages_scanned=10,
            scan_duration_ms=500,
            success=True,
        )

        data = result.to_dict()

        assert data["scanner"] == "pip-audit"
        assert data["success"] is True
        assert "summary" in data
        assert data["summary"]["total"] == 1

    def test_to_json(self, sample_vulnerability):
        """Test converting scan result to JSON."""
        result = ScanResult(
            scanner=ScannerType.PIP_AUDIT,
            scanned_at="2025-01-01T00:00:00",
            target="/path",
            vulnerabilities=[sample_vulnerability],
            packages_scanned=1,
            scan_duration_ms=100,
            success=True,
        )

        json_str = result.to_json()
        parsed = json.loads(json_str)

        assert parsed["scanner"] == "pip-audit"

    def test_save(self, sample_vulnerability, tmp_path):
        """Test saving scan result to file."""
        result = ScanResult(
            scanner=ScannerType.PIP_AUDIT,
            scanned_at="2025-01-01T00:00:00",
            target="/path",
            vulnerabilities=[sample_vulnerability],
            packages_scanned=1,
            scan_duration_ms=100,
            success=True,
        )

        output_path = tmp_path / "scan-result.json"
        result.save(output_path)

        assert output_path.exists()
        content = json.loads(output_path.read_text())
        assert content["scanner"] == "pip-audit"


# =============================================================================
# Test VulnerabilityScanner
# =============================================================================


class TestVulnerabilityScanner:
    """Tests for VulnerabilityScanner class."""

    def test_basic_creation(self):
        """Test creating a scanner."""
        scanner = VulnerabilityScanner()

        assert scanner.scanner_type == ScannerType.PIP_AUDIT

    def test_creation_with_grype(self):
        """Test creating a grype scanner."""
        scanner = VulnerabilityScanner(scanner_type=ScannerType.GRYPE)

        assert scanner.scanner_type == ScannerType.GRYPE

    @patch("backend.plugins.supply_chain.vuln_scanner.subprocess.run")
    def test_scan_directory_pip_audit(self, mock_run, temp_plugin_dir):
        """Test scanning directory with pip-audit."""
        # Mock pip-audit output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "dependencies": [
                    {
                        "name": "requests",
                        "version": "2.28.0",
                        "vulns": [
                            {
                                "id": "CVE-2023-12345",
                                "severity": "high",
                                "description": "Test vuln",
                                "fix_versions": ["2.28.1"],
                            }
                        ],
                    }
                ]
            }),
            stderr="",
        )

        scanner = VulnerabilityScanner(scanner_type=ScannerType.PIP_AUDIT)
        result = scanner.scan_directory(temp_plugin_dir)

        assert result.success is True
        assert len(result.vulnerabilities) == 1
        assert result.vulnerabilities[0].id == "CVE-2023-12345"

    @patch("backend.plugins.supply_chain.vuln_scanner.subprocess.run")
    def test_scan_directory_no_vulns(self, mock_run, temp_plugin_dir):
        """Test scanning with no vulnerabilities found."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"dependencies": []}),
            stderr="",
        )

        scanner = VulnerabilityScanner(scanner_type=ScannerType.PIP_AUDIT)
        result = scanner.scan_directory(temp_plugin_dir)

        assert result.success is True
        assert len(result.vulnerabilities) == 0

    @patch("backend.plugins.supply_chain.vuln_scanner.subprocess.run")
    def test_scan_directory_grype(self, mock_run, temp_plugin_dir):
        """Test scanning directory with grype."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "matches": [
                    {
                        "artifact": {"name": "flask", "version": "2.0.0"},
                        "vulnerability": {
                            "id": "CVE-2023-54321",
                            "severity": "critical",
                            "description": "Critical bug",
                            "fix": {"versions": ["2.0.1"]},
                            "cvss": [{"metrics": {"baseScore": 9.5}}],
                        },
                    }
                ]
            }),
            stderr="",
        )

        scanner = VulnerabilityScanner(scanner_type=ScannerType.GRYPE)
        result = scanner.scan_directory(temp_plugin_dir)

        assert result.success is True
        assert len(result.vulnerabilities) == 1
        assert result.vulnerabilities[0].severity == Severity.CRITICAL

    @patch("backend.plugins.supply_chain.vuln_scanner.subprocess.run")
    def test_scan_sbom(self, mock_run, sample_sbom):
        """Test scanning SBOM file."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"dependencies": []}),
            stderr="",
        )

        scanner = VulnerabilityScanner(scanner_type=ScannerType.PIP_AUDIT)
        result = scanner.scan_sbom(sample_sbom)

        assert result.success is True

    def test_scan_sbom_file_not_found(self, tmp_path):
        """Test scanning non-existent SBOM."""
        scanner = VulnerabilityScanner()
        result = scanner.scan_sbom(tmp_path / "nonexistent.json")

        assert result.success is False
        assert "not found" in result.error


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @patch("backend.plugins.supply_chain.vuln_scanner.subprocess.run")
    def test_scan_plugin(self, mock_run, temp_plugin_dir):
        """Test scan_plugin function."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"dependencies": []}),
            stderr="",
        )

        result = scan_plugin(temp_plugin_dir)

        assert result.success is True
        assert result.scanner == ScannerType.PIP_AUDIT

    @patch("backend.plugins.supply_chain.vuln_scanner.subprocess.run")
    def test_scan_sbom_function(self, mock_run, sample_sbom):
        """Test scan_sbom function."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"dependencies": []}),
            stderr="",
        )

        result = scan_sbom(sample_sbom)

        assert result.success is True

    @patch.object(VulnerabilityScanner, "_is_pip_audit_available", return_value=True)
    @patch.object(VulnerabilityScanner, "_is_grype_available", return_value=False)
    def test_check_scanner_availability(self, mock_grype, mock_pip_audit):
        """Test check_scanner_availability function."""
        availability = check_scanner_availability()

        assert "pip-audit" in availability
        assert "grype" in availability


# =============================================================================
# Test ScannerType Enum
# =============================================================================


class TestScannerType:
    """Tests for ScannerType enum."""

    def test_types_defined(self):
        """Test that all scanner types are defined."""
        assert hasattr(ScannerType, "PIP_AUDIT")
        assert hasattr(ScannerType, "GRYPE")

    def test_type_values(self):
        """Test scanner type values."""
        assert ScannerType.PIP_AUDIT.value == "pip-audit"
        assert ScannerType.GRYPE.value == "grype"
