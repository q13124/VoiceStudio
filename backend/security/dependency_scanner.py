"""
Dependency Security Scanner.

Task 2.3.1: CVE vulnerability scanning.
Task 2.3.2: SBOM generation.
Task 2.3.4: License compliance.
Scans dependencies for security issues and compliance.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class LicenseRisk(Enum):
    """License risk categories."""
    PERMISSIVE = "permissive"  # MIT, Apache, BSD
    WEAK_COPYLEFT = "weak_copyleft"  # LGPL
    STRONG_COPYLEFT = "strong_copyleft"  # GPL
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"


@dataclass
class Vulnerability:
    """A security vulnerability."""
    id: str  # CVE ID
    package: str
    installed_version: str
    fixed_version: str | None
    severity: Severity
    description: str
    url: str | None = None


@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    version: str
    license: str
    license_risk: LicenseRisk
    homepage: str | None = None
    vulnerabilities: list[Vulnerability] = field(default_factory=list)


@dataclass
class ScanResult:
    """Result of a dependency scan."""
    scanned_at: datetime
    total_packages: int
    vulnerabilities: list[Vulnerability]
    dependencies: list[DependencyInfo]

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == Severity.HIGH)

    @property
    def is_clean(self) -> bool:
        return self.critical_count == 0 and self.high_count == 0


@dataclass
class SBOM:
    """Software Bill of Materials."""
    format: str = "CycloneDX"
    version: str = "1.4"
    generated_at: datetime = field(default_factory=datetime.now)
    components: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        """Export SBOM as JSON."""
        return json.dumps({
            "bomFormat": self.format,
            "specVersion": self.version,
            "version": 1,
            "metadata": {
                "timestamp": self.generated_at.isoformat(),
                "component": {
                    "name": "VoiceStudio",
                    "type": "application",
                },
            },
            "components": self.components,
        }, indent=2)


class DependencyScanner:
    """
    Scans dependencies for security vulnerabilities and compliance.

    Features:
    - CVE vulnerability scanning
    - SBOM generation (CycloneDX format)
    - License compliance checking
    - Automated update recommendations
    """

    # License classifications
    PERMISSIVE_LICENSES = {
        "MIT", "Apache-2.0", "Apache 2.0", "BSD-3-Clause", "BSD-2-Clause",
        "ISC", "Unlicense", "0BSD", "CC0-1.0", "WTFPL",
    }

    WEAK_COPYLEFT_LICENSES = {
        "LGPL-2.1", "LGPL-3.0", "LGPL-2.0", "MPL-2.0", "EPL-2.0",
    }

    STRONG_COPYLEFT_LICENSES = {
        "GPL-2.0", "GPL-3.0", "AGPL-3.0", "GPL-2.0-only", "GPL-3.0-only",
    }

    # Allowed licenses for VoiceStudio
    ALLOWED_LICENSES: set[str] = PERMISSIVE_LICENSES | WEAK_COPYLEFT_LICENSES

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    async def scan_python(self) -> ScanResult:
        """Scan Python dependencies for vulnerabilities."""
        vulnerabilities: list[Vulnerability] = []
        dependencies: list[DependencyInfo] = []

        # Get installed packages
        packages = await self._get_python_packages()

        # Check each package
        for pkg in packages:
            dep_info = DependencyInfo(
                name=pkg["name"],
                version=pkg["version"],
                license=pkg.get("license", "UNKNOWN"),
                license_risk=self._classify_license(pkg.get("license", "")),
                homepage=pkg.get("homepage"),
            )

            # Check for vulnerabilities using pip-audit or safety
            pkg_vulns = await self._check_vulnerabilities(pkg["name"], pkg["version"])
            dep_info.vulnerabilities = pkg_vulns
            vulnerabilities.extend(pkg_vulns)

            dependencies.append(dep_info)

        return ScanResult(
            scanned_at=datetime.now(),
            total_packages=len(packages),
            vulnerabilities=vulnerabilities,
            dependencies=dependencies,
        )

    async def _get_python_packages(self) -> list[dict[str, Any]]:
        """Get list of installed Python packages."""
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"pip list failed: {result.stderr}")
                return []

            packages = json.loads(result.stdout)

            # Get additional info for each package
            detailed = []
            for pkg in packages:
                info = await self._get_package_info(pkg["name"])
                detailed.append({
                    "name": pkg["name"],
                    "version": pkg["version"],
                    **info,
                })

            return detailed

        except Exception as e:
            logger.error(f"Failed to get packages: {e}")
            return []

    async def _get_package_info(self, package_name: str) -> dict[str, Any]:
        """Get detailed info about a package."""
        try:
            result = subprocess.run(
                ["pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            info = {}
            for line in result.stdout.split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    key = key.lower().replace("-", "_")
                    info[key] = value.strip()

            return info

        except Exception:
            return {}

    async def _check_vulnerabilities(
        self,
        package: str,
        version: str,
    ) -> list[Vulnerability]:
        """Check a package for known vulnerabilities."""
        vulns = []

        # Try pip-audit first
        try:
            result = subprocess.run(
                ["pip-audit", "--format=json", "--progress-spinner=off"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)

                for item in data.get("dependencies", []):
                    if item.get("name", "").lower() == package.lower():
                        for vuln in item.get("vulns", []):
                            vulns.append(Vulnerability(
                                id=vuln.get("id", "UNKNOWN"),
                                package=package,
                                installed_version=version,
                                fixed_version=vuln.get("fix_versions", [None])[0],
                                severity=self._parse_severity(vuln.get("severity", "UNKNOWN")),
                                description=vuln.get("description", ""),
                                url=vuln.get("url"),
                            ))
                        break

        except FileNotFoundError:
            logger.debug("pip-audit not available")
        except Exception as e:
            logger.debug(f"pip-audit failed: {e}")

        return vulns

    def _parse_severity(self, severity: str) -> Severity:
        """Parse severity string to enum."""
        severity = severity.upper()
        if severity == "CRITICAL":
            return Severity.CRITICAL
        elif severity == "HIGH":
            return Severity.HIGH
        elif severity == "MEDIUM":
            return Severity.MEDIUM
        elif severity == "LOW":
            return Severity.LOW
        return Severity.UNKNOWN

    def _classify_license(self, license_str: str) -> LicenseRisk:
        """Classify a license by risk level."""
        if not license_str:
            return LicenseRisk.UNKNOWN

        license_upper = license_str.upper()

        for lic in self.PERMISSIVE_LICENSES:
            if lic.upper() in license_upper:
                return LicenseRisk.PERMISSIVE

        for lic in self.WEAK_COPYLEFT_LICENSES:
            if lic.upper() in license_upper:
                return LicenseRisk.WEAK_COPYLEFT

        for lic in self.STRONG_COPYLEFT_LICENSES:
            if lic.upper() in license_upper:
                return LicenseRisk.STRONG_COPYLEFT

        return LicenseRisk.UNKNOWN

    async def generate_sbom(self) -> SBOM:
        """Generate a Software Bill of Materials."""
        sbom = SBOM()

        packages = await self._get_python_packages()

        for pkg in packages:
            sbom.components.append({
                "type": "library",
                "name": pkg["name"],
                "version": pkg["version"],
                "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}",
                "licenses": [{"license": {"id": pkg.get("license", "UNKNOWN")}}],
            })

        return sbom

    async def check_license_compliance(self) -> list[DependencyInfo]:
        """Check for license compliance issues."""
        scan_result = await self.scan_python()

        issues = []
        for dep in scan_result.dependencies:
            if dep.license_risk == LicenseRisk.STRONG_COPYLEFT:
                issues.append(dep)
            elif dep.license_risk == LicenseRisk.UNKNOWN:
                # Unknown licenses need review
                issues.append(dep)

        return issues

    async def get_update_recommendations(self) -> list[dict[str, Any]]:
        """Get recommended package updates."""
        recommendations = []

        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                outdated = json.loads(result.stdout)

                for pkg in outdated:
                    recommendations.append({
                        "package": pkg["name"],
                        "current": pkg["version"],
                        "latest": pkg["latest_version"],
                        "type": pkg.get("latest_filetype", "unknown"),
                    })

        except Exception as e:
            logger.error(f"Failed to check outdated packages: {e}")

        return recommendations


# Global scanner
_scanner: DependencyScanner | None = None


def get_dependency_scanner() -> DependencyScanner:
    """Get or create the global dependency scanner."""
    global _scanner
    if _scanner is None:
        _scanner = DependencyScanner()
    return _scanner
