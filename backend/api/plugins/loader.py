"""
Backend Plugin Loader

Loads and registers Python plugins from the plugins/ directory.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger(__name__)


class PluginLoader:
    """Loads and manages backend plugins"""

    def __init__(self, plugins_directory: str | None = None):
        """
        Initialize plugin loader.

        Args:
            plugins_directory: Path to plugins directory (default: plugins/)
        """
        if plugins_directory is None:
            # Default to plugins/ directory in project root
            project_root = Path(__file__).parent.parent.parent
            plugins_directory = str(project_root / "plugins")

        self.plugins_directory = Path(plugins_directory)
        self.loaded_plugins: dict[str, Any] = {}
        self.plugin_metadata: dict[str, dict[str, Any]] = {}

    def load_all_plugins(self, app: FastAPI) -> int:
        """
        Load all plugins from plugins directory.

        Args:
            app: FastAPI application instance

        Returns:
            Number of plugins loaded
        """
        if not self.plugins_directory.exists():
            logger.warning(
                f"Plugins directory does not exist: {self.plugins_directory}"
            )
            return 0

        loaded_count = 0

        # Scan for plugin directories
        for plugin_dir in self.plugins_directory.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Skip hidden directories and example plugin
            if plugin_dir.name.startswith('.') or plugin_dir.name == 'example':
                continue

            try:
                if self._load_plugin(plugin_dir, app):
                    loaded_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to load plugin from {plugin_dir}: {e}",
                    exc_info=True
                )

        logger.info(f"Loaded {loaded_count} plugin(s)")
        return loaded_count

    def _load_plugin(self, plugin_dir: Path, app: FastAPI) -> bool:
        """
        Load a single plugin from directory.

        Args:
            plugin_dir: Plugin directory path
            app: FastAPI application instance

        Returns:
            True if plugin loaded successfully, False otherwise
        """
        manifest_path = plugin_dir / "manifest.json"

        if not manifest_path.exists():
            logger.debug(f"No manifest.json in {plugin_dir}, skipping")
            return False

        # Load manifest
        try:
            with open(manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load manifest from {manifest_path}: {e}")
            return False

        plugin_name = manifest.get("name")
        if not plugin_name:
            logger.error(f"Plugin manifest missing 'name' field: {manifest_path}")
            return False

        # Check if plugin provides backend routes
        capabilities = manifest.get("capabilities", {})
        if not capabilities.get("backend_routes", False):
            logger.debug(f"Plugin {plugin_name} does not provide backend routes")
            return False

        # Get entry point
        entry_points = manifest.get("entry_points", {})
        backend_entry = entry_points.get("backend")

        if not backend_entry:
            logger.warning(
                f"Plugin {plugin_name} has backend_routes=True but no "
                f"backend entry_point"
            )
            return False

        # Load plugin module
        plugin_py = plugin_dir / "plugin.py"
        if not plugin_py.exists():
            logger.warning(f"Plugin {plugin_name} missing plugin.py")
            return False

        try:
            # Import plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_name}",
                plugin_py
            )

            if spec is None or spec.loader is None:
                logger.error(f"Failed to create module spec for {plugin_py}")
                return False

            module = importlib.util.module_from_spec(spec)

            # Snapshot sys.modules before loading so we can clean up
            # plugin-local bare imports (e.g. "processor", "adapter")
            # that would otherwise contaminate the next plugin load.
            modules_before = set(sys.modules.keys())

            # Add plugin directory to path for imports
            sys.path.insert(0, str(plugin_dir))

            try:
                spec.loader.exec_module(module)
            finally:
                # Remove from path after loading
                if str(plugin_dir) in sys.path:
                    sys.path.remove(str(plugin_dir))

                # Remove any bare modules added during this plugin load
                # whose origin is inside the plugin directory, so the next
                # plugin gets its own fresh copy.
                new_modules = set(sys.modules.keys()) - modules_before
                plugin_dir_str = str(plugin_dir)
                for mod_name in new_modules:
                    mod = sys.modules.get(mod_name)
                    if mod is None:
                        continue
                    origin = getattr(getattr(mod, "__spec__", None), "origin", None) or ""
                    mod_file = getattr(mod, "__file__", None) or ""
                    if (
                        origin.startswith(plugin_dir_str)
                        or mod_file.startswith(plugin_dir_str)
                    ):
                        del sys.modules[mod_name]

            # Call entry point function
            entry_parts = backend_entry.split('.')
            if len(entry_parts) == 1:
                # Simple function name
                register_func = getattr(module, entry_parts[0], None)
            else:
                # Module.function format
                obj = module
                for part in entry_parts:
                    obj = getattr(obj, part, None)
                    if obj is None:
                        break
                register_func = obj

            if register_func is None:
                logger.error(
                    f"Entry point '{backend_entry}' not found in plugin "
                    f"{plugin_name}"
                )
                return False

            # Register plugin
            plugin_instance = register_func(app, plugin_dir)

            # Store plugin metadata
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_metadata[plugin_name] = {
                "name": plugin_name,
                "version": manifest.get("version", "1.0.0"),
                "author": manifest.get("author", "Unknown"),
                "description": manifest.get("description", ""),
                "directory": str(plugin_dir)
            }

            logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(
                f"Error loading plugin {plugin_name} from {plugin_dir}: {e}",
                exc_info=True
            )
            return False

    def get_plugin_info(self, plugin_name: str) -> dict[str, Any] | None:
        """Get plugin information"""
        return self.plugin_metadata.get(plugin_name)

    def list_plugins(self) -> list[str]:
        """List all loaded plugin names"""
        return list(self.loaded_plugins.keys())


# Global plugin loader instance
_plugin_loader: PluginLoader | None = None


def load_all_plugins(app: FastAPI, plugins_directory: str | None = None) -> int:
    """
    Load all plugins and register with FastAPI app.

    Args:
        app: FastAPI application instance
        plugins_directory: Optional path to plugins directory

    Returns:
        Number of plugins loaded
    """
    global _plugin_loader

    if _plugin_loader is None:
        _plugin_loader = PluginLoader(plugins_directory)

    return _plugin_loader.load_all_plugins(app)


def get_plugin_loader() -> PluginLoader | None:
    """Get the global plugin loader instance"""
    return _plugin_loader

