# VoiceStudio Quantum+ Memory Bank
## Critical Information That Must Never Be Forgotten

**Last Updated:** 2025-01-27  
**Purpose:** Core specifications, guardrails, and architectural decisions that must be preserved across all AI interactions.

**📋 WORKER ROADMAP:** See `docs\governance\WORKER_ROADMAP_DETAILED.md` for complete detailed plan and timeline for all 6 workers.

**📋 NEW GUIDELINES & SYSTEMS:** See `docs\governance\` for new protocols:
- `TASK_LOG.md` - **CENTRAL TASK LOG** - Single source of truth for task assignments and file locks
- `FILE_LOCKING_PROTOCOL.md` - File access coordination (prevents merge conflicts)
- `BRAINSTORMER_PROTOCOL.md` - Idea generation agent rules (read-only)
- `UI_UX_INTEGRITY_RULES.md` - Design language preservation (WinUI 3 native only)
- `DEFINITION_OF_DONE.md` - Completion criteria (no placeholders/TODOs)
- `PERFORMANCE_STABILITY_SAFEGUARDS.md` - Environment protection (resource monitoring)
- `NEW_GUIDELINES_SUMMARY.md` - Complete summary of all new guidelines
- `NO_MOCK_OUTPUTS_RULE.md` - **CRITICAL** - No mock outputs or placeholder code enforcement
- `voice_studio_guidelines.md` - **CURSOR AGENT GUIDELINES** - Direct guidelines for all Cursor agents

**📋 INTEGRATED LOGS & TRACKING:**
- `TASK_TRACKER_3_WORKERS.md` - Detailed worker progress tracking (day-by-day)
- `Migration-Log.md` - Code migration and porting log (source/target paths)
- `WORKER_STATUS_TEMPLATE.md` - Worker status report template
- `WORKER_[N]_STATUS.md` - Individual worker status reports
- `OVERSEER_QUICK_REFERENCE.md` - Overseer quick reference guide

**📋 QUICK START GUIDES:**
- `QUICK_START_GUIDE.md` - Complete quick start for all agents
- `OVERSEER_PROMPT.md` - Ready-to-use Overseer system prompt
- `WORKER_PROMPT.md` - General Worker system prompt (foundation)
- `WORKER_1_PROMPT.md` - Worker 1 specific prompt (Performance, Memory & Error Handling)
- `WORKER_2_PROMPT.md` - Worker 2 specific prompt (UI/UX Polish & User Experience)
- `WORKER_3_PROMPT.md` - Worker 3 specific prompt (Documentation, Packaging & Release)
- `BRAINSTORMER_PROMPT.md` - Ready-to-use Brainstormer system prompt

---

## 🚨 NON-NEGOTIABLE GUARDRAILS

**These rules are ABSOLUTE and must NEVER be violated:**

1. **100% COMPLETE - NO STUBS, PLACEHOLDERS, BOOKMARKS, OR TAGS** ⚠️ **CRITICAL - HIGHEST PRIORITY**
   - ❌ **NEVER** create TODO comments or placeholder code
   - ❌ **NEVER** leave methods with `throw new NotImplementedException()`
   - ❌ **NEVER** create bookmark stubs or "coming soon" comments
   - ❌ **NEVER** use tags like `#TODO`, `#FIXME`, `[PLACEHOLDER]`, `[WIP]`
   - ❌ **NEVER** use status words like "pending", "incomplete", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc"
   - ❌ **NEVER** use phrases like "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress"
   - ❌ **NEVER** mark tasks complete if they contain stubs/placeholders/bookmarks/tags
   - ✅ **ALWAYS** complete each task 100% before moving to the next
   - ✅ **ALWAYS** implement full functionality, not partial implementations
   - ✅ **ALWAYS** test your implementation before marking complete
   - **Rule:** If it's not 100% complete and tested, it's not done. Don't move on.
   - **See:** 
     - `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` - **COMPREHENSIVE RULE** with ALL forbidden terms, patterns, synonyms, and variations
     - `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - Summary rule

2. **Do NOT simplify the UI layout or collapse panels**
   - Keep the 3-column + nav + bottom deck layout
   - Maintain all 4 PanelHost controls (Left, Center, Right, Bottom)
   - Never replace PanelHost with raw Grids

3. **Do NOT merge Views and ViewModels**
   - Each panel = separate `.xaml` + `.xaml.cs` + `ViewModel.cs` files
   - Maintain strict MVVM separation

4. **Do NOT remove placeholder areas**
   - Waveforms, spectrograms, analyzers, macros, logs are future controls, not decoration
   - Preserve all placeholder structures
   - **Note:** This refers to UI structure placeholders, NOT code stubs/placeholders

5. **Use DesignTokens.xaml for ALL styling**
   - No hardcoded colors, typography, or spacing
   - All values must use `VSQ.*` resources

6. **This is a professional DAW-grade app**
   - Adobe/FL Studio level complexity is REQUIRED
   - High density and complexity are intentional, not bugs

**Violation Detection Patterns:**
- TODO/FIXME/NOTE/HACK/REMINDER comments in code → REJECT - Complete implementation required
- NotImplementedException/NotImplementedError → REJECT - Complete implementation required
- Placeholder text/code → REJECT - Complete implementation required
- Tags like #TODO, #FIXME, [PLACEHOLDER], [WIP] → REJECT - Complete implementation required
- Status words like "pending", "incomplete", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc" → REJECT - Complete implementation required
- Phrases like "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress" → REJECT - Complete implementation required
- Merged View/ViewModel files → REVERT
- PanelHost replaced with Grid → REVERT
- Reduced panel count → REVERT
- Hardcoded colors → REVERT
- Simplified layout → REVERT

**📋 COMPLETE LIST:** See `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` for exhaustive list of ALL forbidden patterns.

---

## 🏗️ CORE ARCHITECTURE

### Technology Stack
- **Frontend:** WinUI 3 (.NET 8, C#/XAML)
- **Backend:** Python FastAPI
- **Communication:** REST/WebSocket
- **Pattern:** MVVM (strict separation)

### MainWindow Structure (CANONICAL)
```
3-Row Grid:
├── Row 0: Top Command Deck
│   ├── MenuBar (File, Edit, View, Modules, Playback, Tools, AI, Help)
│   └── Command Toolbar (48px) - Transport, Project, Engine, Performance HUD
│
├── Row 1: Main Workspace
│   └── 4-Column Grid:
│       ├── Column 0: Nav Rail (64px) - 8 toggle buttons
│       ├── Column 1: LeftPanelHost (20% width)
│       ├── Column 2: CenterPanelHost (55% width)
│       └── Column 3: RightPanelHost (25% width)
│   └── Row 1 (Bottom Deck): BottomPanelHost (18% height, spans all columns)
│
└── Row 2: Status Bar (26px) - Status, Job progress, Metrics
```

### PanelHost System (MANDATORY)
- **PanelHost** is a reusable `UserControl` that hosts individual panels
- **4 PanelHosts:** LeftPanelHost, CenterPanelHost, RightPanelHost, BottomPanelHost
- **PanelHost structure:**
  - Header bar (32px) with title and action buttons
  - Body with ContentPresenter
  - Uses VSQ.* design tokens

### Core Panels (6 Required)
1. **ProfilesView** - Voice profile management (LeftPanelHost default)
2. **TimelineView** - Multi-track timeline editor (CenterPanelHost default)
3. **EffectsMixerView** - Audio mixer and effects (RightPanelHost default)
4. **AnalyzerView** - Audio analysis visuals (RightPanelHost alternative)
5. **MacroView** - Macro scripting interface (BottomPanelHost default)
6. **DiagnosticsView** - System monitoring and logs (BottomPanelHost alternative)

**Each panel must have:**
- `PanelNameView.xaml`
- `PanelNameView.xaml.cs`
- `PanelNameViewModel.cs` (implements `IPanelView`)

### Panel Registry System
- **Location:** `VoiceStudio.Core/Panels/`
- **Types:**
  - `PanelRegion` enum (Left, Center, Right, Bottom, Floating)
  - `IPanelView` interface
  - `PanelDescriptor` class
  - `IPanelRegistry` interface
  - `PanelRegistry` implementation

---

## 🎨 DESIGN TOKENS

**File:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`

