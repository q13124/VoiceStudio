## VoiceStudio Feature / Function Map (file-mapped)

### Scope snapshot

- **Repository root**: `E:\VoiceStudio`
- **Drive scope**: `E:\` (project-dedicated drive; see inventory artifact below)
- **Snapshot date**: 2025-12-27
- **Machine-readable artifacts produced**
  - **Drive inventory**: `docs/governance/E_DRIVE_INVENTORY.json`
  - **Engine manifest catalog**: `docs/governance/ENGINE_MANIFEST_CATALOG.json`
  - **Backend route catalog**: `docs/governance/BACKEND_ROUTE_CATALOG.json`

### How to regenerate the artifacts

- **Drive inventory**
  - `python tools/inventory_drive.py --root "E:\" --max-depth 2 --output "docs\governance\E_DRIVE_INVENTORY.json"`
- **Engine manifest catalog**
  - `python tools/extract_engine_manifest_catalog.py --output "docs\governance\ENGINE_MANIFEST_CATALOG.json"`
- **Backend route catalog**
  - `python tools/extract_backend_route_catalog.py --output "docs\governance\BACKEND_ROUTE_CATALOG.json"`

---

## Drive inventory (E:\) summary

### Top-level classification (from `docs/governance/E_DRIVE_INVENTORY.json`)

