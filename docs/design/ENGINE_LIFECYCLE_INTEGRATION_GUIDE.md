# Engine Lifecycle Integration Guide

**How to integrate the new lifecycle, port, and resource management systems with RuntimeEngine**

---

## Overview

The new engine lifecycle system provides:
- ✅ State machine (stopped → starting → healthy → busy → draining → stopped)
- ✅ Port management (automatic allocation, conflict prevention)
- ✅ Resource management (VRAM-aware scheduling)
- ✅ Hooks system (pre/post execution hooks)
- ✅ Security policies (file system and network access restrictions)
- ✅ Logging configuration (rotating logs, stderr/stdout redirection)

---

## Integration Options

### Option 1: Use Enhanced Runtime Engine (Recommended)

Use `EnhancedRuntimeEngine` which integrates all new features:

```python
from app.core.runtime.runtime_engine_enhanced import EnhancedRuntimeEngine, EnhancedRuntimeEngineManager

# Create manager
manager = EnhancedRuntimeEngineManager(workspace_root="E:\\VoiceStudio")

# Load engine from manifest (v1.1 format)
manager.load_engine("engines/audio/xtts_v2/engine.manifest.json")

# Start engine with job ID (for lease tracking)
manager.start_engine("xtts_v2", job_id="job_123")

# Get engine info
engine = manager.get_engine("xtts_v2")
info = engine.get_info()
# Returns: {
#   "id": "xtts_v2",
#   "state": "HEALTHY",
#   "port": 8200,
#   "pid": 12345,
#   "running": True,
#   "healthy": True
# }

# Stop engine
manager.stop_engine("xtts_v2", job_id="job_123")

# Panic switch: kill all engines
results = manager.stop_all(audit_log=True)
```

### Option 2: Use Managers Directly with RuntimeEngine

Keep using `RuntimeEngine` but add lifecycle management:

```python
from app.core.runtime.runtime_engine import RuntimeEngine, RuntimeEngineManager
from app.core.runtime.engine_lifecycle import get_lifecycle_manager
from app.core.runtime.port_manager import get_port_manager
from app.core.runtime.resource_manager import get_resource_manager

# Get managers
lifecycle = get_lifecycle_manager()
port_mgr = get_port_manager()
resource_mgr = get_resource_manager()

# Register engine with lifecycle manager
lifecycle.register_engine(
    engine_id="xtts_v2",
    manifest=manifest,
    is_singleton=True,
    idle_timeout_seconds=300
)

# Allocate port
port = port_mgr.allocate_port("xtts_v2", preferred_port=8200)

# Use existing RuntimeEngine
runtime_manager = RuntimeEngineManager()
runtime_manager.load_engine("engines/audio/xtts_v2/runtime.manifest.json")
runtime_manager.start_engine("xtts_v2")
```

---

## Manifest v1.1 Format

Update your engine manifests to v1.1 format:

```json
{
  "$schema": "app/schemas/engine.manifest.v1_1.json",
  "protocol": "v1.1",
  "engine_id": "xtts_v2",
  "name": "XTTS v2",
  "type": "audio",
  "subtype": "tts",
  "version": "2.0",
  
  "entry": {
    "kind": "python",
    "exe": "path/to/python.exe",
    "args": ["-m", "TTS.bin.tts_server", "--model_name", "xtts_v2"]
  },
  
  "lifecycle": {
    "pool_size": 1,
    "idle_timeout_seconds": 300,
    "startup_timeout_seconds": 30
  },
  
  "preHooks": ["ensure_models", "prepare_workspace"],
  "postHooks": ["collect_artifacts", "thumbnail"],
  
  "log": {
    "stderr_to_file": true,
    "stdout_to_file": false,
    "rotate_mb": 64,
    "log_dir": "runtime/logs"
  },
  
  "security": {
    "allow_net": false,
    "allow_fs_roots": ["%PROGRAMDATA%/VoiceStudio/models"],
    "allowed_hosts": ["127.0.0.1"],
    "allowed_ports": []
  },
  
  "health": {
    "kind": "http",
    "url": "http://127.0.0.1:{port}/health"
  },
  
  "tasks": ["tts", "clone_infer", "embed_voice"]
}
```

---

## Resource-Aware Job Submission

Submit jobs through the resource manager:

```python
from app.core.runtime.resource_manager import get_resource_manager, JobPriority, ResourceRequirement

resource_mgr = get_resource_manager()

# Submit job with VRAM requirements
resource_mgr.submit_job(
    job_id="job_123",
    engine_id="xtts_v2",
    task="tts",
    priority=JobPriority.INTERACTIVE,
    requirements=ResourceRequirement(
        vram_gb=4.0,
        duration_hint_seconds=30.0
    ),
    payload={"text": "Hello world", "speaker_wav": "path/to/speaker.wav"},
    callback=on_job_complete
)

# Get next job (automatically checks VRAM availability)
job = resource_mgr.get_next_job()

if job:
    # Start engine for job
    manager.start_engine(job.engine_id, job_id=job.job_id)
    
    # Execute job...
    
    # Complete job
    resource_mgr.complete_job(job.job_id, success=True)
```

