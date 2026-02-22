"""
Unit tests for installer_v2.py.

Phase 5C M7: Tests for enhanced plugin installer with .vspkg support,
verification, and atomic installation with rollback.
"""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.gallery.installer_v2 import (
    AtomicInstallResult,
    BackupInfo,
    InstallAction,
    InstallTransaction,
    PackageVerificationResult,
    PluginInstallerV2,
    TransactionState,
    get_installer_v2,
    install_from_vspkg,
    install_plugin_atomic,
    rollback_plugin,
)


class TestTransactionState:
    """Tests for TransactionState enum."""

    def test_all_states_defined(self) -> None:
        """Verify all expected states exist."""
        assert TransactionState.PENDING.value == "pending"
        assert TransactionState.IN_PROGRESS.value == "in_progress"
        assert TransactionState.COMMITTED.value == "committed"
        assert TransactionState.ROLLED_BACK.value == "rolled_back"
        assert TransactionState.FAILED.value == "failed"


class TestInstallAction:
    """Tests for InstallAction enum."""

    def test_all_actions_defined(self) -> None:
        """Verify all expected actions exist."""
        assert InstallAction.INSTALL.value == "install"
        assert InstallAction.UPDATE.value == "update"
        assert InstallAction.UNINSTALL.value == "uninstall"
        assert InstallAction.ROLLBACK.value == "rollback"


class TestBackupInfo:
    """Tests for BackupInfo dataclass."""

    def test_creation(self) -> None:
        """Test basic creation."""
        backup = BackupInfo(
            plugin_id="test-plugin",
            version="1.0.0",
            backup_path="/path/to/backup",
            created_at=datetime(2025, 1, 15, 10, 30, 0),
        )

        assert backup.plugin_id == "test-plugin"
        assert backup.version == "1.0.0"
        assert backup.backup_path == "/path/to/backup"
        assert backup.created_at == datetime(2025, 1, 15, 10, 30, 0)
        assert backup.registry_data == {}

    def test_with_registry_data(self) -> None:
        """Test creation with registry data."""
        backup = BackupInfo(
            plugin_id="test-plugin",
            version="1.0.0",
            backup_path="/path/to/backup",
            created_at=datetime(2025, 1, 15, 10, 30, 0),
            registry_data={"enabled": True, "config": {"key": "value"}},
        )

        assert backup.registry_data == {"enabled": True, "config": {"key": "value"}}

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        backup = BackupInfo(
            plugin_id="test-plugin",
            version="1.0.0",
            backup_path="/path/to/backup",
            created_at=datetime(2025, 1, 15, 10, 30, 0),
            registry_data={"key": "value"},
        )

        result = backup.to_dict()

        assert result["plugin_id"] == "test-plugin"
        assert result["version"] == "1.0.0"
        assert result["backup_path"] == "/path/to/backup"
        assert result["created_at"] == "2025-01-15T10:30:00"
        assert result["registry_data"] == {"key": "value"}


class TestInstallTransaction:
    """Tests for InstallTransaction dataclass."""

    def test_default_creation(self) -> None:
        """Test creation with defaults."""
        transaction = InstallTransaction(id="tx-001")

        assert transaction.id == "tx-001"
        assert transaction.actions == []
        assert transaction.state == TransactionState.PENDING
        assert transaction.backups == []
        assert transaction.started_at is None
        assert transaction.completed_at is None
        assert transaction.error is None

    def test_full_creation(self) -> None:
        """Test creation with all fields."""
        backup = BackupInfo(
            plugin_id="test-plugin",
            version="1.0.0",
            backup_path="/backup",
            created_at=datetime(2025, 1, 15, 10, 0, 0),
        )

        transaction = InstallTransaction(
            id="tx-002",
            actions=[{"action": "install", "plugin_id": "test-plugin"}],
            state=TransactionState.IN_PROGRESS,
            backups=[backup],
            started_at=datetime(2025, 1, 15, 10, 30, 0),
            completed_at=datetime(2025, 1, 15, 10, 35, 0),
            error=None,
        )

        assert transaction.id == "tx-002"
        assert len(transaction.actions) == 1
        assert transaction.state == TransactionState.IN_PROGRESS
        assert len(transaction.backups) == 1
        assert transaction.started_at is not None
        assert transaction.completed_at is not None

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        transaction = InstallTransaction(
            id="tx-003",
            state=TransactionState.COMMITTED,
            started_at=datetime(2025, 1, 15, 10, 30, 0),
            completed_at=datetime(2025, 1, 15, 10, 35, 0),
        )

        result = transaction.to_dict()

        assert result["id"] == "tx-003"
        assert result["state"] == "committed"
        assert result["started_at"] == "2025-01-15T10:30:00"
        assert result["completed_at"] == "2025-01-15T10:35:00"


