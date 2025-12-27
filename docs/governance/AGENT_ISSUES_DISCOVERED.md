# Agent Issues Discovery Log

**Purpose:** Evidence-driven log of discovered issues, errors, bugs, and resolutions during build stabilization and codebase alignment.

**Update Protocol:** 
- Each entry includes: Issue ID, Date, Subsystem, Evidence Link, Affected Files, Resolution Reference
- Link to build logs, binlog excerpts, or compiler error codes
- Update resolution status when fixed

---

## Issue Tracking

| Issue ID | Date | Subsystem | Severity | Evidence | Affected Files | Status |
|----------|------|-----------|----------|----------|----------------|--------|
| BUILD-001 | 2025-01-28 | Build/XAML | Critical | `XamlCompiler.exe exited with code 1` from `Microsoft.UI.Xaml.Markup.Compiler.interop.targets(845,9)` | All XAML files (indirect) | 🔴 Open |
| BUILD-002 | 2025-01-28 | C# Compilation | Critical | 1591 compilation errors preventing build success | Multiple ViewModels, Views | 🔴 Open |
| API-001 | 2025-01-28 | WinUI 3 API | High | `ToastNotificationService.ShowToast` inaccessible due to protection level | TimelineView.xaml.cs, TrainingView.xaml.cs, TrainingQualityVisualizationViewModel.cs | 🔴 Open |
| API-002 | 2025-01-28 | WinUI 3 API | High | `Colors.FromArgb` not found (should be `Color.FromArgb`) | TimelineView.xaml.cs:945 | 🔴 Open |
| API-003 | 2025-01-28 | WinUI 3 API | High | `PointerPointProperties.IsControlKeyPressed` / `IsShiftKeyPressed` not found | TimelineView.xaml.cs:887-888 | 🔴 Open |
| API-004 | 2025-01-28 | Code-Behind | High | Missing `Windows.UI.*` namespace references (should be `Microsoft.UI.*` or design tokens) | BatchQueueVisualControl.xaml.cs (from audit logs) | 🔴 Open |
| API-005 | 2025-01-28 | NAudio | High | `WaveOutEvent.Resume` not found (from audit logs) | AudioPlayerService.cs, AudioPlaybackService.cs | 🔴 Open |
| API-006 | 2025-01-28 | WinRT Async | High | `IAsyncOperation<ContentDialogResult>.GetAwaiter` missing (from audit logs) | WorkflowAutomationView.xaml.cs | 🔴 Open |
| API-007 | 2025-01-28 | Keyboard | Medium | `VirtualKey.Question` not existing (from audit logs) | MainWindow.xaml.cs:874 | 🔴 Open |
| API-008 | 2025-01-28 | Menu/Tooltip | Medium | Tooltip APIs on MenuFlyoutItem not supported (from audit logs) | CustomizableToolbar.xaml.cs, ContextMenuService.cs | 🔴 Open |
| VM-001 | 2025-01-28 | ViewModel | High | Missing property: `SSMLContent` in `SSMLControlViewModel.cs` | SSMLControlViewModel.cs (multiple lines) | 🔴 Open |
| VM-002 | 2025-01-28 | ViewModel | High | Missing property: `EditedTranscript` in `TextSpeechEditorViewModel.cs` | TextSpeechEditorViewModel.cs:118,523,536 | 🔴 Open |
| VM-003 | 2025-01-28 | ViewModel | High | Missing properties: `IsLoading`, `ErrorMessage`, `StatusMessage` | AudioAnalysisViewModel.cs, MarkerManagerViewModel.cs | 🔴 Open |
| VM-004 | 2025-01-28 | ViewModel | High | Missing `CancellationToken` parameters in method calls | Multiple ViewModels | 🔴 Open |
| VM-005 | 2025-01-28 | ViewModel | High | `RelayCommand` type mismatch (custom vs CommunityToolkit) | TagManagerViewModel.cs | 🔴 Open |
| VM-006 | 2025-01-28 | ViewModel | High | Missing method overloads (methods require more parameters) | Multiple ViewModels | 🔴 Open |
| VM-007 | 2025-01-28 | ViewModel | High | Missing `using System.Collections.Generic` (List<> not found) | TextHighlightingViewModel.cs, TrainingDatasetEditorViewModel.cs | ✅ Fixed |
| VM-008 | 2025-01-28 | ViewModel | Medium | `PerformanceProfiler.StartCommand` API mismatch | PluginManagementViewModel.cs, AudioAnalysisViewModel.cs, MarkerManagerViewModel.cs | ✅ Fixed |
| VM-009 | 2025-01-28 | ViewModel | Medium | Missing `ICommand.NotifyCanExecuteChanged` support (should use IRelayCommand) | TrainingQualityVisualizationViewModelViewModel.cs:105 | ✅ Fixed |
| BUILD-003 | 2025-01-28 | Build/Restore | Critical | File lock on `Microsoft.Bcl.AsyncInterfaces.dll` preventing restore - dotnet processes may be holding locks | NuGet cache | 🔴 Open - User Action Required |
| MODEL-001 | 2025-01-28 | Data Model | High | Missing properties: `StylePreset.PresetId`, `Description`, `VoiceProfileId`, `StyleCharacteristics` | StyleTransferViewModel.cs | 🔴 Open |
| MODEL-002 | 2025-01-28 | Data Model | High | Missing property: `ProjectAudioFile.AudioId` | StyleTransferViewModel.cs, SpatialStageViewModel.cs | 🔴 Open |
| MODEL-003 | 2025-01-28 | Data Model | High | Missing properties: `AudioTrack.IsMuted`, `IsSolo` | TimelineView.xaml.cs:826,830 | 🔴 Open |
| MODEL-004 | 2025-01-28 | Data Model | Medium | Missing property: `ModelInfo.EngineId` | TextSpeechEditorViewModel.cs:629 | 🔴 Open |
| SERVICE-001 | 2025-01-28 | Service | High | Missing extension: `ServiceProvider.TryGetErrorLoggingService` | TodoPanelViewModel.cs:89 | 🔴 Open |
| INIT-001 | 2025-01-28 | Initialization | Medium | Invalid field initializer referencing non-static field | ToastNotification.xaml.cs:16 | 🔴 Open |
| CATCH-001 | 2025-01-28 | Exception Handling | Medium | Duplicate catch clauses (general catch before specific) | TrainingQualityVisualizationViewModel.cs:134,197 | 🔴 Open |
| TYPE-001 | 2025-01-28 | Type System | Medium | Type conversion issues (tuple deconstruction, operator overloads) | TimelineViewModel.cs:1388,1417, TextSpeechEditorViewModel.cs:632 | 🔴 Open |

---

## Evidence Sources

- **Build Log:** `E:/Error Audits/build_20251223_203811.log`
- **Build Binlog:** `E:/Error Audits/build_20251223_203811.binlog`
- **Root Causes:** `E:/Error Audits/Summary of Root Causes.md`
- **XAML Output:** `src/VoiceStudio.App/obj/Debug/net8.0-windows10.0.19041.0/output.json`

---

## Resolution Status Legend

- 🔴 Open - Issue identified, not yet fixed
- 🟡 In Progress - Currently being addressed
- 🟢 Resolved - Fixed and verified

---

**Last Updated:** 2025-01-28  
**Total Issues:** 27  
**Critical:** 14  
**High:** 11  
**Medium:** 2