---

## State Management

Monitor engine states:

```python
from app.core.runtime.engine_lifecycle import get_lifecycle_manager, EngineState

lifecycle = get_lifecycle_manager()

# Get all engine states
states = lifecycle.get_all_states()
# Returns: {
#   "xtts_v2": {
#     "state": "HEALTHY",
#     "port": 8200,
#     "job_lease": None,
#     "last_activity": "2025-01-27T12:00:00",
#     "health_check_failures": 0
#   }
# }

# Get specific engine state
state = lifecycle.get_engine_state("xtts_v2")
# Returns: EngineState.HEALTHY
```

---

## Port Management

Ports are automatically allocated and managed:

```python
from app.core.runtime.port_manager import get_port_manager

port_mgr = get_port_manager()

# Allocate port
port = port_mgr.allocate_port("xtts_v2", preferred_port=8200)
# Returns: 8200 (if available) or next available port

# Get allocated port
port = port_mgr.get_port("xtts_v2")
# Returns: 8200 or None if not allocated

# Release port
port_mgr.release_port("xtts_v2")

# List all active ports
active_ports = port_mgr.list_active_ports()
# Returns: {"xtts_v2": 8200, "comfyui": 8188}
```

---

## Hooks System

Hooks are executed automatically during engine lifecycle:

```python
from app.core.runtime.hooks import get_hook_registry

hook_registry = get_hook_registry()

# Register custom pre-hook
def my_pre_hook(context: Dict[str, Any]) -> bool:
    # Do something before engine starts
    logger.info(f"Pre-hook for {context['engine_id']}")
    return True

hook_registry.register_pre_hook("my_custom_hook", my_pre_hook)

# Register custom post-hook
def my_post_hook(context: Dict[str, Any]) -> bool:
    # Do something after engine stops
    logger.info(f"Post-hook for {context['engine_id']}")
    return True

hook_registry.register_post_hook("my_custom_hook", my_post_hook)

# Hooks are executed automatically when manifest includes them:
# "preHooks": ["ensure_models", "prepare_workspace", "my_custom_hook"]
```

---

## Security Policies

Security policies restrict file system and network access:

```python
from app.core.runtime.security import load_security_policy

# Load from manifest
security_policy = load_security_policy(manifest)

# Check file access
if security_policy.check_file_access("/path/to/file"):
    # Access allowed
    pass

# Check network access
if security_policy.check_network_access("127.0.0.1", 8200):
    # Network access allowed
    pass
```

---

## Panic Switch

Emergency shutdown of all engines:

```python
from app.core.runtime.engine_lifecycle import get_lifecycle_manager

lifecycle = get_lifecycle_manager()

# Kill all engines (panic switch)
results = lifecycle.kill_all(audit_log=True)
# Returns: {"xtts_v2": True, "comfyui": True, ...}

# Or use manager
manager.stop_all(audit_log=True)
```

---

## Migration Path

### Step 1: Update Manifests to v1.1

1. Add `"protocol": "v1.1"` to manifests
2. Add `lifecycle` configuration
3. Add `preHooks` and `postHooks` (optional)
4. Add `log` configuration (optional)
5. Add `security` policy (optional)

### Step 2: Use Enhanced Runtime Engine

Replace `RuntimeEngineManager` with `EnhancedRuntimeEngineManager`:

```python
# Old way
from app.core.runtime.runtime_engine import RuntimeEngineManager
manager = RuntimeEngineManager()

# New way
from app.core.runtime.runtime_engine_enhanced import EnhancedRuntimeEngineManager
manager = EnhancedRuntimeEngineManager()
```

### Step 3: Update Job Submission

Use resource manager for job submission:

```python
# Old way: direct engine start
manager.start_engine("xtts_v2")

# New way: resource-aware job submission
resource_mgr.submit_job(job_id="job_123", ...)
job = resource_mgr.get_next_job()
manager.start_engine(job.engine_id, job_id=job.job_id)
```

---

## Benefits

✅ **No port conflicts** - Automatic port allocation and conflict resolution  
✅ **VRAM-aware scheduling** - Jobs queued based on available VRAM  
✅ **Graceful shutdown** - Engines drain gracefully on idle timeout  
✅ **Security** - File system and network access restrictions  
✅ **Extensibility** - Pre/post hooks for custom logic  
✅ **Logging** - Automatic log rotation and file redirection  
✅ **State tracking** - Complete state machine with timestamps  
✅ **Panic switch** - Emergency shutdown of all engines  

---

## Next Steps

1. ✅ Update existing manifests to v1.1 format
2. ✅ Migrate to `EnhancedRuntimeEngineManager`
3. ✅ Integrate resource manager with job submission
4. ✅ Add security policies to manifests
5. ✅ Test lifecycle transitions
6. ✅ Test port allocation and conflict resolution
7. ✅ Test VRAM-aware scheduling
8. ✅ Test panic switch

---

**Status:** ✅ Implementation Complete — Ready for Integration