class TestPackageVerificationResult:
    """Tests for PackageVerificationResult dataclass."""

    def test_valid_result(self) -> None:
        """Test a valid verification result."""
        result = PackageVerificationResult(
            valid=True,
            signature_valid=True,
            sbom_present=True,
            provenance_present=True,
            checksum_valid=True,
            manifest_valid=True,
        )

        assert result.valid is True
        assert result.signature_valid is True
        assert result.sbom_present is True
        assert result.provenance_present is True
        assert result.checksum_valid is True
        assert result.manifest_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result_with_errors(self) -> None:
        """Test an invalid result with errors."""
        result = PackageVerificationResult(
            valid=False,
            checksum_valid=True,
            manifest_valid=False,
            errors=["Invalid manifest", "Missing required field"],
            warnings=["Package not signed"],
        )

        assert result.valid is False
        assert result.manifest_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        result = PackageVerificationResult(
            valid=True,
            signature_valid=True,
            sbom_present=True,
            provenance_present=False,
            checksum_valid=True,
            manifest_valid=True,
            errors=[],
            warnings=["No provenance"],
        )

        data = result.to_dict()

        assert data["valid"] is True
        assert data["signature_valid"] is True
        assert data["sbom_present"] is True
        assert data["provenance_present"] is False
        assert data["checksum_valid"] is True
        assert data["manifest_valid"] is True
        assert data["errors"] == []
        assert data["warnings"] == ["No provenance"]


