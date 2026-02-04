# ADR-017: Engine Subprocess Model

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio integrates 44 AI engines (TTS, STT, voice conversion, image/video generation) with varying:
- VRAM requirements (0-12GB per engine)
- Python dependency conflicts (e.g., torch 2.2 vs 2.6)
- Stability characteristics (some engines crash on specific inputs)

A subprocess model is needed to:
1. Prevent VRAM conflicts between concurrent engines
2. Enable fault isolation (engine crash doesn't kill backend)
3. Support dependency isolation via venv families (TD-015)
4. Allow graceful degradation when engines fail

## Options Considered

### Option 1: In-Process Execution
All engines run in the backend FastAPI process.

**Pros:**
- Simple implementation
- Low latency (no IPC overhead)
- Easy debugging

**Cons:**
- Single VRAM pool causes OOM conflicts
- Engine crash kills entire backend
- Dependency conflicts impossible to resolve
- No fault isolation

### Option 2: Subprocess Per-Call
Spawn a new Python process for each engine operation.

**Pros:**
- Perfect isolation per call
- No shared state between calls
- Memory automatically reclaimed

**Cons:**
- High latency (process startup + model loading per call)
- Impractical for ML engines (10-30s model load time)
- Resource waste from repeated loading

### Option 3: Subprocess Pool (Selected)
Maintain persistent worker processes per engine or engine family.

**Pros:**
- Model loaded once per worker lifetime
- Fault isolation (worker crash is recoverable)
- VRAM isolation per worker
- Supports venv families for dependency isolation
- Worker restart on failure

**Cons:**
- More complex orchestration
- Need health monitoring
- Resource management complexity

## Decision

**Option 3: Subprocess Pool** with the following architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │             Engine Service Layer                 │    │
│  │  (routes → EngineService → EngineRouter)        │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                    HTTP/IPC                              │
│                          │                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Runtime Engine Manager                 │    │
│  │  - Worker pool management                        │    │
│  │  - VRAM budget enforcement (TD-013)             │    │
│  │  - Circuit breaker (TD-014)                     │    │
│  │  - Venv family selection (TD-015)               │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │ Worker 1  │   │ Worker 2  │   │ Worker N  │
    │ venv_core │   │ venv_adv  │   │ venv_stt  │
    │ XTTS,Piper│   │ Chatterbox│   │ Whisper   │
    └───────────┘   └───────────┘   └───────────┘
```

### Implementation Details

1. **Worker Pool**: `app/core/runtime/runtime_engine_enhanced.py`
   - Workers persist across calls
   - Lazy initialization (worker created on first call)
   - Idle timeout for resource reclamation (default: 300s)

2. **VRAM Management**: `app/core/runtime/resource_manager.py`
   - Per-engine VRAM budgets from manifests
   - Eviction policy for low-priority jobs
   - System memory pressure detection

3. **Fault Isolation**: `backend/services/circuit_breaker.py`
   - Circuit breaker per engine
   - Open after 3 consecutive failures
   - Auto-recovery after 30s cooldown

4. **Venv Families**: `app/core/runtime/venv_family_manager.py`
   - 3 families: core_tts, advanced_tts, stt
   - Engines mapped to families via manifests
   - Runtime selects appropriate venv

## Consequences

### Positive
- Engine crashes isolated to worker process
- VRAM conflicts eliminated via budget enforcement
- Dependency conflicts resolved via venv families
- Backend remains stable during engine failures
- Workers can be restarted without backend restart

### Negative
- Increased complexity in orchestration layer
- IPC overhead (~5-10ms per call)
- Memory overhead from multiple Python processes
- Debugging requires worker log aggregation

### Neutral
- Model loading time unchanged (still 10-30s per engine)
- Quality metrics unaffected
- API contracts unchanged

## References

- TD-013: VRAM Resource Scheduler (CLOSED)
- TD-014: Circuit Breaker Pattern (CLOSED)
- TD-015: Venv Families Strategy (CLOSED)
- `app/core/runtime/runtime_engine_enhanced.py`
- `app/core/engines/router.py`
