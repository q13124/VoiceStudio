"""
VoiceStudio Plugin System with Hot-Reload
Implements the plugin system from the Unified Implementation Map
"""

import os
import json
import time
import importlib
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Protocol, Type
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3


# Plugin Protocols
class EnginePlugin(Protocol):
    """Protocol for engine plugins"""

    id: str
    languages: List[str]
    quality: List[str]

    def healthy(self) -> bool: ...
    def current_load(self) -> float: ...
    def supports(self, language: str, tier: str) -> bool: ...
    def tts(self, *, text: str, voice_profile: Dict, params: Dict) -> bytes: ...


class EffectPlugin(Protocol):
    """Protocol for DSP effect plugins"""

    id: str
    name: str

    def process(self, audio_data: bytes, params: Dict) -> bytes: ...


class AnalyzerPlugin(Protocol):
    """Protocol for analyzer plugins"""

    id: str
    name: str

    def analyze(self, audio_data: bytes, params: Dict) -> Dict[str, Any]: ...


@dataclass
class PluginInfo:
    id: str
    name: str
    version: str
    type: str  # 'engine', 'effect', 'analyzer'
    path: str
    enabled: bool = True
    loaded_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PluginRegistry:
    """Central plugin registry with hot-reload capabilities"""

    def __init__(self, registry_path: str, plugin_directories: List[str]):
        self.registry_path = Path(registry_path)
        self.plugin_directories = [Path(d) for d in plugin_directories]
        self.registry_file = self.registry_path / "registry.json"
        self.stamp_file = self.registry_path / "registry.json.stamp"

        # Plugin storage
        self._plugins: Dict[str, PluginInfo] = {}
        self._loaded_modules: Dict[str, Any] = {}

        # Hot-reload monitoring
        self._watchers: List[threading.Thread] = []
        self._stop_watching = threading.Event()
        self._file_timestamps: Dict[str, float] = {}

        # Initialize registry
        self._init_registry()
        self._discover_plugins()
        self._start_file_watchers()

    def _init_registry(self):
        """Initialize the plugin registry"""
        self.registry_path.mkdir(parents=True, exist_ok=True)

        if not self.registry_file.exists():
            initial_registry = {
                "plugins": [],
                "scopes": ["engine", "effect", "analyzer"],
                "hot_reload": True,
                "last_updated": datetime.now().isoformat(),
            }
            with self.registry_file.open("w", encoding="utf-8") as f:
                json.dump(initial_registry, f, indent=2)

    def _discover_plugins(self):
        """Discover plugins in plugin directories"""
        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                continue

            for plugin_file in plugin_dir.glob("*.py"):
                try:
                    plugin_info = self._load_plugin_info(plugin_file)
                    if plugin_info:
                        self._plugins[plugin_info.id] = plugin_info
                except Exception as e:
                    print(f"Warning: Could not load plugin {plugin_file}: {e}")

        self._save_registry()

    def _load_plugin_info(self, plugin_file: Path) -> Optional[PluginInfo]:
        """Load plugin information from file"""
        try:
            # Read plugin file to extract metadata
            with plugin_file.open("r", encoding="utf-8") as f:
                content = f.read()

            # Extract plugin metadata (simple parsing)
            plugin_id = plugin_file.stem
            plugin_name = plugin_id.replace("_", " ").title()
            version = "1.0.0"
            plugin_type = "engine"  # Default

            # Try to extract metadata from comments
            lines = content.split("\n")
            for line in lines:
                if line.strip().startswith("#"):
                    line = line.strip()[1:].strip()
                    if line.startswith("Plugin:"):
                        plugin_name = line.split(":", 1)[1].strip()
                    elif line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                    elif line.startswith("Type:"):
                        plugin_type = line.split(":", 1)[1].strip()

            # Determine plugin type from file name or content
            if "engine" in plugin_file.name.lower():
                plugin_type = "engine"
            elif "effect" in plugin_file.name.lower():
                plugin_type = "effect"
            elif "analyzer" in plugin_file.name.lower():
                plugin_type = "analyzer"

            return PluginInfo(
                id=plugin_id,
                name=plugin_name,
                version=version,
                type=plugin_type,
                path=str(plugin_file),
                last_modified=datetime.fromtimestamp(plugin_file.stat().st_mtime),
            )

        except Exception as e:
            print(f"Error loading plugin info from {plugin_file}: {e}")
            return None

    def _save_registry(self):
        """Save plugin registry to file"""
        registry_data = {
            "plugins": [
                {
                    "id": p.id,
                    "name": p.name,
                    "version": p.version,
                    "type": p.type,
                    "path": p.path,
                    "enabled": p.enabled,
                    "loaded_at": p.loaded_at.isoformat() if p.loaded_at else None,
                    "last_modified": (
                        p.last_modified.isoformat() if p.last_modified else None
                    ),
                    "metadata": p.metadata,
                }
                for p in self._plugins.values()
            ],
            "scopes": ["engine", "effect", "analyzer"],
            "hot_reload": True,
            "last_updated": datetime.now().isoformat(),
        }

        with self.registry_file.open("w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2)

        # Touch stamp file for UI hot-reload
        self.stamp_file.touch()

    def _start_file_watchers(self):
        """Start file watchers for hot-reload"""
        for plugin_dir in self.plugin_directories:
            if plugin_dir.exists():
                watcher = threading.Thread(
                    target=self._watch_directory, args=(plugin_dir,), daemon=True
                )
                watcher.start()
                self._watchers.append(watcher)

    def _watch_directory(self, directory: Path):
        """Watch directory for changes"""
        while not self._stop_watching.is_set():
            try:
                for plugin_file in directory.glob("*.py"):
                    current_mtime = plugin_file.stat().st_mtime
                    file_key = str(plugin_file)

                    if file_key in self._file_timestamps:
                        if current_mtime > self._file_timestamps[file_key]:
                            print(f"Plugin file changed: {plugin_file}")
                            self._reload_plugin(plugin_file)
                            self._file_timestamps[file_key] = current_mtime
                    else:
                        self._file_timestamps[file_key] = current_mtime

                time.sleep(1)  # Check every second

            except Exception as e:
                print(f"Error in file watcher for {directory}: {e}")
                time.sleep(5)  # Wait longer on error

    def _reload_plugin(self, plugin_file: Path):
        """Reload a specific plugin"""
        try:
            plugin_id = plugin_file.stem

            # Unload existing module if loaded
            if plugin_id in self._loaded_modules:
                module = self._loaded_modules[plugin_id]
                if hasattr(module, "__file__"):
                    importlib.reload(module)
                else:
                    del self._loaded_modules[plugin_id]

            # Reload plugin info
            plugin_info = self._load_plugin_info(plugin_file)
            if plugin_info:
                plugin_info.loaded_at = datetime.now()
                self._plugins[plugin_id] = plugin_info
                self._save_registry()
                print(f"Reloaded plugin: {plugin_id}")

        except Exception as e:
            print(f"Error reloading plugin {plugin_file}: {e}")

    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin"""
        if plugin_id not in self._plugins:
            return False

        plugin_info = self._plugins[plugin_id]

        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(plugin_id, plugin_info.path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._loaded_modules[plugin_id] = module
            plugin_info.loaded_at = datetime.now()
            plugin_info.enabled = True

            self._save_registry()
            return True

        except Exception as e:
            print(f"Error loading plugin {plugin_id}: {e}")
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin"""
        if plugin_id not in self._loaded_modules:
            return False

        try:
            del self._loaded_modules[plugin_id]
            if plugin_id in self._plugins:
                self._plugins[plugin_id].enabled = False
                self._plugins[plugin_id].loaded_at = None

            self._save_registry()
            return True

        except Exception as e:
            print(f"Error unloading plugin {plugin_id}: {e}")
            return False

    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """Get loaded plugin module"""
        return self._loaded_modules.get(plugin_id)

    def list_plugins(self, plugin_type: Optional[str] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by type"""
        plugins = list(self._plugins.values())
        if plugin_type:
            plugins = [p for p in plugins if p.type == plugin_type]
        return plugins

    def get_engine_plugins(self) -> List[PluginInfo]:
        """Get all engine plugins"""
        return self.list_plugins("engine")

    def get_effect_plugins(self) -> List[PluginInfo]:
        """Get all effect plugins"""
        return self.list_plugins("effect")

    def get_analyzer_plugins(self) -> List[PluginInfo]:
        """Get all analyzer plugins"""
        return self.list_plugins("analyzer")

    def discover(self) -> Dict[str, Dict]:
        """Discover plugin capabilities (for API)"""
        result = {}

        for plugin_id, plugin_info in self._plugins.items():
            if not plugin_info.enabled:
                continue

            module = self._loaded_modules.get(plugin_id)
            if not module:
                continue

            try:
                if plugin_info.type == "engine":
                    # Get engine capabilities
                    if hasattr(module, "Plugin"):
                        plugin_instance = module.Plugin()
                        result[plugin_id] = {
                            "type": "engine",
                            "healthy": plugin_instance.healthy(),
                            "load": plugin_instance.current_load(),
                            "languages": getattr(plugin_instance, "languages", []),
                            "quality": getattr(plugin_instance, "quality", []),
                            "loaded": True,
                        }
                    else:
                        result[plugin_id] = {
                            "type": "engine",
                            "healthy": False,
                            "load": 1.0,
                            "languages": [],
                            "quality": [],
                            "loaded": False,
                            "error": "No Plugin class found",
                        }

                elif plugin_info.type == "effect":
                    result[plugin_id] = {
                        "type": "effect",
                        "name": plugin_info.name,
                        "loaded": True,
                    }

                elif plugin_info.type == "analyzer":
                    result[plugin_id] = {
                        "type": "analyzer",
                        "name": plugin_info.name,
                        "loaded": True,
                    }

            except Exception as e:
                result[plugin_id] = {
                    "type": plugin_info.type,
                    "loaded": False,
                    "error": str(e),
                }

        return result

    def stop_watching(self):
        """Stop file watchers"""
        self._stop_watching.set()
        for watcher in self._watchers:
            watcher.join(timeout=1)


# Global plugin registry instance
_plugin_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance"""
    global _plugin_registry

    if _plugin_registry is None:
        from config.config_loader import get_plugin_config

        plugin_config = get_plugin_config()

        _plugin_registry = PluginRegistry(
            registry_path=plugin_config.registry_path,
            plugin_directories=plugin_config.plugin_directories,
        )

    return _plugin_registry


def discover_plugins() -> Dict[str, Dict]:
    """Discover all plugins (for API)"""
    return get_plugin_registry().discover()


def load_plugin(plugin_id: str) -> bool:
    """Load a specific plugin"""
    return get_plugin_registry().load_plugin(plugin_id)


def unload_plugin(plugin_id: str) -> bool:
    """Unload a specific plugin"""
    return get_plugin_registry().unload_plugin(plugin_id)


def get_plugin(plugin_id: str) -> Optional[Any]:
    """Get a loaded plugin"""
    return get_plugin_registry().get_plugin(plugin_id)


if __name__ == "__main__":
    # Test plugin registry
    registry = get_plugin_registry()

    print("Available plugins:")
    for plugin in registry.list_plugins():
        print(f"  {plugin.id} ({plugin.type}) - {plugin.name}")

    print("\nPlugin discovery:")
    discovery = registry.discover()
    for plugin_id, info in discovery.items():
        print(f"  {plugin_id}: {info}")
