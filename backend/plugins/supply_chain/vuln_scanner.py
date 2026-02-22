"""
Vulnerability Scanner for Plugin Dependencies.

Phase 5B M2: Wraps pip-audit and grype for dependency vulnerability scanning.
Provides local-first vulnerability detection without requiring external services.

Scanning Tools:
    - pip-audit: Python-specific vulnerability database (PyPI Advisory DB)
    - grype: Anchore's general-purpose vulnerability scanner
    - SBOM-based: Scan from existing SBOM files

This module supports:
    - Direct scanning of plugin directories
    - SBOM-based scanning (scan from CycloneDX SBOM)
    - Multiple vulnerability databases
    - Severity filtering and reporting
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Vulnerability severity levels (CVSS-based)."""

    CRITICAL = "critical"  # CVSS 9.0-10.0
    HIGH = "high"  # CVSS 7.0-8.9
    MEDIUM = "medium"  # CVSS 4.0-6.9
    LOW = "low"  # CVSS 0.1-3.9
    UNKNOWN = "unknown"  # No CVSS score available

    @classmethod
    def from_cvss(cls, score: float) -> Severity:
        """Convert CVSS score to severity level."""
        if score >= 9.0:
            return cls.CRITICAL
        elif score >= 7.0:
            return cls.HIGH
        elif score >= 4.0:
            return cls.MEDIUM
        elif score > 0.0:
            return cls.LOW
        return cls.UNKNOWN

    @classmethod
    def from_string(cls, severity_str: str) -> Severity:
        """Parse severity from string."""
        severity_str = severity_str.lower().strip()
        for severity in cls:
            if severity.value == severity_str:
                return severity
        return cls.UNKNOWN


class ScannerType(Enum):
    """Available vulnerability scanner types."""

    PIP_AUDIT = "pip-audit"
    GRYPE = "grype"


@dataclass
class Vulnerability:
    """A single vulnerability finding."""

    id: str  # CVE or advisory ID
    package: str
    installed_version: str
    fixed_version: Optional[str]
    severity: Severity
    title: str
    description: str = ""
    cvss_score: Optional[float] = None
    references: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "package": self.package,
            "installed_version": self.installed_version,
            "fixed_version": self.fixed_version,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "cvss_score": self.cvss_score,
            "references": self.references,
            "aliases": self.aliases,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Vulnerability:
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            package=data.get("package", ""),
            installed_version=data.get("installed_version", ""),
            fixed_version=data.get("fixed_version"),
            severity=Severity.from_string(data.get("severity", "unknown")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            cvss_score=data.get("cvss_score"),
            references=data.get("references", []),
            aliases=data.get("aliases", []),
        )


