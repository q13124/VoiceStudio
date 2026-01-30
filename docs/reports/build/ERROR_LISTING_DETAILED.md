# VoiceStudio - Detailed Error Listing
**Generated:** December 15, 2025  
**Total Errors:** 416 | **Total Warnings:** 19

---

## Error Breakdown by Type

### CS0246 - Type or Namespace Not Found (~100 errors)

**System Collections/Threading Missing:**
- `List<>` - Not found in: EffectsMixerViewModel.cs, QualityDashboardViewModel.cs (5+ files)
- `Dictionary<,>` - Not found in: TextSpeechEditorViewModel.cs, StyleTransferViewModel.cs, QualityDashboardViewModel.cs, QualityOptimizationWizardViewModel.cs, ProfilesViewModel.cs, EffectsMixerViewModel.cs, ViewModels/ScriptEditorViewModel.cs, ProsodyViewModel.cs, MixAssistantViewModel.cs, Services/Stores/EngineStore.cs (20+ locations)
- `Task` - Not found in: EffectsMixerView.xaml.cs, LibraryView.xaml.cs, TimelineView.xaml.cs (15+ files)

**Custom Types Missing:**
- `IBackendClient` - VideoGenViewModel.cs, MiniTimelineViewModel.cs, VideoEditViewModel.cs (5 references)
- `IAudioPlayerService` - MiniTimelineViewModel.cs (2 references)
- `MultiSelectState` - TagManagerViewModel.cs, LibraryViewModel.cs, EnsembleSynthesisViewModel.cs
- `TranscriptSegmentData` - TextBasedSpeechEditorViewModel.cs (3 references)
- `EditorSession` - TextSpeechEditorViewModel.cs
- `StyleTransferJob` - StyleTransferViewModel.cs
- `SpatialConfig` - SpatialStageViewModel.cs
- `MorphConfig` - VoiceMorphViewModel.cs
- `VoiceBlend` - VoiceMorphViewModel.cs
- `QualityTrendData` - QualityDashboardViewModel.cs
- `AnalyticsSummary`, `AnalyticsCategory`, `AnalyticsMetric`, `StatisticalAnalysisResponse`, `StatisticalTestResult` - AnalyticsDashboardViewModel.cs
- `Conversation`, `Message`, `TaskSuggestion` - AssistantViewModel.cs
- `MixSuggestion` - MixAssistantViewModel.cs
- `KeyboardShortcut` - KeyboardShortcutsViewModel.cs (3 references)
- `Lexicon`, `LexiconEntry` - LexiconViewModel.cs

**XAML/WPF Types Missing:**
- `Point` - EffectsMixerView.xaml.cs, SceneBuilderView.xaml.cs, TemplateLibraryView.xaml.cs, TrainingView.xaml.cs, BatchProcessingView.xaml.cs
- `RoutedEventArgs` - ProfilesView.xaml.cs, TimelineView.xaml.cs, TrainingView.xaml.cs, QualityOptimizationWizardView.xaml.cs
- `UIElement` - EffectsMixerView.xaml.cs, LibraryView.xaml.cs, TimelineView.xaml.cs, TrainingView.xaml.cs
- `DependencyObject` - LibraryView.xaml.cs, TimelineView.xaml.cs, TrainingView.xaml.cs
- `DragStartingEventArgs` - LibraryView.xaml.cs, TimelineView.xaml.cs, TrainingView.xaml.cs
- `DragEventArgs` - LibraryView.xaml.cs, TimelineView.xaml.cs, TrainingView.xaml.cs
- `Visibility` - TimelineViewModel.cs

---

### CS0426 - Type Name Does Not Exist in Type (~80-100 errors)

**TextSegmentItem Issues (40+ references):**
- Location: TextSpeechEditorViewModel.cs (class defined as `TextSpeechEditorSegmentItem`, not `TextSegmentItem`)
- Referenced in:
  - TextSpeechEditorActions.cs (lines 14-184) - 16 references
  - TextHighlightingViewModel.cs - ObservableCollection field
  - TextSpeechEditorView.xaml.cs - Property binding
  - Views/TextSpeechEditorActions.cs - Multiple method parameters

**EditorSessionItem Issues (40+ references):**
- Location: TextSpeechEditorViewModel.cs (missing nested type)
- Referenced in:
  - TextSpeechEditorActions.cs (lines 14-184) - 16 references
  - TextSpeechEditorViewModel.cs - ObservableCollection field
  - Various view models

**TagItem Issues (30+ references):**
- Location: TagManagerViewModel.cs (missing nested type)
- Referenced in:
  - TagActions.cs (lines 14-184)
  - TagManagerView.xaml.cs
  - TagOrganizationView.xaml.cs

**MarkerItem Issues (30+ references):**
- Location: MarkerManagerViewModel.cs (missing nested type)
- Referenced in:
  - MarkerActions.cs (lines 14-184)
  - MarkerManagerView.xaml.cs

