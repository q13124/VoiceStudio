# Backend Plugin API Reference

This document provides complete, authoritative documentation of the VoiceStudio backend plugin API. All classes, methods, properties, and usage patterns are covered with examples.

---

## Core Plugin Classes

### PluginMetadata

The `PluginMetadata` class loads and exposes information from your plugin's `manifest.json` file.

**Location**: `app/core/plugins_api/base.py`

#### Constructor

```python
def __init__(self, manifest_path: Path):
```

**Parameters**:

| Name | Type | Description | Required |
|------|------|-------------|----------|
| `manifest_path` | `Path` | Full path to the plugin's `manifest.json` file | Yes |

**Example**:

```python
from pathlib import Path
from app.core.plugins_api.base import PluginMetadata

manifest_path = Path("/plugins/my_plugin/manifest.json")
metadata = PluginMetadata(manifest_path)
print(metadata.name)  # "my_plugin"
```

#### Properties

##### name

```python
@property
def name(self) -> str:
```

Returns the plugin's unique identifier from `manifest.json`.

**Example**:
```python
plugin_name = metadata.name  # "my_plugin"
```

##### version

```python
@property
def version(self) -> str:
```

Returns the plugin version following semantic versioning.

**Example**:
```python
version = metadata.version  # "1.0.0"
```

##### author

```python
@property
def author(self) -> str:
```

Returns the plugin author name.

**Example**:
```python
author = metadata.author  # "Your Name"
```

##### description

```python
@property
def description(self) -> str:
```

Returns the short description from manifest.

**Example**:
```python
desc = metadata.description  # "My awesome plugin"
```

##### capabilities

```python
@property
def capabilities(self) -> dict[str, Any]:
```

Returns the capabilities dictionary from manifest (backend_routes, effects, etc.).

**Example**:
```python
caps = metadata.capabilities
# {"backend_routes": true, "effects": ["normalize", "amplify"]}
```

##### dependencies

```python
@property
def dependencies(self) -> list[str]:
```

Returns list of plugin dependencies.

**Example**:
```python
deps = metadata.dependencies  # ["requests>=2.28.0"]
```

##### entry_points

```python
@property
def entry_points(self) -> dict[str, str]:
```

Returns entry points from manifest (backend, frontend, etc.).

**Example**:
```python
eps = metadata.entry_points  # {"backend": "plugin.register"}
```

---

### BasePlugin

The `BasePlugin` abstract base class is the foundation for all VoiceStudio plugins. Every plugin must inherit from this class.

**Location**: `app/core/plugins_api/base.py`

#### Constructor

```python
def __init__(self, metadata: PluginMetadata):
```

**Parameters**:

| Name | Type | Description | Required |
|------|------|-------------|----------|
| `metadata` | `PluginMetadata` | Metadata object loaded from `manifest.json` | Yes |

**Example**:

```python
from app.core.plugins_api.base import BasePlugin, PluginMetadata
from pathlib import Path

class MyPlugin(BasePlugin):
    def __init__(self, plugin_dir: Path):
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
```

#### Abstract Methods

##### register

```python
@abstractmethod
def register(self, app) -> None:
```

**Required**: YES (must be implemented)

Registers your plugin's API routes and functionality with the FastAPI application.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `app` | `FastAPI` | The FastAPI application instance |

**Returns**: None

**Raises**: 
- `RuntimeError` — If not implemented by subclass

**Example**:

```python
from fastapi import APIRouter

def register(self, app):
    # Create a router for your endpoints
    router = APIRouter(prefix="/api/plugin/my_plugin", tags=["my_plugin"])
    
    @router.get("/status")
    async def get_status():
        return {"status": "active", "plugin": self.name}
    
    @router.post("/process")
    async def process(data: dict):
        # Your processing logic
        return {"result": "processed"}
    
    # Include router in the app
    app.include_router(router)
```

**Best Practices**:
- Use a consistent prefix: `/api/plugin/{plugin_name}`
- Use async functions for better performance
- Always include your router in the app
- Define request/response models as Pydantic classes

