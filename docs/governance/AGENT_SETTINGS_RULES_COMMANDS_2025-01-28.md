# Agent Settings - Rules and Commands
## Complete Content for Cursor Agent Settings Tab

**Date:** 2025-01-28  
**Status:** READY FOR USE  
**Purpose:** Exact content to paste into Cursor's Agent Settings → Rules and Commands tab

---

## 🎯 WHY USE AGENT SETTINGS

**Benefits:**
- ✅ Rules are always available to AI instances
- ✅ Provides another layer of enforcement
- ✅ Ensures rules are loaded at session start
- ✅ Complements the prompt system
- ✅ Acts as a safety net

**Use BOTH:**
- Agent Settings (Rules and Commands tab) - Always loaded
- System Prompts (from prompt files) - Detailed instructions

---

## 📋 RULES TAB CONTENT

**Paste this into the "Rules" section:**

```
# VoiceStudio Quantum+ - Critical Rules

## THE ABSOLUTE RULE - HIGHEST PRIORITY

EVERY task must be 100% complete before moving to the next task.

NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.

ALL synonyms and variations are FORBIDDEN. Using similar-meaning words to bypass the rule is FORBIDDEN.

## FORBIDDEN TERMS (ALL Synonyms Included)

### Bookmarks (ALL Synonyms):
FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE, marker, flag, indicator, annotation, reference point, anchor, checkpoint, waypoint, signpost, milestone marker, pointer, reference, sticky note, bookmark, reminder marker, fix marker, work marker, return marker, later marker, revisit marker, follow-up marker, and ALL other synonyms

### Placeholders (ALL Synonyms):
dummy, mock, fake, sample, temporary, test data, filler, placeholder, stub data, example data, demonstration data, pseudocode, skeleton data, empty data, null data, blank data, default data, NotImplementedError, NotImplementedException, np.zeros(), return {}, return [], return null, and ALL other synonyms

### Stubs (ALL Synonyms):
skeleton, template, outline, empty function, pass statement, unimplemented, stub, empty method, blank function, void function, null implementation, no-op, no operation, function signature only, and ALL other synonyms

### Tags (ALL Categories):
ALL markup tags, version control tags, code/documentation tags, status/indicator tags, system/metadata tags, API/service tags, tracking/monitoring tags, social/collaboration tags, content/organizational tags

### Status Words (ALL Synonyms):
pending, incomplete, unfinished, partial, in progress, to do, will be, coming soon, not yet, eventually, later, soon, planned, scheduled, assigned, open, active, ongoing, under construction, under development, in development, work in progress, WIP, draft, rough, prototype, experimental, alpha, beta, preview, pre-release, needs, requires, missing, absent, empty, blank, null, void, tbd, tba, tbc, and ALL other synonyms

### Phrases (ALL Variations):
"to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress", "needs to be", "requires to be", "missing implementation", and ALL other variations

### Loophole Prevention:
ALL capitalization variations, spacing variations, punctuation variations, abbreviation variations, language variations, encoding variations, comment style variations, string concatenation variations, variable/function name variations, emoji/unicode variations, whitespace variations, regex/pattern variations, context variations, negation variations, meta-reference variations, indirect reference variations, time-based variations, scope variations, priority variations, status variations

## UI DESIGN RULES

THE UI DESIGN LAYOUT AND PLANS MUST STAY EXACTLY AS GIVEN FROM CHATGPT.

### Exact Requirements (NON-NEGOTIABLE):
- 3-row grid structure (Top Command Deck, Main Workspace, Status Bar)
- 4 PanelHosts (Left, Center, Right, Bottom)
- 64px Nav Rail with 8 toggle buttons
- 48px Command Toolbar
- 26px Status Bar
- VSQ.* design tokens (no hardcoded values)
- MVVM separation (separate .xaml, .xaml.cs, ViewModel.cs files)
- PanelHost UserControl (never replace with raw Grid)

### FORBIDDEN:
- Changing 3-row grid structure
- Removing PanelHost controls
- Merging View/ViewModel files
- Hardcoded colors, fonts, or spacing
- Simplifying layout
- Reducing panel count

## AUTONOMOUS WORKFLOW RULES

YOU WORK 100% AUTONOMOUSLY. YOU DO NOT PAUSE BETWEEN TASKS. YOU DO NOT WAIT FOR APPROVAL. YOU WORK CONTINUOUSLY UNTIL ALL TASKS ARE COMPLETE.

### DO NOT:
- DO NOT PAUSE after completing a task
- DO NOT WAIT for Overseer approval before starting next task
- DO NOT ASK "Should I continue?" or "What's next?"
- DO NOT STOP after each task completion
- DO NOT WAIT for instructions between tasks
- DO NOT REQUEST permission to start next task

### YOU MUST:
- WORK CONTINUOUSLY - Complete task → Immediately start next task
- WORK AUTONOMOUSLY - Make decisions yourself, don't ask
- WORK THROUGH MULTIPLE TASKS - Complete 5-10 tasks before any pause
- UPDATE FILES AUTOMATICALLY - Update checklist and progress as you go
- CONTINUE UNTIL DONE - Work until all tasks complete or you're truly blocked

### When to Pause (Only These Cases):
1. All tasks are complete
2. All tasks are blocked (very rare)
3. Critical system error (very rare)

## PROJECT STRUCTURE

### Active Project Root:
- E:\VoiceStudio - ONLY place where new code and edits are made
- This is the authoritative, active project directory

### Archive/Reference Only (Read-Only):
- C:\VoiceStudio - Read-only reference
- C:\OldVoiceStudio - Read-only reference
- X:\VoiceStudioGodTier - Read-only reference
- These directories are archive/reference only

### Rules:
- All new code goes to E:\VoiceStudio
- All edits happen in E:\VoiceStudio
- May read from reference directories
- May NOT modify reference directories
- May NOT bulk copy from reference directories

## DEPENDENCY INSTALLATION RULE

ALL dependencies MUST be installed for EVERY task. NO EXCEPTIONS.

### Requirements:
- BEFORE starting any task: Check what dependencies are needed
- BEFORE implementing code: Install all required dependencies
- BEFORE marking task complete: Verify all dependencies are installed and working
- NO EXCEPTIONS: Even if a dependency seems optional, if it's needed for the task, install it
- NO SKIPPING: Do not skip dependency installation to save time
- NO ASSUMPTIONS: Do not assume dependencies are already installed - verify and install if needed

### Installation Process:
1. Identify dependencies (check requirements files, documentation, code imports)
2. Check current installation (verify if dependencies are already installed)
3. Install missing dependencies (use appropriate package manager: pip, NuGet, etc.)
4. Verify installation (test that dependencies work correctly)
5. Document installation (update requirements files if new dependencies added)

### Forbidden:
- Skipping dependency installation
- Assuming dependencies are installed
- Marking task complete without installing dependencies
- Leaving dependency installation for "later"
- Using "optional" as excuse to skip installation
- Creating code that requires dependencies without installing them

### Verification:
- All imports work without errors
- All functionality that requires dependencies works
- No "module not found" errors
- No "package not installed" errors
- Requirements files updated with new dependencies

THIS RULE IS MANDATORY AND HAS NO EXCEPTIONS.

## QUALITY REQUIREMENTS

### Before Marking ANY Task Complete:
1. All dependencies installed and verified
2. Code is 100% complete and functional
3. All functionality implemented and tested
4. No placeholders, stubs, bookmarks, or tags in ANY form
5. No loophole attempts
6. Code actually works (not just exists)
7. All error cases handled
8. All edge cases considered
9. Production-ready quality

### UI Compliance (if UI task):
1. 3-row grid structure maintained
2. 4 PanelHosts used (not raw Grid)
3. VSQ.* design tokens used (no hardcoded values)
4. MVVM separation maintained
5. ChatGPT UI specification followed exactly

## REFERENCE DOCUMENTS

Primary Reference: docs/governance/MASTER_RULES_COMPLETE.md
Roadmap: docs/governance/NEW_COMPREHENSIVE_ROADMAP_2025-01-28.md
Task Distribution: docs/governance/BALANCED_TASK_DISTRIBUTION_3_WORKERS_2025-01-28.md
UI Specification: docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md
```

