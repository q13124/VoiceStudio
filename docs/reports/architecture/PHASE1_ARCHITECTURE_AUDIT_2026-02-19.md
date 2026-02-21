# Phase 1: Architecture and Dependency Audit Report

**Date:** 2026-02-19  
**Auditor:** Lead Architect (AI-assisted)  
**Status:** Complete  

---

## Executive Summary

This report documents the Phase 1 audit of VoiceStudio's dependency injection graph, static service locator patterns, duplicate implementations, and cross-layer state coherence. A **critical port mismatch** was identified and fixed during this audit.

### Key Findings

| Category | Finding | Severity | Status |
|----------|---------|----------|--------|
| Port Mismatch | Frontend defaulted to 8001, backend uses 8000 | **CRITICAL** | **FIXED** |
| Static Service Locator | 56 static Get*() methods with 67+ callers | HIGH | Document for migration |
| Duplicate AppStateStore | Two implementations in different namespaces | MEDIUM | DI resolves correctly |
| Duplicate DragDropService | Two implementations with different purposes | MEDIUM | DI resolves correctly |
| Direct HttpClient | 10 files with `new HttpClient()` instantiation | HIGH | Document for migration |

---

## 1. Critical Fix: Port Mismatch

### Issue

The backend starts on port **8000** (`scripts/start_backend.ps1` line 69: `uvicorn backend.api.main:app --port 8000`), but the frontend was configured to default to port **8001**.

### Location

`src/VoiceStudio.App/Services/AppServices.cs`, line 48:
```csharp
// BEFORE (incorrect)
var apiPort = Environment.GetEnvironmentVariable("VOICESTUDIO_API_PORT") ?? "8001";

// AFTER (fixed)
var apiPort = Environment.GetEnvironmentVariable("VOICESTUDIO_API_PORT") ?? "8000";
```

### Impact

This mismatch caused frontend-backend communication failures unless the environment variable was explicitly set. **Fixed in this audit.**

---

## 2. DI Registration Audit

### 2.1 Service Registrations (58 total)

All services are registered as **Singleton**. No `AddTransient` or `AddScoped` registrations exist.

| Service Interface | Implementation | Notes |
|-------------------|----------------|-------|
| ICorrelationIdProvider | CorrelationIdProvider | GAP-I12 cross-layer tracing |
| IBackendClient | BackendClient | Configured with BackendClientConfig |
| IWebSocketService | WebSocketService | Real-time streaming |
| IWebSocketClientFactory | WebSocketClientFactory | Factory pattern |
| IProfilesUseCase | ProfilesUseCase | Use case layer |
| IViewModelContext | ViewModelContext (factory) | Dispatcher handling |
| IDialogService | DialogService (factory) | Requires MainWindow |
| ISettingsService | SettingsService | |
| IUpdateService | UpdateService | |
| IPanelRegistry | PanelRegistry | Panel management |
| PanelStateService | PanelStateService | Concrete type registered |
| INavigationService | NavigationService | |
| IErrorDialogService | ErrorDialogService | |
| IErrorLoggingService | ErrorLoggingService | GAP-I12 correlation |
| IAuditLoggingService | AuditLoggingService | |
| IHelpOverlayService | HelpOverlayService | |
| IAudioPlayerService | AudioPlayerService | |
| OperationQueueService | (concrete) | |
| StatePersistenceService | (concrete) | |
| StateCacheService | (concrete) | |
| GracefulDegradationService | (concrete) | |
| PluginManager | (concrete) | |
| IPluginBridgeService | PluginBridgeService | Phase 1 plugin sync |
| RealTimeQualityService | (concrete) | |
| MultiSelectService | (concrete) | |
| DragDropVisualFeedbackService | (concrete) | |
| ContextMenuService | (concrete) | |
| UndoRedoService | (concrete) | |
| RecentProjectsService | (concrete) | |
| ToolbarConfigurationService | (concrete) | |
| StatusBarActivityService | (concrete) | |
| KeyboardShortcutService | (concrete) | |
| IUnifiedCommandRegistry | UnifiedCommandRegistry | Command pattern |
| CommandRouter | (concrete) | |
| CollaborationService | (concrete) | |
| BackendProcessManager | (concrete) | |
| IFeatureFlagsService | FeatureFlagsService | |
| IErrorPresentationService | ErrorPresentationService | |
| IAnalyticsService | AnalyticsService | |
| EngineManager | (concrete) | |
| IUnifiedThemeService | ThemeManager | Theme management |
| IEventAggregator | EventAggregator | Phase 4 cross-panel |
| IContextManager | ContextManager | Panel Architecture Phase 2 |
| ILayoutService | LayoutService | Phase 3 |
| IWorkspaceService | WorkspaceService | Phase 3 |
| IAppStateStore | AppStateStore | Phase 5 undo/redo |
| AppStateStore | (also concrete) | Dual registration |
| ISelectionStack | SelectionStack | Phase 5 nav stack |
| IDragDropService | DragDropService | Phase 4 |
| ICapabilityService | CapabilityService | Phase 7 |
| IJobService | JobService | Job tracking |
| ISelectionBroadcastService | SelectionBroadcastService | Phase D |
| ISynchronizedScrollService | SynchronizedScrollService | Phase D |
| IEventReplayService | EventReplayService | Phase D |
| IWorkflowCoordinatorService | WorkflowCoordinatorService | Workflow |
| ITelemetryService | TelemetryServiceStub | Local-first stub |
| IProjectRepository | JsonProjectRepository | Local-first storage |
| ISecretsService | DevVaultSecretsService | |
| ModuleLoader | (concrete) | |
| IErrorCoordinator | ErrorCoordinator | |
| IViewModelFactory | ViewModelFactory | Requires IServiceProvider |
| ICommandQueueService | CommandQueueService | GAP-B12 |

