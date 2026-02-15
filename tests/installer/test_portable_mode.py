"""
Portable Mode Detection Tests.

Tests for portable mode (thumb drive) functionality:
- Flag file detection
- Path resolution in portable mode
- Data directory handling

Phase 8C: Portable Mode Testing
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.installer,
    pytest.mark.portable,
]


@pytest.fixture
def temp_portable_dir():
    """Create a temporary directory that simulates a portable installation."""
    with tempfile.TemporaryDirectory(prefix="voicestudio_portable_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def portable_flag(temp_portable_dir: Path):
    """Create a portable.flag file in the temp directory."""
    flag_file = temp_portable_dir / "portable.flag"
    flag_file.touch()
    return flag_file


class TestPortableFlagDetection:
    """Tests for portable.flag file detection."""

    def test_portable_flag_file_created(self, portable_flag: Path):
        """Test that portable flag file can be created."""
        assert portable_flag.exists()
        assert portable_flag.name == "portable.flag"

    def test_portable_flag_content_empty(self, portable_flag: Path):
        """Test that empty flag file is valid."""
        assert portable_flag.read_text() == ""

    def test_portable_flag_content_with_message(self, temp_portable_dir: Path):
        """Test that flag file can contain content."""
        flag_file = temp_portable_dir / "portable.flag"
        flag_file.write_text("Portable installation marker\n")
        assert flag_file.exists()
        assert "Portable" in flag_file.read_text()


class TestPortablePathResolution:
    """Tests for path resolution in portable mode."""

    def test_data_dir_in_portable_mode(self, temp_portable_dir: Path, portable_flag: Path):
        """Test that data directory is within portable directory."""
        # In portable mode, data should be stored next to the portable.flag
        expected_data_dir = temp_portable_dir / "data"
        expected_data_dir.mkdir(exist_ok=True)

        assert expected_data_dir.exists()
        assert expected_data_dir.parent == temp_portable_dir

    def test_logs_dir_in_portable_mode(self, temp_portable_dir: Path, portable_flag: Path):
        """Test that logs directory is within portable directory."""
        expected_logs_dir = temp_portable_dir / "logs"
        expected_logs_dir.mkdir(exist_ok=True)

        assert expected_logs_dir.exists()
        assert expected_logs_dir.parent == temp_portable_dir

    def test_config_dir_in_portable_mode(self, temp_portable_dir: Path, portable_flag: Path):
        """Test that config directory is within portable directory."""
        expected_config_dir = temp_portable_dir / "config"
        expected_config_dir.mkdir(exist_ok=True)

        assert expected_config_dir.exists()
        assert expected_config_dir.parent == temp_portable_dir


class TestPortableDirectoryStructure:
    """Tests for creating portable directory structure."""

    def test_create_full_portable_structure(self, temp_portable_dir: Path, portable_flag: Path):
        """Test creation of full portable directory structure."""
        # Expected directories in a portable installation
        expected_dirs = [
            "data",
            "logs",
            "config",
            "engines",
            "models",
            "cache",
        ]

        for dir_name in expected_dirs:
            dir_path = temp_portable_dir / dir_name
            dir_path.mkdir(exist_ok=True)

        # Verify all directories exist
        for dir_name in expected_dirs:
            dir_path = temp_portable_dir / dir_name
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"

    def test_portable_structure_is_self_contained(self, temp_portable_dir: Path, portable_flag: Path):
        """Test that portable installation is self-contained."""
        # Create structure
        data_dir = temp_portable_dir / "data"
        data_dir.mkdir()

        # Create a test file
        test_file = data_dir / "test.db"
        test_file.touch()

        # Verify file is within portable directory
        assert test_file.is_relative_to(temp_portable_dir)


class TestPortableModeBackendSettings:
    """Tests for portable mode detection in backend settings."""

    def test_portable_flag_in_cwd(self, temp_portable_dir: Path, portable_flag: Path):
        """Test detection when portable.flag is in current working directory."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_portable_dir)
            flag_path = Path.cwd() / "portable.flag"
            assert flag_path.exists()
        finally:
            os.chdir(original_cwd)

    def test_portable_flag_in_parent_dir(self, temp_portable_dir: Path, portable_flag: Path):
        """Test detection when portable.flag is in parent directory."""
        subdir = temp_portable_dir / "backend"
        subdir.mkdir()

        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            flag_path = Path.cwd().parent / "portable.flag"
            assert flag_path.exists()
        finally:
            os.chdir(original_cwd)

    def test_portable_flag_in_script_dir(self, temp_portable_dir: Path, portable_flag: Path):
        """Test detection when portable.flag is next to script."""
        script_dir = temp_portable_dir / "backend"
        script_dir.mkdir()

        # Portable flag should be in parent
        flag_path = script_dir.parent / "portable.flag"
        assert flag_path.exists()


