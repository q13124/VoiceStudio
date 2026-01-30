# VoiceStudio Quantum+ - Complete Ruleset
## All Rules, Guardrails, and Guidelines

**Last Updated:** 2025-01-27  
**Purpose:** Comprehensive reference for all rules governing VoiceStudio development

---

## 🚨 NON-NEGOTIABLE GUARDRAILS

### 1. Do NOT Simplify UI Layout
- ❌ **DO NOT** collapse panels or merge views
- ❌ **DO NOT** reduce panel count
- ❌ **DO NOT** hide "unused" panels
- ❌ **DO NOT** remove placeholder areas
- ✅ **DO** preserve 3-column + nav + bottom deck layout
- ✅ **DO** maintain PanelHost controls
- ✅ **DO** keep dense, dockable panels
- ✅ **DO** preserve panel hierarchy
- ✅ **DO** maintain Adobe/Resolve/FL-style layout

**Rationale:** Professional DAW-grade complexity is REQUIRED. High density and complexity are intentional, not bugs.

### 2. Do NOT Merge Views and ViewModels
- ❌ **DO NOT** merge Views and ViewModels "to be faster"
- ❌ **DO NOT** combine .xaml + .xaml.cs + ViewModel.cs into single file
- ✅ **DO** have separate files: `.xaml`, `.xaml.cs`, `ViewModel.cs` for every panel
- ✅ **DO** maintain strict MVVM pattern separation

**File Structure Required:**
```
Views/Panels/
  ├── ProfilesView.xaml
  ├── ProfilesView.xaml.cs
  ├── ProfilesViewModel.cs
  ├── TimelineView.xaml
  ├── TimelineView.xaml.cs
  ├── TimelineViewModel.cs
  └── ... (repeat for all panels)
```

**Rationale:** Enables independent testing, code reusability, future extensibility to 100+ panels, team collaboration.

### 3. PanelHost Control is MANDATORY
- ❌ **DO NOT** replace custom PanelHost with direct Grids
- ❌ **DO NOT** inline panel content directly in MainWindow
- ✅ **DO** use PanelHost UserControl for all panels
- ✅ **DO** maintain PanelHost structure (header + content area)

**Rationale:** PanelHost provides consistent styling, header controls (pop-out, collapse, options), future drag-docking support, panel swapping infrastructure.

### 4. Do NOT Remove Placeholder Areas
- ❌ **DO NOT** collapse or remove placeholder areas
- ❌ **DO NOT** hide waveform, spectrogram, node graph, or chart regions
- ✅ **DO** keep all placeholder areas visibly distinct in the UI

**Required Placeholders:**
- **TimelineView**: Waveform lanes, spectrogram/visualizer area
- **EffectsMixerView**: Fader controls, FX chain area
- **AnalyzerView**: Chart placeholder for each tab
- **MacroView**: Node graph canvas area
- **DiagnosticsView**: Log list, metrics charts

**Rationale:** These placeholders show the intended UI structure, guide future implementation, maintain visual consistency, help users understand the application layout.

### 5. Design Tokens are MANDATORY
- ❌ **DO NOT** use random colors or hardcoded values
- ❌ **DO NOT** create new color schemes
- ✅ **DO** use VSQ.* resources from DesignTokens.xaml
- ✅ **DO** follow the design system consistently

**Required Resources:**
- `VSQ.Background.Darker`, `VSQ.Background.Dark`
- `VSQ.Accent.Cyan`, `VSQ.Accent.Lime`, `VSQ.Accent.Magenta`
- `VSQ.Text.Primary`, `VSQ.Text.Secondary`
- `VSQ.Panel.BorderBrush`
- `VSQ.CornerRadius.Panel`, `VSQ.CornerRadius.Button`
- `VSQ.Text.Body`, `VSQ.Text.Caption`, `VSQ.Text.Title`, `VSQ.Text.Heading`

**Rationale:** Design tokens ensure visual consistency, easy theme switching, maintainable styling, professional appearance.

### 6. Core Library Separation
- ❌ **DO NOT** put business logic in the App project
- ❌ **DO NOT** duplicate interfaces or models
- ✅ **DO** use VoiceStudio.Core for shared code
- ✅ **DO** reference Core from App project

