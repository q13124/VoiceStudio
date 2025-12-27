# All Project Rules
## VoiceStudio Quantum+ - Complete Rules and Guidelines

**Last Updated:** 2025-01-27  
**Purpose:** Comprehensive compilation of all rules, guidelines, and guardrails for VoiceStudio Quantum+

---

## 🚫 NO MOCK OUTPUTS OR PLACEHOLDER CODE (ENFORCEMENT)

### Rule Summary

All Cursor agents must write **complete, real code** with working logic — no mock data, placeholders, stubs, or speculative interfaces unless explicitly instructed.

### Must Avoid

**🚫 Do NOT generate:**
- ❌ `TODO` comments
- ❌ `pass`-only stubs
- ❌ `return {"mock": true}` or fake responses
- ❌ Empty class/function shells with no logic
- ❌ Unimplemented data flows ("assume this works")
- ❌ Mock protocols or fake API responses
- ❌ Hardcoded filler data
- ❌ Speculative implementations

### Required Output Format

**✅ Agents must:**
- ✅ Implement full function bodies, classes, or components
- ✅ Wire UI and backend code together with real bindings or API calls
- ✅ Return real values, real file I/O, real API wiring — not mock protocols
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional and log its usage
- ✅ Use real engine routers, MCPs, or models
- ✅ Perform actual operations (e.g., saving audio, applying effects)

### Completion Criteria

**Functionality must be:**
- ✅ Verifiable and testable
- ✅ UI panels display actual values or connect to real models, MCPs, or engine routers
- ✅ Backend code performs its intended effect or operation
- ✅ No component marked complete if its implementation is speculative or empty

### Overseer Tasks

**The Overseer agent must:**
- ✅ Reject mock-only modules
- ✅ Flag any output containing `TODO`, `mock`, or hardcoded filler as incomplete
- ✅ Approve only full-functionality commits
- ✅ Encourage reuse of shared libraries or hooks to reduce boilerplate

### Example: BAD ❌

```python
def generate_audio(voice_id):
    # TODO: implement
    return {"mock_audio": true}
```

```csharp
public async Task<AudioResult> SynthesizeAsync(string text)
{
    // TODO: Implement synthesis
    return new AudioResult { Mock = true };
}
```

### Example: GOOD ✅

```python
def generate_audio(voice_id: str) -> dict:
    """Generate audio using real engine."""
    engine = router.get_engine("xtts_v2")
    result = engine.synthesize(
        text=text,
        voice_id=voice_id,
        language="en"
    )
    return {
        "audio_path": result.audio_path,
        "duration": result.duration,
        "quality_metrics": result.quality_metrics
    }
```

```csharp
public async Task<AudioResult> SynthesizeAsync(string text)
{
    var engine = _engineRouter.GetEngine("xtts_v2");
    var result = await engine.SynthesizeAsync(text, _currentVoiceProfile);
    
    return new AudioResult
    {
        AudioPath = result.AudioPath,
        Duration = result.Duration,
        QualityMetrics = result.QualityMetrics
    };
}
```

**See:** Rule #1 above for complete details on 100% Complete requirement

**Code Improvement Example:**
- See `docs/governance/CODE_IMPROVEMENT_EXAMPLE.md` for before/after comparison
- Shows how to transform minimal implementations into production-ready code

---

## 🎯 ENGINE LIBRARY DOWNLOAD RULES (NEW)

### Offline-First Model Management

