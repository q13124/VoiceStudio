# ADR-024: Completion Evidence Guard

## Status

**Accepted** - 2026-02-01

## Context

Previously, sessions could mark plan or task items complete (e.g. `[x]`, `status: complete`) in documentation without committing those changes. Verification could pass with a dirty working tree, and closure protocol did not require completion markers to be committed. This allowed "complete" to be claimed without proof in version control.

## Decision

We adopt a **Completion Evidence Guard** that fails verification when completion markers appear in uncommitted changes under guarded paths. The guard:

- Runs as part of `scripts/run_verification.py` (and can be skipped with `--skip-guard` for dry-run or diagnostics).
- Scans staged and unstaged diffs plus untracked files under: `.cursor/STATE.md`, `.cursor/plans/`, `docs/tasks/`, `docs/reports/verification/`, `docs/reports/packaging/`, `docs/governance/`, `docs/design/`.
- Detects completion patterns: `[x]`, `status: complete`, `status: done`, `state: complete`, `state: done`, `phase: complete`.
- Is integrated with the stop hook (`.cursor/hooks/ensure_state_update.py`) and optional pre-commit hook so agents and developers are prompted to commit completion/proof updates before closing.

Completion markers must be **committed** before verification passes. The guard is local-only: CI (clean checkout) always passes.

## Consequences

### Positive

- Prevents claiming completion without committing proof.
- Aligns closure protocol with version-controlled evidence.
- Single implementation in `tools/overseer/verification/completion_guard.py`; reusable from verification, hooks, and pre-commit.

### Negative

- Developers and agents must be aware of guarded paths; uncommitted checklist updates in those paths will fail the guard.
- Bypass via `--skip-guard` is possible; usage should be limited to dry-run or diagnostic scenarios and documented in DoD/ADR.

### Neutral

- Guard runs in ~1s; acceptable overhead in verification.
- Code fence detection and optional flags (`--dry-run`, `--list-paths`, `--verbose`) reduce false positives and aid diagnostics.
