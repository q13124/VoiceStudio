# Enforcement Quick Reference
## VoiceStudio Quantum+ - Overseer Enforcement Guide

**Date:** 2025-01-28  
**Purpose:** Quick reference for enforcing rules and punishing violations  
**Status:** ✅ **ACTIVE**

---

## 🚨 IMMEDIATE REJECTION PATTERNS

### Automatic REJECT if Found:
- ✅ TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE (ALL synonyms)
- ✅ NotImplementedException, NotImplementedError (unless documented as intentional)
- ✅ Placeholder code, mock outputs, fake responses
- ✅ return {}, return [], return null (without implementation)
- ✅ pass-only stubs, empty functions, skeleton code
- ✅ "pending", "incomplete", "unfinished", "coming soon", "not yet", "eventually", "later", "WIP", "tbd", "tba", "tbc" (ALL synonyms)
- ✅ Merged View/ViewModel files
- ✅ PanelHost replaced with Grid
- ✅ Hardcoded colors, fonts, or spacing (not using DesignTokens)
- ✅ Simplified layout or reduced panel count
- ✅ Missing dependencies (code requires but not installed)
- ✅ Libraries "integrated" but not actually used in code

---

## 🔴 PUNISHMENT PROTOCOL

### Step 1: Detect Violation
```
1. Run verification scripts
2. Check for forbidden terms (ALL synonyms)
3. Check for mock outputs
4. Check for missing dependencies
5. Check for libraries not actually integrated
6. Check UI compliance
```

### Step 2: Immediate Actions
```
1. REJECT work immediately
2. REVERT all violating changes
3. Create violation report: docs/governance/overseer/VIOLATION_REPORT_[DATE].md
4. Document violation details
```

### Step 3: Assign Punishment
```
1. Create TASK-[WORKER]-FIX-[NUMBER]
2. Document violation details
3. Require fix before continuing
4. Add verification requirements
5. Block from new tasks until fixed
```

### Step 4: Escalation (if needed)
```
- Level 1: Minor (first time) - Reject, require fix
- Level 2: Moderate (repeated) - Reject, revert, punishment task
- Level 3: Severe (persistent) - Reject, revert, multiple punishment tasks, block
- Level 4: Critical (UI structure) - Reject, revert, complete rework, block, escalate
```

---

## ✅ QUALITY GATES (Before Approval)

### Gate 1: Rule Compliance
```
- Run: python tools/verify_rules_compliance.py
- Run: python tools/verify_non_mock.py --strict
- Check for ALL forbidden terms (including ALL synonyms)
- Must pass with 0 violations
```

### Gate 2: Functionality
```
- Code must compile/run
- Functionality must work
- Error cases handled
- Edge cases considered
```

### Gate 3: UI Compliance (if UI task)
```
- Verify against ChatGPT specification
- Check design tokens usage
- Verify MVVM separation
- Verify PanelHost structure
- Verify 3-row grid structure
```

### Gate 4: Dependencies
```
- All dependencies installed
- All imports work
- Requirements files updated
- No "module not found" errors
```

### Gate 5: Integration Quality
```
- Libraries actually used in code (not just installed)
- Real functionality (not placeholders)
- Actual code integration (not just installation)
- Verifiable integration (code exists, functions called)
```

---

## 📋 VIOLATION REPORT TEMPLATE

```markdown
# Violation Report - [Date]

**Worker:** [Worker Name]
**Task:** [Task ID]
**Severity:** [Level 1/2/3/4]
**Date:** [Date/Time]

## Violations Detected:
1. [Violation type] - [Details]
2. [Violation type] - [Details]

## Files Affected:
- [File path] - [Violation details]

## Punishment Assigned:
- Task: TASK-[WORKER]-FIX-[NUMBER]
- Actions Required: [List]
- Verification Required: [List]

## Status:
- [ ] Work rejected
- [ ] Changes reverted
- [ ] Punishment task assigned
- [ ] Worker blocked from new tasks
- [ ] Fix in progress
- [ ] Fix verified
```

---

## 🎯 CURRENT PRIORITIES

### Immediate (Fix First):
1. **TASK-W1-FIX-001:** Fix FREE_LIBRARIES_INTEGRATION violations
   - Add all 19 libraries to requirements_engines.txt
   - Actually integrate libraries into codebase
   - Verify all integrations are complete

### Ongoing:
1. Monitor all workers for violations
2. Run quality gates before approval
3. Enforce autonomous workflow
4. Verify dependency installation
5. Verify integration quality

---

## 📊 MONITORING SCHEDULE

### Every 2-4 Hours:
- Quick progress check
- Check for blockers
- Verify workers are progressing

### Every 6-8 Hours:
- Comprehensive review
- Review all worker progress
- Review completed tasks
- Check for violations

### Daily:
- Full status report
- Violation tracking
- Quality gate results
- Next day planning

---

## 🔍 VERIFICATION COMMANDS

### Check for Violations:
```
"Detect violations in [worker/task/file]:
1. Run verification scripts
2. Check for forbidden terms (ALL synonyms)
3. Check for mock outputs
4. Check for missing dependencies
5. Check for libraries not actually integrated
6. Check UI compliance
7. Generate violation report
8. Assign punishment task if violations found"
```

### Run Quality Gates:
```
"Run all quality gates for [task/worker]:
1. Rule Compliance Check
2. Functionality Check
3. UI Compliance Check (if UI task)
4. Dependency Check
5. Integration Quality Check
6. Generate quality gate report
7. Approve or reject based on results"
```

---

## 📝 REMINDERS

- **ZERO TOLERANCE** for violations
- **ALL rules are MANDATORY**
- **Punishment is required** to correct behavior
- **Quality gates** must pass before approval
- **UI specification** is NON-NEGOTIABLE
- **Dependencies** must be installed
- **Libraries** must be actually integrated
- **Workers** must work autonomously
- **Document** all violations and punishments

---

**Use this quick reference for daily enforcement. All violations must be punished to ensure 100% completion.**
