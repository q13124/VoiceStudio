# Worker Communication Protocol
## VoiceStudio Quantum+ - Standard Communication Format

**Date:** 2025-01-28  
**Status:** ✅ **PROTOCOL ESTABLISHED**  
**Purpose:** Standard format for worker communication and task completion

---

## 📋 TASK COMPLETION REPORT FORMAT

### Standard Format

**File:** `docs/governance/progress/TASK_COMPLETION_WX_YYYY-MM-DD.md`

**Required Sections:**

1. **Task Information**
2. **Completion Summary**
3. **Evidence**
4. **Verification Checklist**
5. **Related Files**

---

### Task Completion Report Template

```markdown
# Task Completion Report

**Task ID:** TASK-XXX  
**Worker:** Worker X  
**Date:** YYYY-MM-DD  
**Status:** ✅ COMPLETE / ⚠️ INCOMPLETE

---

## Task Information

**Description:**
[Brief description of task]

**Files Modified:**
- `path/to/file1.py` (Lines X-Y)
- `path/to/file2.cs` (Lines A-B)

**Files Created:**
- `path/to/new_file.py`

**Dependencies Added:**
- `library_name==version` (added to requirements_engines.txt)

---

## Completion Summary

**What Was Done:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Key Changes:**
- [Change 1]
- [Change 2]
- [Change 3]

**Testing Performed:**
- [Test 1]
- [Test 2]
- [Test 3]

---

## Evidence

### Code Evidence

**File:** `path/to/file.py`
```python
# Code snippet showing implementation
def implemented_function():
    # Real implementation
    return result
```

### Test Results

**Test Output:**
```
[Test results]
```

### Screenshots (if UI task)

**Screenshot 1:** [Description]
- File: `docs/governance/progress/screenshots/TASK-XXX_screenshot1.png`

**Screenshot 2:** [Description]
- File: `docs/governance/progress/screenshots/TASK-XXX_screenshot2.png`

---

## Verification Checklist

- [x] No forbidden terms (TODO, FIXME, placeholders, stubs)
- [x] All dependencies installed and working
- [x] UI compliance verified (if applicable)
- [x] Basic functionality tested
- [x] No regressions introduced
- [x] Code quality standards met
- [x] Documentation updated (if needed)
- [x] Tests passing (if applicable)

---

## Related Files

**Modified:**
- `path/to/file1.py`
- `path/to/file2.cs`

**Created:**
- `path/to/new_file.py`

**Dependencies:**
- `requirements_engines.txt` (updated)
```

---

## 🚨 BLOCKER REPORT FORMAT

### Blocker Report Template

```markdown
# Blocker Report

**Blocker ID:** BLOCK-XXX  
**Worker:** Worker X  
**Task:** TASK-XXX  
**Date:** YYYY-MM-DD  
**Status:** ⏳ BLOCKED

---

## Blocker Information

**Type:** [Dependency / Technical / Resource / Other]

**Description:**
[Detailed description of blocker]

**Impact:**
- [Impact 1]
- [Impact 2]

**Affected Tasks:**
- TASK-XXX (blocked)
- TASK-YYY (dependent)

---

## Attempted Solutions

1. [Solution 1] - ❌ Failed: [Reason]
2. [Solution 2] - ❌ Failed: [Reason]
3. [Solution 3] - ⏳ In Progress

---

## Resolution Plan

**Proposed Solution:**
[Description of proposed solution]

**Required Resources:**
- [Resource 1]
- [Resource 2]

**Estimated Time:**
[X hours/days]

**Dependencies:**
- [Dependency 1]
- [Dependency 2]

---

## Escalation

**Escalated To:** [Overseer / User / Other]

**Escalation Reason:**
[Why escalation is needed]

**Requested Action:**
[What is needed to resolve]
```

---

## 📊 PROGRESS UPDATE FORMAT

### Progress Update Template

```markdown
# Progress Update

**Worker:** Worker X  
**Date:** YYYY-MM-DD  
**Period:** [Daily / Weekly]

---

## Tasks Completed

| Task ID | Description | Status | Evidence |
|---------|-------------|--------|----------|
| TASK-XXX | Description | ✅ COMPLETE | [Link to evidence] |
| TASK-YYY | Description | ⏳ IN PROGRESS | [Progress notes] |

---

## Tasks In Progress

| Task ID | Description | Progress | ETA |
|---------|-------------|----------|-----|
| TASK-XXX | Description | 75% | [Date] |

---

## Blockers

| Blocker ID | Description | Status | Resolution Plan |
|------------|-------------|--------|-----------------|
| BLOCK-XXX | Description | ⏳ PENDING | [Plan] |

---

## Next Steps

1. [Next step 1]
2. [Next step 2]
3. [Next step 3]
```

---

## 🔄 ESCALATION PATH

### Escalation Levels

**Level 1: Worker Self-Resolution**
- Worker attempts to resolve blocker
- Worker documents attempts
- Worker proposes solution

**Level 2: Overseer Intervention**
- Worker escalates to Overseer
- Overseer reviews blocker
- Overseer provides guidance or reassigns

**Level 3: User Decision**
- Overseer escalates to user
- User provides decision
- User approves resolution plan

### Escalation Process

1. **Worker Identifies Blocker:**
   - Create blocker report
   - Document attempts
   - Propose solution

2. **Worker Escalates:**
   - Submit blocker report
   - Request Overseer review
   - Wait for response

3. **Overseer Reviews:**
   - Assess blocker
   - Provide guidance
   - Reassign if needed
   - Escalate to user if required

4. **Resolution:**
   - Implement solution
   - Verify resolution
   - Continue work

---

## ✅ SUMMARY

**Communication Protocol:** ✅ **ESTABLISHED**

**Formats:**
- ✅ Task completion reports
- ✅ Blocker reports
- ✅ Progress updates
- ✅ Escalation path

**Status:** ✅ **READY FOR USE**

---

**Document Date:** 2025-01-28  
**Status:** ✅ **PROTOCOL ESTABLISHED**  
**Next Step:** Workers use standard formats for communication

