# Gate F UI Stability Test Plan

**Date:** 2025-12-30  
**Role:** UI Engineer (Role 3)  
**Gate:** F (UI stability)  
**Status:** 📋 **TEST PLAN — Ready for execution**

---

## Purpose

Per UI Engineer DoD requirement:

> "Gate F: UI stability proof - app boots + navigates primary surfaces without binding spam or crashes"

This document provides the test plan for Gate F UI stability verification with real data testing.

---

## Prerequisites

**Before running Gate F tests:**

- [x] Build succeeds: `dotnet build "VoiceStudio.sln" -c Release -p:Platform=x64` (0 errors)
- [x] VS-0024 (CS0126 errors) fixed
- [x] VS-0028 (UI control stubs) completed
- [x] All converters have runtime-safe implementations (no exceptions in Convert methods)
- [ ] Backend is running (if required for UI functionality)
- [ ] Real test data available (audio files, profiles, projects)
- [ ] Debug output window available (Visual Studio or debug console)

---

## Test Scope

### Primary Focus: Controls with Real Data

Based on VS-0028 completion, the following controls need real data verification:

1. **WaveformControl** - Test with actual audio waveform samples
2. **SpectrogramControl** - Test with FFT spectrogram frames
3. **RadarChartControl** - Test with frequency distribution data
4. **LoudnessChartControl** - Test with LUFS measurement data
5. **PhaseAnalysisControl** - Test with phase correlation data
6. **VUMeterControl** - Test with peak/RMS level data
7. **AudioOrbsControl** - Test with frequency visualization data

### Integration Points

These controls are primarily used in:
- **AnalyzerView** (Waveform, Spectral, Radar, Loudness, Phase tabs)
- **TimelineView** (waveform/spectrogram overlays)
- **EffectsMixerView** (VU meters)

---

## Test Plan

### Phase 1: Converter Runtime Safety Verification

**Objective:** Ensure no converter throws exceptions at runtime

**Test Cases:**