**DatasetDetailItem & DatasetAudioFileItem Issues (~50 references):**
- Location: TrainingDatasetEditorViewModel.cs (missing nested types)
- Referenced in:
  - TrainingDatasetActions.cs (lines 14-150)
  - TrainingView.xaml.cs

**Other Missing Nested Types:**
- `ScriptItem` - ScriptEditorViewModel.cs, ScriptEditorView.xaml.cs
- `LexiconEntryItem` - PronunciationLexiconViewModel.cs, LexiconViewModel.cs, LexiconActions.cs
- `EmotionPresetItem` - EmotionControlViewModel.cs, EmotionActions.cs
- `EmotionStyleStylePresetItem` - EmotionStyleControlViewModel.cs (in generated code)

---

### CS0234 - Type/Namespace Does Not Exist in Namespace (~10-15 errors)

**MixerChannel not in VoiceStudio.App.Views:**
- EffectsMixerView.xaml.cs (lines 604, 716, 763, 920, 970, 1006, 1040)

---

### CS0104 - Ambiguous Reference (~5-10 errors)

**SelectionChangedEventArgs (Ambiguous):**
- EffectsMixerView.xaml.cs (lines 352, 401)
- ProfilesView.xaml.cs (line 453)
- TagOrganizationView.xaml.cs (line 51)
- Solution: Use full namespace qualification: `Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs`

**SpectrogramFrame (Ambiguous):**
- AnalyzerViewModel.cs (line 31)
- Between: `VoiceStudio.App.Controls.SpectrogramFrame` and `VoiceStudio.Core.Models.SpectrogramFrame`

**WebSocketState (Ambiguous):**
- WebSocketService.cs (lines 16, 24, 31)
- Between: `VoiceStudio.Core.Services.WebSocketState` and `System.Net.WebSockets.WebSocketState`

---

### CS0102 - Type Already Contains Definition (~5-8 errors)

**Duplicate Fields:**
- EffectsMixerViewModel.cs (line 98): Field `selectedSubGroup` already defined by MVVM Toolkit

**Duplicate Properties:**
- EffectsMixerViewModel.cs (line 461 generated): Property `SelectedSubGroup` defined twice

---

### CS0111 - Type Already Defines Member (~15-20 errors)

**Duplicate Methods in EffectsMixerViewModel.cs:**
- Lines 987, 993, 998, 1004 (generated): Partial method `OnSelectedSubGroupChanging`, `OnSelectedSubGroupChanged` defined twice

**Duplicate Methods in ProfilesViewModel.cs:**
- Line 872: Partial method `multiple implementing declarations`

**Duplicate Methods in BatchProcessingViewModel.cs:**
- Lines 790, 803, 798: Methods `GetQualityScoreDisplay`, `GetQualityStatusDisplay`, `HasQualityMetrics` already defined

**Duplicate Methods in Views:**
- EffectsMixerView.xaml.cs (line 618): `FindChild` already defined
- WorkflowAutomationView.xaml.cs (line 307): `HelpButton_Click` already defined

---

### CS0122 - Member Inaccessible Due to Protection Level (~30-40 errors)

**Private Nested Types Accessed Externally:**
- `AIMixingMasteringViewModel.MixSuggestionData` (line 462)
- `AIMixingMasteringViewModel.MasteringAnalysisResponse` (line 489)
- `TextBasedSpeechEditorViewModel.TranscriptSegmentData` (lines 600, 618, 660)
- `TextBasedSpeechEditorViewModel.AlignSegmentData` (line 676)
- `TextBasedSpeechEditorViewModel.WordTimestampData` (line 704)
- `TextBasedSpeechEditorViewModel.AlignWordData` (line 712)
- `UltimateDashboardViewModel.DashboardSummary` (line 164)
- `UltimateDashboardViewModel.QuickStat` (line 196)
- `UltimateDashboardViewModel.RecentActivity` (line 226)
- `VoiceStyleTransferViewModel.StyleProfileResponse` (line 359)
- `VoiceStyleTransferViewModel.StyleAnalyzeResponse` (line 383)
- `VoiceCloningWizardViewModel.AudioValidationResponse` (line 615)
- `EmotionControlViewModel.EmotionPreset` (line 515)
- `PronunciationLexiconViewModel.LexiconEntryResponse` (line 684)
- `MCPDashboardViewModel.MCPDashboardSummary` (line 521)
- `MCPDashboardViewModel.MCPServer` (line 549)
- `MCPDashboardViewModel.MCPOperation` (line 583)
- `MultiVoiceGeneratorViewModel.VoiceGenerationResultData` (line 687)
- `QualityControlViewModel.CurrentAnalysis` (property type `QualityAnalysisResponse` less accessible)
- `QualityControlViewModel.CurrentOptimization` (property type `QualityOptimizationResponse` less accessible)

**Solution:** Change `private` to `public` for these nested types

---

### CS0535 - Interface Member Not Implemented (~5-10 errors)