### 2.2 Static Service Locator Analysis

**56 static accessor methods** in `AppServices.cs`:

- `GetService<T>()` and `GetRequiredService<T>()` (generic)
- 54 typed accessors (`GetBackendClient()`, `GetAudioPlayerService()`, etc.)
- ~27 `TryGet*()` variants for optional resolution

**67+ callers** across 16 files:

| File | Call Count |
|------|------------|
| ServiceProvider.cs | 40 |
| ProfilesView.xaml.cs | 6 |
| SettingsView.xaml.cs | 4 |
| TimelineView.xaml.cs | 4 |
| MainWindow.xaml.cs | 2 |
| PluginHealthDashboardView.xaml.cs | 2 |
| TimelineViewModel.cs | 1 |
| PanelHost.xaml.cs | 1 |
| VoiceSynthesisViewModel.cs | 1 |
| ProfilesViewModel.cs | 1 |
| PluginManagementViewModel.cs | 1 |
| GlobalSearchViewModel.cs | 1 |
| CommandPaletteViewModel.cs | 1 |
| SettingsViewModel.cs | 1 |
| NPSSurveyViewModel.cs | 1 |
| FeedbackViewModel.cs | 1 |

**Recommendation:** Migrate to constructor injection. Start with ViewModels (they should receive dependencies via factory). ServiceProvider.cs acts as a shim and can remain as a transition layer.

---

## 3. Duplicate Implementation Analysis

### 3.1 AppStateStore (Two Implementations)

| Location | Namespace | Features |
|----------|-----------|----------|
| `Services/AppStateStore.cs` | VoiceStudio.App.Services | Undo/redo stacks, max history |
| `Services/State/AppStateStore.cs` | VoiceStudio.App.Services.State | ObservableObject, simpler dispatch |

**DI Resolution:** Lines 144-145 of AppServices.cs register:
```csharp
services.AddSingleton<IAppStateStore, AppStateStore>();  // Interface registration
services.AddSingleton<AppStateStore>();                  // Concrete type registration
```

Both resolve to `VoiceStudio.App.Services.AppStateStore` (the one with undo/redo), because that's the type in the `using` statements at the top of AppServices.cs.

**Recommendation:** Consider deleting or marking as obsolete `Services/State/AppStateStore.cs` if it's unused.

### 3.2 DragDropService (Two Implementations)

| Location | Namespace | Purpose |
|----------|-----------|---------|
| `Services/DragDropService.cs` | VoiceStudio.App.Services | Cross-panel coordination with StateStore integration |
| `Features/DragDrop/DragDropService.cs` | VoiceStudio.App.Features.DragDrop | XAML-focused drag data handling |

**DI Resolution:** Line 152 registers `IDragDropService` → `Services.DragDropService`.

