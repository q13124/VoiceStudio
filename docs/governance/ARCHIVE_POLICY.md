# VoiceStudio Archive Policy

> **Last Updated**: 2026-02-03  
> **Owner**: Overseer (Role 0)  
> **Status**: Active

## Purpose

This policy defines the rules and procedures for archiving documents in VoiceStudio. Proper archival ensures documentation history is preserved while keeping active directories clean and discoverable.

## When to Archive

Documents should be archived when:

1. **Superseded**: A new document replaces an existing one
2. **Obsolete**: The document describes deprecated functionality
3. **Consolidated**: Multiple documents merged into one
4. **Completed**: Time-limited documents (e.g., migration plans) that are done

## Archive Locations

| Document Type | Archive Location |
|---------------|------------------|
| Governance docs | `docs/archive/governance/` |
| Architecture docs | `docs/archive/architecture/` |
| Design/specs | `docs/archive/design/` |
| Reports | `docs/archive/reports/` |
| Task briefs | `docs/archive/tasks/` |
| Legacy code docs | `docs/archive/legacy/` |

## Archive Procedure

### 1. Mark as Superseded

Before moving, add a header to the document:

```markdown
> **ARCHIVED**: This document has been superseded by [NEW_DOC_PATH](link).  
> **Archive Date**: YYYY-MM-DD  
> **Reason**: [superseded|obsolete|consolidated|completed]
```

### 2. Move to Archive

Move the file to the appropriate archive subdirectory:

```bash
git mv docs/governance/OLD_DOC.md docs/archive/governance/OLD_DOC.md
```

### 3. Update CANONICAL_REGISTRY

In `docs/governance/CANONICAL_REGISTRY.md`:
- Remove the document from the active section
- Add to the "Archived Documents" section with date and reason

### 4. Update References

Search for references to the archived document and update them:
- Point to the new document if superseded
- Mark as archived/deprecated if obsolete

## What NOT to Archive

Do not archive:
- Active configuration files
- Current ADRs (even if partially implemented)
- Living documents that are still being updated
- API documentation for active endpoints

## Retention

Archived documents are retained indefinitely in git history. The archive directories serve as discoverable references for historical context.

## Consolidated Archives

The following consolidation archives were created during the 2026-01-25 governance cleanup:

| Archive | Contents | Date |
|---------|----------|------|
| `docs/archive/governance_consolidated/` | Pre-consolidation governance docs | 2026-01-25 |
| `docs/archive/legacy_worker_system/` | Legacy worker/role system docs | 2026-01-30 |

## Related Documents

- [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md) - Document lifecycle rules
- [CANONICAL_REGISTRY.md](CANONICAL_REGISTRY.md) - Document registry
- ADR-002: Document Governance Architecture