**UpdateService Missing Interface Implementation:**
- Line 19: Doesn't implement `IUpdateService.CheckForUpdatesAsync(bool)`

**SettingsService Missing Implementations:**
- Line 15: Doesn't implement `ISettingsService.SaveSettingsAsync(SettingsData, CancellationToken)`
- Line 15: Doesn't implement `ISettingsService.ValidateSettings(SettingsData, out string?)`

---

### CS0738 - Interface Member Not Properly Implemented (~5 errors)

**SettingsService Return Type Mismatches:**
- `LoadSettingsAsync(CancellationToken)` returns `void Task` instead of `Task<SettingsData>`
- `ResetSettingsAsync(CancellationToken)` returns `void Task` instead of `Task<SettingsData>`
- `GetDefaultSettings()` returns wrong type

**WebSocketService State Property:**
- Line 16: `State` property return type mismatch

---

### CS0425 - Generic Constraint Mismatch (~2 errors)

**BackendClient Generic Methods:**
- PostAsync<TRequest, TResponse> (line 2806): Constraints don't match interface
- PutAsync<TRequest, TResponse> (line 2855): Constraints don't match interface

---

### CS0051 - Inconsistent Accessibility (~2 errors)

**RealTimeAudioVisualizerViewModel (line 202):**
- Parameter type `VisualizerFrame` is less accessible than method `VisualizerFrameItem.VisualizerFrameItem(VisualizerFrame)`

**AdvancedSpectrogramVisualizationViewModel (line 309):**
- Parameter type `ViewTypeInfo` is less accessible than method `ViewTypeItem.ViewTypeItem(ViewTypeInfo)`

---

### CS0757 - Partial Method Multiple Declaring Declarations (~4 errors)

**Generated code in EffectsMixerViewModel.g.cs (lines 987, 993, 998, 1004):**
- Partial method declarations appear multiple times

**JobProgressViewModel (line 513):**
- Partial method `multiple implementing declarations`

---

### CS1520 - Method Must Have a Return Type (~3 errors)

**TextHighlightingViewModel (line 593):**
- Method declaration missing return type

**PronunciationLexiconViewModel (line 684):**
- Method `GetLexiconEntry` missing return type; signature indicates return but declaration missing type

**LexiconViewModel (lines 655, 671):**
- Multiple method declarations missing return types

---

### MSB3073 - XAML Compiler Error (BLOCKING)

**Location:** Microsoft.UI.Xaml.Markup.Compiler.interop.targets (line 841)

```
The command "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk\1.5.240627000\buildTransitive\
tools\net6.0\..\net472\XamlCompiler.exe" exited with code 1.
```

**Status:** BLOCKING - prevents build completion
**Impact:** All dependent build steps fail

---

## Warning Summary (19 warnings)

### CS0105 - Duplicate Using Directive (~1 warning)
- AssistantView.xaml.cs (line 6): `using Windows.System` appeared previously

### CS0108 - Hidden Member Not Using `new` Keyword (~7 warnings)
- FloatingWindowHost.xaml.cs: ContentProperty, Content properties hide UserControl
- LoadingButton.xaml.cs: Multiple properties hide Control/FrameworkElement properties
- PanelHost.xaml.cs: ContentProperty, Content properties hide UserControl

### CS8625 - Cannot Convert Null to Non-Nullable Reference Type (~4 warnings)
- AutomationHelper.cs (lines 93, 106, 123): Passing null to non-nullable parameters

### CS8613 - Nullability Mismatch in Return Type (~2 warnings)
- BackendClient.cs (lines 2806, 2855): Return type nullability doesn't match interface

---

## Files with Most Errors (Top 10)

| File | Error Count |
|------|-------------|
| TextSpeechEditorActions.cs | 20+ |
| EffectsMixerView.xaml.cs | 15+ |
| TagActions.cs | 25+ |
| LibraryView.xaml.cs | 15+ |
| TimelineView.xaml.cs | 15+ |
| TrainingDatasetActions.cs | 25+ |
| QualityDashboardViewModel.cs | 12+ |
| ViewModels/EffectsMixerViewModel.cs | 10+ |
| TrainingView.xaml.cs | 12+ |
| Services/UndoableActions/* | 80+ total |

---

## Files Needing Major Fixes

**Priority 1 (High Impact):**
1. TextSpeechEditorViewModel.cs - Fix class naming
2. All ViewModels with List/Dictionary - Add System.Collections.Generic
3. XAML Code-Behind Files - Add System.Threading.Tasks, Windows.Foundation

**Priority 2 (Medium Impact):**
4. EffectsMixerViewModel.cs - Fix duplicate definitions
5. Service Interfaces - Update implementation stubs
6. LexiconViewModel, PronunciationLexiconViewModel - Fix method signatures

**Priority 3 (Lower Impact):**
7. Ambiguous References - Add full qualification
8. Nested Types - Change private to public
9. Partial Methods - Consolidate declarations

