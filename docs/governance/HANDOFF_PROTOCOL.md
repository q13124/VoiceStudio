# Cross-Role Handoff Protocol

**Version**: 1.0  
**Date**: 2026-01-29  
**Purpose**: Standardized protocol for issue escalation and cross-role handoffs  
**Related**: [CROSS_ROLE_ESCALATION_MATRIX.md](CROSS_ROLE_ESCALATION_MATRIX.md), ADR-017

---

## Overview

This protocol defines the standard process for handing off issues, tasks, or investigations between roles to ensure continuity, clarity, and accountability.

---

## When to Create a Handoff

| Trigger | Action |
|---------|--------|
| Issue exceeds role scope | Handoff to Debug Agent or specialist |
| Root-cause identified, fix needs specialist | Handoff to owner role with diagnosis |
| S0 blocker needs executive action | Escalate to Overseer |
| Architecture decision needed | Handoff to System Architect |
| Cross-layer issue diagnosed | Handoff from Debug Agent to specialist |

---

## Handoff Document Template

All handoffs must use this format:

```markdown
# Handoff: <Issue ID> → <Target Role>

**From**: <Source Role>  
**To**: <Target Role>  
**Date**: <YYYY-MM-DD>  
**Issue ID**: <UUID from Issue Store>  
**Severity**: S0/S1/S2/S3  
**Status**: NEW/ACKNOWLEDGED/IN_PROGRESS

---

## Context

<Brief description of the issue and why handoff is needed>

## What Was Attempted

<List all troubleshooting steps, diagnostics run, and fixes attempted>

## Diagnosis Summary

<What is known about the issue>
- **Root Cause**: <If determined>
- **Affected Components**: <List>
- **Reproduction Steps**: <If available>

## Expected Outcome

<What the target role should deliver>

## Artifacts

- **Issue JSONL**: `.overseer_issues/<date>/<id>.jsonl`
- **Logs**: <paths to relevant log files>
- **Reproduction**: <script path or manual steps>
- **Related Commits**: <if any>
- **Proof Runs**: <if any>

## Acceptance Criteria

- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] Evidence captured in ledger/STATE

---

## Handoff Checklist

- [ ] Issue logged in Issue Store
- [ ] Severity set appropriately
- [ ] Diagnosis section completed
- [ ] Reproduction steps documented
- [ ] Artifacts referenced
- [ ] Target role identified
- [ ] Handoff queue updated (if applicable)
```

---

## Handoff Queue System

### Queue Locations

Per-role handoff queues (JSONL format):
- `.cursor/handoff_queues/role_0_queue.jsonl` (Overseer)
- `.cursor/handoff_queues/role_1_queue.jsonl` (System Architect)
- `.cursor/handoff_queues/role_2_queue.jsonl` (Build & Tooling)
- `.cursor/handoff_queues/role_3_queue.jsonl` (UI Engineer)
- `.cursor/handoff_queues/role_4_queue.jsonl` (Core Platform)
- `.cursor/handoff_queues/role_5_queue.jsonl` (Engine Engineer)
- `.cursor/handoff_queues/role_6_queue.jsonl` (Release Engineer)
- `.cursor/handoff_queues/role_7_queue.jsonl` (Debug Agent)

### Queue Entry Format

```json
{
  "handoff_id": "<uuid>",
  "issue_id": "<uuid>",
  "from_role": "<role-id>",
  "to_role": "<role-id>",
  "severity": "S0|S1|S2|S3",
  "status": "PENDING|ACKNOWLEDGED|IN_PROGRESS|RESOLVED|REJECTED",
  "created_at": "ISO8601",
  "acknowledged_at": "ISO8601|null",
  "message": "<brief summary>",
  "artifacts": ["<path1>", "<path2>"]
}
```

### CLI Commands