#### Optional Methods

##### initialize

```python
def initialize(self) -> None:
```

Called after `register()` completes. Override to perform plugin initialization.

**Example**:

```python
def initialize(self):
    super().initialize()
    # Load configuration
    # Connect to databases
    # Pre-load models
    logger.info(f"Plugin {self.name} initialized")
```

##### cleanup

```python
def cleanup(self) -> None:
```

Called when VoiceStudio shuts down. Override to release resources.

**Example**:

```python
def cleanup(self):
    super().cleanup()
    # Close database connections
    # Stop background threads
    # Save state
    logger.info(f"Plugin {self.name} cleaned up")
```

#### Non-Abstract Methods

##### is_initialized

```python
def is_initialized(self) -> bool:
```

Returns whether the plugin has been initialized.

**Example**:

```python
if plugin.is_initialized():
    print("Plugin is ready")
```

##### get_info

```python
def get_info(self) -> dict[str, Any]:
```

Returns a dictionary with plugin information.

**Example**:

```python
info = plugin.get_info()
# {
#   "name": "my_plugin",
#   "version": "1.0.0",
#   "author": "Your Name",
#   "description": "My awesome plugin",
#   "capabilities": {...},
#   "initialized": true
# }
```

#### Properties

##### name

```python
@property
def name(self) -> str:
```

The plugin's unique identifier.

##### version

```python
@property
def version(self) -> str:
```

The plugin version.

##### author

```python
@property
def author(self) -> str:
```

The plugin author.

##### description

```python
@property
def description(self) -> str:
```

The plugin description.

---

## Specialized Plugin Base Classes

These specialized bases inherit from a common `PluginBase` (different from `BasePlugin`) and are for specific plugin types.

### EnginePlugin

For implementing TTS, transcription, or voice conversion engines.

**Location**: `backend/services/plugin_service.py`

#### Abstract Methods

##### synthesize

```python
@abstractmethod
async def synthesize(
    self,
    text: str,
    voice_id: str,
    options: dict[str, Any],
) -> bytes:
```

Synthesize speech from text.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Text to synthesize |
| `voice_id` | `str` | Voice identifier |
| `options` | `dict` | Synthesis options (pitch, speed, etc.) |

**Returns**: `bytes` — Audio data in WAV format

##### list_voices

```python
@abstractmethod
async def list_voices(self) -> list[dict[str, Any]]:
```

List available voices.

**Returns**: List of voice dictionaries with `id`, `name`, `gender` fields

---

### ProcessorPlugin

For implementing audio effects or processors.

**Location**: `backend/services/plugin_service.py`

#### Abstract Method

##### process

```python
@abstractmethod
async def process(
    self,
    audio_data: bytes,
    sample_rate: int,
    options: dict[str, Any],
) -> bytes:
```

Process audio data.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `audio_data` | `bytes` | Raw audio bytes (WAV format) |
| `sample_rate` | `int` | Sample rate in Hz |
| `options` | `dict` | Processing options |

**Returns**: `bytes` — Processed audio bytes

---

### ExporterPlugin

For implementing audio export formats.

**Location**: `backend/services/plugin_service.py`

#### Abstract Method

##### export

```python
@abstractmethod
async def export(
    self,
    audio_data: bytes,
    output_path: Path,
    options: dict[str, Any],
) -> bool:
```

Export audio to file.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `audio_data` | `bytes` | Raw audio bytes |
| `output_path` | `Path` | Output file path |
| `options` | `dict` | Export options |

**Returns**: `bool` — True if successful

#### Property

##### supported_formats

```python
@property
@abstractmethod
def supported_formats(self) -> list[str]:
```

List of supported export formats (e.g., `["mp3", "flac"]`).

---

### ImporterPlugin

For implementing audio import formats.

**Location**: `backend/services/plugin_service.py`

#### Abstract Method

##### import_file

```python
@abstractmethod
async def import_file(
    self,
    input_path: Path,
    options: dict[str, Any],
) -> bytes:
```

Import audio from file.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `input_path` | `Path` | Input file path |
| `options` | `dict` | Import options |