**Critical Resources:**
- `VSQ.Window.Background` - Window gradient
- `VSQ.Text.PrimaryBrush` - Primary text color
- `VSQ.Text.SecondaryBrush` - Secondary text color
- `VSQ.Accent.CyanBrush` - Accent color
- `VSQ.Panel.BackgroundBrush` - Panel background
- `VSQ.Panel.BorderBrush` - Panel border
- `VSQ.FontSize.Caption/Body/Title/Heading` - Typography sizes
- `VSQ.CornerRadius.Panel/Button` - Corner radius values
- `VSQ.Animation.Duration.Fast/Medium` - Animation durations

**Rule:** ALL styling must reference these tokens. NO hardcoded values.

---

## 📁 FILE STRUCTURE (CANONICAL)

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 frontend
│   │   ├── App.xaml                  # Merges DesignTokens.xaml
│   │   ├── MainWindow.xaml          # 3-row grid with 4 PanelHosts
│   │   ├── Resources/
│   │   │   └── DesignTokens.xaml    # All VSQ.* resources
│   │   ├── Controls/
│   │   │   └── PanelHost.xaml        # Reusable panel container
│   │   └── Views/Panels/
│   │       └── [6 core panels, each with .xaml, .xaml.cs, ViewModel.cs]
│   │
│   └── VoiceStudio.Core/             # Shared library
│       └── Panels/
│           └── [Panel registry types]
│
└── backend/
    └── api/                          # Python FastAPI
        └── [Backend services]