---

## 📋 COMMANDS TAB CONTENT

**Paste this into the "Commands" section:**

```
# VoiceStudio Quantum+ - Commands

## VERIFICATION COMMANDS

### Verify Rules Compliance:
- Check code for ALL forbidden terms (bookmarks, placeholders, stubs, tags, status words, phrases)
- Check for loophole attempts (capitalization, spacing, punctuation variations)
- Verify no placeholders, stubs, bookmarks, or tags exist
- Run verification checks before marking task complete

### Verify UI Compliance:
- Check 3-row grid structure is maintained
- Check 4 PanelHosts are used (not raw Grid)
- Check VSQ.* design tokens are used (no hardcoded values)
- Check MVVM separation is maintained
- Verify exact ChatGPT UI specification is followed

### Verify Dependencies:
- All required dependencies are installed
- All imports work without errors
- No "module not found" or "package not installed" errors
- Requirements files updated if new dependencies added
- Dependencies verified and working

### Verify Functionality:
- Code actually works (not just exists)
- All functionality implemented
- All error cases handled
- All edge cases considered
- Production-ready quality

## WORKFLOW COMMANDS

### Start Work:
1. Read tasks from BALANCED_TASK_DISTRIBUTION_3_WORKERS_2025-01-28.md
2. Identify ALL assigned tasks
3. Identify ALL required dependencies for tasks
4. Install ALL required dependencies BEFORE starting
5. Start with first task immediately
6. DO NOT wait for approval

### Complete Task:
1. Verify task is 100% complete
2. Run verification checks
3. Update MASTER_TASK_CHECKLIST.md
4. Update progress file
5. IMMEDIATELY start next task (do not pause)

### Work Continuously:
- Complete Task 1 → Update → Task 2 → Update → Task 3 → Update → Task 4...
- Work through 5-10 tasks before any pause
- Only pause if all tasks complete or all tasks blocked

## FILE OPERATIONS

### Update Checklist:
- Mark task as COMPLETE in MASTER_TASK_CHECKLIST.md
- Include completion date
- Include notes if needed

### Update Progress:
- Create/update docs/governance/progress/WORKER_[1|2|3]_[DATE].json
- Include: worker, date, status, current_task, tasks_completed_today, progress_percentage, notes, blockers, next_tasks

### Read Reference Documents:
- docs/governance/MASTER_RULES_COMPLETE.md - Primary reference
- docs/governance/NEW_COMPREHENSIVE_ROADMAP_2025-01-28.md - Roadmap
- docs/governance/BALANCED_TASK_DISTRIBUTION_3_WORKERS_2025-01-28.md - Tasks
- docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md - UI specification

## QUALITY COMMANDS

### Before Completing Task:
1. Install and verify all required dependencies
2. Check for forbidden terms
3. Verify functionality works
4. Verify UI compliance (if UI task)
5. Verify code compiles/runs
6. Verify production-ready quality

### If Violation Detected:
1. STOP immediately
2. REVERT violating changes
3. FIX the violation
4. RE-RUN verification checks
5. Only mark complete when 100% fixed

## PROJECT COMMANDS

### Read Reference Code:
- May read from C:\VoiceStudio, C:\OldVoiceStudio, X:\VoiceStudioGodTier
- May NOT modify reference directories
- May NOT bulk copy from reference directories

### Write Code:
- All new code goes to E:\VoiceStudio
- All edits happen in E:\VoiceStudio
- Follow project structure exactly

### Integration:
- Extract concepts from old projects
- Convert to WinUI 3/C# (if from different framework)
- Maintain exact ChatGPT UI specification
- Enhance without degrading
```

