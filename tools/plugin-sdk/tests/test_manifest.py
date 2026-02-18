"""
Tests for manifest module.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from voicestudio_plugin_sdk.manifest import (
    Capability,
    CapabilityParameter,
    Permission,
    PermissionScope,
    PluginManifest,
)


class TestPermission:
    """Tests for Permission dataclass."""

    def test_creation_with_string_scope(self):
        """Test creating permission with string scope."""
        perm = Permission(scope="audio.playback", reason="Play audio")
        assert perm.scope == "audio.playback"
        assert perm.reason == "Play audio"
        assert perm.required is True

    def test_creation_with_enum_scope(self):
        """Test creating permission with enum scope."""
        perm = Permission(
            scope=PermissionScope.AUDIO_PLAYBACK,
            reason="Play audio",
            required=False,
        )
        assert perm.scope == PermissionScope.AUDIO_PLAYBACK
        assert perm.required is False

    def test_to_dict(self):
        """Test converting to dictionary."""
        perm = Permission(
            scope=PermissionScope.STORAGE_LOCAL,
            reason="Store data",
        )
        data = perm.to_dict()
        assert data["scope"] == "storage.local"
        assert data["reason"] == "Store data"

    def test_from_dict(self):
        """Test creating from dictionary."""
        perm = Permission.from_dict({
            "scope": "ui.notifications",
            "reason": "Show alerts",
            "required": False,
        })
        assert perm.scope == "ui.notifications"
        assert perm.required is False


class TestCapabilityParameter:
    """Tests for CapabilityParameter dataclass."""

    def test_creation(self):
        """Test creating capability parameter."""
        param = CapabilityParameter(
            name="text",
            type="string",
            description="Text to process",
            required=True,
        )
        assert param.name == "text"
        assert param.type == "string"

    def test_to_dict(self):
        """Test converting to dictionary."""
        param = CapabilityParameter(
            name="count",
            type="integer",
            default=10,
        )
        data = param.to_dict()
        assert data["name"] == "count"
        assert data["default"] == 10

    def test_from_dict(self):
        """Test creating from dictionary."""
        param = CapabilityParameter.from_dict({
            "name": "value",
            "type": "number",
            "required": False,
        })
        assert param.name == "value"
        assert param.required is False


class TestCapability:
    """Tests for Capability dataclass."""

    def test_creation(self):
        """Test creating capability."""
        cap = Capability(
            name="synthesize",
            description="Convert text to speech",
        )
        assert cap.name == "synthesize"
        assert cap.version == "1.0.0"

    def test_with_parameters(self):
        """Test capability with parameters."""
        cap = Capability(
            name="process",
            parameters=[
                CapabilityParameter(name="input", type="string"),
                CapabilityParameter(name="options", type="object"),
            ],
        )
        assert len(cap.parameters) == 2

    def test_to_dict(self):
        """Test converting to dictionary."""
        cap = Capability(
            name="test",
            version="2.0.0",
            returns={"type": "string"},
        )
        data = cap.to_dict()
        assert data["name"] == "test"
        assert data["version"] == "2.0.0"
        assert data["returns"] == {"type": "string"}

    def test_from_dict(self):
        """Test creating from dictionary."""
        cap = Capability.from_dict({
            "name": "capability",
            "description": "A capability",
            "parameters": [
                {"name": "param", "type": "string"}
            ],
        })
        assert cap.name == "capability"
        assert len(cap.parameters) == 1


class TestPluginManifest:
    """Tests for PluginManifest dataclass."""

    def test_creation_minimal(self):
        """Test creating minimal manifest."""
        manifest = PluginManifest(
            id="my-plugin",
            name="My Plugin",
            version="1.0.0",
        )
        assert manifest.id == "my-plugin"
        assert manifest.license == "MIT"

    def test_creation_full(self):
        """Test creating full manifest."""
        manifest = PluginManifest(
            id="full-plugin",
            name="Full Plugin",
            version="2.0.0",
            description="A complete plugin",
            author="Test Author",
            capabilities=[
                Capability(name="cap1"),
                Capability(name="cap2"),
            ],
            permissions=[
                Permission(scope="audio.playback"),
            ],
            engines=["coqui-tts"],
            keywords=["audio", "tts"],
        )
        assert len(manifest.capabilities) == 2
        assert len(manifest.permissions) == 1

    def test_to_dict(self):
        """Test converting to dictionary."""
        manifest = PluginManifest(
            id="test",
            name="Test",
            version="1.0.0",
            min_host_version="1.5.0",
        )
        data = manifest.to_dict()
        assert data["$schema"].endswith("v5.json")
        assert data["manifest_version"] == 5
        assert data["compatibility"]["min_host_version"] == "1.5.0"

    def test_from_dict(self):
        """Test creating from dictionary."""
        manifest = PluginManifest.from_dict({
            "id": "parsed",
            "name": "Parsed Plugin",
            "version": "1.0.0",
            "capabilities": [{"name": "test"}],
        })
        assert manifest.id == "parsed"
        assert len(manifest.capabilities) == 1

    def test_to_json(self):
        """Test serializing to JSON."""
        manifest = PluginManifest(
            id="json-test",
            name="JSON Test",
            version="1.0.0",
        )
        json_str = manifest.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == "json-test"

    def test_from_json(self):
        """Test parsing from JSON."""
        json_str = json.dumps({
            "id": "from-json",
            "name": "From JSON",
            "version": "1.0.0",
        })
        manifest = PluginManifest.from_json(json_str)
        assert manifest.id == "from-json"

    def test_file_roundtrip(self):
        """Test saving and loading from file."""
        manifest = PluginManifest(
            id="file-test",
            name="File Test",
            version="1.0.0",
            description="Testing file operations",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "plugin.json"
            manifest.save(str(path))

            loaded = PluginManifest.from_file(str(path))
            assert loaded.id == manifest.id
            assert loaded.version == manifest.version

    def test_get_capability(self):
        """Test getting capability by name."""
        manifest = PluginManifest(
            id="test",
            name="Test",
            version="1.0.0",
            capabilities=[
                Capability(name="cap1"),
                Capability(name="cap2"),
            ],
        )
        assert manifest.get_capability("cap1") is not None
        assert manifest.get_capability("cap2") is not None
        assert manifest.get_capability("nonexistent") is None

    def test_has_permission(self):
        """Test checking for permissions."""
        manifest = PluginManifest(
            id="test",
            name="Test",
            version="1.0.0",
            permissions=[
                Permission(scope=PermissionScope.AUDIO_PLAYBACK),
                Permission(scope="custom.permission"),
            ],
        )
        assert manifest.has_permission(PermissionScope.AUDIO_PLAYBACK)
        assert manifest.has_permission("audio.playback")
        assert manifest.has_permission("custom.permission")
        assert not manifest.has_permission("missing.permission")


class TestPermissionScope:
    """Tests for PermissionScope enum."""

    def test_all_scopes_defined(self):
        """Test that all expected scopes are defined."""
        assert PermissionScope.AUDIO_PLAYBACK
        assert PermissionScope.STORAGE_LOCAL
        assert PermissionScope.UI_NOTIFICATIONS
        assert PermissionScope.ENGINE_INVOKE

    def test_scope_values(self):
        """Test scope string values."""
        assert PermissionScope.AUDIO_PLAYBACK.value == "audio.playback"
        assert PermissionScope.NETWORK_INTERNET.value == "network.internet"
