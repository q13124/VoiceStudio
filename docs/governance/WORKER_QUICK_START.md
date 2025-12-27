# Worker Quick Start Guide
## VoiceStudio Quantum+ - Phase 6

**Welcome!** This guide will help you get started quickly.

---

## 🚀 First Steps

### 1. Read Your Assignment
- **Worker 1:** Read `docs/governance/WORKER_1_PROMPT_PERFORMANCE_MEMORY_ERROR.md`
  - **Phase 6:** Fix 7 TODOs in AutomationCurvesEditorControl (1 day)
  - **Phase 7:** Implement 15 audio engines (12-15 days)
- **Worker 2:** Read `docs/governance/WORKER_2_PROMPT_UI_UX_POLISH.md`
  - **Phase 6:** ✅ Complete
  - **Phase 7:** Implement 18 engines - 5 legacy audio + 13 image (12-15 days)
- **Worker 3:** Read `docs/governance/WORKER_3_PROMPT_DOCUMENTATION_PACKAGING.md`
  - **Phase 6:** Verify installer/update/release (2-3 days)
  - **Phase 7:** Implement 10 engines - 8 video + 2 VC (12-15 days)

### 2. Read Engine Implementation Plan (PHASE 7)
**If implementing engines, read:**
- `docs/governance/ENGINE_IMPLEMENTATION_PLAN.md` - Complete engine implementation plan
- `docs/governance/ENGINE_IMPLEMENTATION_SUMMARY.md` - Quick summary
- `requirements_engines.txt` - All Python dependencies

