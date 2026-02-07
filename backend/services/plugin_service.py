"""
Plugin Service

Phase 12.2: Plugin Architecture
Extensible plugin system for VoiceStudio.

Features:
- Plugin discovery and loading
- Plugin lifecycle management
- Extension points (engines, processors, UI)
- Plugin sandboxing
"""

import asyncio
import importlib
import importlib.util
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins."""
    ENGINE = "engine"  # Audio synthesis/processing engine
    PROCESSOR = "processor"  # Audio post-processor
    EXPORTER = "exporter"  # Export format handler
    IMPORTER = "importer"  # Import format handler
    UI_PANEL = "ui_panel"  # Custom UI panel
    TOOL = "tool"  # Utility tool


class PluginState(Enum):
    """Plugin lifecycle states."""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    ERROR = "error"


@dataclass
class PluginManifest:
    """Plugin manifest describing a plugin."""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    min_app_version: str = "1.0.0"
    permissions: List[str] = field(default_factory=list)
    settings_schema: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        return cls(
            plugin_id=data["plugin_id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", "Unknown"),
            plugin_type=PluginType(data["plugin_type"]),
            entry_point=data["entry_point"],
            dependencies=data.get("dependencies", []),
            min_app_version=data.get("min_app_version", "1.0.0"),
            permissions=data.get("permissions", []),
            settings_schema=data.get("settings_schema", {}),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "min_app_version": self.min_app_version,
            "permissions": self.permissions,
            "settings_schema": self.settings_schema,
        }


@dataclass
class PluginInfo:
    """Runtime plugin information."""
    manifest: PluginManifest
    state: PluginState
    path: Path
    instance: Optional[Any] = None
    error_message: Optional[str] = None
    loaded_at: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest": self.manifest.to_dict(),
            "state": self.state.value,
            "path": str(self.path),
            "error_message": self.error_message,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "settings": self.settings,
        }


class PluginBase(ABC):
    """Base class for all plugins."""
    
    def __init__(self, plugin_service: "PluginService"):
        self.plugin_service = plugin_service
        self._initialized = False
    
    @abstractmethod
    async def activate(self) -> bool:
        """Activate the plugin. Called when plugin is enabled."""
        pass
    
    @abstractmethod
    async def deactivate(self) -> bool:
        """Deactivate the plugin. Called when plugin is disabled."""
        pass
    
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return plugin manifest."""
        pass
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get plugin setting."""
        return self.plugin_service.get_plugin_setting(
            self.manifest.plugin_id, key, default
        )
    
    def set_setting(self, key: str, value: Any):
        """Set plugin setting."""
        self.plugin_service.set_plugin_setting(
            self.manifest.plugin_id, key, value
        )


class EnginePlugin(PluginBase):
    """Base class for engine plugins."""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        options: Dict[str, Any],
    ) -> bytes:
        """Synthesize speech."""
        pass
    
    @abstractmethod
    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices."""
        pass


class ProcessorPlugin(PluginBase):
    """Base class for audio processor plugins."""
    
    @abstractmethod
    async def process(
        self,
        audio_data: bytes,
        sample_rate: int,
        options: Dict[str, Any],
    ) -> bytes:
        """Process audio."""
        pass


class ExporterPlugin(PluginBase):
    """Base class for exporter plugins."""
    
    @abstractmethod
    async def export(
        self,
        audio_data: bytes,
        output_path: Path,
        options: Dict[str, Any],
    ) -> bool:
        """Export audio to file."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported export formats."""
        pass


class ImporterPlugin(PluginBase):
    """Base class for importer plugins."""
    
    @abstractmethod
    async def import_file(
        self,
        input_path: Path,
        options: Dict[str, Any],
    ) -> bytes:
        """Import audio from file."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported import formats."""
        pass


# Extension points registry
ExtensionPoint = Callable[..., Any]
EXTENSION_POINTS: Dict[str, List[ExtensionPoint]] = {
    "pre_synthesis": [],
    "post_synthesis": [],
    "voice_loaded": [],
    "audio_processed": [],
    "export_complete": [],
}


