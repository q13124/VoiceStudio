# Engine Extensibility System
## Unlimited Engine Support - No Hardcoded Limits

**Last Updated:** 2025-01-27  
**Purpose:** Document the fully extensible engine system with no hardcoded limits

---

## 🎯 Core Principle

**VoiceStudio has NO hardcoded engine limits. Add as many engines as you need.**

The system is designed as a **plugin architecture** where:
- Engines are discovered automatically from manifest files
- No code changes needed to add new engines
- API dynamically lists available engines
- Unlimited extensibility

---

## 🏗️ Architecture

### Manifest-Based Discovery

Engines are discovered automatically by scanning for `engine.manifest.json` files:

```
engines/
├── audio/
│   ├── xtts_v2/
│   │   └── engine.manifest.json  ← Automatically discovered
│   ├── chatterbox/
│   │   └── engine.manifest.json  ← Automatically discovered
│   ├── tortoise/
│   │   └── engine.manifest.json  ← Automatically discovered
│   └── your_custom_engine/
│       └── engine.manifest.json  ← Automatically discovered
├── image/
│   └── your_image_engine/
│       └── engine.manifest.json  ← Automatically discovered
└── video/
    └── your_video_engine/
        └── engine.manifest.json  ← Automatically discovered
```

### Automatic Loading

The `EngineRouter` automatically:
1. Scans `engines/` directory recursively
2. Finds all `engine.manifest.json` files
3. Loads engine classes from entry points
4. Registers engines dynamically
5. Makes them available via API

**No manual registration required!**

---

## 📋 Adding a New Engine

### Step 1: Create Engine Directory

```
engines/audio/my_new_engine/
```

### Step 2: Create Engine Manifest

Create `engines/audio/my_new_engine/engine.manifest.json`:

```json
{
  "engine_id": "my_new_engine",
  "name": "My New Engine",
  "type": "audio",
  "subtype": "tts",
  "version": "1.0.0",
  "description": "My custom voice cloning engine",
  "entry_point": "app.core.engines.my_new_engine.MyNewEngine",
  "dependencies": {
    "my-package": ">=1.0.0"
  },
  "capabilities": [
    "voice_cloning",
    "text_to_speech"
  ],
  "device_requirements": {
    "gpu": "recommended",
    "vram_min_gb": 4
  }
}
```

### Step 3: Implement Engine Class

Create `app/core/engines/my_new_engine.py`:

```python
from .protocols import EngineProtocol
from typing import Optional, Union
from pathlib import Path
import numpy as np

class MyNewEngine(EngineProtocol):
    """My custom voice cloning engine."""
    
    def __init__(self, device=None, gpu=True):
        super().__init__(device=device, gpu=gpu)
        # Your initialization code
    
    def initialize(self) -> bool:
        # Load models, setup engine
        self._initialized = True
        return True
    
    def synthesize(self, text: str, speaker_wav: Union[str, Path], 
                   language: str = "en", output_path: Optional[Path] = None,
                   **kwargs) -> Optional[np.ndarray]:
        # Your synthesis logic
        pass
    
    def cleanup(self):
        # Clean up resources
        pass
```

### Step 4: That's It!

The engine is now:
- ✅ Automatically discovered
- ✅ Automatically loaded
- ✅ Available via API
- ✅ Listed in `router.list_engines()`
- ✅ Usable in all endpoints

**No code changes to router, API, or UI needed!**

---

## 🔧 API Integration

### Dynamic Engine Discovery

The API automatically discovers engines:

```python
# backend/api/routes/voice.py
if ENGINE_AVAILABLE and engine_router:
    # Dynamically get available engines (no hardcoded list)
    valid_engines = engine_router.list_engines()
    
    # Validate engine against discovered list
    if req.engine not in valid_engines:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid engine. Available: {', '.join(valid_engines)}"
        )
```

### Endpoint Usage

```python
# Use any discovered engine
POST /api/voice/synthesize
{
    "engine": "my_new_engine",  # Any engine from list_engines()
    "text": "Hello world",
    "profile_id": "profile_123"
}
```

---

## 📊 Engine Router API

### List All Engines

```python
from app.core.engines.router import router

# Auto-load all engines
router.load_all_engines("engines")

# List all available engines (dynamically discovered)
engines = router.list_engines()
# Returns: ['xtts_v2', 'chatterbox', 'tortoise', 'my_new_engine', ...]
```

### Get Engine Instance