### 3. Read Memory Bank (CRITICAL!)
**Before doing ANYTHING, read:**
- `docs/design/MEMORY_BANK.md` - Contains non-negotiable architecture rules
- `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - **CRITICAL** - 100% complete rule

**Key Rules to Remember:**
- ❌ **NEVER** create TODO comments or placeholders
- ❌ **NEVER** leave NotImplementedException throws
- ❌ **NEVER** mark tasks complete if they have stubs
- ✅ **ALWAYS** complete 100% before moving on
- ❌ **NEVER** merge View/ViewModel files
- ❌ **NEVER** replace PanelHost with raw Grids
- ❌ **NEVER** hardcode colors/values (use VSQ.* tokens)
- ❌ **NEVER** simplify the UI (complexity is required)
- ✅ **ALWAYS** use DesignTokens.xaml for styling
- ✅ **ALWAYS** maintain MVVM separation

### 4. Set Up Your Status File
Create your status file:
- **Worker 1:** `docs/governance/WORKER_1_STATUS.md`
- **Worker 2:** `docs/governance/WORKER_2_STATUS.md`
- **Worker 3:** `docs/governance/WORKER_3_STATUS.md`

Use the template: `docs/governance/WORKER_STATUS_TEMPLATE.md`

### 5. Check Task Tracker
Review the shared task tracker:
- `docs/governance/TASK_TRACKER_3_WORKERS.md`

---

## 📋 Daily Workflow

### Morning:
1. **Read Memory Bank** - `docs/design/MEMORY_BANK.md` (5 minutes)
2. **Check Task Tracker** - See what others are doing
3. **Review Your Status File** - Remember where you left off
4. **Plan Your Day** - Review your task breakdown

### During Work:
1. **Follow Your Prompt File** - Your detailed instructions
2. **Check Memory Bank** - When unsure about architecture
3. **Test As You Go** - Don't wait until the end
4. **Commit Frequently** - Use descriptive messages

### End of Day:
1. **Update Task Tracker** - `docs/governance/TASK_TRACKER_3_WORKERS.md`
2. **Update Your Status File** - `docs/governance/WORKER_X_STATUS.md`
3. **Commit All Changes** - With descriptive messages
4. **Document Blockers** - If any

---

## 📝 Update Format

### Task Tracker Update:
```markdown
### Day [N] ([Date])
**Worker [X]:**
- Task: [Task name]
- Status: 🚧 In Progress / ✅ Complete / ⏸️ Blocked
- Progress: [X]%
- Notes: [What was accomplished, any issues]
```

### Commit Messages:
Use format: `Worker [X]: [Brief description]`

Examples:
- `Worker 1: Optimize waveform rendering performance`
- `Worker 2: Add loading states to ProfilesView`
- `Worker 3: Complete user manual section on voice synthesis`

---

## 🗂️ Key Files & Directories

### Documentation:
- `docs/design/MEMORY_BANK.md` - **READ DAILY** - Architecture rules
- `docs/governance/` - All governance docs (roadmaps, status, tracking)
- `docs/governance/TASK_TRACKER_3_WORKERS.md` - **UPDATE DAILY** - Shared progress
- `docs/governance/WORKER_X_STATUS.md` - **UPDATE DAILY** - Your detailed status

### Code:
- `src/VoiceStudio.App/` - Frontend (WinUI 3, C#)
- `backend/api/` - Backend (Python FastAPI)
- `app/core/` - Core engine code

### Design System:
- `src/VoiceStudio.App/Resources/DesignTokens.xaml` - All design tokens (VSQ.*)

---

## 🚨 When Stuck

1. **Check Memory Bank FIRST** - `docs/design/MEMORY_BANK.md`
2. **Check Task Tracker** - See what others are doing
3. **Review Existing Code** - Look for similar implementations
4. **Ask Overseer** - Don't spend >2 hours stuck
5. **Document Blocker** - Add to task tracker and status file

---

## ✅ Success Checklist

### Daily:
- [ ] Read Memory Bank
- [ ] Updated Task Tracker
- [ ] Updated Status File
- [ ] Committed changes
- [ ] Tested changes
- [ ] No Memory Bank violations
- [ ] **NO stubs or placeholders** - Everything 100% complete

### Weekly:
- [ ] All day's tasks complete
- [ ] No blockers
- [ ] Coordinated with other workers
- [ ] Quality standards met
- [ ] **All implementations 100% complete** - No TODO comments, no placeholders

## 🚨 CRITICAL: 100% Complete Rule

**ABSOLUTE REQUIREMENT:**
- ❌ **NEVER** create TODO comments
- ❌ **NEVER** leave placeholder code
- ❌ **NEVER** create bookmark stubs
- ❌ **NEVER** mark a task complete if it has "// TODO" or "[PLACEHOLDER]"
- ✅ **ALWAYS** implement 100% before moving to next task
- ✅ **ALWAYS** test your implementation
- ✅ **ALWAYS** verify it works before marking complete

**If it's not 100% complete and tested, it's NOT done. Don't move on.**

---

## 🔄 Coordination Points

### Worker 1 → Worker 3:
- **Day 5:** Share performance metrics
- **Day 7:** Share error handling patterns

### Worker 2 → Worker 3:
- **Day 8:** Share UI screenshots

### All → Worker 3:
- **Day 9:** Share final testing results

---

## 📊 Progress Tracking

### Your Progress Files (MANDATORY - ALL MUST BE UPDATED):
1. **TASK_LOG.md** - `docs/governance/TASK_LOG.md` (MANDATORY - update when tasks assigned/completed)
2. **TASK_TRACKER_3_WORKERS.md** - `docs/governance/TASK_TRACKER_3_WORKERS.md` (MANDATORY - daily updates)
3. **MASTER_TASK_CHECKLIST.md** - `docs/governance/MASTER_TASK_CHECKLIST.md` (MANDATORY - update when tasks complete)
4. **Your Status** - `docs/governance/worker[N]/WORKER_[N]_STATUS_2025-01-28.md` (MANDATORY - daily updates)

### Update Frequency (MANDATORY):
- **TASK_LOG.md:** When tasks are assigned or completed (MANDATORY)
- **TASK_TRACKER_3_WORKERS.md:** Daily (end of day) - MANDATORY
- **MASTER_TASK_CHECKLIST.md:** When tasks are completed (MANDATORY)
- **Status File:** Daily (end of day) - MANDATORY
- **Commits:** As you complete work (frequently)

**⚠️ CRITICAL:** You MUST update all tracking systems. See `docs/governance/overseer/MANDATORY_TRACKING_SYSTEM_USAGE_2025-01-28.md` for complete requirements.

---

## 🎯 Remember

1. **Memory Bank is Law** - Read it daily, follow it always
2. **Test As You Go** - Don't wait until the end
3. **Update Logs Daily** - Task tracker and status file
4. **Coordinate Early** - Don't wait for handoff deadlines
5. **Quality First** - But efficiency matters too

---

**Questions?** Check your prompt file first, then ask the overseer.

**Ready to Start?** Read your prompt file and Memory Bank, then begin Day 1 tasks!

