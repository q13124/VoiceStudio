"""
Unit tests for the testing utilities module.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add SDK to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tools", "plugin-sdk"))

from voicestudio_sdk.audio import AudioBuffer
from voicestudio_sdk.testing import (
    MockHost,
    PluginTestCase,
    create_test_manifest,
    create_test_plugin_directory,
)


class TestMockHost:
    """Tests for MockHost class."""
    
    def test_create_mock_host(self):
        """Test creating a mock host."""
        mock = MockHost()
        assert mock is not None
        assert mock.is_connected is True
    
    @pytest.mark.asyncio
    async def test_log_recording(self):
        """Test that logs are recorded."""
        mock = MockHost()
        
        await mock.log("Test message", level="info")
        await mock.debug("Debug message")
        await mock.warning("Warning message")
        
        logs = mock.get_logs()
        assert len(logs) == 3
        
        assert logs[0].level == "info"
        assert logs[0].message == "Test message"
    
    @pytest.mark.asyncio
    async def test_log_filtering(self):
        """Test filtering logs by level."""
        mock = MockHost()
        
        await mock.info("Info 1")
        await mock.warning("Warning 1")
        await mock.info("Info 2")
        await mock.error("Error 1")
        
        info_logs = mock.get_logs(level="info")
        assert len(info_logs) == 2
        
        error_logs = mock.get_logs(level="error")
        assert len(error_logs) == 1
    
    @pytest.mark.asyncio
    async def test_has_log(self):
        """Test checking for log messages."""
        mock = MockHost()
        
        await mock.info("Processing started")
        await mock.info("Processing item 1")
        
        assert mock.has_log("Processing started")
        assert mock.has_log("Processing", contains=True)
        assert mock.has_log("Processing started", level="info")
        assert not mock.has_log("Processing started", level="error")
        assert not mock.has_log("Nonexistent message")
    
    @pytest.mark.asyncio
    async def test_progress_recording(self):
        """Test that progress updates are recorded."""
        mock = MockHost()
        
        await mock.report_progress(0.25, "Step 1")
        await mock.report_progress(0.5, "Step 2")
        await mock.report_progress(1.0, "Done")
        
        updates = mock.get_progress_updates()
        assert len(updates) == 3
        assert updates[0].progress == 0.25
        assert updates[-1].progress == 1.0
    
    @pytest.mark.asyncio
    async def test_resource_management(self):
        """Test adding and getting resources."""
        mock = MockHost()
        
        mock.add_resource("project://test.txt", b"Hello, World!")
        
        data = await mock.get_resource("project://test.txt")
        assert data == b"Hello, World!"
        
        # Non-existent resource
        data = await mock.get_resource("project://nonexistent.txt")
        assert data is None
    
    @pytest.mark.asyncio
    async def test_resource_string_conversion(self):
        """Test adding string resources."""
        mock = MockHost()
        
        mock.add_resource("project://text.txt", "Hello, World!")
        
        data = await mock.get_resource("project://text.txt")
        assert data == b"Hello, World!"
    
    @pytest.mark.asyncio
    async def test_put_resource(self):
        """Test storing resources."""
        mock = MockHost()
        
        success = await mock.put_resource("project://new.txt", b"New data")
        assert success is True
        
        data = await mock.get_resource("project://new.txt")
        assert data == b"New data"
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing resources."""
        mock = MockHost()
        
        mock.add_resource("project://audio/file1.wav", b"data1")
        mock.add_resource("project://audio/file2.wav", b"data2")
        mock.add_resource("project://config.json", b"config")
        
        all_resources = await mock.list_resources()
        assert len(all_resources) == 3
        
        audio_resources = await mock.list_resources("project://audio/")
        assert len(audio_resources) == 2
    
    @pytest.mark.asyncio
    async def test_notifications(self):
        """Test notification recording."""
        mock = MockHost()
        
        await mock.show_notification("Done!", title="Success", type="success")
        
        notifications = mock.get_notifications()
        assert len(notifications) == 1
        assert notifications[0]["message"] == "Done!"
        assert notifications[0]["type"] == "success"
    
    @pytest.mark.asyncio
    async def test_confirm(self):
        """Test confirmation dialogs."""
        mock = MockHost()
        
        # Default is True
        result = await mock.confirm("Continue?")
        assert result is True
        
        # Set to False
        mock.set_confirm_result(False)
        result = await mock.confirm("Continue?")
        assert result is False
        
        # Confirmations are recorded
        confirmations = mock.get_confirmations()
        assert len(confirmations) == 2
    
    @pytest.mark.asyncio
    async def test_settings(self):
        """Test settings management."""
        mock = MockHost()
        
        mock.set_mock_setting("key1", "value1")
        
        value = await mock.get_setting("key1")
        assert value == "value1"
        
        # Non-existent setting
        value = await mock.get_setting("nonexistent")
        assert value is None
        
        # Set via API
        await mock.set_setting("key2", "value2")
        value = await mock.get_setting("key2")
        assert value == "value2"
    
    @pytest.mark.asyncio
    async def test_capabilities(self):
        """Test capabilities configuration."""
        mock = MockHost()
        
        caps = await mock.get_capabilities()
        assert caps["synthesis"] is True
        
        mock.set_capabilities({"synthesis": False})
        caps = await mock.get_capabilities()
        assert caps["synthesis"] is False
    
    @pytest.mark.asyncio
    async def test_version(self):
        """Test version info."""
        mock = MockHost()
        
        version = await mock.get_version()
        assert "version" in version
        
        mock.set_version("2.0.0", "2")
        version = await mock.get_version()
        assert version["version"] == "2.0.0"
        assert version["api_version"] == "2"
    
    def test_clear_recordings(self):
        """Test clearing all recordings."""
        mock = MockHost()
        
        # Add some data
        mock._logs.append(None)
        mock._progress_updates.append(None)
        mock._notifications.append(None)
        
        mock.clear_recordings()
        
        assert len(mock._logs) == 0
        assert len(mock._progress_updates) == 0
        assert len(mock._notifications) == 0


