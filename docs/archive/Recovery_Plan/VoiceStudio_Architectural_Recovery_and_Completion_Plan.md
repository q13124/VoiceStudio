# VoiceStudio — Architectural Recovery & Completion Plan (Native Desktop)

Date: 2025-12-26

This document defines a professional, build‑integrated route to restore a clean build, restore runtime stability, and ship a polished VoiceStudio desktop application with advanced capabilities.

---

## 1) Non‑negotiables

- Native Windows desktop application with a first‑class Windows UI.
- Offline‑first operation; network activity defaults to disabled.
- Deterministic builds: pinned versions, repeatable setup, automated enforcement.
- Strict separation between UI, domain logic, engines, storage, and diagnostics.
- Feature delivery follows a gated sequence: each gate produces a running application state before the next gate.

---

## 2) Roles (by responsibility)

These roles describe **responsibility boundaries**; one person can cover multiple roles.  
Every change must have **one primary Owner role** and **one Reviewer role** (can be the same person only for trivial doc-only changes).

### 2.1 The [OVERSEER] function (governance + drift prevention)

**Purpose:** Keep the project “by the book” — enforce architecture boundaries, rule compliance, and quality gates *before* features move forward.

**Non‑negotiable rules the Overseer enforces**
- **Functionality before features:** No “advanced” work while build/boot gates are red.
- **Single source of truth:** all bugs/issues go into `QUALITY_LEDGER.md` first (or at the same time), with a reproducible trigger.
- **Evidence-based progress:** each fix requires a *Proof Run* (commands + output summary).
- **No architectural drift:** dependency direction stays one-way; stable contracts only change via ADR.
- **Native desktop only:** no web UI, no “must-use cloud” dependencies; offline-first default.

**Overseer responsibilities (checklist)**
1. **Start-of-work sanity**
   - Confirm the current active gate (A→H) and which items are blocking it.
   - Confirm RuleGuard policy exists and is enabled in the build/CI.
2. **Intake**
   - Ensure any new bug/error is logged in `QUALITY_LEDGER.md` with Severity + Repro + Expected/Actual.
3. **Task slicing**
   - Break work into **≤ 1 day** tasks with a single success condition each.
   - Reject tasks that mix “fix build” + “add features” in the same change set.
4. **Gate enforcement**
   - Block moving to the next gate until the current gate has objective green proof.
5. **Merge discipline**
   - Require: ledger ID, passing RuleGuard, passing tests, and a short upgrade note.
6. **Release discipline**
   - Require: installer verify/repair, rollback note, crash-bundle export path verified.

**Overseer cadence**
- Works in cycles: **Log → Repro → Fix → Proof → Close**.
- Produces `[OVERSEER]` updates at the end of each cycle:
  - Gate status (A–H), top blockers, what changed, and next 1–3 actions.

---

### 2.2 Role playbooks (each role has its own “do / don’t”)

#### Role 0 — Overseer (Quality + Governance)
- **Owns:** gating, drift prevention, quality ledger hygiene, rule compliance.
- **May change:** docs, RuleGuard policy, CI gating configuration.
- **Must not change:** engine logic/UI logic unless acting as a temporary Owner role.
- **Definition of Done:** gates updated, ledger updated, RuleGuard enforced, proof attached.

#### Role 1 — System Architect
- **Owns:** module boundaries, dependency direction, public contracts, ADRs.
- **May change:** `core/api/*`, architectural interfaces, folder layout, plugin contracts (with ADR).
- **Must not change:** UI details or engine internals unless coordinated.
- **Required artifacts:**
  - ADR for any breaking change or new subsystem.
  - Contract tests updated when interfaces change.
- **DoD:** dependency graph unchanged or updated intentionally; contract tests green.

#### Role 2 — Build & Tooling Engineer
- **Owns:** deterministic builds, local setup, CI pipelines, RuleGuard integration.
- **May change:** MSBuild/solution settings, analyzers, `.editorconfig`, scripts, CI YAML.
- **Must not change:** app behavior unless tooling requires it.
- **Required artifacts:**
  - “Clean machine” build instructions (one command).
  - CI job that runs RuleGuard + tests + packaging smoke.
- **DoD:** `git clean -xfd` → build succeeds; CI green; RuleGuard green.

