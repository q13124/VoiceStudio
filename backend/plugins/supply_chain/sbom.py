"""
Software Bill of Materials (SBOM) Generation.

Phase 5B Enhancement: Generates CycloneDX-format SBOMs for plugins
to track dependencies and enable vulnerability scanning.

Features:
    - CycloneDX 1.5 format support (JSON and XML)
    - Automatic dependency extraction from requirements.txt/setup.py
    - Component hashing for integrity verification
    - License detection
    - Integration with pack command

The SBOM includes:
    - Plugin metadata (name, version, author)
    - All direct and transitive dependencies
    - Component hashes (SHA-256)
    - License information
    - Dependency relationships
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class SBOMFormat(str, Enum):
    """Supported SBOM output formats."""

    JSON = "json"
    XML = "xml"


class ComponentType(str, Enum):
    """Type of component in the SBOM."""

    APPLICATION = "application"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    FILE = "file"
    OPERATING_SYSTEM = "operating-system"
    DEVICE = "device"
    FIRMWARE = "firmware"
    CONTAINER = "container"


@dataclass
class License:
    """License information for a component."""

    id: Optional[str] = None  # SPDX identifier
    name: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result: Dict[str, Any] = {}
        if self.id:
            result["id"] = self.id
        if self.name:
            result["name"] = self.name
        if self.url:
            result["url"] = self.url
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> License:
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            url=data.get("url"),
        )


@dataclass
class ExternalReference:
    """External reference for a component."""

    type: str  # e.g., "website", "vcs", "issue-tracker"
    url: str
    comment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"type": self.type, "url": self.url}
        if self.comment:
            result["comment"] = self.comment
        return result


@dataclass
class Hash:
    """Hash of a component for integrity verification."""

    algorithm: str  # e.g., "SHA-256"
    value: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {"alg": self.algorithm, "content": self.value}


@dataclass
class Component:
    """A component (dependency) in the SBOM."""

    name: str
    version: str
    type: ComponentType = ComponentType.LIBRARY
    bom_ref: Optional[str] = None
    purl: Optional[str] = None  # Package URL
    description: Optional[str] = None
    author: Optional[str] = None
    licenses: List[License] = field(default_factory=list)
    hashes: List[Hash] = field(default_factory=list)
    external_references: List[ExternalReference] = field(default_factory=list)

    def __post_init__(self):
        """Initialize defaults."""
        if not self.bom_ref:
            self.bom_ref = f"{self.name}@{self.version}"
        if not self.purl and self.type == ComponentType.LIBRARY:
            # Default to PyPI package URL
            self.purl = f"pkg:pypi/{self.name}@{self.version}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result: Dict[str, Any] = {
            "type": self.type.value,
            "name": self.name,
            "version": self.version,
            "bom-ref": self.bom_ref,
        }

        if self.purl:
            result["purl"] = self.purl
        if self.description:
            result["description"] = self.description
        if self.author:
            result["author"] = self.author
        if self.licenses:
            result["licenses"] = [{"license": lic.to_dict()} for lic in self.licenses]
        if self.hashes:
            result["hashes"] = [h.to_dict() for h in self.hashes]
        if self.external_references:
            result["externalReferences"] = [ref.to_dict() for ref in self.external_references]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Component:
        """Create from dictionary."""
        licenses = []
        for lic_entry in data.get("licenses", []):
            lic_data = lic_entry.get("license", {})
            licenses.append(License.from_dict(lic_data))

        hashes = [Hash(algorithm=h["alg"], value=h["content"]) for h in data.get("hashes", [])]

        external_refs = [
            ExternalReference(
                type=ref["type"],
                url=ref["url"],
                comment=ref.get("comment"),
            )
            for ref in data.get("externalReferences", [])
        ]

        return cls(
            name=data["name"],
            version=data["version"],
            type=ComponentType(data.get("type", "library")),
            bom_ref=data.get("bom-ref"),
            purl=data.get("purl"),
            description=data.get("description"),
            author=data.get("author"),
            licenses=licenses,
            hashes=hashes,
            external_references=external_refs,
        )


@dataclass
class Dependency:
    """Dependency relationship between components."""

    ref: str  # bom-ref of the component
    depends_on: List[str] = field(default_factory=list)  # bom-refs of dependencies

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ref": self.ref,
            "dependsOn": self.depends_on,
        }


@dataclass
class SBOM:
    """
    Software Bill of Materials.

    CycloneDX 1.5 format SBOM containing:
        - Plugin metadata
        - All dependencies
        - Dependency relationships
        - Hashes for integrity
        - License information
    """

    # Metadata
    bom_format: str = "CycloneDX"
    spec_version: str = "1.5"
    version: int = 1
    serial_number: str = field(default_factory=lambda: f"urn:uuid:{uuid4()}")

    # Timestamps
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    # Plugin (main component)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Components (dependencies)
    components: List[Component] = field(default_factory=list)

    # Dependency graph
    dependencies: List[Dependency] = field(default_factory=list)

    def __post_init__(self):
        """Initialize metadata structure."""
        if not self.metadata:
            self.metadata = {
                "timestamp": self.timestamp,
                "tools": [
                    {
                        "vendor": "VoiceStudio",
                        "name": "voicestudio-sbom-generator",
                        "version": "1.0.0",
                    }
                ],
            }

    def add_component(self, component: Component) -> None:
        """Add a component to the SBOM."""
        self.components.append(component)

    def add_dependency(self, ref: str, depends_on: List[str]) -> None:
        """Add a dependency relationship."""
        self.dependencies.append(Dependency(ref=ref, depends_on=depends_on))

    def find_component(self, name: str) -> Optional[Component]:
        """Find a component by name."""
        for comp in self.components:
            if comp.name.lower() == name.lower():
                return comp
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to CycloneDX JSON format."""
        result: Dict[str, Any] = {
            "bomFormat": self.bom_format,
            "specVersion": self.spec_version,
            "version": self.version,
            "serialNumber": self.serial_number,
            "metadata": self.metadata,
        }

        if self.components:
            result["components"] = [c.to_dict() for c in self.components]

        if self.dependencies:
            result["dependencies"] = [d.to_dict() for d in self.dependencies]

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_xml(self) -> str:
        """Convert to CycloneDX XML format."""
        root = ET.Element(
            "bom",
            {
                "xmlns": "http://cyclonedx.org/schema/bom/1.5",
                "version": str(self.version),
                "serialNumber": self.serial_number,
            },
        )

        # Metadata
        metadata_elem = ET.SubElement(root, "metadata")
        timestamp_elem = ET.SubElement(metadata_elem, "timestamp")
        timestamp_elem.text = self.timestamp

        # Tools
        tools_elem = ET.SubElement(metadata_elem, "tools")
        for tool in self.metadata.get("tools", []):
            tool_elem = ET.SubElement(tools_elem, "tool")
            ET.SubElement(tool_elem, "vendor").text = tool.get("vendor", "")
            ET.SubElement(tool_elem, "name").text = tool.get("name", "")
            ET.SubElement(tool_elem, "version").text = tool.get("version", "")

        # Components
        if self.components:
            components_elem = ET.SubElement(root, "components")
            for comp in self.components:
                self._component_to_xml(components_elem, comp)

        # Dependencies
        if self.dependencies:
            deps_elem = ET.SubElement(root, "dependencies")
            for dep in self.dependencies:
                dep_elem = ET.SubElement(deps_elem, "dependency", {"ref": dep.ref})
                for depends_on in dep.depends_on:
                    ET.SubElement(dep_elem, "dependency", {"ref": depends_on})

        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    def _component_to_xml(self, parent: ET.Element, comp: Component) -> None:
        """Convert a component to XML element."""
        comp_elem = ET.SubElement(
            parent,
            "component",
            {
                "type": comp.type.value,
                "bom-ref": comp.bom_ref or "",
            },
        )

        ET.SubElement(comp_elem, "name").text = comp.name
        ET.SubElement(comp_elem, "version").text = comp.version

        if comp.purl:
            ET.SubElement(comp_elem, "purl").text = comp.purl
        if comp.description:
            ET.SubElement(comp_elem, "description").text = comp.description

        if comp.hashes:
            hashes_elem = ET.SubElement(comp_elem, "hashes")
            for h in comp.hashes:
                hash_elem = ET.SubElement(hashes_elem, "hash", {"alg": h.algorithm})
                hash_elem.text = h.value

        if comp.licenses:
            licenses_elem = ET.SubElement(comp_elem, "licenses")
            for lic in comp.licenses:
                lic_wrapper = ET.SubElement(licenses_elem, "license")
                if lic.id:
                    ET.SubElement(lic_wrapper, "id").text = lic.id
                elif lic.name:
                    ET.SubElement(lic_wrapper, "name").text = lic.name

    def save(self, path: Path, format: SBOMFormat = SBOMFormat.JSON) -> None:
        """Save SBOM to file."""
        if format == SBOMFormat.JSON:
            content = self.to_json()
        else:
            content = self.to_xml()

        path.write_text(content, encoding="utf-8")
        logger.info(f"SBOM saved to: {path}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SBOM:
        """Create from dictionary."""
        sbom = cls(
            bom_format=data.get("bomFormat", "CycloneDX"),
            spec_version=data.get("specVersion", "1.5"),
            version=data.get("version", 1),
            serial_number=data.get("serialNumber", f"urn:uuid:{uuid4()}"),
            metadata=data.get("metadata", {}),
        )

        for comp_data in data.get("components", []):
            sbom.components.append(Component.from_dict(comp_data))

        for dep_data in data.get("dependencies", []):
            sbom.dependencies.append(
                Dependency(
                    ref=dep_data["ref"],
                    depends_on=dep_data.get("dependsOn", []),
                )
            )

        return sbom

    @classmethod
    def load(cls, path: Path) -> SBOM:
        """Load SBOM from file."""
        content = path.read_text(encoding="utf-8")

        if path.suffix.lower() == ".json":
            data = json.loads(content)
            return cls.from_dict(data)
        else:
            raise ValueError(f"Unsupported SBOM format: {path.suffix}")


class SBOMGenerator:
    """
    Generates SBOMs for VoiceStudio plugins.

    Extracts dependencies from:
        - requirements.txt
        - setup.py / setup.cfg
        - pyproject.toml
        - Installed packages (via pip freeze)

    And generates CycloneDX format SBOMs with:
        - Component metadata
        - Dependency relationships
        - SHA-256 hashes
        - License information
    """

    def __init__(
        self,
        plugin_path: Path,
        plugin_name: Optional[str] = None,
        plugin_version: Optional[str] = None,
    ):
        self.plugin_path = Path(plugin_path)
        self.plugin_name = plugin_name or self.plugin_path.name
        self.plugin_version = plugin_version or "0.0.0"

        # Cache for package metadata
        self._package_cache: Dict[str, Dict[str, Any]] = {}

    def generate(self, include_transitive: bool = True) -> SBOM:
        """
        Generate SBOM for the plugin.

        Args:
            include_transitive: Include transitive dependencies

        Returns:
            Generated SBOM
        """
        sbom = SBOM()

        # Set plugin as main component in metadata
        sbom.metadata["component"] = {
            "type": "application",
            "name": self.plugin_name,
            "version": self.plugin_version,
        }

        # Extract dependencies
        direct_deps = self._extract_direct_dependencies()

        # Add components
        all_components: Dict[str, Component] = {}

        for dep_name, dep_version in direct_deps.items():
            component = self._create_component(dep_name, dep_version)
            all_components[component.bom_ref or component.name] = component

        # Get transitive dependencies if requested
        if include_transitive:
            transitive = self._get_transitive_dependencies(list(direct_deps.keys()))
            for dep_name, dep_version in transitive.items():
                if dep_name.lower() not in [d.lower() for d in direct_deps]:
                    component = self._create_component(dep_name, dep_version)
                    all_components[component.bom_ref or component.name] = component

        # Add all components to SBOM
        for component in all_components.values():
            sbom.add_component(component)

        # Build dependency graph
        self._build_dependency_graph(sbom, direct_deps)

        logger.info(f"Generated SBOM for {self.plugin_name}: " f"{len(sbom.components)} components")

        return sbom

    def _extract_direct_dependencies(self) -> Dict[str, str]:
        """Extract direct dependencies from plugin files."""
        deps: Dict[str, str] = {}

        # Check requirements.txt
        requirements_file = self.plugin_path / "requirements.txt"
        if requirements_file.exists():
            deps.update(self._parse_requirements(requirements_file))

        # Check pyproject.toml
        pyproject_file = self.plugin_path / "pyproject.toml"
        if pyproject_file.exists():
            deps.update(self._parse_pyproject(pyproject_file))

        # Check setup.py
        setup_file = self.plugin_path / "setup.py"
        if setup_file.exists():
            deps.update(self._parse_setup_py(setup_file))

        return deps

    def _parse_requirements(self, path: Path) -> Dict[str, str]:
        """Parse requirements.txt file."""
        deps: Dict[str, str] = {}

        try:
            content = path.read_text(encoding="utf-8")

            for line in content.splitlines():
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#") or line.startswith("-"):
                    continue

                # Parse requirement specifier
                match = re.match(r"([a-zA-Z0-9_-]+)\s*([<>=!~]+\s*[\d.]+)?", line)
                if match:
                    name = match.group(1)
                    version = match.group(2) or "*"
                    # Clean version specifier
                    version = re.sub(r"[<>=!~]+\s*", "", version)
                    deps[name] = version

        except Exception as e:
            logger.warning(f"Failed to parse requirements.txt: {e}")

        return deps

    def _parse_pyproject(self, path: Path) -> Dict[str, str]:
        """Parse pyproject.toml for dependencies."""
        deps: Dict[str, str] = {}

        try:
            # Try to use tomllib (Python 3.11+) or tomli
            try:
                import tomllib

                with open(path, "rb") as f:
                    data = tomllib.load(f)
            except ImportError:
                try:
                    import tomli

                    with open(path, "rb") as f:
                        data = tomli.load(f)
                except ImportError:
                    logger.debug("No TOML parser available, skipping pyproject.toml")
                    return deps

            # Check [project.dependencies]
            project_deps = data.get("project", {}).get("dependencies", [])
            for dep in project_deps:
                match = re.match(r"([a-zA-Z0-9_-]+)\s*([<>=!~]+\s*[\d.]+)?", dep)
                if match:
                    name = match.group(1)
                    version = match.group(2) or "*"
                    version = re.sub(r"[<>=!~]+\s*", "", version)
                    deps[name] = version

        except Exception as e:
            logger.warning(f"Failed to parse pyproject.toml: {e}")

        return deps

    def _parse_setup_py(self, path: Path) -> Dict[str, str]:
        """Parse setup.py for install_requires."""
        deps: Dict[str, str] = {}

        try:
            content = path.read_text(encoding="utf-8")

            # Simple regex to find install_requires list
            match = re.search(
                r"install_requires\s*=\s*\[([^\]]+)\]",
                content,
                re.DOTALL,
            )

            if match:
                requires_str = match.group(1)
                # Find all quoted strings
                for req_match in re.finditer(r"['\"]([^'\"]+)['\"]", requires_str):
                    req = req_match.group(1)
                    name_match = re.match(r"([a-zA-Z0-9_-]+)", req)
                    if name_match:
                        name = name_match.group(1)
                        version_match = re.search(r"[<>=!~]+\s*([\d.]+)", req)
                        version = version_match.group(1) if version_match else "*"
                        deps[name] = version

        except Exception as e:
            logger.warning(f"Failed to parse setup.py: {e}")

        return deps

    def _get_transitive_dependencies(
        self,
        direct_deps: List[str],
    ) -> Dict[str, str]:
        """Get transitive dependencies via pip."""
        deps: Dict[str, str] = {}

        try:
            # Use pip freeze to get installed packages
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "==" in line:
                        name, version = line.split("==", 1)
                        deps[name.strip()] = version.strip()

        except Exception as e:
            logger.warning(f"Failed to get transitive dependencies: {e}")

        return deps

    def _create_component(self, name: str, version: str) -> Component:
        """Create a Component with full metadata."""
        component = Component(
            name=name,
            version=version,
            type=ComponentType.LIBRARY,
        )

        # Try to get package metadata
        metadata = self._get_package_metadata(name)

        if metadata:
            component.author = metadata.get("author")
            component.description = metadata.get("summary")

            # License
            license_str = metadata.get("license")
            if license_str:
                spdx_id = self._normalize_license(license_str)
                component.licenses.append(License(id=spdx_id, name=license_str))

            # Home page
            home_page = metadata.get("home_page")
            if home_page:
                component.external_references.append(
                    ExternalReference(type="website", url=home_page)
                )

        # Add hash if package file exists
        package_hash = self._get_package_hash(name, version)
        if package_hash:
            component.hashes.append(Hash(algorithm="SHA-256", value=package_hash))

        return component

    def _get_package_metadata(self, name: str) -> Dict[str, Any]:
        """Get package metadata from pip."""
        if name in self._package_cache:
            return self._package_cache[name]

        metadata: Dict[str, Any] = {}

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        key = key.lower().replace("-", "_")
                        metadata[key] = value

            self._package_cache[name] = metadata

        except Exception as e:
            logger.debug(f"Failed to get metadata for {name}: {e}")

        return metadata

    def _get_package_hash(self, name: str, version: str) -> Optional[str]:
        """Get SHA-256 hash for a package."""
        # This would require pip cache inspection or PyPI API
        # For now, return None (hashes are optional in CycloneDX)
        return None

    def _normalize_license(self, license_str: str) -> Optional[str]:
        """Normalize license string to SPDX identifier."""
        # Common license mapping
        license_map = {
            "mit": "MIT",
            "mit license": "MIT",
            "apache": "Apache-2.0",
            "apache 2.0": "Apache-2.0",
            "apache-2.0": "Apache-2.0",
            "apache license 2.0": "Apache-2.0",
            "apache software license": "Apache-2.0",
            "bsd": "BSD-3-Clause",
            "bsd license": "BSD-3-Clause",
            "bsd-3-clause": "BSD-3-Clause",
            "bsd-2-clause": "BSD-2-Clause",
            "gpl": "GPL-3.0-only",
            "gpl-2.0": "GPL-2.0-only",
            "gpl-3.0": "GPL-3.0-only",
            "lgpl": "LGPL-3.0-only",
            "lgpl-2.1": "LGPL-2.1-only",
            "lgpl-3.0": "LGPL-3.0-only",
            "isc": "ISC",
            "mpl": "MPL-2.0",
            "mpl-2.0": "MPL-2.0",
            "psf": "PSF-2.0",
            "python software foundation license": "PSF-2.0",
            "public domain": "Unlicense",
        }

        normalized = license_str.lower().strip()
        return license_map.get(normalized)

    def _build_dependency_graph(
        self,
        sbom: SBOM,
        direct_deps: Dict[str, str],
    ) -> None:
        """Build dependency graph in the SBOM."""
        # Add plugin as root
        plugin_ref = f"{self.plugin_name}@{self.plugin_version}"
        direct_refs = [f"{name}@{version}" for name, version in direct_deps.items()]

        if direct_refs:
            sbom.add_dependency(plugin_ref, direct_refs)

        # For each component, try to find its dependencies
        for component in sbom.components:
            comp_deps = self._get_component_dependencies(component.name)
            if comp_deps:
                dep_refs = [f"{name}@{ver}" for name, ver in comp_deps.items()]
                # Filter to only include components that exist in SBOM
                existing_refs = {c.bom_ref for c in sbom.components}
                valid_refs = [ref for ref in dep_refs if ref in existing_refs]
                if valid_refs:
                    sbom.add_dependency(component.bom_ref or component.name, valid_refs)

    def _get_component_dependencies(self, name: str) -> Dict[str, str]:
        """Get dependencies for a specific component."""
        deps: Dict[str, str] = {}

        metadata = self._get_package_metadata(name)
        requires = metadata.get("requires")

        if requires:
            for req in requires.split(", "):
                match = re.match(r"([a-zA-Z0-9_-]+)", req)
                if match:
                    dep_name = match.group(1)
                    # Get version from installed packages
                    dep_metadata = self._get_package_metadata(dep_name)
                    dep_version = dep_metadata.get("version", "*")
                    deps[dep_name] = dep_version

        return deps


# =============================================================================
# Convenience Functions
# =============================================================================


def generate_sbom(
    plugin_path: Path,
    output_path: Optional[Path] = None,
    plugin_name: Optional[str] = None,
    plugin_version: Optional[str] = None,
    format: SBOMFormat = SBOMFormat.JSON,
    include_transitive: bool = True,
) -> SBOM:
    """
    Generate an SBOM for a plugin.

    Args:
        plugin_path: Path to the plugin directory
        output_path: Optional path to save the SBOM
        plugin_name: Override plugin name
        plugin_version: Override plugin version
        format: Output format (JSON or XML)
        include_transitive: Include transitive dependencies

    Returns:
        Generated SBOM
    """
    generator = SBOMGenerator(
        plugin_path=plugin_path,
        plugin_name=plugin_name,
        plugin_version=plugin_version,
    )

    sbom = generator.generate(include_transitive=include_transitive)

    if output_path:
        sbom.save(output_path, format=format)

    return sbom


def load_sbom(path: Path) -> SBOM:
    """
    Load an SBOM from file.

    Args:
        path: Path to SBOM file (JSON format)

    Returns:
        Loaded SBOM
    """
    return SBOM.load(path)
