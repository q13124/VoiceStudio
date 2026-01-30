# Gate C UI Smoke Test Checklist

## App Boot Stability Verification

**Date:** 2025-01-28  
**Prepared by:** UI Engineer (Role 3)  
**Gate:** C (App boot stability)  
**Status:** 📋 **CHECKLIST — Ready for execution**

---

## Purpose

Per UI Engineer DoD requirement:

> "UI smoke: app boots, navigation works, no binding errors in output"

This document provides the verification checklist for Gate C UI requirements.

---

## Prerequisites

**Before running smoke test:**

- [ ] Build succeeds: `dotnet build "VoiceStudio.sln" -c Debug -p:Platform=x64` (0 errors)
- [ ] Backend is running (if required for UI functionality)
- [ ] Debug output window available (Visual Studio or debug console)

---

## UI Smoke Test Checklist

### Phase 1: App Boot Verification

**Test:** Launch application and verify startup sequence

- [ ] **App launches without crashes**

  - Action: Launch `VoiceStudio.App.exe` (or run from Visual Studio)
  - Expected: Application window appears
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **MainWindow appears correctly**

  - Action: Verify window displays
  - Expected:
    - 3-row grid layout visible (command deck, workspace, status bar)
    - 4 PanelHost containers visible (Left, Center, Right, Bottom)
    - Nav rail visible (64px width, 8 toggle buttons)
    - Status bar visible (26px height)
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Resource dictionaries load**

  - Action: Verify design tokens are available
  - Expected:
    - VSQ.\* resources resolve (no XAML binding errors)
    - Colors, fonts, spacing render correctly
    - No resource lookup errors in debug output
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Default panels load**
  - Action: Verify default panel content
  - Expected:
    - LeftPanelHost shows ProfilesView
    - CenterPanelHost shows TimelineView
    - RightPanelHost shows EffectsMixerView
    - BottomPanelHost shows MacroView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

---

### Phase 2: Navigation Verification

**Test:** Verify all navigation buttons switch panels correctly

#### Navigation Rail Buttons (8 buttons)

- [ ] **NavStudio (S)** — Switch to Studio/Timeline

  - Action: Click NavStudio toggle button
  - Expected: CenterPanelHost switches to TimelineView (or appropriate Studio panel)
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavProfiles (P)** — Switch to Profiles

  - Action: Click NavProfiles toggle button
  - Expected: LeftPanelHost shows ProfilesView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavLibrary (L)** — Switch to Library

  - Action: Click NavLibrary toggle button
  - Expected: LeftPanelHost shows LibraryView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavEffects (E)** — Switch to Effects/Mixer

  - Action: Click NavEffects toggle button
  - Expected: RightPanelHost shows EffectsMixerView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavTrain (T)** — Switch to Training

  - Action: Click NavTrain toggle button
  - Expected: Appropriate panel shows TrainingView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavAnalyze (A)** — Switch to Analyzer

  - Action: Click NavAnalyze toggle button
  - Expected: RightPanelHost shows AnalyzerView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavSettings (⚙)** — Switch to Settings

  - Action: Click NavSettings toggle button
  - Expected: Appropriate panel shows SettingsView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NavLogs (D)** — Switch to Diagnostics/Logs
  - Action: Click NavLogs toggle button
  - Expected: BottomPanelHost shows DiagnosticsView
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

---

### Phase 3: Runtime Error Verification

**Test:** Verify no runtime exceptions or binding errors

- [ ] **No unhandled exceptions during boot**

  - Action: Monitor debug output during app launch
  - Expected: No exceptions in debug console
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **No binding errors during boot**

  - Action: Monitor debug output for binding errors
  - Expected: No "BindingExpression" errors, no "Cannot find source" errors
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **No binding errors during navigation**

  - Action: Click through all nav buttons, monitor debug output
  - Expected: No binding errors when switching panels
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **No XAML parse errors**
  - Action: Monitor debug output for XAML errors
  - Expected: No "XamlParseException" or resource lookup failures
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

---

### Phase 4: MVVM Binding Hygiene

**Test:** Verify ViewModels initialize correctly

- [ ] **All ViewModels initialize without errors**

  - Action: Navigate to each panel, check debug output
  - Expected: ViewModel constructors complete successfully
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **No code-behind logic beyond view wiring**

  - Action: Code review of panel code-behind files
  - Expected: Code-behind only contains InitializeComponent, event handlers, and view-specific wiring
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **DataContext properly set**
  - Action: Verify panels have DataContext set to ViewModel
  - Expected: Each panel's DataContext is its ViewModel
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

---

## Crash-Safe Initialization Verification

**Per Gate C requirement:**

> "Ensure crash‑safe initialization: diagnostics initializes first and writes a crash bundle path on failure"