```python
# Get any engine by ID
engine = router.get_engine("my_new_engine", gpu=True)

# Use engine
audio = engine.synthesize(
    text="Hello",
    speaker_wav="reference.wav",
    language="en"
)
```

### Get Engine Manifest

```python
# Get manifest for any engine
manifest = router.get_manifest("my_new_engine")
print(manifest["name"])  # "My New Engine"
print(manifest["capabilities"])  # ["voice_cloning", "text_to_speech"]
```

---

## 🚫 What NOT to Do

### ❌ Hardcoded Engine Lists

**DON'T:**
```python
# BAD - Hardcoded list
valid_engines = ["xtts", "chatterbox", "tortoise"]
```

**DO:**
```python
# GOOD - Dynamic discovery
valid_engines = router.list_engines()
```

### ❌ Manual Registration in Multiple Places

**DON'T:**
```python
# BAD - Manual registration in multiple files
router.register_engine("xtts", XTTSEngine)  # In voice.py
router.register_engine("xtts", XTTSEngine)  # In main.py
router.register_engine("xtts", XTTSEngine)  # In config.py
```

**DO:**
```python
# GOOD - Auto-load from manifests
router.load_all_engines("engines")  # Once, at startup
```

### ❌ Engine-Specific Code

**DON'T:**
```python
# BAD - Engine-specific logic
if engine == "xtts":
    # XTTS-specific code
elif engine == "chatterbox":
    # Chatterbox-specific code
```

**DO:**
```python
# GOOD - Protocol-based (works with any engine)
engine = router.get_engine(engine_id)
result = engine.synthesize(...)  # Works with any EngineProtocol implementation
```

---

## ✅ Best Practices

### 1. Use EngineProtocol Interface

All engines must implement `EngineProtocol`:
- Ensures consistent interface
- Works with any engine
- No engine-specific code needed

### 2. Complete Manifests

Always include complete manifest information:
- `engine_id` - Unique identifier
- `entry_point` - Python class path
- `capabilities` - What engine can do
- `dependencies` - Required packages

### 3. Error Handling

Handle missing engines gracefully:
```python
engine = router.get_engine("unknown_engine")
if engine is None:
    # Handle missing engine
    logger.warning("Engine not found")
```

### 4. Dynamic Discovery

Always use dynamic discovery:
```python
# At startup
router.load_all_engines("engines")

# When needed
available = router.list_engines()
```

---

## 🔍 Verification

### Check Engine Discovery

```python
from app.core.engines.router import router
from app.core.engines.manifest_loader import find_engine_manifests

# Find all manifests
manifests = find_engine_manifests("engines")
print(f"Found {len(manifests)} engine manifests")

# Load all engines
router.load_all_engines("engines")

# List loaded engines
engines = router.list_engines()
print(f"Loaded {len(engines)} engines: {engines}")
```

### Test New Engine

```python
# Load your new engine
router.load_engine_from_manifest("engines/audio/my_new_engine/engine.manifest.json")

# Verify it's loaded
assert "my_new_engine" in router.list_engines()

# Test it
engine = router.get_engine("my_new_engine")
assert engine is not None
assert engine.initialize()
```

---

## 📚 Examples

### Example: Adding RVC Engine

1. Create `engines/audio/rvc/engine.manifest.json`
2. Create `app/core/engines/rvc_engine.py` implementing `EngineProtocol`
3. Engine automatically available - no other changes needed!

### Example: Adding Whisper STT Engine

1. Create `engines/audio/whisper/engine.manifest.json`
2. Create `app/core/engines/whisper_engine.py` implementing `EngineProtocol`
3. Engine automatically available for transcription!

### Example: Adding Custom Image Engine

1. Create `engines/image/my_image_gen/engine.manifest.json`
2. Create `app/core/engines/my_image_gen_engine.py` implementing `EngineProtocol`
3. Engine automatically available for image generation!

---

## 🎯 Summary

**Key Points:**
- ✅ **No hardcoded limits** - Add unlimited engines
- ✅ **Automatic discovery** - Engines found from manifests
- ✅ **No code changes** - Just add manifest and class
- ✅ **Dynamic API** - Lists engines automatically
- ✅ **Plugin architecture** - Each engine independent
- ✅ **Protocol-based** - Consistent interface

**The system is designed for unlimited extensibility. Add as many engines as you need!**

---

**See Also:**
- `engines/README.md` - Engine registry documentation
- `app/core/engines/router.py` - Engine router implementation
- `app/core/engines/manifest_loader.py` - Manifest loading
- `app/core/engines/protocols.py` - EngineProtocol interface

