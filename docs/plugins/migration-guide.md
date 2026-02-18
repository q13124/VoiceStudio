# Plugin Feature Migration Guide

## Purpose

Guide for migrating existing VoiceStudio functionality into plugin-based units
without changing behavior.

---

## Phase 4: Unified Plugin Migration (ADR-038)

**Version 1.3.0** introduces a unified `Plugin` ABC that replaces all legacy plugin base classes.

### Deprecated Classes (Will Be Removed in v1.5.0)

| Deprecated Class | Location | Replacement |
|------------------|----------|-------------|
| `BasePlugin` | `app/core/plugins_api/base.py` | `Plugin` from `app.core.plugins_api` |
| `PluginBase` | `backend/services/plugin_service.py` | `Plugin` from `app.core.plugins_api` |
| `EnginePlugin` | `backend/services/plugin_service.py` | `Plugin` + `EngineMixin` |
| `ProcessorPlugin` | `backend/services/plugin_service.py` | `Plugin` + `ProcessorMixin` |
| `ExporterPlugin` | `backend/services/plugin_service.py` | `Plugin` + `ExporterMixin` |
| `ImporterPlugin` | `backend/services/plugin_service.py` | `Plugin` + `ImporterMixin` |
| `Plugin` | `backend/plugins/core/base.py` | `Plugin` from `app.core.plugins_api` |

### Migration from BasePlugin

**Before (deprecated):**

```python
from app.core.plugins_api.base import BasePlugin, PluginMetadata

class MyPlugin(BasePlugin):
    def __init__(self, plugin_dir: Path):
        metadata = PluginMetadata(plugin_dir / "manifest.json")
        super().__init__(metadata)
        self.router = APIRouter(prefix="/api/plugin/my_plugin")
```

**After (recommended):**

```python
from app.core.plugins_api import Plugin

class MyPlugin(Plugin):
    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)  # Handles metadata loading
        self.router = APIRouter(prefix="/api/plugin/my_plugin")
```

### Migration from PluginBase/ExporterPlugin

**Before (deprecated):**

```python
from backend.services.plugin_service import ExporterPlugin, PluginManifest

class MyExporter(ExporterPlugin):
    def __init__(self, plugin_service):
        super().__init__(plugin_service)
        self._manifest = PluginManifest.from_dict({...})
```

**After (recommended):**

```python
from app.core.plugins_api import Plugin, ExporterMixin

class MyExporter(Plugin, ExporterMixin):
    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)  # Loads from manifest.json
        self.router = APIRouter(prefix="/api/plugin/my_exporter")

    def register(self, app) -> None:
        self.router.post("/export")(self.export_endpoint)
        app.include_router(self.router)

    @property
    def supported_formats(self) -> list[str]:
        return ["myformat"]

    @property
    def target_format(self) -> str:
        return "myformat"
```

### Available Mixins

| Mixin | Purpose | Key Methods/Properties |
|-------|---------|------------------------|
| `EngineMixin` | TTS/synthesis engines | `synthesize()`, `list_voices()`, `sample_rate` |
| `ProcessorMixin` | Audio effect processors | `process()` |
| `ExporterMixin` | Format exporters | `export()`, `supported_formats` |
| `ImporterMixin` | Format importers | `import_file()`, `supported_formats` |
| `UIPanelMixin` | UI panel providers | `panel_title`, `panel_template` |

### Key Differences

| Aspect | Legacy ABCs | Unified Plugin |
|--------|-------------|----------------|
| Initialization | `metadata` or `plugin_service` param | `plugin_dir: Path` param |
| Metadata | Manually created | Loaded from `manifest.json` automatically |
| Type contracts | Separate base classes | Mixins (composable) |
| Module location | Multiple locations | Single: `app.core.plugins_api` |

### Migration Checklist

- [ ] Update import: `from app.core.plugins_api import Plugin`
- [ ] Change base class to `Plugin`
- [ ] Update `__init__` to accept `plugin_dir: Path`
- [ ] Call `super().__init__(plugin_dir)` (not `metadata`)
- [ ] Add mixins if needed (e.g., `ExporterMixin`)
- [ ] Ensure `register(app)` method exists
- [ ] Update module-level `register(app, plugin_dir)` function
- [ ] Test plugin loads without deprecation warnings

---

## Pattern 1: Audio Effect Migration

### Target

- Source DSP in `backend/voice/effects/*` or `app/core/audio/*`
- Plugin wrapper in `plugins/<effect_name>/`

### Steps