**Recommendation:** Rename `Features/DragDrop/DragDropService.cs` to `DragDataManager.cs` or similar to avoid confusion. It appears to be a helper class, not the primary service.

---

## 4. HttpClient Anti-Pattern Analysis

**10 files** contain `new HttpClient()` instantiations:

| File | Usage Context |
|------|---------------|
| Services/BackendClient.cs | Main backend communication |
| Services/BackendClientAdapter.cs | Adapter layer |
| Services/BackendProcessManager.cs | Process health checks |
| Services/BackendConnectionMonitor.cs | Connection monitoring |
| Services/StartupDiagnostics.cs | Startup health checks |
| Services/UpdateService.cs | Update checks |
| Services/IPC/HmacSigningHandler.cs | HMAC signing handler |
| Views/FirstRunWizard.xaml.cs | First-run checks |
| Views/Panels/HealthCheckViewModel.cs | Health dashboard |
| VoiceStudio.App.Tests/UI/SmokeTestBase.cs | Test infrastructure |

**Recommendation:** Register `IHttpClientFactory` in DI and migrate all HTTP client usage. This enables:
- Connection pooling
- DNS refresh handling
- Simplified testing via mock handlers
- Centralized timeout/retry configuration

---

## 5. Coupling Violations

### 5.1 ServiceProvider Static Shim

`Services/ServiceProvider.cs` contains 40 calls to `AppServices.Get*()` methods and 13 empty catch blocks for "graceful fallback". This creates:

- Hidden coupling to AppServices static state
- Silent failure modes
- Testing difficulties

### 5.2 ViewModel-to-Service Direct Access

Some ViewModels directly call `AppServices.Get*()` instead of receiving dependencies via constructor:

- TimelineViewModel
- VoiceSynthesisViewModel
- ProfilesViewModel
- PluginManagementViewModel
- GlobalSearchViewModel
- SettingsViewModel

---

## 6. Pre/Post Metrics

| Metric | Pre-Audit | Post-Audit |
|--------|-----------|------------|
| Port Configuration | MISMATCHED (8001 vs 8000) | **ALIGNED (8000)** |
| Singleton Registrations | 58 | 58 (documented) |
| Static Accessor Methods | 56 | 56 (migration plan documented) |
| Static Accessor Callers | 67+ | 67+ (migration plan documented) |
| Duplicate Implementations | 2 pairs | 2 pairs (documented) |
| Direct HttpClient Usage | 10 files | 10 files (migration plan documented) |

---

## 7. Recommended Migration Plan

### Phase A: Immediate (This Audit)
- [x] Fix port mismatch (DONE)
- [x] Document all DI registrations (DONE)
- [x] Document static accessor usage (DONE)

### Phase B: Short-Term (Next Sprint)
- [ ] Register `IHttpClientFactory` in DI
- [ ] Migrate BackendClient to use IHttpClientFactory
- [ ] Add unit tests for service resolution

### Phase C: Medium-Term (Roadmap)
- [ ] Migrate ViewModels to constructor injection via ViewModelFactory
- [ ] Consolidate or obsolete duplicate AppStateStore
- [ ] Rename Features/DragDrop/DragDropService to avoid confusion
- [ ] Reduce ServiceProvider.cs to minimal adapter

---

## Appendix A: State Lifecycle Mapping

### A.1 Import Workflow

```
UI Entry Point: Toolbar "Import" button / Ctrl+I
    └── CustomizableToolbar.xaml / MainWindow.xaml
        └── IUnifiedCommandRegistry.Execute("file.import")
            └── FileOperationsHandler.ImportAudioAsync()
                ├── IDialogService.ShowOpenFilesAsync() → OS File Picker
                ├── IDialogService.ShowProgressAsync() → Progress Overlay
                ├── For each file:
                │   ├── IBackendClient.ImportAudioAsync() → POST /api/audio/import
                │   │   └── Backend: AudioService → FFmpeg → Artifact DB
                │   │       └── Returns: AudioImportResult (id, waveform, metadata)
                │   └── Update Project model (project.AudioFiles.Add)
                ├── IProjectRepository.SaveAsync() → Local JSON storage
                ├── IEventAggregator.Publish(ProjectChangedEvent)
                │   └── Subscribers: TimelineViewModel, LibraryViewModel
                └── ToastNotificationService.ShowSuccess()
```

