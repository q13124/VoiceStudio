# ADR-012: Roadmap Integration Scaffolding

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio evolved through multiple development approaches:
1. Initial ChatGPT-guided development with a worker system
2. Cursor-based development with basic rules
3. Current 8-role agent system with comprehensive governance

This evolution created:
- Multiple overlapping roadmap documents
- Conflicting conventions and patterns
- Legacy worker system documentation
- Need for consolidation

## Options Considered

1. **Complete rewrite** - Ignore legacy roadmap
   - Pros: Clean slate, no legacy debt
   - Cons: Loses historical context, breaks references

2. **Incremental migration** - Archive legacy, adopt new patterns
   - Pros: Preserves history, gradual transition, maintains references
   - Cons: Maintenance of archive, dual systems during transition

3. **Hybrid** - Reference legacy, implement with new system
   - Pros: Flexible, can cherry-pick useful legacy items
   - Cons: Confusion about which is authoritative

## Decision

**Option 2: Incremental migration** with:

### 1. Single Source of Truth Roadmap

`docs/governance/MASTER_ROADMAP_UNIFIED.md` is the canonical roadmap:
- Supersedes all prior roadmap documents
- Owner: Overseer (Role 0)
- Updated with each phase completion
- Contains executive summary, phase details, gate status

### 2. Legacy Archive

All legacy documents archived to `docs/archive/`:

| Archive Location | Content |
|------------------|---------|
| `docs/archive/legacy_worker_system/` | ChatGPT worker system (1755 files) |
| `docs/archive/governance_consolidated/` | Previous rule consolidations |
| `docs/archive/architecture_consolidated/` | Previous architecture docs |

### 3. Governance Migration

| Old System | New System |
|------------|------------|
| Worker roles | 8-role agent system |
| Embedded rules | `.cursor/rules/*.mdc` |
| Task system | STATE.md + TASK briefs |
| Quality gates | Gate A-H system |
| Validation | Skeptical Validator |

### 4. Reference Policy

- **Canonical**: `docs/governance/`, `.cursor/rules/`, `docs/architecture/decisions/`
- **Historical**: `docs/archive/` (read-only, for context)
- **Deprecated**: Direct references to archived docs in active code/docs

## Implementation Evidence

- `docs/governance/MASTER_ROADMAP_UNIFIED.md` - Canonical roadmap (v1.0.0)
- `docs/archive/legacy_worker_system/` - Archived legacy (1755 files)
- `docs/archive/governance_consolidated/` - Archived rules
- `.cursor/rules/` - Current rule system (30+ rules)
- `docs/governance/roles/` - 8-role documentation

## Consequences

### Positive
- Single authoritative roadmap
- Historical context preserved
- Clear migration path
- No loss of information
- Gradual, safe transition

### Negative
- Large archive to maintain
- Some references may break
- Need to update all active references

### Neutral
- Archive requires periodic cleanup
- Legacy patterns still visible in older code
- Training needed on new system
