# Role Tasks Summary — 2025-01-28

> ⚠️ **NON-STATUS DOCUMENT — HISTORICAL SNAPSHOT**  
> **This document is a historical snapshot from 2025-01-28 and does NOT reflect current project status.**  
> **For authoritative status, see:** [`Recovery Plan/QUALITY_LEDGER.md`](../../../Recovery%20Plan/QUALITY_LEDGER.md)  
> **Current Gate Status:** Gate C: **DONE** (VS-0012), Gate H: **DONE** (VS-0003) per ledger
>
> **For the current “what’s next by role” snapshot, see:** [`ROLE_TASKS_SUMMARY_CURRENT.md`](ROLE_TASKS_SUMMARY_CURRENT.md)

## Current Project State (Historical — 2025-01-28)

**Gate C Status:** 🚨 **BLOCKED** (Historical — now DONE per ledger)  
**Critical Issue:** Build failure affecting both Debug and Release (Historical — resolved)  
**Ledger Status:** Updated but handoff mismatches need resolution (Historical — resolved)

---

## What Each Role Should Be Working On

### Build & Tooling Engineer (CRITICAL PATH) ⚡

**IMMEDIATE PRIORITY: Fix Build Failure**

**Current Blocker:** XAML compiler exit code 1 affecting both Debug and Release builds

**Tasks:**

1. **Investigate XAML compiler failure** (Today)

   - Check `xaml_compiler_raw.log` for actual error messages
   - Verify wrapper script error capture (`tools/xaml-compiler-wrapper.cmd`)
   - Check if output.json should exist (false-positive pattern from VS-0001)
   - Verify XAML syntax in control files (especially newly created ones)
   - Success: Identify root cause of XAML compiler failure

2. **Fix build failure** (Today)

   - Resolve XAML compilation errors
   - Verify both Debug and Release builds succeed
   - Success: Clean builds for both configurations

3. **Complete VS-0023 if active** (After build fix)
   - Verify if Release build configuration is still a blocker
   - If yes, add to ledger and complete
   - Success: Release build produces launchable artifact

**Blocking:** All other roles are blocked until builds work

---

### Release Engineer ⏸️ **BLOCKED**

**Status:** Waiting on Build & Tooling Engineer to fix build failure

**When Unblocked:**

1. **VS-0012 (TRIAGE)** - WinUI activation crash

   - Reproduce using fixed Release artifact
   - Verify runtime prerequisites for unpackaged launch
   - Document Gate C standard launch method
   - Single lane: unpackaged EXE + installer only (MSIX not used). If unpackaged fails, treat as Gate C blocker and fix prerequisites/runtime determinism.
   - Success: App launches reliably on Gate C artifact

2. **VS-0003 (IN_PROGRESS)** - Installer verification (Gate H)
   - Build installer using stable Release artifact
   - Test on clean Windows profiles: install → launch → upgrade → rollback
   - Verify prerequisites: .NET runtime, model root, ffmpeg
   - Success: Complete installer lifecycle proofs

**Cannot Proceed:** Build failure must be resolved first

---

### UI Engineer ✅

**Recent Completion:**

- ✅ All UI control stubs replaced with functional implementations (VS-0028)

**Current Focus:** Gate F Preparation

**Tasks:**

1. **Test implemented controls** (Once build is fixed)

   - Test WaveformControl, SpectrogramControl, etc. in AnalyzerView
   - Verify visualizations render correctly with real audio data
   - Test zoom and playback position features
   - Success: Controls work correctly with real data

2. **Fix remaining converter placeholders**

   - Implement NullToVisibilityConverter, DictionaryValueConverter
   - Ensure no converters throw NotImplementedException
   - Success: All converters have real implementations

3. **Clean up warnings**

   - Fix nullability warnings (CS8602/CS8604)
   - Fix async-without-await warnings (CS1998/CS4014)
   - Remove duplicated ViewModel base state patterns
   - Success: Warnings materially reduced

4. **Prepare for Gate F** (After Gate C is green)
   - Run UI smoke checklist
   - Verify app boots and navigates without binding errors
   - Success: Gate F readiness confirmed

**Note:** Some tasks blocked until build is fixed

---

### Engine Engineer ✅

**Status:** Gate E mostly complete, continuing improvements

**Recent Completion:**

- ✅ So-VITS-SVC 4.0 engine structure (VS-0027 - if confirmed in ledger)
- ✅ Quality metrics error handling improvements

**Current Focus:** Voice Cloning Quality

**Tasks:**

1. **Verify quality metrics error handling**

   - Ensure missing dependencies return actionable error messages
   - Test PESQ/STOI/resemblyzer error handling
   - Success: Clear, actionable errors when deps missing

