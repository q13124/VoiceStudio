# VoiceStudio Engine Plugin System

Complete guide to creating and integrating engines in VoiceStudio Quantum+.

## Table of Contents

1. [Overview](#overview)
2. [Engine Protocol Interface](#engine-protocol-interface)
3. [Manifest System](#manifest-system)
4. [Engine Lifecycle](#engine-lifecycle)
5. [Creating a New Engine](#creating-a-new-engine)
6. [Examples](#examples)
7. [Best Practices](#best-practices)

---

## Overview

VoiceStudio uses a **plugin architecture** for engines. Engines are discovered automatically from manifest files - no code changes needed to add new engines.

### Key Features

- **Automatic Discovery:** Engines found by scanning for `engine.manifest.json` files
- **No Hardcoded Limits:** Add as many engines as needed
- **Dynamic Loading:** Engines loaded on demand
- **Lifecycle Management:** Automatic initialization and cleanup
- **Resource Management:** VRAM-aware allocation

### Engine Types

- **Audio Engines:** TTS, voice cloning, voice conversion, STT
- **Image Engines:** Image generation, upscaling, inpainting
- **Video Engines:** Video generation, enhancement, processing

---

## Engine Protocol Interface

All engines must implement `EngineProtocol` from `app/core/engines/protocols.py`.

### Base Protocol

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class EngineProtocol(ABC):
    """Base protocol that all engines must implement."""
    
    def __init__(self, device: Optional[str] = None, gpu: bool = True):
        """
        Initialize engine with device selection.
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
        """
        self.device = device or ("cuda" if gpu else "cpu")
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the engine model.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        Clean up resources and free memory.
        """
        pass
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._initialized
    
    def get_device(self) -> str:
        """Get current device."""
        return self.device
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get engine information.
        
        Returns:
            Dictionary with engine metadata
        """
        return {
            "name": self.__class__.__name__,
            "device": self.device,
            "initialized": self._initialized
        }
```

### Required Methods

**1. `initialize()`**
- Load model files
- Setup device (GPU/CPU)
- Prepare for inference
- Return `True` on success, `False` on failure

**2. `cleanup()`**
- Free model memory
- Release GPU resources
- Close file handles
- Reset state

### Optional Methods

Engines can implement additional methods based on their type:

**For TTS/Voice Cloning Engines:**
```python
def synthesize(
    self,
    text: str,
    speaker_wav: Optional[str] = None,
    language: str = "en",
    output_path: Optional[str] = None,
    **kwargs
) -> Union[str, Tuple[str, Dict]]:
    """Synthesize audio from text."""
    pass
```

**For STT Engines:**
```python
def transcribe(
    self,
    audio: str,
    language: Optional[str] = None,
    word_timestamps: bool = False
) -> Dict[str, Any]:
    """Transcribe audio to text."""
    pass
```

---

## Manifest System

Engines are registered via `engine.manifest.json` files. No code changes needed!

### Manifest Location

```
engines/
├── audio/
│   ├── my_engine/
│   │   └── engine.manifest.json  ← Engine manifest
│   └── another_engine/
│       └── engine.manifest.json
├── image/
│   └── my_image_engine/
│       └── engine.manifest.json
└── video/
    └── my_video_engine/
        └── engine.manifest.json
```

### Manifest Schema

**Required Fields:**

```json
{
  "engine_id": "my_engine",
  "name": "My Engine",
  "type": "audio",
  "version": "1.0.0",
  "entry_point": "app.core.engines.my_engine.MyEngine"
}
```

**Complete Schema:**

```json
{
  "engine_id": "my_engine",
  "name": "My Engine",
  "type": "audio",
  "subtype": "tts",
  "version": "1.0.0",
  "description": "Description of the engine",
  "author": "Author Name",
  "license": "MIT",
  "python_version": ">=3.10",
  
  "entry_point": "app.core.engines.my_engine.MyEngine",
  
  "dependencies": {
    "torch": ">=2.0.0",
    "numpy": ">=1.24.0"
  },
  
  "model_paths": {
    "base": "%PROGRAMDATA%\\VoiceStudio\\models\\my_engine",
    "cache": "%PROGRAMDATA%\\VoiceStudio\\models\\my_engine\\cache"
  },
  
  "supported_languages": ["en", "es", "fr"],
  
  "capabilities": [
    "voice_cloning",
    "text_to_speech"
  ],
  
  "device_requirements": {
    "gpu": "recommended",
    "vram_min_gb": 4,
    "ram_min_gb": 8
  },
  
  "config_schema": {
    "model_name": {
      "type": "string",
      "default": "default_model",
      "description": "Model identifier"
    },
    "temperature": {
      "type": "number",
      "default": 0.7,
      "min": 0.0,
      "max": 1.0,
      "description": "Sampling temperature"
    }
  }
}
```

### Field Descriptions

**engine_id:** Unique identifier (lowercase, underscores)
- Example: `"xtts_v2"`, `"my_custom_engine"`

**name:** Human-readable name
- Example: `"XTTS v2"`, `"My Custom Engine"`

**type:** Engine type
- Values: `"audio"`, `"image"`, `"video"`

**subtype:** More specific type (optional)
- For audio: `"tts"`, `"vc"`, `"stt"`
- For image: `"generation"`, `"upscaling"`
- For video: `"generation"`, `"enhancement"`

**version:** Engine version (semantic versioning)
- Example: `"1.0.0"`, `"2.1.3"`

**entry_point:** Python class path
- Format: `"app.core.engines.{module}.{ClassName}"`
- Example: `"app.core.engines.xtts_engine.XTTSEngine"`

**dependencies:** Python package requirements
- Dictionary of package names and version constraints
- Example: `{"torch": ">=2.0.0", "numpy": ">=1.24.0"}`

**model_paths:** Model storage paths
- Uses `%PROGRAMDATA%` for system-wide storage
- Example: `{"base": "%PROGRAMDATA%\\VoiceStudio\\models\\my_engine"}`

**supported_languages:** List of language codes (ISO 639-1)
- Example: `["en", "es", "fr", "de"]`

**capabilities:** List of engine capabilities
- Example: `["voice_cloning", "text_to_speech", "emotion_control"]`

**device_requirements:** Hardware requirements
- `gpu`: `"required"`, `"recommended"`, `"optional"`
- `vram_min_gb`: Minimum VRAM in GB
- `ram_min_gb`: Minimum RAM in GB

**config_schema:** Configuration options schema
- Defines engine-specific configuration options
- Used for validation and UI generation

---

## Engine Lifecycle

### 1. Discovery

**Automatic Discovery:**
```python
from app.core.engines.router import router

# Scan engines/ directory for manifests
router.load_all_engines("engines")
```

**Manual Loading:**
```python
# Load single engine from manifest
router.load_engine_from_manifest("engines/audio/my_engine/engine.manifest.json")
```

### 2. Registration

Engine class loaded from entry point and registered in router:

```python
# Engine class loaded dynamically
engine_class = importlib.import_module("app.core.engines.my_engine").MyEngine

# Registered in router
router.register_engine("my_engine", engine_class)
```

### 3. Initialization

Engine initialized on first use:

```python
# Get engine instance (creates if not exists)
engine = router.get_engine("my_engine", gpu=True)

# Engine.initialize() called automatically
# Model loaded, device setup, ready for use
```

### 4. Execution

Engine methods called:

```python
# Use engine
result = engine.synthesize(
    text="Hello, world!",
    speaker_wav="reference.wav",
    language="en"
)
```

### 5. Cleanup

Engine cleaned up when done:

```python
# Manual cleanup
engine.cleanup()

# Or automatic cleanup via router
router.unregister_engine("my_engine")
```

---

## Creating a New Engine

### Step 1: Create Engine Directory

```
engines/audio/my_engine/
```

### Step 2: Create Engine Manifest

Create `engines/audio/my_engine/engine.manifest.json`:

```json
{
  "engine_id": "my_engine",
  "name": "My Engine",
  "type": "audio",
  "subtype": "tts",
  "version": "1.0.0",
  "description": "My custom voice cloning engine",
  "author": "Your Name",
  "license": "MIT",
  "entry_point": "app.core.engines.my_engine.MyEngine",
  "dependencies": {
    "my-package": ">=1.0.0"
  },
  "supported_languages": ["en"],
  "capabilities": [
    "voice_cloning",
    "text_to_speech"
  ],
  "device_requirements": {
    "gpu": "recommended",
    "vram_min_gb": 2
  }
}
```

### Step 3: Implement Engine Class

Create `app/core/engines/my_engine.py`:

```python
"""
My Engine for VoiceStudio
Custom voice cloning engine implementation
"""

import os
import logging
from typing import Optional, Union, Tuple, Dict
from pathlib import Path

from .protocols import EngineProtocol

logger = logging.getLogger(__name__)


class MyEngine(EngineProtocol):
    """
    My custom voice cloning engine.
    
    Supports voice cloning and text-to-speech synthesis.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        gpu: bool = True
    ):
        """
        Initialize My Engine.
        
        Args:
            model_path: Path to model files
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
        """
        super().__init__(device=device, gpu=gpu)
        self.model_path = model_path
        self.model = None
    
    def initialize(self) -> bool:
        """
        Initialize the engine model.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info(f"Initializing MyEngine on device: {self.device}")
            
            # Load model
            if self.model_path and os.path.exists(self.model_path):
                # Load your model here
                # self.model = load_model(self.model_path)
                logger.info("Model loaded successfully")
            else:
                logger.warning("Model path not found, using default model")
                # Load default model
                # self.model = load_default_model()
            
            self._initialized = True
            logger.info("MyEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MyEngine: {e}", exc_info=True)
            self._initialized = False
            return False
    
    def cleanup(self):
        """Clean up resources and free memory."""
        try:
            logger.info("Cleaning up MyEngine")
            
            # Free model memory
            if self.model is not None:
                # del self.model
                # torch.cuda.empty_cache() if using GPU
                self.model = None
            
            self._initialized = False
            logger.info("MyEngine cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    def synthesize(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        language: str = "en",
        output_path: Optional[str] = None,
        **kwargs
    ) -> Union[str, Tuple[str, Dict]]:
        """
        Synthesize audio from text.
        
        Args:
            text: Text to synthesize
            speaker_wav: Path to reference audio file
            language: Language code
            output_path: Output audio file path
            **kwargs: Additional engine-specific parameters
        
        Returns:
            Output audio file path, or tuple of (path, quality_metrics)
        """
        if not self._initialized:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        try:
            logger.info(f"Synthesizing text: {text[:50]}...")
            
            # Generate output path if not provided
            if output_path is None:
                import tempfile
                output_path = tempfile.mktemp(suffix='.wav')
            
            # Your synthesis logic here
            # audio = self.model.synthesize(text, speaker_wav, language)
            # save_audio(audio, output_path)
            
            # Calculate quality metrics if requested
            calculate_quality = kwargs.get("calculate_quality", False)
            if calculate_quality:
                # quality_metrics = calculate_all_metrics(output_path, speaker_wav)
                # return output_path, quality_metrics
                pass
            
            logger.info(f"Synthesis complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}", exc_info=True)
            raise
    
    def get_info(self) -> Dict:
        """Get engine information."""
        info = super().get_info()
        info.update({
            "model_path": self.model_path,
            "model_loaded": self.model is not None
        })
        return info
```

### Step 4: Test Engine

**Manual Test:**
```python
from app.core.engines.router import router

# Load engine
router.load_engine_from_manifest("engines/audio/my_engine/engine.manifest.json")

# Get engine instance
engine = router.get_engine("my_engine", gpu=True)

# Test synthesis
result = engine.synthesize(
    text="Hello, world!",
    speaker_wav="reference.wav",
    language="en"
)
print(f"Generated audio: {result}")
```

### Step 5: Verify Auto-Discovery

Restart backend and verify engine is discovered:

```python
# In backend startup
from app.core.engines.router import router

router.load_all_engines("engines")
engines = router.list_engines()
print(engines)  # Should include "my_engine"
```

---

## Examples

### Example 1: Simple TTS Engine

```python
class SimpleTTSEngine(EngineProtocol):
    """Simple text-to-speech engine."""
    
    def __init__(self, device=None, gpu=True):
        super().__init__(device=device, gpu=gpu)
        self.tts_model = None
    
    def initialize(self) -> bool:
        """Initialize TTS model."""
        try:
            # Load TTS model
            # self.tts_model = load_tts_model()
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if self.tts_model:
            del self.tts_model
        self._initialized = False
    
    def synthesize(self, text: str, **kwargs) -> str:
        """Synthesize speech from text."""
        if not self._initialized:
            raise RuntimeError("Engine not initialized")
        
        # Generate audio
        audio = self.tts_model.synthesize(text)
        
        # Save to file
        output_path = kwargs.get("output_path") or tempfile.mktemp(suffix='.wav')
        save_audio(audio, output_path)
        
        return output_path
```

### Example 2: STT Engine

```python
class MySTTEngine(EngineProtocol):
    """Speech-to-text engine."""
    
    def initialize(self) -> bool:
        """Initialize STT model."""
        # Load STT model
        self._initialized = True
        return True
    
    def cleanup(self):
        """Clean up resources."""
        self._initialized = False
    
    def transcribe(
        self,
        audio: str,
        language: Optional[str] = None,
        word_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Returns:
            Dictionary with:
            - text: Full transcript
            - segments: List of segments with timestamps
            - word_timestamps: Word-level timestamps (if requested)
            - language: Detected language
        """
        if not self._initialized:
            raise RuntimeError("Engine not initialized")
        
        # Transcribe audio
        result = self.stt_model.transcribe(
            audio,
            language=language,
            word_timestamps=word_timestamps
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "word_timestamps": result.get("word_timestamps", []),
            "language": result.get("language", "en")
        }
```

### Example 3: Image Generation Engine

```python
class MyImageEngine(EngineProtocol):
    """Image generation engine."""
    
    def initialize(self) -> bool:
        """Initialize image generation model."""
        # Load image generation model
        self._initialized = True
        return True
    
    def cleanup(self):
        """Clean up resources."""
        self._initialized = False
    
    def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        **kwargs
    ) -> str:
        """
        Generate image from text prompt.
        
        Returns:
            Path to generated image file
        """
        if not self._initialized:
            raise RuntimeError("Engine not initialized")
        
        # Generate image
        image = self.model.generate(prompt, width, height)
        
        # Save image
        output_path = kwargs.get("output_path") or tempfile.mktemp(suffix='.png')
        save_image(image, output_path)
        
        return output_path
```

---

## Best Practices

### 1. Error Handling

**Always handle errors gracefully:**
```python
def synthesize(self, text: str, **kwargs) -> str:
    try:
        # Synthesis logic
        return output_path
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise RuntimeError("Model files missing") from e
    except Exception as e:
        logger.error(f"Synthesis failed: {e}", exc_info=True)
        raise
```

### 2. Resource Management

**Clean up resources properly:**
```python
def cleanup(self):
    try:
        # Free GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Close file handles
        if self.model_file:
            self.model_file.close()
        
        # Delete model
        del self.model
        self.model = None
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    finally:
        self._initialized = False
```

### 3. Logging

**Use appropriate log levels:**
```python
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### 4. Type Hints

**Add type hints for better documentation:**
```python
from typing import Optional, Union, Tuple, Dict, List

def synthesize(
    self,
    text: str,
    speaker_wav: Optional[str] = None,
    language: str = "en",
    output_path: Optional[str] = None
) -> Union[str, Tuple[str, Dict[str, float]]]:
    """Synthesize audio from text."""
    pass
```

### 5. Configuration

**Use manifest config_schema for configuration:**
```json
{
  "config_schema": {
    "model_name": {
      "type": "string",
      "default": "default_model",
      "description": "Model to use"
    },
    "temperature": {
      "type": "number",
      "default": 0.7,
      "min": 0.0,
      "max": 1.0
    }
  }
}
```

### 6. Quality Metrics

**Support quality metrics if applicable:**
```python
def synthesize(self, text: str, calculate_quality: bool = False, **kwargs):
    """Synthesize with optional quality metrics."""
    output_path = self._synthesize(text, **kwargs)
    
    if calculate_quality:
        from .quality_metrics import calculate_all_metrics
        metrics = calculate_all_metrics(output_path, reference_audio)
        return output_path, metrics
    
    return output_path
```

### 7. Device Management

**Handle GPU/CPU gracefully:**
```python
def __init__(self, device=None, gpu=True):
    super().__init__(device=device, gpu=gpu)
    
    # Check GPU availability
    if gpu and not torch.cuda.is_available():
        logger.warning("GPU requested but not available, using CPU")
        self.device = "cpu"
```

---

## Testing Your Engine

### Unit Tests

```python
import pytest
from app.core.engines.my_engine import MyEngine

def test_engine_initialization():
    """Test engine initialization."""
    engine = MyEngine(device="cpu")
    assert engine.initialize() == True
    assert engine.is_initialized() == True
    engine.cleanup()

def test_engine_synthesis():
    """Test engine synthesis."""
    engine = MyEngine(device="cpu")
    engine.initialize()
    
    result = engine.synthesize("Hello, world!", language="en")
    assert os.path.exists(result)
    
    engine.cleanup()
```

### Integration Tests

```python
def test_engine_via_router():
    """Test engine via router."""
    from app.core.engines.router import router
    
    router.load_engine_from_manifest("engines/audio/my_engine/engine.manifest.json")
    
    engine = router.get_engine("my_engine", gpu=False)
    assert engine is not None
    assert engine.is_initialized()
    
    result = engine.synthesize("Test")
    assert result is not None
```

---

## Troubleshooting

### Engine Not Discovered

**Check:**
1. Manifest file exists: `engines/audio/my_engine/engine.manifest.json`
2. Manifest JSON is valid
3. Entry point path is correct
4. Engine class exists and is importable

### Engine Fails to Initialize

**Check:**
1. Dependencies installed: `pip install -r requirements.txt`
2. Model files exist at specified paths
3. Device availability (GPU/CPU)
4. Logs for error messages

### Engine Not Available in API

**Check:**
1. Backend restarted after adding engine
2. Engine loaded: `router.list_engines()`
3. Engine registered correctly
4. No import errors in logs

---

## References

- [Engine Manifest System](../design/ENGINE_MANIFEST_SYSTEM.md)
- [Engine Extensibility](../design/ENGINE_EXTENSIBILITY.md)
- [Architecture Documentation](ARCHITECTURE.md)

---

**Last Updated:** 2025-01-27  
**Version:** 1.0