```bash
# View queue for a role
python -m tools.overseer.cli.main handoff show --role <role-id>

# Create handoff
python -m tools.overseer.cli.main handoff create \
  --from <source-role> \
  --to <target-role> \
  --issue <issue-id> \
  --message "Brief summary"

# Acknowledge handoff (when receiving)
python -m tools.overseer.cli.main handoff acknowledge <handoff-id>

# Mark handoff resolved
python -m tools.overseer.cli.main handoff resolve <handoff-id> --evidence <path>
```

---

## Common Handoff Patterns

### Pattern 1: Unclear Root Cause → Debug Agent

**Trigger**: Any role encounters issue with unclear diagnosis.

**Process**:
1. Role logs issue with `instance_type` matching their domain
2. Role escalates to Debug Agent: `debug analyze <issue-id>`
3. Debug Agent diagnoses and determines owner
4. Debug Agent hands off to specialist with diagnosis

**Example**:
- UI Engineer sees binding failure but ViewModel looks correct
- Escalates to Debug Agent for cross-layer diagnosis
- Debug Agent finds backend contract mismatch
- Debug Agent hands off to Core Platform with root-cause

### Pattern 2: Diagnosed Issue → Specialist

**Trigger**: Debug Agent completes diagnosis.

**Process**:
1. Debug Agent creates handoff document
2. Debug Agent adds to target role's handoff queue
3. Target role acknowledges and fixes
4. Target role marks resolved with evidence

**Example**:
- Debug Agent diagnoses XAML runtime crash (null reference in ViewModel)
- Hands off to UI Engineer with specific line number
- UI Engineer fixes and validates
- UI Engineer marks resolved with build proof

### Pattern 3: S0 Blocker → Overseer

**Trigger**: Any role encounters S0 severity blocker.

**Process**:
1. Role logs issue with severity S0
2. Auto-escalation to Overseer (via `state_integration.py`)
3. Overseer reviews and assigns urgency
4. Overseer may delegate diagnosis to Debug Agent
5. Overseer tracks to closure

**Example**:
- Build fails completely (exit code 1) with no clear error
- Build & Tooling logs as S0, auto-escalates to Overseer
- Overseer assigns to Debug Agent for diagnosis
- Debug Agent identifies file lock issue
- Debug Agent hands back to Build & Tooling with fix

### Pattern 4: Cross-Role Coordination → Overseer

**Trigger**: Fix requires changes across multiple roles.

**Process**:
1. Identifying role escalates to Overseer
2. Overseer creates coordination plan
3. Overseer assigns sub-tasks to multiple roles
4. Roles complete in sequence or parallel
5. Overseer validates integration

**Example**:
- Contract change affects UI, Backend, and Engine
- System Architect escalates to Overseer
- Overseer coordinates: Architect (ADR) → Platform (backend) → UI (client) → Engine (adapter)
- Each role completes their part with proof
- Overseer validates end-to-end

---

## Handoff Quality Checklist

Before creating a handoff, ensure:

- [ ] Issue is logged in Issue Store (`.overseer_issues/`)
- [ ] Severity is set correctly (S0-S3)
- [ ] Reproduction steps are documented (script or manual)
- [ ] What was attempted is listed (avoid duplicate work)
- [ ] Expected outcome is clear
- [ ] Artifacts are referenced (logs, proof runs, commits)
- [ ] Target role is correct per escalation matrix
- [ ] Handoff document created (see template above)

---

## Handoff Response Protocol

### When Receiving a Handoff

1. **Acknowledge within 4 hours**: Update handoff status to ACKNOWLEDGED
2. **Review diagnosis**: Read all artifacts and context
3. **Plan approach**: Define steps to resolve
4. **Execute**: Implement fix with proof
5. **Validate**: Run regression tests
6. **Document**: Update issue with resolution
7. **Resolve**: Mark handoff RESOLVED with evidence path

### When Rejecting a Handoff

If handoff is incorrect (wrong role, incomplete diagnosis, etc.):

