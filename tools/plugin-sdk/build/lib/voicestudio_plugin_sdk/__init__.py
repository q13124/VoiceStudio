"""
VoiceStudio Plugin SDK.

A Python SDK for developing VoiceStudio plugins with type-safe host API access.

Example:
    from voicestudio_plugin_sdk import Plugin, PluginManifest, Capability

    class MyPlugin(Plugin):
        manifest = PluginManifest(
            id="my-plugin",
            name="My Plugin",
            version="1.0.0",
        )

        async def on_invoke(self, capability: str, params: dict) -> dict:
            return {"status": "ok"}

    if __name__ == "__main__":
        plugin = MyPlugin()
        plugin.run()
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "VoiceStudio Team"

from .manifest import (
    Capability,
    CapabilityParameter,
    Permission,
    PluginManifest,
)
from .plugin import Plugin
from .protocol import (
    ErrorCode,
    MessageType,
    Notification,
    Request,
    Response,
    RPCError,
)

__all__ = [
    # Version
    "__version__",
    # Core plugin
    "Plugin",
    # Manifest
    "PluginManifest",
    "Capability",
    "CapabilityParameter",
    "Permission",
    # Protocol
    "MessageType",
    "ErrorCode",
    "Request",
    "Response",
    "Notification",
    "RPCError",
]