2. **Test So-VITS-SVC integration**

   - Verify engine discovery via manifest system
   - Test checkpoint loading from `models\checkpoints\<project>\`
   - Ensure engine accessible via router
   - Success: So-VITS-SVC engine can be instantiated and used

3. **Verify default engine selection**

   - Confirm `/api/voice/synthesize` defaults to XTTS → Piper → eSpeak
   - Confirm `/api/transcribe` defaults to whisper_cpp
   - Test fallback chain works correctly
   - Success: Default engines work as expected

4. **Ensure model preflight integration**
   - Verify preflight checks called in all engine routes
   - Test auto-download for XTTS/Piper/Whisper
   - Ensure paths resolve to `E:\VoiceStudio\models` correctly
   - Success: Model availability checks work end-to-end

**Not Blocked:** Can continue independently, but verify work with ledger

---

### Core Platform Engineer ✅

**Status:** Gate D complete, maintenance mode

**Recent Completion:**

- ✅ Early crash artifact capture (VS-0026)
- ✅ All Gate D storage/runtime baseline work complete

**Current Focus:** Stability & Support

**Tasks:**

1. **Monitor crash artifact collection**

   - Verify crash artifacts captured for Gate C failures
   - Ensure boot markers and exception logs written correctly
   - Check LocalDumps helper script works
   - Success: Crash artifacts available when needed

2. **Maintain backend preflight readiness**

   - Verify `/api/health/preflight` remains accurate
   - Ensure model root paths reported correctly
   - Test ffmpeg discovery reporting
   - Success: Preflight endpoint remains reliable

3. **Verify persistence systems**

   - Ensure audio artifact registry continues working
   - Verify job state persistence survives restarts
   - Test ProjectStore storage remains reliable
   - Success: All persistence systems stable

4. **Support other roles** as needed with runtime/storage questions

**Not Blocked:** Maintenance work can continue

---

### System Architect ✅

**Status:** Architecture alignment and governance

**Current Focus:** Governance & Documentation

**Tasks:**

1. **Verify ledger-handoff alignment**

   - Ensure all ledger entries have corresponding handoffs
   - Verify no orphaned handoff documents
   - Reconcile VS-0023, VS-0027, VS-0028 mismatch
   - Success: Ledger is single source of truth

2. **Lock Gate C artifact choice**

   - Document unpackaged apphost EXE as Gate C standard
   - MSIX is not used; keep artifact lane locked. Any future change requires explicit Overseer approval + ADR.
   - Update blueprint alignment notes
   - Success: Gate C artifact choice is documented and locked

3. **Validate contract boundaries**

   - Verify frontend/backend contract shapes remain stable (snake_case, endpoints)
   - Ensure no silent breaking changes across network boundary
   - Update `shared/` schemas if needed
   - Success: Contract boundaries remain stable

4. **Review architecture decisions**
   - Monitor for architecture drift
   - Record ADRs for significant decisions
   - Maintain alignment with architecture blueprints
   - Success: Architecture decisions documented

**Not Blocked:** Governance work can continue

---

### Overseer (Role 0) 🎯

**Current Focus:** Drive Gate C to completion

**Immediate Actions:**

1. **Fix Build Failure** (CRITICAL)

   - Investigate XAML compiler exit code 1
   - Work with Build & Tooling Engineer to resolve
   - Success: Builds work again

2. **Resolve Ledger-Handoff Mismatch**

   - Decide on VS-0023, VS-0027, VS-0028 status
   - Add to ledger or archive handoffs
   - Success: Ledger and handoffs aligned

3. **Verify Gate C Blockers**

   - Confirm actual blockers vs potential blockers
   - Update ledger to reflect reality
   - Clear dependency chain
   - Success: Clear understanding of Gate C blockers

4. **Monitor Role Progress**
   - Daily check-ins on critical blockers
   - Block non-Gate-C work as needed
   - Ensure roles have clear next actions
   - Success: All roles unblocked and productive

---

## Summary by Priority

### 🔴 CRITICAL (Blocks Everything)

- **Build & Tooling Engineer:** Fix XAML compiler failure
- **Overseer:** Investigate and drive build fix

### 🟡 HIGH (Blocks Gate C)

- **Build & Tooling Engineer:** Complete VS-0023 if still active
- **Release Engineer:** Ready to proceed with VS-0012 once build is fixed

### 🟢 MEDIUM (Can Continue)

- **UI Engineer:** Test controls, fix converters (some tasks blocked by build)
- **Engine Engineer:** Continue quality improvements (not blocked)
- **Core Platform Engineer:** Maintenance and support (not blocked)
- **System Architect:** Governance and alignment (not blocked)

---

**Last Updated:** 2025-01-28  
**Next Review:** After build failure investigation complete