#### Role 3 — UI Engineer (Native Desktop)
- **Owns:** WinUI navigation, MVVM binding correctness, visual fidelity, accessibility, performance.
- **May change:** `ui/*`, XAML, viewmodels, design tokens/theme resources.
- **Must not change:** core storage/runtime contracts without architect signoff.
- **Required artifacts:**
  - UI smoke: app boots, navigation works, no binding errors in output.
  - Performance budget respected (no blocking calls on UI thread).
- **DoD:** UI gate passes; no XAML compiler errors; no runtime binding spam.

#### Role 4 — Core Platform Engineer
- **Owns:** orchestration, job runtime, storage, plugin host, domain models.
- **May change:** `core/runtime/*`, `core/storage/*`, `core/plugins/*`, serialization, migrations.
- **Must not change:** UI design rules or engine model code unless coordinated.
- **Required artifacts:**
  - Storage migrations idempotent, versioned, and tested.
  - Runtime job cancellation + error propagation proven.
- **DoD:** storage + runtime tests green; crash-safe writes; plugin host loads sample plugins.

#### Role 5 — Engine Engineer (TTS/Cloning/Audio)
- **Owns:** engine adapters, model lifecycle, GPU/CPU execution, audio IO consistency.
- **May change:** `engines/*`, adapter layer, DSP pipeline nodes, model caching.
- **Must not change:** UI or storage schemas without coordination.
- **Required artifacts:**
  - Golden audio test(s) for each engine integration.
  - Deterministic inference settings (seed/config) where possible.
- **DoD:** engine smoke works; latency/VRAM within budget; errors mapped to user-readable faults.

#### Role 6 — Release Engineer
- **Owns:** packaging, installer, upgrades, rollback, crash bundle export.
- **May change:** installer scripts, app manifest, signing pipeline (if any), versioning.
- **Must not change:** core behavior unless it affects packaging.
- **Required artifacts:**
  - Verify/Repair mode, uninstall clean, data folder preserved.
  - Upgrade/rollback notes and migration steps.
- **DoD:** installed app runs; upgrade works; rollback works; crash bundle exports.

---

### 2.3 Cross-role handshake rules (prevents “everyone edits everything”)

**Any change must declare:**
- Owner role
- Reviewer role
- Gate impacted (A–H)
- Ledger ID(s)

**Role escalation rule:**  
If a role needs to touch another role’s boundary, it must:
1) open/update an ADR (if architectural), or  
2) add a ledger entry (if defect), and  
3) request review from that role.

**What can ship without review?**
- Docs-only changes that do not alter behavior (still require ledger if addressing a defect).
- Formatting and comment changes (no functional diffs).


## 3) Target architecture (desktop‑first, engine‑agnostic)

### 3.1 Repository layout (high level)

```
VoiceStudio/
  app/
    VoiceStudio.App/                 # WinUI 3 desktop shell (MVVM)
    VoiceStudio.Core/                # Domain + orchestration + job runtime
    VoiceStudio.Contracts/           # DTOs, schemas, stable public contracts
    VoiceStudio.Storage/             # Project library, indexes, migrations
    VoiceStudio.Audio/               # DSP chain, meters, file IO, device IO
    VoiceStudio.Engines/             # Engine adapters (XTTS, Whisper, etc.)
    VoiceStudio.Plugins/             # Plugin host + packaging
    VoiceStudio.Diagnostics/         # Trace IDs, logs, crash bundles
    VoiceStudio.RuleGuard/           # Build‑integrated rule enforcement
  tools/
    vs-doctor/                       # Environment inspector + report generator
  docs/
    QUALITY_LEDGER.md                # Central defect ledger
    RUNBOOK.md                       # Operator actions (local, offline)
  installer/
    windows/                         # Installer project and assets
```

### 3.2 Dependency direction (one‑way)

- UI → Core → (Audio, Storage, Engines, Diagnostics, Plugins)
- Engines never import UI.
- Storage never imports UI.
- Diagnostics is import‑only (many modules write events; nothing depends on UI).

### 3.3 Runtime topology (single desktop process, optional local worker)

Default topology keeps a single desktop process. Engine workloads run as in‑proc jobs or as isolated local workers.

- **Desktop process**
  - UI thread (WinUI)
  - Job runtime (work queue, priorities, cancellation)
  - Engine execution (CPU/GPU)
- **Optional local worker**
  - Separate process for heavy engines
  - Typed IPC via the contracts package

This preserves a pure desktop experience (no browser UI) while keeping engine isolation available when stability or GPU memory pressure benefits.