1. Update handoff status to REJECTED
2. Add rejection reason to handoff entry
3. Return to source role or escalate to Overseer
4. Do NOT attempt fix if handoff is incorrect

---

## Integration with Issue System

### Issue Store

All issues referenced in handoffs must exist in:
- **Location**: `.overseer_issues/<YYYY-MM-DD>/<issue-id>.jsonl`
- **Format**: JSONL with instance_type, severity, status, message, context
- **Managed by**: `tools/overseer/issues/store.py`

### Automatic Escalation Rules

Issues are auto-escalated based on:

| Condition | Target | Implementation |
|-----------|--------|----------------|
| Severity S0 (blocker) | Overseer (Role 0) | `tools/overseer/issues/escalation.py` |
| Recurring issue (≥3 occurrences) | Debug Agent (Role 7) | `tools/overseer/issues/debug_workflow.py` |
| Cross-layer instance type | Debug Agent (Role 7) | `tools/overseer/issues/escalation.py` |

See `tools/overseer/issues/escalation.py` (`auto_escalate_if_needed()`) for implementation.

---

## STATE.md Integration

### Overseer Queue

Critical escalations appear in `.cursor/STATE.md` Overseer Queue:

```markdown
## Overseer Queue / Validator Escalations

| Date | Task / Source | Summary | Priority |
|------|----------------|---------|----------|
| 2026-01-29 | ISSUE-abc123 | Build failure blocking Gate B | HIGH PRIORITY |
```

**Managed by**: `tools/overseer/issues/state_integration.py`

**Commands**:
```bash
# Add to Overseer Queue
python -m tools.overseer.cli.main issues escalate-overseer <issue-id>

# View Overseer Queue
python -m tools.overseer.cli.main issues query --owner overseer
```

---

## Example Handoff Documents

### Example 1: Debug Agent → UI Engineer

```markdown
# Handoff: 422debc7 → UI Engineer (Role 3)

**From**: Debug Agent (Role 7)  
**To**: UI Engineer (Role 3)  
**Date**: 2026-01-29  
**Issue ID**: 422debc7-96e5-4c30-bb97-22ca7be92470  
**Severity**: S2  
**Status**: ACKNOWLEDGED

---

## Context

ProfilesView binding failures with "Cannot find source" errors. Multiple panels affected (6 similar occurrences).

## What Was Attempted

- Verified ViewModel properties exist and are public
- Checked x:Bind vs Binding syntax
- Reviewed DataContext setting in View constructor

## Diagnosis Summary

- **Root Cause**: ViewModel properties use snake_case naming but x:Bind expects PascalCase (C# convention)
- **Affected Components**: ProfilesView, SettingsView, VoiceSynthesisView, AudioLibraryView (+ 2 more)
- **Reproduction Steps**: Open any affected panel; binding errors appear in debug output

## Expected Outcome

Rename ViewModel properties to PascalCase or update x:Bind paths to match snake_case (prefer PascalCase for C# convention).

## Artifacts

- **Issue JSONL**: `.overseer_issues/2026-01-29/422debc7-96e5-4c30-bb97-22ca7be92470.jsonl`
- **Debug output**: Captured in issue context
- **Affected files**: Listed in issue `affected_files` field

## Acceptance Criteria

- [ ] All 6 affected Views compile without binding warnings
- [ ] Debug output shows no "Cannot find source" errors
- [ ] UI smoke test passes (11 nav steps, 0 binding failures)
```

---

## Reference

- **Escalation Matrix**: [CROSS_ROLE_ESCALATION_MATRIX.md](CROSS_ROLE_ESCALATION_MATRIX.md)
- **Debug Agent Guide**: [roles/ROLE_7_DEBUG_AGENT_GUIDE.md](roles/ROLE_7_DEBUG_AGENT_GUIDE.md)
- **Issue System**: `tools/overseer/issues/` (store, escalation, handoff)
- **CLI Reference**: `python -m tools.overseer.cli.main handoff --help`