class TestAtomicInstallResult:
    """Tests for AtomicInstallResult dataclass."""

    def test_successful_result(self) -> None:
        """Test a successful installation result."""
        verification = PackageVerificationResult(
            valid=True, checksum_valid=True, manifest_valid=True
        )

        result = AtomicInstallResult(
            success=True,
            plugin_id="test-plugin",
            version="1.0.0",
            install_path="/plugins/test-plugin",
            verification=verification,
            transaction_id="tx-001",
            rollback_available=True,
        )

        assert result.success is True
        assert result.plugin_id == "test-plugin"
        assert result.version == "1.0.0"
        assert result.install_path == "/plugins/test-plugin"
        assert result.verification is not None
        assert result.transaction_id == "tx-001"
        assert result.rollback_available is True
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test a failed installation result."""
        result = AtomicInstallResult(
            success=False,
            plugin_id="test-plugin",
            version="1.0.0",
            error="Installation failed: insufficient permissions",
        )

        assert result.success is False
        assert result.error == "Installation failed: insufficient permissions"
        assert result.install_path is None
        assert result.verification is None
        assert result.rollback_available is False

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        verification = PackageVerificationResult(
            valid=True, checksum_valid=True, manifest_valid=True
        )

        result = AtomicInstallResult(
            success=True,
            plugin_id="test-plugin",
            version="1.0.0",
            install_path="/plugins/test-plugin",
            verification=verification,
            transaction_id="tx-001",
            rollback_available=True,
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["plugin_id"] == "test-plugin"
        assert data["version"] == "1.0.0"
        assert data["install_path"] == "/plugins/test-plugin"
        assert data["verification"] is not None
        assert data["verification"]["valid"] is True
        assert data["transaction_id"] == "tx-001"
        assert data["rollback_available"] is True
        assert data["error"] is None


class TestPluginInstallerV2:
    """Tests for PluginInstallerV2 class."""

    @pytest.fixture
    def plugins_dir(self, tmp_path: Path) -> Path:
        """Create a temporary plugins directory."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        return plugins_dir

    @pytest.fixture
    def installer(self, plugins_dir: Path) -> PluginInstallerV2:
        """Create an installer instance."""
        return PluginInstallerV2(plugins_dir=plugins_dir)

    def test_installer_initialization(
        self, installer: PluginInstallerV2, plugins_dir: Path
    ) -> None:
        """Test installer initialization."""
        assert installer._plugins_dir == plugins_dir
        assert installer._backups_dir == plugins_dir / ".backups"
        assert installer._staging_dir == plugins_dir / ".staging"
        assert installer._transactions_dir == plugins_dir / ".transactions"
        assert installer._active_transactions == {}

    def test_supporting_directories_created(self, installer: PluginInstallerV2) -> None:
        """Test that supporting directories are created on init."""
        assert installer._backups_dir.exists()
        assert installer._staging_dir.exists()
        assert installer._transactions_dir.exists()

    @pytest.fixture
    def sample_vspkg(self, tmp_path: Path) -> Path:
        """Create a sample .vspkg package for testing."""
        package_path = tmp_path / "test-plugin-1.0.0.vspkg"

        manifest = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "permissions": [],
        }

        # Create a zip file with manifest and dummy content
        with zipfile.ZipFile(package_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("plugin.py", "# Plugin code\nprint('Hello')")
            zf.writestr("README.md", "# Test Plugin")

        return package_path

    @pytest.fixture
    def signed_vspkg(self, tmp_path: Path) -> Path:
        """Create a signed .vspkg package for testing."""
        package_path = tmp_path / "signed-plugin-1.0.0.vspkg"

        manifest = {
            "id": "signed-plugin",
            "name": "Signed Plugin",
            "version": "1.0.0",
            "description": "A signed test plugin",
        }

        signature = {"algorithm": "ed25519", "signature": "dummy_signature"}
        sbom = {"bomFormat": "CycloneDX", "specVersion": "1.4"}
        provenance = {"builder": {"id": "local"}, "buildType": "local"}

        with zipfile.ZipFile(package_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("signature.json", json.dumps(signature))
            zf.writestr("sbom.json", json.dumps(sbom))
            zf.writestr("provenance.json", json.dumps(provenance))
            zf.writestr("plugin.py", "# Plugin code")

        return package_path

    @pytest.mark.asyncio
    async def test_extract_manifest_valid(
        self, installer: PluginInstallerV2, sample_vspkg: Path
    ) -> None:
        """Test extracting manifest from valid package."""
        manifest = await installer._extract_manifest(sample_vspkg)

        assert manifest is not None
        assert manifest["id"] == "test-plugin"
        assert manifest["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_extract_manifest_invalid_path(
        self, installer: PluginInstallerV2, tmp_path: Path
    ) -> None:
        """Test extracting manifest from non-existent package."""
        manifest = await installer._extract_manifest(tmp_path / "nonexistent.vspkg")
        assert manifest is None

    @pytest.mark.asyncio
    async def test_extract_manifest_no_manifest(
        self, installer: PluginInstallerV2, tmp_path: Path
    ) -> None:
        """Test extracting manifest from package without manifest."""
        package_path = tmp_path / "no-manifest.vspkg"

        with zipfile.ZipFile(package_path, "w") as zf:
            zf.writestr("plugin.py", "# Plugin code")

        manifest = await installer._extract_manifest(package_path)
        assert manifest is None

    @pytest.mark.asyncio
    async def test_verify_package_basic(
        self, installer: PluginInstallerV2, sample_vspkg: Path
    ) -> None:
        """Test basic package verification."""
        result = await installer._verify_package(sample_vspkg)

        assert result.valid is True
        assert result.checksum_valid is True
        assert result.manifest_valid is True
        # Not signed
        assert result.signature_valid is None
        # No SBOM or provenance
        assert result.sbom_present is False
        assert result.provenance_present is False
        assert "Package is not signed" in result.warnings

    @pytest.mark.asyncio
    async def test_verify_package_with_security_metadata(
        self, installer: PluginInstallerV2, signed_vspkg: Path
    ) -> None:
        """Test verification of package with security metadata."""
        result = await installer._verify_package(signed_vspkg)

        assert result.checksum_valid is True
        assert result.manifest_valid is True
        assert result.sbom_present is True
        assert result.provenance_present is True

    @pytest.mark.asyncio
    async def test_create_backup(self, installer: PluginInstallerV2, plugins_dir: Path) -> None:
        """Test creating a plugin backup."""
        # Create a mock installed plugin
        plugin_dir = plugins_dir / "default" / "test-plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "plugin.py").write_text("# Plugin code")
        (plugin_dir / "manifest.json").write_text('{"id": "test-plugin", "version": "1.0.0"}')

        # Register the plugin
        from backend.plugins.gallery.models import InstalledPlugin

        installer._installed["test-plugin"] = InstalledPlugin(
            id="test-plugin",
            version="1.0.0",
            installed_at=datetime.now(),
            install_path=str(plugin_dir),
            state="enabled",
            config={},
        )

        # _create_backup takes only plugin_id (version is read from installed plugin)
        backup = await installer._create_backup("test-plugin")

        assert backup is not None
        assert backup.plugin_id == "test-plugin"
        assert backup.version == "1.0.0"
        assert Path(backup.backup_path).exists()

    @pytest.mark.asyncio
    async def test_backup_exists_after_creation(
        self, installer: PluginInstallerV2, plugins_dir: Path
    ) -> None:
        """Test that backup directory and files exist after backup creation."""
        from backend.plugins.gallery.models import InstalledPlugin

        # Create a mock installed plugin
        plugin_dir = plugins_dir / "default" / "test-plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "plugin.py").write_text("# Original code")
        (plugin_dir / "manifest.json").write_text('{"id": "test-plugin", "version": "1.0.0"}')

        # Register the plugin
        installer._installed["test-plugin"] = InstalledPlugin(
            id="test-plugin",
            version="1.0.0",
            installed_at=datetime.now(),
            install_path=str(plugin_dir),
            state="enabled",
            config={},
        )

        # Create backup (takes only plugin_id)
        backup = await installer._create_backup("test-plugin")
        assert backup is not None

        # Verify backup path exists and has content
        backup_path = Path(backup.backup_path)
        assert backup_path.exists()
        assert (backup_path / "plugin.py").exists()
        assert (backup_path / "plugin.py").read_text() == "# Original code"

    @pytest.mark.asyncio
    async def test_install_from_vspkg_success(
        self, installer: PluginInstallerV2, sample_vspkg: Path, plugins_dir: Path
    ) -> None:
        """Test successful installation from .vspkg."""
        result = await installer.install_from_vspkg(sample_vspkg)

        assert result.success is True
        assert result.plugin_id == "test-plugin"
        assert result.version == "1.0.0"
        assert result.install_path is not None
        assert result.transaction_id is not None

        # Verify plugin was installed
        assert installer.is_installed("test-plugin")

    @pytest.mark.asyncio
    async def test_install_from_vspkg_no_verify(
        self, installer: PluginInstallerV2, sample_vspkg: Path
    ) -> None:
        """Test installation without verification."""
        result = await installer.install_from_vspkg(sample_vspkg, verify=False)

        assert result.success is True
        assert result.verification is None

    @pytest.mark.asyncio
    async def test_install_from_vspkg_invalid_package(
        self, installer: PluginInstallerV2, tmp_path: Path
    ) -> None:
        """Test installation from invalid package."""
        # Create invalid package (not a zip)
        invalid_pkg = tmp_path / "invalid.vspkg"
        invalid_pkg.write_text("not a zip file")

        result = await installer.install_from_vspkg(invalid_pkg)

        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_uninstall_plugin(
        self, installer: PluginInstallerV2, sample_vspkg: Path, plugins_dir: Path
    ) -> None:
        """Test plugin uninstallation."""
        # First install
        install_result = await installer.install_from_vspkg(sample_vspkg)
        assert install_result.success is True

        # Then uninstall
        result = await installer.uninstall_plugin("test-plugin")

        assert result.success is True
        assert result.rollback_available is True
        assert not installer.is_installed("test-plugin")

    @pytest.mark.asyncio
    async def test_uninstall_nonexistent_plugin(self, installer: PluginInstallerV2) -> None:
        """Test uninstalling a plugin that doesn't exist."""
        result = await installer.uninstall_plugin("nonexistent-plugin")

        assert result.success is False
        assert "not installed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_rollback_after_uninstall(
        self, installer: PluginInstallerV2, sample_vspkg: Path
    ) -> None:
        """Test rolling back an uninstallation."""
        # Install and uninstall
        install_result = await installer.install_from_vspkg(sample_vspkg)
        assert install_result.success is True

        uninstall_result = await installer.uninstall_plugin("test-plugin")
        assert uninstall_result.success is True
        assert not installer.is_installed("test-plugin")

        # Rollback
        rollback_result = await installer.rollback_plugin("test-plugin")

        assert rollback_result.success is True
        assert installer.is_installed("test-plugin")

    @pytest.mark.asyncio
    async def test_update_via_vspkg(
        self, installer: PluginInstallerV2, sample_vspkg: Path, tmp_path: Path
    ) -> None:
        """Test plugin update via .vspkg package (re-install pattern)."""
        # Install v1.0.0
        install_result = await installer.install_from_vspkg(sample_vspkg)
        assert install_result.success is True
        assert installer.get_installed_plugin("test-plugin").version == "1.0.0"

        # Create v2.0.0 package
        new_pkg = tmp_path / "test-plugin-2.0.0.vspkg"
        manifest = {"id": "test-plugin", "version": "2.0.0", "name": "Test Plugin"}

        with zipfile.ZipFile(new_pkg, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("plugin.py", "# v2.0.0")

        # Update by re-installing with new package
        # This is the atomic install flow - existing plugin gets backed up and replaced
        result = await installer.install_from_vspkg(new_pkg)

        assert result.success is True
        assert result.version == "2.0.0"
        assert result.rollback_available is True

        # Verify the update
        plugin = installer.get_installed_plugin("test-plugin")
        assert plugin is not None
        assert plugin.version == "2.0.0"

    @pytest.mark.asyncio
    async def test_transaction_management(
        self, installer: PluginInstallerV2, sample_vspkg: Path
    ) -> None:
        """Test transaction creation and tracking."""
        result = await installer.install_from_vspkg(sample_vspkg)

        assert result.transaction_id is not None

        # Verify transaction was recorded
        transaction = installer._active_transactions.get(result.transaction_id)
        assert transaction is not None
        assert transaction.state == TransactionState.COMMITTED

    @pytest.mark.asyncio
    async def test_list_installed(self, installer: PluginInstallerV2, sample_vspkg: Path) -> None:
        """Test listing installed plugins."""
        # Initially empty
        assert len(installer.get_installed_plugins()) == 0

        # Install a plugin
        await installer.install_from_vspkg(sample_vspkg)

        # Should have one
        installed = installer.get_installed_plugins()
        assert len(installed) == 1
        assert installed[0].id == "test-plugin"

    @pytest.mark.asyncio
    async def test_get_installed(self, installer: PluginInstallerV2, sample_vspkg: Path) -> None:
        """Test getting a specific installed plugin."""
        # Not installed yet
        assert installer.get_installed_plugin("test-plugin") is None

        # Install
        await installer.install_from_vspkg(sample_vspkg)

        # Should be available
        plugin = installer.get_installed_plugin("test-plugin")
        assert plugin is not None
        assert plugin.id == "test-plugin"
        assert plugin.version == "1.0.0"


class TestModuleLevelFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self) -> None:
        """Reset the singleton before each test."""
        import backend.plugins.gallery.installer_v2 as module

        module._installer_v2 = None

    def test_get_installer_v2(self) -> None:
        """Test getting an installer instance."""
        installer = get_installer_v2()

        assert installer is not None
        assert isinstance(installer, PluginInstallerV2)

        # Should return same instance (singleton)
        installer2 = get_installer_v2()
        assert installer is installer2


class TestProgressReporting:
    """Tests for progress reporting functionality."""

    @pytest.fixture
    def plugins_dir(self, tmp_path: Path) -> Path:
        """Create a temporary plugins directory."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        return plugins_dir

    @pytest.fixture
    def sample_vspkg(self, tmp_path: Path) -> Path:
        """Create a sample .vspkg package."""
        package_path = tmp_path / "progress-test-1.0.0.vspkg"
        manifest = {"id": "progress-test", "version": "1.0.0", "name": "Progress Test"}

        with zipfile.ZipFile(package_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("plugin.py", "# Plugin")

        return package_path

    @pytest.mark.asyncio
    async def test_progress_callback_called(self, plugins_dir: Path, sample_vspkg: Path) -> None:
        """Test that progress callback is called during installation."""
        from backend.plugins.gallery.models import InstallPhase, InstallProgress

        progress_reports: list[InstallProgress] = []

        def on_progress(progress: InstallProgress) -> None:
            progress_reports.append(progress)

        installer = PluginInstallerV2(plugins_dir=plugins_dir)

        result = await installer.install_from_vspkg(sample_vspkg, progress_callback=on_progress)

        assert result.success is True
        assert len(progress_reports) > 0

        # Verify we have progress for key phases
        phases = [p.phase for p in progress_reports]
        assert InstallPhase.VERIFYING in phases
        # Use EXTRACTING or ACTIVATING instead of INSTALLING (which doesn't exist)
        assert InstallPhase.EXTRACTING in phases or InstallPhase.ACTIVATING in phases
