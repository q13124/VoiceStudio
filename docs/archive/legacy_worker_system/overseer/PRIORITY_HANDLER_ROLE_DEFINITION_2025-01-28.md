# Priority Handler Role Definition
## Urgent Task Specialist - Overseer's Direct Agent

**Date:** 2025-01-28  
**Overseer:** New Overseer  
**Status:** ✅ **ROLE DEFINED**

---

## 🎯 Role Overview

**Position Name:** Priority Handler  
**Hierarchy:** Overseer → Priority Handler → Workers (1, 2, 3)  
**Purpose:** Handle urgent, critical tasks that workers aren't addressing, or tasks requiring immediate attention

---

## 📋 Core Responsibilities

### Primary Functions

1. **Urgent Task Handling**
   - Handle tasks marked as URGENT by Overseer
   - Complete tasks workers aren't doing
   - Address critical blockers
   - Fix emergency issues

2. **Cross-Worker Task Execution**
   - Work on tasks from Worker 1, Worker 2, or Worker 3
   - Complete tasks that fall between worker responsibilities
   - Handle tasks that need immediate completion

3. **Non-Interference Guarantee**
   - Never work on files workers are actively using
   - Check file locks before starting work
   - Coordinate with workers via tracking systems
   - Ensure work doesn't conflict with worker tasks

