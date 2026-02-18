# ADR-037: Plugin Trust Lane Model (Phase 3)

**Status:** Accepted  
**Date:** 2026-02-16  
**Deciders:** System Architect (Role 1), Core Platform (Role 4)
**Supersedes:** None

## Context

Phase 3 migrates first-party VoiceStudio features into the plugin system
(effects, engines, exporters). External analysis recommended a tiered trust model
with an in-process lane for trusted plugins and an isolated lane for
untrusted/third-party plugins.

Current Phase 3 scope is first-party only. Introducing out-of-process isolation
immediately would add complexity and delay migration without reducing practical
risk for first-party code.

## Decision

Adopt a **two-lane trust model** with staged rollout:

- **Lane A (implemented in Phase 3):** trusted first-party plugins run in-process.
- **Lane B (deferred to Phase 4+):** isolated execution for third-party plugins.

Phase 3 plugin contracts are designed to be lane-agnostic so Lane B can be
introduced without breaking plugin APIs.

## Alternatives Considered

1. **Force out-of-process isolation in Phase 3.** Rejected: higher delivery risk
   and complexity for first-party migration.
2. **Stay permanently in-process.** Rejected: insufficient for future third-party
   ecosystem safety requirements.

## Consequences

### Positive

- Enables rapid feature migration with lower implementation risk.
- Preserves path to stronger isolation later.
- Keeps plugin manifests/contracts stable for future hardening.

### Negative

- Phase 3 does not provide third-party execution isolation.
- Additional Phase 4 work is required for sandbox/process boundary hardening.

## Risk Controls in Phase 3

- Capability permissions enforced by existing plugin permission model.
- Plugin lifecycle boundaries with explicit health endpoints.
- Feature-flag fallback path remains available for migrated features.
- Route-level error containment to avoid host crash propagation.

## Phase 4 Follow-ups

- Out-of-process runner for Lane B.
- Signature/provenance policy for third-party plugins.
- Enhanced permission policy enforcement and kill-switch controls.

## References

- `docs/plugins/engine-adapter-pattern.md`
- `docs/plugins/migration-guide.md`
- `docs/architecture/decisions/ADR-036-plugin-system-unification.md`