```

**Rule:** This structure is CANONICAL. Do not simplify or merge files.

---

## 🔧 BACKEND ENGINE SYSTEM

### Unlimited Extensibility

**VoiceStudio has NO hardcoded engine limits. Add as many engines as you need.**

- ✅ **Manifest-based discovery** - Engines automatically discovered from `engine.manifest.json` files
- ✅ **No code changes** - Just add manifest and engine class
- ✅ **Dynamic API** - Lists engines automatically, no hardcoded lists
- ✅ **Plugin architecture** - Each engine is independent
- ✅ **Protocol-based** - All engines implement `EngineProtocol` interface

**See:** `docs\design\ENGINE_EXTENSIBILITY.md` for complete extensibility guide

### Recommended Engines

**Primary TTS Engines:**
- **Chatterbox TTS** - Primary, state-of-the-art quality
- **Coqui TTS (XTTS)** - Primary, flexible framework
- **Tortoise TTS** - Optional HQ render mode

**Primary Transcription Engines:**
- **Whisper (faster-whisper)** - Default STT engine
- **whisper.cpp** - CPU-only fallback
- **WhisperX** - Advanced features (word timestamps, diarization)
- **Vosk** - Low-end machine fallback

**Optimization:**
- **PyTorch** - Primary framework
- **ONNX Runtime** - Optimized deployment
- **CTranslate2** - Whisper acceleration

**All engines are offline, local-first, no API keys required.**

**Note:** These are recommendations, not limits. Add any engine you need!

### Local-First Architecture Principle

**CRITICAL:** VoiceStudio uses APIs ONLY for what cannot be done locally.

**What Runs Locally (100%):**
- ✅ All voice cloning engines (XTTS, Chatterbox, Tortoise)
- ✅ All quality metrics calculation
- ✅ All audio processing
- ✅ All file I/O
- ✅ All model inference
- ✅ All data storage

**What We DON'T Use:**
- ❌ External voice synthesis APIs (OpenAI, ElevenLabs, etc.)
- ❌ Cloud-based processing
- ❌ Online model inference
- ❌ External API keys
- ❌ Remote services

**Architecture:**
- Frontend: Native Windows (WinUI 3)
- Backend: Local Python FastAPI (localhost)
- Engines: Local PyTorch models
- Storage: Local filesystem
- Communication: localhost only

**See:** `docs\governance\PROGRESS_REPORT_LOCAL_FIRST.md` for complete local-first verification

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: Shell & Layout ✅
- WinUI 3 project structure
- DesignTokens.xaml
- MainWindow with 4 PanelHosts
- 6 core panel skeletons

### Phase 2: Styling & Micro-Interactions
- Centralized styles
- NavIconButton control
- Panel swapping on nav click
- Hover/focus states

### Phase 3: Docking & Layout Persistence
- PanelRegistry implementation
- Layout save/restore
- Nav integration with PanelRegistry

### Phase 4-10: [See PHASE_ROADMAP_COMPLETE.md]

---

## 🎯 KEY DECISIONS

1. **PanelHost is MANDATORY** - Never replace with raw Grids
2. **Multiple panels visible simultaneously** - Not single-panel navigation
3. **Professional DAW-grade complexity** - Not a demo or tutorial
4. **Strict MVVM separation** - Never merge View/ViewModel
5. **Design tokens for everything** - No hardcoded styling
6. **Local-first architecture** - All engines run offline
7. **Plugin system** - Engines as backend plugins

---

## 🎁 OPTIONAL ADD-INS (Pre-Cursor Launch)

### 1. PanelStack System ✅ IMPLEMENTED
- **Purpose:** Allow multiple panels per PanelHost region (tabbed interface)
- **Files:** `Controls/PanelStack.xaml`, `PanelStack.xaml.cs`
- **Usage:** PanelHost can contain either single panel OR PanelStack
- **Benefits:** Macros + Logs in bottom, Studio + Profiles in left, etc.

### 2. Command Palette ✅ IMPLEMENTED
- **Purpose:** Searchable quick action UI (Ctrl+P)
- **Files:** `Controls/CommandPalette.xaml`, `Services/ICommandRegistry.cs`
- **Usage:** Global keyboard shortcut, fuzzy search, category grouping
- **Benefits:** Fast access to all actions, keeps UI complex but usable

### 3. Multi-Window Workspace ✅ IMPLEMENTED
- **Purpose:** Pop out panels as independent windows
- **Files:** `Controls/FloatingWindowHost.xaml`, `Services/WindowHostService.cs`
- **Usage:** Power users can use second screen for Analyzer/Logs
- **Status:** Complete - ready for integration

### 4. Per-Panel Settings ✅ IMPLEMENTED
- **Purpose:** Right-click settings menu per panel
- **Files:** `Core/Panels/IPanelConfigurable.cs`, `Services/PanelSettingsStore.cs`
- **Usage:** Panels implement IPanelConfigurable for contextual settings
- **Status:** Complete - ready for integration

### 5. UI Test Hooks ✅ IMPLEMENTED
- **Purpose:** Automation IDs for testing frameworks
- **Files:** `Helpers/AutomationHelper.cs`, `docs/design/UI_TEST_HOOKS.md`
- **Usage:** `#if DEBUG` blocks with AutomationHelper.SetAutomationId
- **Benefits:** Enables Spectron, Appium, WinAppDriver integration
- **Status:** Complete - helper class and documentation ready

