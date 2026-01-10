# UI Engineer — Next task list

## Mission alignment

Deliver WinUI 3 UX correctness + MVVM wiring for voice cloning workflows, aligned to the design token system and the local-first backend.

## Current state snapshot (from evidence)

- Gate C publish/launch path exists (unpackaged apphost EXE default).
- UI warning backlog exists (nullability, async-without-await, shadowed base properties, etc.).

## What you do next (ordered)

### 1) Remove converter placeholders (real implementations)

- [ ] Implement all `IValueConverter` stubs that still throw `NotImplementedException`.
  - Examples: `NullToVisibilityConverter`, `DictionaryValueConverter`, and other converters under `src/VoiceStudio.App/Converters/`
- **Success**: bindings that use converters cannot crash at runtime.

### 2) Resolve MVVM “base state” duplication warnings (CS0108)

- [ ] Remove duplicated `IsLoading/StatusMessage/ErrorMessage/Dispose()` patterns in ViewModels and rely on `BaseViewModel` (or override `Dispose(bool)` properly).
- **Success**: no more “hides inherited member” warnings for those common properties.

### 3) Nullability + async correctness in touched surfaces

- [ ] Fix high-signal warnings without suppression:
  - `CS8602/CS8604` (null dereferences / bad args)
  - `CS1998/CS4014` (async methods without awaits / fire-and-forget)
- **Success**: warnings materially reduced in the panels used for voice cloning flows.

### 4) Gate F / UI stability proof

- [ ] Run the UI smoke checklist (`docs/governance/overseer/GATE_C_UI_SMOKE_TEST.md` / related) once Gate C launch method is stable.
- **Success**: app boots + navigates primary surfaces without binding spam or crashes.