**REQUIRED:**
- ✅ All models must be downloadable and installable offline
- ✅ Use local mirrors, pre-downloaded archives, or bundled ZIPs
- ✅ Verify SHA-256 checksums for all downloaded models
- ✅ Store models in `%PROGRAMDATA%\VoiceStudio\models\{engine}\`
- ✅ Only download models with permissive licenses (MIT, Apache-2.0, BSD, CC-BY, etc.)
- ✅ Update `models.index.json` after successful downloads
- ✅ Support air-gapped/restricted environments

**FORBIDDEN:**
- ❌ Rely on runtime HTTP fetch unless explicitly marked `auto_update=true`
- ❌ Download models with restricted licenses (non-commercial, research-only)
- ❌ Skip checksum verification
- ❌ Store models in application directory (use %PROGRAMDATA%)

**Implementation:**
- See `docs/developer/ENGINE_LIBRARY_DOWNLOAD_GUIDE.md` for complete guide
- Use `tools/download_all_free_models.py` for batch downloads
- All Cursor agents must verify model completeness before marking DONE

---

## 🚨 CRITICAL RULES (NON-NEGOTIABLE)

### 1. 100% COMPLETE - NO STUBS, PLACEHOLDERS, BOOKMARKS, OR TAGS ⚠️ **HIGHEST PRIORITY**

**📋 COMPREHENSIVE RULE:** See `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` for the complete, expanded rule with ALL forbidden terms, patterns, synonyms, and variations.

**FORBIDDEN (Summary - see comprehensive rule for complete list):**

**Bookmarks:**
- ❌ `TODO`, `FIXME`, `NOTE`, `HACK`, `REMINDER`, `XXX`, `WARNING`, `CAUTION`, `BUG`, `ISSUE`, `REFACTOR`, `OPTIMIZE`, `REVIEW`, `CHECK`, `VERIFY`, `TEST`, `DEBUG`, `DEPRECATED`, `OBSOLETE`
- ❌ Any comment indicating incomplete work

**Placeholders:**
- ❌ `throw new NotImplementedException()`, `NotImplementedError`
- ❌ `[PLACEHOLDER]`, `[TODO]`, `[FIXME]`
- ❌ `return {"mock": true}` or fake responses
- ❌ `return {}`, `return []`, `return null` without implementation
- ❌ Comments saying "placeholder", "dummy", "mock", "fake", "sample", "temporary"
- ❌ Hardcoded filler data

**Stubs:**
- ❌ `pass`-only stubs (Python)
- ❌ Empty methods with only comments
- ❌ Empty class/function shells with no logic
- ❌ Functions that just return without doing anything

**Tags:**
- ❌ `#TODO`, `#FIXME`, `#PLACEHOLDER`, `#HACK`, `#NOTE`
- ❌ `[IN PROGRESS]`, `[PENDING]`, `[TO BE DONE]`, `[WIP]`
- ❌ XML/HTML tags like `<placeholder>`, `<todo>`, `<incomplete>`

**Status Words/Phrases:**
- ❌ "pending", "incomplete", "unfinished", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc"
- ❌ "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress"

**REQUIRED:**
- ✅ Full implementation of all methods
- ✅ All functionality working
- ✅ All error cases handled
- ✅ All edge cases considered
- ✅ Tests written and passing (if applicable)
- ✅ Production-ready code
- ✅ Real values, real file I/O, real API wiring
- ✅ Complete function bodies, classes, or components
- ✅ UI and backend wired together with real bindings or API calls
- ✅ Verifiable and testable functionality

**Rule:** If it's not 100% complete and tested, it's NOT done. Don't move on.

**Mock Code Exception:**
- If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional
- Log mock usage clearly
- Never use mocks in production code paths

**See:** 
- `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` - **COMPREHENSIVE RULE** with all forbidden terms
- `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - Summary rule

---

### 2. PanelHost is MANDATORY

**FORBIDDEN:**
- ❌ Replace PanelHost with raw Grids
- ❌ Merge panels into single controls
- ❌ Simplify panel structure
- ❌ Remove PanelHost system

**REQUIRED:**
- ✅ Use PanelHost for all panels
- ✅ Maintain 4 PanelHosts: LeftPanelHost, CenterPanelHost, RightPanelHost, BottomPanelHost
- ✅ Each panel = separate `.xaml` + `.xaml.cs` + `ViewModel.cs` files
- ✅ Never merge View/ViewModel files

---

### 3. Strict MVVM Separation

**FORBIDDEN:**
- ❌ Merge View and ViewModel files
- ❌ Put ViewModel code in code-behind
- ❌ Put View code in ViewModel
- ❌ Mix concerns

**REQUIRED:**
- ✅ Each panel = separate `.xaml` + `.xaml.cs` + `ViewModel.cs`
- ✅ ViewModels in separate files
- ✅ Code-behind only for UI event handlers
- ✅ Business logic in ViewModels

---

### 4. DesignTokens for ALL Styling

**FORBIDDEN:**
- ❌ Hardcoded colors (e.g., `#FF0000`, `Colors.Red`)
- ❌ Hardcoded typography (e.g., `FontSize="14"`)
- ❌ Hardcoded spacing (e.g., `Margin="10"`)
- ❌ Hardcoded corner radius
- ❌ Any hardcoded styling values

**REQUIRED:**
- ✅ Use `VSQ.*` resources from `DesignTokens.xaml`
- ✅ All colors: `{StaticResource VSQ.Text.PrimaryBrush}`
- ✅ All spacing: `{StaticResource VSQ.Spacing.Medium}`
- ✅ All typography: `{StaticResource VSQ.FontSize.Body}`
- ✅ All styling via design tokens

