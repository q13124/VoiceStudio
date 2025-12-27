# Overseer Verification Workflow
## Step-by-Step Process for Verifying Completed Tasks

**Date:** 2025-01-28  
**Status:** ✅ **ACTIVE**  
**Purpose:** Detailed workflow for verifying worker task completion

---

## 🔄 Complete Verification Workflow

### Step 1: Detect Task Completion

**Trigger:** Worker marks task as "completed" in progress file

**Actions:**
1. Monitor progress files for status changes
2. Identify newly completed tasks
3. Note which worker completed the task
4. Note task ID and name

---

### Step 2: Refresh Rules (MANDATORY)

**Before reviewing ANY work, you MUST:**

1. **Read Complete Rules:**
   ```
   Read: docs/governance/MASTER_RULES_COMPLETE.md
   - Read from start to finish
   - Review ALL forbidden terms
   - Review ALL synonyms and variations
   - Review UI design rules
   - Review integration rules
   - Review code quality rules
   ```

2. **Review Verification Checklist:**
   ```
   Review: docs/governance/OVerseer_TASK_VERIFICATION_SYSTEM_2025-01-28.md
   - Review complete verification process
   - Review all checkpoints
   - Prepare verification checklist
   ```

**Time Required:** 5-10 minutes  
**Status:** ✅ MANDATORY - Cannot skip this step

---

### Step 3: Identify Work Scope

**Determine what was done:**

1. **Check Task Description:**
   - What was the task supposed to do?
   - What files should have been created/modified?
   - What functionality should have been implemented?

2. **Search for Created/Modified Files:**
   - Search codebase for new files
   - Check git history (if available)
   - Check file modification dates
   - List ALL files related to the task

3. **Document Work Scope:**
   ```
   Task: [Task ID] - [Task Name]
   Worker: [Worker Number]
   Files Created: [List]
   Files Modified: [List]
   Functionality: [Description]
   ```

---

### Step 4: Read Entire Body of Work

**For EACH file created or modified:**

1. **Read Complete File:**
   ```
   File: [file path]
   - Read from line 1 to end
   - Read every function/method
   - Read every class
   - Read every comment
   - Read every import
   - Read every return statement
   ```

2. **Check for Forbidden Terms:**
   ```bash
   # Search for bookmarks
   grep -n "TODO\|FIXME\|NOTE\|HACK\|REMINDER\|XXX" [file]
   
   # Search for placeholders
   grep -n "dummy\|mock\|fake\|sample\|temporary\|placeholder" [file]
   
   # Search for stubs
   grep -n "pass\|NotImplemented\|skeleton\|template\|stub" [file]
   
   # Search for status words
   grep -n "pending\|incomplete\|unfinished\|partial\|will be\|coming soon" [file]
   
   # Search for empty returns
   grep -n "return {}\|return []\|return null" [file]
   ```

3. **Verify Functionality:**
   - Every function has real implementation
   - No NotImplementedError/NotImplementedException
   - No empty returns
   - Error handling is present
   - Edge cases are handled

4. **Check Integration:**
   - Properly integrated into codebase
   - Follows project structure
   - Uses correct imports
   - Matches existing patterns

5. **Check UI Compliance (if UI task):**
   - Read entire XAML file
   - Read entire ViewModel file
   - Read entire code-behind file
   - Verify 3-row grid structure
   - Verify PanelHosts used
   - Verify VSQ.* design tokens
   - Verify MVVM separation

**Time Required:** 15-30 minutes per file  
**Status:** ✅ MANDATORY - Must read every file completely

---

### Step 5: Document Findings

**Create verification report:**

1. **List All Files Reviewed:**
   - File path
   - Lines read
   - Issues found (if any)

2. **List All Violations (if any):**
   - File path
   - Line number
   - Violation type
   - Rule broken
   - What needs to be fixed

3. **List All Issues (if any):**
   - Functionality issues
   - Integration issues
   - UI compliance issues

---

### Step 6: Approve or Reject

**Decision Criteria:**

**✅ APPROVE if:**
- ALL files reviewed completely
- NO violations found
- ALL functionality verified working
- ALL integration verified proper
- ALL UI compliance verified (if UI task)
- 100% rule compliant

**❌ REJECT if:**
- ANY violations found
- ANY functionality issues
- ANY integration issues
- ANY UI compliance issues
- NOT 100% rule compliant

---

### Step 7: Create Fix Tasks (if rejected)

**If task is rejected:**

1. **Create Fix Task:**
   ```json
   {
     "id": "TASK-W[X]-FIX-[NUMBER]",
     "name": "Fix rule violations in [original task name]",
     "status": "pending",
     "phase": "FIX_REQUIRED",
     "estimated_hours": [estimate],
     "description": "[Detailed violation list]",
     "original_task": "[Task ID]",
     "violations": [
       {
         "file": "[file path]",
         "line": [line number],
         "violation": "[description]",
         "rule": "[rule broken]"
       }
     ]
   }
   ```

2. **Add to Worker's Progress File:**
   - Add to `next_tasks` array
   - Mark original task as "needs_fix"
   - Update worker notes

3. **Notify Worker:**
   - Document all violations clearly
   - Provide file locations and line numbers
   - Explain what needs to be fixed
   - Require re-submission after fixes

---

### Step 8: Update Progress

**After verification:**

1. **Update Task Status:**
   - Mark as "approved" or "rejected"
   - Add verification notes
   - Update completion time

2. **Update Worker Progress:**
   - Update tasks_completed (if approved)
   - Update progress_percentage
   - Add verification notes

3. **Generate Report:**
   - Save verification report
   - Document findings
   - Document actions taken

---

## ⏱️ Time Estimates

**Per Task Verification:**
- Small task (1-2 files): 20-30 minutes
- Medium task (3-5 files): 45-60 minutes
- Large task (6+ files): 90-120 minutes

**This is necessary to ensure 100% quality and rule compliance.**

---

## ✅ Success Criteria

**Verification is successful when:**
1. ✅ Rules refreshed before review
2. ✅ ALL files read completely
3. ✅ ALL violations found (if any)
4. ✅ ALL functionality verified
5. ✅ ALL integration verified
6. ✅ Task approved or rejected with clear reason
7. ✅ Fix tasks created (if rejected)
8. ✅ Progress updated

**NO SHORTCUTS. NO EXCEPTIONS. 100% VERIFICATION REQUIRED.**

---

**Document Created:** 2025-01-28  
**Status:** ACTIVE - Must be followed for ALL task verifications  
**Priority:** HIGHEST - Quality assurance requirement

