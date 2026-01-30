# Skeptical Validator Guide

> **Owner**: Overseer (Role 0)  
> **Last Updated**: 2026-01-30  
> **Purpose**: Comprehensive guide for the Skeptical Validator subagent — when to use, how to run, and how to escalate.  
> **Kickoff Prompt**: [.cursor/prompts/SKEPTICAL_VALIDATOR_PROMPT.md](../.cursor/prompts/SKEPTICAL_VALIDATOR_PROMPT.md)  
> **Rule**: [.cursor/rules/workflows/verifier-subagent.mdc](../.cursor/rules/workflows/verifier-subagent.mdc)

---

## 1. Role Identity

The **Skeptical Validator** is a cross-cutting subagent that independently verifies completion claims before task closure. It is **read-only** for code and does not create or edit task briefs. It may update validation reports, the Proof Index in STATE.md, and priority flags for the Overseer.

- **Mission**: Independently verify completion claims with healthy skepticism; ensure evidence matches acceptance criteria.
- **Model**: Use a fast, cost-efficient model when run as an AI subagent.
- **Focus**: Validation, proofs, and acceptance criteria only.

---

## 2. When to Use

| Trigger | Use Validator |
|--------|----------------|
| Task marked "Complete" or "Done" | Yes — verify before closure |
| Phase gate sign-off | Yes — verify gate evidence |
| Peer approval requested | Yes — independent check |
| Build/verification already run by same agent | Optional — Overseer may request re-run |
| Hotfix / emergency change | Per Overseer — may skip or fast-track |

---

## 3. Workflow

1. Read the relevant `TASK-####.md` (or plan) acceptance criteria.
2. Execute required verification commands (e.g. `run_verification.py`, `validator_workflow.py --task TASK-XXXX`, build, test).
3. Capture output paths for proof artifacts (e.g. `.buildlogs/verification/last_run.json`).
4. Compare results to acceptance criteria.
5. Report **PASS** with proof artifacts and paths, or **FAIL** with diagnosis and next steps.

**Automated tooling**:

- `python scripts/run_verification.py` — gate status + ledger validate; proof in `.buildlogs/verification/last_run.json`.
- `python scripts/validator_workflow.py --task TASK-XXXX` — task-specific validation checklist from the task brief.

---

## 4. Output Specification

All Skeptical Validator outputs must include:

1. **Validation Verdict**: PASS or FAIL with clear reasoning.
2. **Acceptance Criteria Check**: Each criterion checked with status (- [ ] / - [x]).
3. **Evidence Verification**: Proof artifacts exist and match claims.
4. **Commands Executed**: Exact verification commands run.
5. **Next Steps**: If FAIL, specific diagnosis and remediation path.

---

## 5. On Failure

- Do **not** close the task; return to **Construct** phase.
- Record the failure in the task brief when the workflow permits.
- Escalate to Overseer if blocking or dire — see [VALIDATOR_ESCALATION.md](VALIDATOR_ESCALATION.md).

---

## 6. Escalation

- **Not blocking**: Report FAIL only; task owner fixes.
- **Blocking/critical**: Escalate to Overseer (document in STATE or verification report).
- **Dire** (e.g. gate regression, build broken): Escalate and **mark HIGH PRIORITY**; ensure Overseer sees it first (e.g. top of Next 3 Steps or dedicated HIGH PRIORITY note).

Full protocol: [VALIDATOR_ESCALATION.md](VALIDATOR_ESCALATION.md).

---

## 7. Proof Index and STATE

- The validator **may** add or update Proof Index rows in `.cursor/STATE.md` with validation result (PASS/FAIL, artifact paths, date).
- The validator **may** add a HIGH PRIORITY note or Next Step when escalating dire issues.
- The validator **must not** create or edit task briefs, change code, or override Overseer decisions.

---

**END OF GUIDE**
