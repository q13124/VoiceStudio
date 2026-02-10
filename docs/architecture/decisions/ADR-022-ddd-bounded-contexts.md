# ADR-022: Domain-Driven Design Bounded Contexts

## Status

**Accepted** - 2026-02-10

## Context

VoiceStudio's backend has grown organically with multiple feature domains. The `backend/` directory structure needs clear boundaries to:

1. Prevent coupling between unrelated features
2. Enable independent evolution of domains
3. Clarify ownership and responsibility
4. Support future plugin architecture

## Options Considered

### Option A: Flat Structure

All services in a single `services/` directory.

- **Pros**: Simple navigation
- **Cons**: No boundaries, everything can depend on everything

### Option B: Layer-Based Organization

Organize by technical layer (routes, services, models).

- **Pros**: Familiar pattern, clear technical separation
- **Cons**: Business logic scattered across layers, hard to refactor features

### Option C: Domain-Driven Bounded Contexts

Organize by business domain with clear boundaries.

- **Pros**: Domain isolation, clear ownership, plugin-ready
- **Cons**: Requires upfront domain analysis, some duplication

## Decision

Adopt **Option C: Domain-Driven Bounded Contexts**.

### Domain Structure

```
backend/
├── api/                    # API Layer (cross-cutting)
│   ├── routes/             # HTTP endpoints
│   ├── middleware/         # Request processing
│   └── validators/         # Input validation
│
├── domain/                 # Business Logic Domains
│   ├── synthesis/          # Voice synthesis core
│   ├── training/           # Model training
│   ├── analysis/           # Audio analysis
│   └── project/            # Project management
│
├── voice/                  # Voice Processing Domain
│   ├── emotion/            # Emotion detection/synthesis
│   ├── rvc/                # Real-time Voice Conversion
│   ├── translation/        # Voice translation
│   └── effects/            # Audio effects
│
├── integrations/           # External Integrations
│   ├── cloud/              # Cloud provider adapters
│   ├── daw/                # DAW integration
│   └── video/              # Video editor integration
│
├── infrastructure/         # Technical Infrastructure
│   ├── persistence/        # Data storage
│   ├── messaging/          # Event bus
│   └── caching/            # Cache layer
│
└── services/               # Shared Services (legacy, being migrated)
```

### Bounded Context Rules

1. **Internal Cohesion**: Each context owns its models, services, and storage
2. **External Communication**: Contexts communicate via defined interfaces or events
3. **No Circular Dependencies**: Context A cannot depend on Context B if B depends on A
4. **Anti-Corruption Layer**: External integrations wrapped in adapters

### Migration Strategy

Phase 1 (Current):
- Identify domain boundaries
- Create domain directories
- Keep `services/` for shared utilities

Phase 2 (Future):
- Move domain-specific services into contexts
- Introduce domain events
- Define public interfaces per context

## Consequences

### Positive

- Clear feature ownership
- Independent testing per domain
- Easier to extract plugins
- Reduced coupling

### Negative

- Initial complexity increase
- Potential code duplication
- Requires team discipline
- Learning curve for new contributors

### Implementation Evidence

- Domain directories: `backend/domain/`, `backend/voice/`
- Integration directories: `backend/integrations/`
- Infrastructure: `backend/infrastructure/`

## Related ADRs

- ADR-008: Architecture Patterns and Enforcement
- ADR-015: Architecture Integration Contract
