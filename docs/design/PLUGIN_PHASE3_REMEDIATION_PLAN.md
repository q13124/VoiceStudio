# Phase 3 Plugin Migration — Architectural Review & Remediation Plan

**Status:** Complete  
**Date:** 2026-02-16  
**Author:** Lead/Principal Architect  
**Scope:** All Phase 3 deliverables (8 plugins, 3 templates, tests, docs)  
**Cross-reference:** `backend/services/plugin_service.py`, `app/core/plugins_api/base.py`, `backend/api/plugins/loader.py`, ADR-037

---

## 1. Executive Summary

Phase 3 delivered audio effect plugins, engine adapters, and format exporters. This plan captures findings from a full architectural review and a prioritized remediation roadmap. **Critical:** Two plugin loading paths exist: `PluginLoader` (used at FastAPI startup) correctly loads Phase 3 plugins; `PluginService` expects `PluginBase` subclasses and cannot load the 6 `BasePlugin`-derived plugins. Remediation is organized into four sprints (0–3).

---

## 2. Findings Summary

| Severity | Count | Description |
|----------|--------|-------------|
| **Critical** | 4 | Dual ABC, entry-point resolution, import path, PluginService cannot load BasePlugin plugins |
| **High** | 7 | Path traversal, LUFS silent fallback, engine imports, Python 3.10+ syntax, register() errors, test coverage, EngineProtocol.synthesize |
| **Medium** | 10 | Manifest isolation_mode, stub duplication, sample rates, __init__.py, template placeholders, conftest, presets, etc. |
| **Low** | 6 | Response schemas, docstrings, Phase 4 reference, performance numbers, list_voices, migration guide |

**Note:** Startup loading is done by `backend/api/plugins/loader.py` (PluginLoader), which uses `plugin.py` and `register(app, plugin_dir)` and adds the plugin dir to `sys.path`. So entry-point and bare-import issues (C3, C4) do **not** affect current startup; they affect only `PluginService.load_plugin()` if used.

---

## 3. Critical (Sprint 0)

- **C1/C2:** Two ABCs: `BasePlugin` (plugins_api) vs `PluginBase` (plugin_service). PluginService discovers only PluginBase; 6 plugins extend BasePlugin.
- **C3:** PluginService treats `entry_point` as file path (`plugin.register` → missing file). PluginLoader correctly uses `plugin.py` + `register` callable.
- **C4:** Bare imports (`from processor import ...`) work under PluginLoader (it adds plugin dir to sys.path); would fail if loaded via PluginService without path fix.

**Sprint 0 goals:** (1) Resolve dual-ABC via bridge or documentation; (2) If unifying, fix entry-point resolution and import path in PluginService.

---

## 4. High (Sprint 1)

- **H1:** Exporter plugins accept unvalidated `output_path` → path traversal risk.
- **H2:** Normalize plugin ignores `target_lufs` and treats `lufs` like `peak` (silent).
- **H3:** Engine plugin.py files import heavy engine modules at top level.
- **H4:** Adapters use `np.ndarray | None` (Python 3.10+); should use `Optional[np.ndarray]`.
- **H5:** No try/except in plugin `register()` functions.
- **H6:** No integration tests for plugin loading/registration lifecycle.
- **H7:** EngineProtocol has no `synthesize()`; adapter pattern relies on convention.

---

## 5. Medium (Sprint 2)

- **M1:** Manifests say `isolation_mode: "sandboxed"`; ADR-037 Lane A is in-process.
- **M2:** `_PluginServiceStub` duplicated in export_flac, export_opus, format-exporter template.
- **M3:** Engine response sample rates hardcoded (22050, 24000).
- **M4:** No `__init__.py` in plugin directories.
- **M5:** Format-exporter template `supported_formats = ["wav"]` should be tokenized.
- **M6:** Audio-effect-processor template never calls `activate()`.
- **M7:** Exporter tests don't assert correct AudioFormat passed to converter.
- **M8:** Reverb performance test uses non-deterministic random seed.
- **M9:** No shared conftest for plugin tests.
- **M10:** Preset JSONs not loaded at runtime.

---

## 6. Low (Sprint 3)

- **L1:** Inconsistent response envelopes across plugin types.
- **L2:** Missing class docstrings in concrete plugins.
- **L3:** ADR-037 Phase 4 reference with no roadmap doc.
- **L4:** Performance audit lacks actual benchmark numbers.
- **L5:** Engine adapters don't expose `list_voices()`.
- **L6:** Migration guide doesn't explain PluginService vs PluginLoader.

---

## 7. Remediation Sprints

