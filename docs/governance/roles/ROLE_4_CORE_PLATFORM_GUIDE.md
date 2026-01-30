# Role 4: Core Platform Engineer Guide

> **Version**: 1.1.0  
> **Last Updated**: 2026-01-25  
> **Role Number**: 4  
> **Parent Document**: [ROLE_GUIDES_INDEX.md](../ROLE_GUIDES_INDEX.md)

---

## 1. Role Identity

### Role Name
**Core Platform Engineer** (Orchestration + Storage + Runtime)

### Mission Statement
Stabilize local-first orchestration including jobs, storage, artifacts, and preflight systems, ensuring data durability and runtime reliability across restarts.

### Primary Responsibilities

1. **Job Runtime**: Implement and maintain job execution, cancellation, and state management
2. **Storage Durability**: Ensure data persists correctly across application restarts
3. **Artifact Registry**: Manage audio and model artifact storage and retrieval
4. **Preflight Systems**: Implement health checks and readiness probes
5. **Plugin Host**: Manage plugin loading and lifecycle
6. **Domain Models**: Define and maintain core domain entities
7. **Service Layer**: Implement backend service orchestration

### Non-Negotiables

- **Deterministic evidence**: All changes must have proof runs
- **Fully implemented surfaces**: No placeholder implementations
- **Crash-safe writes**: All storage operations must be atomic
- **Local-first**: Core functionality must work offline
- **Restart resilience**: State must survive application restart

### Success Metrics

- Storage + runtime tests green
- Persistence across restart verified
- Preflight endpoints operational
- Plugin host loads sample plugins
- Job cancellation works reliably

---

## 2. Scope and Boundaries

### What This Role Owns

- `backend/services/` — Backend service implementations
- `backend/api/routes/health.py` — Health and preflight endpoints
- `backend/api/routes/voice_cloning_wizard.py` — Wizard job management
- `app/core/runtime/` — Runtime orchestration
- `app/core/storage/` — Storage implementations
- `app/core/plugins/` — Plugin host
- Job state management (`JobStateStore`)
- Audio artifact registry (`AudioArtifactRegistry`)
- Project store and migrations

### What This Role May Change

- `core/runtime/*` — Runtime and orchestration
- `core/storage/*` — Storage implementations
- `core/plugins/*` — Plugin host
- Serialization and migrations
- Backend service implementations
- Health and preflight endpoints

### What This Role Must NOT Change Without Coordination

- UI design rules (requires UI Engineer)
- Engine model code (requires Engine Engineer)
- Architectural interfaces (requires System Architect)
- Build configurations (requires Build & Tooling)

### Escalation Triggers

**Escalate to Overseer (Role 0)** when:
- S0 blocker affecting platform stability
- Storage schema change affects multiple consumers
- Runtime change affects engine isolation
- Gate D or E regression
- Critical preflight failure

**Use Debug Agent (Role 7)** when:
- Job state persistence inconsistent (race condition?)
- Backend API returns unexpected errors
- Preflight checks pass but engine fails
- Context manager or storage issue unclear
- Async/concurrency bugs suspected

See [Cross-Role Escalation Matrix](../../CROSS_ROLE_ESCALATION_MATRIX.md) for decision tree.

### Cross-Role Handoff Requirements

The Core Platform Engineer:
- Provides service contracts to UI Engineer
- Implements engine lifecycle hooks for Engine Engineer
- Reports storage/runtime status to Overseer
- Coordinates schema changes with System Architect

---

## 3. Phase-Gate Responsibility Matrix

