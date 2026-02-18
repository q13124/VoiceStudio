# VoiceStudio Plugin SDK

A Python SDK for developing VoiceStudio plugins with type-safe host API access.

## Installation

```bash
pip install voicestudio-plugin-sdk
```

For full protocol support (OpenAPI spec parsing):

```bash
pip install voicestudio-plugin-sdk[protocol]
```

## Quick Start

### Creating a Basic Plugin

```python
from voicestudio_plugin_sdk import Plugin, PluginManifest, Capability

# Define your plugin
class MyTTSPlugin(Plugin):
    """A simple TTS plugin example."""
    
    manifest = PluginManifest(
        id="my-tts-plugin",
        name="My TTS Plugin",
        version="1.0.0",
        description="A custom text-to-speech plugin",
        capabilities=[
            Capability(
                name="synthesize",
                description="Convert text to speech",
            )
        ],
    )
    
    async def on_initialize(self, config: dict) -> None:
        """Called when the plugin is initialized."""
        self.model = await self.load_model()
    
    async def on_invoke(self, capability: str, params: dict) -> dict:
        """Handle capability invocations."""
        if capability == "synthesize":
            text = params.get("text", "")
            audio = await self.synthesize(text)
            return {"audio": audio}
        raise ValueError(f"Unknown capability: {capability}")
    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text."""
        # Your implementation here
        pass

# Run the plugin
if __name__ == "__main__":
    plugin = MyTTSPlugin()
    plugin.run()
```

### Using the Host API

The SDK provides type-safe access to host services:

```python
from voicestudio_plugin_sdk import Plugin
from voicestudio_plugin_sdk.host_api import HostAPI

class MyPlugin(Plugin):
    async def on_invoke(self, capability: str, params: dict) -> dict:
        # Access storage
        value = await self.host.storage.get("my_key")
        await self.host.storage.set("my_key", {"data": "value"})
        
        # Show notifications
        await self.host.ui.notify("Processing complete!", level="success")
        
        # Use audio services
        devices = await self.host.audio.get_devices()
        
        # Access settings
        setting = await self.host.settings.get("model_path")
        
        return {"status": "ok"}
```

### Logging and Progress

```python
from voicestudio_plugin_sdk import Plugin

class MyPlugin(Plugin):
    async def on_invoke(self, capability: str, params: dict) -> dict:
        # Send log messages
        self.log.info("Starting processing...")
        self.log.debug("Debug details here")
        
        # Report progress
        for i, item in enumerate(items):
            await self.progress(
                operation_id="processing",
                progress=(i + 1) / len(items) * 100,
                message=f"Processing item {i + 1}/{len(items)}"
            )
            await self.process_item(item)
        
        return {"processed": len(items)}
```

## Features

- **Type-Safe API**: Full TypedDict definitions for all protocol messages
- **Async/Await**: Native asyncio support for efficient I/O
- **Host Services**: Easy access to audio, storage, settings, and UI APIs
- **Protocol Compliance**: JSON-RPC 2.0 based IPC protocol
- **Error Handling**: Structured error codes and messages
- **Lifecycle Management**: Initialize, activate, deactivate, shutdown hooks

## Protocol Specification

The SDK is based on the VoiceStudio Plugin IPC Protocol (OpenAPI 3.1):

```python
from voicestudio_plugin_sdk.protocol import get_protocol_spec

spec = get_protocol_spec()
print(f"Protocol version: {spec.version}")
print(f"Available methods: {len(spec.get_methods())}")

# Generate method summary
print(spec.generate_method_summary())
```

## Development

### Running Tests

```bash
pip install voicestudio-plugin-sdk[dev]
pytest
```

### Type Checking

```bash
mypy src/
```

### Building Documentation

```bash
pip install voicestudio-plugin-sdk[docs]
mkdocs serve
```

## License

MIT License - see LICENSE file for details.
