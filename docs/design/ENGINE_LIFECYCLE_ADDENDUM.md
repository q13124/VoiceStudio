# VoiceStudio — Engine Integration Addendum PLUS

**What to add on top of the current plan so Cursor ships a rock-solid, offline, modular studio that matches the dense UI you approved.**

---

## A) Engine Lifecycle & Scheduling (Governor-aware)

**Why:** Prevent port conflicts, crashes, and VRAM thrash when multiple engines run.

### Engine States

State machine: `stopped → starting → healthy → busy → draining → stopped` (timestamped)

- **stopped**: Engine is not running
- **starting**: Engine is starting up
- **healthy**: Engine is running and healthy (idle)
- **busy**: Engine is executing a job (has a lease)
- **draining**: Engine is gracefully shutting down
- **error**: Engine encountered an error

### Port Management

- **Port Registry**: Central registry at `runtime/ports.json` (reserve ranges: ComfyUI 8188, Local HTTP 82xx auto-allocation)
- **Conflict Prevention**: Automatic port conflict detection and resolution
- **Port Cleanup**: Automatic cleanup of stale ports (dead processes)

### Process Policy

- **Lifecycle**: `spawn → health check → job lease → idle timeout (T)` with **graceful drain** on switch
- **Job Leases**: Engines can be leased to jobs to prevent premature shutdown
- **Idle Timeout**: Engines auto-shutdown after idle period (configurable per engine)

### Engine Pooling

- **Fast Engines**: Small pool for fast engines (Piper, whisper.cpp) - multiple instances
- **Heavy Engines**: Singletons for heavy engines (XTTS, ComfyUI/SVD) - one instance

### CPU/GPU Watchdog

- **VRAM Monitoring**: Query VRAM/compute usage
- **Admission Control**: Refuse new jobs if **headroom < threshold**
- **Governor Integration**: Governor can reschedule jobs based on resource availability

### Panic Switch

- **Kill All**: One button kills all external processes (`EngineRunner.KillAll()`)
- **Audit Logging**: All panic actions logged to audit trail

---

## B) Resource Manager (VRAM-aware queue)

### Priority Queues

Three priority levels:
- **realtime**: Highest priority (immediate execution)
- **interactive**: Medium priority (user-initiated)
- **batch**: Lowest priority (background jobs)

### Admission Control

- **Job Declaration**: Job declares `needs.vram_gb` and `duration_hint`
- **Scheduler Decision**: Scheduler accepts or queues based on available resources
- **VRAM Headroom**: Safety headroom to prevent OOM errors

### Backoff & Circuit Breaker

- **Exponential Backoff**: On engine failure, exponential backoff before retry
- **Circuit Breaker**: After 5 failures, engine marked as `degraded` and suggests fallback

---

## C) Manifest Schema v1.1 (versioned + hooks)

### Enhanced Manifest Fields

Every `engine.manifest.json` can include:

```jsonc
{
  "$schema": "app/schemas/engine.manifest.v1_1.json",
  "protocol": "v1.1",
  
  // ... existing fields ...
  
  // Lifecycle configuration
  "lifecycle": {
    "pool_size": 3,  // Pool size for fast engines (1 = singleton)
    "idle_timeout_seconds": 300,  // Auto-shutdown after 5 min idle
    "startup_timeout_seconds": 30
  },
  
  // Pre/post hooks
  "preHooks": ["ensure_models", "prepare_workspace"],
  "postHooks": ["collect_artifacts", "thumbnail"],
  
  // Logging configuration
  "log": {
    "stderr_to_file": true,
    "stdout_to_file": false,
    "rotate_mb": 64,
    "log_dir": "runtime/logs"
  },
  
  // Security policy
  "security": {
    "allow_net": false,
    "allow_fs_roots": [
      "%PROGRAMDATA%/VoiceStudio/models",
      "%APPDATA%/VoiceStudio"
    ],
    "allowed_hosts": ["127.0.0.1", "localhost"],
    "allowed_ports": []
  },
  
  // Workspace configuration
  "workspace": {
    "directories": ["cache", "outputs", "temp"]
  }
}
```

### Built-in Hooks

**Pre-hooks:**
- `ensure_models`: Verify required models are downloaded
- `prepare_workspace`: Create required workspace directories

**Post-hooks:**
- `collect_artifacts`: Collect output artifacts
- `thumbnail`: Generate thumbnails for outputs

### Security Policies

- **Network Access**: `allow_net` controls network access (default: false)
- **File System**: `allow_fs_roots` restricts file system access to specific roots
- **Hosts/Ports**: Whitelist allowed hosts and ports (if network enabled)

---

## Implementation Status

### ✅ Completed

- [x] Port Manager (`app/core/runtime/port_manager.py`)
- [x] Resource Manager (`app/core/runtime/resource_manager.py`)
- [x] Engine Lifecycle Manager (`app/core/runtime/engine_lifecycle.py`)
- [x] Hooks System (`app/core/runtime/hooks.py`)
- [x] Security Policies (`app/core/runtime/security.py`)
- [x] Manifest Schema v1.1 (`app/schemas/engine.manifest.v1_1.json`)

### 🔄 Integration Needed

- [ ] Integrate lifecycle manager with RuntimeEngine
- [ ] Integrate resource manager with engine execution
- [ ] Integrate hooks into engine startup/shutdown
- [ ] Integrate security policies into file/network access
- [ ] Update existing manifests to v1.1 schema

---

## Usage Examples

### Engine Lifecycle

```python
from app.core.runtime.engine_lifecycle import get_lifecycle_manager

lifecycle = get_lifecycle_manager()

# Register engine
lifecycle.register_engine(
    engine_id="xtts_v2",
    manifest=manifest,
    is_singleton=True,  # Heavy engine = singleton
    idle_timeout_seconds=300
)

# Acquire engine for job
engine = lifecycle.acquire_engine(
    engine_id="xtts_v2",
    job_id="job_123",
    auto_start=True
)

# Execute job...

# Release engine
lifecycle.release_engine("xtts_v2", "job_123")

# Panic switch
results = lifecycle.kill_all(audit_log=True)
```

### Resource Management

```python
from app.core.runtime.resource_manager import get_resource_manager, JobPriority, ResourceRequirement

resource_mgr = get_resource_manager()

# Submit job
resource_mgr.submit_job(
    job_id="job_123",
    engine_id="xtts_v2",
    task="tts",
    priority=JobPriority.INTERACTIVE,
    requirements=ResourceRequirement(
        vram_gb=4.0,
        duration_hint_seconds=30.0
    ),
    payload={"text": "Hello world"},
    callback=on_job_complete
)

# Get next job
job = resource_mgr.get_next_job()

# Complete job
resource_mgr.complete_job("job_123", success=True)

# Check resource status
status = resource_mgr.get_resource_status()
```

### Port Management

```python
from app.core.runtime.port_manager import get_port_manager

port_mgr = get_port_manager()

# Allocate port
port = port_mgr.allocate_port("xtts_v2", preferred_port=8200, pid=12345)

# Get port
port = port_mgr.get_port("xtts_v2")

# Release port
port_mgr.release_port("xtts_v2")
```

---

## Related Documents

- **[RUNTIME_ENGINE_SYSTEM.md](RUNTIME_ENGINE_SYSTEM.md)** - Runtime engine system documentation
- **[ENGINE_MANIFEST_SYSTEM.md](ENGINE_MANIFEST_SYSTEM.md)** - Engine manifest system
- **[ENGINE_EXTENSIBILITY.md](ENGINE_EXTENSIBILITY.md)** - Engine extensibility guide

