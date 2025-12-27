# Overseer Task Verification System
## Complete Work Review and Rule Compliance Verification

**Date:** 2025-01-28  
**Status:** ✅ **ACTIVE**  
**Purpose:** Ensure 100% rule compliance through comprehensive work review

---

## 🚨 CRITICAL REQUIREMENT

**When ANY worker marks a task as "completed", the Overseer MUST:**

1. ✅ **Read the ENTIRE body of work** - Not just check the checkbox
2. ✅ **Verify 100% rule compliance** - Check ALL rules, not just some
3. ✅ **Review ALL files changed/created** - Every file, every line
4. ✅ **Check for forbidden terms** - ALL synonyms and variations
5. ✅ **Verify functionality** - Code must actually work
6. ✅ **Check integration quality** - Properly integrated, not just added
7. ✅ **Verify UI compliance** - If UI task, check exact ChatGPT specification
8. ✅ **Refresh rules before review** - Re-read MASTER_RULES_COMPLETE.md

**NO EXCEPTIONS. NO SHORTCUTS. NO "GOOD ENOUGH".**

---

## 📋 Verification Process

### Step 1: Pre-Review Preparation

**Before reviewing ANY completed task:**

1. **Refresh Rules:**
   - Read `docs/governance/MASTER_RULES_COMPLETE.md` completely
   - Review all forbidden terms and variations
   - Review UI design rules
   - Review integration rules
   - Review code quality rules

2. **Identify Work Scope:**
   - What files were created/modified?
   - What functionality was implemented?
   - What dependencies were added?
   - What tests were created?

3. **Prepare Verification Checklist:**
   - Rule compliance checklist
   - Functionality checklist
   - Integration checklist
   - UI compliance checklist (if applicable)

---

### Step 2: Comprehensive Work Review

**For EACH file created or modified:**

1. **Read the ENTIRE file:**
   - Not just snippets
   - Not just the changed lines
   - The COMPLETE file from start to finish

2. **Check for Forbidden Terms:**
   - Search for ALL bookmark synonyms (TODO, FIXME, NOTE, HACK, etc.)
   - Search for ALL placeholder synonyms (dummy, mock, fake, sample, etc.)
   - Search for ALL stub synonyms (skeleton, template, pass, etc.)
   - Search for ALL status words (pending, incomplete, unfinished, etc.)
   - Search for ALL forbidden phrases ("to be done", "will be implemented", etc.)
   - Check for loophole attempts (capitalization, spacing, punctuation variations)

3. **Verify Functionality:**
   - Code must actually work (not just exist)
   - All functions have real implementations
   - No NotImplementedError/NotImplementedException
   - No empty returns (return {}, return [], return null)
   - Error handling is complete
   - Edge cases are handled

4. **Check Integration Quality:**
   - Properly integrated into existing codebase
   - Follows project structure
   - Uses correct imports
   - Matches existing patterns
   - No breaking changes

5. **Verify UI Compliance (if UI task):**
   - 3-row grid structure maintained
   - 4 PanelHosts used (not raw Grid)
   - VSQ.* design tokens used (no hardcoded values)
   - MVVM separation maintained
   - ChatGPT UI specification followed exactly

---

### Step 3: Rule Violation Detection

**If ANY violation is found:**

1. **Document the Violation:**
   - Which file?
   - Which line(s)?
   - What violation?
   - What rule was broken?

2. **Create Fix Task:**
   - Create new task for the worker
   - Task ID: `TASK-W[X]-FIX-[NUMBER]`
   - Task name: "Fix rule violations in [task name]"
   - Task description: Detailed list of violations found
   - Assign to the worker who completed the original task

3. **Reject the Original Task:**
   - Mark original task as "rejected" or "needs_fix"
   - Add note: "Rule violations found. See TASK-W[X]-FIX-[NUMBER]"

4. **Notify Worker:**
   - Document findings clearly
   - List all violations
   - Provide specific file locations and line numbers
   - Explain what needs to be fixed

---

### Step 4: Verification Checklist

**Before approving ANY task, verify:**

#### Rule Compliance
- [ ] Worker has read `MASTER_RULES_COMPLETE.md`
- [ ] No forbidden bookmarks (including ALL synonyms)
- [ ] No forbidden placeholders (including ALL synonyms)
- [ ] No forbidden stubs (including ALL synonyms)
- [ ] No forbidden tags (including ALL categories)
- [ ] No forbidden status words (including ALL synonyms)
- [ ] No forbidden phrases (including ALL variations)
- [ ] No loophole attempts (capitalization, spacing, punctuation, etc.)

