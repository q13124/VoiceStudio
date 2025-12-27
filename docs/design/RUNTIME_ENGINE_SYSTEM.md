# Runtime Engine System
## Process-Based Engine Management

**Purpose:** Manage engines that run as separate processes/servers (e.g., TTS servers, API endpoints).

---

## 📋 Runtime Manifest Format

Runtime engines use `runtime.manifest.json` files:

```json
{
  "id": "xtts_v2",
  "type": "audio_tts",
  "displayName": "Coqui XTTS v2",
  "entry": {
    "kind": "python",
    "exe": "..\\..\\..\\.venv\\Scripts\\python.exe",
    "args": ["-m", "TTS.bin.tts_server", "--model_name", "tts_models/multilingual/multi-dataset/xtts_v2"]
  },
  "health": {
    "kind": "http",
    "url": "http://127.0.0.1:8021/health"
  },
  "tasks": ["tts", "clone_infer", "embed_voice"],
  "resources": {
    "needs": ["cuda_optional"],
    "vram_gb": 4
  }
}
```

### Manifest Fields

- **id:** Unique engine identifier
- **type:** Engine type (e.g., "audio_tts", "audio_vc", "image_gen")
- **displayName:** Human-readable name
- **entry:** How to start the engine
  - **kind:** Entry type ("python", "executable", etc.)
  - **exe:** Executable path (supports relative paths)
  - **args:** Command-line arguments
- **health:** Health check configuration
  - **kind:** Check type ("http", "tcp", etc.)
  - **url:** Health check endpoint
- **tasks:** List of tasks this engine can perform
- **resources:** Resource requirements
  - **needs:** Required resources (e.g., "cuda_optional", "cuda_required")
  - **vram_gb:** VRAM requirement in GB

---

## 🔧 Usage

### Loading and Starting Engines

```python
from app.core.runtime import RuntimeEngineManager

# Create manager
manager = RuntimeEngineManager(workspace_root="E:\\VoiceStudio")

# Load single engine
manager.load_engine("engines/audio/xtts_v2/runtime.manifest.json")

# Load all engines
manager.load_all_engines("engines")

# Start engine
manager.start_engine("xtts_v2")

# Check if running
engine = manager.get_engine("xtts_v2")
if engine.is_running() and engine.is_healthy():
    print("Engine is ready!")
```

### Task-Based Engine Selection

```python
# Get engine that supports a task
engine = manager.get_engine_for_task("tts")
if engine:
    engine.start()
    # Use engine...
```

### Health Monitoring

```python
engine = manager.get_engine("xtts_v2")

# Check if running
if engine.is_running():
    print("Engine process is running")

# Check health (via HTTP endpoint)
if engine.is_healthy():
    print("Engine is healthy and responding")
```

### Stopping Engines

```python
# Stop single engine
manager.stop_engine("xtts_v2")

# Stop all engines
manager.stop_all()
```

---

## 🏗️ Architecture

### Two Engine Types

VoiceStudio supports two engine types:

1. **Class-Based Engines** (`engine.manifest.json`)
   - Python classes inheriting from `EngineProtocol`
   - Loaded directly into the process
   - Fast, low-latency
   - Shared memory space

2. **Runtime Engines** (`runtime.manifest.json`)
   - Separate processes/servers
   - Isolated execution
   - HTTP/API communication
   - Resource isolation

### Engine Router Integration

The `EngineRouter` can work with both types:

```python
from app.core.engines.router import router
from app.core.runtime import RuntimeEngineManager

# Class-based engines
router.load_all_engines("engines")
class_engine = router.get_engine("xtts_v2")

# Runtime engines
runtime_manager = RuntimeEngineManager()
runtime_manager.load_all_engines("engines")
runtime_engine = runtime_manager.get_engine("xtts_v2")
```

---

## 📁 Directory Structure

Engines can have both manifest types:

```
engines/
├── audio/
│   └── xtts_v2/
│       ├── engine.manifest.json      # Class-based
│       └── runtime.manifest.json     # Process-based
```

**Use Cases:**
- **Class-based:** Direct integration, fast inference
- **Runtime:** Server mode, isolation, API access

---

## 🔍 Health Checks

### HTTP Health Check

```json
{
  "health": {
    "kind": "http",
    "url": "http://127.0.0.1:8021/health"
  }
}
```

The manager will:
1. Start the engine process
2. Wait for startup (2 seconds)
3. Poll the health endpoint
4. Report health status

### No Health Check

If no health check is defined, the manager assumes the engine is healthy if the process is running.

---

## 🎯 Task Routing

Engines declare supported tasks:

```json
{
  "tasks": ["tts", "clone_infer", "embed_voice"]
}
```

The manager can find engines by task:

```python
# Get engine for TTS task
engine = manager.get_engine_for_task("tts")
```

This enables:
- Automatic engine selection
- Task-based routing
- Fallback engines
- Load balancing (future)

---

## 📊 Resource Management

Manifests declare resource requirements:

```json
{
  "resources": {
    "needs": ["cuda_optional"],
    "vram_gb": 4
  }
}
```

**Resource Types:**
- `cuda_optional` - GPU preferred but not required
- `cuda_required` - GPU mandatory
- `vram_gb` - VRAM requirement in GB

**Future:** Resource validation before starting engines.

---

## 🔄 Lifecycle Management

### Starting

1. Load manifest
2. Resolve executable path (handles relative paths)
3. Start process with arguments
4. Wait for startup
5. Check health (if configured)
6. Report status

### Stopping

1. Send terminate signal
2. Wait for graceful shutdown (10 seconds)
3. Force kill if needed
4. Clean up resources

### Monitoring

- Process status (running/stopped)
- Health status (healthy/unhealthy)
- Task support
- Resource usage (future)

---

## 📚 Reference

- **Runtime Engine Manager:** `app/core/runtime/runtime_engine.py`
- **Engine Hook:** `app/core/runtime/engine_hook.py`
- **Class-Based Engines:** `docs/design/ENGINE_MANIFEST_SYSTEM.md`
- **Engine Router:** `app/core/engines/router.py`

---

**The runtime engine system provides process isolation and server-based engine management alongside class-based engines.**