- [ ] **Diagnostics initializes before MainWindow**

  - Action: Verify ServiceProvider.Initialize() order
  - Expected: Diagnostics service available before window creation
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Crash bundle path written on failure** (if applicable)
  - Action: Test failure scenario (if possible)
  - Expected: Crash bundle path logged/written before crash
  - Actual: ******\_\_\_******
  - Status: ⬜ Pass / ⬜ Fail / ⬜ N/A (requires failure scenario)

---

## Test Execution

**When to execute:**

- After build succeeds with 0 errors
- Before marking Gate C complete
- Required before UI Engineer handoff

**Execution steps:**

1. Build solution: `dotnet build "VoiceStudio.sln" -c Debug -p:Platform=x64`
2. Launch app (Visual Studio debug or directly)
3. Execute checklist above
4. Document results
5. Create ledger entries for any failures

---

## Issues Found

**Document any issues discovered during smoke test:**

| Issue | Severity | Description | Status |
| ----- | -------- | ----------- | ------ |
|       |          |             |        |

---

## Results Summary

**Overall Status:** ⬜ **PASS** / ⬜ **FAIL**

**Pass Criteria:**

- ✅ All checklist items pass
- ✅ No runtime exceptions
- ✅ No binding errors
- ✅ All navigation works
- ✅ App launches reliably

**Sign-off:**

**UI Engineer:** ******\_\_\_****** Date: ******\_\_\_******  
**System Architect (Reviewer):** ******\_\_\_****** Date: ******\_\_\_******

---

## UI Smoke Test Results (2025-01-28)

### Executive Summary

**Build Status:** ✅ **SUCCESS**
- `dotnet build` completes successfully (0 errors, 0 warnings)
- XAML compilation working with improved wrapper script
- All navigation code compiles correctly
- Time Elapsed: ~11 seconds

**Navigation Implementation:** ✅ **SUCCESS**
- All 8 navigation buttons now have Click handlers
- Mapped to correct PanelRegion and View factories
- Code compiles without errors (verified with `dotnet build`)
- Integration with existing `SwitchToPanel` method confirmed

**App Launch:** ❌ **BLOCKED — Runtime Environment Issue**
- **Error:** `COMException (0x80040154): Class not registered`
- **Root Cause:** WinUI 3 runtime components not available in current environment
- **Technical Details:** Missing Windows App SDK runtime for WinUI 3 applications
- **Impact:** Cannot execute full UI smoke test until proper development environment is available

### Navigation Implementation Details

**Files Modified:**
- `src/VoiceStudio.App/MainWindow.xaml` — Added Click handlers to all nav ToggleButtons
- `src/VoiceStudio.App/MainWindow.xaml.cs` — Implemented 8 click handler methods

**Navigation Mappings:**
- **NavStudio (S)** → Center Panel: TimelineView
- **NavProfiles (P)** → Left Panel: ProfilesView
- **NavLibrary (L)** → Left Panel: LibraryView
- **NavEffects (E)** → Right Panel: EffectsMixerView
- **NavTrain (T)** → Left Panel: TrainingView
- **NavAnalyze (A)** → Right Panel: AnalyzerView
- **NavSettings (⚙)** → Right Panel: SettingsView
- **NavLogs (D)** → Bottom Panel: DiagnosticsView

**Code Quality:**
- ✅ Compiles successfully (0 errors, 0 warnings)
- ✅ Follows existing SwitchToPanel pattern
- ✅ Proper error handling (existing in SwitchToPanel method)
- ✅ No code-behind logic beyond view wiring (MVVM compliant)

### Runtime Environment Issue

**Error Details:**
```
Unhandled exception. System.Runtime.InteropServices.COMException (0x80040154): Class not registered
   at Microsoft.UI.Xaml.Application.Start(ApplicationInitializationCallback callback)
```

**Diagnosis:**
- WinUI 3 applications require Windows App SDK runtime components
- Current environment lacks proper WinUI 3 development setup
- Application cannot initialize XAML framework

**Resolution Required:**
- Install Windows App SDK runtime
- Configure proper Windows development environment
- Do not deploy as MSIX; use the unpackaged Gate C publish artifact and `scripts/gatec-publish-launch.ps1`

### Recommendations

**For Immediate Testing:**
1. Set up proper WinUI 3 development environment
2. Install Windows App SDK workload in Visual Studio
3. Re-run UI smoke test with full navigation testing

**For Gate C Completion:**
1. Verify navigation works correctly (all 8 buttons switch panels)
2. Confirm no binding errors during navigation
3. Test app boot performance (< 3 seconds target)
4. Validate crash-safe initialization

---

## Related Documents

- `Recovery Plan/VoiceStudio_Architectural_Recovery_and_Completion_Plan.md` — Gate C requirements
- `docs/governance/overseer/roles/UI_ENGINEER.md` — UI Engineer DoD
- `Recovery Plan/QUALITY_LEDGER.md` — Ledger for issues found
