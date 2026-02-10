# Change Control Rules

> **Version**: 1.0.0  
> **Last Updated**: 2026-02-09  
> **Status**: ACTIVE  
> **Owner**: Overseer (Role 0)

---

## Purpose

This document establishes **non-negotiable change control rules** that prevent regressions and ensure every change is proven before merge. These rules apply to all agents and developers working on VoiceStudio.

**The Problem This Solves:**
- "Fix 1 thing, break 5 things" cycle
- Undetected regressions shipping to production
- Agents making "helpful" changes that cause collateral damage
- No machine-enforced gate preventing broken code from merging

---

## The Golden Rule

> **No changes allowed unless `scripts/verify.ps1` stays GREEN.**

This is the single most important rule. It is non-negotiable.

```powershell
# Before ANY merge, run:
.\scripts\verify.ps1

# Exit code MUST be 0
# If exit code is non-zero, the merge is BLOCKED
```

---

## Non-Negotiable Rules

### Rule 1: Verification Gate

Every change must pass the unified verification harness:

```powershell
.\scripts\verify.ps1  # Full verification
.\scripts\verify.ps1 -Quick  # Quick pre-commit check
```

**What it checks:**
1. C# solution builds cleanly
2. Python code passes lint and type checks
3. C# unit tests pass
4. Python unit tests pass
5. Contract tests pass (C# ↔ Python)
6. Backend integration tests pass
7. UI smoke tests pass
8. Gate/ledger validation passes

**Enforcement:**
- CI blocks merge on verification failure
- Pre-commit hook runs quick verification
- Agents must run verification before claiming task complete

### Rule 2: No Sweeping Refactors During Stabilization

During stabilization periods (red gates, release prep, incident response):

| Allowed | Prohibited |
|---------|------------|
| Bug fixes with minimal diff | Sweeping refactors |
| Targeted file changes | "Cleanup" passes |
| Adding regression tests | Reorganizing folders |
| Documentation updates | Renaming symbols across codebase |
| Security patches | Formatting-only changes |

**Why:** Sweeping changes introduce risk and make it impossible to identify which change caused a regression.

### Rule 3: Every Fix Must Include Proof

A fix is not complete without:

1. **Bug reproduction** - A failing test or script that reproduces the issue
2. **The fix** - Minimal code change that addresses the root cause
3. **Proof** - `verify.ps1` runs green after the fix

**Format:**
```markdown
## Fix Proof

**Issue:** [Description]
**Reproduction:** [Test name or steps]
**Fix:** [Files changed and why]
**Verification:**
- [ ] verify.ps1 exit code: 0
- [ ] Regression test added: [test name]
```

### Rule 4: Blast Radius Limits

Changes are limited to prevent collateral damage:

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| Files changed per fix | ≤ 5 | Soft limit, requires justification |
| Files changed per fix | ≤ 10 | Hard limit, requires Overseer approval |
| Lines changed | ≤ 200 | Soft limit, consider splitting |
| Cross-boundary changes | Requires ADR | UI + Backend + Engine = split into tasks |

**Exception process:**
1. Document why the limit must be exceeded
2. Get Overseer approval
3. Add extra regression tests
4. Run full verification twice (before and after)

### Rule 5: No Silent Changes

Every edit must have a stated reason:

**Prohibited:**
- Silent "cleanup" during other work
- Reformatting files you're not fixing
- Renaming variables "for consistency"
- Adding dependencies without documentation

**Required:**
- Clear commit message explaining the change
- Link to ledger entry (VS-XXXX) if fixing an issue
- Explicit note if changing files beyond the primary fix

---

## Cursor Agent Operating Protocol

When operating as a Cursor agent on VoiceStudio, paste this protocol:

```markdown
## VoiceStudio Stabilization Protocol

You are not allowed to make any change unless `scripts/verify.ps1` stays GREEN.

### Pre-Change Checklist
Before making any code change:
1. Run `.\scripts\verify.ps1 -Quick` to establish baseline
2. Confirm current state is GREEN
3. If RED, fix existing issues first

### During Changes
- Make minimal, localized edits
- Do NOT refactor unrelated code
- Do NOT rename symbols
- Do NOT reformat files you're not fixing
- If more than 5 files need changes, STOP and explain

### Post-Change Checklist
After every change:
1. Run `.\scripts\verify.ps1`
2. If RED, fix the issue you introduced
3. If still RED after 2 attempts, revert and try different approach
4. Do NOT claim task complete until GREEN

### Prohibited Actions
- Sweeping refactors
- "Cleanup" passes
- Formatting-only changes
- Adding dependencies without documentation
- Changing build configuration without approval
- Modifying test infrastructure without approval

### If You Break Something
1. STOP immediately
2. Identify what broke (check verify.ps1 output)
3. Fix the specific issue
4. Run verify.ps1 again
5. If you can't fix it, REVERT and explain
```

---

## Stabilization Mode

When the project enters stabilization mode (triggered by Overseer):

### Entering Stabilization

```markdown
## Stabilization Active

**Started:** [date]
**Reason:** [reason]
**Exit Criteria:** verify.ps1 green for 3 consecutive runs

During stabilization:
- Work only on `stabilize/*` branches
- No feature work until exit criteria met
- Only small, localized fixes allowed
- Every fix requires Overseer approval
```

### Stabilization Restrictions

| Category | Status |
|----------|--------|
| New features | ❌ BLOCKED |
| Refactors | ❌ BLOCKED |
| Dependency updates | ❌ BLOCKED |
| Bug fixes | ✅ Allowed (with approval) |
| Security patches | ✅ Allowed (expedited) |
| Test fixes | ✅ Allowed (with approval) |
| Documentation | ✅ Allowed |

### Exiting Stabilization

Stabilization ends when:
1. `verify.ps1` passes 3 consecutive times
2. All S0/S1 blockers resolved
3. Overseer approves exit

---

## Scope Limiters

Use these scope limiters in Cursor prompts to prevent collateral damage:

### File Scope
```
Only edit these files: [list specific files]
Do not touch anything else.
```

### Pattern Scope
```
Only modify code matching this pattern: [pattern]
Do not change other occurrences.
```

### Layer Scope
```
Only work in the [UI/Backend/Engine] layer.
Do not cross boundaries without explicit approval.
```

### Change Type Scope
```
Only make these types of changes:
- Bug fixes in [specific area]
- Test additions for [specific feature]

Do NOT:
- Refactor anything
- Rename anything
- Reformat anything
```

---

## Enforcement Mechanisms

### Automated Enforcement

| Mechanism | Location | What It Checks |
|-----------|----------|----------------|
| Pre-commit hook | `.git/hooks/pre-commit` | Quick verification |
| CI gate | `.github/workflows/build.yml` | Full verification |
| PR check | `.github/workflows/test.yml` | All test suites |

### Manual Enforcement

| Checkpoint | Who | What They Check |
|------------|-----|-----------------|
| Task closure | Skeptical Validator | Proof artifacts exist |
| PR approval | Overseer | verify.ps1 green, scope appropriate |
| Gate transition | Overseer | All evidence collected |

---

## Violation Response

### Minor Violation
- **Definition:** Small scope creep, missing proof
- **Response:** Fix immediately, document in task notes
- **Escalation:** None if fixed promptly

### Moderate Violation
- **Definition:** Broke verify.ps1, exceeded file limit
- **Response:** Revert changes, split into smaller tasks
- **Escalation:** Notify Overseer, require approval for next changes

### Critical Violation
- **Definition:** Merged broken code, systematic rule ignorance
- **Response:** Immediate revert, stabilization mode triggered
- **Escalation:** Full stop, post-incident review required

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHANGE CONTROL CHECKLIST                     │
├─────────────────────────────────────────────────────────────────┤
│ Before changing code:                                           │
│   [ ] verify.ps1 -Quick is GREEN                                │
│   [ ] Change scope is ≤5 files                                  │
│   [ ] No refactors, renames, or reformatting                    │
│                                                                 │
│ After changing code:                                            │
│   [ ] verify.ps1 is GREEN                                       │
│   [ ] Regression test added (if bug fix)                        │
│   [ ] Commit message explains the change                        │
│                                                                 │
│ Before claiming complete:                                       │
│   [ ] All verification stages pass                              │
│   [ ] Proof documented in task/ledger                           │
│   [ ] No unintended changes in diff                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## CI Integration

The CI workflows should align with `verify.ps1`:

| CI Workflow | Status | Notes |
|-------------|--------|-------|
| `.github/workflows/build.yml` | Aligned | C# build mirrors Stage 1 |
| `.github/workflows/test.yml` | Aligned | Python/C# tests mirror Stages 3-4 |
| `.github/workflows/governance.yml` | Aligned | Gate checks mirror Stage 8 |

**To enable local parity with CI:**

```powershell
# Local verification = CI verification
.\scripts\verify.ps1 -Configuration Release
```

**Pre-commit hook integration:**

```bash
# Enable quick verification in pre-commit
export VOICESTUDIO_QUICK_VERIFY=1
git commit -m "your message"
```

---

## Related Documents

- [verify.ps1](../../scripts/verify.ps1) - Unified verification harness
- [ADR-027](../architecture/decisions/ADR-027-unified-verification-harness.md) - Architecture decision
- [verification-harness.mdc](../../.cursor/rules/workflows/verification-harness.mdc) - Agent rule
- [error-resolution.mdc](../../.cursor/rules/workflows/error-resolution.mdc) - Error handling
- [closure-protocol.mdc](../../.cursor/rules/workflows/closure-protocol.mdc) - Task closure
- [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) - Quality standards