| Path | Classification | Files | Dirs | Size (bytes) |
|------|----------------|-------|------|--------------|
| `E:\VoiceStudio` | product_source | 28,136 | 1,889 | 576,962,010 |
| `E:\Error Audits` | audit_bundle | 19 | 1 | 20,097,726 |
| `E:\cursor` | tooling_cache | 8,770 | 2,101 | 612,506,449 |
| `E:\System Volume Information` | system | 0 | 1 | 0 |
| `E:\` (root files bucket) | unclassified | 11 | 0 | 386,714 |

Other unclassified top-level folders exist on `E:\` (see the full inventory JSON for the complete list and stats).

**Scan detail**: `E:\System Volume Information` is not readable without elevation; the inventory records the expected permission error.

---

## Architecture map (what exists today)

### Native Windows app (WinUI 3 / .NET 8)

- **Solution entry**: `VoiceStudio.sln`
- **Primary app project**: `src/VoiceStudio.App/VoiceStudio.App.csproj`
- **Unit/UI coverage project**: `src/VoiceStudio.App.Tests/VoiceStudio.App.Tests.csproj`
- **Shared/core project**: `src/VoiceStudio.Core/VoiceStudio.Core.csproj` (currently minimal; many “Core.*” namespaces live under `src/VoiceStudio.App/`)

### Local backend API (Python / FastAPI)

- **Backend entry**: `backend/api/main.py`
- **Startup helper**: `start_backend.ps1` (uvicorn launcher)
- **WebSockets**: `backend/api/ws/`
- **Routes (per-module)**: `backend/api/routes/` (see `docs/governance/BACKEND_ROUTE_CATALOG.json`)

### Local engine layer (Python, manifest-driven)

- **Engine manifests**: `engines/**/engine.manifest.json` (44 manifests; see `docs/governance/ENGINE_MANIFEST_CATALOG.json`)
- **Runtime engine manifests**: `engines/**/runtime.manifest.json` (1 manifest)
- **Engine implementations**: `app/core/engines/*_engine.py`
- **Engine router + manifest loader**: `app/core/engines/router.py`, `app/core/engines/manifest_loader.py`
- **Runtime process manager**: `app/core/runtime/runtime_engine.py`

### Plugins

- **Plugin packages (Python)**: `plugins/*/manifest.json`, `plugins/*/plugin.py`
- **Backend plugin loader**: `backend/api/plugins/loader.py`, `backend/api/plugins/integration.py`
- **UI plugin loader (C#)**: `src/VoiceStudio.App/Services/PluginManager.cs`
- **UI plugin contract (C#)**: `src/VoiceStudio.App/Core/Plugins/IPlugin.cs`

### Installer / packaging

- **Inno Setup**: `installer/VoiceStudio.iss`
- **WiX**: `installer/VoiceStudio.wxs`
- **Build/installer integrity scripts**: `installer/*.ps1`, `scripts/package_release.ps1`, `scripts/prepare-release.ps1`

### Shared contracts (UI ↔ backend)

- **JSON schema contracts**: `shared/contracts/*.schema.json`

### Repository top-level map (where to look first)

- **`app/`**: Python core runtime (engines, training, audio, resilience), plus a legacy WinUI shell copy under `app/ui/`
- **`backend/`**: FastAPI backend (`backend/api/`) + MCP bridge (`backend/mcp_bridge/`) + local MCP server(s) (`backend/mcp_servers/`)
- **`docs/`**: governance, design specs, recovery plans, plus generated catalogs under `docs/governance/`
- **`engines/`**: declarative engine registrations (`engine.manifest.json`, `runtime.manifest.json`)
- **`installer/`**: installer sources (Inno Setup + WiX) and installer integrity scripts
- **`models/`**: example trained model artifacts + metadata (project-local sample content)
- **`plugins/`**: example Python plugins (manifest-driven)
- **`scripts/`**: packaging, export, and maintenance scripts (PowerShell + Python)
- **`shared/`**: shared JSON schemas used as UI↔backend contracts
- **`src/`**: WinUI 3 application source (C# + XAML) + app tests
- **`tests/`**: Python tests (unit/integration/e2e/performance/quality) + contract tests
- **`tools/`**: migration, inspection, inventory, and catalog generation tools
- **Build diagnostics / forensics**
  - **`*.binlog` / `*.log`**: MSBuild logs and build output captures
  - **`.buildlogs/`**: XAML compiler diagnostics and extracted `.g.cs` dumps
  - **`xaml_bisect_tmp/`**: XAML bisect outputs

---

## Intended capabilities (from recovery plan + design specs)

### Recovery gates A–H (from `Recovery Plan/VoiceStudio_Architectural_Recovery_and_Completion_Plan.md`)

- **Gate A — Deterministic environment**
  - **Focus**: stable SDK/WinAppSDK alignment, repeatable environment inspection
- **Gate B — Clean compile**
  - **Focus**: eliminate compiler failures; isolate WinUI API drift behind UI wrappers
- **Gate C — App boot stability**
  - **Focus**: crash-safe startup, reliable window creation/navigation/resource loading
- **Gate D — Core job runtime + storage baseline**
  - **Focus**: job queue + project storage + content-addressed cache
- **Gate E — Engine integration baseline**
  - **Focus**: standard engine interface + at least one full TTS path + one transcription path
- **Gate F — Studio UX parity**
  - **Focus**: waveform/transport/A-B compare/meters/effects chain + presets + provenance
- **Gate G — Advanced capabilities**
  - **Focus**: plugin manager, multi-voice timeline, training workflows, overseer diagnostics
- **Gate H — Packaging and upgrades**
  - **Focus**: installer, repair/uninstall, upgrade/rollback, crash bundle export

### UI shell non-negotiables (from `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`)

- **Layout**: 3-row grid; main workspace with Nav rail + Left/Center/Right + Bottom dock
- **Panel hosting**: 4 `PanelHost` containers
- **MVVM**: every panel has separate `.xaml`, `.xaml.cs`, and `ViewModel.cs`
- **Design tokens**: `VSQ.*` resources (see `src/VoiceStudio.App/Resources/DesignTokens.xaml`)

---

## Feature/function map (by subsystem)

### UI shell + composition (WinUI 3)

- **Purpose**: desktop “studio” shell with docked panels, command surface, status strip, overlays
- **Primary entry points**
  - **App startup**: `src/VoiceStudio.App/App.xaml.cs`
  - **Main window**: `src/VoiceStudio.App/MainWindow.xaml`, `src/VoiceStudio.App/MainWindow.xaml.cs`
- **Key controls**
  - **Panel hosting**: `src/VoiceStudio.App/Controls/PanelHost.xaml`, `src/VoiceStudio.App/Controls/PanelHost.xaml.cs`
  - **Panel stacking / tabs**: `src/VoiceStudio.App/Controls/PanelStack.xaml`, `src/VoiceStudio.App/Controls/PanelStack.xaml.cs`
  - **Resize handle**: `src/VoiceStudio.App/Controls/PanelResizeHandle.xaml`
  - **Toolbar**: `src/VoiceStudio.App/Controls/CustomizableToolbar.xaml`, `src/VoiceStudio.App/Controls/CustomizableToolbar.xaml.cs`
  - **Global search overlay UI**: `src/VoiceStudio.App/Views/GlobalSearchView.xaml`
- **Panel registry system**
  - **Contracts + registry**: `src/VoiceStudio.App/Core/Panels/*`
  - **Auto catalog of XAML surfaces**: `app/core/PanelRegistry.Auto.cs`
  - **Panel consistency script**: `app/cli/verify_panels.py`

### UI panels (WinUI 3) — functional surface area

**Canonical list**: `app/core/PanelRegistry.Auto.cs` (XAML paths). Below is the functional grouping and the key file pattern.

- **Voice synthesis / cloning / speech**
  - **Purpose**: text→speech, quick cloning, guided cloning, voice browsing, morph/blend, style transfer
  - **Entry points**: panels under `src/VoiceStudio.App/Views/Panels/`
  - **Key files (examples)**
    - `VoiceSynthesisView.xaml` + `ViewModels/VoiceSynthesisViewModel.cs`
    - `VoiceQuickCloneView.xaml` + `ViewModels/VoiceQuickCloneViewModel.cs`
    - `VoiceCloningWizardView.xaml` + `ViewModels/VoiceCloningWizardViewModel.cs`
    - `VoiceBrowserView.xaml` + `ViewModels/VoiceBrowserViewModel.cs`
    - `VoiceMorphView.xaml` + `ViewModels/VoiceMorphViewModel.cs`
    - `VoiceMorphingBlendingView.xaml` + `ViewModels/VoiceMorphingBlendingViewModel.cs`
    - `VoiceStyleTransferView.xaml` + `ViewModels/VoiceStyleTransferViewModel.cs`
- **Timeline / recording / projects**
  - **Purpose**: project structure, tracks, clip placement, recording capture, markers/scenes
  - **Key files (examples)**
    - `TimelineView.xaml` + `Views/Panels/TimelineViewModel.cs`
    - `MiniTimelineView.xaml` + `Views/Panels/MiniTimelineViewModel.cs`
    - `RecordingView.xaml` + `ViewModels/RecordingViewModel.cs`
    - `SceneBuilderView.xaml` + `ViewModels/SceneBuilderViewModel.cs`
    - `MarkerManagerView.xaml` + `ViewModels/MarkerManagerViewModel.cs`
- **Mixing / effects / automation**
  - **Purpose**: mixer-style control surface, effects routing, automation curves/macros
  - **Key files (examples)**
    - `EffectsMixerView.xaml` + `Views/Panels/EffectsMixerViewModel.cs`
    - `AutomationView.xaml` + `ViewModels/AutomationViewModel.cs`
    - `MacroView.xaml` + `Views/Panels/MacroViewModel.cs`
    - `AIMixingMasteringView.xaml` + `ViewModels/AIMixingMasteringViewModel.cs`
- **Analysis / visualization**
  - **Purpose**: spectrograms, waveform analysis, sonography, quality dashboards
  - **Key files (examples)**
    - `SpectrogramView.xaml` + `ViewModels/SpectrogramViewModel.cs`
    - `AudioAnalysisView.xaml` + `ViewModels/AudioAnalysisViewModel.cs`
    - `SonographyVisualizationView.xaml` + `ViewModels/SonographyVisualizationViewModel.cs`
    - `AdvancedWaveformVisualizationView.xaml` + `ViewModels/AdvancedWaveformVisualizationViewModel.cs`
    - `AdvancedSpectrogramVisualizationView.xaml` + `ViewModels/AdvancedSpectrogramVisualizationViewModel.cs`
- **Training**
  - **Purpose**: dataset ingest/editing, training workflows, training quality visualization
  - **Key files (examples)**
    - `TrainingView.xaml` + `Views/Panels/TrainingViewModel.cs`
    - `TrainingDatasetEditorView.xaml` + `ViewModels/TrainingDatasetEditorViewModel.cs`
    - `TrainingQualityVisualizationView.xaml` + `ViewModels/TrainingQualityVisualizationViewModel.cs`
- **System / diagnostics**
  - **Purpose**: diagnostics console, job progress, GPU/system status, dashboards, help/shortcuts
  - **Key files (examples)**
    - `DiagnosticsView.xaml` + `Views/Panels/DiagnosticsViewModel.cs`
    - `JobProgressView.xaml` + `ViewModels/JobProgressViewModel.cs`
    - `GPUStatusView.xaml` + `ViewModels/GPUStatusViewModel.cs`
    - `MCPDashboardView.xaml` + `ViewModels/MCPDashboardViewModel.cs`
    - `KeyboardShortcutsView.xaml` + `Views/KeyboardShortcutsView.xaml.cs`

### UI services (WinUI 3)

- **Purpose**: local orchestration for UI state, backend communications, plugin discovery, diagnostics, UI utilities
- **Service locator**: `src/VoiceStudio.App/Services/ServiceProvider.cs`
- **Backend client adapter**: `src/VoiceStudio.App/Services/BackendClientAdapter.cs`
- **Update service**: `src/VoiceStudio.App/Services/UpdateService.cs`
- **Panel state + layout**: `src/VoiceStudio.App/Services/PanelStateService.cs`
- **Operation queue**: `src/VoiceStudio.App/Services/OperationQueueService.cs`
- **Status bar activity**: `src/VoiceStudio.App/Services/StatusBarActivityService.cs`
- **Plugin loader**: `src/VoiceStudio.App/Services/PluginManager.cs`

### Backend API (FastAPI)

- **Purpose**: local-first API surface for engines, projects, synthesis, analysis, training, automation, and dashboards
- **Entry point**: `backend/api/main.py`
- **Startup scripts**
  - `start_backend.ps1`
  - `start_backend_alt_port.ps1`
- **Dependencies**
  - `requirements.txt` (backend + shared Python deps)
- **Route inventory**
  - Full machine-readable list: `docs/governance/BACKEND_ROUTE_CATALOG.json`
  - Router registration: `backend/api/main.py` (`app.include_router(...)` per module)
- **WebSockets**
  - `/ws/events`: `backend/api/ws/events.py` (legacy heartbeat stream)
  - `/ws/realtime`: `backend/api/ws/realtime.py` (topic-based realtime stream)
- **Core support**
  - **Error handling**: `backend/api/error_handling.py`, `backend/api/exceptions.py`
  - **Response caching**: `backend/api/response_cache.py`
  - **Rate limiting**: `backend/api/rate_limiting.py`, `backend/api/rate_limiting_enhanced.py`
  - **Audio processing helpers**: `backend/api/audio_processing/*`
  - **Quality utilities**: `backend/api/utils/quality_*`

### MCP bridge layer (backend)

- **Purpose**: normalize MCP server responses into `shared/contracts/` schemas
- **Docs**: `backend/mcp_bridge/README.md`
- **Client(s)**: `backend/mcp_bridge/pdf_unlocker_client.py`
- **Local MCP server(s)**: `backend/mcp_servers/`
  - `backend/mcp_servers/mcp-unlock-pdf/` (server entry: `main.py`)
- **API surface example**
  - `/api/pdf/*` routes: `backend/api/routes/pdf.py`

### Engine manifest registry (declarative)

- **Purpose**: engine discovery without hardcoded lists (audio/image/video engines)
- **Root**: `engines/`
- **Config**: `engines/config.json`
- **Machine-readable catalog**: `docs/governance/ENGINE_MANIFEST_CATALOG.json`
- **Manifest schema examples**
  - `engines/audio/xtts_v2/engine.manifest.json`
  - `engines/audio/xtts_v2/runtime.manifest.json`

### Engine runtime + implementations (Python)

- **Purpose**: local engine execution (in-process + out-of-process), model management, quality metrics
- **Dependencies**
  - `requirements_engines.txt` (engine-adjacent Python deps)
  - `requirements_missing_libraries.txt` (audit/diagnostic list)
- **Core router + manifest plumbing**
  - `app/core/engines/router.py`
  - `app/core/engines/manifest_loader.py`
  - `app/core/engines/protocols.py`
  - `app/core/engines/config.py`
- **Runtime engine manager**
  - `app/core/runtime/runtime_engine.py`
  - `app/core/runtime/engine_hook.py`
- **Engine implementations**
  - `app/core/engines/*_engine.py` (examples: `xtts_engine.py`, `chatterbox_engine.py`, `tortoise_engine.py`, `whisper_engine.py`)
- **Model storage rules**
  - `%PROGRAMDATA%\VoiceStudio\models\...` (mirrored in manifests and environment inspection tools)
  - Env verifier: `tools/verify_env.py`

### Audio processing + quality (Python)

- **Purpose**: post-processing chains, metrics, benchmarking/QA tools, optimization
- **Audio modules**: `app/core/audio/*`
- **Quality metrics + optimization (engine-adjacent)**: `app/core/engines/quality_metrics*.py`, `app/core/engines/quality_optimizer.py`
- **Benchmark tooling**: `app/core/tools/audio_quality_benchmark.py`, `app/core/tools/dataset_qa.py`, `app/core/tools/quality_dashboard.py`

### Training system (Python)

- **Purpose**: training workflows, parameter optimization, progress monitoring
- **Modules**: `app/core/training/*` (examples: `unified_trainer.py`, `auto_trainer.py`, `parameter_optimizer.py`)
- **Backend routes**: `backend/api/routes/training.py`, `backend/api/routes/training_audit.py`, `backend/api/routes/dataset.py`

### Plugins (Python + C#)

- **Purpose**: extensibility surface for engines/effects/import/export and optional UI panels
- **Python plugin API**: `app/core/plugins_api/*`
- **Python plugins directory**: `plugins/*`
- **Backend plugin loader**: `backend/api/plugins/*`
- **C# plugin system**
  - Contract: `src/VoiceStudio.App/Core/Plugins/IPlugin.cs`
  - Loader: `src/VoiceStudio.App/Services/PluginManager.cs`

### Installer + releases

- **Purpose**: packaging, install/repair/uninstall, upgrades
- **Installer sources**
  - `installer/VoiceStudio.iss`
  - `installer/VoiceStudio.wxs`
- **Build and installer integrity scripts**
  - `installer/build-installer.ps1`
  - `installer/verify-installer.ps1`
  - `scripts/prepare-release.ps1`
  - `scripts/package_release.ps1`

### Tooling / audits

- **Purpose**: inspection, migrations, inventory, openapi export, panel discovery
- **Catalog scripts**
  - `tools/inventory_drive.py`
  - `tools/extract_engine_manifest_catalog.py`
  - `tools/extract_backend_route_catalog.py`
- **Panel tooling**
  - `tools/Find-AllPanels.ps1`
  - `app/cli/verify_panels.py`
- **OpenAPI export**
  - `scripts/export_openapi_schema.py`
  - `scripts/export_openapi.py`

### Coverage suites

- **Purpose**: regression coverage for contracts, engines, backend routes, and UI-level flows
- **Root**: `tests/`
- **Key areas**
  - `tests/unit/`: unit suite (Python)
  - `tests/integration/`: integration suite (Python + some C# harnesses)
  - `tests/e2e/`: end-to-end suite (Python)
  - `tests/performance/`: performance suite (Python)
  - `tests/quality/`: quality-oriented suite (Python)
  - `tests/contract/`: contract validation suite (schemas, templates, and a `.csproj`)

---

## Solved failures (documented) vs reproducible now

### Build / XAML pipeline

- **Documented fix: Pass2 dependency ordering**
  - **Docs**: `PASS2_DEPENDENCY_FIX.md`
  - **Code**: `Directory.Build.targets` (`MarkupCompilePass2DependsOn` includes `CoreCompile`)
  - **Repo presence**: present in repo; XamlCompiler still exits with code 1 (see below)

- **Documented fix: XamlGeneratedOutputPath trailing backslash**
  - **Docs**: `BUILD_FIX_ANALYSIS_2025-01-28.md`, `XAML_COMPILATION_ISSUE_SUMMARY.md`
  - **Code**: `Directory.Build.targets` sets `XamlGeneratedOutputPath` via `TrimEnd('\')`
  - **Repo presence**: the `dotnet build` XamlCompiler invocation uses single-backslash paths; XamlCompiler still exits with code 1

- **Reproducible now: XamlCompiler exit code 1**
  - **Docs**: `XAML_COMPILER_DIAGNOSTIC_REPORT_2025-01-28.md`, `XAML_COMPILATION_ISSUE_SUMMARY.md`
  - **Current proof run**: `dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Debug -p:Platform=x64`
  - **Current outcome**: still fails with `MSB3073` from `Microsoft.UI.Xaml.Markup.Compiler.interop.targets`

### Engine dependency handling

- **Documented fix: fail-fast on dependency-not-installed conditions (no silent fallback when dependencies are not installed)**
  - **Docs**: `docs/governance/ENGINE_DEPENDENCY_FIX_COMPLETE_2025-01-28.md`
  - **Code**:
    - `app/core/engines/deepfacelab_engine.py` (TensorFlow required checks + clear ImportError messages)
    - `app/core/engines/dependency_validator.py` (TensorFlow marked required for DeepFaceLab)
  - **Repo presence**: present in repo

### UI functional gaps closed (examples)

- **Documented fix: print support**
  - **Docs**: `docs/governance/priority_handler/PRIORITY_HANDLER_VIOLATIONS_FIXED_2025-01-28.md`
  - **Code**: `src/VoiceStudio.App/Views/KeyboardShortcutsView.xaml.cs` (PrintManager / PrintDocument flow)
  - **Repo presence**: present in repo

- **Documented fix: floating panel pop-out (app/ui legacy shell)**
  - **Docs**: `docs/governance/priority_handler/PRIORITY_HANDLER_VIOLATIONS_FIXED_2025-01-28.md`
  - **Code**: `app/ui/VoiceStudio.App/Views/Controls/PanelHost.xaml.cs` (`OnPopOutClick` implemented)
  - **Repo presence**: present in repo

### Reliability / resilience

- **Documented addition: retry/circuit-breaker/health endpoints/graceful-degradation**
  - **Docs**: `docs/governance/worker1/ERROR_RECOVERY_RESILIENCE_COMPLETE_2025-01-28.md`
  - **Code**:
    - `app/core/resilience/*`
    - `backend/api/routes/health.py` (expanded health endpoints)
  - **Repo presence**: present in repo

---

## Notes on “what exists where” (avoids duplicate mapping effort)

- **If you want a definitive UI panel surface list**: use `app/core/PanelRegistry.Auto.cs` (or regenerate it via the panel scripts).
- **If you want a definitive backend API surface list**: use `docs/governance/BACKEND_ROUTE_CATALOG.json` (generated from decorators in `backend/api/routes/*.py`).
- **If you want a definitive engine list (with entry points)**: use `docs/governance/ENGINE_MANIFEST_CATALOG.json`.

