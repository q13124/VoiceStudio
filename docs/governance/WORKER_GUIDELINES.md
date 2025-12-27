# Worker Guidelines
## VoiceStudio Quantum+ - Rules to Prevent Duplicate Work

**Date Created:** 2025-01-28  
**Purpose:** Clear guidelines for all workers to prevent duplicate work and ensure efficient collaboration

---

## 🚨 CRITICAL RULES

### Rule 1: ALWAYS Check Master Checklist Before Starting ANY Task

**MANDATORY WORKFLOW:**
1. **Before starting any task:**
   - Read `docs/governance/MASTER_TASK_CHECKLIST.md`
   - Search for your task ID (e.g., `TASK-W1-003`)
   - Check the status:
     - ✅ **COMPLETE** = DO NOT START, task is done
     - 🔄 **IN PROGRESS** = DO NOT START, another worker is working on it
     - ⏳ **PENDING** = Safe to start

2. **If task is COMPLETE or IN PROGRESS:**
   - DO NOT start the task
   - Move to the next available task in your assignment
   - If you believe there's an error, check the completion notes first

3. **If task is PENDING:**
   - Mark it as 🔄 **IN PROGRESS** in the checklist BEFORE starting
   - Then proceed with the work

---

### Rule 2: ALWAYS Update Master Checklist After Completing a Task

**MANDATORY WORKFLOW:**
1. **Immediately after completing a task:**
   - Open `docs/governance/MASTER_TASK_CHECKLIST.md`
   - Find your task
   - Update status from `🔄 IN PROGRESS` to `✅ COMPLETE`
   - Add completion date: `(YYYY-MM-DD)`
   - Add brief completion notes if helpful

2. **Example Update:**
   ```markdown
   #### TASK-W1-003: ToastNotificationService Integration
   **Status:** ✅ **COMPLETE** (2025-01-28)
   **Notes:** All 8 panels integrated with toast notifications for user actions
   ```

3. **If task has sub-items (panels, files, etc.):**
   - Mark each sub-item as ✅ when complete
   - Update overall task status when all sub-items are done

---

### Rule 3: NEVER Start Work Without Checking Status First

**PROHIBITED ACTIONS:**
- ❌ Starting a task without checking the checklist
- ❌ Assuming a task is available
- ❌ Working on a task that's marked COMPLETE
- ❌ Working on a task that's marked IN PROGRESS by another worker

**REQUIRED ACTIONS:**
- ✅ Always check checklist first
- ✅ Verify task status
- ✅ Mark as IN PROGRESS before starting
- ✅ Update to COMPLETE when done

---

### Rule 4: Communication Protocol

**If You Find a Conflict:**
1. Check the completion notes in the checklist
2. Verify the task is actually complete by checking the code
3. If you believe there's an error:
   - Document what you found
   - Check if the task needs additional work
   - Update the checklist with your findings

**If You Need to Change Task Status:**
- Only change status of tasks you're assigned to
- If you need to change another worker's task status, document why
- Always add notes explaining status changes

---

## 📋 TASK SELECTION WORKFLOW

### Step 1: Review Your Assignment
1. Check `docs/governance/OPTIMIZED_TASK_DISTRIBUTION.md`
2. Find tasks assigned to your worker number (W1, W2, or W3)
3. Note the priority order (🔴 Immediate, 🟡 High, 🟢 Medium)

### Step 2: Check Master Checklist
1. Open `docs/governance/MASTER_TASK_CHECKLIST.md`
2. Find your assigned tasks
3. Identify the first PENDING task in priority order

### Step 3: Verify Task Availability
1. Check if task is marked:
   - ✅ COMPLETE → Skip to next task
   - 🔄 IN PROGRESS → Skip to next task
   - ⏳ PENDING → Proceed to Step 4

### Step 4: Claim the Task
1. Update checklist: Change status to `🔄 IN PROGRESS`
2. Add your worker identifier if needed
3. Note the start time/date

### Step 5: Complete the Task
1. Do the work
2. Test your changes
3. Verify it works

### Step 6: Update Checklist
1. Change status to `✅ COMPLETE`
2. Add completion date: `(YYYY-MM-DD)`
3. Add completion notes
4. Update any sub-items

---