- [ ] **NullToVisibilityConverter** - Test with null, empty string, valid string
  - Expected: Returns Visibility.Collapsed for null/empty, Visible for valid
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **StringFormatConverter** - Test with valid format, invalid format, null value
  - Expected: Returns formatted string or empty string on error (no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **NumberFormatConverter** - Test with valid numbers, invalid format, null
  - Expected: Returns formatted number or empty string on error (no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **DictionaryValueConverter** - Test with valid dictionary, missing key, null value
  - Expected: Returns default value for target type (no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **FirstLetterConverter** - Test with valid string, empty string, null
  - Expected: Returns first letter or "?" on error (no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **InitialsConverter** - Test with single word, multiple words, empty, null
  - Expected: Returns initials or "?" on error (no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **IsSelectedConverter** - Test with valid selection helper, null parameter
  - Expected: Returns bool (false on error, no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **StringToBrushConverter** - Test with hex colors, named colors, invalid strings
  - Expected: Returns SolidColorBrush or fallback (no exception)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

**Success Criteria:**
- ✅ No runtime exceptions from any converter
- ✅ All converters return safe defaults on error
- ✅ No binding errors in debug output

---

### Phase 2: VS-0028 Control Testing with Real Data

#### 2.1 WaveformControl Testing

**Test Environment:** AnalyzerView → Waveform tab

**Test Cases:**

- [ ] **Load waveform with real audio data**
  - Action: Select audio file, navigate to AnalyzerView → Waveform tab
  - Expected: WaveformControl displays waveform visualization
  - Data Source: Real audio file from library or synthesis output
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test peak mode rendering**
  - Action: Verify Mode="peak" displays peak waveform
  - Expected: Waveform shows peak amplitudes correctly
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test RMS mode rendering**
  - Action: Change Mode to "rms" (if supported)
  - Expected: Waveform shows RMS amplitudes
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test zoom functionality**
  - Action: Adjust ZoomLevel property or zoom controls
  - Expected: Waveform zooms in/out smoothly
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test playback position indicator**
  - Action: Set PlaybackPosition during audio playback
  - Expected: Playback line moves across waveform
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test empty/null data handling**
  - Action: Load AnalyzerView with no audio selected
  - Expected: Control displays gracefully (empty state or placeholder)
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 2.2 SpectrogramControl Testing

**Test Environment:** AnalyzerView → Spectral tab

**Test Cases:**

- [ ] **Load spectrogram with real FFT data**
  - Action: Select audio file, navigate to AnalyzerView → Spectral tab
  - Expected: SpectrogramControl displays frequency heatmap
  - Data Source: Real audio analysis FFT frames
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test color gradient rendering**
  - Action: Verify spectrogram uses color gradient (Blue → Cyan → Green → Yellow → Red)
  - Expected: Colors represent frequency intensity correctly
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test playback position sync**
  - Action: Set PlaybackPosition during playback
  - Expected: Vertical line indicates current playback position
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test zoom and pan**
  - Action: Zoom in/out, pan across spectrogram
  - Expected: Control responds smoothly to zoom/pan
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 2.3 RadarChartControl Testing

**Test Environment:** AnalyzerView → Radar tab

**Test Cases:**

- [ ] **Load radar chart with frequency distribution**
  - Action: Navigate to AnalyzerView → Radar tab
  - Expected: RadarChartControl displays circular frequency distribution
  - Data Source: Real frequency analysis data
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test axis and label rendering**
  - Action: Verify frequency axis lines and labels display
  - Expected: Axes and labels are readable and correctly positioned
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 2.4 LoudnessChartControl Testing

**Test Environment:** AnalyzerView → Loudness tab

**Test Cases:**

- [ ] **Load loudness chart with LUFS data**
  - Action: Navigate to AnalyzerView → Loudness tab
  - Expected: LoudnessChartControl displays LUFS line chart
  - Data Source: Real loudness measurement data
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test integrated and peak indicators**
  - Action: Verify integrated LUFS and peak indicators display
  - Expected: Indicators show correct values and positions
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 2.5 PhaseAnalysisControl Testing

**Test Environment:** AnalyzerView → Phase tab

**Test Cases:**

- [ ] **Load phase analysis with correlation data**
  - Action: Navigate to AnalyzerView → Phase tab
  - Expected: PhaseAnalysisControl displays phase correlation visualization
  - Data Source: Real phase analysis data
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test stereo width visualization**
  - Action: Verify stereo width display
  - Expected: Visualization shows stereo width correctly
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 2.6 VUMeterControl Testing

**Test Environment:** EffectsMixerView (or applicable panel)

**Test Cases:**

- [ ] **Display VU meters with real audio levels**
  - Action: Play audio, verify VU meters respond
  - Expected: Peak and RMS bars update with audio levels
  - Data Source: Real-time audio level data
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Test color coding (green/yellow/red)**
  - Action: Verify color changes based on level thresholds
  - Expected: Colors indicate safe/warning/clipping zones
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 2.7 AudioOrbsControl Testing

**Test Environment:** Applicable panel (if integrated)

**Test Cases:**

- [ ] **Display circular frequency visualization**
  - Action: Load control with frequency data
  - Expected: Circular/orbital frequency visualization renders
  - Data Source: Real frequency analysis data
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

---

### Phase 3: Panel Integration Testing with Real Data

#### 3.1 AnalyzerView Integration

**Test Cases:**

- [ ] **Tab navigation with real data**
  - Action: Navigate between Waveform, Spectral, Radar, Loudness, Phase tabs
  - Expected: Each tab loads correct control with real data, no crashes
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Audio file selection and analysis**
  - Action: Select audio file, trigger analysis
  - Expected: All visualization controls populate with real analysis data
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Real-time updates during playback**
  - Action: Play audio, verify controls update playback position
  - Expected: Playback indicators sync across all controls
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 3.2 LibraryView with Real Assets

**Test Cases:**

- [ ] **Load library with real audio assets**
  - Action: Navigate to LibraryView, verify assets display
  - Expected: Asset list shows real files, metadata displays correctly
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Asset selection with IsSelectedConverter**
  - Action: Select assets, verify selection state
  - Expected: IsSelectedConverter correctly identifies selected items
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Asset context menu operations**
  - Action: Right-click asset, verify menu operations work
  - Expected: Menu items execute without crashes
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 3.3 ProfilesView with Real Profiles

**Test Cases:**

- [ ] **Load profiles list with real profile data**
  - Action: Navigate to ProfilesView
  - Expected: Profile cards display with real profile information
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Profile quality metrics display**
  - Action: View profile details
  - Expected: Quality metrics render correctly using converters
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

#### 3.4 TimelineView with Real Project Data

**Test Cases:**

- [ ] **Load timeline with real project**
  - Action: Open project, navigate to TimelineView
  - Expected: Timeline displays tracks and clips correctly
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **Waveform overlay rendering**
  - Action: Verify waveform overlays on clips
  - Expected: WaveformControl renders correctly on timeline clips
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

---

### Phase 4: Binding Error Verification

**Test:** Monitor for binding errors during real data operations

**Test Cases:**

- [ ] **No binding errors during control loading**
  - Action: Navigate to panels with VS-0028 controls, monitor debug output
  - Expected: No "BindingExpression" errors, no "Cannot find source" errors
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **No binding errors during data updates**
  - Action: Update data sources, verify bindings update correctly
  - Expected: Controls update without binding errors
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

- [ ] **No converter exceptions in debug output**
  - Action: Perform all test scenarios, monitor for converter exceptions
  - Expected: No exceptions from converter Convert methods
  - Actual: ________________
  - Status: ⬜ Pass / ⬜ Fail

---

## Test Data Requirements

### Audio Files

- [ ] Sample audio files (WAV, MP3) available for testing
- [ ] Audio files with known characteristics (duration, sample rate, channels)
- [ ] Files for synthesis output testing

### Profiles

- [ ] Real voice profiles with metadata
- [ ] Profiles with quality metrics data
- [ ] Profiles with avatar images (if applicable)

### Projects

- [ ] Sample project files with timeline data
- [ ] Projects with multiple tracks and clips
- [ ] Projects with audio analysis data

---

## Test Execution

**When to execute:**

- After Gate C is green (app launches successfully)
- After VS-0028 controls are integrated
- Before marking Gate F complete

**Execution steps:**

1. Prepare test data (audio files, profiles, projects)
2. Build solution: `dotnet build "VoiceStudio.sln" -c Release -p:Platform=x64`
3. Launch app (Visual Studio debug or published EXE)
4. Execute test plan above
5. Document results in this checklist
6. Create ledger entries for any failures

---

## Success Criteria

**Gate F Pass Requirements:**

- ✅ All converter runtime safety tests pass (no exceptions)
- ✅ All VS-0028 controls render correctly with real data
- ✅ Panel integration tests pass with real data
- ✅ No binding errors in debug output
- ✅ No runtime crashes during data operations
- ✅ All controls handle empty/null data gracefully

---

## Issues Found

**Document any issues discovered during testing:**

| Issue | Severity | Description | Status |
| ----- | -------- | ----------- | ------ |
|       |          |             |        |

---

## Results Summary

**Overall Status:** ⬜ **PASS** / ⬜ **FAIL**

**Test Coverage:**
- Converter Safety: ___ / 8 tests passed
- VS-0028 Controls: ___ / 7 controls tested
- Panel Integration: ___ / 4 panels tested
- Binding Errors: ⬜ None / ⬜ Found (see Issues)

**Sign-off:**

**UI Engineer:** ________________ Date: ________________  
**System Architect (Reviewer):** ________________ Date: ________________

---

## Related Documents

- `docs/governance/overseer/GATE_C_UI_SMOKE_TEST.md` — Gate C smoke test checklist
- `docs/governance/overseer/handoffs/VS-0028.md` — VS-0028 control implementation details
- `Recovery Plan/QUALITY_LEDGER.md` — Ledger for issues found
- `tests/ui/PANEL_TESTING_SPECIFICATION.md` — Complete panel testing spec
