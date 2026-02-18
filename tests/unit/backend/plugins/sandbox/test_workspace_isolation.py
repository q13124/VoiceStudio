"""
Unit tests for workspace isolation.

Tests the Workspace, WorkspaceManager, and related classes for
multi-configuration plugin support.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.plugins.sandbox.workspace_isolation import (
    PluginWorkspaceConfig,
    Workspace,
    WorkspaceError,
    WorkspaceExistsError,
    WorkspaceLockError,
    WorkspaceManager,
    WorkspaceMetadata,
    WorkspaceNotFoundError,
    WorkspaceState,
    get_active_workspace,
    get_plugin_data_dir,
    get_workspace_manager,
    reset_workspace_manager,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_workspaces_dir(tmp_path):
    """Create a temporary workspaces directory."""
    workspaces_dir = tmp_path / "workspaces"
    workspaces_dir.mkdir()
    return workspaces_dir


@pytest.fixture
def basic_metadata():
    """Create basic workspace metadata."""
    return WorkspaceMetadata(
        id="test-workspace",
        name="Test Workspace",
        description="A test workspace",
    )


@pytest.fixture
def workspace(tmp_path, basic_metadata):
    """Create a test workspace."""
    workspace_dir = tmp_path / "test-workspace"
    return Workspace(basic_metadata, workspace_dir)


@pytest.fixture
def manager(temp_workspaces_dir):
    """Create a workspace manager."""
    return WorkspaceManager(base_dir=temp_workspaces_dir)


@pytest.fixture(autouse=True)
def reset_global_manager():
    """Reset global manager before each test."""
    reset_workspace_manager()
    yield
    reset_workspace_manager()


# =============================================================================
# Test WorkspaceMetadata
# =============================================================================


class TestWorkspaceMetadata:
    """Tests for WorkspaceMetadata dataclass."""

    def test_basic_creation(self):
        """Test creating basic metadata."""
        metadata = WorkspaceMetadata(
            id="my-workspace",
            name="My Workspace",
        )

        assert metadata.id == "my-workspace"
        assert metadata.name == "My Workspace"
        assert metadata.state == WorkspaceState.INACTIVE
        assert metadata.parent_workspace is None

    def test_to_dict(self, basic_metadata):
        """Test converting metadata to dictionary."""
        data = basic_metadata.to_dict()

        assert data["id"] == "test-workspace"
        assert data["name"] == "Test Workspace"
        assert data["state"] == "inactive"
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "id": "from-dict",
            "name": "From Dict Workspace",
            "description": "Created from dict",
            "state": "active",
            "tags": ["test", "example"],
            "enabled_plugins": ["plugin1", "plugin2"],
            "disabled_plugins": ["plugin3"],
        }

        metadata = WorkspaceMetadata.from_dict(data)

        assert metadata.id == "from-dict"
        assert metadata.name == "From Dict Workspace"
        assert metadata.state == WorkspaceState.ACTIVE
        assert "test" in metadata.tags
        assert "plugin1" in metadata.enabled_plugins
        assert "plugin3" in metadata.disabled_plugins

    def test_roundtrip(self, basic_metadata):
        """Test that to_dict and from_dict are reversible."""
        data = basic_metadata.to_dict()
        restored = WorkspaceMetadata.from_dict(data)

        assert restored.id == basic_metadata.id
        assert restored.name == basic_metadata.name
        assert restored.description == basic_metadata.description


# =============================================================================
# Test PluginWorkspaceConfig
# =============================================================================


class TestPluginWorkspaceConfig:
    """Tests for PluginWorkspaceConfig dataclass."""

    def test_basic_creation(self):
        """Test creating basic config."""
        config = PluginWorkspaceConfig(plugin_id="my.plugin")

        assert config.plugin_id == "my.plugin"
        assert config.enabled is True
        assert config.settings == {}
        assert config.storage_quota_mb is None

    def test_with_settings(self):
        """Test config with settings."""
        config = PluginWorkspaceConfig(
            plugin_id="my.plugin",
            enabled=False,
            settings={"key": "value"},
            storage_quota_mb=100,
        )

        assert config.enabled is False
        assert config.settings["key"] == "value"
        assert config.storage_quota_mb == 100

    def test_to_dict(self):
        """Test converting to dictionary."""
        config = PluginWorkspaceConfig(
            plugin_id="my.plugin",
            settings={"setting1": "value1"},
            storage_quota_mb=256,
        )

        data = config.to_dict()

        assert data["plugin_id"] == "my.plugin"
        assert data["enabled"] is True
        assert data["settings"]["setting1"] == "value1"
        assert data["storage_quota_mb"] == 256

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "plugin_id": "from.dict",
            "enabled": False,
            "settings": {"a": 1},
            "permissions_override": {"read": True},
        }

        config = PluginWorkspaceConfig.from_dict(data)

        assert config.plugin_id == "from.dict"
        assert config.enabled is False
        assert config.settings["a"] == 1
        assert config.permissions_override["read"] is True


# =============================================================================
# Test Workspace
# =============================================================================


class TestWorkspace:
    """Tests for Workspace class."""

    def test_initial_state(self, workspace):
        """Test initial workspace state."""
        assert workspace.state == WorkspaceState.INACTIVE
        assert workspace.id == "test-workspace"
        assert workspace.name == "Test Workspace"

    def test_directories_created(self, workspace):
        """Test that directories are created."""
        assert workspace.workspace_dir.exists()
        assert workspace.data_dir.exists()
        assert workspace.plugins_dir.exists()

    def test_activate_deactivate(self, workspace):
        """Test activating and deactivating workspace."""
        workspace.activate()
        assert workspace.state == WorkspaceState.ACTIVE

        workspace.deactivate()
        assert workspace.state == WorkspaceState.INACTIVE

    def test_lock_unlock(self, workspace):
        """Test locking and unlocking workspace."""
        workspace.lock()
        assert workspace.state == WorkspaceState.LOCKED

        workspace.unlock()
        assert workspace.state == WorkspaceState.INACTIVE

    def test_activate_locked_raises(self, workspace):
        """Test that activating a locked workspace raises."""
        workspace.lock()

        with pytest.raises(WorkspaceLockError):
            workspace.activate()


class TestWorkspacePluginState:
    """Tests for plugin state management in workspace."""

    def test_plugin_enabled_by_default(self, workspace):
        """Test that plugins are enabled by default."""
        assert workspace.is_plugin_enabled("any.plugin") is True

    def test_enable_plugin(self, workspace):
        """Test enabling a plugin."""
        workspace.disable_plugin("my.plugin")
        assert workspace.is_plugin_enabled("my.plugin") is False

        workspace.enable_plugin("my.plugin")
        assert workspace.is_plugin_enabled("my.plugin") is True

    def test_disable_plugin(self, workspace):
        """Test disabling a plugin."""
        workspace.disable_plugin("my.plugin")
        assert workspace.is_plugin_enabled("my.plugin") is False

    def test_enable_plugin_when_locked_raises(self, workspace):
        """Test that enabling plugin when locked raises."""
        workspace.lock()

        with pytest.raises(WorkspaceLockError):
            workspace.enable_plugin("my.plugin")

    def test_disable_plugin_when_locked_raises(self, workspace):
        """Test that disabling plugin when locked raises."""
        workspace.lock()

        with pytest.raises(WorkspaceLockError):
            workspace.disable_plugin("my.plugin")


class TestWorkspacePluginConfig:
    """Tests for plugin configuration in workspace."""

    def test_get_plugin_config_creates_default(self, workspace):
        """Test that get_plugin_config creates default config."""
        config = workspace.get_plugin_config("new.plugin")

        assert config.plugin_id == "new.plugin"
        assert config.enabled is True
        assert config.settings == {}

    def test_set_plugin_config(self, workspace):
        """Test setting plugin configuration."""
        config = PluginWorkspaceConfig(
            plugin_id="my.plugin",
            settings={"key": "value"},
        )

        workspace.set_plugin_config(config)

        retrieved = workspace.get_plugin_config("my.plugin")
        assert retrieved.settings["key"] == "value"

    def test_get_plugin_settings(self, workspace):
        """Test getting merged plugin settings."""
        # Set workspace-level override
        workspace.metadata.plugin_overrides["my.plugin"] = {"global": "value"}

        # Set plugin-specific setting
        config = workspace.get_plugin_config("my.plugin")
        config.settings["specific"] = "setting"
        workspace.set_plugin_config(config)

        settings = workspace.get_plugin_settings("my.plugin")

        assert settings["global"] == "value"
        assert settings["specific"] == "setting"

    def test_set_plugin_setting(self, workspace):
        """Test setting a single plugin setting."""
        workspace.set_plugin_setting("my.plugin", "key", "value")

        settings = workspace.get_plugin_settings("my.plugin")
        assert settings["key"] == "value"


class TestWorkspacePluginStorage:
    """Tests for plugin storage in workspace."""

    def test_get_plugin_data_dir(self, workspace):
        """Test getting plugin data directory."""
        data_dir = workspace.get_plugin_data_dir("my.plugin")

        assert data_dir.exists()
        assert "my_plugin" in str(data_dir)  # Sanitized name

    def test_plugin_data_dir_sanitization(self, workspace):
        """Test that plugin IDs are sanitized for directory names."""
        data_dir = workspace.get_plugin_data_dir("com.example/my.plugin")

        # Should not contain dots or slashes
        dir_name = data_dir.name
        assert "." not in dir_name
        assert "/" not in dir_name

    def test_get_plugin_storage_quota(self, workspace):
        """Test getting plugin storage quota."""
        workspace.set_plugin_storage_quota("my.plugin", 256)

        quota = workspace.get_plugin_storage_quota("my.plugin")
        assert quota == 256

    def test_clear_plugin_data(self, workspace):
        """Test clearing plugin data."""
        data_dir = workspace.get_plugin_data_dir("my.plugin")

        # Create some test files
        (data_dir / "test.txt").write_text("test data")
        assert (data_dir / "test.txt").exists()

        workspace.clear_plugin_data("my.plugin")

        # Directory should exist but be empty
        assert data_dir.exists()
        assert not (data_dir / "test.txt").exists()


class TestWorkspacePersistence:
    """Tests for workspace persistence."""

    def test_config_saved_on_change(self, workspace):
        """Test that config is saved when changes are made."""
        workspace.enable_plugin("test.plugin")

        config_file = workspace.workspace_dir / "workspace.json"
        assert config_file.exists()

    def test_config_loaded_on_init(self, tmp_path, basic_metadata):
        """Test that config is loaded on initialization."""
        workspace_dir = tmp_path / "persist-test"

        # Create initial workspace and make changes
        workspace1 = Workspace(basic_metadata, workspace_dir)
        workspace1.disable_plugin("test.plugin")
        workspace1.set_plugin_setting("test.plugin", "key", "value")

        # Create new workspace instance from same directory
        workspace2 = Workspace(basic_metadata, workspace_dir)

        # Should have loaded the configuration
        assert "test.plugin" in workspace2.metadata.disabled_plugins
        settings = workspace2.get_plugin_settings("test.plugin")
        assert settings.get("key") == "value"


# =============================================================================
# Test WorkspaceManager
# =============================================================================


class TestWorkspaceManager:
    """Tests for WorkspaceManager class."""

    def test_default_workspace_created(self, manager):
        """Test that default workspace is created on init."""
        assert manager.has_workspace(WorkspaceManager.DEFAULT_WORKSPACE_ID)

    def test_default_workspace_activated(self, manager):
        """Test that default workspace is activated."""
        assert manager.active_workspace is not None
        assert manager.active_workspace_id == WorkspaceManager.DEFAULT_WORKSPACE_ID

    def test_create_workspace(self, manager):
        """Test creating a new workspace."""
        workspace = manager.create_workspace(
            workspace_id="new-workspace",
            name="New Workspace",
            description="A new test workspace",
        )

        assert workspace.id == "new-workspace"
        assert manager.has_workspace("new-workspace")

    def test_create_duplicate_raises(self, manager):
        """Test that creating duplicate workspace raises."""
        manager.create_workspace("test", "Test")

        with pytest.raises(WorkspaceExistsError):
            manager.create_workspace("test", "Test Again")

    def test_get_workspace(self, manager):
        """Test getting a workspace."""
        manager.create_workspace("get-test", "Get Test")

        workspace = manager.get_workspace("get-test")

        assert workspace.id == "get-test"

    def test_get_nonexistent_raises(self, manager):
        """Test that getting non-existent workspace raises."""
        with pytest.raises(WorkspaceNotFoundError):
            manager.get_workspace("nonexistent")

    def test_list_workspaces(self, manager):
        """Test listing workspaces."""
        manager.create_workspace("ws1", "Workspace 1")
        manager.create_workspace("ws2", "Workspace 2")

        workspaces = manager.list_workspaces()

        # Should include default + 2 created
        assert len(workspaces) >= 3
        ids = [ws.id for ws in workspaces]
        assert "ws1" in ids
        assert "ws2" in ids


class TestWorkspaceManagerSwitching:
    """Tests for workspace switching."""

    def test_switch_workspace(self, manager):
        """Test switching workspaces."""
        manager.create_workspace("new-ws", "New Workspace")

        workspace = manager.switch_workspace("new-ws")

        assert workspace.id == "new-ws"
        assert manager.active_workspace_id == "new-ws"
        assert workspace.state == WorkspaceState.ACTIVE

    def test_switch_deactivates_previous(self, manager):
        """Test that switching deactivates previous workspace."""
        manager.create_workspace("ws1", "Workspace 1")
        manager.create_workspace("ws2", "Workspace 2")

        manager.switch_workspace("ws1")
        ws1 = manager.get_workspace("ws1")
        assert ws1.state == WorkspaceState.ACTIVE

        manager.switch_workspace("ws2")
        assert ws1.state == WorkspaceState.INACTIVE

    def test_switch_to_nonexistent_raises(self, manager):
        """Test that switching to non-existent workspace raises."""
        with pytest.raises(WorkspaceNotFoundError):
            manager.switch_workspace("nonexistent")


class TestWorkspaceManagerDeletion:
    """Tests for workspace deletion."""

    def test_delete_workspace(self, manager):
        """Test deleting a workspace."""
        manager.create_workspace("to-delete", "To Delete")

        manager.delete_workspace("to-delete")

        assert not manager.has_workspace("to-delete")

    def test_delete_default_raises(self, manager):
        """Test that deleting default workspace raises."""
        with pytest.raises(WorkspaceError, match="Cannot delete default"):
            manager.delete_workspace(WorkspaceManager.DEFAULT_WORKSPACE_ID)

    def test_delete_active_switches_to_default(self, manager):
        """Test that deleting active workspace switches to default."""
        manager.create_workspace("active-ws", "Active Workspace")
        manager.switch_workspace("active-ws")

        manager.delete_workspace("active-ws")

        assert manager.active_workspace_id == WorkspaceManager.DEFAULT_WORKSPACE_ID


class TestWorkspaceManagerCloning:
    """Tests for workspace cloning."""

    def test_clone_workspace(self, manager):
        """Test cloning a workspace."""
        # Set up source workspace
        source = manager.create_workspace("source", "Source Workspace")
        source.disable_plugin("plugin1")
        source.set_plugin_setting("plugin2", "key", "value")

        # Clone it
        cloned = manager.clone_workspace(
            source_id="source",
            new_id="cloned",
            new_name="Cloned Workspace",
        )

        # Check configuration was copied
        assert cloned.id == "cloned"
        assert cloned.is_plugin_enabled("plugin1") is False
        settings = cloned.get_plugin_settings("plugin2")
        assert settings.get("key") == "value"

    def test_clone_nonexistent_raises(self, manager):
        """Test that cloning non-existent workspace raises."""
        with pytest.raises(WorkspaceNotFoundError):
            manager.clone_workspace("nonexistent", "new", "New")

    def test_clone_to_existing_raises(self, manager):
        """Test that cloning to existing ID raises."""
        manager.create_workspace("source", "Source")
        manager.create_workspace("existing", "Existing")

        with pytest.raises(WorkspaceExistsError):
            manager.clone_workspace("source", "existing", "Conflict")


class TestWorkspaceInheritance:
    """Tests for workspace inheritance."""

    def test_create_with_parent(self, manager):
        """Test creating workspace with parent."""
        manager.create_workspace("parent", "Parent")
        child = manager.create_workspace(
            "child",
            "Child",
            parent_workspace="parent",
        )

        assert child.metadata.parent_workspace == "parent"

    def test_create_with_nonexistent_parent_raises(self, manager):
        """Test that creating with non-existent parent raises."""
        with pytest.raises(WorkspaceNotFoundError):
            manager.create_workspace(
                "child",
                "Child",
                parent_workspace="nonexistent",
            )

    def test_effective_plugin_state_inheritance(self, manager):
        """Test that plugin state is inherited from parent."""
        # Create parent and disable a plugin
        parent = manager.create_workspace("parent", "Parent")
        parent.disable_plugin("inherited.plugin")

        # Create child
        manager.create_workspace("child", "Child", parent_workspace="parent")

        # Check effective state
        state = manager.get_effective_plugin_state("inherited.plugin", "child")

        # Plugin should be disabled due to parent
        assert state["enabled"] is False

    def test_child_can_override_parent(self, manager):
        """Test that child can override parent settings."""
        # Create parent and set a setting
        parent = manager.create_workspace("parent", "Parent")
        parent.set_plugin_setting("my.plugin", "key", "parent_value")

        # Create child and override
        child = manager.create_workspace("child", "Child", parent_workspace="parent")
        child.set_plugin_setting("my.plugin", "key", "child_value")

        # Check effective state
        state = manager.get_effective_plugin_state("my.plugin", "child")

        # Child value should win
        assert state["settings"]["key"] == "child_value"


# =============================================================================
# Test Global Functions
# =============================================================================


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_get_workspace_manager_singleton(self, temp_workspaces_dir):
        """Test that get_workspace_manager returns singleton."""
        with patch.dict("os.environ", {"VOICESTUDIO_WORKSPACES_PATH": str(temp_workspaces_dir)}):
            manager1 = get_workspace_manager()
            manager2 = get_workspace_manager()

            assert manager1 is manager2

    def test_reset_workspace_manager(self, temp_workspaces_dir):
        """Test resetting workspace manager."""
        with patch.dict("os.environ", {"VOICESTUDIO_WORKSPACES_PATH": str(temp_workspaces_dir)}):
            manager1 = get_workspace_manager()
            reset_workspace_manager()
            manager2 = get_workspace_manager()

            assert manager1 is not manager2

    def test_get_active_workspace(self, temp_workspaces_dir):
        """Test getting active workspace."""
        with patch.dict("os.environ", {"VOICESTUDIO_WORKSPACES_PATH": str(temp_workspaces_dir)}):
            workspace = get_active_workspace()

            assert workspace is not None
            assert workspace.id == WorkspaceManager.DEFAULT_WORKSPACE_ID

    def test_get_plugin_data_dir_from_active(self, temp_workspaces_dir):
        """Test getting plugin data dir from active workspace."""
        with patch.dict("os.environ", {"VOICESTUDIO_WORKSPACES_PATH": str(temp_workspaces_dir)}):
            data_dir = get_plugin_data_dir("test.plugin")

            assert data_dir.exists()
            assert "test_plugin" in str(data_dir)


# =============================================================================
# Test WorkspaceState Enum
# =============================================================================


class TestWorkspaceState:
    """Tests for WorkspaceState enum."""

    def test_all_states_defined(self):
        """Test that all expected states are defined."""
        expected_states = ["INACTIVE", "ACTIVE", "LOCKED", "MIGRATING"]

        for state_name in expected_states:
            assert hasattr(WorkspaceState, state_name)

    def test_state_values(self):
        """Test state value strings."""
        assert WorkspaceState.INACTIVE.value == "inactive"
        assert WorkspaceState.ACTIVE.value == "active"
        assert WorkspaceState.LOCKED.value == "locked"
        assert WorkspaceState.MIGRATING.value == "migrating"