### Sprint 0: Critical contract unification
- **S0.1:** Add LegacyPluginAdapter in plugin_service to wrap BasePlugin as PluginBase, **or** document that startup loading is PluginLoader-only and PluginService is for future PluginBase plugins.
- **S0.2:** In PluginService.load_plugin(), parse `entry_points.backend` as `module.function` (e.g. `plugin.register` → load `plugin.py`, call `register(app, path)`).
- **S0.3:** When loading via PluginService, add plugin path to sys.path around load; remove after.

### Sprint 1: High-severity fixes
- **S1.1:** Path validator for exporter output_path (allowlist directory).
- **S1.2:** Normalize: implement LUFS or raise NotImplementedError for mode="lufs".
- **S1.3:** Lazy or deferred engine class import in engine plugin.py files.
- **S1.4:** Replace `np.ndarray | None` with `Optional[np.ndarray]` in adapters.
- **S1.5:** try/except and logging in all register() functions.
- **S1.6:** Integration tests: load each plugin via loader, TestClient, health + route existence.
- **S1.7:** Document or add synthesize() to EngineProtocol.

### Sprint 2: Medium
- **S2.1:** Manifest isolation_mode → in_process / lane_a.
- **S2.2:** Shared PluginServiceStub in backend/services/plugin_service_testing.py.
- **S2.3:** Engine-reported sample rate in adapter/response.
- **S2.4:** Add __init__.py to all 8 plugin dirs.
- **S2.5:** Format-exporter template token for supported_formats.
- **S2.6:** Call activate() in processor template register().
- **S2.7:** Exporter tests assert target_format.
- **S2.8:** Reverb test: fixed RNG seed.
- **S2.9:** conftest.py with fake_engine, deterministic_audio, mock_converter.
- **S2.10:** Preset loading helper (optional).

### Sprint 3: Low
- **S3.1:** Standardize plugin response envelope.
- **S3.2:** Class docstrings for concrete plugins.
- **S3.3:** Phase 4 roadmap placeholder and ADR-037 link.
- **S3.4:** Performance audit with real numbers.
- **S3.5:** list_voices() stub for engine adapters.
- **S3.6:** Migration guide: PluginService vs PluginLoader, troubleshooting.

---

## 8. Verification Gates

- **Sprint 0:** PluginService can load (or document why not) all 8 plugins; no regression in PluginLoader.
- **Sprint 1:** Unit + new integration tests pass; path traversal test rejects invalid path; LUFS behavior documented or implemented.
- **Sprint 2:** Manifests validate; tests deterministic; conftest in use.
- **Sprint 3:** Response schema consistent; migration guide updated.
- **Final:** `pytest tests/` and `dotnet build` pass; all manifests validate.

---

## 9. Progress (implemented)

- **C3 (S0.2):** Entry-point resolution fixed — all 8 manifests use `"backend": "register"` (function name only); loader resolves correctly via `getattr(module, "register")`.
- **C4 (S0.3):** `sys.modules` contamination fixed — `PluginLoader._load_plugin()` snapshots `sys.modules` before loading and removes plugin-local bare-import modules (e.g. `processor`, `adapter`) after loading, ensuring each plugin gets its own fresh copy.
- **H1 (S1.1):** Path validation for exporter `output_path` — `backend/services/export_path_validator.py`; FLAC/Opus plugins call `validate_export_path()` in export endpoint.
- **H2 (S1.2):** Normalize plugin raises `NotImplementedError` for `mode="lufs"` with clear message; peak unchanged.
- **H3 (S1.3):** Lazy engine import in `engine_xtts_v2`, `engine_piper`, `engine_bark` — engine class resolved in `initialize()` via `importlib.import_module` + `getattr`.
- **H4 (S1.4):** Adapters use `Optional[np.ndarray]` in place of `np.ndarray | None`.
- **H5 (S1.5):** try/except + `logger.exception` in all 8 plugin `register()` functions; re-raise after log.
- **H6 (S1.6):** Integration tests added — `tests/integration/plugins/test_plugin_loading.py` (14 tests): plugin loading via PluginLoader, health endpoints, route existence, manifest validation, metadata recording.
- **H7 (S1.7):** `synthesize()` convention documented on `EngineProtocol` class docstring (duck-typed, engine-specific signatures).
- **M1 (S2.1):** All 8 manifests updated `isolation_mode` from `"sandboxed"` to `"in_process"` (ADR-037 Lane A).
- **M2 (S2.2):** Shared `PluginServiceStub` in `backend/services/plugin_service_testing.py`; FLAC/Opus and exporter tests use it.
- **M4 (S2.4):** `__init__.py` added to all 8 plugin packages.
- **M5 (S2.5):** Format-exporter template tokenized: `{{TARGET_FORMAT}}`, `{{FORMAT_ENUM}}`; uses shared `PluginServiceStub` and `validate_export_path`; has try/except in `register()`.
- **M6 (S2.6):** Audio-effect-processor template calls `plugin._initialized = True` in `register()` (sync-safe activation); has try/except and logging.
- **M7 (S2.7):** Exporter tests assert `target_format` (FLAC/Opus) via `_FakeConverter.last_call_kwargs`.
- **M8 (S2.8):** Reverb test uses `np.random.default_rng(5678)` for deterministic audio.
- **M9 (S2.9):** Shared `conftest.py` at `tests/unit/backend/services/conftest.py` with `deterministic_audio_24k`, `deterministic_audio_44k`, `sine_wave_24k`, `sine_wave_44k`, `FakeEngine`, `FakeConverter`, `PluginServiceStub` fixtures.