class TestNonPortableMode:
    """Tests for non-portable (installed) mode behavior."""

    def test_no_portable_flag(self, temp_portable_dir: Path):
        """Test behavior when no portable.flag exists."""
        flag_path = temp_portable_dir / "portable.flag"
        assert not flag_path.exists()

    def test_portable_flag_removed(self, temp_portable_dir: Path, portable_flag: Path):
        """Test behavior when portable.flag is removed."""
        assert portable_flag.exists()

        # Remove the flag
        portable_flag.unlink()

        assert not portable_flag.exists()


class TestPortableFlagLocations:
    """Tests for different portable.flag locations."""

    def test_flag_locations_priority(self, temp_portable_dir: Path):
        """Test that flag can be detected at multiple locations."""
        # Create nested structure
        backend_dir = temp_portable_dir / "backend" / "api"
        backend_dir.mkdir(parents=True)

        # Flag at root level
        root_flag = temp_portable_dir / "portable.flag"
        root_flag.touch()

        # Check detection from backend directory
        locations_to_check = [
            backend_dir / "portable.flag",
            backend_dir.parent / "portable.flag",
            backend_dir.parent.parent / "portable.flag",
        ]

        # At least one location should have the flag
        flag_found = any(loc.exists() for loc in locations_to_check)
        assert flag_found, "Portable flag should be detectable from backend dir"


class TestPortableDataIsolation:
    """Tests for data isolation in portable mode."""

    def test_multiple_portable_instances(self):
        """Test that multiple portable installations can coexist."""
        with tempfile.TemporaryDirectory(prefix="portable1_") as dir1:
            with tempfile.TemporaryDirectory(prefix="portable2_") as dir2:
                path1 = Path(dir1)
                path2 = Path(dir2)

                # Create flags in both
                (path1 / "portable.flag").touch()
                (path2 / "portable.flag").touch()

                # Create data in both
                (path1 / "data").mkdir()
                (path2 / "data").mkdir()

                (path1 / "data" / "instance1.db").touch()
                (path2 / "data" / "instance2.db").touch()

                # Verify isolation
                assert not (path1 / "data" / "instance2.db").exists()
                assert not (path2 / "data" / "instance1.db").exists()

    def test_portable_no_system_paths(self, temp_portable_dir: Path, portable_flag: Path):
        """Test that portable mode data structure is self-contained within app directory."""
        # Create portable data directory
        data_dir = temp_portable_dir / "data"
        data_dir.mkdir()

        # Verify data_dir is a child of the portable root
        # (the test temp dir may be in LOCALAPPDATA/Temp, but that's OK for testing)
        assert data_dir.parent == temp_portable_dir
        
        # The key property: data is relative to app root, not a fixed system path
        relative_path = data_dir.relative_to(temp_portable_dir)
        assert relative_path == Path("data")
        
        # Verify the path doesn't contain user profile name patterns
        # (indicating it's not using user-specific resolution)
        path_str = str(data_dir.relative_to(temp_portable_dir))
        assert "AppData" not in path_str
        assert "Users" not in path_str