**Core Library Contains:**
- Panel registry interfaces
- Data models (VoiceProfile, AudioClip, MeterReading)
- Service interfaces (IBackendClient)
- Shared enums (PanelRegion)

**Rationale:** Separation enables independent testing of core logic, reuse across multiple frontends, clear API boundaries, future backend integration.

### 7. Backend Architecture
- ❌ **DO NOT** implement backend logic in the frontend
- ❌ **DO NOT** hardcode API endpoints
- ✅ **DO** use IBackendClient interface
- ✅ **DO** follow shared contract schemas

**Required Structure:**
```
backend/
  api/              # FastAPI/Express
  mcp_bridge/       # MCP integration
  models/           # TTS, VC, Whisper
shared/
  contracts/        # JSON schemas
```

**Rationale:** Enables backend flexibility (Python/Node), supports MCP integration, maintains API contracts, allows independent deployment.

---

## 📍 PROJECT ROOTS & SCOPE

### Active Project Root (Authoritative)
- **`E:\VoiceStudio`** - **ONLY** place where new code and edits are made
- This is the **authoritative, active project directory**
- All modifications, creations, and updates happen here
- This is the **primary working directory**

### Archive / Reference Only (Read-Only)
- **`C:\VoiceStudio`** - Read-only reference (if present)
- **`C:\OldVoiceStudio`** - Read-only reference (if present)
- These directories are **archive/reference only**

### Cursor MUST:

1. **Treat `E:\VoiceStudio` as the ONLY place for changes:**
   - All new code goes here
   - All edits happen here
   - All file creation happens here
   - This is the authoritative source

2. **Treat `C:\VoiceStudio` and `C:\OldVoiceStudio` as read-only reference:**
   - ✅ **MAY** open and read files there
   - ✅ **MAY** reference code/patterns from there
   - ✅ **MAY** use as inspiration or reference
   - ❌ **MAY NOT** modify or create files there
   - ❌ **MAY NOT** bulk copy directories from there into `E:\VoiceStudio`
   - ❌ **MAY NOT** write to these directories

3. **Smart Reference Usage:**
   - When referencing legacy code:
     - Read and understand the pattern
     - Recreate/adapt in `E:\VoiceStudio` (not copy)
     - Ensure compatibility with new architecture
     - Update to match current standards

4. **Migration Approach:**
   - If importing from reference directories:
     - Read the file/pattern
     - Create new version in `E:\VoiceStudio`
     - Update to match current architecture
     - Verify compatibility
     - Do not bulk copy

---

## 🎯 GENERAL PRINCIPLES

### Precision & Professionalism
- **Maintain a high standard of quality** in every deliverable
- All outputs should be **meticulously aligned** with the project's premium-grade vision
- Ensure an **advanced, feature-rich, and information-dense UI**
- No shortcuts or simplifications that compromise quality

### Iterative Process
- Break tasks into manageable **"blocks"** (typically 50 blocks per cycle)
- Each block should be:
  - **Self-contained**
  - **Clearly defined**
  - **Executable by Cursor without ambiguity**
- Provide feedback after each block for the next iteration

### Compatibility First
- Always ensure code, components, or configurations comply with **"UltraClone Governance"** standards
- Verify **pinned dependencies and architecture** before making changes
- If unsure about a new dependency or update, **perform a compatibility check**
- Reference `TECHNICAL_STACK_SPECIFICATION.md` for version requirements

### Non-Destructive Changes
- Ensure the system is **not broken by any change**
- Each modification should be:
  - **Incremental**
  - **Reversible if needed**
- Test after each change to verify functionality

### Avoid Over-Simplification
- Adhere strictly to the **"Full-Fidelity Mode"** directive
- Keep every UI element, functionality, and interaction **as complex and sophisticated as possible**
- **Do NOT simplify** unless explicitly requested
- Reference `GLOBAL_GUARDRAILS.md` for anti-simplification rules

### Follow the Master Plan
- All tasks, UI components, backend features, and integrations must align with the **VoiceStudio Master Plan**
- Do not deviate from the plan unless explicitly instructed by the overseer
- Reference `PHASE_ROADMAP_COMPLETE.md` for phase structure

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
- ❌ Online services for core functionality