**Returns**: `bytes` — Raw audio bytes in WAV format

#### Property

##### supported_formats

```python
@property
@abstractmethod
def supported_formats(self) -> list[str]:
```

List of supported import formats (e.g., `["mp3", "ogg"]`).

---

## Sandbox and Security Classes

### PluginSandbox

Executes plugin code with resource limits and permission checks.

**Location**: `backend/services/plugin_sandbox.py`

#### Constructor

```python
def __init__(
    self,
    plugin_id: str,
    permissions: SandboxPermissions,
    limits: ResourceLimits
):
```

#### Context Manager

##### execute_context

```python
@contextmanager
def execute_context():
```

Use as a context manager for safe sandboxed execution.

**Example**:

```python
sandbox = SandboxManager().create_sandbox(
    plugin_id="my_plugin",
    permissions=sandbox_permissions,
    limits=resource_limits
)

with sandbox.execute_context():
    # Code runs with resource limits enforced
    result = process_audio(data)
```

#### Methods

##### execute_async

```python
async def execute_async(
    self,
    func: Callable,
    *args,
    **kwargs
) -> Any:
```

Execute an async function in the sandbox.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `func` | `Callable` | Async function to execute |
| `*args` | | Arguments for function |
| `**kwargs` | | Keyword arguments for function |

**Returns**: Function's return value

**Example**:

```python
result = await sandbox.execute_async(my_async_function, arg1, arg2)
```

##### execute_subprocess

```python
def execute_subprocess(
    self,
    command: list[str],
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
    capture_output: bool = True
) -> CompletedProcess:
```

Execute a subprocess with permission checks.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `command` | `list[str]` | Command as list (e.g., `["ffmpeg", "-i", "file.mp3"]`) |
| `cwd` | `Path` | Working directory (optional) |
| `env` | `dict` | Environment variables (optional) |
| `capture_output` | `bool` | Capture stdout/stderr (default: True) |

**Returns**: `CompletedProcess` with `returncode`, `stdout`, `stderr`

**Raises**: `PermissionViolation` — If plugin lacks `system.process` permission

**Example**:

```python
result = sandbox.execute_subprocess(
    ["ffmpeg", "-i", "input.mp3", "output.wav"],
    capture_output=True
)
if result.returncode == 0:
    print("Success:", result.stdout.decode())
```

##### check_file_permission

```python
def check_file_permission(
    self,
    path: Path,
    operation: str  # "read", "write", "execute"
) -> bool:
```

Check if plugin can access a file.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `path` | `Path` | File path to check |
| `operation` | `str` | Operation: "read", "write", or "execute" |

**Returns**: `bool` — True if permitted

**Raises**: `PermissionViolation` — If not permitted

**Example**:

```python
try:
    sandbox.check_file_permission(Path("/path/to/file"), "read")
    with open("/path/to/file") as f:
        data = f.read()
except PermissionViolation:
    logger.error("Plugin lacks permission to read file")
```

##### check_network_permission

```python
def check_network_permission(
    self,
    host: str,
    port: int = 80
) -> bool:
```

Check if plugin can access a network resource.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `host` | `str` | Hostname or IP |
| `port` | `int` | Port number (default: 80) |

**Returns**: `bool` — True if permitted

**Example**:

```python
if sandbox.check_network_permission("api.example.com", 443):
    # Make API call
```

##### terminate

```python
def terminate() -> None:
```

Forcefully terminate the sandbox execution.

##### get_metrics

```python
def get_metrics() -> dict[str, Any]:
```

Get execution metrics (CPU, memory, time).

##### get_violations

```python
def get_violations() -> list[str]:
```

Get list of security violations that occurred.

---

### SandboxPermissions

Defines what resources a plugin can access.

**Location**: `backend/services/plugin_sandbox.py`

#### Constructor

```python
def __init__(
    self,
    plugin_id: str,
    granted_permissions: Set[str],
    allowed_paths: List[Path],
    allowed_hosts: List[str],
    allowed_ports: List[int]
):
```