**Coupling violations:** None identified in Import workflow. Uses proper DI and EventAggregator.

### A.2 Playback Workflow

```
UI Entry Point: Timeline Play button / Spacebar
    └── TimelineView.xaml (Views/Panels/)
        └── TimelineViewModel.PlayCommand.Execute()
            ├── IAudioPlayerService.PlayAsync(filePath)
            │   └── NAudio.WaveOutEvent → System Audio
            ├── IEventAggregator.Publish(PlaybackStartedEvent)
            │   └── Subscribers: WaveformView, TransportPanel
            └── UI Update: IsPlaying = true (PropertyChanged)
```

**Coupling violation identified:**
- `VoiceSynthesisViewModel` stores `_backendBaseUrl` directly (line 38), bypassing `BackendClientConfig`

### A.3 Export Workflow

```
UI Entry Point: File → Export / Ctrl+Shift+E
    └── FileOperationsHandler.ExportAudioAsync()
        ├── IDialogService.ShowSaveFileAsync() → OS Save Dialog
        ├── IBackendClient.ExportAudioAsync() → POST /api/audio/export
        │   └── Backend: ExportService → FFmpeg → Output file
        ├── File.Copy() → Final destination
        └── ToastNotificationService.ShowSuccess()
```

### A.4 Clone (Voice Cloning) Workflow

```
UI Entry Point: Voice Synthesis Panel "Clone Voice" button
    └── VoiceSynthesisView.xaml
        └── VoiceSynthesisViewModel.CloneVoiceCommand.Execute()
            ├── IDialogService.ShowOpenFilesAsync() → Select reference audio
            ├── IBackendClient.CloneVoiceAsync() → POST /api/voice/clone
            │   └── Backend: VoiceCloneService → ML Engine (XTTS/RVC)
            │       └── Returns: VoiceProfile (id, name, embedding)
            ├── Profile added to IBackendClient.ListProfilesAsync() refresh
            ├── IEventAggregator.Publish(ProfileCreatedEvent)
            │   └── Subscribers: ProfilesViewModel, VoiceSynthesisViewModel
            └── UI Update: Profiles list refreshed
```

### A.5 Analyze Workflow

```
UI Entry Point: Analyzer Panel / Right-click → Analyze
    └── AnalyzerView.xaml
        └── AnalyzerViewModel.AnalyzeCommand.Execute()
            ├── IBackendClient.AnalyzeAudioAsync() → POST /api/audio/analyze
            │   └── Backend: AudioAnalysisService → Librosa/Spectral analysis
            │       └── Returns: AnalysisResult (pitch, energy, spectogram)
            └── UI Update: AnalysisData property (x:Bind to charts)
```

---

## Appendix B: Additional Duplicate Implementations Found

### B.1 TimelineViewModel (Two Implementations)

| Location | Namespace | Features |
|----------|-----------|----------|
| `Views/Panels/TimelineViewModel.cs` | VoiceStudio.App.Views.Panels | IPanelView, Project list, Audio player |
| `Features/Timeline/TimelineViewModel.cs` | VoiceStudio.App.Features.Timeline | IPanelStatePersistable, ITimelineGateway, Asset selection |

**Analysis:** These serve different purposes:
- `Views/Panels/` version is the primary panel ViewModel (registered in panel registry)
- `Features/Timeline/` version is an extended timeline feature module

**Recommendation:** Consolidate into single class or rename `Features/Timeline/` version to `TimelineFeatureViewModel` to avoid confusion.

---

## Appendix C: Coupling Violations Summary

| Location | Violation | Severity |
|----------|-----------|----------|
| VoiceSynthesisViewModel | Stores `_backendBaseUrl` directly | MEDIUM |
| FileOperationsHandler L46 | Uses `AppServices.TryGetEventAggregator()` fallback | LOW |
| ProfilesView.xaml.cs | 6 direct `AppServices.Get*()` calls | HIGH |
| SettingsView.xaml.cs | 4 direct `AppServices.Get*()` calls | HIGH |
| TimelineView.xaml.cs | 4 direct `AppServices.Get*()` calls | HIGH |
| ServiceProvider.cs | 40 forwarding calls (architectural shim) | DOCUMENTED |

---

**Report completed:** 2026-02-19T01:45:00Z  
**Next phase:** Phase 2 Binding Forensics