---

## 🚨 CRITICAL RULES (Non-Negotiable)

### Preservation Rules
1. **NEVER delete existing files** without explicit instruction
2. **NEVER remove existing functionality**
3. **NEVER remove existing data bindings**
4. **NEVER remove existing event handlers**
5. **NEVER replace existing code unnecessarily**

### Architecture Rules
1. **PanelHost is MANDATORY** - Never replace with raw Grids
2. **MVVM separation** - No logic in code-behind
3. **Design tokens** - No hardcoded colors/sizes
4. **PanelRegistry** - All panels must be registered
5. **IPanelView** - All ViewModels must implement interface

### Simplification Rules
1. **Do NOT collapse panels** or merge layouts
2. **Do NOT merge Views and ViewModels**
3. **Do NOT replace PanelHost** with raw Grids
4. **Do NOT remove placeholder areas** (they're future controls)
5. **Do NOT simplify UI** for "speed" or "convenience"

---

## 📋 IMPLEMENTATION CHECKLIST

When implementing or modifying code, verify:

- [ ] All 6 panels exist with separate View/ViewModel files
- [ ] MainWindow uses 3×2 grid layout
- [ ] All panels use PanelHost control
- [ ] All placeholders are visible and distinct
- [ ] All colors use VSQ.* design tokens
- [ ] Core library is separate and referenced
- [ ] File structure matches canonical tree
- [ ] No files merged "for simplicity"
- [ ] All work done in E:\VoiceStudio (not C:\VoiceStudio)
- [ ] Legacy code recreated (not copied) from C:\VoiceStudio

---

## 🔄 REMEDIATION COMMANDS

If violations detected:

```
Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to CIS. Do not merge or collapse.

Specific violations:
- [List violations]

Required actions:
1. Restore PanelHost control (if replaced)
2. Separate merged View/ViewModel files
3. Restore panel count to 6
4. Restore 3×2 grid layout
5. Restore all placeholder regions
6. Use VSQ.* design tokens only
7. Ensure all work is in E:\VoiceStudio
```

---

## 📚 REFERENCE DOCUMENTS

### Must Read Before Starting
1. **MEMORY_BANK.md** - Critical information
2. **GLOBAL_GUARDRAILS.md** - Anti-simplification rules
3. **TECHNICAL_STACK_SPECIFICATION.md** - Version requirements
4. **CURSOR_MASTER_INSTRUCTIONS.md** - Integration guide

### Implementation Guides
1. **PANEL_IMPLEMENTATION_GUIDE.md** - Panel development
2. **SKELETON_INTEGRATION_GUIDE.md** - Integration process
3. **PHASE_ROADMAP_COMPLETE.md** - Phase structure

### Architecture
1. **VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md** - Master spec
2. **architecture/README.md** - Canonical architecture index (Parts 1–9)
3. **architecture/Part6_State_Data.md** - State & data flow
4. **ENGINE_RECOMMENDATIONS.md** - Backend engines

---

## ✅ PRE-EXECUTION CHECKLIST

Before executing any task, verify:

- [ ] Read relevant documentation
- [ ] Check version compatibility
- [ ] Verify no guardrail violations
- [ ] Ensure non-destructive approach
- [ ] Plan incremental changes
- [ ] Prepare rollback strategy
- [ ] Check against master plan
- [ ] Verify theme/density compatibility
- [ ] Ensure MVVM compliance
- [ ] Check design token usage
- [ ] Verify working in E:\VoiceStudio (not C:\VoiceStudio)

---

## 🎯 SUCCESS CRITERIA

A task is successful when:

- ✅ All functionality works as specified
- ✅ UI is complex and information-dense
- ✅ No existing functionality broken
- ✅ Version compatibility maintained
- ✅ Performance within budget
- ✅ Code follows MVVM pattern
- ✅ Design tokens used correctly
- ✅ Documentation updated
- ✅ Tests pass
- ✅ User experience is smooth
- ✅ All work done in E:\VoiceStudio

---

**This ruleset is the definitive guide for all operations on VoiceStudio. Always refer to this document when making decisions or executing tasks.**