**File:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`

---

### 5. WinUI 3 Native Only

**FORBIDDEN:**
- ❌ React, Electron, webviews
- ❌ Cross-platform frameworks
- ❌ Web-based components
- ❌ Framework migrations
- ❌ Any non-native technologies

**REQUIRED:**
- ✅ WinUI 3 controls only
- ✅ Native Windows application
- ✅ Full native performance
- ✅ Windows integration

---

### 6. Professional DAW-Grade Complexity

**FORBIDDEN:**
- ❌ Simplifying layouts
- ❌ Reducing panel count
- ❌ "This is too complex" changes
- ❌ Reducing information density
- ❌ Merging panels "for simplicity"

**REQUIRED:**
- ✅ Adobe/FL Studio level complexity
- ✅ High information density
- ✅ Professional appearance
- ✅ Complex workflows supported
- ✅ Multiple panels visible simultaneously

---

### 7. Layout Structure (CANONICAL)

**MANDATORY STRUCTURE:**
```
3-Row Grid:
├── Row 0: Top Command Deck
│   ├── MenuBar (File, Edit, View, Modules, Playback, Tools, AI, Help)
│   └── Command Toolbar (48px)
│
├── Row 1: Main Workspace
│   └── 4-Column Grid:
│       ├── Column 0: Nav Rail (64px) - 8 toggle buttons
│       ├── Column 1: LeftPanelHost (20% width)
│       ├── Column 2: CenterPanelHost (55% width)
│       └── Column 3: RightPanelHost (25% width)
│   └── Row 1 (Bottom Deck): BottomPanelHost (18% height)
│
└── Row 2: Status Bar (26px)
```

**FORBIDDEN:**
- ❌ Changing this structure
- ❌ Removing panels
- ❌ Simplifying layout
- ❌ Fixed, non-dockable panels

---

## 📋 FILE LOCKING PROTOCOL

### Before Editing Any File:

1. **Check TASK_LOG.md** for existing file locks
2. **If file is locked:**
   - Wait for unlock (if task nearly complete)
   - Request handoff from current worker
   - Work on different file
3. **If file is unlocked:**
   - Add file to lock list in `TASK_LOG.md`
   - Include task ID, worker name, timestamp
   - Begin work

### After Completing Work:

1. Complete all edits
2. Test changes
3. Remove file from lock list in `TASK_LOG.md`
4. Mark task as complete
5. Notify Overseer for review

**See:** `docs/governance/FILE_LOCKING_PROTOCOL.md` for complete protocol

---

## 🎨 UI/UX INTEGRITY RULES

### Design Language Requirements:

1. **WinUI 3 Native Only**
   - Use only WinUI 3 controls and XAML
   - No web technologies
   - Full native performance

2. **Docked, Modular Panels**
   - Panels must be dockable
   - Panels must be resizable and rearrangeable
   - PanelHost system for all panels
   - 3-column + nav + bottom deck layout maintained

3. **Design Consistency**
   - Use DesignTokens.xaml for ALL styling
   - Consistent fonts and spacings
   - Uniform look & feel
   - Visual hierarchy matches style guidelines

4. **Premium Details**
   - High-quality polish (subtle animations)
   - No generic stock imagery
   - Consistent alignments
   - Smooth transitions
   - Professional DAW-grade appearance

**See:** `docs/governance/UI_UX_INTEGRITY_RULES.md` for complete requirements

---

## ✅ DEFINITION OF DONE

**A feature is "Done" ONLY when ALL criteria are met:**

1. **Windows Installer**
   - ✅ Native Windows installer created
   - ✅ Tested on clean Windows systems
   - ✅ Uninstaller works correctly
   - ✅ File associations configured

2. **Pixel-Perfect UI**
   - ✅ Interface matches approved design spec
   - ✅ All UI elements pixel-accurate
   - ✅ Colors, fonts, icons, layouts match spec

3. **All Panels Functional**
   - ✅ Every panel fully implemented
   - ✅ Real functionality (not placeholders)
   - ✅ All features wired and operational

4. **No Placeholders or TODOs**
   - ✅ No temporary stubs
   - ✅ No placeholder code
   - ✅ No "TODO" comments
   - ✅ All features fully implemented

5. **Tested and Documented**
   - ✅ All code tested
   - ✅ UI behavior verified
   - ✅ All functionality documented

**See:** `docs/governance/DEFINITION_OF_DONE.md` for complete criteria

---

## 🛡️ PERFORMANCE & STABILITY SAFEGUARDS

### 1. Monitor Resource Usage
- Track CPU/GPU/memory usage per agent
- If usage spikes → Pause or reset
- Thresholds: CPU > 80%, Memory > 2GB, GPU > 90%

### 2. Staggered Access
- If multiple agents need same file → Retry/backoff
- No tight loops (busy-waiting)
- Exponential backoff pattern
- Maximum retry limit: 5 attempts

### 3. Loop/Time Limits
- Maximum iterations per loop: 1000
- Maximum execution time per task: 30 minutes
- Maximum retry attempts: 5
- Overseer detects and intervenes if stuck

### 4. Logging Cooldowns
- Batch or throttle logs
- Max 1 update per 5 seconds
- Essential information only
- ERROR: Always log
- INFO: Batch updates

### 5. Fail-Safes
- If agent crashes/hangs → Overseer terminates
- System fails gracefully (roll back changes)
- Preserve work in progress
- No data loss

**See:** `docs/governance/PERFORMANCE_STABILITY_SAFEGUARDS.md` for complete details

---

## 💡 BRAINSTORMER PROTOCOL

### Brainstormer is READ-ONLY

**What Brainstormer Does:**
- ✅ Generates UX/UI enhancement ideas
- ✅ Submits ideas to Overseer
- ✅ Suggests improvements

**What Brainstormer Does NOT Do:**
- ❌ Edit code files
- ❌ Modify documentation
- ❌ Update roadmap directly
- ❌ Implement features
- ❌ Fix bugs

### Design Compliance Requirements:

All ideas must:
- ✅ Respect WinUI 3 native requirement
- ✅ Maintain DAW-style layout
- ✅ Preserve information density
- ✅ Enhance without simplifying

**Prohibited Ideas:**
- ❌ Switching to web technologies
- ❌ Simplifying layout
- ❌ Reducing complexity
- ❌ Framework changes

**See:** `docs/governance/BRAINSTORMER_PROTOCOL.md` for complete protocol

---

## 🏗️ ARCHITECTURE RULES

### Technology Stack:
- **Frontend:** WinUI 3 (.NET 8, C#/XAML)
- **Backend:** Python FastAPI
- **Communication:** REST/WebSocket
- **Pattern:** MVVM (strict separation)

### Local-First Architecture:
- ✅ All engines run offline
- ✅ No external APIs for core features
- ✅ No API keys required
- ✅ All processing local
- ✅ All storage local

### Engine System:
- ✅ Manifest-based discovery
- ✅ No hardcoded engine limits
- ✅ Dynamic API
- ✅ Plugin architecture
- ✅ Protocol-based interface

---

## 📁 FILE STRUCTURE RULES

### Canonical Structure:
```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 frontend
│   │   ├── App.xaml
│   │   ├── MainWindow.xaml
│   │   ├── Resources/DesignTokens.xaml
│   │   ├── Controls/PanelHost.xaml
│   │   └── Views/Panels/             # Each panel: .xaml, .xaml.cs, ViewModel.cs
│   │
│   └── VoiceStudio.Core/             # Shared library
│       └── Panels/                   # Panel registry types
│
└── backend/
    └── api/                          # Python FastAPI
