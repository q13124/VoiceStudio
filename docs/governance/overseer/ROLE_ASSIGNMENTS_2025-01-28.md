# Role Assignments — 2025-01-28

**Overseer Status:** Gate C blocked by 3 critical blockers  
**Priority:** Drive VS-0023 → VS-0025 → VS-0012 to completion

---

## Build & Tooling Engineer (CRITICAL PATH)

**Status:** 🚨 **BLOCKING Gate C**

### Current Blockers (Priority Order)

1. **VS-0023 (IN_PROGRESS)** — Release build configuration hotfix
   - **Issue:** Release builds fail or produce non-functional binaries
   - **Action Required:**
     - Investigate why `WindowsAppSDKSelfContained=true` doesn't copy runtime redist files
     - Add explicit copy targets for Windows App SDK bootstrap DLLs to publish output
     - Test publish output contains all required runtime components
   - **Success Criteria:** Release publish produces launchable artifact
   - **Blocks:** VS-0025, VS-0012, VS-0003

2. **VS-0025 (TRIAGE)** — CoreMessagingXP.dll crash (0xC0000602)
   - **Issue:** Release publish launch crashes with `0xC0000602` in CoreMessagingXP.dll
   - **Action Required:**
     - Once VS-0023 is fixed, verify CoreMessagingXP.dll is included in publish output
     - If not, add explicit copy targets for CoreMessagingXP.dll and dependencies
     - Capture successful launch proof run
   - **Success Criteria:** Release artifact launches without crash
   - **Depends On:** VS-0023 completion

### Next Steps After Unblocking

- Add CI checks for publish output sanity (presence of apphost, required DLLs)
- Complete Gate C script with reproducible publish+launch
- Document the Gate C artifact standard (unpackaged apphost EXE)

---

## Release Engineer (BLOCKED)

**Status:** ⏸️ **Waiting on Build & Tooling Engineer**

### When Unblocked (After VS-0023/VS-0025)

1. **VS-0012 (TRIAGE)** — WinUI activation crash (0x80040154)
   - **Issue:** App crashes on startup with `0x80040154` (class not registered)
   - **Action Required:**
     - Reproduce using fixed Release artifact from VS-0023/VS-0025
     - Verify runtime prerequisites are deterministic for unpackaged launch
     - Single lane: unpackaged EXE + installer only (MSIX not used). If unpackaged launch fails, treat as Gate C blocker and fix prerequisites/runtime determinism.
     - Document the Gate C standard launch method
   - **Success Criteria:** App launches reliably on Gate C artifact
   - **Depends On:** VS-0023, VS-0025 completion

2. **VS-0003 (IN_PROGRESS)** — Installer verification (Gate H)
   - **Issue:** Installer package verification and upgrade/rollback path
   - **Action Required:**
     - Build installer using stable Release artifact
     - Test on clean Windows profiles (VMs): install → launch → upgrade → rollback → uninstall
     - Confirm prerequisites: .NET runtime, model root, ffmpeg/native tools
   - **Success Criteria:** Complete installer lifecycle proofs
   - **Depends On:** Gate C closure (VS-0012 completion)

---

## UI Engineer

**Status:** ✅ **Recent completion, preparing for Gate F**

### Recent Completion

- ✅ **VS-0028 (DONE)** — All UI control stubs replaced with functional implementations
  - WaveformControl, SpectrogramControl, LoudnessChartControl, RadarChartControl, PhaseAnalysisControl, VUMeterControl, AudioOrbsControl
  - All use Path-based rendering (no Win2D dependency)
  - RuleGuard passes, builds cleanly

### Next Tasks (Gate F Preparation)

1. **Test implemented controls** in AnalyzerView with real audio data
   - Verify visualizations render correctly
   - Test zoom and playback position features
   - Ensure controls respond to ViewModel data bindings

2. **Fix remaining converter placeholders**
   - Implement NullToVisibilityConverter, DictionaryValueConverter, etc.
   - Ensure no converters throw NotImplementedException

3. **Prepare for Gate F UI smoke test** (once Gate C is green)
   - Run UI smoke checklist (`docs/governance/overseer/GATE_C_UI_SMOKE_TEST.md`)
   - Verify app boots and navigates primary surfaces without binding errors

4. **Clean up high-signal warnings**
   - Fix nullability warnings (CS8602/CS8604)
   - Fix async-without-await warnings (CS1998/CS4014)
   - Remove duplicated ViewModel base state patterns

---