#### Functionality
- [ ] Code actually works (not just exists)
- [ ] All functionality implemented
- [ ] All error cases handled
- [ ] All edge cases considered
- [ ] No NotImplementedError/NotImplementedException
- [ ] No empty returns (return {}, return [], return null)
- [ ] Production-ready quality

#### Integration Quality
- [ ] Properly integrated into codebase
- [ ] Follows project structure
- [ ] Uses correct imports
- [ ] Matches existing patterns
- [ ] No breaking changes
- [ ] Dependencies properly installed

#### UI Compliance (if UI task)
- [ ] 3-row grid structure maintained
- [ ] 4 PanelHosts used (not raw Grid)
- [ ] VSQ.* design tokens used (no hardcoded values)
- [ ] MVVM separation maintained
- [ ] ChatGPT UI specification followed exactly

#### Documentation (if applicable)
- [ ] Documentation is complete
- [ ] No placeholders in documentation
- [ ] Examples are real (not dummy data)
- [ ] All sections filled in

---

## 🔍 Verification Tools

### Automated Checks

**Use these tools to help verify:**

1. **Grep for Forbidden Terms:**
   ```bash
   grep -r "TODO\|FIXME\|PLACEHOLDER\|NotImplemented" [file/directory]
   ```

2. **Check for Empty Returns:**
   ```bash
   grep -r "return {}\|return []\|return null" [file/directory]
   ```

3. **Check for NotImplementedError:**
   ```bash
   grep -r "NotImplementedError\|NotImplementedException" [file/directory]
   ```

### Manual Review

**For each file:**
1. Read the entire file
2. Check every function/method
3. Check every comment
4. Check every return statement
5. Verify all imports work
6. Verify all functionality is real

---

## 📝 Verification Report Template

**When reviewing a completed task, create a report:**

```markdown
# Task Verification Report
## [Task ID]: [Task Name]

**Worker:** [Worker Number]  
**Date:** [Date]  
**Status:** ✅ APPROVED / ❌ REJECTED

### Files Reviewed
- [List all files created/modified]

### Rule Compliance Check
- [ ] All rules followed
- [ ] No forbidden terms found
- [ ] No violations detected

### Functionality Check
- [ ] Code works correctly
- [ ] All functionality implemented
- [ ] Error handling complete

### Integration Check
- [ ] Properly integrated
- [ ] Follows project structure
- [ ] No breaking changes

### Violations Found (if any)
1. [File]:[Line] - [Violation description]
2. [File]:[Line] - [Violation description]

### Fix Tasks Created
- TASK-W[X]-FIX-[NUMBER]: [Description]

### Approval Status
✅ APPROVED / ❌ REJECTED - [Reason]
```

---

## 🚨 Violation Remediation

**When violations are found:**

1. **Create Fix Task:**
   - Add to worker's `next_tasks` array
   - Mark original task as "needs_fix"
   - Provide detailed violation list

2. **Worker Must:**
   - Fix ALL violations
   - Re-submit for review
   - Task cannot be marked complete until ALL violations fixed

3. **Overseer Must:**
   - Review fix work again
   - Verify ALL violations are fixed
   - Only approve when 100% compliant

---

## 📊 Verification Schedule

**Verification must happen:**
- ✅ **Immediately** when worker marks task complete
- ✅ **Before** approving any task
- ✅ **After** worker fixes violations
- ✅ **Before** moving to next task

**NO TASK IS APPROVED WITHOUT COMPLETE VERIFICATION.**

---

## ✅ Success Criteria

**A task is only approved when:**
1. ✅ ALL files reviewed completely
2. ✅ ALL rules verified compliant
3. ✅ ALL functionality verified working
4. ✅ ALL integration verified proper
5. ✅ ALL UI compliance verified (if UI task)
6. ✅ NO violations found
7. ✅ NO exceptions made

**100% COMPLIANCE REQUIRED. NO EXCEPTIONS.**

---

**Document Created:** 2025-01-28  
**Status:** ACTIVE - Must be followed for ALL task reviews  
**Priority:** HIGHEST - No task approved without complete verification

