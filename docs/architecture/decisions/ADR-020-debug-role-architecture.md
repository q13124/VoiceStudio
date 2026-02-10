# ADR-020: Debug Role Architecture

## Status

**Accepted** - 2026-02-10

## Context

VoiceStudio requires a dedicated debugging capability for systematic issue diagnosis. The Debug Agent (Role 7) needs a well-defined architecture for:

1. Receiving handoffs from other roles when issues arise
2. Systematic error investigation using audit logs, stack traces, and context
3. Root cause analysis with actionable fix recommendations
4. Integration with the Quality Ledger and Issue Store

## Options Considered

### Option A: Ad-hoc Debugging

Each role handles its own debugging.

- **Pros**: Simple, no new infrastructure needed
- **Cons**: Inconsistent approaches, no audit trail, knowledge silos

### Option B: Centralized Debug Agent

A dedicated role with specialized tooling and workflows.

- **Pros**: Consistent methodology, audit trail, specialized expertise, knowledge accumulation
- **Cons**: Handoff overhead, requires clear escalation paths

### Option C: Hybrid Approach

Roles handle simple issues, escalate complex issues to Debug Agent.

- **Pros**: Balances efficiency with expertise
- **Cons**: Requires clear severity classification

## Decision

Adopt **Option C: Hybrid Approach** with the following architecture:

### Components

1. **AuditLogger** (`tools/overseer/audit_logger.py`)
   - Records file changes, build events, exceptions, and decisions
   - Categories: FILE_CHANGE, BUILD, ERROR, EXCEPTION, DEBUG, DECISION

2. **IssueStore** (`tools/overseer/issues/issue_store.py`)
   - JSONL-based persistent issue tracking
   - Auto-creation from audit events via AuditIssueBridge

3. **HandoffQueue** (`tools/context/handoffs/handoff_queue.py`)
   - Role-to-role handoff with context preservation
   - Priority-based queue for Debug Agent workload

4. **DebugRoleNotifier** (`tools/debug/notifier.py`)
   - Routes CRITICAL/HIGH severity issues to Debug Agent
   - Categories: ERROR, EXCEPTION, DEBUG, CRASH, DIAGNOSTIC

### Workflow

1. Error occurs during role execution
2. AuditLogger records event
3. AuditIssueBridge creates issue if severity >= ERROR
4. DebugRoleNotifier checks severity:
   - CRITICAL/HIGH: Auto-handoff to Debug Agent
   - MEDIUM/LOW: Record in Issue Store, owner fixes

### Context Allocation

The Context Manager allocates the `audit` source to Debug Agent:
- Priority weight: 0.95 (highest among roles)
- Budget: 2500 characters
- Includes recent errors, warnings, build failures

## Consequences

### Positive

- Systematic issue diagnosis across the codebase
- Audit trail of all debugging activities
- Accumulated knowledge in Issue Store
- Clear escalation path prevents issues from falling through cracks

### Negative

- Handoff overhead for simple issues
- Requires maintaining debug infrastructure
- Context switching between roles

### Implementation Evidence

- Role guide: `docs/governance/roles/ROLE_7_DEBUG_AGENT_GUIDE.md`
- Prompt: `.cursor/prompts/ROLE_7_DEBUG_AGENT_PROMPT.md`
- Skill: `.cursor/skills/roles/debug-agent/SKILL.md`
- Audit infrastructure: `tools/overseer/audit_logger.py`

## Related ADRs

- ADR-003: Agent Governance Framework
- ADR-011: Context Manager Architecture
