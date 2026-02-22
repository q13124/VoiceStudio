"""
Plugin-Engine Integration System

Provides hooks and event handling for plugin integration with the engine system.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# Plugin hook registry
_plugin_hooks: dict[str, list[Callable]] = {}
_plugin_events: dict[str, list[Callable]] = {}
_plugin_resources: dict[str, dict[str, Any]] = {}


class PluginHook:
    """Plugin hook for engine integration."""

    # Engine lifecycle hooks
    ENGINE_PRE_INIT = "engine.pre_init"
    ENGINE_POST_INIT = "engine.post_init"
    ENGINE_PRE_SYNTHESIS = "engine.pre_synthesis"
    ENGINE_POST_SYNTHESIS = "engine.post_synthesis"
    ENGINE_PRE_TRAINING = "engine.pre_training"
    ENGINE_POST_TRAINING = "engine.post_training"

    # Audio processing hooks
    AUDIO_PRE_PROCESS = "audio.pre_process"
    AUDIO_POST_PROCESS = "audio.post_process"

    # Quality hooks
    QUALITY_PRE_CALCULATE = "quality.pre_calculate"
    QUALITY_POST_CALCULATE = "quality.post_calculate"

    # Project hooks
    PROJECT_PRE_CREATE = "project.pre_create"
    PROJECT_POST_CREATE = "project.post_create"
    PROJECT_PRE_SAVE = "project.pre_save"
    PROJECT_POST_SAVE = "project.post_save"


def register_hook(hook_name: str, callback: Callable) -> None:
    """
    Register a plugin hook callback.

    Args:
        hook_name: Hook name (use PluginHook constants)
        callback: Callback function to execute
    """
    if hook_name not in _plugin_hooks:
        _plugin_hooks[hook_name] = []

    _plugin_hooks[hook_name].append(callback)
    logger.debug(f"Registered hook '{hook_name}'")


def unregister_hook(hook_name: str, callback: Callable) -> None:
    """
    Unregister a plugin hook callback.

    Args:
        hook_name: Hook name
        callback: Callback function to remove
    """
    if hook_name in _plugin_hooks and callback in _plugin_hooks[hook_name]:
        _plugin_hooks[hook_name].remove(callback)
        logger.debug(f"Unregistered hook '{hook_name}'")


def call_hook(hook_name: str, *args, **kwargs) -> list[Any]:
    """
    Call all registered hooks for a given hook name.

    Args:
        hook_name: Hook name
        *args: Positional arguments to pass to hooks
        **kwargs: Keyword arguments to pass to hooks

    Returns:
        List of return values from all hooks
    """
    results = []

    if hook_name in _plugin_hooks:
        for callback in _plugin_hooks[hook_name]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error calling hook '{hook_name}': {e}", exc_info=True)

    return results


def register_event_handler(event_type: str, callback: Callable) -> None:
    """
    Register an event handler callback.

    Args:
        event_type: Event type (e.g., "synthesis_complete", "training_started")
        callback: Callback function to execute
    """
    if event_type not in _plugin_events:
        _plugin_events[event_type] = []

    _plugin_events[event_type].append(callback)
    logger.debug(f"Registered event handler '{event_type}'")


def unregister_event_handler(event_type: str, callback: Callable) -> None:
    """
    Unregister an event handler callback.

    Args:
        event_type: Event type
        callback: Callback function to remove
    """
    if event_type in _plugin_events and callback in _plugin_events[event_type]:
        _plugin_events[event_type].remove(callback)
        logger.debug(f"Unregistered event handler '{event_type}'")


def emit_event(event_type: str, payload: dict[str, Any]) -> None:
    """
    Emit an event to all registered handlers.

    Args:
        event_type: Event type
        payload: Event payload data
    """
    if event_type in _plugin_events:
        for callback in _plugin_events[event_type]:
            try:
                callback(event_type, payload)
            except Exception as e:
                logger.error(f"Error handling event '{event_type}': {e}", exc_info=True)


def register_resource(plugin_id: str, resource_type: str, resource: Any) -> None:
    """
    Register a plugin resource.

    Args:
        plugin_id: Plugin identifier
        resource_type: Resource type (e.g., "model", "processor", "effect")
        resource: Resource object
    """
    if plugin_id not in _plugin_resources:
        _plugin_resources[plugin_id] = {}

    _plugin_resources[plugin_id][resource_type] = resource
    logger.debug(f"Registered resource '{resource_type}' for plugin '{plugin_id}'")


def unregister_resource(plugin_id: str, resource_type: str) -> None:
    """
    Unregister a plugin resource.

    Args:
        plugin_id: Plugin identifier
        resource_type: Resource type
    """
    if plugin_id in _plugin_resources and resource_type in _plugin_resources[plugin_id]:
        del _plugin_resources[plugin_id][resource_type]
        logger.debug(f"Unregistered resource '{resource_type}' for plugin '{plugin_id}'")


def get_plugin_resources(plugin_id: str | None = None) -> dict[str, Any]:
    """
    Get plugin resources.

    Args:
        plugin_id: Optional plugin identifier to filter by

    Returns:
        Dictionary of resources (by plugin_id if specified, or all resources)
    """
    if plugin_id is not None:
        return _plugin_resources.get(plugin_id, {})

    return _plugin_resources.copy()


def cleanup_plugin_resources(plugin_id: str) -> None:
    """
    Clean up all resources for a plugin.

    Args:
        plugin_id: Plugin identifier
    """
    if plugin_id in _plugin_resources:
        # Clean up resources (e.g., close files, release memory)
        for resource_type, resource in _plugin_resources[plugin_id].items():
            try:
                # If resource has cleanup method, call it
                if hasattr(resource, "cleanup"):
                    resource.cleanup()
                elif hasattr(resource, "close"):
                    resource.close()
            except Exception as e:
                logger.warning(
                    f"Error cleaning up resource '{resource_type}' "
                    f"for plugin '{plugin_id}': {e}"
                )

        del _plugin_resources[plugin_id]
        logger.info(f"Cleaned up resources for plugin '{plugin_id}'")


def get_hook_count(hook_name: str | None = None) -> int:
    """
    Get the number of registered hooks.

    Args:
        hook_name: Optional hook name to filter by

    Returns:
        Number of hooks
    """
    if hook_name is not None:
        return len(_plugin_hooks.get(hook_name, []))

    return sum(len(hooks) for hooks in _plugin_hooks.values())


def get_event_handler_count(event_type: str | None = None) -> int:
    """
    Get the number of registered event handlers.

    Args:
        event_type: Optional event type to filter by

    Returns:
        Number of event handlers
    """
    if event_type is not None:
        return len(_plugin_events.get(event_type, []))

    return sum(len(handlers) for handlers in _plugin_events.values())
