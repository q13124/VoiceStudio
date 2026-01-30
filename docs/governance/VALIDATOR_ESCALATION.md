# Validator Escalation Protocol

> **Owner**: Overseer (Role 0)  
> **Last Updated**: 2026-01-30  
> **Purpose**: When and how the Skeptical Validator escalates to the Overseer; HIGH PRIORITY handling.  
> **Related**: [SKEPTICAL_VALIDATOR_GUIDE.md](SKEPTICAL_VALIDATOR_GUIDE.md), [PROJECT_HANDOFF_GUIDE.md](PROJECT_HANDOFF_GUIDE.md), [.cursor/rules/workflows/verifier-subagent.mdc](../.cursor/rules/workflows/verifier-subagent.mdc)

---

## 1. When to Escalate

| Severity | Condition | Action |
|----------|-----------|--------|
| **None** | Validation PASS or FAIL (non-blocking) | Report only; no escalation |
| **Blocking** | FAIL blocks another task or phase gate | Escalate to Overseer; document in STATE or verification report |
| **Critical** | Build broken, gate regression, evidence missing or fabricated | Escalate and **mark HIGH PRIORITY** |
| **Dire** | Production risk, security, or data integrity concern | Escalate immediately; HIGH PRIORITY; ensure Overseer sees first |

---

## 2. How to Escalate

1. **Document**: Add a clear note in the validation report or STATE.md (e.g. "Validator: FAIL — [reason]. Escalating to Overseer.").
2. **HIGH PRIORITY**: For critical/dire issues, add **HIGH PRIORITY** (or equivalent) so the Overseer queue surfaces it first (e.g. top of Next 3 Steps or a dedicated HIGH PRIORITY section).
3. **Evidence**: Include proof artifact paths, commands run, and exact acceptance criteria that failed.
4. **Next steps**: Suggest concrete remediation (e.g. "Re-run build with -c Release", "Restore X from branch Y").

The Validator **must not** fix code, create tasks, or override Overseer decisions; it only reports and escalates.

---

## 3. Overseer Queue

The Overseer consumes:

- Next 3 Steps and active task in STATE.md.
- HIGH PRIORITY items (from Validator or other roles) at the top of the queue.
- Verification reports and Proof Index updates.

When the Validator marks an item HIGH PRIORITY, the Overseer should address it before other non-priority work.

---

## 4. Triggers (Summary)

- **Gate regression**: Gate B–H was GREEN and is now RED — escalate HIGH PRIORITY.
- **Build broken**: `dotnet build` or verification script fails where it previously passed — escalate HIGH PRIORITY.
- **Evidence fabricated or missing**: Claimed proof artifact does not exist or does not match claim — escalate HIGH PRIORITY.
- **Task closure blocked**: Task cannot be closed because acceptance criteria are not met and owner is stuck — escalate to Overseer (normal priority).

---

**END OF PROTOCOL**