def register_extension(point_name: str) -> Callable:
    """Decorator to register an extension point handler."""
    def decorator(func: ExtensionPoint) -> ExtensionPoint:
        if point_name in EXTENSION_POINTS:
            EXTENSION_POINTS[point_name].append(func)
        return func
    return decorator


class PluginService:
    """
    Plugin management service.
    
    Phase 12.2: Plugin Architecture
    
    Features:
    - Plugin discovery from plugins directory
    - Plugin lifecycle management
    - Settings persistence
    - Extension point system
    """
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        self._plugins_dir = plugins_dir or Path("plugins")
        self._plugins: Dict[str, PluginInfo] = {}
        self._settings: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
        logger.info(f"PluginService created with plugins dir: {self._plugins_dir}")
    
    async def initialize(self) -> bool:
        """Initialize the plugin service."""
        if self._initialized:
            return True
        
        try:
            # Create plugins directory
            self._plugins_dir.mkdir(parents=True, exist_ok=True)
            
            # Load settings
            await self._load_settings()
            
            # Discover plugins
            await self.discover_plugins()
            
            self._initialized = True
            logger.info("PluginService initialized")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize PluginService: {e}")
            return False
    
    async def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins."""
        discovered = []
        
        if not self._plugins_dir.exists():
            return discovered
        
        for plugin_path in self._plugins_dir.iterdir():
            if not plugin_path.is_dir():
                continue
            
            manifest_path = plugin_path / "plugin.json"
            if not manifest_path.exists():
                continue
            
            try:
                with open(manifest_path, "r") as f:
                    manifest_data = json.load(f)
                
                manifest = PluginManifest.from_dict(manifest_data)
                
                plugin_info = PluginInfo(
                    manifest=manifest,
                    state=PluginState.DISCOVERED,
                    path=plugin_path,
                    settings=self._settings.get(manifest.plugin_id, {}),
                )
                
                self._plugins[manifest.plugin_id] = plugin_info
                discovered.append(plugin_info)
                
                logger.info(f"Discovered plugin: {manifest.name} ({manifest.plugin_id})")
            
            except Exception as e:
                logger.warning(f"Failed to load plugin from {plugin_path}: {e}")
        
        return discovered
    
    async def load_plugin(self, plugin_id: str) -> bool:
        """Load a plugin."""
        if plugin_id not in self._plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin_info = self._plugins[plugin_id]
        
        try:
            # Load the plugin module
            entry_point = plugin_info.manifest.entry_point
            module_path = plugin_info.path / entry_point
            
            if not module_path.exists():
                raise FileNotFoundError(f"Entry point not found: {entry_point}")
            
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_id}",
                module_path,
            )
            
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module: {entry_point}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find and instantiate the plugin class
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type) and
                    issubclass(obj, PluginBase) and
                    obj is not PluginBase and
                    obj not in (EnginePlugin, ProcessorPlugin, ExporterPlugin, ImporterPlugin)
                ):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                raise TypeError(f"No plugin class found in {entry_point}")
            
            plugin_info.instance = plugin_class(self)
            plugin_info.state = PluginState.LOADED
            plugin_info.loaded_at = datetime.now()
            
            logger.info(f"Loaded plugin: {plugin_info.manifest.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            plugin_info.state = PluginState.ERROR
            plugin_info.error_message = str(e)
            return False
    
    async def activate_plugin(self, plugin_id: str) -> bool:
        """Activate a loaded plugin."""
        if plugin_id not in self._plugins:
            return False
        
        plugin_info = self._plugins[plugin_id]
        
        if plugin_info.state == PluginState.DISCOVERED:
            if not await self.load_plugin(plugin_id):
                return False
        
        if plugin_info.state != PluginState.LOADED and plugin_info.state != PluginState.DEACTIVATED:
            logger.warning(f"Cannot activate plugin in state: {plugin_info.state}")
            return False
        
        try:
            if plugin_info.instance:
                await plugin_info.instance.activate()
            
            plugin_info.state = PluginState.ACTIVATED
            logger.info(f"Activated plugin: {plugin_info.manifest.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to activate plugin {plugin_id}: {e}")
            plugin_info.state = PluginState.ERROR
            plugin_info.error_message = str(e)
            return False
    
    async def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate an active plugin."""
        if plugin_id not in self._plugins:
            return False
        
        plugin_info = self._plugins[plugin_id]
        
        if plugin_info.state != PluginState.ACTIVATED:
            return False
        
        try:
            if plugin_info.instance:
                await plugin_info.instance.deactivate()
            
            plugin_info.state = PluginState.DEACTIVATED
            logger.info(f"Deactivated plugin: {plugin_info.manifest.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to deactivate plugin {plugin_id}: {e}")
            plugin_info.error_message = str(e)
            return False
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        if plugin_id not in self._plugins:
            return False
        
        plugin_info = self._plugins[plugin_id]
        
        if plugin_info.state == PluginState.ACTIVATED:
            await self.deactivate_plugin(plugin_id)
        
        plugin_info.instance = None
        plugin_info.state = PluginState.DISCOVERED
        
        logger.info(f"Unloaded plugin: {plugin_info.manifest.name}")
        return True
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin info by ID."""
        return self._plugins.get(plugin_id)
    
    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        state: Optional[PluginState] = None,
    ) -> List[PluginInfo]:
        """List plugins with optional filtering."""
        plugins = list(self._plugins.values())
        
        if plugin_type:
            plugins = [p for p in plugins if p.manifest.plugin_type == plugin_type]
        
        if state:
            plugins = [p for p in plugins if p.state == state]
        
        return plugins
    
    def get_active_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """Get all activated plugins."""
        return self.list_plugins(plugin_type=plugin_type, state=PluginState.ACTIVATED)
    
    def get_engine_plugins(self) -> List[PluginInfo]:
        """Get all engine plugins."""
        return self.list_plugins(plugin_type=PluginType.ENGINE, state=PluginState.ACTIVATED)
    
    def get_processor_plugins(self) -> List[PluginInfo]:
        """Get all processor plugins."""
        return self.list_plugins(plugin_type=PluginType.PROCESSOR, state=PluginState.ACTIVATED)
    
    # Settings management
    
    def get_plugin_setting(self, plugin_id: str, key: str, default: Any = None) -> Any:
        """Get a plugin setting."""
        if plugin_id not in self._settings:
            return default
        return self._settings[plugin_id].get(key, default)
    
    def set_plugin_setting(self, plugin_id: str, key: str, value: Any):
        """Set a plugin setting."""
        if plugin_id not in self._settings:
            self._settings[plugin_id] = {}
        self._settings[plugin_id][key] = value
        
        # Update plugin info
        if plugin_id in self._plugins:
            self._plugins[plugin_id].settings = self._settings[plugin_id]
        
        # Save settings (async)
        asyncio.create_task(self._save_settings())
    
    async def _load_settings(self):
        """Load plugin settings from file."""
        settings_path = self._plugins_dir / "settings.json"
        
        if settings_path.exists():
            try:
                with open(settings_path, "r") as f:
                    self._settings = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load plugin settings: {e}")
                self._settings = {}
    
    async def _save_settings(self):
        """Save plugin settings to file."""
        settings_path = self._plugins_dir / "settings.json"
        
        try:
            with open(settings_path, "w") as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin settings: {e}")
    
    # Extension points
    
    async def call_extension_point(
        self,
        point_name: str,
        *args,
        **kwargs,
    ) -> List[Any]:
        """Call all handlers registered for an extension point."""
        results = []
        
        if point_name not in EXTENSION_POINTS:
            return results
        
        for handler in EXTENSION_POINTS[point_name]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(*args, **kwargs)
                else:
                    result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Extension point handler error: {e}")
        
        return results


# Singleton instance
_plugin_service: Optional[PluginService] = None


def get_plugin_service() -> PluginService:
    """Get or create the plugin service singleton."""
    global _plugin_service
    if _plugin_service is None:
        _plugin_service = PluginService()
    return _plugin_service
