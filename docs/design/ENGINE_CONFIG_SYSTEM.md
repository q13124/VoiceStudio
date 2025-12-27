# Engine Configuration System
## Default Engines, Overrides, and Installed Tracking

**Purpose:** Manage engine defaults, per-task overrides, and track installed engines.

---

## 📋 Configuration File

Engine configuration is stored in `engines/config.json`:

```json
{
  "defaults": {
    "tts": "xtts_v2",
    "image_gen": "sdxl_comfy",
    "video_gen": "svd"
  },
  "overrides": {},
  "installed": [
    "xtts_v2",
    "piper",
    "openvoice",
    "sdxl_comfy",
    "realesrgan",
    "svd"
  ]
}
```

### Configuration Fields

- **defaults:** Default engine for each task type
  - `tts` - Text-to-speech engines
  - `image_gen` - Image generation engines
  - `video_gen` - Video generation engines
  - Additional task types can be added

- **overrides:** Per-task overrides (takes precedence over defaults)
  - Can override default for specific tasks
  - Empty object means no overrides

- **installed:** List of installed engine IDs
  - Tracks which engines are available
  - Used for UI display and validation

---

## 🔧 Usage

### Getting Default Engines

```python
from app.core.engines.config import get_engine_config

config = get_engine_config()

# Get default TTS engine
tts_engine_id = config.get_default_engine("tts")
# Returns: "xtts_v2"

# Get default image generation engine
img_engine_id = config.get_default_engine("image_gen")
# Returns: "sdxl_comfy"
```

### Setting Default Engines

```python
# Set default TTS engine
config.set_default_engine("tts", "piper")

# Set default video generation engine
config.set_default_engine("video_gen", "svd")
```

### Using Overrides

```python
# Override default for a specific use case
config.set_override("tts", "openvoice")

# Clear override
config.clear_override("tts")
```

### Managing Installed Engines

```python
# Check if engine is installed
if config.is_installed("xtts_v2"):
    print("XTTS v2 is installed")

# Get all installed engines
installed = config.get_installed_engines()
# Returns: ["xtts_v2", "piper", "openvoice", ...]

# Add installed engine
config.add_installed_engine("new_engine")

# Remove installed engine
config.remove_installed_engine("old_engine")
```

---

## 🎯 Integration with Engine Router

### Automatic Default Selection

The engine router and runtime manager automatically use defaults:

```python
from app.core.engines.router import router
from app.core.runtime import RuntimeEngineManager

# Get engine for task type (uses default)
tts_engine = router.get_engine_for_task_type("tts")
# Returns default TTS engine (xtts_v2)

# Runtime manager also respects defaults
runtime_manager = RuntimeEngineManager()
tts_runtime = runtime_manager.get_engine_for_task("tts", prefer_default=True)
```

### Engine Hook Integration

The EngineHook provides unified access:

```python
from app.core.runtime import hook

# Get default engine for task type
tts_engine = hook.get_default_engine("tts")

# Get engine for specific task (respects defaults and overrides)
engine = hook.get_engine_for_task("tts")
```

---

## 🔄 Override Priority

When getting an engine, priority is:

1. **Override** (if set for task type)
2. **Default** (from config)
3. **First available** (fallback)

Example:
```python
# Config has: defaults.tts = "xtts_v2"
# Override set: overrides.tts = "piper"

engine_id = config.get_default_engine("tts")
# Returns: "piper" (override takes precedence)
```

---

## 📊 Task Type Mapping

Tasks map to task types:

| Task | Task Type |
|------|-----------|
| `tts` | `tts` |
| `clone_infer` | `tts` |
| `embed_voice` | `tts` |
| `text_to_image` | `image_gen` |
| `image_to_image` | `image_gen` |
| `image_to_video` | `video_gen` |
| `video_generation` | `video_gen` |

---

## 🚀 Auto-Discovery

When engines are loaded, they can be automatically added to installed list:

```python
from app.core.engines.router import router
from app.core.engines.config import get_engine_config

# Load all engines
router.load_all_engines("engines")

# Auto-add to installed list
config = get_engine_config()
for engine_id in router.list_engines():
    config.add_installed_engine(engine_id)
```

---

## 💾 Configuration Persistence

Configuration is automatically saved to `engines/config.json` when:
- Default engine is set
- Override is set/cleared
- Installed engine is added/removed
- Configuration is updated

The file is created automatically if it doesn't exist.

---

## 📚 Reference

- **Config Manager:** `app/core/engines/config.py`
- **Engine Router:** `app/core/engines/router.py`
- **Runtime Manager:** `app/core/runtime/runtime_engine.py`
- **Engine Hook:** `app/core/runtime/engine_hook.py`
- **Config File:** `engines/config.json`

---

**The configuration system provides centralized management of engine defaults, overrides, and installation tracking.**