1. Extract or wrap existing DSP logic in `processor.py`.
2. Keep request/response models in `plugin.py` route layer.
3. Register routes under `/api/plugin/<plugin_name>/...`.
4. Add preset JSON files when effect has tunable parameters.
5. Add regression test comparing plugin output to source module output.

### Checklist

- [ ] Manifest validates with `PluginSchemaValidator`
- [ ] Route returns deterministic schema
- [ ] Regression tests pass with float tolerance
- [ ] Effect can be disabled without host crash

## Pattern 2: Engine Adapter Migration

### Target

- Existing engine class remains in `app/core/engines/`
- Adapter plugin in `plugins/engine_<name>/`

### Steps

1. Create `adapter.py` wrapping engine initialize/synthesize/cleanup calls.
2. Create plugin route layer in `plugin.py`.
3. Register engine metadata in registry on plugin initialize.
4. Keep engine logic out of plugin (no model reimplementation).
5. Add adapter unit tests with fake engine stubs.

### Checklist

- [ ] Adapter is thin (delegates, does not duplicate engine logic)
- [ ] Plugin lifecycle maps to engine lifecycle
- [ ] Plugin failures return errors without crashing host

## Pattern 3: Format Exporter Migration

### Target

- Converter remains `backend/core/audio/conversion.py`
- Export plugin in `plugins/export_<format>/`

### Steps

1. Implement `ExporterPlugin` contract wrapper.
2. Accept base64 WAV payload at route boundary.
3. Decode to temp WAV and call `AudioConversionService.convert_to_format`.
4. Return success/failure state with safe diagnostics.
5. Add tests using mocked conversion service.

### Checklist

- [ ] Format-specific manifest capability set
- [ ] Service call passes format/options correctly
- [ ] Exporter tests pass without FFmpeg dependency

## Plugin Loading Systems

VoiceStudio has **two** plugin loading paths.  Understanding which one applies
avoids confusion when writing or debugging plugins.

### PluginLoader (startup loader)

| Attribute | Value |
|-----------|-------|
| **Module** | `backend/api/plugins/loader.py` |
| **Base class** | `Plugin` (`app/core/plugins_api`) — also supports deprecated `BasePlugin` |
| **When called** | `startup_event()` in `backend/api/main.py` |
| **Entry point** | `register(app, plugin_dir)` function in `plugin.py` |
| **Lifecycle** | Sync: `register(app)` → `initialize()` → `cleanup()` |
| **Used by** | All plugins (audio effects, engine adapters, exporters, processors) |

**How it works:**