---

## 🎯 HOW TO USE

### Step 1: Open Cursor Settings
1. Open Cursor
2. Go to Settings (or Preferences)
3. Find "Agent" or "AI" section
4. Look for "Rules" and "Commands" tabs

### Step 2: Paste Rules
1. Open "Rules" tab
2. Copy content from "RULES TAB CONTENT" section above
3. Paste into Rules field
4. Save

### Step 3: Paste Commands
1. Open "Commands" tab
2. Copy content from "COMMANDS TAB CONTENT" section above
3. Paste into Commands field
4. Save

### Step 4: Verify
1. Start new chat/instance
2. Verify rules are loaded
3. Test with a simple query to confirm rules are active

---

## 📊 BENEFITS

**Using Agent Settings Provides:**
- ✅ **Always Available** - Rules loaded at every session start
- ✅ **Safety Net** - Complements prompt system
- ✅ **Consistency** - Same rules for all instances
- ✅ **Enforcement** - Another layer of rule enforcement
- ✅ **Quick Reference** - Easy access to key rules

**Combined with Prompts:**
- Agent Settings = Always-loaded rules (safety net)
- System Prompts = Detailed instructions (full context)
- Together = Maximum enforcement and clarity

---

## 🔄 MAINTENANCE

### When to Update:
- When rules change
- When new forbidden terms discovered
- When workflow changes
- When UI requirements change

### How to Update:
1. Update this document
2. Update Agent Settings in Cursor
3. Update system prompts
4. Notify all instances to refresh

---

## ✅ CHECKLIST

**Before Starting Work:**
- [ ] Rules pasted into Agent Settings → Rules tab
- [ ] Commands pasted into Agent Settings → Commands tab
- [ ] Settings saved
- [ ] Verified rules are loaded in new instance
- [ ] System prompts also loaded (complementary)

---

**Last Updated:** 2025-01-28  
**Status:** READY FOR USE  
**Version:** 1.0