| Gate | Entry Criteria | Platform Tasks | Deliverables | Exit Criteria | Proof Requirements |
|------|----------------|----------------|--------------|---------------|-------------------|
| **A** | Repository accessible | (Supporting role) | - | - | - |
| **B** | Gate A complete | (Supporting role) | - | - | - |
| **C** | Gate B complete | Fix boot issues, service provider setup, crash capture | Boot proof, crash artifacts | App launches without runtime exceptions | Startup log |
| **D** | Gate C complete | Implement persistence, preflight, job state, artifact registry | Persistence tests, preflight proof | Data survives restart | Test execution + restart proof |
| **E** | Gate D complete | Engine lifecycle hooks, adapter interfaces | Engine interface tests | Engine start/stop works | Engine smoke tests |
| **F** | Gate E complete | (Supporting role) | - | - | - |
| **G** | All prior gates | Storage/runtime QA | Platform QA report | All platform tests pass | Test execution logs |
| **H** | Gate G complete | (Supporting role) | - | - | - |

---

## 4. Operational Workflows

### Job Runtime Patterns

The job system manages long-running operations:

```python
# Job lifecycle
job_id = await job_store.create_job(job_type, payload)
await job_store.update_status(job_id, "processing")
try:
    result = await execute_job(payload)
    await job_store.update_status(job_id, "completed", result=result)
except Exception as e:
    await job_store.update_status(job_id, "failed", error=str(e))
```

**Key Patterns**:
- Jobs persist to disk via `JobStateStore`
- In-flight jobs marked "failed" on restart
- Cancellation token checked periodically
- Progress updates via WebSocket

### Storage Durability Requirements

All persistent data must:
1. **Be atomic**: Use write-rename pattern
2. **Be versioned**: Include schema version
3. **Be idempotent**: Migrations can run multiple times safely
4. **Be recoverable**: Failed writes don't corrupt state

```python
# Write-rename pattern
temp_path = f"{target_path}.tmp"
with open(temp_path, 'w') as f:
    json.dump(data, f)
os.replace(temp_path, target_path)  # Atomic on POSIX/Windows
```

### Preflight Protocol

The `/api/health/preflight` endpoint validates readiness:

```json
{
  "projects_root": {"exists": true, "path": "..."},
  "cache_root": {"exists": true, "path": "..."},
  "model_root": {"exists": true, "path": "..."},
  "audio_registry": {"exists": true, "path": "..."},
  "ffmpeg": {"found": true, "path": "..."}
}
```

**Implementation Checklist**:
- [ ] Projects root accessible
- [ ] Cache root accessible
- [ ] Model root (VOICESTUDIO_MODELS_PATH) accessible
- [ ] Audio registry directory exists
- [ ] FFmpeg discoverable

### State Persistence Verification

To verify persistence across restart:

```powershell
# 1. Create some state
Invoke-RestMethod -Uri "http://localhost:8000/api/voice/clone" -Method POST -Body $payload

# 2. Restart backend
Stop-Process -Name python -Force
.\scripts\backend\start_backend.ps1

# 3. Verify state persisted
$job = Invoke-RestMethod -Uri "http://localhost:8000/api/jobs/$jobId"
$job.status  # Should show previous state
```

### Daily Cadence

1. **Test Execution**: Run storage and runtime tests
2. **Preflight Check**: Verify health endpoints
3. **Migration Review**: Check for pending schema changes
4. **Plugin Status**: Verify plugin host health

---

## 5. Quality Standards and Definition of Done

### Role-Specific DoD

A task is complete when:
- Storage + runtime tests green
- Crash-safe writes verified
- Plugin host loads sample plugins (if applicable)
- Preflight endpoints operational
- Persistence across restart proven

### Verification Methods

1. **Storage Tests**
   ```powershell
   python -m pytest tests/unit/backend/services/test_job_state_store.py -v
   python -m pytest tests/unit/backend/services/test_audio_artifact_registry.py -v
   ```

2. **Health Endpoint Tests**
   ```powershell
   python -m pytest tests/unit/backend/api/routes/test_health.py -v
   ```

