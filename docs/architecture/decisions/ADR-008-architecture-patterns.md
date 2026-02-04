# ADR-008: Architecture Patterns and Enforcement

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio uses "sacred boundaries" to maintain separation of concerns:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     UI      │ ←→  │    Core     │ ←→  │   Engines   │
│  (WinUI 3)  │     │  (Contracts)│     │  (Python)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Sacred Boundaries:**
1. UI may NOT call engine internals directly
2. UI interacts through stable core contracts (interfaces/protocols)
3. Engines attach via adapters that implement those contracts
4. These boundaries enable independent evolution of each layer

Without enforcement, developers may violate boundaries for convenience, leading to:
- Tight coupling between layers
- Breaking changes when engines evolve
- Difficulty testing UI without engines
- Architecture erosion over time

## Options Considered

### Option 1: Convention-Based (Code Review)
Rely on code review and documentation to enforce boundaries.

**Pros:**
- No tooling overhead
- Flexible for edge cases

**Cons:**
- Human error in review
- Inconsistent enforcement
- No automated detection

### Option 2: Interface-Enforced (Contracts Only)
Enforce via interfaces in `VoiceStudio.Core` that UI and engines must implement.

**Pros:**
- Compile-time enforcement for C#
- Clear contracts
- IDE support for navigation

**Cons:**
- No enforcement for Python engines
- Doesn't prevent direct imports
- Requires discipline to maintain

### Option 3: Automated Enforcement (Selected)
Combine interfaces with automated linting and pre-commit checks.

**Pros:**
- Catches violations before commit
- Consistent enforcement
- Scalable across team
- Documents patterns via rules

**Cons:**
- Initial setup overhead
- May need rule maintenance
- False positives possible

## Decision

**Option 3: Automated Enforcement** with a layered approach:

### Layer 1: Core Contracts (Compile-Time)

```csharp
// src/VoiceStudio.Core/Contracts/IBackendClient.cs
public interface IBackendClient
{
    Task<EnginesListResponse> GetEnginesAsync();
    Task<VoiceConvertResponse> ConvertVoiceAsync(VoiceConvertRequest request);
    // ...
}
```

- UI depends only on interfaces in `VoiceStudio.Core`
- Backend implements these contracts via HTTP
- Engines implement `EngineProtocol` in Python

### Layer 2: Rule Files (Documentation + Guidance)

```yaml
# .cursor/rules/core/architecture.mdc
## Sacred boundaries (UI ↔ Core ↔ Engines)
- UI may NOT call engine internals directly
- UI interacts through stable core contracts
- Engines attach via adapters
```

- Rules provide context for AI agents
- Documentation for developers
- Referenced in code reviews

### Layer 3: Pre-Commit Hooks (Automated)

```yaml
# .pre-commit-config.yaml
- id: architecture-boundary-check
  name: Check Architecture Boundaries
  entry: python scripts/check_architecture_boundaries.py
  language: system
  types: [csharp]
```

- Blocks commits that violate boundaries
- Checks for direct engine imports in UI code
- Validates namespace usage

### Layer 4: Roslyn Analyzers (Build-Time - Future)

```csharp
// Future: Custom Roslyn analyzer
[DiagnosticAnalyzer(LanguageNames.CSharp)]
public class BoundaryAnalyzer : DiagnosticAnalyzer
{
    // Detect: using app.core.engines (forbidden in UI)
}
```

- IDE warnings for violations
- Build errors in CI
- Planned for Phase 9

## Implementation Status

| Layer | Status | Evidence |
|-------|--------|----------|
| Core Contracts | ✅ Complete | `src/VoiceStudio.Core/` interfaces |
| Rule Files | ✅ Complete | `.cursor/rules/core/architecture.mdc` |
| Pre-Commit Hooks | ⚠️ Partial | Basic hooks exist; boundary check TODO |
| Roslyn Analyzers | ❌ Planned | Phase 9 |

## Consequences

### Positive
- Boundaries enforced automatically
- Violations caught before merge
- Clear contracts for each layer
- Supports independent evolution
- Testability improved (mock contracts)

### Negative
- Initial setup time for analyzers
- False positives need handling
- Developers must understand patterns
- Maintenance overhead for rules

### Neutral
- Existing code may have violations to fix
- Learning curve for new developers
- Rules need periodic review

## Enforcement Examples

### Allowed
```csharp
// UI → Core contract → Backend
var engines = await _backendClient.GetEnginesAsync();
```

```python
# Backend → Engine service → Engine
result = await engine_service.synthesize(text, engine_id)
```

### Forbidden
```csharp
// UI directly importing engine internals
using app.core.engines;  // ❌ FORBIDDEN
var engine = new XTTSEngine();  // ❌ FORBIDDEN
```

```python
# Route directly importing engine
from app.core.engines.xtts_engine import XTTSEngine  # ❌ Use EngineService
```

## References

- `.cursor/rules/core/architecture.mdc`
- `src/VoiceStudio.Core/` - Contract interfaces
- ADR-007: IPC Boundary (HTTP choice)
- ADR-019: Orchestration in Python