### 3.4 Public contracts (stable seam)

All cross‑module communication uses types in `VoiceStudio.Contracts`.

Core contract groups:

- **Project**: ProjectId, Timeline, Track, Segment, AssetRef, RenderRef
- **Audio**: WaveFormat, LoudnessStats, MeterStats, ClipMetadata, EffectPreset
- **Engines**: EngineId, EngineCaps, SynthesisRequest, SynthesisResult, TranscriptResult
- **Diagnostics**: TraceId, EventEnvelope, CrashBundleRef
- **Plugins**: PluginId, PluginManifest, PermissionSet, CapabilitySet

### 3.5 Engine layer (adapter model)

Core engine interface examples (conceptual):

- `ITextToSpeechEngine`: synthesize, list voices, load model
- `ITranscriptionEngine`: transcribe, align, emit word‑timings
- `IEmbeddingEngine`: voice embedding, cache key generation
- `ITrainingEngine`: dataset ingest, fine‑tune runner, artifact export

Engine selection is runtime‑selectable. UI binds to capability descriptors rather than engine‑specific fields.

### 3.6 Plugin format (engine/effect/import/export/UI panels)

- Plugin packages ship with:
  - manifest (id, version, api range, capabilities, permissions)
  - signed hashes for integrity
  - entry points (engine adapter, effect adapter, importer/exporter, optional UI panel)
- The plugin host enforces:
  - version compatibility with the app API range
  - permission grants (fs scope, gpu access, net access default disabled)
  - optional subprocess isolation for high‑risk engines

---

## 4) Build‑integrated enforcement (RuleGuard)

### 4.1 What RuleGuard enforces

RuleGuard scans project‑controlled files and enforces:

- prohibited tokens from the master rule set
- architecture direction (module boundaries, forbidden dependencies)
- contract stability rules (public surface changes require versioning)
- packaging rules (no runtime writes outside app data locations)
- UI text rules (resource keys, no hard‑coded product strings)

### 4.2 How RuleGuard runs

- Runs as part of the standard build pipeline.
- Fails the build when violations appear.
- Produces a single report file in a stable path under the repository.

### 4.3 Scan scope

- Include: source code, XAML, JSON, PowerShell scripts, documentation
- Exclude: build artifacts, dependency caches, generated folders

---

## 5) Central ledger file (QUALITY_LEDGER.md)

A single ledger keeps every defect in one place with consistent structure and traceability. It prevents scattered remarks and gives a deterministic way to drive recovery.

A template file is included as a separate deliverable:
- `QUALITY_LEDGER.md`

Process rule:
- Each change links to one ledger entry ID.
- Each ledger entry contains a reproducible trigger and a proof run.

---

## 6) Recovery sequence (gated)

Each gate produces a running application state. A gate is not crossed until the proof run passes.

### Gate A — Deterministic environment

Observed failure patterns in the audit bundle:
- toolchain drift across Windows SDK versions and Windows App SDK package versions
- XAML compiler execution path using a different toolset lane than the rest of the build

Actions:
- Standardize SDK and Windows tooling versions for the repository.
- Add `vs-doctor` tool to produce an environment report with the exact installed versions.
- Align Windows target version consistently across all projects.
- Align Windows App SDK package versions consistently across all UI projects.

Proof run:
- Run environment inspector.
- Build solution from a clean workspace.
- Produce the report artifact.

Deliverable:
- Deterministic environment report stored under `docs/`.

### Gate B — Clean compile

Observed failure patterns in the audit bundle:
- WinUI API drift from UWP API usage (examples: ToolTipService on menu items, Application.Windows, Windows.UI.Text.FontWeights)
- unresolved base namespaces in multiple files (for example, `Exception` resolving fails when System imports are not present)
- collisions between toolkit types and custom types in the same namespace surface

Actions:
- Move UI‑API calls behind UI‑layer wrappers so the UI layer owns WinUI‑specific API usage.
- Add a single file for global imports to eliminate repeated unresolved namespace usage across the codebase.
- Resolve type collisions by renaming custom types or removing redundant definitions.

Proof run:
- Build succeeds with zero compiler failures.
- RuleGuard pass.

Deliverable:
- Desktop app builds locally from a single command.

### Gate C — App boot stability

Actions:
- Restore the startup path: initialization, window creation, navigation frame, resource dictionary load.
- Ensure crash‑safe initialization: diagnostics initializes first and writes a crash bundle path on failure.

