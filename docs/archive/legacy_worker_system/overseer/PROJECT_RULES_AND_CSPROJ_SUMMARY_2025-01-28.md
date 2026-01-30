# Project Rules and .csproj Files Summary
## Complete Overview of All Rules and Project Files

**Date:** 2025-01-28  
**Overseer:** ACTIVE  
**Status:** ✅ **COMPREHENSIVE REVIEW COMPLETE**

---

## 📦 .CSPROJ FILES COUNT

**Total .csproj Files:** **3**

### 1. VoiceStudio.App.csproj
**Location:** `src/VoiceStudio.App/VoiceStudio.App.csproj`  
**Type:** WinUI 3 Application  
**Target Framework:** `net8.0-windows10.0.19041.0`  
**Output Type:** WinExe  
**Status:** ✅ **EXISTS**

**Package References:**
- Microsoft.WindowsAppSDK (1.5.240627000)
- Microsoft.Windows.SDK.BuildTools (10.0.26100.1)
- CommunityToolkit.WinUI.UI.Controls (7.1.2)
- CommunityToolkit.Mvvm (8.2.2)

**Project References:**
- VoiceStudio.Core

**Features:**
- XAML page compilation
- app.manifest support
- RuntimeIdentifier error suppression

---

### 2. VoiceStudio.Core.csproj
**Location:** `src/VoiceStudio.Core/VoiceStudio.Core.csproj`  
**Type:** .NET 8 Library  
**Target Framework:** `net8.0`  
**Output Type:** Library  
**Status:** ✅ **EXISTS**

**Package References:**
- None (uses built-in .NET 8 features)

**Project References:**
- None (standalone library)

**Features:**
- ImplicitUsings enabled
- Nullable enabled
- System.Text.Json.Serialization (built-in)

---

### 3. VoiceStudio.App.Tests.csproj
**Location:** `src/VoiceStudio.App.Tests/VoiceStudio.App.Tests.csproj`  
**Type:** MSTest Test Project  
**Target Framework:** `net8.0-windows10.0.19041.0`  
**Output Type:** Library (Test)  
**Status:** ✅ **EXISTS**

**Package References:**
- Microsoft.WindowsAppSDK (1.5.240627000)
- Microsoft.Windows.SDK.BuildTools (10.0.26100.1)
- MSTest.TestAdapter (3.4.3)
- MSTest.TestFramework (3.4.3)
- Microsoft.TestPlatform.TestHost (17.12.0)
- coverlet.collector (6.0.2)

**Project References:**
- VoiceStudio.App (Condition="Exists(...)")
- VoiceStudio.Core (Condition="Exists(...)")

**Features:**
- UI test support ([UITestMethod])
- Unit test support ([TestMethod])
- Code coverage support
- RuntimeIdentifier error suppression

---

## 📋 PROJECT RULES SUMMARY

### Primary Rules Documents

1. **AGENT_SETTINGS_RULES_COMMANDS_2025-01-28.md**
   - Main rules file for Cursor Agent Settings
   - Contains: Absolute Rule, UI Design Rules, Autonomous Workflow, Dependency Installation, Quality Requirements

2. **MASTER_RULES_COMPLETE.md**
   - Complete master reference document
   - Contains: All rules, guidelines, and requirements in full
   - 1250+ lines of comprehensive rules

3. **ALL_PROJECT_RULES.md**
   - Complete compilation of all project rules
   - Contains: No mock outputs, UI/UX integrity, integration rules

4. **UI_UX_INTEGRITY_RULES.md**
   - Design language preservation rules
   - Contains: WinUI 3 native only, docked panels, design consistency, premium details

5. **RECOMMENDED_MARKDOWN_STANDARDS_RULE.md**
   - Markdown formatting standards (MD026 compliance)
   - Contains: No trailing punctuation in headings

---

## 🚨 CRITICAL RULES

