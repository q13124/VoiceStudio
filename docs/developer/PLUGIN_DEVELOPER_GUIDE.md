# VoiceStudio Plugin Developer Guide

**Version:** 1.0.0
**Last Updated:** 2026-02-21
**Schema Version:** 6.0.0

This guide covers everything you need to build, test, sign, and publish plugins for VoiceStudio.

---

## Prerequisites

- Python 3.9+
- VoiceStudio repository cloned
- Plugin CLI available at `tools/plugin-cli/`

## Plugin Architecture Overview

VoiceStudio plugins extend the platform without modifying core code. The plugin system consists of:

- **Plugin Service** (`backend/services/plugin_service.py`) -- discovers, loads, and manages plugin lifecycle
- **Plugin Sandbox** (`backend/services/plugin_sandbox.py`) -- isolates plugins with path restrictions and resource limits
- **Plugin Gallery** (`backend/plugins/gallery/`) -- catalog browsing, installation, and updates
- **Plugin CLI** (`tools/plugin-cli/`) -- development tools for init, validate, test, pack, sign, publish
- **Manifest Schema** (`shared/schemas/plugin-manifest.schema.json`) -- v6.0.0 unified schema

### Plugin Types

| Type | Description | Examples |
|------|-------------|----------|
| `backend_only` | Python-only processing, no UI | Noise reduction, format converter |
| `frontend_only` | C# UI panel, no backend logic | Custom visualization, theme |
| `full_stack` | Both Python backend and C# UI | Interactive audio editor |

### Categories

| Category | Description |
|----------|-------------|
| `voice_synthesis` | Text-to-speech plugins |
| `speech_recognition` | Speech-to-text plugins |
| `audio_effects` | Audio processing and effects |
| `audio_analysis` | Audio analysis and metrics |
| `voice_conversion` | Voice identity conversion |
| `utilities` | Format conversion, general tools |
| `integrations` | External service connectors |
| `developer_tools` | Debugging and development tools |

---

## Quick Start

### 1. Initialize a New Plugin

```bash
cd tools/plugin-cli
python -m plugin_cli init --name my_plugin --template processing
```

Available templates: `basic`, `synthesis`, `transcription`, `processing`, `enhancement`, `embedding`, `diarization`, `multilingual`

This creates a directory structure:

```
my_plugin/
  manifest.json      # Plugin manifest (schema v6.0.0)
  plugin.py          # Entry point with plugin class
  __init__.py         # Package init
  tests/
    test_plugin.py   # Unit tests
  README.md          # Plugin documentation
```

### 2. Implement Your Plugin

Your plugin class must implement these methods:

```python
class MyPlugin:
    PLUGIN_ID = "com.yourname.my_plugin"
    PLUGIN_VERSION = "1.0.0"

    async def activate(self) -> bool:
        """Called when plugin is enabled. Return True on success."""
        return True

    async def deactivate(self) -> None:
        """Called when plugin is disabled. Clean up resources."""
        pass

    def configure(self, settings: dict) -> None:
        """Apply user configuration settings."""
        pass

    async def process(self, input_data: dict) -> dict:
        """Process input data and return results."""
        audio_path = input_data["audio_path"]
        # ... your processing logic ...
        return {"audio_path": output_path}

    def get_info(self) -> dict:
        """Return plugin metadata."""
        return {"id": self.PLUGIN_ID, "version": self.PLUGIN_VERSION}
```

### 3. Configure the Manifest

Edit `manifest.json` with your plugin details:

```json
{
  "schema_version": "6.0.0",
  "id": "com.yourname.my_plugin",
  "name": "my_plugin",
  "display_name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "plugin_type": "backend_only",
  "category": "audio_effects",
  "entry_point": "plugin.py",
  "permissions": {
    "filesystem": {
      "read": ["$PLUGIN_DIR", "$TEMP_DIR"],
      "write": ["$TEMP_DIR"]
    },
    "network": false
  }
}
```

Required fields: `name`, `version`, `author`, `plugin_type`, `category`

### 4. Validate

```bash
python -m plugin_cli validate --path my_plugin/
```

### 5. Test

```bash
python -m plugin_cli test --path my_plugin/
```

### 6. Package

```bash
python -m plugin_cli pack --path my_plugin/
```

Creates a `.vspkg` archive for distribution.

### 7. Sign

```bash
python -m plugin_cli sign --package my_plugin-1.0.0.vspkg
```

Uses Ed25519 cryptographic signing. Keys are stored locally in your keystore.

### 8. Publish

```bash
python -m plugin_cli publish --package my_plugin-1.0.0.vspkg.signed
```

---

## Security Requirements

### Permissions

Plugins must declare all required permissions in `manifest.json`:

- **Filesystem**: Use `$PLUGIN_DIR`, `$TEMP_DIR`, `$PROJECT_DIR` variables (never absolute paths)
- **Network**: Set to `false` unless the plugin genuinely needs network access
- **Subprocess**: Set to `true` only if the plugin calls external executables (e.g., FFmpeg)

### Sandbox

All plugins run in an isolated sandbox with:
- Temporary workspace in system temp directory
- Path access restricted to declared paths only
- Resource limits (memory, CPU, execution time)
- No access to the host filesystem outside allowed paths

### Signing

All published plugins must be cryptographically signed with Ed25519. The plugin service verifies signatures before loading. Unsigned plugins can only run in development mode.

---

## Manifest Reference

See the full schema at `shared/schemas/plugin-manifest.schema.json` (v6.0.0). Key sections:

| Section | Purpose |
|---------|---------|
| `permissions` | Filesystem, network, subprocess access |
| `dependencies` | Runtime and Python package requirements |
| `settings_schema` | JSON Schema for user-configurable settings |
| `catalog` | Tags, featured status, verified flag |
| `distribution` | Published state, release channel |
| `security` | Isolation mode, resource limits |

---

## Configuration Schema (Phase 8 WS3)

The `settings_schema` in your manifest defines user-configurable options. The schema follows JSON Schema. Supported types: `string`, `number`, `boolean`, `integer`, `enum`.

Example:

```json
"settings_schema": {
  "type": "object",
  "properties": {
    "reduction_strength": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "default": 0.7,
      "description": "Noise reduction strength (0.0 = none, 1.0 = maximum)"
    },
    "stationary": {
      "type": "boolean",
      "default": true,
      "description": "Use stationary noise reduction"
    }
  }
}
```

Your plugin receives settings via `configure(settings: dict)`. Persist per-plugin config to `data/plugin_config/{plugin_id}.json` when using the plugin settings UI.

---

## Permission Model

Plugins declare permissions in the manifest. The sandbox enforces these at runtime:

| Permission | Values | Description |
|------------|--------|-------------|
| `filesystem.read` | List of path variables | Directories the plugin may read |
| `filesystem.write` | List of path variables | Directories the plugin may write |
| `network` | `true` / `false` | Whether the plugin may make network requests |
| `subprocess` | `true` / `false` | Whether the plugin may spawn subprocesses |

Path variables: `$PLUGIN_DIR`, `$TEMP_DIR`, `$PROJECT_DIR`. Never use absolute paths.

Before install, the gallery displays declared permissions. Users can approve or deny. Denied permissions are enforced at the sandbox boundary.

---

## API Endpoints

### Plugin Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plugins` | GET | List all loaded plugins |
| `/api/plugins/{id}` | GET | Get plugin details |
| `/api/plugins/{id}/load` | POST | Load a plugin |
| `/api/plugins/{id}/unload` | POST | Unload a plugin |
| `/api/plugins/{id}/config` | GET | Get plugin configuration |
| `/api/plugins/{id}/config` | PUT | Update plugin configuration |

### Plugin Gallery

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plugin-gallery/catalog` | GET | Browse plugin catalog |
| `/api/plugin-gallery/catalog/search` | GET | Search plugins by query |
| `/api/plugin-gallery/install` | POST | Install a plugin |
| `/api/plugin-gallery/installed` | GET | List installed plugins |
| `/api/plugin-gallery/updates` | GET | Check for updates |

### WebSocket

| Endpoint | Purpose |
|----------|---------|
| `/ws/plugins` | Real-time plugin state synchronization |

---

## Reference Plugins

Three reference plugins demonstrate the system. Study them as examples:

| Plugin | Category | What It Shows |
|--------|----------|---------------|
| `plugins/reference/noise_reduction/` | audio_effects | Audio processing with noisereduce library |
| `plugins/reference/format_converter/` | utilities | FFmpeg-based format conversion with subprocess |
| `plugins/reference/silence_detector/` | audio_analysis | Librosa-based audio analysis |

---

## Testing Your Plugin

### Unit Tests

```bash
python -m pytest my_plugin/tests/ -v
```

### Integration with VoiceStudio

```bash
# Start the backend
python -m uvicorn backend.api.main:app --reload

# Test loading your plugin
curl -X POST http://localhost:8000/api/plugins/com.yourname.my_plugin/load
```

### Running the Plugin E2E Test Suite

```bash
python -m pytest tests/e2e/test_plugin_lifecycle.py -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Plugin not discovered | Check `entry_point` in manifest matches your file |
| Manifest validation fails | Run `python -m plugin_cli validate` for details |
| Sandbox blocks file access | Add paths to `permissions.filesystem` in manifest |
| Signing fails | Ensure `cryptography` package is installed |
| Plugin crashes host | Check resource limits in sandbox configuration |