@dataclass
class ScanResult:
    """Result of a vulnerability scan."""

    scanner: ScannerType
    scanned_at: str
    target: str
    vulnerabilities: List[Vulnerability]
    packages_scanned: int
    scan_duration_ms: int
    success: bool
    error: Optional[str] = None

    @property
    def vulnerability_count(self) -> int:
        """Total number of vulnerabilities found."""
        return len(self.vulnerabilities)

    @property
    def critical_count(self) -> int:
        """Number of critical vulnerabilities."""
        return len([v for v in self.vulnerabilities if v.severity == Severity.CRITICAL])

    @property
    def high_count(self) -> int:
        """Number of high severity vulnerabilities."""
        return len([v for v in self.vulnerabilities if v.severity == Severity.HIGH])

    @property
    def medium_count(self) -> int:
        """Number of medium severity vulnerabilities."""
        return len([v for v in self.vulnerabilities if v.severity == Severity.MEDIUM])

    @property
    def low_count(self) -> int:
        """Number of low severity vulnerabilities."""
        return len([v for v in self.vulnerabilities if v.severity == Severity.LOW])

    def filter_by_severity(self, min_severity: Severity) -> List[Vulnerability]:
        """Filter vulnerabilities by minimum severity."""
        severity_order = [
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
            Severity.CRITICAL,
        ]

        min_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        return [v for v in self.vulnerabilities if v.severity in severity_order[min_index:]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scanner": self.scanner.value,
            "scanned_at": self.scanned_at,
            "target": self.target,
            "success": self.success,
            "error": self.error,
            "packages_scanned": self.packages_scanned,
            "scan_duration_ms": self.scan_duration_ms,
            "summary": {
                "total": self.vulnerability_count,
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
            },
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: Path) -> None:
        """Save scan result to file."""
        path.write_text(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScanResult:
        """Create from dictionary."""
        return cls(
            scanner=ScannerType(data.get("scanner", "pip-audit")),
            scanned_at=data.get("scanned_at", ""),
            target=data.get("target", ""),
            success=data.get("success", True),
            error=data.get("error"),
            packages_scanned=data.get("packages_scanned", 0),
            scan_duration_ms=data.get("scan_duration_ms", 0),
            vulnerabilities=[Vulnerability.from_dict(v) for v in data.get("vulnerabilities", [])],
        )


class VulnerabilityScanner:
    """
    Vulnerability scanner for plugin dependencies.

    Supports multiple scanning backends (pip-audit, grype) and provides
    a unified interface for vulnerability detection.
    """

    def __init__(
        self,
        scanner_type: ScannerType = ScannerType.PIP_AUDIT,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize scanner.

        Args:
            scanner_type: Scanner backend to use
            cache_dir: Directory for caching vulnerability databases
        """
        self.scanner_type = scanner_type
        self.cache_dir = cache_dir or Path.home() / ".voicestudio" / "vuln_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._verify_scanner_available()

    def _verify_scanner_available(self) -> None:
        """Verify that the selected scanner is available."""
        if self.scanner_type == ScannerType.PIP_AUDIT:
            if not self._is_pip_audit_available():
                logger.warning("pip-audit not found, install with: pip install pip-audit")
        elif self.scanner_type == ScannerType.GRYPE:
            if not self._is_grype_available():
                logger.warning("grype not found, install from: https://github.com/anchore/grype")

    def _is_pip_audit_available(self) -> bool:
        """Check if pip-audit is installed."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _is_grype_available(self) -> bool:
        """Check if grype is installed."""
        try:
            result = subprocess.run(
                ["grype", "version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def scan_directory(
        self,
        plugin_path: Path,
        requirements_file: Optional[str] = None,
    ) -> ScanResult:
        """
        Scan a plugin directory for vulnerabilities.

        Args:
            plugin_path: Path to plugin directory
            requirements_file: Specific requirements file to scan (default: auto-detect)

        Returns:
            ScanResult with findings
        """
        start_time = datetime.now()

        if self.scanner_type == ScannerType.PIP_AUDIT:
            result = self._scan_with_pip_audit(plugin_path, requirements_file)
        elif self.scanner_type == ScannerType.GRYPE:
            result = self._scan_with_grype(plugin_path)
        else:
            result = ScanResult(
                scanner=self.scanner_type,
                scanned_at=datetime.now().isoformat(),
                target=str(plugin_path),
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error=f"Unknown scanner type: {self.scanner_type}",
            )

        # Calculate duration
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        result.scan_duration_ms = duration_ms

        return result

    def scan_sbom(self, sbom_path: Path) -> ScanResult:
        """
        Scan an SBOM file for vulnerabilities.

        Args:
            sbom_path: Path to SBOM file (CycloneDX JSON)

        Returns:
            ScanResult with findings
        """
        start_time = datetime.now()

        if not sbom_path.exists():
            return ScanResult(
                scanner=self.scanner_type,
                scanned_at=datetime.now().isoformat(),
                target=str(sbom_path),
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error=f"SBOM file not found: {sbom_path}",
            )

        # Grype can scan SBOMs directly
        if self.scanner_type == ScannerType.GRYPE:
            result = self._scan_sbom_with_grype(sbom_path)
        else:
            # pip-audit: Extract packages from SBOM and scan
            result = self._scan_sbom_with_pip_audit(sbom_path)

        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        result.scan_duration_ms = duration_ms

        return result

    def _scan_with_pip_audit(
        self,
        plugin_path: Path,
        requirements_file: Optional[str],
    ) -> ScanResult:
        """Scan using pip-audit."""
        target = str(plugin_path)

        # Build command
        cmd = [sys.executable, "-m", "pip_audit", "--format", "json"]

        # Find requirements file
        if requirements_file:
            req_path = plugin_path / requirements_file
        else:
            # Auto-detect
            for candidate in ["requirements.txt", "requirements-prod.txt"]:
                req_path = plugin_path / candidate
                if req_path.exists():
                    break
            else:
                req_path = None

        if req_path and req_path.exists():
            cmd.extend(["-r", str(req_path)])
        else:
            # Scan installed packages
            cmd.append("--local")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=plugin_path,
            )

            vulnerabilities = []
            packages_scanned = 0

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    # pip-audit outputs a list of findings
                    if isinstance(data, dict):
                        dependencies = data.get("dependencies", [])
                    else:
                        dependencies = data

                    for dep in dependencies:
                        packages_scanned += 1
                        vulns = dep.get("vulns", [])
                        for vuln in vulns:
                            vulnerabilities.append(
                                Vulnerability(
                                    id=vuln.get("id", ""),
                                    package=dep.get("name", ""),
                                    installed_version=dep.get("version", ""),
                                    fixed_version=(
                                        vuln.get("fix_versions", [None])[0]
                                        if vuln.get("fix_versions")
                                        else None
                                    ),
                                    severity=Severity.from_string(vuln.get("severity", "unknown")),
                                    title=vuln.get("id", ""),  # pip-audit doesn't provide titles
                                    description=vuln.get("description", ""),
                                    aliases=vuln.get("aliases", []),
                                )
                            )
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse pip-audit output: {e}")

            return ScanResult(
                scanner=ScannerType.PIP_AUDIT,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=vulnerabilities,
                packages_scanned=packages_scanned,
                scan_duration_ms=0,
                success=True,
            )

        except FileNotFoundError:
            return ScanResult(
                scanner=ScannerType.PIP_AUDIT,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error="pip-audit not installed. Install with: pip install pip-audit",
            )
        except Exception as e:
            return ScanResult(
                scanner=ScannerType.PIP_AUDIT,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error=str(e),
            )

    def _scan_with_grype(self, plugin_path: Path) -> ScanResult:
        """Scan using grype."""
        target = str(plugin_path)

        cmd = ["grype", f"dir:{plugin_path}", "-o", "json"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            vulnerabilities = []
            packages_scanned = 0

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    matches = data.get("matches", [])

                    seen_packages: Set[str] = set()

                    for match in matches:
                        artifact = match.get("artifact", {})
                        vulnerability_data = match.get("vulnerability", {})

                        pkg_name = artifact.get("name", "")
                        if pkg_name not in seen_packages:
                            seen_packages.add(pkg_name)
                            packages_scanned += 1

                        cvss_data = vulnerability_data.get("cvss", [])
                        cvss_score = None
                        if cvss_data:
                            cvss_score = cvss_data[0].get("metrics", {}).get("baseScore")

                        severity = Severity.from_string(
                            vulnerability_data.get("severity", "unknown")
                        )
                        if cvss_score:
                            severity = Severity.from_cvss(cvss_score)

                        vulnerabilities.append(
                            Vulnerability(
                                id=vulnerability_data.get("id", ""),
                                package=pkg_name,
                                installed_version=artifact.get("version", ""),
                                fixed_version=(
                                    vulnerability_data.get("fix", {}).get("versions", [None])[0]
                                    if vulnerability_data.get("fix", {}).get("versions")
                                    else None
                                ),
                                severity=severity,
                                title=vulnerability_data.get("id", ""),
                                description=vulnerability_data.get("description", ""),
                                cvss_score=cvss_score,
                                references=vulnerability_data.get("urls", []),
                            )
                        )
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse grype output: {e}")

            return ScanResult(
                scanner=ScannerType.GRYPE,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=vulnerabilities,
                packages_scanned=packages_scanned,
                scan_duration_ms=0,
                success=True,
            )

        except FileNotFoundError:
            return ScanResult(
                scanner=ScannerType.GRYPE,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error="grype not installed. Install from: https://github.com/anchore/grype",
            )
        except Exception as e:
            return ScanResult(
                scanner=ScannerType.GRYPE,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error=str(e),
            )

    def _scan_sbom_with_grype(self, sbom_path: Path) -> ScanResult:
        """Scan SBOM file using grype."""
        target = str(sbom_path)

        cmd = ["grype", f"sbom:{sbom_path}", "-o", "json"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0 and "error" in result.stderr.lower():
                return ScanResult(
                    scanner=ScannerType.GRYPE,
                    scanned_at=datetime.now().isoformat(),
                    target=target,
                    vulnerabilities=[],
                    packages_scanned=0,
                    scan_duration_ms=0,
                    success=False,
                    error=result.stderr,
                )

            # Parse same as directory scan
            vulnerabilities = []
            packages_scanned = 0

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    matches = data.get("matches", [])
                    seen_packages: Set[str] = set()

                    for match in matches:
                        artifact = match.get("artifact", {})
                        vuln_data = match.get("vulnerability", {})

                        pkg_name = artifact.get("name", "")
                        if pkg_name not in seen_packages:
                            seen_packages.add(pkg_name)
                            packages_scanned += 1

                        vulnerabilities.append(
                            Vulnerability(
                                id=vuln_data.get("id", ""),
                                package=pkg_name,
                                installed_version=artifact.get("version", ""),
                                fixed_version=(
                                    vuln_data.get("fix", {}).get("versions", [None])[0]
                                    if vuln_data.get("fix", {}).get("versions")
                                    else None
                                ),
                                severity=Severity.from_string(vuln_data.get("severity", "unknown")),
                                title=vuln_data.get("id", ""),
                                description=vuln_data.get("description", ""),
                            )
                        )
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse grype SBOM output: {e}")

            return ScanResult(
                scanner=ScannerType.GRYPE,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=vulnerabilities,
                packages_scanned=packages_scanned,
                scan_duration_ms=0,
                success=True,
            )

        except FileNotFoundError:
            return ScanResult(
                scanner=ScannerType.GRYPE,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error="grype not installed",
            )
        except Exception as e:
            return ScanResult(
                scanner=ScannerType.GRYPE,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error=str(e),
            )

    def _scan_sbom_with_pip_audit(self, sbom_path: Path) -> ScanResult:
        """
        Scan SBOM using pip-audit.

        Extracts packages from SBOM and checks against PyPI Advisory Database.
        """
        import tempfile

        target = str(sbom_path)

        try:
            # Load SBOM
            sbom_data = json.loads(sbom_path.read_text())
            components = sbom_data.get("components", [])

            if not components:
                return ScanResult(
                    scanner=ScannerType.PIP_AUDIT,
                    scanned_at=datetime.now().isoformat(),
                    target=target,
                    vulnerabilities=[],
                    packages_scanned=0,
                    scan_duration_ms=0,
                    success=True,
                )

            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                delete=False,
            ) as f:
                for component in components:
                    name = component.get("name", "")
                    version = component.get("version", "")
                    if name and version:
                        f.write(f"{name}=={version}\n")
                temp_requirements = f.name

            try:
                # Run pip-audit on temp requirements
                cmd = [
                    sys.executable,
                    "-m",
                    "pip_audit",
                    "-r",
                    temp_requirements,
                    "--format",
                    "json",
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                vulnerabilities = []
                packages_scanned = len(components)

                if result.stdout:
                    data = json.loads(result.stdout)
                    if isinstance(data, dict):
                        dependencies = data.get("dependencies", [])
                    else:
                        dependencies = data

                    for dep in dependencies:
                        for vuln in dep.get("vulns", []):
                            vulnerabilities.append(
                                Vulnerability(
                                    id=vuln.get("id", ""),
                                    package=dep.get("name", ""),
                                    installed_version=dep.get("version", ""),
                                    fixed_version=(
                                        vuln.get("fix_versions", [None])[0]
                                        if vuln.get("fix_versions")
                                        else None
                                    ),
                                    severity=Severity.from_string(vuln.get("severity", "unknown")),
                                    title=vuln.get("id", ""),
                                    description=vuln.get("description", ""),
                                    aliases=vuln.get("aliases", []),
                                )
                            )

                return ScanResult(
                    scanner=ScannerType.PIP_AUDIT,
                    scanned_at=datetime.now().isoformat(),
                    target=target,
                    vulnerabilities=vulnerabilities,
                    packages_scanned=packages_scanned,
                    scan_duration_ms=0,
                    success=True,
                )

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_requirements)
                except Exception as cleanup_err:
                    # Best-effort cleanup of temp file
                    logger.debug(f"Temp file cleanup failed: {cleanup_err}")

        except Exception as e:
            return ScanResult(
                scanner=ScannerType.PIP_AUDIT,
                scanned_at=datetime.now().isoformat(),
                target=target,
                vulnerabilities=[],
                packages_scanned=0,
                scan_duration_ms=0,
                success=False,
                error=str(e),
            )


def scan_plugin(
    plugin_path: Path | str,
    scanner_type: ScannerType = ScannerType.PIP_AUDIT,
    requirements_file: Optional[str] = None,
) -> ScanResult:
    """
    Convenience function to scan a plugin for vulnerabilities.

    Args:
        plugin_path: Path to plugin directory
        scanner_type: Scanner to use
        requirements_file: Specific requirements file

    Returns:
        ScanResult with findings
    """
    scanner = VulnerabilityScanner(scanner_type=scanner_type)
    return scanner.scan_directory(Path(plugin_path), requirements_file)


def scan_sbom(
    sbom_path: Path | str,
    scanner_type: ScannerType = ScannerType.PIP_AUDIT,
) -> ScanResult:
    """
    Convenience function to scan an SBOM for vulnerabilities.

    Args:
        sbom_path: Path to SBOM file
        scanner_type: Scanner to use

    Returns:
        ScanResult with findings
    """
    scanner = VulnerabilityScanner(scanner_type=scanner_type)
    return scanner.scan_sbom(Path(sbom_path))


def check_scanner_availability() -> Dict[str, bool]:
    """
    Check which vulnerability scanners are available.

    Returns:
        Dictionary with scanner availability
    """
    scanner = VulnerabilityScanner()
    return {
        "pip-audit": scanner._is_pip_audit_available(),
        "grype": scanner._is_grype_available(),
    }
