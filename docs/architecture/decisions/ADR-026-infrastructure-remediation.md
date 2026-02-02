# ADR-026: Infrastructure Remediation

**Status**: Accepted  
**Date**: 2026-02-02  
**Deciders**: Overseer (Role 0), Core Platform (Role 4), Build & Tooling (Role 2)  
**Technical Story**: Infrastructure audit revealed ~40% average utilization of implemented systems

## Context

A comprehensive audit of VoiceStudio's development infrastructure identified significant gaps between implemented systems and their actual usage:

| System | Implementation | Actual Usage Before | Target |
|--------|---------------|---------------------|--------|
| Role System | 100% | ~70% | 95%+ |
| Context Manager | 90% | ~40% | 90%+ |
| Issue System | 95% | ~30% | 90%+ |
| Telemetry | 70% | ~10% | 80%+ |
| OpenMemory MCP | 80% | ~20% | 80%+ |

Root causes identified:
1. **Missing files**: `task_generator.py` caused ImportError, blocking auto-task creation
2. **Broken CLI**: Context CLI missing `--level` and `--part` arguments
3. **Not wired**: Error recording functions existed but weren't called from error paths
4. **Not initialized**: Telemetry service implemented but not registered at startup
5. **Disabled by default**: OpenMemory MCP and telemetry disabled in config

## Decision

Activate all dormant infrastructure through a phased remediation:

### Phase 1: Create Missing Files
- `tools/overseer/issues/task_generator.py` - Auto-generate task briefs from issues
- `tools/context/config/roles/debug-agent.json` - Debug Agent context profile
- `docs/developer/OVERSEER_ISSUE_SYSTEM.md` - Issue system documentation

### Phase 2: Fix CLI Arguments
- Add `--level` and `--part` arguments to context CLI

### Phase 3: Fix Verification Encoding
- UTF-8 encoding in `completion_guard.py` subprocess calls
- Integrate `boundary_checker` into verification
- Add `validator_workflow` to CI

### Phase 4: Initialize Telemetry
- JSON logging via `VOICESTUDIO_JSON_LOGGING` env var
- Telemetry middleware via `VOICESTUDIO_TELEMETRY` env var
- `/api/telemetry` routes for metrics and SLOs

### Phase 5: Wire Issue Recording
- `record_backend_error()` in `error_handling.py`
- `record_engine_error()` in `runtime_engine_enhanced.py`
- `record_build_error()` in `run_verification.py`

### Phase 6: Enable OpenMemory MCP
- Set `mcp_enabled: true` in `context-sources.json`
- Set `offline: false` for memory adapter

### Phase 7: Formalize Onboarding Config
- Create `tools/onboarding/config/onboarding.json`
- Create `tools/onboarding/config/roles.json` with role registry

## Consequences

### Positive
- Issue system will automatically track backend/engine/build errors
- Telemetry data available for SLO monitoring and debugging
- Context CLI usable for standalone context allocation
- Memory search uses MCP when server is available
- Onboarding packets configurable via JSON
- Debug Agent role fully functional with context profile

### Negative
- Additional environment variables needed to enable features
- Slight performance overhead from issue recording (mitigated by try/except)
- MCP memory requires external server (falls back to file if unavailable)

### Neutral
- Agent governance modules remain dormant (separate ADR needed for activation)
- Advanced automation (reflexion_loop.py, auto_verify.py) deferred

## Verification

- [ ] `python -c "from tools.overseer.issues.task_generator import IssueToTaskGenerator"` succeeds
- [ ] `python -m tools.context.cli.allocate --role debug-agent --level mid` exits 0
- [ ] `python scripts/run_verification.py` passes all checks
- [ ] Backend starts with `VOICESTUDIO_JSON_LOGGING=1` and logs JSON
- [ ] `/api/telemetry/metrics` returns 200
- [ ] Simulated backend error creates issue in `~/.voicestudio/issues/`

## Related ADRs

- ADR-003: Agent Governance Framework (role system)
- ADR-015: Architecture Integration Contract
- ADR-024: Completion Evidence Guard
- ADR-025: Compatibility Matrix and Scaffolding