3. **Preflight Verification**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8000/api/health/preflight" | ConvertTo-Json
   ```

4. **Restart Persistence Test**
   ```powershell
   # Create state, restart, verify state persists
   ```

### Storage Review Checklist

When reviewing storage changes:

- [ ] Atomic write pattern used
- [ ] Schema version included
- [ ] Migration path provided (if schema change)
- [ ] Error handling covers disk failures
- [ ] Tests verify persistence
- [ ] Restart resilience tested

### Common Failure Modes

| Failure Mode | Prevention |
|--------------|------------|
| Data loss on crash | Use write-rename pattern |
| Corrupt state on restart | Validate on load, use defaults |
| Orphaned temp files | Cleanup on startup |
| Race conditions | Use file locks or atomic ops |
| Memory leaks in services | Proper disposal patterns |

---

## 6. Tooling and Resources

### Required Tools

- Python 3.11.x with pytest
- FastAPI and Uvicorn
- SQLite for local storage
- File system access for artifact storage

### Key Documentation References

| Document | Purpose |
|----------|---------|
| `backend/services/` | Service implementations |
| `backend/api/routes/health.py` | Health endpoints |
| `backend/services/JobStateStore.py` | Job persistence |
| `backend/services/AudioArtifactRegistry.py` | Audio storage |
| `app/core/runtime/` | Runtime orchestration |
| `.cursor/rules/languages/python-backend.mdc` | Python backend rules |

### Useful Scripts

```powershell
# Run all backend tests
python -m pytest tests/unit/backend/ -v

# Run storage tests specifically
python -m pytest tests/unit/backend/services/test_job_state_store.py -v

# Check health endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/health/preflight

# Start backend
.\scripts\backend\start_backend.ps1 -CoquiTosAgreed
```

### MCP Servers Relevant to Role

- `sqlite` - Local database operations
- `fastapi-mcp` - FastAPI integration
- `sequential-thinking` - Complex problem solving

### IDE Configuration

- Enable Python type checking
- Configure pytest integration
- Set up debugger for backend

---

## 7. Common Scenarios and Decision Trees

### Scenario 1: Implementing Durable Storage

**Context**: New data needs to persist across restarts.

**Decision Tree**:
```
New persistent data needed
  ↓
Identify storage location:
  ├─ User data → projects_root
  ├─ Cache/temp → cache_root
  ├─ Models → model_root
  └─ Audio → audio_registry
  ↓
Define schema with version
  ↓
Implement storage class:
  - Atomic writes (write-rename)
  - Load with validation
  - Migration support
  ↓
Add tests:
  - Create/Read/Update/Delete
  - Restart persistence
  - Corruption recovery
  ↓
Document in API if exposed
```

**Worked Example (VS-0021)**:
- Issue: Persist voice cloning wizard job state across restart
- Implementation: Created `JobStateStore` with disk-backed persistence
- Storage: `VOICESTUDIO_CACHE_DIR/jobs/`
- Proof: `pytest tests/unit/backend/services/test_job_state_store.py` passes

### Scenario 2: ServiceProvider/Boot Issue

**Context**: App crashes on startup with service error.

**Decision Tree**:
```
Boot crash detected
  ↓
Check crash logs (%LOCALAPPDATA%\VoiceStudio\crashes\)
  ↓
Error type:
  ├─ Recursion → Check service registration order
  ├─ Missing dependency → Add service registration
  ├─ Circular dependency → Refactor service graph
  └─ Null reference → Add null checks
  ↓
Fix service registration
  ↓
Verify boot succeeds
  ↓
Add regression test
```

**Worked Example (VS-0011)**:
- Issue: ServiceProvider recursion fix
- Root cause: Circular dependency in service registration
- Fix: Reorder service registration, break cycle
- Proof: App boots without runtime exceptions

### Scenario 3: Implementing Preflight Check

**Context**: New readiness condition needed.

**Decision Tree**:
```
New readiness condition identified
  ↓
Is it blocking for operation?
  ├─ Yes → Add to required checks
  └─ No → Add to advisory checks
  ↓
Implement check:
  - Fast execution (no heavy IO)
  - Clear error message
  - Deterministic result
  ↓
Add to /api/health/preflight response
  ↓
Add tests
  ↓