**See:** `PRE_CURSOR_ADDINS.md` for details

### 6. Advanced UI/UX Features (Recommended)
- **Documentation:** `ADVANCED_UI_UX_FEATURES.md`
- **Priority Features:**
  - Keyboard Shortcuts System
  - Drag-and-Drop Support
  - Context Menus
  - AI Quality Feedback UI (for 3 AI + Overseer setup)
  - Customizable Workspaces
  - Advanced Undo/Redo
  - Accessibility Features
- **AI Integration:** Special features for quality monitoring and overseer guidance

---

## 📚 REFERENCE DOCUMENTS

### Original UI Specification (CRITICAL - MUST PRESERVE)
- **`ORIGINAL_UI_SCRIPT_CHATGPT.md`** - **CRITICAL** - Original ChatGPT/User UI script - **THIS IS THE SOURCE OF TRUTH**
- **`VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`** - **CRITICAL** - Complete original specification with full XAML code (source document)
- **`UI_IMPLEMENTATION_SPEC.md`** - Detailed UI implementation specification

### Core Specifications
- `ENGINE_RECOMMENDATIONS.md` - Backend engine choices
- `PHASE_ROADMAP_COMPLETE.md` - 10-phase development plan
- `GLOBAL_GUARDRAILS.md` - Detailed guardrails and violations
- `EXECUTION_PLAN.md` - Overseer + 8 Worker agent plan
- `PRE_CURSOR_ADDINS.md` - Optional add-ins documentation
- `PANELSTACK_USAGE.md` - PanelStack usage guide
- `COMMAND_PALETTE_USAGE.md` - Command Palette usage guide

---

## ⚠️ COMMON VIOLATIONS TO WATCH FOR

1. **"Let's simplify this"** → REJECT - Complexity is required
2. **"We can merge these files"** → REJECT - Separation is mandatory
3. **"PanelHost is unnecessary"** → REJECT - It's the foundation
4. **"Hardcoded values are fine"** → REJECT - Use design tokens
5. **"This is too complex"** → REJECT - Professional apps are complex
6. **"We can reduce panel count"** → REJECT - All 6 are required

---

## 📋 WORKER ROADMAP & PLANNING

**All workers must reference:**
- `docs\governance\WORKER_COMPLETION_CHECKLIST.md` - **CRITICAL** - 100% completion checklist (260 tasks with checkboxes)
  - Explicit completion criteria for each worker
  - Task-by-task tracking
  - Progress percentage calculation
  - Phase 0 success criteria

