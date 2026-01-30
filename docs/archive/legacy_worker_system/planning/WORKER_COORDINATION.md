# Worker Coordination
## Coordination Between Workers and Priority Handler

**Date:** 2025-01-28  
**Purpose:** Coordinate work to prevent conflicts  
**Last Updated:** 2025-01-28

---

## 🎯 Coordination Rules

### All Workers Must:
1. **Check Active File Locks** before starting work
2. **Check Priority Handler Active Tasks** before claiming tasks
3. **Lock files** before editing
4. **Update tracking systems** after work
5. **Coordinate** if work overlaps

### Priority Handler Must:
1. **Check worker locks** before starting work
2. **Check worker active tasks** before claiming tasks
3. **Lock files** before editing
4. **Notify workers** if work overlaps
5. **Update tracking systems** after work

---

## 📋 Priority Handler Active Work

**Check this section before starting any task:**

*No Priority Handler active work currently*

---

## 🚫 Worker Exclusion Lists

### Tasks Workers Should NOT Work On

**Priority Handler Assigned:**
*No Priority Handler assigned tasks currently*

**File Locks:**
*No active file locks currently*

---

## ✅ Coordination Checklist

### Before Starting Work:
- [ ] Check `ACTIVE_FILE_LOCKS.md` for file conflicts
- [ ] Check `PRIORITY_HANDLER_ACTIVE_TASKS.md` for task conflicts
- [ ] Check `TASK_LOG.md` for task assignments
- [ ] Verify task isn't assigned to Priority Handler
- [ ] Lock files before editing
- [ ] Update tracking systems

### During Work:
- [ ] Update file lock timestamps
- [ ] Update task progress
- [ ] Check for new conflicts
- [ ] Coordinate if overlaps discovered

### After Work:
- [ ] Remove file locks
- [ ] Update tracking systems
- [ ] Mark tasks complete
- [ ] Report completion

---

**Status:** ✅ **COORDINATION SYSTEM ACTIVE**  
**Last Updated:** 2025-01-28