1. Scans `plugins/` for directories with `manifest.json`.
2. Reads `entry_points.backend` from the manifest (e.g. `"register"`).
3. Loads `plugin.py` via `importlib.util.spec_from_file_location`.
4. Temporarily adds the plugin directory to `sys.path` for bare imports.
5. Calls the entry-point function: `register(app, plugin_dir)`.
6. Cleans up `sys.modules` to prevent cross-plugin import contamination.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Entry point not found" | `entry_points.backend` is `"plugin.register"` instead of `"register"` | Use function name only: `"register"` |
| Wrong module imported (e.g. compressor gets normalize_volume's processor) | `sys.modules` contamination | Already fixed in loader; ensure plugin dirs don't share module names with `sys.path` entries |
| Plugin loads in dev but not in test | Test runner doesn't add plugin dir to `sys.path` | Use `plugins.<name>.module` import path in tests, or replicate loader's path logic |

### PluginService (service-layer lifecycle)

| Attribute | Value |
|-----------|-------|
| **Module** | `backend/services/plugin_service.py` |
| **Base class** | `Plugin` (`app/core/plugins_api`) — also supports deprecated `PluginBase` |
| **When called** | WebSocket plugin management, dynamic load/unload |
| **Entry point** | `load_plugin()` method on `PluginService` |
| **Lifecycle** | Sync: `initialize()` → `register(app)` → `cleanup()` (unified Plugin) |
| **Used by** | Dynamic plugin management, gallery installations |

### Which base class to use?

**v1.3.0+: Use the unified `Plugin` class with optional mixins (see ADR-038).**

| Plugin type | Recommended base | Reason |
|-------------|-----------------|--------|
| Audio effect (DSP) | `Plugin` | Simple sync lifecycle, unified interface |
| Engine adapter | `Plugin` + `EngineMixin` | Wraps existing engine; mixin adds synthesis contract |
| Format exporter | `Plugin` + `ExporterMixin` | Mixin provides `export()` / `supported_formats` contract |
| Format importer | `Plugin` + `ImporterMixin` | Mixin provides `import_file()` / `supported_formats` contract |
| Processor | `Plugin` + `ProcessorMixin` | Mixin provides audio processing contract |
| UI panel | `Plugin` + `UIPanelMixin` | Mixin provides panel metadata |

See [Phase 4: Unified Plugin Migration (ADR-038)](#phase-4-unified-plugin-migration-adr-038) for complete migration guidance.

### Legacy Dual-ABC rationale (DEPRECATED)

> **Note:** The section below describes the deprecated system. Use the unified `Plugin` class from `app.core.plugins_api` for new development. Legacy classes will be removed in v1.5.0.

The two legacy base classes existed because they served different purposes:

- **`BasePlugin`** (deprecated) was minimal and sync-oriented — suited for plugins loaded at
  startup that register FastAPI routes and initialize once.
- **`PluginBase`** (deprecated) was richer with async lifecycle, settings integration, and
  typed subclasses (`ProcessorPlugin`, `ExporterPlugin`, `EnginePlugin`) — suited
  for plugins managed dynamically via WebSocket or the plugin gallery.

**These classes are now deprecated.** The unified `Plugin` class from `app.core.plugins_api`
combines the best of both approaches with optional mixins for type-specific contracts.
Migrate existing plugins using the [Phase 4 migration guide](#phase-4-unified-plugin-migration-adr-038).

---

## Regression Testing Methodology

1. Create deterministic source signal (fixed seed or sinusoid).
2. Run source implementation and migrated plugin path.
3. Compare arrays with `np.testing.assert_allclose(...)`.
4. Enforce strict tolerances unless algorithm intentionally changed.

## Performance Benchmarking Methodology

- **Effects**: process 1 second/44.1kHz in <100ms per effect function test.
- **Adapters**: mock heavy engine in unit tests; profile real engines separately.
- **Exporters**: benchmark conversion service path with representative WAV sizes.

---

## Phase 4: Plugin SDK and Marketplace Migration

**Version 2.0.0** introduces the VoiceStudio Plugin SDK (`voicestudio-plugin-sdk`) and the community marketplace (Gallery). This section covers migrating existing internal plugins to the new SDK.

### Overview

The SDK provides:
- Standalone Python package (`pip install voicestudio-plugin-sdk`)
- Type-safe base classes with full type hints
- Built-in audio handling utilities
- Configuration schema system
- Testing utilities (MockHost, PluginTestCase)
- CLI tools for plugin development

### SDK Installation

```bash
# For plugin developers
pip install voicestudio-plugin-sdk

# For development
pip install voicestudio-plugin-sdk[dev]

# CLI tools
pip install voicestudio-plugin-cli
```

### Migration from Internal Plugin Classes

#### Before (internal implementation):

```python
from app.core.plugins_api import Plugin, EngineMixin

class MySynthesisPlugin(Plugin, EngineMixin):
    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        
    def initialize(self) -> None:
        self._model = load_model()
        
    def synthesize(self, text: str) -> bytes:
        return self._model.generate(text)
```

#### After (SDK-based):

```python
from voicestudio_sdk import SynthesisPlugin, PluginContext, AudioBuffer, register_plugin

@register_plugin("com.mycompany.my-synthesis")
class MySynthesisPlugin(SynthesisPlugin):
    async def initialize(self, ctx: PluginContext) -> None:
        await super().initialize(ctx)
        self._model = await self._load_model()
        
    async def synthesize(self, text: str, voice: str = "default", **options) -> AudioBuffer:
        audio_data = await self._model.generate(text, voice)
        return AudioBuffer(
            data=audio_data,
            sample_rate=22050,
            format=AudioFormat.WAV
        )
    
    async def get_voices(self) -> list:
        return ["default", "male", "female"]
```

### Key Migration Changes

| Aspect | Internal Plugin | SDK Plugin |
|--------|-----------------|------------|
| Import | `from app.core.plugins_api import Plugin` | `from voicestudio_sdk import Plugin` |
| Registration | None | `@register_plugin("id")` decorator |
| Lifecycle | Sync methods | Async methods |
| Context | `plugin_dir: Path` | `PluginContext` object |
| Audio | `bytes` | `AudioBuffer` class |
| Configuration | Manual dict handling | `PluginConfig` + `ConfigField` |
| Host API | Direct service calls | `HostAPI` interface |
| Testing | pytest + mocks | `PluginTestCase` + `MockHost` |

### Specialized Plugin Types

The SDK provides specialized base classes:

| Plugin Type | SDK Class | Required Methods |
|-------------|-----------|------------------|
| TTS | `SynthesisPlugin` | `synthesize()`, `get_voices()` |
| STT | `TranscriptionPlugin` | `transcribe()`, `get_languages()` |
| Effects | `ProcessingPlugin` | `process()` |
| Enhancement | `EnhancementPlugin` | `enhance()` |
| Analysis | `AnalysisPlugin` | `analyze()` |

### Manifest v4 Updates

SDK plugins use manifest v4 schema:

```json
{
  "$schema": "https://voicestudio.app/schemas/plugin-manifest.v4.json",
  "id": "com.mycompany.my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "plugin_type": "synthesis",
  "min_voicestudio_version": "2.0.0",
  
  "entry_point": {
    "module": "my_plugin.main",
    "class": "MyPlugin"
  },
  
  "security": {
    "permissions": ["file_read"],
    "sandbox_mode": "subprocess"
  },
  
  "distribution": {
    "package_format": "vspkg"
  }
}
```

### Audio Handling Migration

#### Before:

```python
def process_audio(self, audio_data: bytes) -> bytes:
    # Manual WAV parsing
    with io.BytesIO(audio_data) as f:
        sample_rate, samples = read_wav(f)
    processed = self._process(samples)
    return write_wav(processed, sample_rate)
```

#### After:

```python
async def process(self, audio: AudioBuffer, **options) -> AudioBuffer:
    samples = audio.as_raw_samples()
    processed = await self._process(samples)
    return AudioBuffer.from_raw_samples(
        samples=processed,
        sample_rate=audio.sample_rate,
        channels=audio.channels
    )
```

### Configuration Migration

#### Before:

```python
def __init__(self, plugin_dir: Path):
    super().__init__(plugin_dir)
    config = self.manifest.get("config", {})
    self.model_size = config.get("model_size", "medium")
```

#### After:

```python
from voicestudio_sdk import PluginConfig, ConfigField, ConfigType

def get_config_schema(self) -> PluginConfig:
    config = PluginConfig()
    config.add_field(ConfigField(
        name="model_size",
        field_type=ConfigType.SELECT,
        label="Model Size",
        options=["small", "medium", "large"],
        default="medium"
    ))
    return config

async def initialize(self, ctx: PluginContext) -> None:
    self.model_size = ctx.get_config("model_size", "medium")
```

### Testing Migration

#### Before:

```python
import pytest
from unittest.mock import Mock

class TestMyPlugin:
    def test_process(self):
        plugin = MyPlugin(Path("./test_plugin"))
        plugin.initialize()
        result = plugin.process(test_audio_bytes)
        assert len(result) > 0
```

#### After:

```python
from voicestudio_sdk.testing import PluginTestCase, MockHost

class TestMyPlugin(PluginTestCase):
    plugin_class = MyPlugin
    
    async def test_process(self):
        result = await self.plugin.process(self.create_test_audio())
        self.assert_valid_audio(result)
        assert self.host.has_log("info", "Processing complete")
```

### SDK Migration Checklist

- [ ] Install SDK: `pip install voicestudio-plugin-sdk`
- [ ] Update imports to use `voicestudio_sdk`
- [ ] Add `@register_plugin` decorator
- [ ] Convert lifecycle methods to async
- [ ] Replace `plugin_dir` with `PluginContext`
- [ ] Use `AudioBuffer` instead of raw bytes
- [ ] Implement `get_config_schema()` for configuration
- [ ] Update tests to use `PluginTestCase`
- [ ] Update manifest to v4 schema
- [ ] Add `security` section to manifest
- [ ] Test with `voicestudio-plugin test`
- [ ] Validate with `voicestudio-plugin validate`

### Marketplace Preparation

For plugins intended for the Gallery:

1. **Package**: `voicestudio-plugin pack`
2. **Sign**: `voicestudio-plugin sign --key your-key.pem`
3. **Validate**: `voicestudio-plugin validate --strict`
4. **Publish**: `voicestudio-plugin publish`

See [PLUGIN_MARKETPLACE_GUIDE.md](../developer/PLUGIN_MARKETPLACE_GUIDE.md) for complete publishing instructions.

---

## SDK Documentation Resources

| Resource | Description |
|----------|-------------|
| [Plugin Development Guide](../developer/PLUGIN_DEVELOPMENT_GUIDE.md) | Getting started with SDK |
| [SDK API Reference](../developer/PLUGIN_SDK_REFERENCE.md) | Complete API documentation |
| [CLI Reference](../developer/PLUGIN_CLI_REFERENCE.md) | CLI command documentation |
| [Security Guide](../developer/PLUGIN_SECURITY_GUIDE.md) | Security best practices |
| [Testing Guide](../developer/PLUGIN_TESTING_GUIDE.md) | Testing plugins |
| [Marketplace Guide](../developer/PLUGIN_MARKETPLACE_GUIDE.md) | Publishing to Gallery |
