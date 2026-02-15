"""
Runtime Engine Manager
Manages engines that run as separate processes/servers

DEPRECATION NOTICE (GAP-ENG-003):
    This module is maintained for backward compatibility.
    New code should use EnhancedRuntimeEngine from runtime_engine_enhanced.py
    which provides:
    - Lifecycle management
    - Port allocation
    - Resource management
    - Security policies
    - Hook registry support
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


class RuntimeEngine:
    """
    Manages a runtime engine that runs as a separate process/server.

    .. deprecated::
        Use EnhancedRuntimeEngine from runtime_engine_enhanced.py instead.
        RuntimeEngine is maintained for backward compatibility only.
    """

    def __init__(self, manifest: dict[str, Any], workspace_root: str = "."):
        """
        Initialize runtime engine from manifest.

        Args:
            manifest: Runtime manifest dictionary
            workspace_root: Root directory of workspace
        """
        self.manifest = manifest
        self.workspace_root = Path(workspace_root)
        self.process: subprocess.Popen | None = None
        self.engine_id = manifest["id"]
        self.display_name = manifest.get("displayName", self.engine_id)
        self.engine_type = manifest.get("type", "unknown")
        self.tasks = manifest.get("tasks", [])

    def start(self) -> bool:
        """
        Start the engine process.

        Returns:
            True if started successfully, False otherwise
        """
        if self.process is not None:
            logger.warning(f"Engine {self.engine_id} already running")
            return True

        entry = self.manifest.get("entry", {})
        if entry.get("kind") != "python":
            logger.error(f"Unsupported entry kind: {entry.get('kind')}")
            return False

        # Resolve executable path
        exe_path = entry.get("exe", "")
        if exe_path.startswith(".."):
            # Relative path from manifest location
            manifest_dir = Path(self.manifest.get("_manifest_path", ".")).parent
            exe_path = (manifest_dir / exe_path).resolve()
        else:
            exe_path = Path(exe_path)

        if not exe_path.exists():
            logger.error(f"Executable not found: {exe_path}")
            return False

        # Build command
        args = entry.get("args", [])
        cmd = [str(exe_path), *args]

        try:
            logger.info(f"Starting engine {self.engine_id}: {cmd}")
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            # Wait a bit for startup
            time.sleep(2)

            # Check if process is still running
            if self.process.poll() is not None:
                logger.error(f"Engine {self.engine_id} exited immediately")
                return False

            # Check health if available
            if self.is_healthy():
                logger.info(f"Engine {self.engine_id} started and healthy")
                return True
            else:
                logger.warning(f"Engine {self.engine_id} started but health check failed")
                return True  # Still return True, health might be delayed

        except Exception as e:
            logger.error(f"Failed to start engine {self.engine_id}: {e}")
            return False

    def stop(self):
        """Stop the engine process."""
        if self.process is not None:
            logger.info(f"Stopping engine {self.engine_id}")
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Engine {self.engine_id} did not terminate, killing")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping engine {self.engine_id}: {e}")
            finally:
                self.process = None

    def is_running(self) -> bool:
        """Check if engine process is running."""
        if self.process is None:
            return False
        return self.process.poll() is None

    def is_healthy(self) -> bool:
        """
        Check engine health.

        Returns:
            True if engine is healthy, False otherwise
        """
        health = self.manifest.get("health", {})
        if not health:
            # No health check defined, assume healthy if running
            return self.is_running()

        kind = health.get("kind")
        if kind == "http":
            url = health.get("url")
            if url:
                try:
                    response = requests.get(url, timeout=2)
                    return response.status_code == 200
                except Exception as e:
                    logger.debug(f"Health check failed for {self.engine_id}: {e}")
                    return False

        # Unknown health check kind
        return self.is_running()

    def supports_task(self, task: str) -> bool:
        """Check if engine supports a specific task."""
        return task in self.tasks

    def get_info(self) -> dict[str, Any]:
        """Get engine information."""
        return {
            "id": self.engine_id,
            "display_name": self.display_name,
            "type": self.engine_type,
            "tasks": self.tasks,
            "running": self.is_running(),
            "healthy": self.is_healthy()
        }


class RuntimeEngineManager:
    """
    Manages multiple runtime engines.

    .. deprecated::
        Use EnhancedRuntimeEngineManager from runtime_engine_enhanced.py instead.
        RuntimeEngineManager is maintained for backward compatibility only.
    """

    def __init__(self, workspace_root: str = "."):
        """Initialize runtime engine manager."""
        self.workspace_root = Path(workspace_root)
        self.engines: dict[str, RuntimeEngine] = {}

    def load_engine(self, manifest_path: str) -> RuntimeEngine | None:
        """
        Load an engine from a runtime manifest.

        Args:
            manifest_path: Path to runtime.manifest.json file

        Returns:
            RuntimeEngine instance or None
        """
        try:
            with open(manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)

            # Store manifest path for relative path resolution
            manifest["_manifest_path"] = str(Path(manifest_path).absolute())

            engine = RuntimeEngine(manifest, str(self.workspace_root))
            self.engines[engine.engine_id] = engine

            logger.info(f"Loaded runtime engine: {engine.engine_id}")
            return engine

        except Exception as e:
            logger.error(f"Failed to load engine from {manifest_path}: {e}")
            return None

    def find_runtime_manifests(self, engines_root: str = "engines") -> dict[str, str]:
        """
        Find all runtime manifest files.

        Args:
            engines_root: Root directory containing engine manifests

        Returns:
            Dictionary mapping engine_id to manifest file path
        """
        manifests = {}
        engines_dir = Path(engines_root)

        if not engines_dir.exists():
            logger.warning(f"Engines directory not found: {engines_root}")
            return manifests

        # Search for runtime.manifest.json files
        for manifest_file in engines_dir.rglob("runtime.manifest.json"):
            try:
                with open(manifest_file, encoding='utf-8') as f:
                    manifest = json.load(f)
                engine_id = manifest.get("id")
                if engine_id:
                    manifests[engine_id] = str(manifest_file)
            except Exception as e:
                logger.error(f"Failed to read manifest {manifest_file}: {e}")

        logger.info(f"Found {len(manifests)} runtime engine manifests")
        return manifests

    def load_all_engines(self, engines_root: str = "engines"):
        """Load all runtime engines from manifests."""
        manifests = self.find_runtime_manifests(engines_root)

        for _engine_id, manifest_path in manifests.items():
            self.load_engine(manifest_path)

    def start_engine(self, engine_id: str) -> bool:
        """Start an engine by ID."""
        if engine_id not in self.engines:
            logger.error(f"Engine not found: {engine_id}")
            return False

        return self.engines[engine_id].start()

    def stop_engine(self, engine_id: str):
        """Stop an engine by ID."""
        if engine_id in self.engines:
            self.engines[engine_id].stop()

    def get_engine(self, engine_id: str) -> RuntimeEngine | None:
        """Get engine by ID."""
        return self.engines.get(engine_id)

    def get_engine_for_task(self, task: str, prefer_default: bool = True) -> RuntimeEngine | None:
        """
        Get an engine that supports a specific task.

        Args:
            task: Task name
            prefer_default: If True, prefer default engine for task type

        Returns:
            RuntimeEngine instance or None
        """
        # Map task to task type
        task_type_map = {
            "tts": "tts",
            "clone_infer": "tts",
            "embed_voice": "tts",
            "text_to_image": "image_gen",
            "image_to_image": "image_gen",
            "image_to_video": "video_gen",
            "video_generation": "video_gen"
        }

        task_type = task_type_map.get(task, task)

        # Try to get default engine if prefer_default
        if prefer_default:
            try:
                from app.core.engines.config import get_engine_config
                config = get_engine_config()
                default_id = config.get_default_engine(task_type)
                if default_id and default_id in self.engines:
                    engine = self.engines[default_id]
                    if engine.supports_task(task):
                        return engine
            except Exception as e:
                logger.debug(f"Failed to get default engine: {e}")

        # Fallback to any engine that supports the task
        for engine in self.engines.values():
            if engine.supports_task(task):
                return engine

        return None

    def list_engines(self) -> list[str]:
        """List all loaded engine IDs."""
        return list(self.engines.keys())

    def stop_all(self):
        """Stop all engines."""
        for engine in self.engines.values():
            engine.stop()

