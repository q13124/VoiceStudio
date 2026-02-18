# ADR-040: Dual Plugin Loader Architecture

**Status:** Accepted  
**Date:** 2026-02-18  
**Deciders:** Lead/Principal Architect, System Architect (Role 1)  
**Supersedes:** None (clarifies existing architecture)

## Context

VoiceStudio has two independent plugin loading mechanisms:

| Loader | Location | Purpose | Lifecycle |
|--------|----------|---------|-----------|
| `PluginLoader` | `backend/api/plugins/loader.py` | Startup-time loading of bundled plugins | Application startup |
| `PluginService` | `backend/services/plugin_service.py` | Dynamic runtime plugin management | Any time during runtime |

This dual architecture exists for historical reasons and has caused confusion among contributors. This ADR documents the rationale and intended usage of each system.

## Decision

**Maintain both loaders** with clearly defined responsibilities:

### PluginLoader (API Layer)

**Purpose:** Load first-party bundled plugins at FastAPI startup.

**Characteristics:**
- Synchronous loading during `app.on_startup`
- Registers routes directly with FastAPI app
- Used for plugins shipped with VoiceStudio
- Located in API layer (`backend/api/plugins/`)

**Usage:**
```python
# In backend/api/main.py
from backend.api.plugins.loader import PluginLoader

@app.on_event("startup")
async def load_bundled_plugins():
    loader = PluginLoader(app)
    loader.discover_and_load("plugins/")
```

### PluginService (Service Layer)

**Purpose:** Manage third-party and user-installed plugins dynamically.

**Characteristics:**
- Async lifecycle management (discover, load, activate, deactivate, unload)
- State machine tracking (DISCOVERED → LOADED → ACTIVATED)
- Signature verification integration
- Wasm execution support
- Located in service layer (`backend/services/`)

**Usage:**
```python
from backend.services.plugin_service import PluginService

service = PluginService()
await service.discover_plugins()
await service.load_plugin("/path/to/plugin")
await service.activate_plugin("plugin_id")
```

### When to Use Each

| Scenario | Loader |
|----------|--------|
| First-party plugins shipped with VoiceStudio | `PluginLoader` |
| Third-party marketplace plugins | `PluginService` |
| User-installed local plugins | `PluginService` |
| Wasm plugins | `PluginService` |
| Plugins requiring signature verification | `PluginService` |
| Hot-reloadable plugins | `PluginService` |

### Interaction Between Loaders

1. `PluginLoader` runs first during FastAPI startup
2. `PluginService` initializes after, discovering additional plugins
3. Bundled plugins are NOT managed by `PluginService` (separate lifecycles)
4. Both can coexist without conflict

## Consequences

### Positive
- Clear separation of concerns
- First-party plugins load fast without async overhead
- Third-party plugins get full lifecycle management
- No breaking changes to existing plugins

### Negative
- Two codepaths to maintain
- Potential for confusion without this documentation
- Bundled plugins cannot use PluginService features (Wasm, signatures)

### Future Consolidation

If consolidation is desired, the recommended path is:

1. Migrate first-party plugins to use `PluginService` with "trusted" flag
2. Add synchronous initialization option to `PluginService`
3. Deprecate `PluginLoader` once all plugins migrated
4. Remove `PluginLoader` in a major version

This consolidation is **NOT** required for Phase 6 completion and is deferred to a future release.

## Related ADRs

- ADR-036: Plugin System Unification
- ADR-038: Plugin ABC Unification
- ADR-039: Phase 6 Strategic Maturity
