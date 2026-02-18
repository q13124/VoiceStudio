"""
Tests for Plugin Storage Isolation.

Phase 5A: Validates per-plugin storage isolation and path validation.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add backend to path
sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "backend")))

from backend.plugins.sandbox.storage_isolation import (
    PathValidationError,
    PluginStorage,
    QuotaExceededError,
    StorageManager,
    StorageQuota,
    StorageType,
    StorageUsage,
    get_plugin_storage,
    get_storage_manager,
)


class TestStorageQuota:
    """Tests for StorageQuota configuration."""
    
    def test_default_quota(self):
        """Test default values."""
        quota = StorageQuota()
        
        assert quota.max_total_bytes is None
        assert quota.max_file_size_bytes is None
        assert quota.max_file_count is None
    
    def test_from_manifest(self):
        """Test creating quota from manifest."""
        resource_limits = {
            "max_storage_mb": 100,
            "max_file_size_mb": 10,
            "max_file_count": 1000,
        }
        
        quota = StorageQuota.from_manifest(resource_limits)
        
        assert quota.max_total_bytes == 100 * 1024 * 1024
        assert quota.max_file_size_bytes == 10 * 1024 * 1024
        assert quota.max_file_count == 1000
    
    def test_from_manifest_partial(self):
        """Test creating quota with partial manifest data."""
        resource_limits = {"max_storage_mb": 50}
        
        quota = StorageQuota.from_manifest(resource_limits)
        
        assert quota.max_total_bytes == 50 * 1024 * 1024
        assert quota.max_file_size_bytes is None
        assert quota.max_file_count is None


class TestStorageUsage:
    """Tests for StorageUsage data structure."""
    
    def test_to_dict(self):
        """Test serialization."""
        usage = StorageUsage(
            total_bytes=1024 * 1024 * 10,  # 10 MB
            file_count=100,
            largest_file_bytes=1024 * 1024 * 2,  # 2 MB
        )
        
        data = usage.to_dict()
        
        assert data["total_bytes"] == 10 * 1024 * 1024
        assert data["total_mb"] == 10.0
        assert data["file_count"] == 100
        assert data["largest_file_bytes"] == 2 * 1024 * 1024
        assert data["largest_file_mb"] == 2.0


class TestPluginStorage:
    """Tests for PluginStorage."""
    
    @pytest.fixture
    def temp_base(self, tmp_path):
        """Create a temporary base directory."""
        return tmp_path / "plugin_data"
    
    @pytest.fixture
    def storage(self, temp_base):
        """Create a test storage instance."""
        storage = PluginStorage("test.plugin.example", temp_base)
        storage.initialize()
        return storage
    
    def test_initialization(self, temp_base):
        """Test storage initialization creates directories."""
        storage = PluginStorage("test.plugin", temp_base)
        storage.initialize()
        
        assert storage.root.exists()
        assert storage.get_path(StorageType.DATA).exists()
        assert storage.get_path(StorageType.CACHE).exists()
        assert storage.get_path(StorageType.CONFIG).exists()
        assert storage.get_path(StorageType.LOGS).exists()
        assert storage.get_path(StorageType.TEMP).exists()
    
    def test_safe_dir_name(self):
        """Test that plugin IDs are converted to safe directory names."""
        # Test with special characters
        name1 = PluginStorage._safe_dir_name("com.example.plugin")
        assert "/" not in name1
        assert "\\" not in name1
        
        # Test uniqueness
        name2 = PluginStorage._safe_dir_name("com.example.plugin")
        assert name1 == name2  # Same ID produces same name
        
        name3 = PluginStorage._safe_dir_name("com.example.other")
        assert name1 != name3  # Different IDs produce different names
    
    def test_write_and_read_file(self, storage):
        """Test writing and reading files."""
        data = b"Hello, World!"
        
        # Write
        path = storage.write_file("test.txt", data)
        assert path.exists()
        
        # Read
        read_data = storage.read_file("test.txt")
        assert read_data == data
    
    def test_write_nested_path(self, storage):
        """Test writing to nested paths."""
        data = b"Nested content"
        
        path = storage.write_file("subdir/nested/file.txt", data)
        
        assert path.exists()
        assert path.parent.name == "nested"
        assert storage.read_file("subdir/nested/file.txt") == data
    
    def test_delete_file(self, storage):
        """Test file deletion."""
        storage.write_file("to_delete.txt", b"data")
        assert storage.file_exists("to_delete.txt")
        
        result = storage.delete_file("to_delete.txt")
        
        assert result is True
        assert not storage.file_exists("to_delete.txt")
    
    def test_delete_nonexistent(self, storage):
        """Test deleting non-existent file."""
        result = storage.delete_file("nonexistent.txt")
        assert result is False
    
    def test_list_files(self, storage):
        """Test listing files."""
        storage.write_file("file1.txt", b"1")
        storage.write_file("file2.txt", b"2")
        storage.write_file("subdir/file3.txt", b"3")
        
        # Non-recursive
        files = storage.list_files()
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "subdir" in files
        assert len(files) == 3
        
        # Recursive
        files = storage.list_files(recursive=True)
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert any("file3.txt" in f for f in files)
    
    def test_file_exists(self, storage):
        """Test file existence check."""
        assert not storage.file_exists("missing.txt")
        
        storage.write_file("exists.txt", b"data")
        assert storage.file_exists("exists.txt")
    
    def test_get_usage(self, storage):
        """Test usage statistics."""
        storage.write_file("file1.txt", b"x" * 1000)
        storage.write_file("file2.txt", b"y" * 2000)
        
        usage = storage.get_usage()
        
        assert usage.total_bytes >= 3000
        assert usage.file_count >= 2
        assert usage.largest_file_bytes >= 2000
    
    def test_storage_types(self, storage):
        """Test different storage types."""
        storage.write_file("data.txt", b"data", StorageType.DATA)
        storage.write_file("cache.txt", b"cache", StorageType.CACHE)
        storage.write_file("config.txt", b"config", StorageType.CONFIG)
        
        assert storage.file_exists("data.txt", StorageType.DATA)
        assert storage.file_exists("cache.txt", StorageType.CACHE)
        assert storage.file_exists("config.txt", StorageType.CONFIG)
        
        # Files are isolated per type
        assert not storage.file_exists("data.txt", StorageType.CACHE)
    
    def test_clear_storage_type(self, storage):
        """Test clearing a specific storage type."""
        storage.write_file("data.txt", b"data", StorageType.DATA)
        storage.write_file("cache.txt", b"cache", StorageType.CACHE)
        
        storage.clear(StorageType.CACHE)
        
        assert storage.file_exists("data.txt", StorageType.DATA)
        assert not storage.file_exists("cache.txt", StorageType.CACHE)
    
    def test_clear_all(self, storage):
        """Test clearing all storage."""
        storage.write_file("data.txt", b"data", StorageType.DATA)
        storage.write_file("cache.txt", b"cache", StorageType.CACHE)
        
        storage.clear()
        
        assert not storage.file_exists("data.txt", StorageType.DATA)
        assert not storage.file_exists("cache.txt", StorageType.CACHE)
    
    def test_destroy(self, storage):
        """Test destroying all storage."""
        storage.write_file("data.txt", b"data")
        root = storage.root
        
        storage.destroy()
        
        assert not root.exists()


class TestPathValidation:
    """Tests for path validation security."""
    
    @pytest.fixture
    def storage(self, tmp_path):
        """Create a test storage instance."""
        storage = PluginStorage("test.plugin", tmp_path / "plugin_data")
        storage.initialize()
        return storage
    
    def test_valid_relative_path(self, storage):
        """Test valid relative paths."""
        path = storage.validate_path(Path("subdir/file.txt"), StorageType.DATA)
        assert path.is_absolute()
    
    def test_path_traversal_blocked(self, storage):
        """Test that path traversal is blocked."""
        with pytest.raises(PathValidationError):
            storage.validate_path(Path("../../../etc/passwd"), StorageType.DATA)
    
    def test_double_dot_in_middle_blocked(self, storage):
        """Test that .. in the middle of path is blocked."""
        with pytest.raises(PathValidationError):
            storage.validate_path(Path("subdir/../../../secret"), StorageType.DATA)
    
    def test_absolute_path_outside_blocked(self, storage):
        """Test that absolute paths outside storage are blocked."""
        with pytest.raises(PathValidationError):
            storage.validate_path(Path("/etc/passwd"), StorageType.DATA)
    
    def test_valid_absolute_path_inside(self, storage):
        """Test that absolute paths inside storage are allowed."""
        data_path = storage.get_path(StorageType.DATA)
        valid_absolute = data_path / "valid_file.txt"
        
        result = storage.validate_path(valid_absolute, StorageType.DATA)
        assert result == valid_absolute


class TestStorageQuotaEnforcement:
    """Tests for storage quota enforcement."""
    
    @pytest.fixture
    def storage_with_quota(self, tmp_path):
        """Create storage with strict quotas."""
        quota = StorageQuota(
            max_total_bytes=10000,       # 10 KB total
            max_file_size_bytes=5000,    # 5 KB per file
            max_file_count=5,            # 5 files max
        )
        storage = PluginStorage(
            "test.plugin",
            tmp_path / "plugin_data",
            quota,
        )
        storage.initialize()
        return storage
    
    def test_file_size_quota(self, storage_with_quota):
        """Test that file size quota is enforced."""
        # Should succeed (under limit)
        storage_with_quota.write_file("small.txt", b"x" * 1000)
        
        # Should fail (over limit)
        with pytest.raises(QuotaExceededError):
            storage_with_quota.write_file("large.txt", b"x" * 6000)
    
    def test_total_storage_quota(self, storage_with_quota):
        """Test that total storage quota is enforced."""
        # Write several files
        storage_with_quota.write_file("file1.txt", b"x" * 3000)
        storage_with_quota.write_file("file2.txt", b"x" * 3000)
        storage_with_quota.write_file("file3.txt", b"x" * 3000)
        
        # Next write should fail
        with pytest.raises(QuotaExceededError):
            storage_with_quota.write_file("file4.txt", b"x" * 3000)
    
    def test_file_count_quota(self, storage_with_quota):
        """Test that file count quota is enforced."""
        for i in range(5):
            storage_with_quota.write_file(f"file{i}.txt", b"x")
        
        with pytest.raises(QuotaExceededError):
            storage_with_quota.write_file("file5.txt", b"x")
    
    def test_overwrite_doesnt_count_twice(self, storage_with_quota):
        """Test that overwriting a file doesn't double-count storage."""
        storage_with_quota.write_file("file.txt", b"x" * 4000)
        
        # Overwrite should succeed (replaces existing)
        storage_with_quota.write_file("file.txt", b"y" * 4000)


