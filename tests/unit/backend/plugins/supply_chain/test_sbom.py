"""
Unit tests for SBOM (Software Bill of Materials) generation.

Tests the SBOM, SBOMGenerator, Component, and related classes
for CycloneDX-format SBOM generation.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.supply_chain.sbom import (
    SBOM,
    Component,
    ComponentType,
    Dependency,
    ExternalReference,
    Hash,
    License,
    SBOMFormat,
    SBOMGenerator,
    generate_sbom,
    load_sbom,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a temporary plugin directory."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    return plugin_dir


@pytest.fixture
def plugin_with_requirements(temp_plugin_dir):
    """Create a plugin with requirements.txt."""
    requirements = """
# Main dependencies
requests>=2.28.0
pydantic==2.0.0
fastapi~=0.100.0

# Dev dependencies
pytest
"""
    (temp_plugin_dir / "requirements.txt").write_text(requirements)
    return temp_plugin_dir


@pytest.fixture
def plugin_with_pyproject(temp_plugin_dir):
    """Create a plugin with pyproject.toml."""
    pyproject = """
[project]
name = "test-plugin"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
    "pydantic==2.0.0",
]
"""
    (temp_plugin_dir / "pyproject.toml").write_text(pyproject)
    return temp_plugin_dir


@pytest.fixture
def basic_component():
    """Create a basic component."""
    return Component(
        name="requests",
        version="2.28.0",
        type=ComponentType.LIBRARY,
    )


@pytest.fixture
def basic_sbom():
    """Create a basic SBOM."""
    return SBOM()


# =============================================================================
# Test License
# =============================================================================


class TestLicense:
    """Tests for License dataclass."""

    def test_basic_creation(self):
        """Test creating a basic license."""
        license = License(id="MIT")
        assert license.id == "MIT"
        assert license.name is None

    def test_with_all_fields(self):
        """Test license with all fields."""
        license = License(
            id="Apache-2.0",
            name="Apache License 2.0",
            url="https://www.apache.org/licenses/LICENSE-2.0",
        )
        assert license.id == "Apache-2.0"
        assert license.name == "Apache License 2.0"
        assert license.url is not None

    def test_to_dict(self):
        """Test converting license to dictionary."""
        license = License(id="MIT", name="MIT License")
        data = license.to_dict()

        assert data["id"] == "MIT"
        assert data["name"] == "MIT License"

    def test_from_dict(self):
        """Test creating license from dictionary."""
        data = {"id": "MIT", "name": "MIT License"}
        license = License.from_dict(data)

        assert license.id == "MIT"
        assert license.name == "MIT License"


# =============================================================================
# Test Component
# =============================================================================


class TestComponent:
    """Tests for Component dataclass."""

    def test_basic_creation(self):
        """Test creating a basic component."""
        comp = Component(name="requests", version="2.28.0")

        assert comp.name == "requests"
        assert comp.version == "2.28.0"
        assert comp.type == ComponentType.LIBRARY

    def test_auto_bom_ref(self):
        """Test automatic bom-ref generation."""
        comp = Component(name="requests", version="2.28.0")

        assert comp.bom_ref == "requests@2.28.0"

    def test_auto_purl(self):
        """Test automatic PURL generation."""
        comp = Component(name="requests", version="2.28.0")

        assert comp.purl == "pkg:pypi/requests@2.28.0"

    def test_custom_bom_ref(self):
        """Test custom bom-ref."""
        comp = Component(
            name="requests",
            version="2.28.0",
            bom_ref="custom-ref",
        )

        assert comp.bom_ref == "custom-ref"

    def test_with_licenses(self):
        """Test component with licenses."""
        comp = Component(
            name="requests",
            version="2.28.0",
            licenses=[License(id="Apache-2.0")],
        )

        assert len(comp.licenses) == 1
        assert comp.licenses[0].id == "Apache-2.0"

    def test_with_hashes(self):
        """Test component with hashes."""
        comp = Component(
            name="requests",
            version="2.28.0",
            hashes=[Hash(algorithm="SHA-256", value="abc123")],
        )

        assert len(comp.hashes) == 1
        assert comp.hashes[0].algorithm == "SHA-256"

    def test_to_dict(self, basic_component):
        """Test converting component to dictionary."""
        data = basic_component.to_dict()

        assert data["name"] == "requests"
        assert data["version"] == "2.28.0"
        assert data["type"] == "library"
        assert data["bom-ref"] == "requests@2.28.0"
        assert "purl" in data

    def test_from_dict(self):
        """Test creating component from dictionary."""
        data = {
            "name": "requests",
            "version": "2.28.0",
            "type": "library",
            "bom-ref": "requests@2.28.0",
            "purl": "pkg:pypi/requests@2.28.0",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "hashes": [{"alg": "SHA-256", "content": "abc123"}],
        }

        comp = Component.from_dict(data)

        assert comp.name == "requests"
        assert comp.version == "2.28.0"
        assert len(comp.licenses) == 1
        assert len(comp.hashes) == 1


# =============================================================================
# Test Dependency
# =============================================================================


class TestDependency:
    """Tests for Dependency dataclass."""

    def test_basic_creation(self):
        """Test creating a basic dependency."""
        dep = Dependency(ref="requests@2.28.0")

        assert dep.ref == "requests@2.28.0"
        assert dep.depends_on == []

    def test_with_dependencies(self):
        """Test dependency with dependsOn list."""
        dep = Dependency(
            ref="requests@2.28.0",
            depends_on=["urllib3@2.0.0", "certifi@2023.7.0"],
        )

        assert len(dep.depends_on) == 2

    def test_to_dict(self):
        """Test converting dependency to dictionary."""
        dep = Dependency(
            ref="requests@2.28.0",
            depends_on=["urllib3@2.0.0"],
        )

        data = dep.to_dict()

        assert data["ref"] == "requests@2.28.0"
        assert data["dependsOn"] == ["urllib3@2.0.0"]


# =============================================================================
# Test SBOM
# =============================================================================


class TestSBOM:
    """Tests for SBOM class."""

    def test_basic_creation(self, basic_sbom):
        """Test creating a basic SBOM."""
        assert basic_sbom.bom_format == "CycloneDX"
        assert basic_sbom.spec_version == "1.5"
        assert basic_sbom.version == 1
        assert basic_sbom.serial_number.startswith("urn:uuid:")

    def test_add_component(self, basic_sbom, basic_component):
        """Test adding a component."""
        basic_sbom.add_component(basic_component)

        assert len(basic_sbom.components) == 1
        assert basic_sbom.components[0].name == "requests"

    def test_add_dependency(self, basic_sbom):
        """Test adding a dependency."""
        basic_sbom.add_dependency("app@1.0.0", ["requests@2.28.0"])

        assert len(basic_sbom.dependencies) == 1
        assert basic_sbom.dependencies[0].ref == "app@1.0.0"

    def test_find_component(self, basic_sbom, basic_component):
        """Test finding a component by name."""
        basic_sbom.add_component(basic_component)

        found = basic_sbom.find_component("requests")
        assert found is not None
        assert found.name == "requests"

        not_found = basic_sbom.find_component("nonexistent")
        assert not_found is None

    def test_to_dict(self, basic_sbom, basic_component):
        """Test converting SBOM to dictionary."""
        basic_sbom.add_component(basic_component)
        data = basic_sbom.to_dict()

        assert data["bomFormat"] == "CycloneDX"
        assert data["specVersion"] == "1.5"
        assert "components" in data
        assert len(data["components"]) == 1

    def test_to_json(self, basic_sbom, basic_component):
        """Test converting SBOM to JSON."""
        basic_sbom.add_component(basic_component)
        json_str = basic_sbom.to_json()

        # Parse to verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["bomFormat"] == "CycloneDX"

    def test_to_xml(self, basic_sbom, basic_component):
        """Test converting SBOM to XML."""
        basic_sbom.add_component(basic_component)
        xml_str = basic_sbom.to_xml()

        assert "<?xml version" in xml_str
        assert "cyclonedx.org" in xml_str
        assert "requests" in xml_str

    def test_save_json(self, basic_sbom, basic_component, tmp_path):
        """Test saving SBOM to JSON file."""
        basic_sbom.add_component(basic_component)
        output_path = tmp_path / "sbom.json"

        basic_sbom.save(output_path, SBOMFormat.JSON)

        assert output_path.exists()
        content = json.loads(output_path.read_text())
        assert content["bomFormat"] == "CycloneDX"

    def test_save_xml(self, basic_sbom, basic_component, tmp_path):
        """Test saving SBOM to XML file."""
        basic_sbom.add_component(basic_component)
        output_path = tmp_path / "sbom.xml"

        basic_sbom.save(output_path, SBOMFormat.XML)

        assert output_path.exists()
        content = output_path.read_text()
        assert "cyclonedx" in content.lower()

    def test_from_dict(self, basic_sbom, basic_component):
        """Test creating SBOM from dictionary."""
        basic_sbom.add_component(basic_component)
        basic_sbom.add_dependency("app@1.0.0", ["requests@2.28.0"])

        data = basic_sbom.to_dict()
        restored = SBOM.from_dict(data)

        assert restored.bom_format == "CycloneDX"
        assert len(restored.components) == 1
        assert len(restored.dependencies) == 1

    def test_load(self, basic_sbom, basic_component, tmp_path):
        """Test loading SBOM from file."""
        basic_sbom.add_component(basic_component)
        output_path = tmp_path / "sbom.json"
        basic_sbom.save(output_path, SBOMFormat.JSON)

        loaded = SBOM.load(output_path)

        assert loaded.bom_format == "CycloneDX"
        assert len(loaded.components) == 1


# =============================================================================
# Test SBOMGenerator
# =============================================================================


class TestSBOMGenerator:
    """Tests for SBOMGenerator class."""

    def test_basic_creation(self, temp_plugin_dir):
        """Test creating a generator."""
        generator = SBOMGenerator(
            plugin_path=temp_plugin_dir,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
        )

        assert generator.plugin_name == "test-plugin"
        assert generator.plugin_version == "1.0.0"

    def test_default_name_from_path(self, temp_plugin_dir):
        """Test that plugin name defaults to directory name."""
        generator = SBOMGenerator(plugin_path=temp_plugin_dir)

        assert generator.plugin_name == "test_plugin"

    def test_parse_requirements(self, plugin_with_requirements):
        """Test parsing requirements.txt."""
        generator = SBOMGenerator(plugin_path=plugin_with_requirements)
        deps = generator._extract_direct_dependencies()

        assert "requests" in deps
        assert "pydantic" in deps
        assert "fastapi" in deps
        assert "pytest" in deps

    @patch("backend.plugins.supply_chain.sbom.subprocess.run")
    def test_generate_basic(self, mock_run, plugin_with_requirements):
        """Test generating a basic SBOM."""
        # Mock pip freeze output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="requests==2.28.0\npydantic==2.0.0\nfastapi==0.100.0\n",
        )

        generator = SBOMGenerator(
            plugin_path=plugin_with_requirements,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
        )

        sbom = generator.generate(include_transitive=False)

        assert sbom.bom_format == "CycloneDX"
        assert len(sbom.components) > 0

    @patch("backend.plugins.supply_chain.sbom.subprocess.run")
    def test_generate_with_transitive(self, mock_run, plugin_with_requirements):
        """Test generating SBOM with transitive dependencies."""

        # Mock pip freeze and pip show
        def run_side_effect(*args, **kwargs):
            cmd = args[0]
            result = MagicMock()

            if "freeze" in cmd:
                result.returncode = 0
                result.stdout = "requests==2.28.0\n" "urllib3==2.0.0\n" "certifi==2023.7.0\n"
            elif "show" in cmd:
                result.returncode = 0
                result.stdout = "Name: test\n" "Version: 1.0.0\n" "License: MIT\n"
            else:
                result.returncode = 1
                result.stdout = ""

            return result

        mock_run.side_effect = run_side_effect

        generator = SBOMGenerator(
            plugin_path=plugin_with_requirements,
            plugin_name="test-plugin",
            plugin_version="1.0.0",
        )

        sbom = generator.generate(include_transitive=True)

        # Should include both direct and transitive deps
        assert len(sbom.components) >= 3  # requests, urllib3, certifi


class TestSBOMGeneratorLicenseNormalization:
    """Tests for license normalization."""

    def test_normalize_mit(self, temp_plugin_dir):
        """Test normalizing MIT license."""
        generator = SBOMGenerator(plugin_path=temp_plugin_dir)

        assert generator._normalize_license("MIT") == "MIT"
        assert generator._normalize_license("mit license") == "MIT"
        assert generator._normalize_license("Mit") == "MIT"

    def test_normalize_apache(self, temp_plugin_dir):
        """Test normalizing Apache license."""
        generator = SBOMGenerator(plugin_path=temp_plugin_dir)

        assert generator._normalize_license("Apache 2.0") == "Apache-2.0"
        assert generator._normalize_license("Apache License 2.0") == "Apache-2.0"
        assert generator._normalize_license("Apache Software License") == "Apache-2.0"

    def test_normalize_bsd(self, temp_plugin_dir):
        """Test normalizing BSD license."""
        generator = SBOMGenerator(plugin_path=temp_plugin_dir)

        assert generator._normalize_license("BSD") == "BSD-3-Clause"
        assert generator._normalize_license("BSD License") == "BSD-3-Clause"

    def test_unknown_license(self, temp_plugin_dir):
        """Test that unknown licenses return None."""
        generator = SBOMGenerator(plugin_path=temp_plugin_dir)

        assert generator._normalize_license("Unknown License") is None


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @patch("backend.plugins.supply_chain.sbom.subprocess.run")
    def test_generate_sbom(self, mock_run, plugin_with_requirements, tmp_path):
        """Test generate_sbom function."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        output_path = tmp_path / "sbom.json"

        sbom = generate_sbom(
            plugin_path=plugin_with_requirements,
            output_path=output_path,
            plugin_name="my-plugin",
            plugin_version="2.0.0",
        )

        assert sbom.bom_format == "CycloneDX"
        assert output_path.exists()

    def test_load_sbom(self, tmp_path):
        """Test load_sbom function."""
        # Create a test SBOM file
        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "serialNumber": "urn:uuid:12345",
            "components": [{"name": "test", "version": "1.0.0", "type": "library"}],
        }

        sbom_path = tmp_path / "test-sbom.json"
        sbom_path.write_text(json.dumps(sbom_data))

        loaded = load_sbom(sbom_path)

        assert loaded.bom_format == "CycloneDX"
        assert len(loaded.components) == 1


# =============================================================================
# Test ComponentType Enum
# =============================================================================


class TestComponentType:
    """Tests for ComponentType enum."""

    def test_all_types_defined(self):
        """Test that all expected component types are defined."""
        expected_types = [
            "APPLICATION",
            "LIBRARY",
            "FRAMEWORK",
            "FILE",
            "OPERATING_SYSTEM",
            "DEVICE",
            "FIRMWARE",
            "CONTAINER",
        ]

        for type_name in expected_types:
            assert hasattr(ComponentType, type_name)

    def test_type_values(self):
        """Test component type values."""
        assert ComponentType.APPLICATION.value == "application"
        assert ComponentType.LIBRARY.value == "library"
        assert ComponentType.FRAMEWORK.value == "framework"


# =============================================================================
# Test SBOMFormat Enum
# =============================================================================


class TestSBOMFormat:
    """Tests for SBOMFormat enum."""

    def test_formats_defined(self):
        """Test that all formats are defined."""
        assert hasattr(SBOMFormat, "JSON")
        assert hasattr(SBOMFormat, "XML")

    def test_format_values(self):
        """Test format values."""
        assert SBOMFormat.JSON.value == "json"
        assert SBOMFormat.XML.value == "xml"
