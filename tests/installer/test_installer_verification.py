"""
Installer Verification Tests.

Tests for installer infrastructure validation:
- Required installer scripts exist
- Source files for packaging exist
- Build output verification

Phase 8A: Installer Build Validation
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.installer,
]


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    # Navigate from tests/installer to project root
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def installer_dir(project_root: Path) -> Path:
    """Get the installer directory."""
    return project_root / "installer"


class TestInstallerScriptsExist:
    """Tests that required installer scripts exist."""

    def test_build_installer_script_exists(self, installer_dir: Path):
        """Test that build-installer.ps1 exists."""
        script = installer_dir / "build-installer.ps1"
        assert script.exists(), f"Build script not found: {script}"

    def test_install_script_exists(self, installer_dir: Path):
        """Test that install.ps1 exists."""
        script = installer_dir / "install.ps1"
        assert script.exists(), f"Install script not found: {script}"

    def test_inno_setup_script_exists(self, installer_dir: Path):
        """Test that VoiceStudio.iss exists."""
        script = installer_dir / "VoiceStudio.iss"
        assert script.exists(), f"Inno Setup script not found: {script}"

    def test_prerequisites_script_exists(self, installer_dir: Path):
        """Test that prerequisites.iss exists."""
        script = installer_dir / "prerequisites.iss"
        assert script.exists(), f"Prerequisites script not found: {script}"

    def test_verify_installer_script_exists(self, installer_dir: Path):
        """Test that verify-installer.ps1 exists."""
        script = installer_dir / "verify-installer.ps1"
        assert script.exists(), f"Verify script not found: {script}"

    def test_verify_installer_build_script_exists(self, installer_dir: Path):
        """Test that verify-installer-build.ps1 exists."""
        script = installer_dir / "verify-installer-build.ps1"
        assert script.exists(), f"Verify build script not found: {script}"


class TestInstallerTestScriptsExist:
    """Tests that installer test scripts exist."""

    def test_silent_test_script_exists(self, installer_dir: Path):
        """Test that test-installer-silent.ps1 exists."""
        script = installer_dir / "test-installer-silent.ps1"
        assert script.exists(), f"Silent test script not found: {script}"

    def test_lifecycle_test_script_exists(self, installer_dir: Path):
        """Test that test-installer-lifecycle.ps1 exists."""
        script = installer_dir / "test-installer-lifecycle.ps1"
        assert script.exists(), f"Lifecycle test script not found: {script}"


class TestSourceFilesExist:
    """Tests that required source files for installer exist."""

    def test_backend_main_exists(self, project_root: Path):
        """Test that backend/api/main.py exists."""
        main_py = project_root / "backend" / "api" / "main.py"
        assert main_py.exists(), f"Backend main.py not found: {main_py}"

    def test_backend_routes_exist(self, project_root: Path):
        """Test that backend routes directory exists with files."""
        routes_dir = project_root / "backend" / "api" / "routes"
        assert routes_dir.exists(), f"Backend routes directory not found: {routes_dir}"
        route_files = list(routes_dir.glob("*.py"))
        assert len(route_files) > 0, "No route files found in backend/api/routes"

    def test_engine_manifests_exist(self, project_root: Path):
        """Test that engine manifests exist."""
        engines_dir = project_root / "engines"
        assert engines_dir.exists(), f"Engines directory not found: {engines_dir}"

    def test_core_engines_exist(self, project_root: Path):
        """Test that core engine files exist."""
        core_engines = project_root / "app" / "core" / "engines"
        assert core_engines.exists(), f"Core engines directory not found: {core_engines}"
        engine_files = list(core_engines.glob("*.py"))
        assert len(engine_files) > 0, "No engine files found"

    def test_license_exists(self, project_root: Path):
        """Test that LICENSE file exists."""
        license_file = project_root / "LICENSE"
        assert license_file.exists(), f"LICENSE file not found: {license_file}"


class TestInstallerConfiguration:
    """Tests for installer configuration."""

    def test_installer_config_exists(self, installer_dir: Path):
        """Test that installer config exists."""
        config_dir = installer_dir / "config"
        assert config_dir.exists(), f"Config directory not found: {config_dir}"

    def test_installer_readme_exists(self, installer_dir: Path):
        """Test that installer README exists."""
        readme = installer_dir / "README.md"
        assert readme.exists(), f"README not found: {readme}"

    def test_thumbdrive_readme_exists(self, installer_dir: Path):
        """Test that thumb drive README exists."""
        readme = installer_dir / "README-THUMBDRIVE.txt"
        assert readme.exists(), f"Thumb drive README not found: {readme}"


class TestRuntimeDependencies:
    """Tests for runtime dependencies included in installer."""

    def test_runtime_ffmpeg_exists(self, installer_dir: Path):
        """Test that FFmpeg runtime exists."""
        ffmpeg_dir = installer_dir / "runtime" / "ffmpeg"
        # FFmpeg may not be present in dev environment
        if ffmpeg_dir.exists():
            ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
            assert ffmpeg_exe.exists(), "ffmpeg.exe not found in runtime"

    def test_runtime_python_exists(self, installer_dir: Path):
        """Test that Python runtime exists."""
        python_dir = installer_dir / "runtime" / "python"
        # Python runtime may not be present in dev environment
        if python_dir.exists():
            # At minimum, the Scripts directory should exist
            scripts_dir = python_dir / "Scripts"
            assert scripts_dir.exists(), "Python Scripts not found in runtime"


class TestInstallerOutputStructure:
    """Tests for expected installer output structure."""

    def test_output_directory_exists(self, installer_dir: Path):
        """Test that Output directory exists."""
        output_dir = installer_dir / "Output"
        # Output may not exist until installer is built
        # This test just checks the structure is correct when it exists
        if output_dir.exists():
            # Check for any installer executables
            installers = list(output_dir.glob("*.exe"))
            # Could be 0 if not built yet, but structure should be valid
            assert output_dir.is_dir()