Proof run:
- Launch app.
- Navigate across all primary pages without runtime exceptions.

Deliverable:
- App launches to a usable dashboard every time.

### Gate D — Core job runtime + storage baseline

Actions:
- Implement job queue with cancellation, priority lanes, and structured events.
- Implement project library storage with schema validation and migrations.
- Implement content‑addressed audio cache to deduplicate waveforms and model artifacts.

Proof run:
- Create a project, import audio, generate a derived artifact, close and relaunch the project, confirm artifacts appear.

Deliverable:
- Projects persist reliably across restarts.

### Gate E — Engine integration baseline

Actions:
- Standardize an engine interface (synthesis, transcription, embedding, training hooks).
- Implement at least one full engine path (XTTS family) including GPU lane and CPU lane.
- Implement one transcription engine (Whisper family) for dataset alignment.

Proof run:
- Import a voice clip.
- Run transcription.
- Synthesize speech with the selected engine.
- Export audio to the library.

Deliverable:
- End‑to‑end create → transcribe → synthesize → export.

### Gate F — Studio UX parity

Actions:
- Implement a Studio view: waveform, transport, A/B compare, meters, effects chain.
- Implement preset system for effects and voice settings.
- Implement history view with render provenance (engine, settings, input clip IDs).

Proof run:
- Create multiple renders, switch presets, replay audio, export stems.

Deliverable:
- Studio feature set usable for daily work.

### Gate G — Advanced capabilities

Actions:
- Plugin manager: install, activate, deactivate engine/effect/import/export plugins.
- Multi‑voice timeline: track lanes, per‑segment voice selection, stems export.
- Training workflows: dataset ingest, alignment, quality scoring, fine‑tune loop with safeguards.
- Overseer diagnostics: periodic in‑app status banner with alignment + build health + next actions.

Proof run:
- Install an engine plugin package.
- Create a multi‑voice project and export stems.
- Run a fine‑tune cycle on a small dataset and produce a new voice profile entry.

Deliverable:
- Advanced workflow end‑to‑end without external services.

### Gate H — Packaging and upgrades

Actions:
- Installer with repair path, clean uninstall, file associations, model cache location rules.
- Upgrade path supports rollback via snapshots.
- Crash bundle export includes logs, environment report, and last actions trace.

Proof run:
- Install, launch, create a project, upgrade from a prior build, keep projects intact, uninstall.

Deliverable:
- Production‑grade installer and upgrade experience.

---

## 7) Detailed work breakdown (small tasks)

This section defines a task decomposition that keeps changes atomic and traceable.

### 7.1 Build determinism tasks

- Create `vs-doctor` tool that outputs:
  - OS build, SDK versions, workloads present, PATH summary
  - NuGet cache location summary
  - repo pin summary
- Add CI pipeline steps:
  - restore
  - build
  - RuleGuard scan
  - packaging artifact build

### 7.2 UI stability tasks

- Central navigation service (route registry, back stack rules)
- Resource dictionary consolidation (theme tokens, icons, typography)
- MVVM binding hygiene (no code‑behind logic beyond view wiring)

### 7.3 Core runtime tasks

- Job runtime with:
  - deterministic IDs
  - cancellation tokens
  - structured events with trace IDs
- Storage with:
  - schema versioning
  - migration runner
  - atomic writes

### 7.4 Engine tasks

- Engine interface
- Model lifecycle manager (local paths only; network disabled by default)
- GPU execution policy (VRAM budgeting, fallback lane)

### 7.5 Advanced feature tasks

- Plugin packaging format and signature
- Multi‑voice timeline model and renderer
- Dataset alignment pipeline with quality scoring
- Fine‑tune runner with reproducible configs
- Offline documentation exporter for project provenance

---

## 8) Professional repo rules (embedded)

- Every change set updates the central ledger.
- Every public contract change increments a version and updates migration logic.
- Every UI string uses resource keys.
- Every engine call emits structured diagnostics events.
- Every file write routes via a storage API that enforces allowed directories.
- RuleGuard runs on every build and in CI.

---

## 9) Operating rhythm

- Work proceeds gate by gate in the order above.
- Each gate closes only after the proof run passes and the ledger entries are updated.

---

## Appendix A — Deliverables in this bundle

- `VoiceStudio_Architectural_Recovery_and_Completion_Plan.md`
- `QUALITY_LEDGER.md`
- `ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md`