class TestPluginTestCase:
    """Tests for PluginTestCase class."""
    
    def test_create_test_case(self):
        """Test creating a plugin test case."""
        case = PluginTestCase()
        case.setUp()
        
        assert case.mock_host is not None
        assert case.context is not None
        
        case.tearDown()
    
    def test_create_test_audio(self):
        """Test creating test audio."""
        case = PluginTestCase()
        case.setUp()
        
        try:
            audio = case.create_test_audio(duration=0.5)
            
            assert audio is not None
            assert isinstance(audio, AudioBuffer)
            assert abs(audio.duration - 0.5) < 0.1
        finally:
            case.tearDown()
    
    def test_create_temp_file(self):
        """Test creating temp files."""
        case = PluginTestCase()
        case.setUp()
        
        try:
            path = case.create_temp_file("test content", "test.txt")
            
            assert path.exists()
            assert path.read_text() == "test content"
        finally:
            case.tearDown()
    
    def test_create_temp_dir(self):
        """Test creating temp directories."""
        case = PluginTestCase()
        case.setUp()
        
        try:
            path = case.create_temp_dir("subdir")
            
            assert path.exists()
            assert path.is_dir()
        finally:
            case.tearDown()
    
    def test_assert_valid_audio(self):
        """Test audio validation assertions."""
        case = PluginTestCase()
        case.setUp()
        
        try:
            audio = case.create_test_audio(duration=1.0)
            
            # Should not raise
            case.assert_valid_audio(audio)
            case.assert_valid_audio(audio, min_duration=0.5)
            case.assert_valid_audio(audio, max_duration=2.0)
            
            # Should raise
            with pytest.raises(AssertionError):
                case.assert_valid_audio(audio, min_duration=2.0)
        finally:
            case.tearDown()


class TestCreateTestManifest:
    """Tests for create_test_manifest helper."""
    
    def test_create_minimal_manifest(self):
        """Test creating a minimal manifest."""
        manifest = create_test_manifest()
        
        assert "schema_version" in manifest
        assert manifest["id"] == "com.test.plugin"
        assert manifest["name"] == "Test Plugin"
        assert manifest["version"] == "1.0.0"
        assert manifest["type"] == "synthesis"
    
    def test_create_custom_manifest(self):
        """Test creating a manifest with custom values."""
        manifest = create_test_manifest(
            plugin_id="com.custom.plugin",
            name="Custom Plugin",
            version="2.0.0",
            plugin_type="transcription",
        )
        
        assert manifest["id"] == "com.custom.plugin"
        assert manifest["name"] == "Custom Plugin"
        assert manifest["version"] == "2.0.0"
        assert manifest["type"] == "transcription"
    
    def test_create_manifest_with_kwargs(self):
        """Test creating manifest with extra fields."""
        manifest = create_test_manifest(
            homepage="https://example.com",
            repository="https://github.com/test/plugin",
        )
        
        assert manifest["homepage"] == "https://example.com"
        assert manifest["repository"] == "https://github.com/test/plugin"


class TestCreateTestPluginDirectory:
    """Tests for create_test_plugin_directory helper."""
    
    def test_create_plugin_directory(self):
        """Test creating a plugin directory structure."""
        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "test_plugin"
            
            result = create_test_plugin_directory(plugin_path)
            
            assert result.exists()
            assert (result / "plugin.json").exists()
    
    def test_manifest_content(self):
        """Test that manifest is created correctly."""
        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "test_plugin"
            
            create_test_plugin_directory(
                plugin_path,
                plugin_id="com.test.myplugin",
                name="My Plugin",
            )
            
            manifest = json.loads((plugin_path / "plugin.json").read_text())
            
            assert manifest["id"] == "com.test.myplugin"
            assert manifest["name"] == "My Plugin"
    
    def test_module_creation(self):
        """Test that Python module is created."""
        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "test_plugin"
            
            create_test_plugin_directory(
                plugin_path,
                plugin_id="com.test.myplugin",
                create_module=True,
            )
            
            module_dir = plugin_path / "myplugin"
            assert module_dir.exists()
            assert (module_dir / "__init__.py").exists()
            assert (module_dir / "main.py").exists()
    
    def test_skip_module_creation(self):
        """Test skipping module creation."""
        with tempfile.TemporaryDirectory() as tmp:
            plugin_path = Path(tmp) / "test_plugin"
            
            create_test_plugin_directory(
                plugin_path,
                plugin_id="com.test.myplugin",
                create_module=False,
            )
            
            module_dir = plugin_path / "myplugin"
            assert not module_dir.exists()
