# File Locking Protocol
## VoiceStudio Quantum+ - Preventing Merge Conflicts

**Last Updated:** 2025-01-27  
**Purpose:** Explicit lock/check-out system to ensure only one agent edits a file at a time, eliminating merge conflicts.

---

## 🔒 Lock System Overview

**Principle:** Only one agent can edit a file at a time. All other agents must wait or request handoff.

---

## 📋 Lock Protocol

### 1. Before Editing a File

**Required Steps:**
1. Check `TASK_LOG.md` for existing file locks
2. If file is locked:
   - **Option A:** Wait for unlock (if task is nearly complete)
   - **Option B:** Request handoff from current worker
   - **Option C:** Work on different file
3. If file is unlocked:
   - Add file to lock list in `TASK_LOG.md`
   - Include task ID, worker name, and timestamp
   - Begin work

### 2. During File Edit

**Lock Status:**
- File remains locked until task completion
- Other workers cannot edit the same file
- Lock is visible in `TASK_LOG.md`

### 3. After Completing Work

**Unlock Steps:**
1. Complete all edits
2. Test changes
3. Remove file from lock list in `TASK_LOG.md`
4. Mark task as complete
5. Notify Overseer for review

---

## 🔄 Lock Request Protocol

### Requesting a Locked File

If you need a file that's currently locked:

```
Worker A (needs file): "Requesting handoff of [filename] from Worker B for [task description]"
Worker B (has lock): "Releasing lock on [filename], task [TASK-XXX] complete"
Overseer: "Approved. Worker A now has lock on [filename]"
```

### Emergency Unlock

If a worker is stuck or unresponsive:
1. Overseer reviews situation
2. Overseer can force unlock after 24 hours of inactivity
3. Overseer assigns task to new worker
4. Original worker's changes are preserved (if any)

---

## ⚠️ Staggered Access Pattern

**For Shared Resources:**

If multiple agents need the same file or resource:
1. **First agent:** Acquires lock, begins work
2. **Other agents:** 
   - Check lock status
   - Implement retry/backoff (see Performance Safeguards)
   - Sleep briefly before retrying (not tight loop)
   - Wait for unlock notification

**Example:**
```python
# Backend retry pattern
max_retries = 5
retry_delay = 2  # seconds

for attempt in range(max_retries):
    if file_is_unlocked(filename):
        acquire_lock(filename)
        break
    else:
        sleep(retry_delay * (attempt + 1))  # Exponential backoff
```

---

## 📝 Lock Format in TASK_LOG.md

**Lock Entry Format:**
```markdown
| File Path | Locked By | Task ID | Locked At | Expected Unlock |
|-----------|-----------|---------|-----------|-----------------|
| `src/.../File.cs` | Worker 1 | TASK-001 | 2025-01-27 10:00 | 2025-01-27 12:00 |
```

---

## 🚨 Conflict Prevention

### Merge Conflict Prevention

**Before Committing:**
1. Check `TASK_LOG.md` for any locks on files you modified
2. Ensure your lock is still valid
3. If another worker has a lock, coordinate before committing

### Git Integration

**Recommended Workflow:**
1. Create feature branch: `worker-1/task-001`
2. Work on locked files
3. Commit changes
4. Remove lock in `TASK_LOG.md`
5. Create PR for Overseer review
6. Overseer merges after approval

---

## ✅ Best Practices

1. **Lock Early:** Acquire lock before starting work
2. **Lock Scope:** Lock only files you're actively editing
3. **Quick Unlock:** Remove lock immediately after completion
4. **Communication:** Notify Overseer when requesting handoffs
5. **Documentation:** Always update `TASK_LOG.md` with lock status

---

## 🔍 Lock Verification

**Before Starting Work:**
```bash
# Check TASK_LOG.md for locks
grep -i "locked" docs/governance/TASK_LOG.md

# Check specific file
grep "filename.cs" docs/governance/TASK_LOG.md
```

---

## 📚 Related Documents

- `TASK_LOG.md` - Central task log with lock status
- `PERFORMANCE_STABILITY_SAFEGUARDS.md` - Retry/backoff patterns
- `OVERSEER_SYSTEM_PROMPT_V2.md` - Overseer lock management

---

**This protocol ensures orderly file access and prevents merge conflicts in multi-agent development.**

