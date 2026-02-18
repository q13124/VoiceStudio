# ADR-038: Plugin ABC Unification (Phase 4)

**Status:** Accepted  
**Date:** 2026-02-17  
**Deciders:** Lead/Principal Architect, System Architect (Role 1)  
**Supersedes:** Clarifies ADR-036

## Context

Phase 3 delivered 8 first-party plugins using `BasePlugin` from `app/core/plugins_api/base.py`. Simultaneously, `PluginService` in `backend/services/plugin_service.py` defines an entirely separate hierarchy with `PluginBase` and its subclasses (`EnginePlugin`, `ProcessorPlugin`, `ExporterPlugin`, `ImporterPlugin`).

This dual-ABC situation creates confusion:

| Class | Location | Used By | Interface |
|-------|----------|---------|-----------|
| `BasePlugin` | `app/core/plugins_api/base.py` | Phase 3 plugins, `PluginLoader` | `register(app)`, `initialize()`, `cleanup()` |
| `PluginBase` | `backend/services/plugin_service.py` | `PluginService` lifecycle | `activate()`, `deactivate()`, `manifest` property |

Third-party plugin developers cannot reasonably choose between these without deep VoiceStudio internals knowledge. This is a blocker for Phase 4 community marketplace adoption.

## Decision

**Unify into a single `Plugin` ABC** with the following design:

1. Create new `Plugin` class in `app/core/plugins_api/plugin.py`
2. Combine the best of both existing ABCs:
   - `register(app)` from `BasePlugin` (required for FastAPI route registration)
   - `initialize()` / `cleanup()` lifecycle hooks
   - `activate()` / `deactivate()` async lifecycle (optional, for dynamic enable/disable)
   - `manifest` property and `PluginMetadata` integration
   - `health()` method for health checks
3. Provide optional mixins for plugin types:
   - `ProcessorMixin` -- adds `process()` contract
   - `EngineMixin` -- adds `synthesize()`, `list_voices()` contracts
   - `ExporterMixin` -- adds `export()`, `supported_formats` contracts
4. Deprecate both `BasePlugin` and `PluginBase` with `warnings.warn()`
5. Keep deprecated classes functional for 2 minor releases, then remove

## Unified Plugin Interface

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class Plugin(ABC):
    """Unified base class for all VoiceStudio plugins."""
    
    def __init__(self, plugin_dir: Path):
        self._plugin_dir = plugin_dir
        self._metadata = PluginMetadata(plugin_dir / "manifest.json")
        self._initialized = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    @property
    def name(self) -> str:
        return self._metadata.name
    
    @property
    def version(self) -> str:
        return self._metadata.version
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @abstractmethod
    def register(self, app) -> None:
        """Register plugin routes with FastAPI. Required for all plugins."""
        ...
    
    def initialize(self) -> None:
        """Synchronous initialization after registration. Optional."""
        self._initialized = True
    
    def cleanup(self) -> None:
        """Synchronous cleanup on shutdown. Optional."""
        self._initialized = False
    
    async def activate(self) -> bool:
        """Async activation for dynamic enable. Optional."""
        return True
    
    async def deactivate(self) -> bool:
        """Async deactivation for dynamic disable. Optional."""
        return True
    
    def health(self) -> dict[str, Any]:
        """Return health status. Optional."""
        return {"status": "healthy" if self._initialized else "not_initialized"}
```

## Migration Path

### For existing Phase 3 plugins (BasePlugin consumers)

1. Change base class: `class MyPlugin(BasePlugin)` → `class MyPlugin(Plugin)`
2. Update `__init__`: accept `plugin_dir: Path` instead of `metadata: PluginMetadata`
3. No other changes required (API is compatible)

### For PluginService consumers (PluginBase consumers)

1. Change base class: `class MyPlugin(PluginBase)` → `class MyPlugin(Plugin)`
2. Rename `activate()`/`deactivate()` implementations (async signatures unchanged)
3. Add `register(app)` implementation if not present

### Deprecation timeline

- **v1.3.0**: Introduce `Plugin`, mark `BasePlugin` and `PluginBase` deprecated
- **v1.4.0**: Emit deprecation warnings on import
- **v1.5.0**: Remove `BasePlugin` and `PluginBase`

## Alternatives Considered

1. **Keep both ABCs.** Rejected: Confusing for third-party developers; documentation burden; maintenance cost.
2. **Favor one ABC over the other.** Rejected: Both have valid features; combining is better than discarding.
3. **Create a facade adapter.** Rejected: Adds indirection without solving root cause.

## Consequences

### Positive

- Single clear path for third-party developers
- Consistent interface across all plugins
- Simpler documentation
- Easier testing (one ABC to mock)
- Enables Phase 4 marketplace with clear SDK

### Negative

- Migration work for existing 8 plugins and 7 templates
- Breaking change for any external consumers of deprecated ABCs
- Two-release deprecation window requires coordination

### Neutral

- `PluginService` and `PluginLoader` both need updates to accept unified `Plugin`

## Implementation Checklist

- [x] Create `app/core/plugins_api/plugin.py` with unified `Plugin` ABC
- [x] Create mixins in `app/core/plugins_api/mixins.py`
- [x] Migrate 8 Phase 3 plugins to `Plugin`
- [x] Migrate 6 templates to `Plugin` (7th was a duplicate)
- [x] Update `PluginLoader` to expect `Plugin` (both `backend/api/plugins/loader.py` and `backend/plugins/core/loader.py`)
- [x] Update `PluginService` to expect `Plugin`
- [x] Add deprecation warnings to `BasePlugin` and `PluginBase` (and `backend/plugins/core/base.Plugin`)
- [x] Update `docs/plugins/migration-guide.md`
- [x] Verify all tests pass (2026-02-16: plugin imports verified, schema validator 29/29 passed)

## References

- `app/core/plugins_api/base.py` (current BasePlugin)
- `backend/services/plugin_service.py` (current PluginBase)
- ADR-036: Plugin System Unification
- ADR-037: Plugin Trust Lane Model
- Phase 4 Marketplace Plan