class TestStorageManager:
    """Tests for StorageManager."""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create a test storage manager."""
        return StorageManager(tmp_path / "plugin_data")
    
    def test_get_storage(self, manager):
        """Test getting storage for a plugin."""
        storage = manager.get_storage("test.plugin")
        
        assert storage is not None
        assert storage.root.exists()
        
        # Same instance returned on second call
        storage2 = manager.get_storage("test.plugin")
        assert storage is storage2
    
    def test_has_storage(self, manager):
        """Test checking for storage existence."""
        assert not manager.has_storage("new.plugin")
        
        manager.get_storage("new.plugin")
        
        assert manager.has_storage("new.plugin")
    
    def test_remove_storage(self, manager):
        """Test removing plugin storage."""
        storage = manager.get_storage("to.remove")
        storage.write_file("data.txt", b"data")
        root = storage.root
        
        result = manager.remove_storage("to.remove")
        
        assert result is True
        assert not root.exists()
        assert not manager.has_storage("to.remove")
    
    def test_remove_nonexistent(self, manager):
        """Test removing non-existent storage."""
        result = manager.remove_storage("nonexistent")
        assert result is False
    
    def test_get_total_usage(self, manager):
        """Test getting usage across plugins."""
        storage1 = manager.get_storage("plugin1")
        storage1.write_file("file.txt", b"x" * 1000)
        
        storage2 = manager.get_storage("plugin2")
        storage2.write_file("file.txt", b"x" * 2000)
        
        usage = manager.get_total_usage()
        
        assert "plugin1" in usage
        assert "plugin2" in usage
        assert usage["plugin1"].total_bytes >= 1000
        assert usage["plugin2"].total_bytes >= 2000
    
    def test_cleanup_temp(self, manager):
        """Test cleaning up temp storage for all plugins."""
        storage = manager.get_storage("plugin")
        storage.write_file("temp.txt", b"temp", StorageType.TEMP)
        storage.write_file("data.txt", b"data", StorageType.DATA)
        
        manager.cleanup_temp()
        
        assert not storage.file_exists("temp.txt", StorageType.TEMP)
        assert storage.file_exists("data.txt", StorageType.DATA)
    
    def test_cleanup_cache(self, manager):
        """Test cleaning up cache storage for all plugins."""
        storage = manager.get_storage("plugin")
        storage.write_file("cache.txt", b"cache", StorageType.CACHE)
        storage.write_file("data.txt", b"data", StorageType.DATA)
        
        manager.cleanup_cache()
        
        assert not storage.file_exists("cache.txt", StorageType.CACHE)
        assert storage.file_exists("data.txt", StorageType.DATA)


class TestGlobalManager:
    """Tests for global storage manager."""
    
    def test_get_plugin_storage_convenience(self, tmp_path, monkeypatch):
        """Test convenience function."""
        # Reset global manager
        import backend.plugins.sandbox.storage_isolation as module
        monkeypatch.setattr(module, "_storage_manager", None)
        
        # Use tmp_path for testing
        manager = get_storage_manager(tmp_path / "plugin_data")
        storage = get_plugin_storage("test.convenience")
        
        assert storage is not None
        assert storage.root.exists()
