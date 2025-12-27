# Legacy Engine Isolation Proposal
## Better Solution for Tortoise TTS and Other Legacy Engines

**Date:** 2025-01-28  
**Status:** Proposal  
**Priority:** HIGH - Tortoise TTS is one of the best voice cloning engines

---

## 🎯 PROBLEM

Current approach:
- Legacy engines (Tortoise TTS, MeloTTS, etc.) have dependency conflicts with modern stack
- Solution: Isolate in separate venvs (not user-friendly)
- Problem: Can't easily use Tortoise TTS, which is still considered one of the best voice cloning engines

---

## ✅ PROPOSED SOLUTION: Subprocess-Based Engine Isolation

### Concept

Instead of requiring separate virtual environments, use **subprocess isolation** where legacy engines run in separate Python processes with their own dependencies, communicating via JSON-RPC or similar protocol.

### Architecture

```
┌─────────────────────────────────────┐
│  Main VoiceStudio Process           │
│  (Modern Stack: PyTorch 2.9, etc.)  │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Engine Router                │ │
│  │  - Manages all engines        │ │
│  │  - Routes requests            │ │
│  └───────────┬───────────────────┘ │
│              │                      │
│              │ IPC (JSON-RPC)       │
│              ▼                      │
│  ┌───────────────────────────────┐ │
│  │  Legacy Engine Manager         │ │
│  │  - Spawns isolated processes   │ │
│  │  - Manages lifecycle           │ │
│  └───────────┬───────────────────┘ │
└──────────────┼──────────────────────┘
               │
               │ Subprocess
               ▼
┌─────────────────────────────────────┐
│  Isolated Tortoise TTS Process      │
│  (Legacy Stack: PyTorch 2.0, etc.)  │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Tortoise Engine Wrapper      │ │
│  │  - Loads Tortoise TTS         │ │
│  │  - Exposes EngineProtocol API │ │
│  │  - Communicates via JSON-RPC  │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTATION

### 1. Legacy Engine Wrapper

Create a wrapper that:
- Runs in isolated subprocess
- Loads legacy engine with its own dependencies
- Exposes EngineProtocol interface
- Communicates via JSON-RPC over stdin/stdout or named pipes

### 2. Legacy Engine Manager

Manager that:
- Spawns and manages isolated processes
- Handles process lifecycle (start, stop, restart)
- Manages communication (JSON-RPC client)
- Provides EngineProtocol-compatible interface to router

### 3. Configuration

Each legacy engine gets a config file:
```yaml
# engines/legacy/tortoise/config.yaml
name: tortoise-tts
python_path: python  # or specific venv path
working_directory: engines/legacy/tortoise
dependencies:
  - tortoise-tts>=2.4.0
  - torch==2.0.0
  - transformers==4.31.0
isolation_mode: subprocess
communication: jsonrpc
```

---

## 📝 IMPLEMENTATION STEPS

### Step 1: Create Legacy Engine Base Classes

**File:** `app/core/engines/legacy/base.py`

```python
"""
Base classes for legacy engine isolation
"""
import json
import subprocess
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..protocols import EngineProtocol

logger = logging.getLogger(__name__)


class LegacyEngineWrapper(EngineProtocol):
    """
    Wrapper for legacy engines running in isolated subprocesses.
    """
    
    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.process: Optional[subprocess.Popen] = None
        self._start_process()
    
    def _start_process(self):
        """Start isolated subprocess for legacy engine"""
        # Implementation here
        pass
    
    def synthesize(self, text: str, **kwargs) -> bytes:
        """Synthesize via JSON-RPC"""
        request = {
            "method": "synthesize",
            "params": {"text": text, **kwargs},
            "id": 1
        }
        response = self._call(request)
        return response["result"]
    
    def _call(self, request: Dict) -> Dict:
        """Make JSON-RPC call to subprocess"""
        # Implementation here
        pass
```

### Step 2: Create Tortoise TTS Isolated Process

**File:** `engines/legacy/tortoise/wrapper.py`

```python
"""
Tortoise TTS isolated process wrapper
Runs in separate process with legacy dependencies
"""
import json
import sys
from tortoise.api import TextToSpeech

def main():
    """Main entry point for isolated process"""
    tts = TextToSpeech()
    
    # Read JSON-RPC requests from stdin
    for line in sys.stdin:
        request = json.loads(line)
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "synthesize":
            result = tts.tts_with_preset(
                params["text"],
                voice_samples=params.get("voice_samples"),
                conditioning_latents=params.get("conditioning_latents"),
                preset=params.get("preset", "fast"),
            )
            response = {
                "jsonrpc": "2.0",
                "result": result.tolist(),  # Convert to list for JSON
                "id": request.get("id")
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": request.get("id")
            }
        
        # Write response to stdout
        print(json.dumps(response))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
