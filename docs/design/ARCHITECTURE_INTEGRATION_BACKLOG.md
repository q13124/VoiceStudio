# Architecture Integration Plan – Phase 4 Backlog

**Source**: [Architecture Integration Review](docs/reports/verification/ARCHITECTURE_INTEGRATION_REVIEW_2026-01-28.md) Phase 4 (R10–R12); see plan in `.cursor/plans/` or the review’s integration plan section.  
**Status**: R10 and R11 implemented; R12 documented as backlog.

---

## R10 – Expand role profile configurations ✅

**Status**: Done.

Role profiles with weights and budgets are defined under `tools/context/config/roles/` for all VoiceStudio roles (overseer, system-architect, build-tooling, ui-engineer, core-platform, engine-engineer, release-engineer, validator). `ContextManager._build_budget()` and config loading use them when `AllocationContext.role` matches.

---

## R11 – Role invocation CLI ✅

**Status**: Done.

- **Command**: `python -m tools.overseer.cli.main role invoke <role_id>`
- **Behavior**: Runs the same onboarding + context flow as the `inject_context` hook: assembles onboarding packet for the role, runs context allocation, prints context preamble to stdout.
- **Options**: `--output PATH` writes the onboarding packet to a file; `--git` includes git context in allocation.
- **List roles**: `python -m tools.overseer.cli.main role list`

Implementation: `tools/overseer/cli/role_cli.py`; wired in `tools/overseer/cli/main.py` under the `role` command.

---

## R12 – Expose skills as MCP tools (backlog)

**Status**: Backlog. Documented as architecture option; not scheduled.

**Scope**: Design and, if adopted, implement an MCP server or tool layer so VoiceStudio role/tool skills can be invoked as MCP tools by Cursor or other MCP clients.

**Design options** (to be decided when implemented):

1. **MCP server**: A small MCP server process that wraps VoiceStudio skills. Tools such as `role_invoke`, `gate_status`, `ledger_validate` map to existing Overseer/onboarding flows. Clients call them via MCP.
2. **Tool bridge**: An adapter in an existing MCP stack that translates tool calls into `tools.overseer.*` or `tools.onboarding.*` invocations (e.g. subprocess or in-process).

**Requirements** (when picked up):

- MCP contract design (tool names, input/output schemas).
- Decide host (new service vs. bridge in existing stack).
- Align with local-first and free-only rules (no required external services).

**References**: Architecture Integration Review §5 (MCP and Skills Integration); ADR-015 (integration contract).

---

## Changelog

| Date       | Change |
|-----------|--------|
| 2026-01-28 | R10, R11 completed; R12 added as backlog. |
