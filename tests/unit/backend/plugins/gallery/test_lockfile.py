"""
Unit tests for the lockfile system.

Phase 5C M4: Tests for version pinning and deployment consistency.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from backend.plugins.gallery.lockfile import (
    DEFAULT_LOCKFILE_NAME,
    LOCKFILE_VERSION,
    LockedDependency,
    LockedPlugin,
    Lockfile,
    LockfileConflict,
    LockfileManager,
    LockfileStatus,
    LockfileValidationResult,
    ResolutionStrategy,
    generate_lockfile,
    get_lockfile_manager,
    lock_plugin,
    unlock_plugin,
    validate_lockfile,
)


class TestLockfileStatus:
    """Tests for LockfileStatus enum."""

    def test_all_statuses_defined(self):
        """Verify all expected statuses exist."""
        expected = [
            "VALID",
            "OUTDATED",
            "MISSING_PLUGINS",
            "EXTRA_PLUGINS",
            "VERSION_MISMATCH",
            "INTEGRITY_FAILED",
            "CORRUPTED",
            "NOT_FOUND",
        ]
        actual = [s.name for s in LockfileStatus]
        for status in expected:
            assert status in actual

    def test_status_values(self):
        """Verify status values."""
        assert LockfileStatus.VALID.value == "valid"
        assert LockfileStatus.OUTDATED.value == "outdated"
        assert LockfileStatus.NOT_FOUND.value == "not_found"


class TestResolutionStrategy:
    """Tests for ResolutionStrategy enum."""

    def test_all_strategies_defined(self):
        """Verify all expected strategies exist."""
        expected = [
            "USE_LOCKFILE",
            "USE_INSTALLED",
            "USE_LATEST",
            "INTERACTIVE",
            "FAIL",
        ]
        actual = [s.name for s in ResolutionStrategy]
        for strategy in expected:
            assert strategy in actual


class TestLockedDependency:
    """Tests for LockedDependency dataclass."""

    def test_basic_creation(self):
        """Test basic creation."""
        dep = LockedDependency(
            plugin_id="dep-plugin",
            version="^1.0.0",
            resolved_version="1.0.5",
            checksum_sha256="abc123",
        )
        assert dep.plugin_id == "dep-plugin"
        assert dep.version == "^1.0.0"
        assert dep.resolved_version == "1.0.5"
        assert dep.checksum_sha256 == "abc123"
        assert dep.required_by == []
        assert dep.optional is False

    def test_with_required_by(self):
        """Test with required_by list."""
        dep = LockedDependency(
            plugin_id="dep-plugin",
            version="1.0.0",
            resolved_version="1.0.0",
            checksum_sha256="abc123",
            required_by=["main-plugin", "other-plugin"],
        )
        assert dep.required_by == ["main-plugin", "other-plugin"]

    def test_to_dict(self):
        """Test serialization to dict."""
        dep = LockedDependency(
            plugin_id="dep-plugin",
            version="1.0.0",
            resolved_version="1.0.0",
            checksum_sha256="abc123",
            download_url="https://example.com/dep.vspkg",
            required_by=["main-plugin"],
            optional=True,
        )
        data = dep.to_dict()
        assert data["plugin_id"] == "dep-plugin"
        assert data["version"] == "1.0.0"
        assert data["resolved_version"] == "1.0.0"
        assert data["checksum_sha256"] == "abc123"
        assert data["download_url"] == "https://example.com/dep.vspkg"
        assert data["required_by"] == ["main-plugin"]
        assert data["optional"] is True

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "plugin_id": "dep-plugin",
            "version": "1.0.0",
            "resolved_version": "1.0.0",
            "checksum_sha256": "abc123",
            "download_url": "https://example.com/dep.vspkg",
            "required_by": ["main-plugin"],
            "optional": True,
        }
        dep = LockedDependency.from_dict(data)
        assert dep.plugin_id == "dep-plugin"
        assert dep.version == "1.0.0"
        assert dep.optional is True


class TestLockedPlugin:
    """Tests for LockedPlugin dataclass."""

    def test_basic_creation(self):
        """Test basic creation."""
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.2.3",
            checksum_sha256="hash123",
            install_date="2024-01-15T10:30:00Z",
        )
        assert plugin.plugin_id == "my-plugin"
        assert plugin.version == "1.2.3"
        assert plugin.checksum_sha256 == "hash123"
        assert plugin.install_date == "2024-01-15T10:30:00Z"
        assert plugin.source == "catalog"
        assert plugin.dependencies == []
        assert plugin.dev_dependencies == []
        assert plugin.metadata == {}

    def test_with_dependencies(self):
        """Test with dependencies."""
        dep = LockedDependency(
            plugin_id="dep",
            version="1.0.0",
            resolved_version="1.0.0",
            checksum_sha256="dep-hash",
        )
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.2.3",
            checksum_sha256="hash123",
            install_date="2024-01-15T10:30:00Z",
            dependencies=[dep],
        )
        assert len(plugin.dependencies) == 1
        assert plugin.dependencies[0].plugin_id == "dep"

    def test_to_dict(self):
        """Test serialization to dict."""
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.2.3",
            checksum_sha256="hash123",
            install_date="2024-01-15T10:30:00Z",
            source="git",
            download_url="https://example.com/plugin.vspkg",
            metadata={"key": "value"},
        )
        data = plugin.to_dict()
        assert data["plugin_id"] == "my-plugin"
        assert data["version"] == "1.2.3"
        assert data["source"] == "git"
        assert data["metadata"] == {"key": "value"}

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "plugin_id": "my-plugin",
            "version": "1.2.3",
            "checksum_sha256": "hash123",
            "install_date": "2024-01-15T10:30:00Z",
            "source": "local",
            "dependencies": [
                {
                    "plugin_id": "dep",
                    "version": "1.0.0",
                    "resolved_version": "1.0.0",
                    "checksum_sha256": "dep-hash",
                }
            ],
        }
        plugin = LockedPlugin.from_dict(data)
        assert plugin.plugin_id == "my-plugin"
        assert plugin.source == "local"
        assert len(plugin.dependencies) == 1


class TestLockfileConflict:
    """Tests for LockfileConflict dataclass."""

    def test_basic_creation(self):
        """Test basic creation."""
        conflict = LockfileConflict(
            plugin_id="my-plugin",
            lockfile_version="1.0.0",
            installed_version="1.1.0",
            conflict_type="version_mismatch",
        )
        assert conflict.plugin_id == "my-plugin"
        assert conflict.lockfile_version == "1.0.0"
        assert conflict.installed_version == "1.1.0"
        assert conflict.conflict_type == "version_mismatch"
        assert conflict.resolution is None

    def test_to_dict(self):
        """Test serialization to dict."""
        conflict = LockfileConflict(
            plugin_id="my-plugin",
            lockfile_version="1.0.0",
            installed_version="",
            conflict_type="missing",
            resolution="install",
        )
        data = conflict.to_dict()
        assert data["plugin_id"] == "my-plugin"
        assert data["conflict_type"] == "missing"
        assert data["resolution"] == "install"


class TestLockfileValidationResult:
    """Tests for LockfileValidationResult dataclass."""

    def test_valid_result(self):
        """Test a valid result."""
        result = LockfileValidationResult(
            status=LockfileStatus.VALID,
            valid=True,
            message="All good",
        )
        assert result.valid is True
        assert result.status == LockfileStatus.VALID
        assert result.conflicts == []
        assert result.missing_plugins == []
        assert result.extra_plugins == []

    def test_invalid_result(self):
        """Test an invalid result with conflicts."""
        conflict = LockfileConflict(
            plugin_id="plugin1",
            lockfile_version="1.0.0",
            installed_version="2.0.0",
            conflict_type="version_mismatch",
        )
        result = LockfileValidationResult(
            status=LockfileStatus.VERSION_MISMATCH,
            valid=False,
            conflicts=[conflict],
            message="Version mismatch detected",
        )
        assert result.valid is False
        assert len(result.conflicts) == 1

    def test_to_dict(self):
        """Test serialization to dict."""
        result = LockfileValidationResult(
            status=LockfileStatus.MISSING_PLUGINS,
            valid=False,
            missing_plugins=["plugin1", "plugin2"],
        )
        data = result.to_dict()
        assert data["status"] == "missing_plugins"
        assert data["valid"] is False
        assert data["missing_plugins"] == ["plugin1", "plugin2"]


class TestLockfile:
    """Tests for Lockfile dataclass."""

    def test_basic_creation(self):
        """Test basic creation."""
        lockfile = Lockfile()
        assert lockfile.version == LOCKFILE_VERSION
        assert lockfile.generated_at != ""
        assert lockfile.plugins == {}
        assert lockfile.integrity_hash == ""

    def test_add_plugin(self):
        """Test adding a plugin."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        assert "my-plugin" in lockfile.plugins
        assert lockfile.integrity_hash != ""

    def test_remove_plugin(self):
        """Test removing a plugin."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        assert lockfile.remove_plugin("my-plugin") is True
        assert "my-plugin" not in lockfile.plugins

    def test_remove_nonexistent_plugin(self):
        """Test removing a plugin that doesn't exist."""
        lockfile = Lockfile()
        assert lockfile.remove_plugin("nonexistent") is False

    def test_has_plugin(self):
        """Test checking if a plugin exists."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        assert lockfile.has_plugin("my-plugin") is True
        assert lockfile.has_plugin("other-plugin") is False

    def test_get_plugin(self):
        """Test getting a plugin."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        retrieved = lockfile.get_plugin("my-plugin")
        assert retrieved is not None
        assert retrieved.plugin_id == "my-plugin"
        assert lockfile.get_plugin("nonexistent") is None

    def test_verify_integrity_pass(self):
        """Test integrity verification passes for unmodified lockfile."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        assert lockfile.verify_integrity() is True

    def test_verify_integrity_fail(self):
        """Test integrity verification fails for modified lockfile."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        # Tamper with the plugins directly
        lockfile.plugins["my-plugin"].version = "2.0.0"
        assert lockfile.verify_integrity() is False

    def test_to_dict(self):
        """Test serialization to dict."""
        lockfile = Lockfile(voicestudio_version="1.5.0")
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        data = lockfile.to_dict()
        assert data["version"] == LOCKFILE_VERSION
        assert data["voicestudio_version"] == "1.5.0"
        assert "my-plugin" in data["plugins"]

    def test_to_json(self):
        """Test JSON serialization."""
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        json_str = lockfile.to_json()
        parsed = json.loads(json_str)
        assert parsed["version"] == LOCKFILE_VERSION

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "version": "1.0",
            "generated_at": "2024-01-15T10:30:00Z",
            "voicestudio_version": "1.5.0",
            "plugins": {
                "my-plugin": {
                    "plugin_id": "my-plugin",
                    "version": "1.0.0",
                    "checksum_sha256": "hash",
                    "install_date": "2024-01-15T10:30:00Z",
                }
            },
            "integrity_hash": "somehash",
        }
        lockfile = Lockfile.from_dict(data)
        assert lockfile.voicestudio_version == "1.5.0"
        assert lockfile.has_plugin("my-plugin")

    def test_from_json(self):
        """Test deserialization from JSON."""
        json_str = json.dumps({
            "version": "1.0",
            "generated_at": "2024-01-15T10:30:00Z",
            "voicestudio_version": "1.5.0",
            "plugins": {},
            "integrity_hash": "",
        })
        lockfile = Lockfile.from_json(json_str)
        assert lockfile.voicestudio_version == "1.5.0"

    def test_save_and_load(self):
        """Test save and load roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.lock"
            
            lockfile = Lockfile(voicestudio_version="1.5.0")
            plugin = LockedPlugin(
                plugin_id="my-plugin",
                version="1.0.0",
                checksum_sha256="hash",
                install_date="2024-01-15T10:30:00Z",
            )
            lockfile.add_plugin(plugin)
            lockfile.save(path)
            
            loaded = Lockfile.load(path)
            assert loaded.voicestudio_version == "1.5.0"
            assert loaded.has_plugin("my-plugin")
            assert loaded.verify_integrity() is True


class TestLockfileManager:
    """Tests for LockfileManager class."""

    @pytest.fixture
    def temp_plugins_dir(self):
        """Create a temporary plugins directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            plugins_dir.mkdir()
            yield plugins_dir

    def test_create_manager(self, temp_plugins_dir):
        """Test creating a manager."""
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        assert manager.lockfile_path.name == DEFAULT_LOCKFILE_NAME
        assert manager.lockfile_exists() is False

    def test_generate_lockfile_empty(self, temp_plugins_dir):
        """Test generating lockfile with no plugins."""
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        lockfile = manager.generate_lockfile()
        assert len(lockfile.plugins) == 0

    def test_generate_lockfile_with_registry(self, temp_plugins_dir):
        """Test generating lockfile from registry."""
        # Create a mock registry
        registry = {
            "plugin1": {
                "version": "1.0.0",
                "installed_at": "2024-01-15T10:30:00Z",
                "source": "catalog",
            },
            "plugin2": {
                "version": "2.0.0",
                "installed_at": "2024-01-16T10:30:00Z",
                "source": "local",
            },
        }
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        lockfile = manager.generate_lockfile()
        
        assert len(lockfile.plugins) == 2
        assert lockfile.has_plugin("plugin1")
        assert lockfile.has_plugin("plugin2")

    def test_save_and_load_lockfile(self, temp_plugins_dir):
        """Test saving and loading lockfile."""
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="my-plugin",
            version="1.0.0",
            checksum_sha256="hash",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        manager.save_lockfile(lockfile)
        
        assert manager.lockfile_exists() is True
        
        loaded = manager.load_lockfile()
        assert loaded is not None
        assert loaded.has_plugin("my-plugin")

    def test_validate_lockfile_not_found(self, temp_plugins_dir):
        """Test validation when lockfile doesn't exist."""
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        result = manager.validate_lockfile()
        assert result.status == LockfileStatus.NOT_FOUND
        assert result.valid is False

    def test_validate_lockfile_valid(self, temp_plugins_dir):
        """Test validation with matching installation."""
        # Create registry
        registry = {
            "plugin1": {
                "version": "1.0.0",
                "installed_at": "2024-01-15T10:30:00Z",
            }
        }
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        # Create lockfile that matches
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="plugin1",
            version="1.0.0",
            checksum_sha256="",  # Empty checksum skips integrity check
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        manager.save_lockfile(lockfile)
        
        result = manager.validate_lockfile()
        assert result.valid is True
        assert result.status == LockfileStatus.VALID

    def test_validate_lockfile_version_mismatch(self, temp_plugins_dir):
        """Test validation detects version mismatch."""
        # Create registry with one version
        registry = {
            "plugin1": {
                "version": "2.0.0",  # Different version
                "installed_at": "2024-01-15T10:30:00Z",
            }
        }
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        # Create lockfile with different version
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="plugin1",
            version="1.0.0",
            checksum_sha256="",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        manager.save_lockfile(lockfile)
        
        result = manager.validate_lockfile()
        assert result.valid is False
        assert result.status == LockfileStatus.VERSION_MISMATCH
        assert len(result.conflicts) == 1
        assert result.conflicts[0].conflict_type == "version_mismatch"

    def test_validate_lockfile_missing_plugin(self, temp_plugins_dir):
        """Test validation detects missing plugins."""
        # Empty registry
        registry = {}
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        # Lockfile expects a plugin
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="plugin1",
            version="1.0.0",
            checksum_sha256="",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        manager.save_lockfile(lockfile)
        
        result = manager.validate_lockfile()
        assert result.valid is False
        assert result.status == LockfileStatus.MISSING_PLUGINS
        assert "plugin1" in result.missing_plugins

    def test_validate_lockfile_extra_plugin(self, temp_plugins_dir):
        """Test validation detects extra plugins."""
        # Registry has a plugin
        registry = {
            "extra-plugin": {
                "version": "1.0.0",
                "installed_at": "2024-01-15T10:30:00Z",
            }
        }
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        # Empty lockfile
        lockfile = Lockfile()
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        manager.save_lockfile(lockfile)
        
        result = manager.validate_lockfile()
        assert result.valid is False
        assert result.status == LockfileStatus.EXTRA_PLUGINS
        assert "extra-plugin" in result.extra_plugins

    def test_lock_plugin(self, temp_plugins_dir):
        """Test locking a specific plugin."""
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        lockfile = manager.lock_plugin(
            plugin_id="my-plugin",
            version="1.0.0",
            source="catalog",
        )
        assert lockfile.has_plugin("my-plugin")
        assert lockfile.get_plugin("my-plugin").version == "1.0.0"

    def test_unlock_plugin(self, temp_plugins_dir):
        """Test unlocking a plugin."""
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        
        # First lock a plugin
        manager.lock_plugin(
            plugin_id="my-plugin",
            version="1.0.0",
        )
        
        # Then unlock it
        lockfile = manager.unlock_plugin("my-plugin")
        assert lockfile is not None
        assert not lockfile.has_plugin("my-plugin")

    def test_get_install_plan_in_sync(self, temp_plugins_dir):
        """Test install plan when in sync."""
        # Matching registry and lockfile
        registry = {
            "plugin1": {
                "version": "1.0.0",
                "installed_at": "2024-01-15T10:30:00Z",
            }
        }
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="plugin1",
            version="1.0.0",
            checksum_sha256="",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        manager.save_lockfile(lockfile)
        
        plan = manager.get_install_plan()
        assert plan["install_count"] == 0
        assert plan["change_count"] == 0

    def test_get_install_plan_needs_install(self, temp_plugins_dir):
        """Test install plan detects needed installs."""
        # Empty registry
        registry = {}
        registry_path = temp_plugins_dir / "registry.json"
        registry_path.write_text(json.dumps(registry))
        
        lockfile = Lockfile()
        plugin = LockedPlugin(
            plugin_id="plugin1",
            version="1.0.0",
            checksum_sha256="",
            install_date="2024-01-15T10:30:00Z",
        )
        lockfile.add_plugin(plugin)
        
        manager = LockfileManager(plugins_dir=temp_plugins_dir)
        manager.save_lockfile(lockfile)
        
        plan = manager.get_install_plan()
        assert plan["install_count"] == 1
        assert plan["actions"][0]["action"] == "install"
        assert plan["actions"][0]["plugin_id"] == "plugin1"

    def test_export_lockfile(self, temp_plugins_dir):
        """Test exporting lockfile."""
        with tempfile.TemporaryDirectory() as export_dir:
            export_path = Path(export_dir) / "exported.lock"
            
            manager = LockfileManager(plugins_dir=temp_plugins_dir)
            manager.lock_plugin("my-plugin", "1.0.0")
            manager.export_lockfile(export_path)
            
            assert export_path.exists()
            loaded = Lockfile.load(export_path)
            assert loaded.has_plugin("my-plugin")

    def test_import_lockfile(self, temp_plugins_dir):
        """Test importing lockfile."""
        with tempfile.TemporaryDirectory() as import_dir:
            import_path = Path(import_dir) / "import.lock"
            
            # Create a lockfile to import
            lockfile = Lockfile()
            plugin = LockedPlugin(
                plugin_id="imported-plugin",
                version="2.0.0",
                checksum_sha256="hash",
                install_date="2024-01-15T10:30:00Z",
            )
            lockfile.add_plugin(plugin)
            lockfile.save(import_path)
            
            manager = LockfileManager(plugins_dir=temp_plugins_dir)
            imported = manager.import_lockfile(import_path)
            
            assert imported.has_plugin("imported-plugin")
            assert manager.lockfile_exists()


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture
    def temp_plugins_dir(self, monkeypatch):
        """Create temp plugins dir and patch singleton."""
        import backend.plugins.gallery.lockfile as lockfile_module
        
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            plugins_dir.mkdir()
            
            # Reset singleton
            lockfile_module._lockfile_manager = None
            
            # Create new manager
            manager = LockfileManager(plugins_dir=plugins_dir)
            lockfile_module._lockfile_manager = manager
            
            yield plugins_dir
            
            # Clean up singleton
            lockfile_module._lockfile_manager = None

    def test_get_lockfile_manager(self, temp_plugins_dir):
        """Test getting the manager singleton."""
        manager1 = get_lockfile_manager()
        manager2 = get_lockfile_manager()
        # Should be the same instance
        assert manager1 is manager2

    def test_generate_lockfile_function(self, temp_plugins_dir):
        """Test generate_lockfile function."""
        lockfile = generate_lockfile(voicestudio_version="2.0.0", save=True)
        assert lockfile.voicestudio_version == "2.0.0"

    def test_lock_plugin_function(self, temp_plugins_dir):
        """Test lock_plugin function."""
        lockfile = lock_plugin("test-plugin", "1.0.0")
        assert lockfile.has_plugin("test-plugin")

    def test_unlock_plugin_function(self, temp_plugins_dir):
        """Test unlock_plugin function."""
        # First lock
        lock_plugin("test-plugin", "1.0.0")
        
        # Then unlock
        lockfile = unlock_plugin("test-plugin")
        assert lockfile is not None
        assert not lockfile.has_plugin("test-plugin")