```

**Rule:** This structure is CANONICAL. Do not simplify or merge files.

---

## 🔄 TASK MANAGEMENT RULES

### Task Assignment:
1. Check `TASK_LOG.md` for assignments
2. Check file locks before starting work
3. Acquire file lock before editing
4. Update progress in `TASK_TRACKER_3_WORKERS.md`
5. Mark complete in `TASK_LOG.md` when done

### Task Completion:
1. Verify Definition of Done criteria met
2. Remove file locks
3. Update task status
4. Create status report
5. Notify Overseer for review

### Task Handoff:
1. Worker marks task complete
2. Worker removes file locks
3. Overseer reviews work
4. Overseer approves and assigns next task
5. Next worker takes ownership

---

## 🚨 VIOLATION DETECTION PATTERNS

**Immediate REJECT:**
- TODO comments in code
- NotImplementedException
- Placeholder code
- Merged View/ViewModel files
- PanelHost replaced with Grid
- Reduced panel count
- Hardcoded colors
- Simplified layout
- Deleted existing functionality

**Remediation Command:**
```
STOP. Detected violation. Revert changes immediately.
This UI is intentionally complex. Preserve all existing functionality.
Restore PanelHost and separate panel Views/ViewModels.
Integrate new components alongside existing, not as replacements.
```

---

## 📋 WORKFLOW RULES

### Before Starting Work:
1. Read `docs/design/MEMORY_BANK.md` - **ALWAYS FIRST**
2. Load appropriate system prompt
3. Check `TASK_LOG.md` for assignments
4. Check file locks before editing
5. Review `DEFINITION_OF_DONE.md`

### During Work:
1. Follow Performance Safeguards
2. Update progress daily
3. Follow all guardrails
4. Use DesignTokens for all styling
5. Maintain MVVM separation

### Before Completion:
1. Verify Definition of Done criteria
2. Check for violations
3. Remove file locks
4. Update task status
5. Create status report
6. Notify Overseer

---

## 🎯 INTEGRATION PRIORITY

**MOST IMPORTANT:**
1. **PRESERVE** existing code that works
2. **INTEGRATE** new UI components alongside existing
3. **ENHANCE** existing features, don't replace them
4. **MAINTAIN** backward compatibility

**BEFORE ANY CHANGES:**
1. Read existing file completely
2. Document existing functionality
3. Document existing data bindings
4. Document existing event handlers
5. Create preservation checklist
6. Check TASK_LOG.md for file locks

---

## 📚 REFERENCE DOCUMENTS

### Critical Documents (Must Read):
- `docs/design/MEMORY_BANK.md` - **CRITICAL** - All agents must read first
- `docs/governance/QUICK_START_GUIDE.md` - Complete workflow guide
- `docs/governance/TASK_LOG.md` - Task assignments and locks
- `docs/governance/DEFINITION_OF_DONE.md` - Completion criteria

### System Prompts:
- `docs/governance/OVERSEER_PROMPT.md` - Overseer system prompt
- `docs/governance/WORKER_1_PROMPT.md` - Worker 1 prompt
- `docs/governance/WORKER_2_PROMPT.md` - Worker 2 prompt
- `docs/governance/WORKER_3_PROMPT.md` - Worker 3 prompt
- `docs/governance/BRAINSTORMER_PROMPT.md` - Brainstormer prompt

### Rules Documents:
- `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - No stubs rule
- `docs/governance/UI_UX_INTEGRITY_RULES.md` - UI rules
- `docs/governance/FILE_LOCKING_PROTOCOL.md` - File locking
- `docs/governance/PERFORMANCE_STABILITY_SAFEGUARDS.md` - Safeguards
- `docs/governance/BRAINSTORMER_PROTOCOL.md` - Brainstormer rules

