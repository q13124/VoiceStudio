# Engine Manifest System
## Declarative Engine Registration

**Purpose:** Engine manifests provide a declarative way to register and configure engines without hardcoding.

---

## 📁 Directory Structure

Engines are organized by type in `engines/`:

```
engines/
├── audio/
│   ├── xtts_v2/
│   │   └── engine.manifest.json
│   ├── piper/
│   │   └── engine.manifest.json
│   └── openvoice/
│       └── engine.manifest.json
├── image/
│   ├── sdxl_comfy/
│   │   └── engine.manifest.json
│   └── upscalers/
│       └── realesrgan/
│           └── engine.manifest.json
└── video/
    └── svd/
        └── engine.manifest.json
```

---

## 📋 Manifest Format

Each `engine.manifest.json` contains:

### Required Fields

- **engine_id:** Unique identifier (e.g., "xtts_v2")
- **name:** Human-readable name
- **type:** Engine type ("audio", "image", "video")
- **version:** Engine version
- **entry_point:** Python class path (e.g., "app.core.engines.xtts_engine.XTTSEngine")
- **dependencies:** Python package requirements

### Optional Fields

- **subtype:** More specific type (e.g., "tts", "upscaling")
- **description:** Engine description
- **author:** Engine author/creator
- **license:** License information
- **model_paths:** Model storage paths (uses `%PROGRAMDATA%`)
- **supported_languages:** List of language codes
- **capabilities:** List of engine capabilities
- **device_requirements:** GPU/VRAM/RAM requirements
- **config_schema:** Configuration options schema

---

## 🔧 Usage

### Loading Engines from Manifests

```python
from app.core.engines.router import router

# Load single engine from manifest
router.load_engine_from_manifest("engines/audio/xtts_v2/engine.manifest.json")

# Load all engines automatically
router.load_all_engines("engines")

# Get engine instance
engine = router.get_engine("xtts_v2", gpu=True)
```

### Accessing Manifest Data

```python
# Get manifest for an engine
manifest = router.get_manifest("xtts_v2")

# Access manifest fields
print(manifest["name"])
print(manifest["version"])
print(manifest["model_paths"])
```

### Auto-Loading on Startup

```python
# In app initialization
from app.core.engines.router import router

# Load all engines from manifests
router.load_all_engines()

# Now all engines are available
engines = router.list_engines()
```

---

## 📦 Model Storage

All models use `%PROGRAMDATA%\VoiceStudio\models\`:

```
%PROGRAMDATA%\VoiceStudio\models\
├── xtts_v2\          # XTTS models
├── piper\            # Piper voices
├── openvoice\        # OpenVoice checkpoints
├── sdxl\             # SDXL models
├── realesrgan\       # Real-ESRGAN models
└── svd\              # SVD models
```

**Benefits:**
- Models off C: drive
- Shared between installations
- Centralized management
- Environment variable expansion

---

## 🎯 Engine Types

### Audio Engines

- **TTS (Text-to-Speech):** XTTS v2, Piper, OpenVoice
- **VC (Voice Conversion):** RVC, So-VITS-SVC (to be added)
- **ASR (Automatic Speech Recognition):** Whisper (to be added)

### Image Engines

- **Generation:** SDXL ComfyUI
- **Upscaling:** Real-ESRGAN
- **Inpainting:** (to be added)

### Video Engines

- **Generation:** Stable Video Diffusion (SVD)
- **Enhancement:** (to be added)

---

## ➕ Adding New Engines

### Step 1: Create Manifest

Create `engines/{type}/{engine_id}/engine.manifest.json`:

```json
{
  "engine_id": "my_engine",
  "name": "My Engine",
  "type": "audio",
  "version": "1.0",
  "entry_point": "app.core.engines.my_engine.MyEngine",
  "dependencies": {
    "my-package": ">=1.0.0"
  }
}
```

### Step 2: Implement Engine Class

```python
# app/core/engines/my_engine.py
from .protocols import EngineProtocol

class MyEngine(EngineProtocol):
    def initialize(self) -> bool:
        # Initialize engine
        self._initialized = True
        return True
    
    def cleanup(self):
        # Cleanup resources
        self._initialized = False
```

### Step 3: Auto-Load

The engine will be automatically discovered and loaded when `router.load_all_engines()` is called.

---

## 🔍 Manifest Loader API

### `load_engine_manifest(manifest_path)`

Load and validate a manifest file.

```python
from app.core.engines.manifest_loader import load_engine_manifest

manifest = load_engine_manifest("engines/audio/xtts_v2/engine.manifest.json")
```

### `find_engine_manifests(engines_root)`

Find all manifest files in engines directory.

```python
from app.core.engines.manifest_loader import find_engine_manifests

manifests = find_engine_manifests("engines")
# Returns: {"xtts_v2": "engines/audio/xtts_v2/engine.manifest.json", ...}
```

### `validate_engine_requirements(manifest)`

Check if system meets engine requirements.

```python
from app.core.engines.manifest_loader import validate_engine_requirements

results = validate_engine_requirements(manifest)
# Returns: {"python_version": True, "dependencies": True, "device": True}
```

---

## 📚 Reference

- **Manifest Examples:** `engines/` directory
- **Manifest Loader:** `app/core/engines/manifest_loader.py`
- **Engine Router:** `app/core/engines/router.py`
- **Engine Protocol:** `app/core/engines/protocols.py`
- **Models Directory:** `models/README.md`

---

**The manifest system provides a clean, declarative way to manage engines without hardcoding registration logic.**