### 1. THE ABSOLUTE RULE (HIGHEST PRIORITY)

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**Forbidden Terms:**
- **Bookmarks:** TODO, FIXME, NOTE, HACK, REMINDER, XXX, WARNING, CAUTION, BUG, ISSUE, REFACTOR, OPTIMIZE, REVIEW, CHECK, VERIFY, TEST, DEBUG, DEPRECATED, OBSOLETE, and ALL synonyms
- **Placeholders:** dummy, mock, fake, sample, temporary, test data, filler, placeholder, stub data, example data, and ALL synonyms
- **Stubs:** skeleton, template, outline, empty function, pass statement, unimplemented, stub, empty method, and ALL synonyms
- **Tags:** ALL markup tags, version control tags, code/documentation tags, status/indicator tags
- **Status Words:** pending, incomplete, unfinished, partial, in progress, to do, will be, coming soon, not yet, eventually, later, soon, planned, scheduled, and ALL synonyms
- **Phrases:** "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", and ALL variations

**Applies To:**
- All code files (C#, Python, XAML, JSON, etc.)
- All documentation files (Markdown, text, etc.)
- All configuration files
- All comments in code
- All UI text and labels
- All error messages
- All test files
- All build scripts
- All installer files
- **EVERYTHING**

---

### 2. UI DESIGN RULES

**THE UI DESIGN LAYOUT AND PLANS MUST STAY EXACTLY AS GIVEN FROM CHATGPT.**

**Exact Requirements (NON-NEGOTIABLE):**
- 3-row grid structure (Top Command Deck, Main Workspace, Status Bar)
- 4 PanelHosts (Left, Center, Right, Bottom)
- 64px Nav Rail with 8 toggle buttons
- 48px Command Toolbar
- 26px Status Bar
- VSQ.* design tokens (no hardcoded values)
- MVVM separation (separate .xaml, .xaml.cs, ViewModel.cs files)
- PanelHost UserControl (never replace with raw Grid)

**FORBIDDEN:**
- Changing 3-row grid structure
- Removing PanelHost controls
- Merging View/ViewModel files
- Hardcoded colors, fonts, or spacing
- Simplifying layout
- Reducing panel count

---

### 3. AUTONOMOUS WORKFLOW RULES

**YOU WORK 100% AUTONOMOUSLY. YOU DO NOT PAUSE BETWEEN TASKS. YOU DO NOT WAIT FOR APPROVAL. YOU WORK CONTINUOUSLY UNTIL ALL TASKS ARE COMPLETE.**

**DO NOT:**
- DO NOT PAUSE after completing a task
- DO NOT WAIT for Overseer approval before starting next task
- DO NOT ASK "Should I continue?" or "What's next?"
- DO NOT STOP after each task completion
- DO NOT WAIT for instructions between tasks
- DO NOT REQUEST permission to start next task

**YOU MUST:**
- WORK CONTINUOUSLY - Complete task → Immediately start next task
- WORK AUTONOMOUSLY - Make decisions yourself, don't ask
- WORK THROUGH MULTIPLE TASKS - Complete 5-10 tasks before any pause
- UPDATE FILES AUTOMATICALLY - Update checklist and progress as you go
- CONTINUE UNTIL DONE - Work until all tasks complete or you're truly blocked

**When to Pause (Only These Cases):**
1. All tasks are complete
2. All tasks are blocked (very rare)
3. Critical system error (very rare)

---

### 4. DEPENDENCY INSTALLATION RULE

**ALL dependencies MUST be installed for EVERY task. NO EXCEPTIONS.**

**Requirements:**
- BEFORE starting any task: Check what dependencies are needed
- BEFORE implementing code: Install all required dependencies
- BEFORE marking task complete: Verify all dependencies are installed and working
- NO EXCEPTIONS: Even if a dependency seems optional, if it's needed for the task, install it
- NO SKIPPING: Do not skip dependency installation to save time
- NO ASSUMPTIONS: Do not assume dependencies are already installed - verify and install if needed

**Installation Process:**
1. Identify dependencies (check requirements files, documentation, code imports)
2. Check current installation (verify if dependencies are already installed)
3. Install missing dependencies (use appropriate package manager: pip, NuGet, etc.)
4. Verify installation (test that dependencies work correctly)
5. Document installation (update requirements files if new dependencies added)

**Forbidden:**
- Skipping dependency installation
- Assuming dependencies are installed
- Marking task complete without installing dependencies
- Leaving dependency installation for "later"
- Using "optional" as excuse to skip installation
- Creating code that requires dependencies without installing them

**Verification:**
- All imports work without errors
- All functionality that requires dependencies works
- No "module not found" errors
- No "package not installed" errors
- Requirements files updated with new dependencies

**THIS RULE IS MANDATORY AND HAS NO EXCEPTIONS.**

---

### 5. PROJECT STRUCTURE RULES

**Active Project Root:**
- E:\VoiceStudio - ONLY place where new code and edits are made
- This is the authoritative, active project directory

**Archive/Reference Only (Read-Only):**
- C:\VoiceStudio - Read-only reference
- C:\OldVoiceStudio - Read-only reference
- X:\VoiceStudioGodTier - Read-only reference
- These directories are archive/reference only

**Rules:**
- All new code goes to E:\VoiceStudio
- All edits happen in E:\VoiceStudio
- May read from reference directories
- May NOT modify reference directories
- May NOT bulk copy from reference directories

---

### 6. UI/UX INTEGRITY RULES

**WinUI 3 Native Only:**
- ✅ Use only WinUI 3 controls and XAML
- ✅ Native Windows application (no web technologies)
- ✅ Full native performance and integration
- ❌ React, Electron, webviews, or other frameworks
- ❌ Cross-platform widgets
- ❌ Web-based components
- ❌ Framework migrations

**Docked, Modular Panels:**
- ✅ Follow approved layout: panels must be dockable
- ✅ Panels must be resizable and rearrangeable
- ✅ Main window uses central waveform view with collapsible side panels
- ✅ PanelHost system for all panels
- ✅ 3-column + nav + bottom deck layout maintained

**Design Consistency:**
- ✅ Apply established theme and components (fonts, colors, icons)
- ✅ Use DesignTokens.xaml for ALL styling
- ✅ Maintain clarity and consistency
- ✅ Consistent fonts and spacings
- ✅ Uniform look & feel
- ✅ Visual hierarchy matches style guidelines
- ✅ Feedback cues match style guidelines
- ❌ Hardcoded colors or values
- ❌ Inconsistent styling
- ❌ Random color schemes
- ❌ Mixed design languages

**Design Token Usage:**
- `VSQ.*` resources from DesignTokens.xaml
- No hardcoded colors, typography, or spacing
- Consistent corner radius, shadows, borders
- Theme-aware styling

---

### 7. DOCUMENTATION STANDARDS RULES

**Markdown Formatting Rules (MANDATORY):**

**FORBIDDEN in Markdown Headings:**
- NO trailing punctuation (colons, periods, commas, etc.)
- NO trailing spaces
- NO special characters at end of headings

**Required Markdown Compliance:**
1. **Headings (MD026):** NO trailing punctuation in any heading level (#, ##, ###, etc.)
   - ❌ FORBIDDEN: `### Code Quality Verification:`
   - ✅ CORRECT: `### Code Quality Verification`

2. **Consistency:** All headings must follow same formatting rules
3. **Linting:** All markdown files must pass markdownlint checks
4. **Overseer Reports:** All Overseer-generated documentation must comply

**Verification:**
- Run markdown linter before committing documentation
- Fix all MD026 and other markdown linting errors
- Ensure no trailing punctuation in any heading

**THIS RULE APPLIES TO ALL DOCUMENTATION FILES INCLUDING:**
- Overseer status reports
- Worker progress reports
- Task documentation
- All markdown files in docs/ directory

---

### 8. QUALITY REQUIREMENTS

**Before Marking ANY Task Complete:**
1. All dependencies installed and verified
2. Code is 100% complete and functional
3. All functionality implemented and tested
4. No placeholders, stubs, bookmarks, or tags in ANY form
5. No loophole attempts
6. Code actually works (not just exists)
7. All error cases handled
8. All edge cases considered
9. Production-ready quality

**UI Compliance (if UI task):**
1. 3-row grid structure maintained
2. 4 PanelHosts used (not raw Grid)
3. VSQ.* design tokens used (no hardcoded values)
4. MVVM separation maintained
5. ChatGPT UI specification followed exactly

---

### 9. NO MOCK OUTPUTS OR PLACEHOLDER CODE

**All Cursor agents must write complete, real code with working logic — no mock data, placeholders, stubs, or speculative interfaces unless explicitly instructed.**

**Must Avoid:**
- ❌ `TODO` comments
- ❌ `pass`-only stubs
- ❌ `return {"mock": true}` or fake responses
- ❌ Empty class/function shells with no logic
- ❌ Unimplemented data flows ("assume this works")
- ❌ Mock protocols or fake API responses
- ❌ Hardcoded filler data
- ❌ Speculative implementations

**Required Output Format:**
- ✅ Implement full function bodies, classes, or components
- ✅ Wire UI and backend code together with real bindings or API calls
- ✅ Return real values, real file I/O, real API wiring — not mock protocols
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional and log its usage
- ✅ Use real engine routers, MCPs, or models
- ✅ Perform actual operations (e.g., saving audio, applying effects)

**Completion Criteria:**
- ✅ Verifiable and testable
- ✅ UI panels display actual values or connect to real models, MCPs, or engine routers
- ✅ Backend code performs its intended effect or operation
- ✅ No component marked complete if its implementation is speculative or empty

---

## 📊 RULES DOCUMENTATION STRUCTURE

### Main Rules Files
1. `docs/governance/AGENT_SETTINGS_RULES_COMMANDS_2025-01-28.md` - Cursor Agent Settings content
2. `docs/governance/MASTER_RULES_COMPLETE.md` - Complete master reference (1250+ lines)
3. `docs/governance/ALL_PROJECT_RULES.md` - Complete compilation
4. `docs/governance/UI_UX_INTEGRITY_RULES.md` - UI/UX design preservation
5. `docs/governance/overseer/RECOMMENDED_MARKDOWN_STANDARDS_RULE.md` - Markdown standards

### Additional Rules Files
- `docs/governance/PERIODIC_RULES_REFRESH_SYSTEM.md` - Rules refresh system
- `docs/governance/OVERSEER_UI_RULES_COMPLETE.md` - Overseer-specific UI rules
- `docs/governance/CURSOR_GUARDRAILS.md` - Cursor guardrails
- `docs/design/CURSOR_OPERATIONAL_RULESET.md` - Operational ruleset
- `docs/design/CURSOR_AGENT_GUIDELINES_V2.md` - Agent guidelines
- `docs/design/WORKER_AGENT_PROMPTS.md` - Worker prompts

### Worker-Specific Rules
- `docs/governance/worker1/WORKER_1_RULES_AND_TASKS_SUMMARY_2025-01-28.md` - Worker 1 rules
- Worker 2 and Worker 3 have their own rule sets in respective directories

---

## ✅ VERIFICATION SUMMARY

### .csproj Files
- ✅ **3 .csproj files found** (all exist and properly configured)
  - VoiceStudio.App.csproj ✅
  - VoiceStudio.Core.csproj ✅
  - VoiceStudio.App.Tests.csproj ✅

### Rules Coverage
- ✅ **Absolute Rule** - Highest priority, no exceptions
- ✅ **UI Design Rules** - ChatGPT specification must be followed exactly
- ✅ **Autonomous Workflow** - 100% autonomous, no pauses
- ✅ **Dependency Installation** - Mandatory, no exceptions
- ✅ **Project Structure** - E:\VoiceStudio is active root
- ✅ **UI/UX Integrity** - WinUI 3 native, design tokens, docked panels
- ✅ **Documentation Standards** - Markdown MD026 compliance
- ✅ **Quality Requirements** - Production-ready, 100% complete
- ✅ **No Mock Outputs** - Real code only, no placeholders

---

## 🎯 KEY TAKEAWAYS

1. **3 .csproj files** - All exist and are properly configured
2. **Comprehensive rules** - Multiple layers of enforcement
3. **Highest priority** - The Absolute Rule (100% complete, no placeholders)
4. **UI preservation** - ChatGPT specification must be followed exactly
5. **Autonomous work** - Workers must work continuously without pauses
6. **Dependency mandatory** - All dependencies must be installed
7. **Documentation standards** - Markdown MD026 compliance required
8. **Quality first** - Production-ready code, no shortcuts

---

**Last Updated:** 2025-01-28  
**Status:** ✅ **COMPREHENSIVE REVIEW COMPLETE**