- `docs\governance\WORKER_ROADMAP_DETAILED.md` - **COMPLETE DETAILED PLAN** for all 6 workers
  - Day-by-day task breakdown
  - Step-by-step instructions
  - Dependencies and timelines
  - Success criteria for each task
  - Inter-worker coordination

**Additional planning documents:**
- `docs\governance\WORKER_BRIEFING.md` - Worker briefing with priorities
- `docs\governance\WORKER_PROMPTS_LAUNCH.md` - Launch instructions
- `docs\governance\DEVELOPMENT_ROADMAP.md` - Overall development plan

---

## 🛡️ PERFORMANCE & STABILITY SAFEGUARDS

**CRITICAL:** These safeguards ensure the Cursor environment remains stable and responsive during multi-agent development.

### 1. Monitor Resource Usage

**Requirements:**
- Track CPU/GPU/memory usage for each agent process
- Use Cursor's agent dashboard (if available) to monitor resource stats
- If agent's resource usage spikes abnormally → Pause or reset to avoid degradation

**Thresholds:**
- CPU > 80% sustained → Pause and report
- Memory > 2GB per agent → Review and optimize
- GPU > 90% → Throttle operations

### 2. Staggered Access

**File/Resource Access:**
- If multiple agents need same file → Implement retries/backoff
- If Agent A has locked file → Agent B should sleep briefly before retrying (NOT tight loop)
- Prevents busy-waiting and race conditions

**Retry Pattern:**
- Exponential backoff (increasing delay)
- Maximum retry limit (e.g., 5 attempts)
- Report to Overseer if stuck
- No tight loops (busy-waiting)

### 3. Loop/Time Limits

**Prevent Infinite Loops:**
- Set sensible limits in prompts/tasks
- Instruct agents to break if no progress after N iterations
- Overseer detects and intervenes if agent stuck repeating step

**Example Limits:**
- Maximum iterations per loop: 1000
- Maximum execution time per task: 30 minutes
- Maximum retry attempts: 5

### 4. Logging Cooldowns

**Limit Log Verbosity:**
- Avoid logging same progress message every second
- Batch or throttle logs (e.g., at most one update per few seconds)
- Keep logs readable and essential information only

**Log Throttling:**
- ERROR: Always log
- WARNING: Log with cooldown
- INFO: Batch updates (max 1 per 5 seconds)
- DEBUG: Disable in production

### 5. Fail-Safes

**Crash/Hang Handling:**
- If agent crashes or hangs → Overseer terminates and possibly restarts
- System should fail gracefully (e.g., roll back partial changes if commit fails)
- Preserve work in progress
- No data loss

**See:** `docs/governance/PERFORMANCE_STABILITY_SAFEGUARDS.md` for complete details

---

## 📋 QUICK START & PROMPTS

**📋 ALL PROJECT RULES:** See `docs/governance/ALL_PROJECT_RULES.md` - **COMPLETE RULES REFERENCE** - All rules in one place

**All agents must use these ready-to-use prompts:**
- `docs/governance/QUICK_START_GUIDE.md` - **START HERE** - Complete quick start for all agents
- `docs/governance/OVERSEER_PROMPT.md` - Ready-to-use Overseer system prompt
- `docs/governance/WORKER_PROMPT.md` - Ready-to-use Worker system prompt
- `docs/governance/BRAINSTORMER_PROMPT.md` - Ready-to-use Brainstormer system prompt

**All agents must follow these workflows:**
1. Read Memory Bank first (`docs/design/MEMORY_BANK.md`)
2. Load appropriate system prompt
3. Check `TASK_LOG.md` for assignments
4. Follow file locking protocol
5. Update progress daily
6. Verify Definition of Done before completion

---

## 🔄 WHEN IN DOUBT

1. Check `docs/governance/ALL_PROJECT_RULES.md` - **COMPLETE RULES REFERENCE**
2. Check `docs/design/MEMORY_BANK.md` - **ALWAYS CHECK THIS FIRST**
3. Check `docs/governance/QUICK_START_GUIDE.md` - Complete workflow guide
4. Check `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`
5. Verify against `GLOBAL_GUARDRAILS.md`
6. Check `WORKER_ROADMAP_DETAILED.md` for your specific tasks
7. Ensure PanelHost structure is preserved
8. Confirm design tokens are used
9. Maintain strict MVVM separation
10. Check `TASK_LOG.md` for file locks and assignments

**Remember: This is a professional DAW-grade application. Complexity and modularity are features, not bugs.**