Document in API
```

**Worked Example (VS-0019)**:
- Issue: Backend preflight readiness report
- Implementation: Added `/api/health/preflight` endpoint
- Checks: projects_root, cache_root, model_root, audio_registry, ffmpeg
- Proof: `pytest tests/unit/backend/api/routes/test_health.py` — 16 passed

### Scenario 4: Audio Artifact Registry

**Context**: Audio needs to be stored and retrieved.

**Worked Example (VS-0020)**:
- Issue: Durable audio artifact registry (audio_id -> file_path)
- Implementation: Disk-backed registry with content-addressed cache
- Integration: Voice and RVC routes register outputs
- Proof: `pytest tests/unit/backend/services/test_audio_artifact_registry.py` passes

### Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| In-memory only state | Lost on restart | Persist to disk |
| Non-atomic writes | Corruption risk | Write-rename pattern |
| Blocking health checks | Slow startup | Fast, async checks |
| Hardcoded paths | Not portable | Use env vars, config |
| Silent failures | Hidden bugs | Log and surface errors |

---

## 8. Cross-Role Coordination

### Dependencies on Other Roles

| Role | Dependency Type | Coordination Pattern |
|------|-----------------|---------------------|
| Overseer | Gate validation, evidence collection | Report platform status |
| System Architect | Service contracts, schema approval | Coordinate interface changes |
| Build & Tooling | Backend build integration | Ensure Python builds work |
| UI Engineer | Service consumption | Provide stable service contracts |
| Engine Engineer | Engine lifecycle integration | Implement engine adapters |
| Release Engineer | Startup reliability | Ensure boot is robust |

### Conflict Resolution Protocol

Core Platform has authority over:
- Runtime and storage correctness
- Service implementation details
- Persistence patterns

Defer to other roles for:
- UI presentation (defer to UI Engineer)
- Engine internals (defer to Engine Engineer)
- Contract definitions (defer to System Architect)

### Shared Artifacts

| Artifact | Platform Role | Other Roles |
|----------|---------------|-------------|
| Backend services | Primary owner | UI (consumer), Engine (consumer) |
| Health endpoints | Primary owner | Release (consumer) |
| Job state store | Primary owner | UI (status display) |
| Audio registry | Primary owner | Engine (producer), UI (consumer) |
| Context manager | Primary owner | All (consumers) |

---

## 9. Context Manager Implementation (Primary Owner)

> **Reference**: [CONTEXT_MANAGER_INTEGRATION.md](../CONTEXT_MANAGER_INTEGRATION.md)

The Core Platform Engineer is the **primary owner** of the context manager implementation. This section details ownership, implementation status, and required work.

### 9.1 Context Manager Architecture

The context manager is a protocol-driven framework at `tools/context/`:

```
tools/context/
├── core/                    # Core framework (PRIMARY OWNERSHIP)
│   ├── protocols.py         # ContextSourceProtocol definition
│   ├── models.py            # ContextBundle, AllocationContext
│   ├── manager.py           # ContextManager facade
│   ├── allocator.py         # ContextAllocator (budget enforcement)
│   ├── registry.py          # SourceRegistry (adapter management)
│   └── exceptions.py        # Custom exceptions
├── sources/                 # Source adapters (PRIMARY OWNERSHIP)
│   ├── base.py              # BaseSourceAdapter
│   ├── state_adapter.py     # Reads .cursor/STATE.md
│   ├── task_adapter.py      # Reads docs/tasks/TASK-####.md
│   ├── rules_adapter.py     # Reads .cursor/rules/**/*.mdc
│   ├── memory_adapter.py    # OpenMemory (STUBBED - needs implementation)
│   └── git_adapter.py       # Git status/shortlog
├── infra/                   # Infrastructure (PRIMARY OWNERSHIP)
│   ├── cache.py             # InMemoryCache (TTL-based)
│   ├── validation.py        # Config validation
│   └── logging.py           # Structured logging
├── config/                  # Configuration (shared with Overseer)
│   ├── context-sources.json
│   └── roles/*.json
└── cli/allocate.py          # CLI entrypoint
```

### 9.2 Implementation Status

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| ContextManager | ✅ Complete | `core/manager.py` | Facade with caching |
| ContextAllocator | ✅ Complete | `core/allocator.py` | Budget enforcement |
| SourceRegistry | ✅ Complete | `core/registry.py` | Adapter management |
| StateSourceAdapter | ✅ Complete | `sources/state_adapter.py` | Reads STATE.md |
| TaskSourceAdapter | ✅ Complete | `sources/task_adapter.py` | Ready (no briefs exist) |
| RulesSourceAdapter | ✅ Complete | `sources/rules_adapter.py` | Reads .mdc files |
| GitSourceAdapter | ✅ Complete | `sources/git_adapter.py` | Read-only git ops |
| InMemoryCache | ✅ Complete | `infra/cache.py` | TTL-based (60s) |
| **MemorySourceAdapter** | ⚠️ **STUBBED** | `sources/memory_adapter.py` | **Needs implementation** |
| MRU Cache | ❌ Not started | - | Enhancement |
| Metrics/Telemetry | ❌ Not started | - | Enhancement |

### 9.3 OpenMemory Integration Gap (Implementation Required)

**Current State**: The memory adapter is a stub that only reads from environment variable.

**File**: `tools/context/sources/memory_adapter.py` (line 20-25)

```python
# Current stubbed implementation:
def fetch(self, context: AllocationContext) -> SourceResult:
    def _load():
        # Placeholder for OpenMemory MCP integration; keep offline-safe.
        return {"memory": self._fetch_env_hint()}
    return self._measure(_load, context)
```

**Required Implementation**:

```python
# Replace stub with MCP integration
import os
from typing import List, Dict, Any

class MemorySourceAdapter(BaseSourceAdapter):
    """Fetch context from OpenMemory MCP server."""
    
    MCP_SERVER = "user-openmemory"
    PROJECT_ID = "wtsteward11/VoiceStudio"
    
    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> Dict[str, Any]:
            # Try MCP integration first
            memories = self._fetch_from_openmemory(context)
            if memories:
                return {"memory": memories}
            # Offline fallback (local-first requirement)
            return {"memory": self._fetch_env_hint()}
        return self._measure(_load, context)
    
    def _fetch_from_openmemory(self, context: AllocationContext) -> List[Dict]:
        """
        Fetch memories from OpenMemory MCP server.
        Returns empty list if MCP unavailable (offline fallback).
        """
        try:
            # MCP call via user-openmemory server
            # search-memory with:
            #   - project_id: wtsteward11/VoiceStudio
            #   - query: context.task_id or "project context"
            #   - memory_types: ["component", "implementation", "project_info"]
            # Return parsed results
            pass  # TODO: Implement MCP call
        except Exception:
            # MCP unavailable - return empty (offline fallback)
            return []
    
    def _fetch_env_hint(self) -> List[Dict]:
        """Fallback: read from CONTEXT_MEMO env var."""
        injected = os.getenv("CONTEXT_MEMO")
        if injected:
            return [{"content": injected, "source": "env:CONTEXT_MEMO"}]
        return []
```

**Implementation Checklist**:

- [ ] Read MCP tool schema: `mcps/user-openmemory/tools/search-memory.json`
- [ ] Add MCP client helper (can use subprocess to call MCP)
- [ ] Add `_fetch_from_openmemory()` implementation
- [ ] Add offline detection (try/except with fallback)
- [ ] Test with MCP available and unavailable
- [ ] Respect budget limit (`memory`: 2000 chars default)
- [ ] Add to memory_types filter: `component`, `implementation`, `project_info`, `debug`

### 9.4 Context Caching

**Current**: TTL-based InMemoryCache (60 seconds default).

**Location**: `tools/context/infra/cache.py`

```python
# Current cache key structure:
cache_key = f"{task_id}:{phase}:{role}:{include_git}:{budget_chars}"
```

**Future Enhancement (MRU Cache)**:

The MRU (Most Recently Used) cache should:
- Track access frequency for each key
- Evict least recently used entries when cache is full
- Maintain separate TTL and size limits
- Provide cache hit/miss metrics

**Implementation Design**:

```python
class MRUCache:
    """Most Recently Used cache with size limit and TTL."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache.pop(key)
            if not entry.is_expired(self._ttl_seconds):
                self._cache[key] = entry  # Move to end (most recent)
                self._hits += 1
                return entry.value
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._cache.pop(key)
        elif len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # Remove oldest
        self._cache[key] = CacheEntry(value)
    
    def metrics(self) -> Dict[str, int]:
        return {"hits": self._hits, "misses": self._misses, "size": len(self._cache)}
```

### 9.5 Metrics and Telemetry

**Not Yet Implemented**

Recommended metrics to add:

| Metric | Type | Description |
|--------|------|-------------|
| `context_fetch_time_ms` | Histogram | Time to fetch all sources |
| `context_cache_hit_rate` | Gauge | Cache hit percentage |
| `context_budget_utilization` | Gauge | % of budget used |
| `context_source_errors` | Counter | Errors per source adapter |
| `context_allocations_total` | Counter | Total allocations |

**Integration Point**: `backend/api/routes/telemetry.py`

### 9.6 Context Manager Maintenance Protocol

**Daily Checks**:

1. **Test Execution**
   ```powershell
   python -m pytest tests/tools/test_context_allocator.py -v
   ```

2. **CLI Verification**
   ```powershell
   python tools/context/allocate.py --task TASK-0001 --preamble
   ```

3. **Hook Verification**
   ```powershell
   python .cursor/hooks/inject_context.py
   ```

**When Adding New Source Adapter**:

1. Create adapter in `tools/context/sources/`
2. Implement `ContextSourceProtocol`
3. Register in `SourceRegistry`
4. Add configuration in `context-sources.json`
5. Add tests in `tests/tools/`
6. Update ADR-011 if protocol changes
7. Update CONTEXT_MANAGER_INTEGRATION.md

### 9.7 Worked Example: OpenMemory Integration

**Quality Ledger Reference**: New item (not yet in ledger)

**Objective**: Replace OpenMemory stub with real MCP integration.

**Steps**:

1. Read MCP tool schema:
   ```powershell
   Get-Content mcps\user-openmemory\tools\search-memory.json | ConvertFrom-Json | Format-List
   ```

2. Implement MCP call in `memory_adapter.py`:
   - Use subprocess or HTTP to call MCP server
   - Parse JSON response
   - Transform to adapter format

3. Add offline fallback:
   ```python
   try:
       memories = self._fetch_from_openmemory(context)
   except (ConnectionError, TimeoutError, MCPError):
       memories = self._fetch_env_hint()  # Offline fallback
   ```

4. Test:
   ```powershell
   # With MCP available
   python tools/context/allocate.py --task TASK-0001 --preamble
   
   # Without MCP (offline fallback)
   $env:CONTEXT_MEMO = "Test context"
   python tools/context/allocate.py --task TASK-0001 --preamble
   ```

5. Add proof artifact to `.buildlogs/proof_runs/`

**Exit Criteria**:
- MCP integration fetches relevant memories
- Offline fallback works when MCP unavailable
- Budget limits respected
- Tests pass

---

## Appendix A: Templates

### Service Implementation Template

```python
"""
Service: ExampleService
Purpose: [Description]
Gate: D
"""

import os
import json
from pathlib import Path
from typing import Optional

class ExampleService:
    def __init__(self, cache_dir: Optional[str] = None):
        self._cache_dir = Path(cache_dir or os.getenv(
            "VOICESTUDIO_CACHE_DIR",
            os.path.expanduser("~/.voicestudio/cache")
        ))
        self._data_file = self._cache_dir / "example_data.json"
        self._data: dict = {}
        self._load()
    
    def _load(self) -> None:
        """Load state from disk."""
        if self._data_file.exists():
            try:
                with open(self._data_file, 'r') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}
    
    def _save(self) -> None:
        """Save state to disk atomically."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self._data_file.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(self._data, f)
        temp_path.replace(self._data_file)
    
    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)
    
    def set(self, key: str, value: str) -> None:
        self._data[key] = value
        self._save()
```

### Storage Test Template

```python
"""
Tests for ExampleService
Gate: D
"""

import pytest
import tempfile
import os

from backend.services.example_service import ExampleService

class TestExampleService:
    def test_persistence_across_restart(self):
        """Verify data persists across service restart."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First instance - write data
            service1 = ExampleService(cache_dir=tmpdir)
            service1.set("key", "value")
            
            # Second instance - should load persisted data
            service2 = ExampleService(cache_dir=tmpdir)
            assert service2.get("key") == "value"
    
    def test_atomic_write(self):
        """Verify writes are atomic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ExampleService(cache_dir=tmpdir)
            service.set("key", "value")
            
            # Verify no temp files remain
            files = os.listdir(tmpdir)
            assert not any(f.endswith('.tmp') for f in files)
```

### Preflight Check Template

```python
@router.get("/health/preflight")
async def preflight() -> dict:
    """
    Preflight readiness report.
    Returns status of all required paths and dependencies.
    """
    return {
        "projects_root": _check_path(PROJECTS_ROOT),
        "cache_root": _check_path(CACHE_ROOT),
        "model_root": _check_path(MODEL_ROOT),
        "audio_registry": _check_path(AUDIO_REGISTRY_DIR),
        "ffmpeg": _check_executable("ffmpeg"),
    }

def _check_path(path: str) -> dict:
    return {
        "exists": os.path.exists(path),
        "path": path,
        "writable": os.access(path, os.W_OK) if os.path.exists(path) else False,
    }
```

---

## Appendix B: Quick Reference

### Platform Prompt (for Cursor)

```text
You are the VoiceStudio Core Platform Engineer (Role 4).
Mission: stabilize local-first orchestration (jobs, storage, artifacts, preflight).
Non-negotiables: deterministic evidence; fully implemented platform surfaces.
Start by reading: openmemory.md, backend/services/*, docs/governance/VoiceStudio_Production_Build_Plan.md.
Output: readiness gaps, persistence plan, proof commands + expected artifacts.
```

### Key Paths

| Path | Purpose |
|------|---------|
| `VOICESTUDIO_PROJECTS_DIR` | User projects |
| `VOICESTUDIO_CACHE_DIR` | Cache and temp |
| `VOICESTUDIO_MODELS_PATH` | ML models |
| `VOICESTUDIO_FFMPEG_PATH` | FFmpeg override |

### Storage Locations

```
~/.voicestudio/
├── projects/           # User projects
├── cache/
│   ├── jobs/          # Job state
│   ├── audio/         # Audio cache
│   └── models/        # Model cache
└── logs/              # Application logs
```

### Quality Ledger Items (This Role)

| ID | Gate | Category | Title |
|----|------|----------|-------|
| VS-0004 | D | STORAGE | Persist project metadata |
| VS-0006 | D | STORAGE,AUDIO | Content-addressed audio cache |
| VS-0011 | C | BOOT | ServiceProvider recursion fix |
| VS-0014 | D | RUNTIME | Job Runtime hardening |
| VS-0015 | D | STORAGE | ProjectStore migration |
| VS-0016 | E | ENGINE | Standardize Engine Interface |
| VS-0017 | E | ENGINE | Engine Manager Service |
| VS-0019 | D | STORAGE,RUNTIME | Backend preflight |
| VS-0020 | D | STORAGE,AUDIO | Durable audio artifact registry |
| VS-0021 | D | RUNTIME,STORAGE | Persist wizard job state |
| VS-0022 | D | RUNTIME,PLUGINS | Deterministic ffmpeg discovery |
| VS-0026 | C | BOOT,RUNTIME | Early crash artifact capture |
| VS-0029 | D | RUNTIME,STORAGE | Preflight jobs_root enhancement |
| VS-0033 | D | RUNTIME | Route registration |