```

### Step 3: Update Tortoise Engine to Use Isolation

**File:** `app/core/engines/tortoise_engine.py`

```python
"""
Tortoise TTS Engine - Uses subprocess isolation
"""
import logging
from pathlib import Path
from typing import Optional

from .legacy.base import LegacyEngineWrapper
from .protocols import EngineProtocol

logger = logging.getLogger(__name__)

class TortoiseEngine(LegacyEngineWrapper):
    """
    Tortoise TTS Engine using subprocess isolation.
    
    Runs in separate process with legacy dependencies to avoid conflicts.
    """
    
    def __init__(self, **kwargs):
        config_path = Path(__file__).parent.parent.parent / "engines" / "legacy" / "tortoise" / "config.yaml"
        super().__init__(config_path)
        logger.info("Tortoise TTS engine initialized (isolated subprocess)")
```

---

## 🎯 BENEFITS

### 1. **No Manual Venv Management**
- User doesn't need to create/manage separate venvs
- Automatic isolation handled by system

### 2. **Seamless Integration**
- Legacy engines work just like modern engines
- Same EngineProtocol interface
- Router doesn't need special handling

### 3. **Better Resource Management**
- Processes can be started/stopped on demand
- Memory isolation (can unload when not needed)
- Better error isolation (crash doesn't affect main process)

### 4. **Flexibility**
- Can use different Python versions per engine
- Can use different dependency sets
- Easy to add new legacy engines

### 5. **Performance**
- Processes run in parallel
- No GIL limitations
- Can utilize multiple CPU cores better

---

## 📋 ALTERNATIVE APPROACHES

### Option 1: Docker Containers (More Isolation)
- **Pros:** Complete isolation, can use different OS versions
- **Cons:** Requires Docker, more overhead, slower startup

### Option 2: HTTP API Wrapper (More Flexible)
- **Pros:** Can run on different machines, language-agnostic
- **Cons:** Network overhead, more complex setup

### Option 3: Current Proposal: Subprocess (Best Balance)
- **Pros:** Good isolation, fast, no external dependencies
- **Cons:** Still same OS, but sufficient for dependency conflicts

---

## 🚀 IMPLEMENTATION PRIORITY

### Phase 1: Proof of Concept (Tortoise TTS)
1. Create legacy engine base classes
2. Implement Tortoise TTS subprocess wrapper
3. Update Tortoise engine to use isolation
4. Test with real synthesis

### Phase 2: Generalize
1. Create configuration system for legacy engines
2. Create legacy engine manager
3. Add support for other legacy engines (MeloTTS, etc.)

### Phase 3: Integration
1. Update engine router to handle legacy engines
2. Add UI for managing legacy engines
3. Add monitoring and health checks

---

## 📝 CONFIGURATION EXAMPLE

**File:** `engines/legacy/tortoise/config.yaml`

```yaml
name: tortoise-tts
display_name: Tortoise TTS (Legacy)
version: 2.4.0
description: High-quality voice cloning engine (legacy dependencies)

isolation:
  mode: subprocess
  python_path: python  # or path to venv python
  working_directory: engines/legacy/tortoise
  environment:
    TORTOISE_CACHE_DIR: .cache/tortoise

dependencies:
  - tortoise-tts>=2.4.0
  - torch==2.0.0
  - transformers==4.31.0
  - numpy==1.22.0

communication:
  protocol: jsonrpc
  transport: stdio  # or named_pipe, unix_socket

capabilities:
  - text_to_speech
  - voice_cloning
  - multi_voice
  - high_quality

settings:
  default_preset: fast
  max_text_length: 400
  supported_formats: [wav, mp3]
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Tortoise TTS works without dependency conflicts
- [ ] No manual venv management required
- [ ] Same EngineProtocol interface as modern engines
- [ ] Process lifecycle managed automatically
- [ ] Error isolation (legacy engine crash doesn't affect main)
- [ ] Performance acceptable (<100ms overhead for subprocess)
- [ ] Easy to add new legacy engines

---

## 🎉 CONCLUSION

This approach provides:
- ✅ **Better UX:** No manual venv management
- ✅ **Better Integration:** Seamless with existing system
- ✅ **Better Isolation:** Process-level isolation
- ✅ **Better Performance:** Can run in parallel
- ✅ **Future-Proof:** Easy to extend to other legacy engines

**Tortoise TTS deserves better than being locked away in a separate venv!**

---

**Last Updated:** 2025-01-28