#### Methods

##### has_permission

```python
def has_permission(self, permission: str) -> bool:
```

Check if plugin has a specific permission.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `permission` | `str` | Permission name (e.g., `"filesystem.read.workspace"`) |

**Returns**: `bool` — True if permission granted

**Example**:

```python
if permissions.has_permission("network.http"):
    # Can make HTTP requests
```

##### can_access_path

```python
def can_access_path(self, path: Path, operation: str) -> bool:
```

Check if plugin can access a file path.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `path` | `Path` | Path to check |
| `operation` | `str` | Operation: "read", "write", "execute" |

**Returns**: `bool` — True if access allowed

##### can_access_network

```python
def can_access_network(self, host: str, port: int) -> bool:
```

Check if plugin can access a network resource.

---

### ResourceLimits

Defines resource constraints for plugin execution.

**Location**: `backend/services/plugin_sandbox.py`

```python
@dataclass
class ResourceLimits:
    max_memory_mb: int = 512              # Max memory in MB
    max_cpu_percent: float = 100.0        # Max CPU percentage
    max_io_mbps: int = 100                # Max I/O speed
    max_execution_time_ms: int = 30000    # Max execution time
    max_concurrent_tasks: int = 4         # Max concurrent tasks
    max_file_size_mb: int = 100           # Max file size
    max_open_files: int = 64              # Max open files
    max_processes: int = 4                # Max subprocesses
    max_network_connections: int = 10     # Max network connections
    requires_gpu: bool = False            # GPU needed
```

---

### SandboxManager

Creates and manages sandboxes for plugins.

**Location**: `backend/services/plugin_sandbox.py`

#### Singleton Access

```python
@classmethod
def get_instance() -> SandboxManager:
```

Get the global sandbox manager instance.

**Example**:

```python
manager = SandboxManager.get_instance()
```

#### Methods

##### create_sandbox

```python
def create_sandbox(
    plugin_id: str,
    permissions: SandboxPermissions,
    limits: ResourceLimits
) -> PluginSandbox:
```

Create a new sandbox for a plugin.

**Returns**: `PluginSandbox` instance

##### get_sandbox

```python
def get_sandbox(plugin_id: str) -> Optional[PluginSandbox]:
```

Get existing sandbox for plugin or None.

##### destroy_sandbox

```python
def destroy_sandbox(plugin_id: str) -> None:
```

Destroy a sandbox and release resources.

##### destroy_all

```python
def destroy_all() -> None:
```

Destroy all sandboxes.

##### get_all_metrics

```python
def get_all_metrics() -> dict[str, dict[str, Any]]:
```

Get metrics for all active sandboxes.

---

## Schema Validation

### PluginSchemaValidator

Validates plugin manifests against the unified JSON schema.

**Location**: `backend/services/plugin_schema_validator.py`

#### Constructor

```python
def __init__(self, schema_path: Optional[Union[Path, str]] = None):
```

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `schema_path` | `Path \| str` | Path to JSON schema (uses default if None) |

#### Methods

##### validate

```python
def validate(manifest: dict) -> tuple[bool, list[str]]:
```

Validate a manifest dictionary.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `manifest` | `dict` | Parsed manifest JSON |

**Returns**: Tuple of (is_valid, error_messages)

**Example**:

```python
import json

with open("manifest.json") as f:
    manifest = json.load(f)

is_valid, errors = validator.validate(manifest)
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

##### validate_file

```python
def validate_file(path: Union[Path, str]) -> tuple[bool, list[str], Optional[dict]]:
```

Validate a manifest file.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `path` | `Path \| str` | Path to manifest.json file |

**Returns**: Tuple of (is_valid, error_messages, parsed_manifest)

**Example**:

```python
from pathlib import Path

