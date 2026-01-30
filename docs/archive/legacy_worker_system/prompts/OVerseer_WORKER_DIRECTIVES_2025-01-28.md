# Overseer Worker Directives
## VoiceStudio Quantum+ - Official Task Assignments

**Date:** 2025-01-28  
**Status:** ✅ **ACTIVE DIRECTIVES**  
**Authority:** Overseer (Autonomous Decision)

---

## 👷 WORKER 1: Backend/Engines/Audio Processing

### IMMEDIATE TASK ASSIGNMENT

**Phase A1.1: RVC Engine Fixes**  
**Priority:** CRITICAL  
**Timeline:** 3-4 days  
**Status:** 🔄 **ASSIGNED - START IMMEDIATELY**

**Requirements:**
1. Review `app/core/engines/rvc_engine.py` for any placeholder implementations
2. Verify all methods have real implementations (not stubs)
3. Ensure no `pass` statements in non-abstract methods
4. Test functionality works
5. Update progress file after completion

**Next Task (After RVC):**
- Phase A1.2: GPT-SoVITS Engine - Port from old project (2-3 days)

**Progress File Required:**
- Create: `docs/governance/progress/WORKER_1_2025-01-28.json`
- Update after each task completion
- Report blockers immediately

---

## 👷 WORKER 2: UI/UX/Frontend Specialist

### IMMEDIATE TASK ASSIGNMENT

**Phase A3.1: VideoGenViewModel Fixes**  
**Priority:** HIGH  
**Timeline:** 0.5 days  
**Status:** 🔄 **ASSIGNED - START IMMEDIATELY**

**Requirements:**
1. Review `src/VoiceStudio.App/ViewModels/VideoGenViewModel.cs`
2. Verify quality metrics integration is complete
3. Ensure no placeholder implementations
4. Test functionality works
5. Update progress file after completion

**Next Task (After VideoGenViewModel):**
- Phase A3.2: TrainingDatasetEditorViewModel - Real editing (1 day)

**Progress File Required:**
- Create: `docs/governance/progress/WORKER_2_2025-01-28.json`
- Update after each task completion
- Report blockers immediately

---

## 👷 WORKER 3: Testing/Quality/Documentation

### CURRENT TASK (CONTINUE)

**TASK-W3-013: User Manual**  
**Status:** ✅ **ACTIVE** (58.8% complete)  
**Action:** Continue current work  
**Next Tasks:** TASK-W3-014, TASK-W3-015, TASK-W3-016, TASK-W3-017

**Progress File:** ✅ Already exists and updated

---

## 🚨 CRITICAL RULES ENFORCEMENT

### Absolute Rule: NO Stubs, Placeholders, Bookmarks, or Tags
- ❌ **FORBIDDEN:** `pass` statements (except in abstract methods)
- ❌ **FORBIDDEN:** `return None` without error handling
- ❌ **FORBIDDEN:** `NotImplementedException` or `NotImplementedError`
- ❌ **FORBIDDEN:** TODO, FIXME, placeholder comments
- ✅ **REQUIRED:** 100% complete, functional implementations

### Quality Gates
- ✅ Code must compile/run
- ✅ Functionality must work
- ✅ No forbidden terms
- ✅ UI compliance (for UI tasks)

---

## 📊 AUTONOMOUS WORKFLOW REQUIREMENTS

### For All Workers:
1. **Work Continuously:** NO PAUSING between tasks
2. **Update Progress:** After each task completion
3. **Self-Verify:** Before marking task complete
4. **Report Blockers:** Immediately when stuck
5. **Move to Next Task:** Automatically after completion

### Progress File Format:
```json
{
  "worker": "Worker 1",
  "date": "2025-01-28",
  "status": "working",
  "current_task": "Phase A1.1 - RVC Engine",
  "tasks_completed_today": 0,
  "tasks_in_progress": 1,
  "tasks_blocked": 0,
  "progress_percentage": 0.0,
  "last_update": "2025-01-28T[time]",
  "notes": "Starting RVC Engine fixes",
  "blockers": [],
  "next_tasks": ["Phase A1.2 - GPT-SoVITS Engine"]
}
```

---

## ✅ VERIFICATION CHECKLIST

### Before Task Completion:
- [ ] All functionality implemented (no placeholders)
- [ ] No forbidden terms in code
- [ ] Code compiles/runs
- [ ] Functionality tested
- [ ] Progress file updated
- [ ] MASTER_TASK_CHECKLIST.md updated (if applicable)

---

## 🎯 SUCCESS CRITERIA

**Task is Complete When:**
- ✅ All code is 100% functional
- ✅ No forbidden terms present
- ✅ Functionality verified working
- ✅ Progress file updated
- ✅ Ready for next task

---

**Last Updated:** 2025-01-28  
**Status:** ✅ **DIRECTIVES ACTIVE**  
**Authority:** Overseer (Autonomous)

