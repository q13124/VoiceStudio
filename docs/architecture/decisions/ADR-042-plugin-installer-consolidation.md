# ADR-042: Plugin Installer Consolidation (v1 to v2)

**Status:** Accepted
**Date:** 2026-02-21
**Decision Makers:** Overseer (Role 0)

## Context

Two plugin installer implementations exist in `backend/plugins/gallery/`:

- `installer.py` (v1): Basic download, checksum verification, dependency checking
- `installer_v2.py` (v2): Atomic installation with rollback, .vspkg format, integrated verification (signature, SBOM, provenance), transaction-based multi-plugin installation, backup/restore

Both are exported from `__init__.py`. Code may import from either.

## Decision

Consolidate on `installer_v2.py` as the sole plugin installer. The v1 `installer.py` receives a deprecation notice directing all callers to v2.

## Rationale

- v2 is a strict superset of v1 functionality
- v2 adds atomic installation with rollback (critical for reliability)
- v2 integrates with the supply chain verification pipeline (signatures, SBOM)
- v2 supports the .vspkg package format used by the plugin CLI
- No code paths exclusively require v1 behavior

## Consequences

### Positive

- Single installer implementation reduces maintenance burden
- Atomic install/rollback prevents broken plugin states
- Integrated verification improves security posture

### Negative

- Minor: callers importing from `installer.py` must migrate to `installer_v2.py`
- The `get_install_service()` convenience function in v1 remains as a compatibility shim

### Migration Path

1. `installer.py` adds deprecation warning on import
2. `__init__.py` continues exporting both for backward compatibility
3. New code must use `installer_v2` imports exclusively
4. v1 will be removed in a future release (v1.1.0+)