is_valid, errors, manifest = validator.validate_file(
    Path("plugins/my_plugin/manifest.json")
)
```

---

## Plugin Manifest Schema Reference

### Required Fields

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `name` | `string` | `^[a-z][a-z0-9_]{0,63}$` | `"my_plugin"` |
| `version` | `string` | Semantic version | `"1.0.0"` |
| `author` | `string` | Free text | `"Your Name"` |
| `plugin_type` | `string` | `"backend_only" \| "frontend_only" \| "full_stack"` | `"backend_only"` |

### Key Sections

#### capabilities

```json
{
  "capabilities": {
    "backend_routes": true,
    "ui_panels": ["panel_id_1", "panel_id_2"],
    "effects": ["normalize", "amplify"],
    "engines": ["tts", "transcription"],
    "export_formats": ["mp3", "flac"],
    "import_formats": ["ogg", "m4a"],
    "integrations": ["slack", "discord"],
    "mcp_integration": false
  }
}
```

#### entry_points

```json
{
  "entry_points": {
    "backend": "plugin.register",
    "frontend": "MyPlugin.dll"
  }
}
```

#### permissions

Array of permission strings. See **Permission Vocabulary** section below.

#### settings_schema

JSON Schema defining plugin configuration:

```json
{
  "settings_schema": {
    "type": "object",
    "properties": {
      "option_name": {
        "type": "string",
        "default": "default value",
        "description": "What this option does"
      }
    }
  }
}
```

#### resource_limits

```json
{
  "resource_limits": {
    "max_memory_mb": 512,
    "max_cpu_percent": 50,
    "max_execution_time_ms": 30000,
    "requires_gpu": false
  }
}
```

---

## Permission Vocabulary

All available permissions for plugins using dot-notation:

### File System Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `filesystem.read.self` | Low | Read from plugin directory only |
| `filesystem.write.self` | Low | Write to plugin directory only |
| `filesystem.read.user_selected` | Medium | Read files user selects via dialog |
| `filesystem.write.user_selected` | Medium | Write to files user selects via dialog |
| `filesystem.read.workspace` | Medium | Read from project workspace directory |
| `filesystem.write.workspace` | Medium | Write to project workspace directory |
| `filesystem.execute` | High | Execute files or scripts |

### Network Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `network.localhost` | Low | Connect to localhost only |
| `network.allowed_domains` | Medium | Connect to pre-approved domains |
| `network.any` | High | Connect to any host |
| `network.listen` | Medium | Open listening ports (server mode) |

### Audio Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `audio.input` | High | Read audio input/microphone |
| `audio.output` | Low | Write/play audio |
| `audio.process` | Low | Process audio data |

### Engine Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `engine.tts` | Low | Use TTS engines |
| `engine.stt` | Low | Use transcription engines |
| `engine.vc` | Medium | Use voice conversion engines |
| `engine.config` | Low | Access engine configuration |
| `engine.register` | High | Register new engines |

### UI Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `ui.notify` | Low | Show notifications |
| `ui.dialog` | Low | Show dialogs |
| `ui.context_menu` | Medium | Add context menu items |
| `ui.toolbar` | Medium | Add toolbar items |
| `ui.panel` | Medium | Add UI panels |
| `ui.theme` | Low | Access theme settings |

### Data Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `data.project.read` | Low | Read project data |
| `data.project.write` | Medium | Modify project data |
| `data.settings.read` | Low | Read user settings |
| `data.settings.write` | High | Modify user settings |
| `data.storage` | Low | Use persistent storage |

### System Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `system.info` | Low | Access system information |
| `system.process` | High | Execute subprocesses |
| `system.clipboard.read` | Medium | Read clipboard |
| `system.clipboard.write` | Medium | Write to clipboard |

### Integration Permissions

| Permission | Risk | Description |
|-----------|------|-------------|
| `integration.plugin_events` | Low | Subscribe to plugin events |
| `integration.plugin_call` | Medium | Call other plugins |
| `integration.external_api` | Medium | Integrate with external APIs |

---

## REST API Endpoints

### Plugin Management Endpoints

#### List All Plugins

```
GET /api/plugins
```

**Response**:
```json
{
  "plugins": [
    {
      "name": "my_plugin",
      "state": "active",
      "version": "1.0.0"
    }
  ]
}
```

#### Get Plugin Info

```
GET /api/plugins/{plugin_id}
```

**Response**:
```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "author": "Author Name",
  "description": "Plugin description",
  "state": "active"
}
```

#### Get Plugin Manifest

```
GET /api/plugins/{plugin_id}/manifest
```

**Response**: Full manifest.json content

#### Load Plugin

```
POST /api/plugins/{plugin_id}/load
```

#### Unload Plugin

```
POST /api/plugins/{plugin_id}/unload
```

#### Get Plugin Config

```
GET /api/plugins/{plugin_id}/config
```

#### Update Plugin Config

```
PUT /api/plugins/{plugin_id}/config
```

---

## WebSocket Protocol

### Connection

**URL**: `ws://localhost:8000/ws/plugins`

