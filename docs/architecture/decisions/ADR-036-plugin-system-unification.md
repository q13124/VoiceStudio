# ADR-036: Plugin System Unification

**Status:** Accepted
**Date:** 2026-02-16
**Deciders:** Overseer (Role 0), System Architect (Role 1)
**Supersedes:** None

## Context

VoiceStudio has two independent, dormant plugin systems that evolved separately:

- **Backend (Python):** `backend/services/plugin_service.py` provides discovery, lifecycle management, hot-reload, and extension points via `BasePlugin` in `app/core/plugins_api/base.py`. API integration lives in `backend/api/plugins/`.
- **Frontend (C#):** `src/VoiceStudio.App/Services/PluginManager.cs` discovers DLL assemblies implementing `IPlugin`, registers panels via `IPanelRegistry`, and connects to the backend via `IBackendClient`.

These systems are disconnected: different manifest schemas, no state synchronization, no shared security model. A plugin loaded in the backend has no coordination with the frontend, and vice versa. The plugin directories contain only placeholder/example content.

External analysis (ChatGPT architectural review) confirmed that unifying these systems and establishing a security/governance framework is the correct next step for ecosystem extensibility.

## Decision

We will **unify the backend and frontend plugin systems** under a single architecture with three implementation phases:

### Phase 1: Foundation (Unified Schema + Bridge + Security)
- **Single manifest schema** at `shared/schemas/plugin-manifest.schema.json` validated by both Python and C# layers.
- **Plugin bridge service** in the frontend that synchronizes plugin state with the backend via existing HTTP/WS boundary (per ADR-007).
- **Capability-based permission model** with user approval workflow and sandboxed file/network access.
- **Working example plugin** demonstrating full-stack (Python + C#) capabilities.

### Phase 2: Developer Experience
- Getting Started guide, API reference, best practices documentation.
- Plugin templates (backend-only, frontend-only, full-stack, audio effect).
- CLI generator tool for scaffolding new plugins.

### Phase 3: Core Migration
- Migrate suitable features (audio effects, optional TTS engines, export formats) to plugins.
- Feature-flag-gated parallel implementations during transition.

## Constraints

| Constraint | Resolution |
|------------|------------|
| **Sacred boundaries (UI ↔ Core ↔ Engine)** | Bridge service uses `IBackendClient` HTTP/WS only; no direct cross-layer calls |
| **Free-only policy** | Use `JsonSchema.Net` (MIT, already in project) for C# validation; NOT `Newtonsoft.Json.Schema` (rate-limited free tier) |
| **Core stays dependency-light** | Plugin schema validator lives in `VoiceStudio.App`, not `VoiceStudio.Core`; shared models/interfaces only in Core |
| **Local-first** | No cloud plugin marketplace required; local directory discovery is the default |
| **No error suppression** | Plugin load failures are logged with actionable messages; never silently skipped |

## Alternatives Considered

1. **Keep systems separate.** Rejected: perpetuates fragmentation, prevents full-stack plugins, doubles maintenance.
2. **Replace both with a single new system.** Rejected: discards working infrastructure; higher risk, longer timeline.
3. **Backend-only plugins, no C# plugins.** Rejected: limits UI extensibility that the existing `PluginManager` already supports.

## Consequences

### Positive
- Single manifest schema eliminates schema drift between layers.
- Bridge service provides unified plugin status view for the management UI.
- Permission model establishes security boundaries before third-party plugins arrive.
- Templates and tooling reduce plugin creation time from days to hours.
- Feature migration to plugins reduces core application complexity.

### Negative
- Adds `jsonschema` Python dependency (already in requirements.txt).
- Bridge service adds a synchronization layer that must be maintained.
- Manifest schema evolution requires backward-compatible changes.

### Risks
| Risk | Mitigation |
|------|------------|
| Schema changes break existing plugins | Version schema; support multiple versions during migration |
| Plugin crashes affect host application | Sandboxing + error boundaries; future: out-of-process isolation |
| Low adoption by developers | Invest in Phase 2 DX; maintain reference plugin |
| Performance overhead from plugin abstraction | Lazy loading; per-plugin resource budgets; monitoring |

## Compliance

- Implements guidelines from external architectural review (ChatGPT analysis, 2026-02-16).
- Aligns with `architecture.mdc` "Plugin-first mindset" principle.
- Governed by `docs/governance/PLUGIN_SYSTEM_GUIDELINES.md` (companion document).
- ADR-007 (IPC boundary) governs the bridge communication pattern.
- ADR-025 (Compatibility Matrix) governs dependency additions.

## References

- `docs/governance/PLUGIN_SYSTEM_GUIDELINES.md` — Operational guidelines for plugin development
- `shared/schemas/plugin-manifest.schema.json` — Unified manifest schema
- `backend/services/plugin_service.py` — Backend plugin service
- `src/VoiceStudio.App/Services/PluginManager.cs` — Frontend plugin manager
- `app/core/plugins_api/base.py` — Plugin base classes and contracts