## 🔍 HOW TO CHECK IF A TASK IS ALREADY DONE

### Method 1: Check Master Checklist
1. Open `docs/governance/MASTER_TASK_CHECKLIST.md`
2. Search for your task ID (Ctrl+F)
3. Check the status line

### Method 2: Check Code Files
1. If checklist says COMPLETE, verify in code
2. Look for the expected changes
3. If changes exist, task is done
4. If changes don't exist, there may be an error

### Method 3: Check Progress Reports
1. Check `docs/governance/HIGH_PRIORITY_TASKS_PROGRESS_2025-01-28.md`
2. Look for your task in the completed section
3. Verify completion details

---

## ⚠️ COMMON MISTAKES TO AVOID

### Mistake 1: Assuming a Task is Available
**Wrong:** "I'll just start working on TASK-W1-003"
**Right:** "Let me check the checklist first to see if TASK-W1-003 is available"

### Mistake 2: Not Updating Checklist
**Wrong:** Completing a task and forgetting to update the checklist
**Right:** Update checklist immediately after completing a task

### Mistake 3: Working on Completed Tasks
**Wrong:** "The checklist says COMPLETE, but I'll do it again to be sure"
**Right:** "The checklist says COMPLETE, so I'll move to the next task"

### Mistake 4: Not Marking as IN PROGRESS
**Wrong:** Starting work without updating checklist
**Right:** Mark as IN PROGRESS before starting, then do the work

---

## 📝 CHECKLIST UPDATE TEMPLATE

### When Starting a Task:
```markdown
#### TASK-WX-XXX: Task Name
**Status:** 🔄 **IN PROGRESS** (Started 2025-01-28 by Worker X)
```

### When Completing a Task:
```markdown
#### TASK-WX-XXX: Task Name
**Status:** ✅ **COMPLETE** (2025-01-28)
**Notes:** Brief description of what was completed
**Files Changed:**
- File1.xaml.cs
- File2.xaml
```

### When Completing Sub-Items:
```markdown
**Panels:**
1. ✅ Panel1 (2025-01-28)
2. ✅ Panel2 (2025-01-28)
3. ⏳ Panel3 (Next)
4. ⏳ Panel4 (Next)
```

---

## 🎯 PRIORITY ORDER

### For All Workers:
1. **🔴 Immediate Priority** - Do these first
2. **🟡 High Priority** - Do these next
3. **🟢 Medium Priority** - Do these last

### Within Each Priority:
- Work from top to bottom
- Complete one task before moving to the next
- Update checklist after each task

---

## ✅ VERIFICATION CHECKLIST

Before starting any task, verify:
- [ ] Task is assigned to my worker (W1, W2, or W3)
- [ ] Task status is ⏳ PENDING in Master Checklist
- [ ] Task is not marked as ✅ COMPLETE
- [ ] Task is not marked as 🔄 IN PROGRESS by another worker
- [ ] I understand what the task requires
- [ ] I have updated the checklist to mark it as IN PROGRESS

After completing any task, verify:
- [ ] Task is fully complete (all sub-items done)
- [ ] Code compiles without errors
- [ ] Changes are tested and working
- [ ] Checklist is updated to ✅ COMPLETE
- [ ] Completion date is added
- [ ] Completion notes are added (if helpful)

---

## 🚀 QUICK REFERENCE

### Before Starting Work:
1. ✅ Check Master Checklist
2. ✅ Verify task is PENDING
3. ✅ Mark as IN PROGRESS
4. ✅ Start work

### After Completing Work:
1. ✅ Test changes
2. ✅ Update Master Checklist
3. ✅ Mark as COMPLETE
4. ✅ Add completion date
5. ✅ Move to next task

---

## 📞 IF YOU HAVE QUESTIONS

### About Task Status:
- Check Master Checklist first
- Check Progress Report second
- If still unclear, document your findings

### About Task Requirements:
- Check the task description in Master Checklist
- Check the detailed description in Optimized Task Distribution
- Check the original task in Evenly Balanced Task Distribution

### About Conflicts:
- Document what you found
- Check if it's actually a conflict or just needs additional work
- Update checklist with your findings

---

**Last Updated:** 2025-01-28  
**Remember:** Always check the checklist before starting, always update it after completing!