- **S0.1:** Dual-ABC documented in `docs/plugins/migration-guide.md` — "Plugin Loading Systems" section with PluginLoader vs PluginService comparison, base class guidance, and troubleshooting table. Bridge deferred to future unification work.
- **S2.3 (M3):** Engine adapter `sample_rate` property added to all 3 adapters; queries engine's `sample_rate` attribute, falls back to class constant. Plugin responses now use `self._adapter.sample_rate`.
- **L1 (S3.1):** Typed Pydantic response models added: `SynthesizeResponse` for engine plugins, `ExportResponse` for exporter plugins; no more raw dicts.
- **L2 (S3.2):** Class docstrings added to all 8 concrete plugin classes.
- **L6 (S3.6):** Migration guide updated with dual-ABC rationale, loader comparison, base class decision table, and troubleshooting.
- **Infra:** Added `plugins/__init__.py` (parent package) to support `plugins.<name>.module` imports in tests.

**Remaining:** S2.10 (preset loading, optional — N/A, no presets in scope), L4 (performance audit needs CI benchmark harness — deferred to Phase 4). All other items implemented.

---

## 10. Phase 4 Roadmap Placeholder

The following topics remain open for Phase 4 planning.  Each should be addressed in a dedicated Phase 4 plan document (`docs/plugin-phase4-plan.md`) before implementation begins.

| ID | Topic | Notes |
|----|-------|-------|
| P4-1 | **Unify BasePlugin / PluginBase** | Converge the dual-ABC into a single base class with optional mixins (see migration guide §Plugin Loading Systems). Requires careful migration of all 8 Phase 3 plugins and `PluginService` consumers. |
| P4-2 | **Sandboxed isolation (Lane B)** | ADR-037 defines Lane B for third-party plugins requiring `isolation_mode: "sandboxed"`. Implement subprocess/container isolation, IPC bridge, and resource quotas. |
| P4-3 | **Plugin marketplace / discovery** | Enable users to install community plugins from a registry. Requires trust scoring, signing, and a UI panel. |
| P4-4 | **Engine adapter `list_voices()` population** | Phase 3 added `list_voices()` stubs; Phase 4 should wire them to actual engine voice inventories. |
| P4-5 | **Preset system** | Define a plugin preset schema, storage, and UI for user-defined and bundled presets. |
| P4-6 | **Performance benchmarks** | Establish a CI-gated benchmark suite measuring plugin load time, audio processing latency, and memory footprint. |

Cross-reference: ADR-037 (Trust Lane Model), `docs/plugins/migration-guide.md`.

---

## 11. References

- ADR-036 Plugin System Unification  
- ADR-037 Plugin Trust Lane Model  
- docs/plugins/migration-guide.md  
- docs/plugins/engine-adapter-pattern.md  
- backend/api/plugins/loader.py (startup loader)  
- backend/services/plugin_service.py (PluginBase lifecycle)  
- docs/plugin-phase3-plan.md (original Phase 3 plan)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-16 | Initial plan from Phase 3 architectural review. |
| 2026-02-16 | Implemented H1, H2, H3, H4, H5, M2, M4, M7, M8; added Progress §9. |
| 2026-02-17 | Implemented C3, C4, H5, H6, H7, M1, M5, M6, M9; loader module isolation; integration tests; format-exporter/processor template hardened. |
| 2026-02-17 | Implemented S0.1, S2.3, L1, L2, L6; dual-ABC documented; adapter sample rates; typed response models; class docstrings; migration guide. All sprints 0–3 substantively complete. |
| 2026-02-17 | Implemented L3 (Phase 4 roadmap §10), L5 (`list_voices()` on all 3 adapters + GET /voices endpoints). S2.10 cancelled (no presets in scope). L4 deferred to Phase 4 CI benchmark harness. Plan complete. |
