# ADR-002: Document Governance Architecture

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio requires a formal document governance system to manage canonical documentation, prevent duplication, and maintain documentation hygiene. Without governance:
- Duplicate documents proliferate (e.g., spec_v2.md, spec_final.md)
- Conflicting information causes confusion
- Finding authoritative documentation becomes difficult
- Documentation debt accumulates

## Options Considered

1. **Informal governance** - No formal structure, rely on convention
   - Pros: Low overhead, flexible
   - Cons: Inconsistent enforcement, documentation sprawl

2. **Registry-based governance** - Single CANONICAL_REGISTRY as source of truth
   - Pros: Clear authority, discoverable, maintainable
   - Cons: Requires discipline to maintain registry

3. **Tooling-enforced governance** - Automated validation of document structure
   - Pros: Consistent enforcement, scalable
   - Cons: High implementation overhead, may be too rigid

## Decision

**Option 2: Registry-based governance** with agent rule enforcement.

The system consists of three components:

### 1. Canonical Registry (`docs/governance/CANONICAL_REGISTRY.md`)
- Single source of truth for all canonical documents
- Lists document path, purpose, and owner
- Updated when documents are created or archived

### 2. Governance Rules (`docs/governance/DOCUMENT_GOVERNANCE.md`)
- 4-gate check before creating any document
- Location rules by document type
- Naming conventions
- Archive workflow for superseded documents

### 3. Agent Rules (`.cursor/rules/workflows/document-lifecycle.mdc`)
- AI agents follow 4-gate check automatically
- Prevents creation of duplicate documents
- Enforces location and naming compliance

### Location Rules

| Type | Location |
|------|----------|
| ADR | `docs/architecture/decisions/` |
| Roadmap | `docs/governance/` |
| Plan/Spec | `docs/design/` |
| Reference | `docs/REFERENCE/` |
| Developer Guide | `docs/developer/` |
| Report | `docs/reports/{category}/` |
| Release Notes | `docs/release/` |

## Implementation Evidence

- `docs/governance/CANONICAL_REGISTRY.md` - Document registry (active)
- `docs/governance/DOCUMENT_GOVERNANCE.md` - Governance rules (active)
- `.cursor/rules/workflows/document-lifecycle.mdc` - Agent rules (active)
- `docs/archive/` - Archive location for superseded documents

## Consequences

### Positive
- Single source of truth for documentation authority
- Reduced documentation sprawl
- Consistent document organization
- Agent-enforced compliance reduces human error

### Negative
- Requires registry maintenance
- Learning curve for new contributors
- May slow initial document creation

### Neutral
- Existing documents require migration/registration
- Registry becomes critical dependency
