"""
Host API for Plugin Subprocess Communication.

Phase 4 Enhancement: Defines the API surface exposed to plugins
running in subprocesses. All host functionality is accessed through
permission-gated RPC calls.

Phase 5A Enhancement: Wire stub handlers to actual backend services.

The Host API provides:
    - Audio services (playback, recording, processing)
    - UI services (notifications, dialogs, panel updates)
    - Storage services (plugin-scoped data persistence via StorageManager)
    - Settings services (read/write configuration)
    - Engine services (invoke other engines/plugins via EngineService)
"""

import base64
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

from .bridge import IPCBridge
from .permissions import (
    PermissionEnforcer,
    PermissionLevel,
    get_auditor,
)
from .protocol import ErrorCode, HostMethods, RPCError
from .storage_isolation import (
    PathValidationError,
    PluginStorage,
    QuotaExceededError,
    StorageManager,
    StorageQuota,
    StorageType,
    get_plugin_storage,
    get_storage_manager,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Service Protocols for Dependency Injection
# =============================================================================


class IAudioService(Protocol):
    """Protocol for audio playback and processing services."""

    async def play_audio(
        self,
        audio_data: Optional[bytes] = None,
        audio_path: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Play audio and return playback info."""
        ...

    async def stop_playback(self, playback_id: Optional[str] = None) -> Dict[str, Any]:
        """Stop audio playback."""
        ...

    async def get_devices(self) -> List[Dict[str, Any]]:
        """List available audio devices."""
        ...

    async def process_audio(
        self,
        audio_data: bytes,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process audio with specified operation."""
        ...


class IUIService(Protocol):
    """Protocol for UI notification services."""

    async def show_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration_ms: int = 3000,
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Show a notification."""
        ...

    async def show_dialog(
        self,
        title: str,
        content: str,
        dialog_type: str = "info",
        buttons: Optional[List[str]] = None,
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Show a dialog."""
        ...

    async def update_panel(
        self,
        panel_id: str,
        updates: Dict[str, Any],
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a plugin panel."""
        ...


class ISettingsService(Protocol):
    """Protocol for settings service."""

    async def get_setting(self, key: str) -> Any:
        """Get a setting value."""
        ...

    async def set_setting(self, key: str, value: Any) -> Dict[str, Any]:
        """Set a setting value."""
        ...

    def get_plugin_settings_prefix(self, plugin_id: str) -> str:
        """Get the settings prefix for a plugin."""
        ...


class IEngineService(Protocol):
    """Protocol for engine service."""

    def list_engines(self) -> List[Dict[str, Any]]:
        """List available engines."""
        ...

    def is_engine_available(self, engine_id: str) -> bool:
        """Check if engine is available."""
        ...

    async def invoke_engine(
        self,
        engine_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Invoke a method on an engine."""
        ...


# =============================================================================
# Default Service Implementations (Stubs for testing / standalone mode)
# =============================================================================


class DefaultAudioService:
    """Default audio service implementation (logging only)."""

    async def play_audio(
        self,
        audio_data: Optional[bytes] = None,
        audio_path: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        playback_id = str(uuid.uuid4())
        logger.info(f"DefaultAudioService.play_audio: id={playback_id}")
        return {
            "status": "playing",
            "playback_id": playback_id,
        }

    async def stop_playback(self, playback_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"DefaultAudioService.stop_playback: id={playback_id}")
        return {"status": "stopped"}

    async def get_devices(self) -> List[Dict[str, Any]]:
        return [
            {"id": "default", "name": "Default Output Device", "type": "output"},
            {"id": "default-input", "name": "Default Input Device", "type": "input"},
        ]

    async def process_audio(
        self,
        audio_data: bytes,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        logger.info(
            f"DefaultAudioService.process_audio: op={operation}, "
            f"data_len={len(audio_data)}"
        )
        return {
            "status": "processed",
            "operation": operation,
            "output_path": None,
        }


class DefaultUIService:
    """Default UI service implementation (logging only)."""

    async def show_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration_ms: int = 3000,
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        notification_id = str(uuid.uuid4())
        logger.info(
            f"DefaultUIService.show_notification: [{level}] {title}: {message} "
            f"(from {source_plugin})"
        )
        return {"shown": True, "notification_id": notification_id}

    async def show_dialog(
        self,
        title: str,
        content: str,
        dialog_type: str = "info",
        buttons: Optional[List[str]] = None,
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        dialog_id = str(uuid.uuid4())
        logger.info(
            f"DefaultUIService.show_dialog: {title} (type={dialog_type}, "
            f"from {source_plugin})"
        )
        return {
            "shown": True,
            "dialog_id": dialog_id,
            "result": None,
        }

    async def update_panel(
        self,
        panel_id: str,
        updates: Dict[str, Any],
        source_plugin: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.info(
            f"DefaultUIService.update_panel: panel={panel_id}, "
            f"updates={list(updates.keys())} (from {source_plugin})"
        )
        return {"updated": True}


class DefaultSettingsService:
    """Default settings service implementation (in-memory)."""

    def __init__(self):
        self._settings: Dict[str, Any] = {}

    async def get_setting(self, key: str) -> Any:
        return self._settings.get(key)

    async def set_setting(self, key: str, value: Any) -> Dict[str, Any]:
        self._settings[key] = value
        return {"updated": True, "key": key}

    def get_plugin_settings_prefix(self, plugin_id: str) -> str:
        return f"plugin.{plugin_id}."


class DefaultEngineService:
    """Default engine service implementation (stub)."""

    def list_engines(self) -> List[Dict[str, Any]]:
        return []

    def is_engine_available(self, engine_id: str) -> bool:
        return False

    async def invoke_engine(
        self,
        engine_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError(f"Engine {engine_id} not available in default mode")


# =============================================================================
# Service Locator
# =============================================================================


@dataclass
class ServiceLocator:
    """
    Service locator for Host API dependencies.

    This pattern allows for dependency injection of backend services
    while providing sensible defaults for testing and standalone operation.
    """

    audio_service: Optional[IAudioService] = None
    ui_service: Optional[IUIService] = None
    settings_service: Optional[ISettingsService] = None
    engine_service: Optional[IEngineService] = None
    storage_manager: Optional[StorageManager] = None

    # Default instances (lazy-initialized)
    _default_audio: Optional[DefaultAudioService] = field(
        default=None, repr=False, init=False
    )
    _default_ui: Optional[DefaultUIService] = field(
        default=None, repr=False, init=False
    )
    _default_settings: Optional[DefaultSettingsService] = field(
        default=None, repr=False, init=False
    )
    _default_engine: Optional[DefaultEngineService] = field(
        default=None, repr=False, init=False
    )

    def get_audio(self) -> IAudioService:
        """Get audio service (injected or default)."""
        if self.audio_service is not None:
            return self.audio_service
        if self._default_audio is None:
            self._default_audio = DefaultAudioService()
        return self._default_audio

    def get_ui(self) -> IUIService:
        """Get UI service (injected or default)."""
        if self.ui_service is not None:
            return self.ui_service
        if self._default_ui is None:
            self._default_ui = DefaultUIService()
        return self._default_ui

    def get_settings(self) -> ISettingsService:
        """Get settings service (injected or default)."""
        if self.settings_service is not None:
            return self.settings_service
        if self._default_settings is None:
            self._default_settings = DefaultSettingsService()
        return self._default_settings

    def get_engine(self) -> IEngineService:
        """Get engine service (injected or default)."""
        if self.engine_service is not None:
            return self.engine_service
        if self._default_engine is None:
            self._default_engine = DefaultEngineService()
        return self._default_engine

    def get_storage(self) -> StorageManager:
        """Get storage manager (injected or global)."""
        if self.storage_manager is not None:
            return self.storage_manager
        return get_storage_manager()


# Global service locator instance
_service_locator: Optional[ServiceLocator] = None


def get_service_locator() -> ServiceLocator:
    """Get the global service locator instance."""
    global _service_locator
    if _service_locator is None:
        _service_locator = ServiceLocator()
    return _service_locator


def configure_services(
    audio_service: Optional[IAudioService] = None,
    ui_service: Optional[IUIService] = None,
    settings_service: Optional[ISettingsService] = None,
    engine_service: Optional[IEngineService] = None,
    storage_manager: Optional[StorageManager] = None,
) -> ServiceLocator:
    """
    Configure the global service locator with backend services.

    Call this at application startup to wire up real services.

    Args:
        audio_service: Audio playback/processing service
        ui_service: UI notification service
        settings_service: Settings service
        engine_service: Engine invocation service
        storage_manager: Plugin storage manager

    Returns:
        The configured ServiceLocator instance
    """
    global _service_locator
    _service_locator = ServiceLocator(
        audio_service=audio_service,
        ui_service=ui_service,
        settings_service=settings_service,
        engine_service=engine_service,
        storage_manager=storage_manager,
    )
    logger.info("Host API services configured")
    return _service_locator


def reset_services() -> None:
    """Reset the global service locator (for testing)."""
    global _service_locator
    _service_locator = None


# =============================================================================
# Permission Context
# =============================================================================


@dataclass
class PermissionContext:
    """
    Context for permission checking.

    Enhanced to use the hardened PermissionEnforcer for
    hierarchical permission checking and audit logging.
    """

    plugin_id: str
    permissions: Dict[str, Any]
    _enforcer: Optional[PermissionEnforcer] = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize the permission enforcer."""
        self._enforcer = PermissionEnforcer(
            plugin_id=self.plugin_id,
            permissions=self.permissions,
            auditor=get_auditor(),
        )

    @property
    def enforcer(self) -> PermissionEnforcer:
        """Get the underlying permission enforcer."""
        if self._enforcer is None:
            self._enforcer = PermissionEnforcer(
                plugin_id=self.plugin_id,
                permissions=self.permissions,
                auditor=get_auditor(),
            )
        return self._enforcer

    def has_permission(self, permission: str) -> bool:
        """
        Check if the plugin has a specific permission.

        Permission format: "category.action" (e.g., "audio.playback")
        """
        return self.enforcer.has(permission)

    def require_permission(
        self,
        permission: str,
        level: PermissionLevel = PermissionLevel.FULL,
        audit_method: Optional[str] = None,
    ) -> None:
        """
        Require a permission, raising PermissionError if not granted.

        Args:
            permission: The required permission string
            level: The required permission level (default: FULL)
            audit_method: Optional method name for audit logging

        Raises:
            PermissionError: If permission is not granted
        """
        check = self.enforcer.check(permission, level, audit_method)
        if not check.granted:
            raise PermissionError(f"Permission denied: {permission} - {check.reason}")

    def get_level(self, permission: str) -> PermissionLevel:
        """Get the granted level for a permission."""
        return self.enforcer.get_level(permission)

    def list_granted(self) -> List[str]:
        """List all granted permissions."""
        return self.enforcer.list_granted()


# =============================================================================
# Host API Handlers
# =============================================================================


class HostAPIHandler(ABC):
    """Base class for Host API method handlers."""

    @abstractmethod
    def get_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        """Return a mapping of method names to handler functions."""
        pass


class AudioAPIHandler(HostAPIHandler):
    """
    Handles audio-related Host API calls.

    Phase 5A: Wired to IAudioService for actual playback/processing.
    """

    def __init__(self, context: PermissionContext, services: ServiceLocator):
        self.context = context
        self.services = services

    def get_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        return {
            HostMethods.AUDIO_PLAY: self.play,
            HostMethods.AUDIO_STOP: self.stop,
            HostMethods.AUDIO_GET_DEVICES: self.get_devices,
            HostMethods.AUDIO_PROCESS: self.process,
        }

    async def play(
        self,
        audio_data: Optional[str] = None,  # Base64 encoded
        audio_path: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Play audio through the host."""
        self.context.require_permission("audio.playback", audit_method="audio.play")

        # Decode base64 audio data if provided
        decoded_data = None
        if audio_data is not None and audio_data:
            try:
                decoded_data = base64.b64decode(audio_data)
            except Exception as e:
                logger.warning(f"Failed to decode audio data: {e}")
                raise ValueError("Invalid base64 audio data")

        # Delegate to audio service
        audio_svc = self.services.get_audio()
        result = await audio_svc.play_audio(
            audio_data=decoded_data,
            audio_path=audio_path,
            device_id=device_id,
        )

        logger.info(f"Audio play completed for plugin {self.context.plugin_id}")
        return result

    async def stop(self, playback_id: Optional[str] = None) -> Dict[str, Any]:
        """Stop audio playback."""
        self.context.require_permission("audio.playback", audit_method="audio.stop")

        audio_svc = self.services.get_audio()
        result = await audio_svc.stop_playback(playback_id)

        logger.info(f"Audio stop completed for plugin {self.context.plugin_id}")
        return result

    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get available audio devices."""
        # Device listing doesn't require special permission
        audio_svc = self.services.get_audio()
        return await audio_svc.get_devices()

    async def process(
        self,
        audio_data: str,  # Base64 encoded
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process audio through the host."""
        self.context.require_permission("audio.process", audit_method="audio.process")

        # Decode base64 audio data
        try:
            decoded_data = base64.b64decode(audio_data)
        except Exception as e:
            logger.warning(f"Failed to decode audio data: {e}")
            raise ValueError("Invalid base64 audio data")

        audio_svc = self.services.get_audio()
        result = await audio_svc.process_audio(
            audio_data=decoded_data,
            operation=operation,
            params=params,
        )

        logger.info(
            f"Audio process '{operation}' completed for plugin {self.context.plugin_id}"
        )
        return result


class UIAPIHandler(HostAPIHandler):
    """
    Handles UI-related Host API calls.

    Phase 5A: Wired to IUIService for actual UI operations.
    """

    def __init__(self, context: PermissionContext, services: ServiceLocator):
        self.context = context
        self.services = services

    def get_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        return {
            HostMethods.UI_NOTIFY: self.notify,
            HostMethods.UI_SHOW_DIALOG: self.show_dialog,
            HostMethods.UI_UPDATE_PANEL: self.update_panel,
        }

    async def notify(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration_ms: int = 3000,
    ) -> Dict[str, Any]:
        """Show a notification in the UI."""
        # Notifications are generally allowed (no special permission)
        ui_svc = self.services.get_ui()
        result = await ui_svc.show_notification(
            title=title,
            message=message,
            level=level,
            duration_ms=duration_ms,
            source_plugin=self.context.plugin_id,
        )

        logger.debug(
            f"UI notification from plugin {self.context.plugin_id}: [{level}] {title}"
        )
        return result

    async def show_dialog(
        self,
        title: str,
        content: str,
        dialog_type: str = "info",
        buttons: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Show a dialog in the UI."""
        ui_svc = self.services.get_ui()
        result = await ui_svc.show_dialog(
            title=title,
            content=content,
            dialog_type=dialog_type,
            buttons=buttons,
            source_plugin=self.context.plugin_id,
        )

        logger.info(f"UI dialog from plugin {self.context.plugin_id}: {title}")
        return result

    async def update_panel(
        self,
        panel_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a plugin panel in the UI."""
        ui_svc = self.services.get_ui()
        result = await ui_svc.update_panel(
            panel_id=panel_id,
            updates=updates,
            source_plugin=self.context.plugin_id,
        )

        logger.debug(
            f"UI panel update from plugin {self.context.plugin_id}: {panel_id}"
        )
        return result


class StorageAPIHandler(HostAPIHandler):
    """
    Handles storage-related Host API calls.

    Phase 5A: Wired to StorageManager for persistent, isolated storage.
    """

    def __init__(self, context: PermissionContext, services: ServiceLocator):
        self.context = context
        self.services = services
        self._storage: Optional[PluginStorage] = None

    def _get_storage(self) -> PluginStorage:
        """Get or create the plugin's isolated storage."""
        if self._storage is None:
            storage_manager = self.services.get_storage()

            # Extract quota from permissions if available
            resource_limits = self.context.permissions.get("resource_limits", {})
            quota = StorageQuota.from_manifest(resource_limits)

            # Get storage for this plugin
            self._storage = storage_manager.get_storage(
                self.context.plugin_id,
                quota=quota,
            )
        return self._storage

    def get_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        return {
            HostMethods.STORAGE_GET: self.get,
            HostMethods.STORAGE_SET: self.set,
            HostMethods.STORAGE_DELETE: self.delete,
        }

    async def get(self, key: str) -> Any:
        """Get a value from plugin storage."""
        self.context.require_permission("filesystem.read", audit_method="storage.get")

        storage = self._get_storage()

        try:
            # Storage key is used as filename (with .json extension for structured data)
            filename = self._key_to_filename(key)
            if not storage.file_exists(filename, StorageType.DATA):
                return None

            data = storage.read_file(filename, StorageType.DATA)
            # Deserialize JSON data
            return json.loads(data.decode("utf-8"))

        except PathValidationError as e:
            logger.warning(f"Path validation error for key {key}: {e}")
            raise PermissionError(f"Invalid storage key: {key}")
        except json.JSONDecodeError:
            # Return raw data if not JSON
            return data.decode("utf-8")

    async def set(self, key: str, value: Any) -> Dict[str, Any]:
        """Set a value in plugin storage."""
        self.context.require_permission("filesystem.write", audit_method="storage.set")

        storage = self._get_storage()

        try:
            filename = self._key_to_filename(key)
            # Serialize value to JSON
            data = json.dumps(value, ensure_ascii=False).encode("utf-8")
            storage.write_file(filename, data, StorageType.DATA)

            return {"stored": True, "key": key}

        except PathValidationError as e:
            logger.warning(f"Path validation error for key {key}: {e}")
            raise PermissionError(f"Invalid storage key: {key}")
        except QuotaExceededError as e:
            logger.warning(f"Storage quota exceeded for plugin {self.context.plugin_id}")
            raise ResourceError(f"Storage quota exceeded: {e}")

    async def delete(self, key: str) -> Dict[str, Any]:
        """Delete a value from plugin storage."""
        self.context.require_permission(
            "filesystem.write", audit_method="storage.delete"
        )

        storage = self._get_storage()

        try:
            filename = self._key_to_filename(key)
            existed = storage.delete_file(filename, StorageType.DATA)

            return {"deleted": existed, "key": key}

        except PathValidationError as e:
            logger.warning(f"Path validation error for key {key}: {e}")
            raise PermissionError(f"Invalid storage key: {key}")

    @staticmethod
    def _key_to_filename(key: str) -> str:
        """Convert a storage key to a safe filename."""
        # Replace dots with slashes for hierarchical keys
        # e.g., "config.audio.volume" -> "config/audio/volume.json"
        parts = key.split(".")
        if len(parts) > 1:
            return "/".join(parts[:-1]) + "/" + parts[-1] + ".json"
        return key + ".json"


class ResourceError(Exception):
    """Exception raised when a resource limit is exceeded."""
    pass


class SettingsAPIHandler(HostAPIHandler):
    """
    Handles settings-related Host API calls.

    Phase 5A: Wired to ISettingsService for actual settings access.
    """

    def __init__(self, context: PermissionContext, services: ServiceLocator):
        self.context = context
        self.services = services

    def get_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        return {
            HostMethods.SETTINGS_GET: self.get,
            HostMethods.SETTINGS_SET: self.set,
        }

    async def get(self, key: str) -> Any:
        """Get a setting value."""
        settings_svc = self.services.get_settings()
        prefix = settings_svc.get_plugin_settings_prefix(self.context.plugin_id)

        # Plugins can read their own settings without permission
        # Reading host settings requires permission
        if not key.startswith(prefix):
            self.context.require_permission(
                "settings.read", audit_method="settings.get"
            )

        result = await settings_svc.get_setting(key)
        logger.debug(f"Settings get from plugin {self.context.plugin_id}: {key}")
        return result

    async def set(self, key: str, value: Any) -> Dict[str, Any]:
        """Set a setting value."""
        settings_svc = self.services.get_settings()
        prefix = settings_svc.get_plugin_settings_prefix(self.context.plugin_id)

        # Plugins can only modify their own settings
        if not key.startswith(prefix):
            raise PermissionError(
                f"Plugins can only modify their own settings (must start with '{prefix}')"
            )

        result = await settings_svc.set_setting(key, value)
        logger.info(f"Settings set from plugin {self.context.plugin_id}: {key}")
        return result


class EngineAPIHandler(HostAPIHandler):
    """
    Handles engine-related Host API calls.

    Phase 5A: Wired to IEngineService for actual engine operations.
    """

    def __init__(self, context: PermissionContext, services: ServiceLocator):
        self.context = context
        self.services = services

    def get_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        return {
            HostMethods.ENGINE_INVOKE: self.invoke,
            HostMethods.ENGINE_LIST: self.list,
        }

    async def invoke(
        self,
        engine_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Invoke a method on another engine."""
        self.context.require_permission(
            "host_api.engine.invoke", audit_method="engine.invoke"
        )

        # Check API-specific permissions
        host_api_perms = self.context.permissions.get("host_api", {})
        if isinstance(host_api_perms, bool):
            # host_api: true grants all, no specific API restrictions
            allowed_apis = []
            denied_apis = []
        else:
            allowed_apis = host_api_perms.get("allowed_apis", [])
            denied_apis = host_api_perms.get("denied_apis", [])

        api_path = f"engine.{engine_id}.{method}"

        if api_path in denied_apis:
            raise PermissionError(f"API explicitly denied: {api_path}")

        if allowed_apis and api_path not in allowed_apis:
            # If allowed_apis is specified, only those are permitted
            if not any(
                api_path.startswith(a.rstrip("*")) for a in allowed_apis if "*" in a
            ):
                if api_path not in allowed_apis:
                    raise PermissionError(f"API not in allowed list: {api_path}")

        # Check if engine exists
        engine_svc = self.services.get_engine()
        if not engine_svc.is_engine_available(engine_id):
            raise ValueError(f"Engine not available: {engine_id}")

        # Invoke the engine method
        result = await engine_svc.invoke_engine(
            engine_id=engine_id,
            method=method,
            params=params,
        )

        logger.info(
            f"Engine invoke from plugin {self.context.plugin_id}: "
            f"{engine_id}.{method}"
        )
        return {
            "invoked": True,
            "engine_id": engine_id,
            "method": method,
            "result": result,
        }

    async def list(self) -> List[Dict[str, Any]]:
        """List available engines."""
        # Listing doesn't require special permission
        engine_svc = self.services.get_engine()
        engines = engine_svc.list_engines()

        logger.debug(
            f"Engine list requested by plugin {self.context.plugin_id}, "
            f"found {len(engines)} engines"
        )
        return engines


# =============================================================================
# Host API Aggregation
# =============================================================================


@dataclass
class HostAPI:
    """
    Complete Host API for a plugin subprocess.

    Aggregates all API handlers and manages permission context.
    Phase 5A: Uses ServiceLocator for wiring to actual backend services.
    """

    plugin_id: str
    permissions: Dict[str, Any] = field(default_factory=dict)
    services: Optional[ServiceLocator] = None

    # Handlers
    _context: PermissionContext = field(init=False, repr=False)
    _audio: AudioAPIHandler = field(init=False, repr=False)
    _ui: UIAPIHandler = field(init=False, repr=False)
    _storage: StorageAPIHandler = field(init=False, repr=False)
    _settings: SettingsAPIHandler = field(init=False, repr=False)
    _engine: EngineAPIHandler = field(init=False, repr=False)

    def __post_init__(self):
        """Initialize handlers."""
        # Use provided services or global service locator
        if self.services is None:
            self.services = get_service_locator()

        self._context = PermissionContext(
            plugin_id=self.plugin_id,
            permissions=self.permissions,
        )
        self._audio = AudioAPIHandler(self._context, self.services)
        self._ui = UIAPIHandler(self._context, self.services)
        self._storage = StorageAPIHandler(self._context, self.services)
        self._settings = SettingsAPIHandler(self._context, self.services)
        self._engine = EngineAPIHandler(self._context, self.services)

    def get_all_methods(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        """Get all registered method handlers."""
        methods = {}
        methods.update(self._audio.get_methods())
        methods.update(self._ui.get_methods())
        methods.update(self._storage.get_methods())
        methods.update(self._settings.get_methods())
        methods.update(self._engine.get_methods())
        return methods

    def register_with_bridge(self, bridge: IPCBridge) -> None:
        """Register all handlers with an IPC bridge."""
        for method, handler in self.get_all_methods().items():
            bridge.register_handler(method, handler)

        logger.debug(f"Registered {len(self.get_all_methods())} Host API methods")

    @property
    def context(self) -> PermissionContext:
        """Get the permission context."""
        return self._context


@dataclass
class HostAPIRegistry:
    """
    Registry of Host API instances for all running plugin subprocesses.

    Manages the lifecycle of Host API instances and provides
    lookup by plugin ID.
    """

    _apis: Dict[str, HostAPI] = field(default_factory=dict, repr=False)
    _services: Optional[ServiceLocator] = None

    def __post_init__(self):
        """Initialize internal state."""
        self._apis = {}

    def set_services(self, services: ServiceLocator) -> None:
        """Set the service locator for new API instances."""
        self._services = services

    def create(
        self,
        plugin_id: str,
        permissions: Optional[Dict[str, Any]] = None,
    ) -> HostAPI:
        """
        Create a new Host API instance for a plugin.

        Args:
            plugin_id: The plugin identifier
            permissions: Permission configuration from manifest

        Returns:
            The created HostAPI instance
        """
        if plugin_id in self._apis:
            raise ValueError(f"Host API already exists for plugin: {plugin_id}")

        api = HostAPI(
            plugin_id=plugin_id,
            permissions=permissions or {},
            services=self._services or get_service_locator(),
        )
        self._apis[plugin_id] = api

        logger.debug(f"Created Host API for plugin: {plugin_id}")
        return api

    def get(self, plugin_id: str) -> Optional[HostAPI]:
        """Get the Host API instance for a plugin."""
        return self._apis.get(plugin_id)

    def remove(self, plugin_id: str) -> bool:
        """Remove and clean up a Host API instance."""
        if plugin_id in self._apis:
            del self._apis[plugin_id]
            logger.debug(f"Removed Host API for plugin: {plugin_id}")
            return True
        return False

    def list_plugins(self) -> List[str]:
        """List all plugins with active Host API instances."""
        return list(self._apis.keys())
