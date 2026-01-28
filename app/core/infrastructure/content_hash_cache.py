"""
Content Hash Cache Module for VoiceStudio
Content hashing and caching system for duplicate detection and fast lookups

Compatible with:
- Python 3.10+
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentHashCache:
    """
    Content Hash Cache for file hashing and duplicate detection.

    Supports:
    - File content hashing
    - Hash caching
    - Duplicate detection
    - Fast lookups
    - Cache persistence
    - Cache invalidation
    """

    def __init__(self, cache_file: Optional[Path] = None):
        """
        Initialize Content Hash Cache.

        Args:
            cache_file: Optional path to cache file for persistence
        """
        self.cache_file = cache_file or Path(".content_hash_cache.json")
        self._hash_cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def compute_hash(
        self, file_path: Path, algorithm: str = "sha256", chunk_size: int = 8192
    ) -> str:
        """
        Compute content hash for a file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, sha1, md5)
            chunk_size: Chunk size for reading file

        Returns:
            Hexadecimal hash string
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check cache first
        cache_key = str(file_path.absolute())
        if cache_key in self._hash_cache:
            cached_entry = self._hash_cache[cache_key]
            cached_mtime = cached_entry.get("mtime")
            current_mtime = file_path.stat().st_mtime

            if cached_mtime == current_mtime:
                logger.debug(f"Using cached hash for {file_path}")
                return cached_entry["hash"]

        # Compute hash
        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_obj.update(chunk)

        hash_value = hash_obj.hexdigest()

        # Cache result
        self._hash_cache[cache_key] = {
            "hash": hash_value,
            "algorithm": algorithm,
            "mtime": file_path.stat().st_mtime,
            "size": file_path.stat().st_size,
            "computed_at": datetime.utcnow().isoformat(),
        }

        logger.debug(f"Computed hash for {file_path}: {hash_value[:16]}...")
        return hash_value

    def get_hash(self, file_path: Path) -> Optional[str]:
        """
        Get cached hash for a file.

        Args:
            file_path: Path to file

        Returns:
            Hash string or None if not cached
        """
        file_path = Path(file_path)
        cache_key = str(file_path.absolute())

        if cache_key not in self._hash_cache:
            return None

        cached_entry = self._hash_cache[cache_key]
        cached_mtime = cached_entry.get("mtime")
        current_mtime = file_path.stat().st_mtime

        if cached_mtime != current_mtime:
            # File modified, invalidate cache
            del self._hash_cache[cache_key]
            return None

        return cached_entry["hash"]

    def find_duplicates(
        self, file_paths: List[Path], algorithm: str = "sha256"
    ) -> Dict[str, List[str]]:
        """
        Find duplicate files by content hash.

        Args:
            file_paths: List of file paths to check
            algorithm: Hash algorithm to use

        Returns:
            Dictionary mapping hash to list of file paths with that hash
        """
        hash_to_files: Dict[str, List[str]] = {}

        for file_path in file_paths:
            try:
                file_path = Path(file_path)
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    continue

                hash_value = self.compute_hash(file_path, algorithm=algorithm)

                if hash_value not in hash_to_files:
                    hash_to_files[hash_value] = []

                hash_to_files[hash_value].append(str(file_path.absolute()))

            except Exception as e:
                logger.warning(f"Failed to hash {file_path}: {e}")
                continue

        # Filter to only duplicates (more than one file per hash)
        duplicates = {
            hash_value: files
            for hash_value, files in hash_to_files.items()
            if len(files) > 1
        }

        return duplicates

    def is_duplicate(self, file_path: Path, algorithm: str = "sha256") -> bool:
        """
        Check if a file is a duplicate of any cached file.

        Args:
            file_path: Path to file to check
            algorithm: Hash algorithm to use

        Returns:
            True if duplicate found
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return False

        hash_value = self.compute_hash(file_path, algorithm=algorithm)

        # Check if this hash exists for a different file
        for cached_path, cached_entry in self._hash_cache.items():
            if cached_path != str(file_path.absolute()):
                if cached_entry.get("hash") == hash_value:
                    return True

        return False

    def get_files_by_hash(self, hash_value: str) -> List[str]:
        """
        Get all files with a specific hash.

        Args:
            hash_value: Hash value to search for

        Returns:
            List of file paths with that hash
        """
        files = []
        for cached_path, cached_entry in self._hash_cache.items():
            if cached_entry.get("hash") == hash_value:
                files.append(cached_path)
        return files

    def invalidate(self, file_path: Optional[Path] = None):
        """
        Invalidate cache entries.

        Args:
            file_path: Optional specific file to invalidate, or None to clear all
        """
        if file_path is None:
            self._hash_cache.clear()
            logger.info("Cache cleared")
        else:
            cache_key = str(Path(file_path).absolute())
            if cache_key in self._hash_cache:
                del self._hash_cache[cache_key]
                logger.info(f"Invalidated cache for {file_path}")

    def _load_cache(self):
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._hash_cache = json.load(f)
                logger.info(f"Loaded {len(self._hash_cache)} cache entries")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self._hash_cache = {}

    def save_cache(self):
        """Save cache to file atomically (tmp + replace)."""
        tmp_path = None
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.cache_file.with_suffix(self.cache_file.suffix + ".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._hash_cache, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.cache_file)
            logger.info(f"Saved {len(self._hash_cache)} cache entries to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_size = sum(
            entry.get("size", 0) for entry in self._hash_cache.values()
        )

        return {
            "total_entries": len(self._hash_cache),
            "total_size": total_size,
            "cache_file": str(self.cache_file),
        }

    def cleanup_invalid_entries(self):
        """Remove cache entries for files that no longer exist."""
        invalid_keys = []
        for cache_key in self._hash_cache.keys():
            file_path = Path(cache_key)
            if not file_path.exists():
                invalid_keys.append(cache_key)

        for key in invalid_keys:
            del self._hash_cache[key]

        if invalid_keys:
            logger.info(f"Removed {len(invalid_keys)} invalid cache entries")


def create_content_hash_cache(
    cache_file: Optional[Path] = None,
) -> ContentHashCache:
    """
    Factory function to create a Content Hash Cache instance.

    Args:
        cache_file: Optional path to cache file for persistence

    Returns:
        Initialized ContentHashCache instance
    """
    return ContentHashCache(cache_file=cache_file)

