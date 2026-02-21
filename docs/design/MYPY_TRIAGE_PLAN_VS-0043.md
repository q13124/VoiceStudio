# VS-0043 Mypy Triage Plan

**Ledger ID**: VS-0043  
**Status**: OPEN (S4 Chore)  
**Scope**: 5892 mypy errors in `backend/` (technical debt baseline)  
**Created**: 2026-02-21 (Phase 8 WS5)

## Summary

Running `mypy backend/ --strict --ignore-missing-imports` surfaces ~5892 type errors. This document provides a prioritized remediation plan.

## Severity Categories

| Category | Description | Example | Priority |
|----------|-------------|---------|----------|
| **Critical** | Public API routes, engine service, plugin system | Missing return types, `Any` in request/response | P0 |
| **High** | Shared services, middleware | Unannotated function params | P1 |
| **Medium** | Internal helpers, utilities | Optional chaining, union types | P2 |
| **Low** | Test files, deprecated code | Legacy patterns | P3 |

## Prioritized Remediation Order

1. **API routes** (`backend/api/routes/`) — Request/response models, Depends()
2. **Engine service** (`backend/services/engine_service.py`, `app/core/engines/`) — Core synthesis path
3. **Plugin system** (`backend/plugins/`, `backend/services/plugin_*.py`) — Sandbox, gallery
4. **Middleware** (`backend/api/middleware/`) — Auth, tracing, validation
5. **Models** (`backend/api/models*.py`) — Pydantic and shared types

## Top-20 Impactful Fixes (Phase 8 Target)

1. Add return type annotations to API route handlers
2. Annotate `Depends()` injection targets
3. Fix `Optional`/`None` handling in engine router
4. Add type hints to plugin sandbox public methods
5. Annotate circuit breaker callbacks
6. Fix `list` vs `List` in model definitions (use `list` from `__future__` annotations)
7. Add `TypeVar` for generic service returns
8. Annotate WebSocket handler parameters
9. Fix `dict` vs `Dict` in JSON response types
10. Add `Protocol` for engine adapter interface
11–20. Continue with remaining high-traffic paths

## Commands

```bash
# Full audit
python -m mypy backend/ --strict --ignore-missing-imports 2>&1 | tee .buildlogs/mypy_audit.txt

# Count by file
python -m mypy backend/ --strict --ignore-missing-imports 2>&1 | grep "error:" | cut -d: -f1 | sort | uniq -c | sort -rn | head -30
```

## References

- QUALITY_LEDGER.md § VS-0043
- pyproject.toml [tool.mypy]
- ADR-027 (verification harness)