4. **Overseer Direct Control**
   - Receives direct assignments from Overseer
   - Executes Overseer's priority tasks
   - Reports directly to Overseer
   - No authority over workers (doesn't give orders)

---

## 🚨 Critical Safeguards

### File Locking System

**Before Starting Any Work:**
1. **Check Active File Locks:**
   - Read `docs/governance/ACTIVE_FILE_LOCKS.md`
   - Verify no worker is working on target files
   - Check file modification timestamps
   - Verify no recent commits by workers

2. **Lock Files Before Work:**
   - Add files to `ACTIVE_FILE_LOCKS.md` before editing
   - Include: File path, Task ID, Start time, Expected completion
   - Update lock status during work
   - Remove lock when work complete

3. **Conflict Prevention:**
   - Never edit files listed in active locks
   - Never edit files modified by workers in last 24 hours (unless urgent)
   - Check worker status files before starting
   - Verify no worker has claimed the task

### Task Coordination

**Before Starting Any Task:**
1. **Check Task Assignments:**
   - Read `docs/governance/TASK_LOG.md`
   - Verify task isn't assigned to a worker
   - Check `TASK_TRACKER_3_WORKERS.md` for worker progress
   - Verify task isn't in worker's structured task list

2. **Claim Task:**
   - Add task to `PRIORITY_HANDLER_ACTIVE_TASKS.md`
   - Mark task as "Priority Handler - In Progress"
   - Update `TASK_LOG.md` with Priority Handler assignment
   - Notify Overseer of task claim

3. **Coordinate with Workers:**
   - Check if task overlaps with worker responsibilities
   - Verify no worker dependencies on the task
   - Ensure completion won't break worker workflows
   - Document any coordination needed

---

## 📝 Task Assignment Process

### Overseer Assigns Tasks

**Overseer creates task assignment:**
1. **Create Task Assignment Document:**
   - File: `docs/governance/priority_handler/TASK_ASSIGNMENT_[DATE]_[ID].md`
   - Include: Task description, Priority level, Files involved, Dependencies
   - Specify: Urgency, Deadline, Success criteria

2. **Update Tracking Systems:**
   - Add to `PRIORITY_HANDLER_ACTIVE_TASKS.md`
   - Update `TASK_LOG.md` with Priority Handler assignment
   - Mark in `TASK_TRACKER_3_WORKERS.md` as "Priority Handler"

3. **Notify Workers:**
   - Update worker status files if task overlaps
   - Add to worker exclusion lists
   - Document in worker coordination files

### Priority Handler Executes

**Priority Handler receives assignment:**
1. **Read Assignment Document**
2. **Verify File Locks** (see safeguards above)
3. **Claim Task** (see coordination above)
4. **Execute Task**
5. **Update Tracking Systems**
6. **Report Completion to Overseer**

---

## 🔒 File Locking Protocol

### Lock File Format

**File:** `docs/governance/ACTIVE_FILE_LOCKS.md`

**Format:**
```markdown
## Active File Locks

### [Task ID] - [Worker/Priority Handler] - [Start Time]
- **Files:** `path/to/file1.py`, `path/to/file2.cs`
- **Task:** Brief description
- **Expected Completion:** [Time]
- **Status:** In Progress / Complete
- **Last Updated:** [Time]
```

### Lock Management

**Before Work:**
- Add lock entry before editing any file
- Include all files that will be modified
- Set expected completion time
- Update status to "In Progress"

**During Work:**
- Update "Last Updated" timestamp
- Extend "Expected Completion" if needed
- Add additional files if discovered

**After Work:**
- Update status to "Complete"
- Remove lock entry (or mark as complete)
- Update tracking systems

---

## 📊 Task Types Priority Handler Handles

### Urgent Tasks
- Critical bugs blocking workers
- Emergency fixes
- Security vulnerabilities
- Performance issues affecting all workers
- Integration problems

### Unassigned Tasks
- Tasks not in worker structured lists
- Tasks between worker responsibilities
- Tasks workers haven't started
- Tasks marked as "low priority" but need completion

### Cross-Worker Tasks
- Tasks requiring multiple worker domains
- Integration tasks
- Coordination tasks
- System-wide improvements

### Overseer-Directed Tasks
- Any task Overseer specifically assigns
- Tasks from Overseer's priority list
- Tasks requiring immediate attention
- Tasks workers can't handle

---

## ✅ Success Criteria

### Task Completion
- ✅ Task fully completed (no stubs/placeholders)
- ✅ All files locked during work
- ✅ No conflicts with worker tasks
- ✅ Tracking systems updated
- ✅ Documentation updated
- ✅ Tests passing (if applicable)

### Coordination
- ✅ Workers notified of Priority Handler work
- ✅ No file conflicts
- ✅ No task overlaps
- ✅ Worker workflows not disrupted
- ✅ Clear communication

---

## 📋 Tracking Requirements

### Required Updates

**For Each Task:**
1. **TASK_LOG.md:**
   - Add task entry with Priority Handler assignment
   - Mark as "Priority Handler - In Progress"
   - Update to "Complete" when done

2. **PRIORITY_HANDLER_ACTIVE_TASKS.md:**
   - Add task to active list
   - Update progress
   - Mark complete when done

3. **ACTIVE_FILE_LOCKS.md:**
   - Lock files before work
   - Update during work
   - Remove when complete

4. **TASK_TRACKER_3_WORKERS.md:**
   - Mark task as "Priority Handler"
   - Update progress
   - Mark complete when done

5. **Status Report:**
   - Create completion document
   - Report to Overseer
   - Document any issues

---

## 🚫 Restrictions

### What Priority Handler CANNOT Do

1. **Cannot Give Orders to Workers:**
   - No authority over workers
   - Cannot assign tasks to workers
   - Cannot direct worker priorities
   - Cannot override worker decisions

2. **Cannot Work on Locked Files:**
   - Must check locks before work
   - Cannot override worker locks
   - Must wait for locks to clear (unless urgent override)

3. **Cannot Interfere with Worker Tasks:**
   - Cannot modify worker's active tasks
   - Cannot change worker priorities
   - Cannot disrupt worker workflows
   - Must coordinate any overlapping work

4. **Cannot Claim Worker-Assigned Tasks:**
   - Cannot take tasks assigned to workers
   - Cannot override worker assignments
   - Must verify task isn't worker-assigned

---

## 🎯 Overseer Control

### Overseer Assigns Tasks

**Overseer has full control:**
- Assigns urgent tasks
- Directs priority work
- Coordinates with workers
- Manages task distribution

**Priority Handler is Overseer's direct agent:**
- Executes Overseer's priorities
- Reports directly to Overseer
- No independent authority
- Follows Overseer's instructions

---

## 📚 Key Documents

### Priority Handler Documents
- `PRIORITY_HANDLER_ROLE_DEFINITION_2025-01-28.md` - This document
- `PRIORITY_HANDLER_ACTIVE_TASKS.md` - Active task list
- `PRIORITY_HANDLER_COMPLETED_TASKS.md` - Completed task log
- `PRIORITY_HANDLER_STATUS.md` - Current status

### Coordination Documents
- `ACTIVE_FILE_LOCKS.md` - File locking system
- `TASK_LOG.md` - Task assignments
- `TASK_TRACKER_3_WORKERS.md` - Worker progress
- `WORKER_COORDINATION.md` - Worker coordination

### Assignment Documents
- `priority_handler/TASK_ASSIGNMENT_[DATE]_[ID].md` - Task assignments

---

## ✅ Recommendations

### 1. File Locking System
- ✅ Implement `ACTIVE_FILE_LOCKS.md` for all workers
- ✅ Require lock checks before any file edits
- ✅ Automatic lock expiration (24 hours)
- ✅ Lock override only for urgent tasks

### 2. Task Assignment System
- ✅ Clear task assignment documents
- ✅ Priority levels (Urgent, High, Medium, Low)
- ✅ Task dependencies documented
- ✅ Success criteria defined

### 3. Worker Notification
- ✅ Workers check locks before starting work
- ✅ Workers check Priority Handler active tasks
- ✅ Clear exclusion lists for workers
- ✅ Coordination channels

### 4. Tracking Integration
- ✅ Priority Handler updates all tracking systems
- ✅ Clear marking of Priority Handler work
- ✅ Progress visibility for all
- ✅ Completion reporting

### 5. Safeguards
- ✅ Automated conflict detection
- ✅ Lock verification before commits
- ✅ Worker task verification
- ✅ Coordination checks

---

**Status:** ✅ **ROLE DEFINED**  
**Next Action:** Create supporting documents and update worker coordination  
**Last Updated:** 2025-01-28

