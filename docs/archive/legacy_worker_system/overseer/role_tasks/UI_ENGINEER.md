# UI Engineer — Next task list

## Mission alignment

Deliver WinUI 3 UX correctness + MVVM wiring for voice cloning workflows, aligned to the design token system and the local-first backend.

## Current state snapshot (from evidence)

- ✅ Gate C is **DONE** (publish + `--smoke-ui` PASS; 0 binding failures).
- ✅ Gate H is **DONE** (VS-0003 installer lifecycle proof).
- UI warning backlog exists (nullability, async-without-await, shadowed base properties, etc.).
- ✅ **VS-0028 (COMPLETED)** - All UI control stubs replaced with functional Path-based rendering implementations (handoff exists, needs ledger reconciliation).

## What you do next (ordered)

### 1) Quality + functions UX readiness

- [x] When backend proof is green, surface required quality metrics/summary in the UI panels (keep token use consistent).
  - Evidence: `VoiceCloningWizardView.xaml` now uses display properties and shows MOS/Similarity/Naturalness/SNR/Artifacts/Clicks/Distortion.
  - Parsing hardened in `VoiceCloningWizardViewModel.cs` (`QualityMetricsItem` handles `JsonElement` values).
- [x] Spot-check the installed build with `--smoke-ui` to ensure no regression, but priority is on quality feature visibility.
  - Evidence: `%LOCALAPPDATA%\VoiceStudio\crashes\ui_smoke_summary.json` (exit_code 0, binding_failure_count 0).
- **Success**: UI can display the new quality outputs without binding failures.

### 2) Resolve MVVM “base state” duplication warnings (CS0108)

- [ ] Remove duplicated `IsLoading/StatusMessage/ErrorMessage/Dispose()` patterns in ViewModels and rely on `BaseViewModel` (or override `Dispose(bool)` properly).
- **Success**: no more “hides inherited member” warnings for those common properties.

### 3) Nullability + async correctness in touched surfaces

- [ ] Fix high-signal warnings without suppression:
  - `CS8602/CS8604` (null dereferences / bad args)
  - `CS1998/CS4014` (async methods without awaits / fire-and-forget)
- **Success**: warnings materially reduced in the panels used for voice cloning flows.

### 4) Localization + accessibility (no drift)

- [ ] Ensure user-facing strings in the voice workflows are localizable (`x:Uid` + `.resw`) and key controls have AutomationProperties.
- **Success**: UI meets the “no hardcoded user-facing text” + accessibility norms in the core voice panels.

**Code Quality Note:** Roslynator is integrated and configured as warnings (non-blocking). Fix warnings incrementally as you work to improve code quality and maintain clean UI code.
