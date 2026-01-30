# Master Rules - VoiceStudio Quantum+ Complete Ruleset
## All Rules, Guidelines, and Requirements in Full

**Date:** 2025-01-28  
**Status:** COMPLETE - Master Reference Document  
**Purpose:** Single source of truth for ALL project rules  
**Version:** 1.0

---

## 📋 TABLE OF CONTENTS

1. [The Absolute Rule - NO Stubs/Placeholders/Bookmarks/Tags](#1-the-absolute-rule)
2. [Dependency Installation Rule - ALWAYS Install Dependencies](#2-dependency-installation-rule)
3. [UI Design Rules - ChatGPT Specification](#3-ui-design-rules)
4. [Integration Rules](#4-integration-rules)
5. [Code Quality Rules](#5-code-quality-rules)
   - [Correctness Over Speed Rule](#-correctness-over-speed-rule---highest-priority)
6. [Architecture Rules](#6-architecture-rules)
7. [Worker Rules](#7-worker-rules)
8. [Overseer Rules](#8-overseer-rules)
9. [Enforcement Rules](#9-enforcement-rules)
10. [Periodic Refresh System](#10-periodic-refresh-system)

---

## 1. THE ABSOLUTE RULE

### 🚨 THE MAIN RULE - HIGHEST PRIORITY

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**This rule applies to:**
- ✅ All code files (C#, Python, XAML, JSON, etc.)
- ✅ All documentation files (Markdown, text, etc.)
- ✅ All configuration files
- ✅ All comments in code
- ✅ All UI text and labels
- ✅ All error messages
- ✅ All test files
- ✅ All build scripts
- ✅ All installer files
- ✅ **EVERYTHING**

---

### ❌ FORBIDDEN TERMS AND PATTERNS

#### 1. Bookmarks (FORBIDDEN)

**Explicit incomplete markers only:**
- TODO, FIXME, HACK, XXX, TBD, TBA, TBC, WIP

**Examples of FORBIDDEN usage:**
- `// TODO: Implement this`
- `// FIXME: Fix this later`
- `// HACK: Temporary workaround`
- `// XXX: Important`
- `// WIP`

#### 2. Placeholders (FORBIDDEN)

**Explicit non-functional markers only:**
- `NotImplementedError`, `NotImplementedException`
- `pass` as the only statement in a concrete function
- Placeholder tags like `[PLACEHOLDER]`, `[TODO]`, `[FIXME]`, `[WIP]`
- Deliberate placeholder responses in production paths

**Examples of FORBIDDEN usage:**
- `return {"mock": true}` in production paths
- `throw new NotImplementedException();`
- `pass` in non-abstract methods

#### 3. Stubs (FORBIDDEN)

**Explicit non-implemented bodies only:**
- Empty method bodies in non-abstract types
- Methods/functions that only throw NotImplemented exceptions
- Function signatures without behavior

#### 4. Tags (FORBIDDEN)

**Incomplete-work tags only:**
- `#TODO`, `#FIXME`, `#TBD`, `#WIP`, or any tag explicitly indicating unfinished work

#### 5. Status Words and Phrases (FORBIDDEN)

**Explicit incomplete markers only:**
- "to be implemented", "to be done", "not implemented yet", "will be implemented later"
- `TBD`, `TBA`, `TBC`, `WIP`

---

### 🚫 LOOPHOLE PREVENTION - NO WORKAROUNDS ALLOWED

Do not obfuscate the explicit incomplete markers above via capitalization, spacing, punctuation, encoding, naming tricks, or string concatenation.

**NO EXCEPTIONS. NO WORKAROUNDS. NO LOOPHOLES.**

---

### ✅ WHAT IS REQUIRED

#### Code Requirements:
- ✅ Full implementation of all methods
- ✅ All functionality working and tested
- ✅ All error cases handled
- ✅ All edge cases considered
- ✅ Tests written and passing (if applicable)
- ✅ Real values, real file I/O, real API wiring
- ✅ Complete function bodies, classes, or components
- ✅ UI and backend wired together with real bindings or API calls
- ✅ Verifiable and testable functionality
- ✅ Production-ready code
- ✅ No speculative implementations
- ✅ No "assume this works" comments
- ✅ No hardcoded filler data

#### Documentation Requirements:
- ✅ Complete content, not outlines
- ✅ All examples work and are tested
- ✅ All procedures tested
- ✅ All links verified
- ✅ No empty sections
- ✅ No "TODO: Add content here"
- ✅ No placeholder text

#### UI Requirements:
- ✅ All controls functional
- ✅ All interactions work
- ✅ All states implemented
- ✅ All animations complete
- ✅ No "Placeholder" text in UI
- ✅ No disabled buttons that never work
- ✅ No "Coming soon" messages
- ✅ No empty states that say "TODO"

#### Exception for Testing:
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- ✅ Log mock usage clearly
- ✅ Never use mocks in production code paths
- ✅ Test mocks must be clearly marked and isolated

---

### 🔍 VERIFICATION CHECKLIST

**Before Marking ANY Task Complete:**

1. **Search your code for ALL forbidden patterns:**
   - [ ] Bookmarks (TODO, FIXME, HACK, XXX, TBD, TBA, TBC, WIP - all variations)
   - [ ] Placeholders (NotImplementedError, NotImplementedException, [PLACEHOLDER], [TODO], [FIXME], [WIP], pass-only bodies, placeholder responses)
   - [ ] Stubs (empty bodies in non-abstract types, NotImplemented-only bodies, signature-only functions)
   - [ ] Tags (#TODO, #FIXME, #TBD, #WIP - all variations)
   - [ ] Status Words ("to be implemented", "to be done", "not implemented yet", "will be implemented later", TBD/TBA/TBC/WIP - all variations)
   - [ ] Loophole Prevention Patterns (capitalization, spacing, punctuation, comment style, string concatenation, naming tricks, encoding, whitespace, regex, context)

2. **Functional Testing:**
   - [ ] Does the code actually work?
   - [ ] Are all cases handled?
   - [ ] Are there any errors?
   - [ ] Is it production-ready?
   - [ ] Can it be tested?
   - [ ] Does it perform the actual intended function?

**If you find ANY of these patterns:**
- 🚨 **STOP IMMEDIATELY**
- 🚨 **COMPLETE THE IMPLEMENTATION**
- 🚨 **TEST IT**
- 🚨 **THEN** mark as complete

---

### 🚨 CONSEQUENCES OF VIOLATION

**If Stubs/Placeholders/Bookmarks/Tags Found:**

1. **Task marked as INCOMPLETE**
2. **Worker must complete before moving on**
3. **No credit for partial work**
4. **May delay overall timeline**
5. **Commit rejected** (if using automated checks)
6. **Release blocked** (if found in release candidate)

**Why This Matters:**

- **Quality:** Stubs create technical debt
- **Reliability:** Placeholders can cause bugs
- **User Experience:** Incomplete features frustrate users
- **Maintainability:** Future workers waste time on stubs
- **Professionalism:** Production code must be complete
- **Trust:** Incomplete code erodes trust in the system
- **Efficiency:** Finding and fixing stubs later is more expensive than doing it right the first time

---

## 2. UI DESIGN RULES

### 🚨 THE UI DESIGN LAYOUT AND PLANS MUST STAY EXACTLY AS GIVEN FROM CHATGPT

**Source of Truth:**
- **`docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md`** - Original ChatGPT/User collaboration UI script
- **`docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`** - Complete original specification with full XAML code

**Framework:** WinUI 3 (.NET 8, C#/XAML) - **NOT** React/TypeScript, **NOT** Python GUI

---

### NON-NEGOTIABLE UI GUARDRAILS

#### Rule 1: Layout Complexity - DO NOT SIMPLIFY
```
❌ DO NOT reduce 3-column + nav + bottom deck layout
❌ DO NOT remove any PanelHost controls
❌ DO NOT collapse panels into single views
✅ MUST maintain MainWindow 3-Row Grid structure
✅ MUST have 4 PanelHosts: Left, Center, Right, Bottom
✅ MUST have 64px Nav Rail (8 toggle buttons)
✅ MUST have 48px Command Toolbar
✅ MUST have 26px Status Bar
```

#### Rule 2: MVVM Separation - DO NOT MERGE
```
❌ DO NOT merge View and ViewModel files
❌ DO NOT combine .xaml + .xaml.cs + ViewModel.cs
✅ MUST have separate files for every panel:
   - PanelNameView.xaml
   - PanelNameView.xaml.cs
   - PanelNameViewModel.cs (implements IPanelView)
```

#### Rule 3: PanelHost Control - DO NOT REPLACE
```
❌ DO NOT replace PanelHost with raw Grid
❌ DO NOT inline panel content in MainWindow
✅ MUST use PanelHost UserControl for all panels
✅ MUST maintain PanelHost structure (header 32px + content area)
```

#### Rule 4: Design Tokens - DO NOT HARDCODE
```
❌ DO NOT use hardcoded colors, fonts, or spacing
❌ DO NOT create new color schemes
✅ MUST use VSQ.* resources from DesignTokens.xaml
✅ MUST reference design tokens for ALL styling
```

#### Rule 5: Professional Complexity - REQUIRED
```
❌ DO NOT simplify "for clarity"
❌ DO NOT reduce panel count
❌ DO NOT remove placeholder areas
✅ MUST maintain Adobe/FL Studio level complexity
✅ MUST keep all 6 core panels
✅ MUST preserve all placeholder regions
```

---

### MAINWINDOW STRUCTURE (CANONICAL - NEVER CHANGE)

**Structure (3-Row Grid):**

```
MainWindow.xaml
└── Grid (3 Rows)
    ├── Row 0: Top Command Deck (Auto height)
    │   ├── MenuBar
    │   │   └── MenuItems: File, Edit, View, Modules, Playback, Tools, AI, Help
    │   └── Command Toolbar (48px height)
    │       ├── Column 0: Transport (Play, Pause, Stop, Record, Loop)
    │       ├── Column 1: Project name + Engine selector
    │       ├── Column 2: Undo/Redo + Workspace dropdown
    │       └── Column 3: Performance HUD (CPU, GPU, Latency bars)
    │
    ├── Row 1: Main Workspace (*)
    │   └── Grid (4 Columns, 2 Rows)
    │       ├── Column 0: Nav Rail (64px width)
    │       │   └── Vertical Stack: 8 toggle buttons
    │       │       ├── Studio
    │       │       ├── Profiles
    │       │       ├── Library
    │       │       ├── Effects
    │       │       ├── Train
    │       │       ├── Analyze
    │       │       ├── Settings
    │       │       └── Logs
    │       │
    │       ├── Row 0, Column 1: LeftPanelHost (20% width)
    │       │   └── Default: ProfilesView
    │       │
    │       ├── Row 0, Column 2: CenterPanelHost (55% width)
    │       │   └── Default: TimelineView
    │       │
    │       ├── Row 0, Column 3: RightPanelHost (25% width)
    │       │   └── Default: EffectsMixerView
    │       │
    │       └── Row 1, Columns 0-3: BottomPanelHost (18% height, spans all)
    │           └── Default: MacroView
    │
    └── Row 2: Status Bar (26px height, Auto)
        └── Grid (3 Columns)
            ├── Column 0 (*): Status text ("Ready")
            ├── Column 1 (2*): Job progress (Job name + progress bar)
            └── Column 2 (*): Mini meters (CPU, GPU, RAM) + Clock
```

**Critical Dimensions:**
- **Window Default:** 1600×900
- **Nav Rail:** 64px width (fixed)
- **Command Toolbar:** 48px height (fixed)
- **Status Bar:** 26px height (fixed)
- **Left Panel:** 20% width (resizable)
- **Center Panel:** 55% width (resizable)
- **Right Panel:** 25% width (resizable)
- **Bottom Panel:** 18% height (resizable)

---

### PANELHOST STRUCTURE (MANDATORY)

**Each PanelHost MUST have:**
- **Header Bar:** 32px height
  - Icon (Segoe MDL2 glyph)
  - Title text
  - Pop-out button (stub)
  - Collapse button
  - Options button (MenuFlyout)
- **Body:** ContentPresenter with Border
  - CornerRadius: 8px (VSQ.CornerRadius.Panel)
  - BorderBrush: VSQ.Panel.BorderBrush
  - BorderThickness: 1px

---

### DESIGN TOKENS (DesignTokens.xaml)

**Critical Resources - MUST USE:**

#### Colors (VSQ.*)
```
VSQ.Background.Darker: #FF0A0F15
VSQ.Background.Dark: #FF121A24
VSQ.Accent.Cyan: #FF00B7C2
VSQ.Accent.Lime: #FF9AFF33
VSQ.Accent.Magenta: #FFB040FF
VSQ.Text.Primary: #FFCDD9E5
VSQ.Text.Secondary: #FF8A9BB3
VSQ.Border.Subtle: #26FFFFFF
VSQ.Warn: #FFFFB540
VSQ.Error: #FFFF4060
```

#### Brushes (VSQ.*Brush)
```
VSQ.Window.Background: LinearGradientBrush (Dark → Darker)
VSQ.Text.PrimaryBrush: SolidColorBrush
VSQ.Text.SecondaryBrush: SolidColorBrush
VSQ.Accent.CyanBrush: SolidColorBrush
VSQ.Panel.BackgroundBrush: SolidColorBrush
VSQ.Panel.BorderBrush: SolidColorBrush
```

#### Typography (VSQ.Font.*)
```
VSQ.Font.Caption: 10
VSQ.Font.Body: 12
VSQ.Font.Title: 16
VSQ.Font.Heading: 20
```

#### Styles (VSQ.Text.*)
```
VSQ.Text.Body: FontSize=12, Foreground=Primary
VSQ.Text.Caption: FontSize=10, Foreground=Secondary
VSQ.Text.Title: FontSize=16, Foreground=Primary, SemiBold
VSQ.Text.Heading: FontSize=20, Foreground=Primary, Bold
```

#### Constants (VSQ.*)
```
VSQ.CornerRadius.Panel: 8
VSQ.CornerRadius.Button: 4
VSQ.Animation.Duration.Fast: 100ms
VSQ.Animation.Duration.Medium: 150ms
VSQ.Animation.Duration.Slow: 300ms
```

---

### 6 CORE PANELS (REQUIRED)

1. **ProfilesView** - LeftPanelHost default
   - Tabs: Profiles / Library (32px header)
   - Left: Profiles grid (WrapGrid, 180×120 cards)
   - Right: Detail inspector (260px width)

2. **TimelineView** - CenterPanelHost default
   - Toolbar (32px): Add Track, Zoom, Grid settings
   - Tracks area (*): ItemsControl with track templates
   - Visualizer (160px): Spectrogram/visualizer placeholder

3. **EffectsMixerView** - RightPanelHost default
   - Mixer (60%): Horizontal ItemsControl with mixer strips
   - FX Chain (40%): Node view / FX chain placeholder

4. **AnalyzerView** - RightPanelHost alternative
   - Tabs (32px): Waveform, Spectral, Radar, Loudness, Phase
   - Chart area (*): Placeholder for chart rendering

5. **MacroView** - BottomPanelHost default
   - Tabs (32px): Macros / Automation
   - Node graph canvas (*): Placeholder for node-based macro system

6. **DiagnosticsView** - BottomPanelHost alternative
   - Logs (60%): ListView with log entries
   - Metrics charts (40%): CPU, GPU, RAM progress bars

---

### VIOLATION DETECTION & REMEDIATION

**If you detect ANY of these violations, issue immediate remediation:**

1. **Merged View/ViewModel files** → REVERT
2. **PanelHost replaced with Grid** → REVERT
3. **Reduced panel count** → REVERT
4. **Hardcoded colors** → REVERT
5. **Simplified layout** → REVERT

**REMEDIATION COMMAND:**
"Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to ChatGPT specification. Do not merge or collapse."

---

## 4. INTEGRATION RULES

### INTEGRATION POLICY

**Principles:**
- ✅ **ONLY** integrate what enhances the current project
- ✅ **EXTRACT CONCEPTS** from different frameworks and convert to WinUI 3/C#
- ✅ **MAINTAIN** exact ChatGPT UI specification (layout structure)
- ✅ **ENHANCE** functionality without changing UI structure
- ✅ **ADAPT** features, patterns, and logic from any framework to WinUI 3/C#
- ✅ **CONVERT** concepts and ideas from any language/framework to our current stack
- ✅ **LEARN FROM** all implementations regardless of framework - extract what's useful
- ✅ **NEVER EXCLUDE** based on framework - always consider conversion/adaptation
- ✅ **PRINCIPLE:** Different UI framework ≠ Exclusion. Extract concepts and implement in our stack.

**Convertible/Adaptable Items:**
- React/TypeScript frontend (`C:\OldVoiceStudio\frontend\`) - **CONVERTIBLE** (extract concepts, implement in WinUI 3/C#)
- Python GUI implementations (`C:\OldVoiceStudio\gui\`) - **CONVERTIBLE** (extract panel concepts, implement in WinUI 3/C#)

**Conversion Approach:**
- Extract concepts, features, patterns, and logic
- Implement in WinUI 3/C# following ChatGPT UI specification
- Maintain exact layout structure (3-row grid, 4 PanelHosts, Nav rail, etc.)
- Use MVVM pattern, DesignTokens.xaml, and PanelHost UserControl

**See:** `docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md` for complete integration priorities and guidelines

---

## 4. CODE QUALITY RULES

### 🚨 CORRECTNESS OVER SPEED RULE - HIGHEST PRIORITY

**THE FUNDAMENTAL PRINCIPLE:**

**Do not prioritize speed or task count. Your only priority is to produce the correct solution, even if it takes longer or results in fewer changes. Never rush or cut corners.**

**This rule applies to:**
- ✅ All code implementations
- ✅ All task completions
- ✅ All bug fixes
- ✅ All feature additions
- ✅ All refactoring
- ✅ All testing
- ✅ All documentation
- ✅ **EVERYTHING**

**Requirements:**
- ✅ **Take the time needed** to implement correctly
- ✅ **Do it right the first time** - no shortcuts
- ✅ **Quality over quantity** - fewer correct tasks is better than many incomplete tasks
- ✅ **Thoroughness over speed** - complete understanding before implementation
- ✅ **Verification before completion** - verify correctness before marking done
- ✅ **No rushing** - if it takes longer, it takes longer
- ✅ **No cutting corners** - implement fully, test thoroughly, verify completely

**Forbidden:**
- ❌ Rushing to complete more tasks
- ❌ Cutting corners to save time
- ❌ Skipping verification to move faster
- ❌ Incomplete implementations to increase task count
- ❌ "Good enough" solutions
- ❌ Quick fixes that don't address root causes
- ❌ Assuming something works without testing
- ❌ Marking tasks complete without verification

**Examples:**
- ✅ **CORRECT:** Take 2 days to implement correctly → Verify it works → Mark complete
- ✅ **CORRECT:** Implement 1 task perfectly → Test thoroughly → Document → Move to next
- ❌ **WRONG:** Rush through 5 tasks → Leave placeholders → Mark all complete
- ❌ **WRONG:** Quick implementation → Skip testing → Mark complete to move faster

**Remember:**
- **One correct implementation is worth more than ten incomplete ones**
- **Time spent doing it right is never wasted**
- **Quality cannot be rushed**
- **Correctness is the only metric that matters**

**This rule is MANDATORY and has NO EXCEPTIONS.**

---

### PRODUCTION-READY CODE

**All code must be:**
- ✅ Fully implemented (no stubs, placeholders, bookmarks, tags)
- ✅ Tested and working
- ✅ Error handling included
- ✅ Edge cases considered
- ✅ Production-ready quality
- ✅ Real implementations (no mocks in production)
- ✅ Verifiable and testable

### REAL IMPLEMENTATIONS ONLY

**Forbidden:**
- ❌ Mock outputs in return values
- ❌ `{"mock": true}` or similar fake responses
- ❌ `pass`-only stubs (Python)
- ❌ Hardcoded filler data
- ❌ Speculative implementations
- ❌ "Assume this works" comments

**Required:**
- ✅ Real API calls to backend services
- ✅ Real file I/O operations
- ✅ Real engine/router connections
- ✅ UI connected to real data sources
- ✅ All operations perform actual work
- ✅ Test mode mocks (if any) clearly marked and logged

**Exception for Testing:**
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- ✅ Log mock usage clearly
- ✅ Never use mocks in production code paths
- ✅ Test mocks must be clearly marked and isolated

### DEPENDENCY INSTALLATION RULE

**🚨 CRITICAL RULE - NO EXCEPTIONS:**

**ALL dependencies MUST be installed for EVERY task. NO EXCEPTIONS.**

**This rule applies to:**
- ✅ Python packages (pip install)
- ✅ .NET packages (NuGet)
- ✅ System dependencies (FFmpeg, etc.)
- ✅ Engine-specific dependencies
- ✅ Development dependencies
- ✅ Testing dependencies
- ✅ **EVERY dependency required for the task**

**Requirements:**
- ✅ **BEFORE starting any task:** Check what dependencies are needed
- ✅ **BEFORE implementing code:** Install all required dependencies
- ✅ **BEFORE marking task complete:** Verify all dependencies are installed and working
- ✅ **NO EXCEPTIONS:** Even if a dependency seems optional, if it's needed for the task, install it
- ✅ **NO SKIPPING:** Do not skip dependency installation to save time
- ✅ **NO ASSUMPTIONS:** Do not assume dependencies are already installed - verify and install if needed

**Installation Process:**
1. **Identify dependencies:** Check requirements files, documentation, code imports
2. **Check current installation:** Verify if dependencies are already installed
3. **Install missing dependencies:** Use appropriate package manager (pip, NuGet, etc.)
4. **Verify installation:** Test that dependencies work correctly
5. **Document installation:** Update requirements files if new dependencies added

**Forbidden:**
- ❌ Skipping dependency installation
- ❌ Assuming dependencies are installed
- ❌ Marking task complete without installing dependencies
- ❌ Leaving dependency installation for "later"
- ❌ Using "optional" as excuse to skip installation
- ❌ Creating code that requires dependencies without installing them

**Verification:**
- ✅ All imports work without errors
- ✅ All functionality that requires dependencies works
- ✅ No "module not found" errors
- ✅ No "package not installed" errors
- ✅ Requirements files updated with new dependencies

**Examples:**
- ✅ **CORRECT:** Task requires `librosa` → Install `librosa` → Verify import works → Implement code
- ✅ **CORRECT:** Task requires `fairseq` for RVC → Install `fairseq` → Test RVC engine → Complete task
- ❌ **WRONG:** Task requires `pesq` → Skip installation → Write code that imports `pesq` → Mark complete
- ❌ **WRONG:** Task requires `pedalboard` → Assume it's installed → Code fails → Mark complete anyway

**This rule is MANDATORY and has NO EXCEPTIONS.**

---

## 5. ARCHITECTURE RULES

### WINDOWS NATIVE APPLICATION

**✅ YES - This is a Windows Native Program:**
- **Framework:** WinUI 3 (Windows App SDK)
- **Language:** C# (.NET 8)
- **UI Markup:** XAML
- **Platform:** Windows Desktop Application
- **Target:** Windows 10 17763+ / Windows 11
- **Architecture:** Native Windows application, NOT web-based

**❌ NOT:**
- ❌ NOT a web app (no Electron, no browser)
- ❌ NOT a cross-platform framework (WinUI 3 is Windows-only)
- ❌ NOT a hybrid app (fully native Windows)

### LOCAL-FIRST ARCHITECTURE

**Principle:** 100% Local-First - APIs only used for what cannot be done locally

**All engines run locally:**
- ✅ XTTS Engine (Coqui TTS) - Runs locally with PyTorch
- ✅ Chatterbox TTS Engine - Runs locally with PyTorch
- ✅ Tortoise TTS Engine - Runs locally for HQ mode
- ✅ All engines integrated, tested, and working locally

**All quality analysis runs locally:**
- ✅ MOS Score calculation (local)
- ✅ Voice similarity metrics (local)
- ✅ Naturalness analysis (local)
- ✅ SNR calculation (local)
- ✅ Artifact detection (local)

**Backend API runs locally:**
- ✅ All endpoints run locally
- ✅ No external API calls
- ✅ No API keys required
- ✅ No cloud services
- ✅ Communication: `localhost:8000` (internal)

### WORKSPACE SETUP

**Active Repository (Authoritative):**
- **`E:\VoiceStudio`** - **ONLY** place where code is written
- This is the **active, authoritative project directory**
- All modifications, creations, and updates happen here
- This is the **primary working directory**

**Reference Repository (Read-Only):**
- **`C:\VoiceStudio`** - **Read-only reference** (if present)
- **`C:\OldVoiceStudio`** - **Read-only reference** (if present)
- These directories are **archive/reference only**

**Cursor MUST:**
1. **Set workspace to `E:\VoiceStudio`** when opening Cursor
2. **Treat `E:\VoiceStudio` as the ONLY place for changes:**
   - All new code goes here
   - All edits happen here
   - All file creation happens here
   - This is the authoritative source
3. **Treat `C:\VoiceStudio` and `C:\OldVoiceStudio` as read-only reference:**
   - ✅ **MAY** open and read files there
   - ✅ **MAY** reference code/patterns from there
   - ✅ **MAY** use as inspiration or reference
   - ❌ **MAY NOT** modify or create files there
   - ❌ **MAY NOT** bulk copy directories from there into `E:\VoiceStudio`
   - ❌ **MAY NOT** write to these directories

---

## 6. WORKER RULES

### WORKER RESPONSIBILITIES

**Worker 1 (Backend/Engines):**
- Backend API development
- Engine integration
- Quality metrics implementation
- Performance optimization
- Audio processing

**Worker 2 (UI/UX):**
- WinUI 3/C# frontend development
- Panel implementation
- Design token usage
- MVVM pattern adherence
- UI/UX polish

**Worker 3 (Testing/Quality):**
- Testing implementation
- Quality verification
- Documentation
- Packaging and deployment

### WORKER REQUIREMENTS

**All Workers MUST:**
- ✅ Read `docs/governance/MASTER_RULES_COMPLETE.md` before starting
- ✅ Read `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` (if UI work)
- ✅ Follow the NO stubs/placeholders/bookmarks/tags rule
- ✅ **Install ALL dependencies for EVERY task (NO EXCEPTIONS)**
- ✅ Complete tasks 100% before moving on
- ✅ Verify completion before marking tasks done
- ✅ Use periodic refresh system (see Section 9)

**Dependency Installation (MANDATORY):**
- ✅ **BEFORE starting any task:** Identify and install all required dependencies
- ✅ **BEFORE implementing code:** Verify all dependencies are installed
- ✅ **BEFORE marking task complete:** Verify all dependencies work correctly
- ✅ **NO EXCEPTIONS:** Install dependencies even if they seem optional
- ✅ **NO SKIPPING:** Do not skip dependency installation
- ✅ **NO ASSUMPTIONS:** Verify dependencies are installed, don't assume

---

## 7. OVERSEER RULES

### OVERSEER RESPONSIBILITIES

**The Overseer MUST:**
- ✅ Enforce all rules and guardrails
- ✅ Verify workers have refreshed rules
- ✅ Check for rule violations
- ✅ Reject incomplete work
- ✅ Ensure UI specification compliance
- ✅ Coordinate worker tasks
- ✅ Maintain quality standards
- ✅ Verify 100% completion before task approval

### VIOLATION DETECTION

**If violations found:**
1. **Immediate:** Revert violating changes
2. **Reminder:** Refresh critical rules
3. **Verification:** Confirm understanding
4. **Prevention:** Strengthen refresh schedule if needed

---

## 8. ENFORCEMENT RULES

### AUTOMATED ENFORCEMENT

**Pre-Commit Checks:**
- Run automated checks before committing
- Reject commits containing forbidden patterns
- Provide clear error messages

**Pre-Release Checks:**
- Full codebase scan before release
- Block release if violations found
- Generate violation report

**Continuous Monitoring:**
- Regular automated scans
- Alert on violations
- Track violation trends

### MANUAL ENFORCEMENT

**Overseer Review:**
- Check all code changes
- Verify rule compliance
- Reject incomplete work

**Worker Self-Verification:**
- Workers must verify their own work
- Search for forbidden patterns
- Test functionality before marking complete

**Code Reviews:**
- Peer review of all changes
- Focus on rule compliance
- Verify 100% completion

---

## 9. PERIODIC REFRESH SYSTEM

**PRIMARY REFERENCE:** `docs/governance/MASTER_RULES_COMPLETE.md` - **ALL INSTANCES MUST USE THIS AS PRIMARY REFERENCE**

**This document (`MASTER_RULES_COMPLETE.md`) contains ALL rules, ALL forbidden terms (including ALL synonyms and variations), and ALL loophole prevention patterns. This prevents instances from using similar-meaning words to bypass the rule.**

### REFRESH SCHEDULE

**1. Session Start Refresh**
- **When:** At the beginning of every new AI session
- **Action:** Read the master rules document
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - **MUST READ FIRST AND COMPLETELY**
    - Contains ALL rules in full
    - Contains ALL forbidden terms, synonyms, and variations
    - Contains ALL loophole prevention patterns
    - Contains UI design rules
    - Contains integration rules
    - Contains all other project rules

**2. Task Start Refresh**
- **When:** Before starting any new task
- **Action:** Review relevant sections of master rules document
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Review relevant sections:
    - Section 1: The Absolute Rule (for all tasks)
    - Section 2: UI Design Rules (for UI tasks)
    - Section 3: Integration Rules (for integration tasks)
    - Section 4: Code Quality Rules (for all code tasks)
    - Section 5: Architecture Rules (for architecture tasks)

**3. Periodic Refresh (Every 30 Minutes)**
- **When:** During long sessions, refresh every 30 minutes
- **Action:** Quick review of critical sections
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Quick review:
    - Section 1: The Absolute Rule (forbidden terms and patterns)
    - Section 2: UI Design Rules (if UI work)
    - Section 9: Periodic Refresh System (this section)

**4. Before Code Changes**
- **When:** Before making any code changes
- **Action:** Verify compliance with rules
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Review:
    - Section 1: The Absolute Rule - Verification Checklist
    - Section 1: The Absolute Rule - Loophole Prevention
    - Section 1: The Absolute Rule - All Forbidden Terms (complete list)
- **Check:**
  - No stubs, placeholders, bookmarks, or tags (including ALL synonyms and variations)
  - No loophole attempts (capitalization, spacing, punctuation, etc.)
  - UI changes follow ChatGPT specification exactly
  - Code is 100% complete and functional

**5. Before Task Completion**
- **When:** Before marking a task as complete
- **Action:** Final verification against all rules
- **PRIMARY DOCUMENT:**
  - **`docs/governance/MASTER_RULES_COMPLETE.md`** - Final verification:
    - Section 1: The Absolute Rule - Verification Checklist (complete all checks)
    - Section 1: The Absolute Rule - All Forbidden Terms (search for ALL variations)
    - Section 1: The Absolute Rule - Loophole Prevention (check for ALL workarounds)
- **Check:**
  - All functionality implemented (no placeholders, including ALL synonyms)
  - No forbidden terms in ANY form (including ALL variations and workarounds)
  - UI follows exact ChatGPT specification
  - All rules followed

### CRITICAL DOCUMENTS TO REFRESH

**PRIMARY REFERENCE (MUST USE):**
- **`docs/governance/MASTER_RULES_COMPLETE.md`** - **PRIMARY REFERENCE FOR ALL INSTANCES**
  - Contains ALL rules in full
  - Contains ALL forbidden terms (bookmarks, placeholders, stubs, tags, status words)
  - Contains ALL synonyms and variations
  - Contains ALL loophole prevention patterns
  - Contains UI design rules
  - Contains integration rules
  - Contains code quality rules
  - Contains architecture rules
  - Contains worker rules
  - Contains overseer rules
  - Contains enforcement rules
  - Contains periodic refresh system

**Secondary References (For Specific Details):**
- `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` - Original ChatGPT UI specification (source of truth)
- `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Complete original specification with full XAML code
- `docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md` - Integration priorities and guidelines
- `docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md` - Enforcement strategies

**See:** `docs/governance/PERIODIC_RULES_REFRESH_SYSTEM.md` for complete refresh system details

---

## 🎯 REMEMBER

**The UI design layout and plans MUST stay exactly as given from ChatGPT.**

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**Refresh yourself on these rules regularly. Don't forget. Don't deviate.**

**Quality over speed. Completeness over progress. Correctness over task count.**

**Do not prioritize speed or task count. Your only priority is to produce the correct solution, even if it takes longer or results in fewer changes. Never rush or cut corners.**

**This rule applies to ALL workers, ALL tasks, ALL the time.**

**NO EXCEPTIONS.**

---

## 📚 REFERENCE DOCUMENTS

**For complete details, see:**
- `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` - Complete forbidden terms list
- `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` - Original ChatGPT UI specification
- `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Complete original specification
- `docs/governance/OVERSEER_UI_RULES_COMPLETE.md` - Complete UI rules
- `docs/governance/COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md` - Integration priorities
- `docs/governance/PERIODIC_RULES_REFRESH_SYSTEM.md` - Periodic refresh system
- `docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md` - Enforcement strategies

---

**Last Updated:** 2025-01-28  
**Status:** COMPLETE - Master Rules Document  
**Version:** 1.0

