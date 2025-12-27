# Worker Launch Instructions
## VoiceStudio Quantum+ - Phase 6 Worker Activation

**Date:** 2025-11-23  
**Status:** 🟢 Ready to Launch  
**Purpose:** Ensure workers have latest prompts and rules

---

## 🎯 How Workers Access Prompts

### Option 1: Workers Read Files Directly (RECOMMENDED)

**If workers are AI instances that can read files from the repository:**

✅ **Workers automatically get updates** - They read the prompt files each time they need them

**Instructions for Workers:**
1. Read your prompt file at the start of each session:
   - Worker 1: `docs/governance/WORKER_1_PROMPT_PERFORMANCE_MEMORY_ERROR.md`
   - Worker 2: `docs/governance/WORKER_2_PROMPT_UI_UX_POLISH.md`
   - Worker 3: `docs/governance/WORKER_3_PROMPT_DOCUMENTATION_PACKAGING.md`

2. Read Memory Bank: `docs/design/MEMORY_BANK.md`

3. Read 100% Complete Rule: `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md`

4. Check Task Tracker: `docs/governance/TASK_TRACKER_3_WORKERS.md`

**Advantage:** Workers always have the latest version with all updates.

---

### Option 2: Workers Given Prompts Once (NEEDS UPDATE)

**If workers are separate AI sessions that were given prompts at launch:**

⚠️ **Workers need to be notified of updates** - They won't automatically see changes

**What to Tell Workers:**

```
IMPORTANT UPDATE: The worker prompts have been updated with critical rules.

Please re-read your prompt file:
- Worker 1: docs/governance/WORKER_1_PROMPT_PERFORMANCE_MEMORY_ERROR.md
- Worker 2: docs/governance/WORKER_2_PROMPT_UI_UX_POLISH.md
- Worker 3: docs/governance/WORKER_3_PROMPT_DOCUMENTATION_PACKAGING.md

NEW CRITICAL RULES ADDED:
1. 100% Complete Rule - NO stubs or placeholders (see NO_STUBS_PLACEHOLDERS_RULE.md)
2. Code Quality Analysis - Duplicate removal tasks (see CODE_QUALITY_ANALYSIS.md)
3. Enhanced logging requirements - Daily status updates required

Please read these files before continuing work:
- docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md
- docs/governance/CODE_QUALITY_ANALYSIS.md (Worker 1 only)
- docs/governance/WORKER_QUICK_START.md
```

---

## 📋 Recommended Launch Process

### Step 1: Verify Files Are Updated
- [ ] All worker prompts updated with 100% complete rule
- [ ] Memory Bank updated with 100% complete rule
- [ ] NO_STUBS_PLACEHOLDERS_RULE.md created
- [ ] CODE_QUALITY_ANALYSIS.md created (for Worker 1)
- [ ] All files committed to repository

### Step 2: Launch Workers

**For Each Worker, Provide:**

1. **Primary Prompt File:**
   - Worker 1: `docs/governance/WORKER_1_PROMPT_PERFORMANCE_MEMORY_ERROR.md`
   - Worker 2: `docs/governance/WORKER_2_PROMPT_UI_UX_POLISH.md`
   - Worker 3: `docs/governance/WORKER_3_PROMPT_DOCUMENTATION_PACKAGING.md`

2. **Required Reading (In Order):**
   - `docs/governance/WORKER_QUICK_START.md` - Quick orientation
   - `docs/design/MEMORY_BANK.md` - **CRITICAL** - Architecture rules
   - `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - **CRITICAL** - 100% complete rule
   - `docs/governance/TASK_TRACKER_3_WORKERS.md` - Progress tracking
   - `docs/governance/OVERSEER_3_WORKER_OPTIMIZED_PLAN.md` - Overall plan

3. **Worker-Specific Additional Reading:**
   - **Worker 1:** `docs/governance/CODE_QUALITY_ANALYSIS.md` - Code quality issues
   - **All Workers:** `docs/governance/WORKER_STATUS_TEMPLATE.md` - Status file template

### Step 3: Initial Setup (Workers Do)

Each worker should:
1. Read all required files above
2. Create their status file using the template
3. Review task tracker
4. Confirm understanding of 100% complete rule
5. Begin Day 1 tasks

---

## 🔄 If Prompts Are Updated Later

### If Updates Are Made After Launch:

**Option A: Workers Read Files (Automatic)**
- ✅ Workers automatically see updates when they read files
- No action needed

**Option B: Workers Need Notification (Manual)**
- ⚠️ Overseer must notify workers of updates
- Provide list of changed files
- Ask workers to re-read updated files
- Verify workers acknowledge updates

### Update Notification Template:

```
WORKER UPDATE NOTIFICATION

The following files have been updated:
- [List updated files]

Critical changes:
- [List key changes]

Action required:
1. Re-read your prompt file: [file path]
2. Re-read: [other updated files]
3. Acknowledge you've read the updates
4. Continue with your current task

Please confirm you've read the updates before continuing.
```

---

## ✅ Verification Checklist

### Before Launching Workers:
- [ ] All prompt files updated and committed
- [ ] Memory Bank updated with 100% complete rule
- [ ] NO_STUBS_PLACEHOLDERS_RULE.md created
- [ ] CODE_QUALITY_ANALYSIS.md created
- [ ] Task tracker ready
- [ ] Status template ready

### After Launching Workers:
- [ ] Workers confirm they've read all required files
- [ ] Workers confirm understanding of 100% complete rule
- [ ] Workers have created their status files
- [ ] Workers have reviewed task tracker
- [ ] Workers ready to begin Day 1 tasks

---

## 🎯 Best Practice

**RECOMMENDED:** Have workers read prompt files directly from the repository rather than copying prompts into their session. This ensures:

1. ✅ Workers always have latest version
2. ✅ Updates are automatically available
3. ✅ No need to re-send prompts
4. ✅ Consistency across all workers
5. ✅ Easier maintenance

**How to Implement:**
- Tell workers: "Read your prompt file from: `docs/governance/WORKER_X_PROMPT_*.md`"
- Workers read the file each session/day
- Workers automatically get all updates

---

## 📝 Summary

**Question:** Do workers need new prompts or will they automatically adjust?

**Answer:** 
- **If workers read files:** ✅ They automatically adjust (no action needed)
- **If workers were given prompts once:** ⚠️ They need notification to re-read updated files

**Recommendation:** Have workers read prompt files directly from repository for automatic updates.

---

**Status:** 🟢 Ready for Launch  
**Next Step:** Launch workers with instructions to read prompt files from repository