## Engine Engineer

**Status:** ✅ **Gate E mostly complete, continuing quality improvements**

### Recent Completion

- ✅ **VS-0027 (DONE)** — So-VITS-SVC 4.0 engine structure + quality metrics error handling
  - Engine structure created with manifest-based discovery
  - Quality metrics now return actionable error messages for missing dependencies

### Next Tasks

1. **Verify quality metrics error handling**
   - Ensure PESQ/STOI/resemblyzer missing deps return actionable guidance
   - Test error messages are operator-clear

2. **Test So-VITS-SVC integration end-to-end**
   - Verify engine discovery works via manifest system
   - Test checkpoint loading from `models\checkpoints\<project>\`
   - Ensure engine can be instantiated and accessed via router

3. **Verify default engine selection**
   - Confirm `/api/voice/synthesize` defaults to XTTS → Piper → eSpeak fallback
   - Confirm `/api/transcribe` defaults to whisper_cpp
   - Test fallback chain works correctly

4. **Ensure model preflight integration**
   - Verify preflight checks are called in all engine routes
   - Test auto-download works for XTTS/Piper/Whisper
   - Ensure paths resolve to `E:\VoiceStudio\models` correctly

---

## Core Platform Engineer

**Status:** ✅ **Gate D complete, maintenance mode**

### Recent Completion

- ✅ **VS-0026 (DONE)** — Early crash artifact capture
  - Boot marker and pre-App exception logging
  - WER LocalDumps helper script
  - Crash artifact paths documented

### Next Tasks (Maintenance & Support)

1. **Monitor crash artifact collection**
   - Verify crash artifacts are captured for Gate C failures
   - Ensure boot markers and exception logs are written correctly

2. **Maintain backend preflight readiness**
   - Verify `/api/health/preflight` remains accurate
   - Ensure model root paths are reported correctly
   - Test ffmpeg discovery reporting

3. **Verify persistence systems**
   - Ensure audio artifact registry continues working
   - Verify job state persistence (voice cloning wizard) survives restarts
   - Test ProjectStore storage remains reliable

4. **Support other roles** as needed with runtime/storage questions

---

## System Architect

**Status:** ✅ **Architecture alignment, governance maintenance**

### Next Tasks

1. **Verify ledger ↔ handoff alignment**
   - Ensure all ledger entries have corresponding handoffs
   - Verify no orphaned handoff documents exist
   - Confirm ledger is single source of truth

2. **Lock Gate C artifact choice**
   - Document unpackaged apphost EXE as the Gate C standard
   - MSIX is not used; keep artifact lane locked. Any future change requires explicit Overseer approval + ADR.
   - Update blueprint alignment notes

3. **Validate contract boundaries**
   - Verify frontend/backend contract shapes remain stable (snake_case, endpoints)
   - Ensure no silent breaking changes across network boundary
   - Update `shared/` schemas if needed

4. **Review architecture decisions**
   - Monitor for any architecture drift
   - Record ADRs for significant decisions
   - Maintain alignment with architecture blueprints

---

## Overseer (Role 0)

**Status:** 🎯 **Driving Gate C to completion**

### Immediate Priorities

1. **Unblock Gate C (CRITICAL)**
   - Daily check-in with Build & Tooling Engineer on VS-0023 progress
   - Block any non-Gate-C work that doesn't move blockers forward
   - Escalate VS-0025 and VS-0012 immediately after VS-0023 completion

2. **Ledger Hygiene**
   - ✅ VS-0028 added to ledger
   - ✅ VS-0025 added to ledger
   - Verify VS-0023 handoff has latest status
   - Ensure all active work is captured

3. **Role Task Updates**
   - ✅ Updated role assignments (this document)
   - Monitor role progress on assigned tasks
   - Adjust priorities as blockers resolve

4. **Evidence Collection**
   - Ensure all Gate C blocker fixes have proof runs
   - Verify handoffs match ledger entries
   - Require proof before marking DONE

### Success Metrics

**Gate C Closure:**
- ✅ VS-0023: Release build produces launchable artifact
- ⏳ VS-0025: Release artifact launches without CoreMessagingXP.dll crash
- ⏳ VS-0012: App launches reliably on Gate C standard artifact

**Once Gate C is Green:**
- Release Engineer → VS-0003 (Installer)
- UI Engineer → Gate F smoke tests
- All downstream gates unblocked

---

**Last Updated:** 2025-01-28  
**Next Review:** After VS-0023 completion