### Message Format

All messages are JSON objects with a `type` field:

#### Request: Sync Request

```json
{
  "type": "sync_request"
}
```

#### Response: Full Sync

```json
{
  "type": "plugin_sync",
  "payload": {
    "action": "sync_all",
    "plugins": [
      {
        "id": "my_plugin",
        "state": "active",
        "permissions": [...]
      }
    ]
  }
}
```

#### Request: Plugin Command

```json
{
  "type": "plugin_command",
  "command": "enable",
  "plugin_id": "my_plugin"
}
```

**Available commands**: `enable`, `disable`, `reload`, `health_check`, `install`, `uninstall`

#### Response: Command Response

```json
{
  "type": "plugin_command_response",
  "payload": {
    "success": true,
    "message": "Command executed"
  }
}
```

---

## Complete Example

Here's a minimal complete backend plugin using all concepts:

```python
"""
Complete Backend Plugin Example
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.plugins_api.base import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)


class ProcessRequest(BaseModel):
    data: str


class ProcessResponse(BaseModel):
    result: str
    timestamp: str


class CompletePlugin(BasePlugin):
    """A complete plugin demonstrating all concepts."""
    
    def __init__(self, plugin_dir: Path):
        metadata = PluginMetadata(plugin_dir / "manifest.json")
        super().__init__(metadata)
        self.plugin_dir = plugin_dir
        self.router = APIRouter(prefix="/api/plugin/complete")
    
    def register(self, app) -> None:
        """Register routes with FastAPI."""
        self.router.post("/process")(self.process)
        self.router.get("/health")(self.health)
        app.include_router(self.router)
        logger.info(f"{self.name}: Registered routes")
    
    def initialize(self) -> None:
        """Initialize plugin."""
        super().initialize()
        logger.info(f"{self.name}: Initialized")
    
    def cleanup(self) -> None:
        """Cleanup on shutdown."""
        super().cleanup()
        logger.info(f"{self.name}: Cleaned up")
    
    async def process(self, request: ProcessRequest) -> ProcessResponse:
        """Process data."""
        return ProcessResponse(
            result=request.data.upper(),
            timestamp=datetime.now().isoformat()
        )
    
    async def health(self) -> dict[str, Any]:
        """Health check."""
        return {
            "healthy": self.is_initialized(),
            "plugin": self.name,
            "version": self.version
        }


def register(app, plugin_dir: Path) -> CompletePlugin:
    """Entry point for plugin loader."""
    plugin = CompletePlugin(plugin_dir)
    plugin.register(app)
    plugin.initialize()
    return plugin
```

---

## Best Practices

1. **Always inherit from BasePlugin** — Use the proper base class for your plugin type
2. **Implement error handling** — Never suppress errors with empty except blocks
3. **Use logging** — Log important events with context
4. **Validate inputs** — Use Pydantic for request validation
5. **Request minimum permissions** — Only ask for what you need
6. **Use async** — Define FastAPI routes as async for performance
7. **Document your API** — Include docstrings and examples
8. **Write tests** — Test your plugin independently

---

## Reference Links

- [Getting Started Guide](getting-started.md)
- [Best Practices Guide](best-practices.md)
- [Frontend API Reference](api-reference-frontend.md)
- [Manifest Schema](../../shared/schemas/plugin-manifest.schema.json)