---

## 🔄 WHEN IN DOUBT

1. Check `docs/design/MEMORY_BANK.md` - **ALWAYS CHECK THIS FIRST**
2. Check `docs/voice_studio_guidelines.md` - **CURSOR AGENT GUIDELINES**
3. Check `docs/governance/QUICK_START_GUIDE.md`
4. Check `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`
5. Verify against `GLOBAL_GUARDRAILS.md`
6. Check `TASK_LOG.md` for file locks
7. Ensure PanelHost structure is preserved
8. Confirm design tokens are used
9. Maintain strict MVVM separation
10. **Run `python tools/verify_non_mock.py` before committing**

**Remember: This is a professional DAW-grade application. Complexity and modularity are features, not bugs.**

---

## ✅ QUICK REFERENCE CHECKLIST

### Code Quality:
- [ ] No TODO comments
- [ ] No NotImplementedException
- [ ] No placeholder code
- [ ] All functionality implemented
- [ ] All error cases handled
- [ ] Production-ready code

### UI/UX:
- [ ] WinUI 3 native only
- [ ] PanelHost used (not Grid)
- [ ] DesignTokens for all styling
- [ ] MVVM separation maintained
- [ ] Pixel-perfect to design spec
- [ ] Professional DAW-grade appearance

### Task Management:
- [ ] Checked TASK_LOG.md for assignments
- [ ] Checked file locks before editing
- [ ] Acquired file lock if needed
- [ ] Updated progress daily
- [ ] Verified Definition of Done
- [ ] Removed file locks on completion

### Performance:
- [ ] Resource usage monitored
- [ ] Retry/backoff for locked files
- [ ] Loop limits set
- [ ] Logging throttled
- [ ] Fail-safes in place

---

**Last Updated:** 2025-01-27  
**Status:** Complete Rules Reference  
**All agents must follow these rules. No exceptions.**

