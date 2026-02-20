# VoiceStudio Quantum+ — Complete Feature & Button Analysis

## Engineering Roadmap for Professional Software Engineers

**Project**: VoiceStudio Quantum+
**Path**: `E:\VoiceStudio`
**Stack**: WinUI 3 (C#) + Python FastAPI backend + MCP Bridge
**Architecture**: MVVM with Panel-based dockable workspace, 4-region layout (Left, Center, Right, Bottom)

---

## 1. APPLICATION SHELL & LAYOUT

### 1.1 Main Window Structure (`MainWindow.xaml`)

The application uses a 3-row Grid layout:

| Row | Height | Content |
|-----|--------|---------|
| 0 | 48px | `CustomizableToolbar` — configurable command toolbar |
| 1 | * | Workspace — 4-column panel grid + overlays |
| 2 | 26px | Status bar — processing/network/engine indicators, job progress, system metrics, clock |

The workspace is a 2-row × 4-column grid:

| Region | Grid Position | Default Panel | Purpose |
|--------|--------------|---------------|---------|
| **Nav Rail** | Col 0, RowSpan 2 | 8 ToggleButtons | Primary navigation (64px wide) |
| **Left Panel** | Row 0, Col 1 (20%) | ProfilesView | Profile/Library/Training management |
| **Center Panel** | Row 0, Col 2 (55%) | TimelineView | Main workspace, synthesis, editing |
| **Right Panel** | Row 0, Col 3 (25%) | EffectsMixerView | Effects, analysis, settings |
| **Bottom Panel** | Row 1, Col 1–3 | MacroView | Macros, mini-timeline, diagnostics |

**Overlay Systems:**
- **Global Search Overlay** — `GlobalSearchView` (Ctrl+K), full-screen semi-transparent overlay
- **Toast Notification Container** — bottom-right stacked notifications
- **Collaboration Panel** — right-aligned overlay showing collaborator cursors/presence

### 1.2 Navigation Rail Buttons (8 Buttons)

Each button is a `ToggleButton` (44×44px) with Segoe Fluent Icons, hover preview, and command router integration.

| # | Button Name | Tooltip | Icon | Click Handler | Command ID | Target Region | Default Panel |
|---|------------|---------|------|---------------|------------|---------------|---------------|
| 1 | `NavStudio` | Studio | E80F | `NavStudio_Click` | `nav.studio` | Center | TimelineView |
| 2 | `NavProfiles` | Profiles | E77B | `NavProfiles_Click` | `nav.profiles` | Left | ProfilesView |
| 3 | `NavLibrary` | Library | E8F1 | `NavLibrary_Click` | `nav.library` | Left | LibraryView |
| 4 | `NavEffects` | Effects | E9D9 | `NavEffects_Click` | `nav.effects` | Right | EffectsMixerView |
| 5 | `NavTrain` | Train | E7BE | `NavTrain_Click` | `nav.train` | Left | TrainingView |
| 6 | `NavAnalyze` | Analyze | E9D9 | `NavAnalyze_Click` | `nav.analyze` | Right | AnalyzerView |
| — | *separator* | | | | | | |
| 7 | `NavSettings` | Settings | E713 | `NavSettings_Click` | `nav.settings` | Right | SettingsView |
| 8 | `NavLogs` | Diagnostics | E7BA | `NavLogs_Click` | `nav.logs` | Bottom | DiagnosticsView |

**Hover Behavior (IDEA 20):** Each nav button triggers `NavButton_PointerEntered` → shows `PanelPreviewPopup` with title, description, icon, and bullet-point feature summary. Hides after 300ms on pointer exit.

### 1.3 Status Bar Components

| Component | Name | Content | Update Interval |
|-----------|------|---------|-----------------|
| Processing Indicator | `ProcessingIndicator` | 8×8 circle (green/yellow/red/gray) | Event-driven |
| Network Indicator | `NetworkIndicator` | 8×8 circle | Event-driven |
| Engine Indicator | `EngineIndicator` | 8×8 circle | Event-driven |
| Status Text | `StatusText` | "Ready" / "Processing (N jobs)" / "Paused" / "Error" | Event-driven |
| Job Status | `JobStatusText` | "Idle" or active job name | Event-driven |
| Job Progress | `JobProgressBar` | 200px ProgressBar | Event-driven |
| CPU | `CpuText` | "CPU N%" | 2 seconds |
| GPU | `GpuText` | "GPU N%" | 2 seconds (async from backend telemetry) |
| RAM | `RamText` | "RAM N%" | 2 seconds |
| Sample Rate | `SampleRateText` | "48 kHz" | Static |
| Latency | `LatencyText` | "Nms" | 2 seconds (backend ping) |
| Collaborators | `CollaboratorsToggleButton` | Toggle button | On click |
| Clock | `ClockText` | "HH:mm" | 1 minute |

---

## 2. MENU SYSTEM (8 Top-Level Menus)

### 2.1 File Menu
- New Project (Ctrl+N) — `file.new`
- Open Project (Ctrl+O) — `file.open`
- Save Project (Ctrl+S) — `file.save`
- Save As... (Ctrl+Shift+S) — `file.saveAs`
- Import Audio... (Ctrl+I) — `file.import` (supports .wav, .mp3, .flac, .ogg, .m4a, .aac, .wma)
- Export Audio... (Ctrl+E) — `file.export`
- Close Project (Ctrl+W) — `file.close`
- Recent Projects (submenu with pin/unpin/clear)
- Exit

### 2.2 Edit Menu
- Undo (Ctrl+Z)
- Redo (Ctrl+Y)

### 2.3 View Menu
- Studio (Ctrl+1), Library (Ctrl+2), Profiles (Ctrl+3), Effects (Ctrl+4), Settings (Ctrl+,)
- Go Back (Alt+Left), Go Forward (Alt+Right)
- Toggle Mini Timeline / Show Macro View
- Global Search (Ctrl+K)

### 2.4 Modules Menu (9 Submenus, 65+ Items)

**Voice (13 items):** Voice Synthesis, Voice Cloning Wizard, Quick Clone, Voice Morph, Voice Blending, Style Transfer, Multi-Voice Generator, Ensemble Synthesis, Real-Time Converter, Emotion Control, Emotion Style, Multilingual

**Audio (6 items):** Transcribe, Recording, Effects Mixer, Spatial Audio, AI Mixing & Mastering, Audio Analysis

**Analysis (10 items):** Analyzer, Spectrogram, Real-Time Visualizer, Sonography, Embedding Explorer, Quality Dashboard, Quality Benchmark, Quality Optimizer, A/B Testing, Profile Comparison

**Media (6 items):** Image Generation, Video Generation, Deepfake Creator, Upscaling, Image Search, Video Editor

**Training (4 items):** Training, Dataset Editor, Model Manager, Dataset QA

**Editing (8 items):** Timeline, Text/Speech Editor, Script Editor, Scene Builder, SSML Controls, Prosody, Pronunciation Lexicon

**Automation (4 items):** Macros, Workflow Designer, Batch Processing, Automation

**Management (8 items):** Profiles, Library, Presets, Templates, Tags, Markers, Backup & Restore, Plugins

**System (9 items):** Settings, Advanced Settings, API Keys, GPU Status, Diagnostics, Health Check, Job Progress, MCP Dashboard, Help

### 2.5 Playback Menu
- Play/Pause (Space) — `playback.toggle`
- Stop — `playback.stop`
- Record (R) — `playback.record`
- Rewind (Home), Fast Forward (End), Step Back (Left), Step Forward (Right)

### 2.6 Tools Menu
- Customize Toolbar...
- Check for Updates...
- Keyboard Shortcuts

### 2.7 AI Menu
- AI Mixing & Mastering
- Ensemble Synthesis

### 2.8 Help Menu
- Documentation Folder
- About VoiceStudio

---

## 3. COMPLETE PANEL INVENTORY (100+ Panels)

### 3.1 Core Synthesis Panels

| Panel ID | View Class | ViewModel | Default Region | Description |
|----------|-----------|-----------|----------------|-------------|
| VoiceSynthesis | VoiceSynthesisView | VoiceSynthesisViewModel | Center | Primary TTS synthesis with engine selection |
| EnsembleSynthesis | EnsembleSynthesisView | EnsembleSynthesisViewModel | Center | Multi-engine ensemble synthesis |
| BatchProcessing | BatchProcessingView | BatchProcessingViewModel | Center | Bulk TTS processing queue |
| TextSpeechEditor | TextSpeechEditorView | TextSpeechEditorViewModel | Center | Text-based speech editing |
| MultiVoiceGenerator | MultiVoiceGeneratorView | MultiVoiceGeneratorViewModel | Center | Multi-character dialogue generation |
| RealTimeVoiceConverter | RealTimeVoiceConverterView | RealTimeVoiceConverterViewModel | Center | Live voice conversion |

### 3.2 Voice Cloning & Morphing Panels

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| VoiceQuickClone | VoiceQuickCloneView | Center | Quick 1-click voice cloning |
| VoiceCloningWizard | VoiceCloningWizardView | Center | Guided multi-step cloning wizard |
| VoiceMorph | VoiceMorphView | Center | Voice transformation/morphing |
| VoiceMorphingBlending | VoiceMorphingBlendingView | Center | Multi-voice blending/interpolation |
| VoiceStyleTransfer | VoiceStyleTransferView | Center | Style transfer between voices |
| StyleTransfer | StyleTransferView | Center | General audio style transfer |

### 3.3 Emotion & Prosody Controls

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| EmotionControl | EmotionControlView | Right | Basic emotion parameter control |
| EmotionStyleControl | EmotionStyleControlView | Right | Advanced emotion/style presets |
| EmotionStylePresetEditor | EmotionStylePresetEditorView | Right | Custom emotion preset editor |
| Prosody | ProsodyView | Right | Pitch, rate, volume prosody control |
| SSMLControl | SSMLControlView | Right | SSML markup editor |
| PronunciationLexicon | PronunciationLexiconView | Right | Custom pronunciation dictionary |
| MultilingualSupport | MultilingualSupportView | Right | Language and dialect settings |

### 3.4 Audio Processing & Recording

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Recording | RecordingView | Center | Audio recording interface |
| Transcribe | TranscribeView | Center | Speech-to-text transcription |
| AudioAnalysis | AudioAnalysisView | Center | Detailed audio analysis |
| EffectsMixer | EffectsMixerView | Right | Audio effects chain and mixer |
| SpatialAudio | SpatialAudioView | Center | 3D/spatial audio positioning |
| SpatialStage | SpatialStageView | Center | Visual spatial stage layout |
| AIMixingMastering | AIMixingMasteringView | Center | AI-powered mixing/mastering |
| MixAssistant | MixAssistantView | Right | AI mix recommendations |

### 3.5 Visualization & Analysis

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Analyzer | AnalyzerView | Right | Waveform + spectrum analyzer |
| Spectrogram | SpectrogramView | Center | Full spectrogram visualization |
| RealTimeAudioVisualizer | RealTimeAudioVisualizerView | Center | Live audio visualization |
| SonographyVisualization | SonographyVisualizationView | Center | Sonography display |
| EmbeddingExplorer | EmbeddingExplorerView | Center | Voice embedding space explorer |
| AdvancedRealTimeVisualization | AdvancedRealTimeVisualizationView | Center | Advanced real-time viz |

### 3.6 Quality & Benchmarking

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| QualityControl | QualityControlView | Right | Quality metrics display |
| QualityDashboard | QualityDashboardView | Center | Comprehensive quality overview |
| QualityBenchmark | QualityBenchmarkView | Center | A/B quality benchmarking |
| QualityOptimizationWizard | QualityOptimizationWizardView | Center | Guided quality improvement |
| ABTesting | ABTestingView | Center | A/B comparison testing |
| ProfileComparison | ProfileComparisonView | Center | Side-by-side profile comparison |
| ProfileHealthDashboard | ProfileHealthDashboardView | Center | Profile quality health metrics |

### 3.7 Training & Dataset

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Training | TrainingView | Left | Voice model training interface |
| TrainingDatasetEditor | TrainingDatasetEditorView | Center | Dataset annotation/editing |
| ModelManager | ModelManagerView | Center | Model lifecycle management |
| DatasetQA | DatasetQAView | Center | Dataset quality assurance |
| TrainingQualityVisualization | TrainingQualityVisualizationView | Center | Training metrics visualization |

### 3.8 Media Generation

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| ImageGen | ImageGenView | Center | AI image generation |
| VideoGen | VideoGenView | Center | AI video generation |
| DeepfakeCreator | DeepfakeCreatorView | Center | Face/voice deepfake tools |
| Upscaling | UpscalingView | Center | Image/video upscaling |
| ImageSearch | ImageSearchView | Left | Image search browser |
| VideoEdit | VideoEditView | Center | Video editing tools |
| ImageVideoEnhancementPipeline | ImageVideoEnhancementPipelineView | Center | Enhancement pipeline |

### 3.9 Editing & Scripting

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Timeline | TimelineView | Center | Main project timeline/DAW |
| MiniTimeline | MiniTimelineView | Bottom | Compact timeline overview |
| ScriptEditor | ScriptEditorView | Center | Script/dialogue editor |
| SceneBuilder | SceneBuilderView | Center | Visual scene composition |
| TextBasedSpeechEditor | TextBasedSpeechEditorView | Center | Text-driven speech editing |
| TextHighlighting | TextHighlightingView | Center | Karaoke-style word highlighting |
| MarkerManager | MarkerManagerView | Right | Timeline marker management |

### 3.10 Automation & Workflow

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Macro | MacroView | Center | Macro recording/playback |
| WorkflowAutomation | WorkflowAutomationView | Center | Visual workflow designer |
| Automation | AutomationView | Center | Automation curves/lanes |
| PipelineConversation | PipelineConversationView | Center | AI-guided pipeline builder |

### 3.11 Asset Management

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Profiles | ProfilesView | Left | Voice profile management |
| Library | LibraryView | Left | Asset library browser |
| PresetLibrary | PresetLibraryView | Left | Effect/voice presets |
| TemplateLibrary | TemplateLibraryView | Left | Project templates |
| TagManager | TagManagerView | Right | Tag/category management |
| TagOrganization | TagOrganizationView | Right | Tag hierarchy editor |
| VoiceBrowser | VoiceBrowserView | Left | Voice browser/marketplace |

### 3.12 Settings & Configuration

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Settings | SettingsView | Right | Main settings panel |
| AdvancedSettings | AdvancedSettingsView | Right | Power-user settings |
| APIKeyManager | APIKeyManagerView | Right | API key vault |
| ThemeEditor | ThemeEditorView | Right | Custom theme builder |
| EngineParameterTuning | EngineParameterTuningView | Right | Engine parameter fine-tuning |
| EngineRecommendation | EngineRecommendationView | Right | AI engine recommendation |

### 3.13 System & Monitoring

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| Diagnostics | DiagnosticsView | Bottom | System logs and diagnostics |
| GPUStatus | GPUStatusView | Right | GPU/VRAM monitoring |
| HealthCheck | HealthCheckView | Right | System health dashboard |
| JobProgress | JobProgressView | Bottom | Active job queue/progress |
| MCPDashboard | MCPDashboardView | Center | MCP server/tool dashboard |
| SLODashboard | SLODashboardView | Center | Service level objectives |
| AudioMonitoringDashboard | AudioMonitoringDashboardView | Center | Audio I/O monitoring |
| AnalyticsDashboard | AnalyticsDashboardView | Center | Usage analytics |
| UltimateDashboard | UltimateDashboardView | Center | All-in-one dashboard |
| BackupRestore | BackupRestoreView | Center | Data backup & restore |
| TodoPanel | TodoPanelView | Right | Task/todo tracking |

### 3.14 Plugin Ecosystem

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| PluginManagement | PluginManagementView | Center | Plugin install/manage |
| PluginGallery | PluginGalleryView | Center | Plugin marketplace |
| PluginDetail | PluginDetailView | Center | Individual plugin view |
| PluginHealthDashboard | PluginHealthDashboardView | Center | Plugin health monitoring |

### 3.15 Collaboration & Communication

| Panel ID | View Class | Default Region | Description |
|----------|-----------|----------------|-------------|
| CollaborationIndicator | (Control) | Overlay | User presence indicators |
| AssistantView | AssistantView | Right | AI assistant chat |
| AIProductionAssistant | AIProductionAssistantView | Right | AI production guidance |
| AdvancedSearch | AdvancedSearchView | Center | Advanced search/filter |

---

## 4. KEYBOARD SHORTCUTS (40+ Registered)

### 4.1 File Operations
| Shortcut | Action | Command ID |
|----------|--------|------------|
| Ctrl+N | New Project | `file.new` |
| Ctrl+O | Open Project | `file.open` |
| Ctrl+S | Save Project | `file.save` |
| Ctrl+I | Import Audio | `file.import` |

### 4.2 Playback
| Shortcut | Action | Command ID |
|----------|--------|------------|
| Space | Play/Pause | `playback.play` |
| S | Stop | `playback.stop` |
| Ctrl+R | Record | `playback.record` |

### 4.3 Edit
| Shortcut | Action | Command ID |
|----------|--------|------------|
| Ctrl+Z | Undo | `edit.undo` |
| Ctrl+Y | Redo | `edit.redo` |

### 4.4 Navigation
| Shortcut | Action | Command ID |
|----------|--------|------------|
| Ctrl+P | Command Palette | `nav.commandpalette` |
| Ctrl+K | Global Search | `nav.globalsearch` |
| Ctrl+1 | Profiles (Left) | `nav.panel.1` |
| Ctrl+2 | Library (Left) | `nav.panel.2` |
| Ctrl+3 | Training (Left) | `nav.panel.3` |
| Ctrl+4 | Timeline (Center) | `nav.panel.4` |
| Ctrl+5 | Voice Synthesis (Center) | `nav.panel.5` |
| Ctrl+6 | Text Speech Editor (Center) | `nav.panel.6` |
| Ctrl+7 | Effects Mixer (Right) | `nav.panel.7` |
| Ctrl+8 | Analyzer (Right) | `nav.panel.8` |
| Ctrl+9 | Quality Control (Right) | `nav.panel.9` |
| Ctrl+Tab | Cycle Next Panel Region | `panel.cycleNext` |
| Ctrl+Shift+Tab | Cycle Previous Panel Region | `panel.cyclePrevious` |
| Ctrl+Alt+1 | Focus Left Panel | `panel.focusLeft` |
| Ctrl+Alt+2 | Focus Center Panel | `panel.focusCenter` |
| Ctrl+Alt+3 | Focus Right Panel | `panel.focusRight` |
| Ctrl+Alt+4 | Focus Bottom Panel | `panel.focusBottom` |

### 4.5 Zoom
| Shortcut | Action |
|----------|--------|
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| Ctrl+0 | Reset Zoom |

### 4.6 Help
| Shortcut | Action |
|----------|--------|
| Shift+F1 | Keyboard Shortcuts |
| Shift+/ (?) | Keyboard Shortcuts (alt) |

---

## 5. CUSTOM CONTROLS (59 Controls)

### Audio Controls
- `WaveformControl` / `WaveformDisplay` — audio waveform rendering
- `SpectrogramControl` — spectrogram visualization
- `SpectrumAnalyzerControl` — frequency spectrum display
- `VUMeterControl` — VU level metering
- `FaderControl` / `PanFaderControl` — volume/pan faders
- `LoudnessChartControl` — LUFS loudness visualization
- `PitchContourControl` — F0 pitch contour display
- `PhaseAnalysisControl` — phase correlation analysis
- `AudioOrbsControl` — particle-based audio visualization

### Editor Controls
- `SSMLEditorControl` — SSML markup editor
- `AutomationCurveEditorControl` / `AutomationCurvesEditorControl` — automation lane editors
- `MacroNodeEditorControl` — visual node-based macro editor

### UI Infrastructure Controls
- `PanelHost` — dockable panel container with region awareness
- `PanelPreviewPopup` — hover preview for nav buttons
- `PanelQuickSwitchIndicator` — visual feedback for Ctrl+N switching
- `PanelResizeHandle` — draggable panel resize
- `PanelStack` — stacked panel container
- `PanelTemplateSelector` — DataTemplateSelector for panel types
- `CustomizableToolbar` — user-configurable command toolbar
- `CommandPalette` — Ctrl+P command palette
- `CollaborationIndicator` — multi-user presence display
- `UserCursorIndicator` — remote collaborator cursor overlay
- `ToastNotification` — notification toast component
- `DropZoneOverlay` — drag-and-drop file overlay
- `FloatingWindowHost` — detachable floating window
- `NavIconButton` — reusable nav rail icon button with hover state

### Data Display Controls
- `RadarChartControl` — multi-axis radar chart
- `MatplotlibControl` / `PlotlyControl` — embedded Python chart renderers
- `TrainingProgressChart` — training epoch visualization
- `QualityBadgeControl` — quality score badge
- `BatchQueueTimelineControl` / `BatchQueueVisualControl` — batch job visualization
- `EnsembleTimelineControl` — ensemble synthesis timeline
- `AnalyticsChartControl` — analytics chart renderer
- `VoiceTimelineBlock` — timeline voice clip block (code-only)

### Dynamic/Schema Controls
- `DynamicParameterPanel` — schema-driven dynamic parameter form
- `SchemaToControlMapper` — JSON schema → WinUI control mapper
- `VirtualizedListHelper` — virtualization helper for large lists

### Plugin Controls
- `PluginCard` — plugin gallery card display

### UX Controls
- `LoadingButton` — button with spinner state
- `LoadingOverlay` — full-panel loading spinner
- `SkeletonScreen` — content placeholder animation
- `EmptyState` — empty state illustration
- `ErrorDialog` / `ErrorMessage` — error display
- `HelpOverlay` — contextual help overlay
- `OnboardingHints` — first-run onboarding tooltips
- `UndoRedoIndicator` — undo/redo stack indicator
- `VSQButton` / `VSQCard` / `VSQBadge` / `VSQFormField` / `VSQProgressIndicator` — design system components

---

## 6. BACKEND API (141 Route Files)

The Python FastAPI backend provides 141 route modules across these categories:

**Voice & Speech:** voice.py, voice_cloning_wizard.py, voice_morph.py, voice_browser.py, voice_effects.py, voice_speech.py, instant_cloning.py, rvc.py, multi_voice_generator.py, ensemble.py, realtime_converter.py, emotion.py, emotion_style.py, prosody.py, ssml.py, style_transfer.py, multilingual.py, articulation.py, formant.py, granular.py, dubbing.py, multi_speaker_dubbing.py, lexicon.py, translation.py

**Audio Processing:** audio.py, audio_analysis.py, audio_audit.py, effects.py, mixer.py, mix_assistant.py, mix_scene.py, spatial_audio.py, recording.py, transcribe.py, nr.py (noise reduction), spectral.py, waveform.py, spectrogram.py, advanced_spectrogram.py, sonography.py, realtime_visualizer.py, text_highlighting.py, text_speech_editor.py

**Training & Models:** training.py, training_audit.py, dataset.py, dataset_editor.py, models.py, model_inspect.py, embedding_explorer.py, eval_abx.py, reward.py, ml_optimization.py

**Media:** image_gen.py, video_gen.py, video_edit.py, video_enhance.py, image_search.py, img_sampler.py, deepfake_creator.py, upscaling.py, lip_sync.py, pdf.py

**Quality:** quality.py, quality_pipelines.py, ai_enhancement.py

**Project & Management:** projects.py, timeline.py, tracks.py, library.py, profiles.py, presets.py, templates.py, tags.py, markers.py, script_editor.py, scenes.py, search.py, backup.py

**Automation:** macros.py, workflows.py, automation.py, batch.py, pipeline.py, jobs.py

**AI & Assistants:** assistant.py, assistant_run.py, ai_production_assistant.py

**System:** health.py, diagnostics.py, engine.py, engines.py, engine_audit.py, gpu_status.py, telemetry.py, monitoring.py, analytics.py, metrics.py, slo.py, settings.py, advanced_settings.py, realtime_settings.py, api_key_manager.py, shortcuts.py, feedback.py, help.py, plugins.py, plugin_gallery.py, plugin_health.py, mcp_dashboard.py, todo_panel.py, ultimate_dashboard.py, experiments.py, integrations.py, docs.py, adr.py, version.py

**Infrastructure:** auth.py, rate_limiting.py, security/, middleware/, gateway_aliases.py, huggingface_fix.py, tracing.py, errors.py, repair.py, safety.py

---

## 7. ENGINEERING NEXT STEPS

### PRIORITY 1 — CRITICAL (Do First)

#### 7.1 Root Directory Cleanup (Immediate)
**Problem:** 700+ `xaml_compiler_raw_*.log` files polluting the project root.
**Action:**
- Add `xaml_compiler_raw_*.log` to `.gitignore` (verify already present)
- Create `scripts/cleanup-root.ps1` to move/delete these files
- Move all build artifacts (`build_*.txt`, `collect_*.txt`, `*_stderr.txt`, `*_stdout.txt`) to `.buildlogs/`
- Expected outcome: Clean root with < 30 files

#### 7.2 Fix Panel Registry Duplication
**Problem:** Two panel registries exist — a `_legacyPanelRegistry` dictionary in MainWindow.xaml.cs AND a unified `IPanelRegistry` from DI. The `CreatePanelFromRegistry()` method falls back to legacy. **47 panels remain in legacy only** (see Section 13.4).
**Action:**
- Migrate all 47 legacy entries to `CorePanelRegistrationService` in 5 batches (see Section 18)
- Normalize Advanced panel IDs from kebab-case to PascalCase
- Remove `_legacyPanelRegistry` dictionary entirely
- Add unit test: all panel IDs resolve from unified registry

#### 7.3 Consolidate View/ViewModel Wiring
**Problem:** Many View `.xaml.cs` files likely manually instantiate ViewModels instead of using DI.
**Action:**
- Audit all 100+ Views for `DataContext` / ViewModel assignment patterns
- Ensure all ViewModels are registered in DI container
- Use `ViewModelLocator` consistently
- Verify `BaseViewModel` inheritance chain

#### 7.4 Backend Health & Startup Reliability
**Problem:** `start_backend.ps1`, `backend_startup.log`, `backend_stderr.log` files at root suggest backend startup issues.
**Action:**
- Review and stabilize `start_backend.ps1`
- Implement health check retry logic in frontend `BackendClient`
- Add backend readiness probe before enabling synthesis features
- Ensure graceful degradation when backend is offline

### PRIORITY 2 — HIGH (This Sprint)

#### 7.5 Complete Test Coverage
**Current state:** Tests exist in `tests/` (Python) and `src/VoiceStudio.App.Tests/` (C#), but coverage for 100+ panels is likely low.
**Action:**
- Run `scripts/verify.ps1` and document current pass/fail state
- Add ViewModel unit tests for all 78+ ViewModels (focus on command execution, state transitions)
- Add contract tests for all new backend route modules
- Target: 80% ViewModel coverage, 100% route contract coverage

#### 7.6 Panel State Persistence
**Problem:** `PanelStateService` exists but workspace layout restore has a `RestorePanelsFromLayout()` that falls back to defaults if layout is empty.
**Action:**
- Verify workspace layout JSON is correctly saved on window close
- Test workspace profile switching (studio ↔ training)
- Add persistence for per-panel state (scroll position, selections, expanded sections)
- Add workspace profile management UI (create, rename, delete profiles)

#### 7.7 Command Router Completion
**Problem:** `CommandRouter` exists but menu items have fallback paths for when it's null.
**Action:**
- Ensure `CommandRouter` is always available from DI
- Register all 5 command handler classes fully (see Section 12)
- Remove all `if (_commandRouter != null)` fallback branches
- Add command discoverability to Command Palette

#### 7.8 Error Handling Audit
**Problem:** Many `catch (Exception ex)` blocks use `ErrorLogger.LogWarning` with generic messages. Some empty catches exist (marked with `// ALLOWED: empty catch` comments).
**Action:**
- Audit all catch blocks for proper error recovery
- Replace generic catches with specific exception types
- Ensure all user-facing errors show toast notifications
- Add crash report aggregation to DiagnosticsView

### PRIORITY 3 — MEDIUM (Next Sprint)

#### 7.9 Backend API Route Consolidation
**Problem:** 141 route files with potential overlap (e.g., `voice.py` vs `voice_speech.py` vs `voice_effects.py`).
**Action:**
- Create route dependency graph
- Identify and merge overlapping routes
- Implement API versioning properly (v2/ directory already exists)
- Add OpenAPI schema validation for all endpoints
- Generate client SDK from OpenAPI spec

#### 7.10 Plugin System Maturation
**Problem:** Plugin infrastructure exists (PluginManagement, PluginGallery, PluginHealth panels + backend routes) but needs hardening.
**Action:**
- Review `plugins/` directory for installed plugins
- Implement plugin sandboxing per ADR decisions
- Add plugin dependency resolution
- Create plugin development SDK documentation
- Build plugin marketplace backend

#### 7.11 Real-Time Features
**Problem:** WebSocket infrastructure exists (`backend/api/ws/`) with 5 client types but real-time features need testing.
**Action:**
- Audit WebSocket connection lifecycle for all 5 clients
- Test `CollaborationIndicator` with multiple concurrent users
- Verify `RealTimeVoiceConverterView` latency and stability
- Implement reconnection logic for dropped WebSocket connections

#### 7.12 Accessibility Compliance
**Problem:** `Features/Accessibility/` directory exists, `AutomationProperties.AutomationId` is used on key controls, but full coverage is unknown.
**Action:**
- Audit all 100+ panels for accessibility support
- Ensure all interactive controls have `AutomationProperties.Name`
- Test keyboard-only navigation through all panels
- Add screen reader support verification
- Reference `docs/developer/AUTOMATION_ID_REGISTRY.md`

### PRIORITY 4 — LOW (Backlog)

#### 7.13 Performance Optimization
- Profile startup time (PerformanceProfiler is already instrumented)
- Implement lazy loading for all non-default panels
- Add virtualization to large lists (Library, Profiles)
- Optimize backend response caching per `response_cache.py`
- Benchmark engine latency for each TTS engine

#### 7.14 Documentation Sync
- Sync `docs/user/USER_MANUAL.md` with actual current feature set
- Generate API documentation from OpenAPI spec
- Create panel-by-panel user guides
- Update architecture diagrams in `docs/design/`

#### 7.15 CI/CD Pipeline
- Automate `scripts/verify.ps1` in GitHub Actions
- Add automated UI smoke tests per `RunGateCUiSmokeNavigationAsync`
- Implement staged deployment (dev → staging → production)
- Add binary signing for installer

#### 7.16 Temp File / Log Management
- `CleanupTempAudioFiles()` exists but only runs on close
- Add periodic cleanup during long sessions
- Implement log rotation for `backend_*.log` files
- Add disk space monitoring alert

#### 7.17 Deepfake & Safety
- Review `DeepfakeCreatorView` for ethical guardrails
- Implement consent verification workflow
- Add watermarking to generated content
- Review `backend/api/routes/safety.py` implementation

---

## 8. FEATURE SUBSYSTEMS SUMMARY

| Subsystem | Directory | Purpose |
|-----------|-----------|---------|
| Accessibility | `Features/Accessibility/` | Screen reader, keyboard nav, high contrast |
| Animations | `Features/Animations/` | Panel transitions, micro-animations |
| DragDrop | `Features/DragDrop/` | File drag-drop import, panel rearrangement |
| Notifications | `Features/Notifications/` | Toast notifications, alert system |
| Panels | `Features/Panels/` | Panel registry, lifecycle, docking |
| PowerUser | `Features/PowerUser/` | Macros, command palette, shortcuts |
| Search | `Features/Search/` | Global search, advanced filtering |
| Settings | `Features/Settings/` | Preferences persistence, config management |
| StatusBar | `Features/StatusBar/` | Activity indicators, metrics display |
| Synthesis | `Features/Synthesis/` | TTS engine integration, voice generation |
| Theming | `Features/Theming/` | Dark/light themes, custom theme editor |
| Timeline | `Features/Timeline/` | DAW-style timeline, track management |
| Toolbar | `Features/Toolbar/` | Customizable toolbar, toolbar profiles |
| UndoRedo | `Features/UndoRedo/` | Undo/redo stack, operation history |
| VoiceProfile | `Features/VoiceProfile/` | Profile CRUD, quality scoring |
| Waveform | `Features/Waveform/` | Waveform rendering, peak calculation |
| Workspaces | `Features/Workspaces/` | Workspace layout profiles |

---

## 9. ENGINE INTEGRATION

**Supported Engines (from README):**

| Engine | Status | Quality | Languages |
|--------|--------|---------|-----------|
| XTTS v2 (Coqui TTS) | ✅ Integrated | High | 14 languages |
| Chatterbox TTS (Resemble AI) | ✅ Integrated ⭐ Recommended | State-of-the-art | 23 languages |
| Tortoise TTS | ✅ Integrated 🔥 HQ Mode | Ultra-realistic | English |
| Piper | ✅ Integrated | Fast/lightweight | Multiple |

Engine manifests are stored in `engines/` directory. Engine adapter contracts are tested via `tests/contract/test_engine_adapter_contracts.py`.

---

## 10. VERIFICATION CHECKLIST

Before any merge, engineers must run:

```powershell
# Full verification (8 stages)
.\scripts\verify.ps1

# Quick pre-commit check (~30 seconds)
.\scripts\verify.ps1 -Quick
```

**8 Verification Stages:**
1. Clean Build (C#)
2. Python Quality Checks (ruff, mypy)
3. C# Unit Tests
4. Python Unit Tests
5. Contract Tests (C# ↔ Python)
6. Backend Integration Tests
7. UI Smoke Tests
8. Gate/Ledger Validation

**Rule:** No green = no merge (per `docs/governance/CHANGE_CONTROL_RULES.md`)

---

## 11. DIALOGS, WIZARDS & OVERLAY VIEWS

These are standalone windows/overlays not part of the dockable panel system.

### 11.1 Dialogs

| Dialog | File | Purpose | Trigger |
|--------|------|---------|---------|
| `AgentApprovalDialog` | AgentApprovalDialog.xaml | Approve/reject AI agent actions before execution | MCP agent tool calls |
| `PluginPermissionDialog` | Dialogs/PluginPermissionDialog.xaml | Grant/deny plugin permissions at install | Plugin installation |
| `TelemetryConsentDialog` | Dialogs/TelemetryConsentDialog.xaml | GDPR/privacy telemetry opt-in/out | First run or settings |
| `ToolbarCustomizationDialog` | Dialogs/ToolbarCustomizationDialog.xaml | Drag-drop toolbar button arrangement | Tools → Customize Toolbar |
| `FeedbackDialog` | FeedbackDialog.xaml | User feedback submission form | Help menu or NPS flow |
| `ErrorDialog` | Controls/ErrorDialog.xaml | Structured error display with copy/report | Error events |
| `UpdateDialog` | UpdateDialog.xaml | Software update download/install prompt | Tools → Check for Updates |

### 11.2 Wizards & First-Run

| View | File | Purpose | Trigger |
|------|------|---------|---------|
| `FirstRunWizard` | FirstRunWizard.xaml | Guided onboarding: engine selection, audio device, theme, workspace layout | First launch detection |
| `NPSSurvey` | NPSSurvey.xaml | Net Promoter Score survey popup (0–10 rating + text) | Periodic prompt (configurable interval) |
| `WelcomeView` | WelcomeView.xaml | Welcome/landing screen with recent projects, quick actions | App launch (if no project auto-loaded) |
| `VoiceCloningWizardView` | Panels/VoiceCloningWizardView.xaml | Multi-step guided voice cloning: upload → analyze → train → test | Modules → Voice → Voice Cloning Wizard |
| `QualityOptimizationWizardView` | Panels/QualityOptimizationWizardView.xaml | Guided quality improvement: diagnose → suggest → apply → verify | Modules → Analysis → Quality Optimizer |

### 11.3 Overlay Views

| View | File | Purpose | Shortcut |
|------|------|---------|----------|
| `GlobalSearchView` | GlobalSearchView.xaml | Full-screen fuzzy search across panels, commands, assets, profiles | Ctrl+K |
| `CommandPaletteView` | CommandPaletteView.xaml | VS Code-style command palette with category filtering | Ctrl+P |
| `CommandPaletteWindow` | CommandPaletteWindow.xaml | Windowed variant of command palette for multi-monitor | — |
| `KeyboardShortcutsView` | KeyboardShortcutsView.xaml (root + Panels/) | Searchable shortcut reference sheet | Shift+F1 or Shift+/ |

---

## 12. COMMAND HANDLER ARCHITECTURE

### 12.1 Command System Overview

The unified command system uses `IUnifiedCommandRegistry` with `CommandDescriptor` entries. Commands are registered by 5 handler classes, bootstrapped at startup via `CommandHandlerBootstrapper.Initialize()`.

```
CommandHandlerBootstrapper.Initialize()
  ├── FileOperationsHandler       → file.* commands
  ├── ProfileOperationsHandler    → profile.* commands
  ├── PlaybackOperationsHandler   → playback.* commands
  ├── NavigationHandler           → nav.* commands
  └── SettingsOperationsHandler   → settings.* commands
```

### 12.2 FileOperationsHandler — Registered Commands

| Command ID | Title | Shortcut | Description |
|------------|-------|----------|-------------|
| `file.new` | New Project | Ctrl+N | Create empty project, prompt save if unsaved |
| `file.open` | Open Project | Ctrl+O | File picker → load `.vsqp` project file |
| `file.save` | Save Project | Ctrl+S | Save to current path, or Save As if new |
| `file.saveAs` | Save As | Ctrl+Shift+S | File picker → save with new name/location |
| `file.import` | Import Audio | Ctrl+I | Import .wav/.mp3/.flac/.ogg/.m4a/.aac/.wma |
| `file.export` | Export Audio | Ctrl+E | Export rendered audio with format selection |
| `file.close` | Close Project | Ctrl+W | Close with unsaved changes prompt |

**Dependencies:** `IProjectRepository`, `IDialogService`, `IBackendClient?`, `ToastNotificationService?`, `IEventAggregator?`

### 12.3 PlaybackOperationsHandler — Registered Commands

| Command ID | Title | Shortcut | Description |
|------------|-------|----------|-------------|
| `playback.play` | Play/Pause | Space | Toggle playback of timeline/preview |
| `playback.stop` | Stop | S | Stop and reset playhead to start |
| `playback.record` | Record | Ctrl+R | Start/stop microphone recording |
| `playback.rewind` | Rewind | Home | Jump playhead to beginning |
| `playback.fastForward` | Fast Forward | End | Jump playhead to end |
| `playback.stepBack` | Step Back | Left Arrow | Step back one frame/chunk |
| `playback.stepForward` | Step Forward | Right Arrow | Step forward one frame/chunk |

**Dependencies:** `IAudioPlayerService`, `ToastNotificationService?`

### 12.4 NavigationHandler — Registered Commands

| Command ID | Title | Description |
|------------|-------|-------------|
| `nav.studio` | Studio | Navigate to Timeline in Center |
| `nav.profiles` | Profiles | Navigate to ProfilesView in Left |
| `nav.library` | Library | Navigate to LibraryView in Left |
| `nav.effects` | Effects | Navigate to EffectsMixerView in Right |
| `nav.train` | Train | Navigate to TrainingView in Left |
| `nav.analyze` | Analyze | Navigate to AnalyzerView in Right |
| `nav.settings` | Settings | Navigate to SettingsView in Right |
| `nav.logs` | Diagnostics | Navigate to DiagnosticsView in Bottom |
| `nav.globalsearch` | Global Search | Open GlobalSearchView overlay |
| `nav.commandpalette` | Command Palette | Open CommandPaletteView overlay |
| `nav.panel.1`–`nav.panel.9` | Quick Panel Switch | Ctrl+1 through Ctrl+9 panel hotkeys |
| `panel.cycleNext` | Cycle Next | Ctrl+Tab region cycling |
| `panel.cyclePrevious` | Cycle Previous | Ctrl+Shift+Tab reverse cycling |
| `panel.focusLeft/Center/Right/Bottom` | Focus Region | Ctrl+Alt+1/2/3/4 |

**Dependencies:** `INavigationService`, `ToastNotificationService?`

### 12.5 ProfileOperationsHandler — Registered Commands

| Command ID | Title | Description |
|------------|-------|-------------|
| `profile.create` | Create Profile | Launch new voice profile wizard |
| `profile.import` | Import Profile | Import profile from file |
| `profile.export` | Export Profile | Export selected profile |
| `profile.delete` | Delete Profile | Delete with confirmation |
| `profile.duplicate` | Duplicate Profile | Clone selected profile |
| `profile.setDefault` | Set Default | Mark profile as default |

**Dependencies:** `IProfilesUseCase`, `IDialogService`, `ToastNotificationService?`

### 12.6 SettingsOperationsHandler — Registered Commands

| Command ID | Title | Description |
|------------|-------|-------------|
| `settings.open` | Open Settings | Navigate to SettingsView |
| `settings.openAdvanced` | Advanced Settings | Navigate to AdvancedSettingsView |
| `settings.reset` | Reset to Defaults | Reset all settings with confirmation |
| `settings.export` | Export Settings | Export config to JSON file |
| `settings.import` | Import Settings | Import config from JSON file |

**Dependencies:** `ISettingsService`, `IDialogService`, `ToastNotificationService?`

---

## 13. PANEL REGISTRY ARCHITECTURE

### 13.1 Dual Registration System

Two registration services populate `IPanelRegistry` at startup:

| Service | File | Panel Count | ID Style | Description |
|---------|------|-------------|----------|-------------|
| `CorePanelRegistrationService` | Services/CorePanelRegistrationService.cs | 37 panels | `PascalCase` (e.g., `VoiceSynthesis`) | Main panels migrated from legacy MainWindow dictionary |
| `AdvancedPanelRegistrationService` | Services/AdvancedPanelRegistrationService.cs | 11 panels | `kebab-case` (e.g., `text-speech-editor`) | Pro/advanced panels added later |

**⚠ ID Naming Inconsistency:** Core uses `PascalCase` IDs, Advanced uses `kebab-case`. This should be normalized.

### 13.2 Core Registry Panels (37)

VoiceSynthesis, EnsembleSynthesis, BatchProcessing, TrainingDatasetEditor, ModelManager, Training, Transcribe, Recording, AudioAnalysis, QualityControl, Timeline, Profiles, Library, EffectsMixer, Analyzer, VoiceMorph, EmotionControl, Diagnostics, Settings, Help, SSMLControl, VoiceQuickClone, QualityDashboard, QualityBenchmark, ImageGen, VideoGen, DeepfakeCreator, DatasetQA, ScriptEditor, SceneBuilder, Macro, WorkflowAutomation, AdvancedSettings, APIKeyManager, GPUStatus, TodoPanel

### 13.3 Advanced Registry Panels (11)

text-speech-editor, prosody, spatial-audio, ai-mixing-mastering, voice-style-transfer, embedding-explorer, ai-production-assistant, pronunciation-lexicon, voice-morphing-blending, plugin-gallery, theme-editor

### 13.4 Legacy Panel Registry (Still in MainWindow.xaml.cs)

The `_legacyPanelRegistry` dictionary in `MainWindow.xaml.cs` acts as fallback when `CreatePanelFromRegistry()` doesn't find a panel in the unified registry. **Panels only in legacy (not yet migrated):**

| Panel ID | View Class | Region | Status |
|----------|-----------|--------|--------|
| SpatialStage | SpatialStageView | Center | Legacy only |
| HealthCheck | HealthCheckView | Right | Legacy only |
| MiniTimeline | MiniTimelineView | Bottom | Legacy only |
| JobProgress | JobProgressView | Bottom | Legacy only |
| MCPDashboard | MCPDashboardView | Center | Legacy only |
| SLODashboard | SLODashboardView | Center | Legacy only |
| AudioMonitoringDashboard | AudioMonitoringDashboardView | Center | Legacy only |
| AnalyticsDashboard | AnalyticsDashboardView | Center | Legacy only |
| UltimateDashboard | UltimateDashboardView | Center | Legacy only |
| BackupRestore | BackupRestoreView | Center | Legacy only |
| PluginManagement | PluginManagementView | Center | Legacy only |
| PluginDetail | PluginDetailView | Center | Legacy only |
| PluginHealthDashboard | PluginHealthDashboardView | Center | Legacy only |
| ProfileComparison | ProfileComparisonView | Center | Legacy only |
| ProfileHealthDashboard | ProfileHealthDashboardView | Center | Legacy only |
| ABTesting | ABTestingView | Center | Legacy only |
| Spectrogram | SpectrogramView | Center | Legacy only |
| RealTimeAudioVisualizer | RealTimeAudioVisualizerView | Center | Legacy only |
| SonographyVisualization | SonographyVisualizationView | Center | Legacy only |
| AdvancedRealTimeVisualization | AdvancedRealTimeVisualizationView | Center | Legacy only |
| Automation | AutomationView | Center | Legacy only |
| PipelineConversation | PipelineConversationView | Center | Legacy only |
| PresetLibrary | PresetLibraryView | Left | Legacy only |
| TemplateLibrary | TemplateLibraryView | Left | Legacy only |
| TagManager | TagManagerView | Right | Legacy only |
| TagOrganization | TagOrganizationView | Right | Legacy only |
| VoiceBrowser | VoiceBrowserView | Left | Legacy only |
| MarkerManager | MarkerManagerView | Right | Legacy only |
| MixAssistant | MixAssistantView | Right | Legacy only |
| ImageSearch | ImageSearchView | Left | Legacy only |
| Upscaling | UpscalingView | Center | Legacy only |
| VideoEdit | VideoEditView | Center | Legacy only |
| ImageVideoEnhancementPipeline | ImageVideoEnhancementPipelineView | Center | Legacy only |
| MultiVoiceGenerator | MultiVoiceGeneratorView | Center | Legacy only |
| RealTimeVoiceConverter | RealTimeVoiceConverterView | Center | Legacy only |
| TextHighlighting | TextHighlightingView | Center | Legacy only |
| TextBasedSpeechEditor | TextBasedSpeechEditorView | Center | Legacy only |
| EmotionStyleControl | EmotionStyleControlView | Right | Legacy only |
| EmotionStylePresetEditor | EmotionStylePresetEditorView | Right | Legacy only |
| MultilingualSupport | MultilingualSupportView | Right | Legacy only |
| AssistantView | AssistantView | Right | Legacy only |
| AdvancedSearch | AdvancedSearchView | Center | Legacy only |
| EngineParameterTuning | EngineParameterTuningView | Right | Legacy only |
| EngineRecommendation | EngineRecommendationView | Right | Legacy only |
| TrainingQualityVisualization | TrainingQualityVisualizationView | Center | Legacy only |
| QualityOptimizationWizard | QualityOptimizationWizardView | Center | Legacy only |
| LexiconView | LexiconView | Right | Legacy only |

**⚠ Action Required:** 47 panels still in legacy registry. All must be migrated to `CorePanelRegistrationService` (see Priority 1 item 7.2 and Section 18).

---

## 14. SERVICES INFRASTRUCTURE (130+ Services)

### 14.1 Core Application Services

| Service | File | Purpose |
|---------|------|---------|
| `AppServices` | AppServices.cs | Static service locator / DI bridge for legacy code |
| `AppStateStore` | AppStateStore.cs | Global application state container |
| `ServiceProvider` | ServiceProvider.cs | DI container wrapper |
| `DeferredServiceInitializer` | DeferredServiceInitializer.cs | Lazy initialization of heavy services |
| `ModuleLoader` | ModuleLoader.cs | Module discovery and loading |
| `VersionService` | VersionService.cs | App version management |
| `StartupDiagnostics` | StartupDiagnostics.cs | Startup health validation |

### 14.2 Backend Communication

| Service | File | Purpose |
|---------|------|---------|
| `BackendClient` | BackendClient.cs | Primary HTTP client for FastAPI backend |
| `BackendClientAdapter` | BackendClientAdapter.cs | Adapter pattern for backend interface |
| `BackendConnectionMonitor` | BackendConnectionMonitor.cs | Heartbeat/health check monitoring |
| `BackendProcessManager` | BackendProcessManager.cs | Python process lifecycle (start/stop/restart) |
| `WebSocketService` | WebSocketService.cs | Base WebSocket connection management |
| `WebSocketClientFactory` | WebSocketClientFactory.cs | Factory for specialized WS clients |

### 14.3 WebSocket Real-Time Clients

| Client | File | Purpose | Endpoint |
|--------|------|---------|----------|
| `JobProgressWebSocketClient` | JobProgressWebSocketClient.cs | Live job progress streaming | `ws://.../ws/jobs` |
| `MeterWebSocketClient` | MeterWebSocketClient.cs | Real-time VU meter levels | `ws://.../ws/meter` |
| `RealtimeVoiceWebSocketClient` | RealtimeVoiceWebSocketClient.cs | Live voice conversion audio stream | `ws://.../ws/realtime-voice` |
| `PipelineStreamingWebSocketClient` | PipelineStreamingWebSocketClient.cs | AI pipeline step-by-step progress | `ws://.../ws/pipeline` |
| `StreamingAudioPlayer` | StreamingAudioPlayer.cs | Audio chunk playback for streaming TTS | Internal |

### 14.4 Navigation & Panel Services

| Service | File | Purpose |
|---------|------|---------|
| `NavigationService` | NavigationService.cs | Panel navigation with history stack |
| `NavigationBridge` | NavigationBridge.cs | Cross-module navigation adapter |
| `PanelRegistry` | PanelRegistry.cs | `IPanelRegistry` implementation |
| `PanelLoader` | PanelLoader.cs | Lazy panel instantiation |
| `PanelStateService` | PanelStateService.cs | Panel state persistence (expanded, scroll) |
| `PanelSettingsStore` | PanelSettingsStore.cs | Per-panel settings storage |
| `LayoutService` | LayoutService.cs | Workspace layout save/restore |
| `WorkspaceService` | WorkspaceService.cs | Workspace profile management |
| `WorkspaceHistoryService` | WorkspaceHistoryService.cs | Workspace navigation history |
| `WindowHostService` | WindowHostService.cs | Floating/detached window management |
| `MultiMonitorManager` | MultiMonitorManager.cs | Multi-display window positioning |

### 14.5 Command & Input Services

| Service | File | Purpose |
|---------|------|---------|
| `UnifiedCommandRegistry` | UnifiedCommandRegistry.cs | Command registration + execution + health |
| `CommandRouter` | CommandRouter.cs | Route command IDs to handlers |
| `CommandRegistry` | CommandRegistry.cs | Legacy command registry (being replaced) |
| `CommandPaletteService` | CommandPaletteService.cs | Command palette search/filtering |
| `CommandQueueService` | CommandQueueService.cs | Queued command execution |
| `CommandMutexService` | CommandMutexService.cs | Prevent concurrent conflicting commands |
| `CommandInvalidationService` | CommandInvalidationService.cs | CanExecute state invalidation |
| `SharedDelegatingCommandService` | SharedDelegatingCommandService.cs | Shared command delegate pattern |
| `KeyboardShortcutService` | KeyboardShortcutService.cs | Shortcut registration and dispatch |
| `KeyboardNavigationHelper` | KeyboardNavigationHelper.cs | Focus management and tab navigation |

### 14.6 Audio Services

| Service | File | Purpose |
|---------|------|---------|
| `AudioPlayerService` | AudioPlayerService.cs | Audio playback engine |
| `AudioPlaybackService` | AudioPlaybackService.cs | High-level playback orchestration |
| `MicrophoneRecordingService` | MicrophoneRecordingService.cs | Mic capture and recording |
| `RealTimeQualityService` | RealTimeQualityService.cs | Live quality metrics during playback |
| `ReferenceAudioQualityAnalyzer` | ReferenceAudioQualityAnalyzer.cs | Reference audio quality scoring |
| `EngineManager` | EngineManager.cs | TTS engine lifecycle and selection |
| `BatchProcessingService` | BatchProcessingService.cs | Batch synthesis job management |

### 14.7 UI & UX Services

| Service | File | Purpose |
|---------|------|---------|
| `ThemeManager` | ThemeManager.cs | Theme loading, switching, custom themes |
| `ToastNotificationService` | ToastNotificationService.cs | Toast notification queue and display |
| `ToolbarConfigurationService` | ToolbarConfigurationService.cs | Toolbar layout persistence |
| `DragDropService` | DragDropService.cs | Drag-drop coordination |
| `DragDropVisualFeedbackService` | DragDropVisualFeedbackService.cs | Visual indicators during drag |
| `VisualFeedbackService` | VisualFeedbackService.cs | Button press, panel switch animations |
| `ContextMenuService` | ContextMenuService.cs | Dynamic context menu construction |
| `HelpOverlayService` | HelpOverlayService.cs | Contextual help tooltip overlays |
| `OnboardingService` | OnboardingService.cs | First-run hints and guided tours |
| `OnboardingWizardService` | OnboardingWizardService.cs | Multi-step onboarding flow |
| `AccessibilityService` | AccessibilityService.cs | Screen reader, high contrast support |

### 14.8 Data & State Services

| Service | File | Purpose |
|---------|------|---------|
| `JsonProjectRepository` | JsonProjectRepository.cs | Project file I/O (`.vsqp` JSON format) |
| `RecentProjectsService` | RecentProjectsService.cs | MRU project list with pin/unpin |
| `SettingsService` | SettingsService.cs | User preferences persistence |
| `StateCacheService` | StateCacheService.cs | In-memory state caching |
| `StatePersistenceService` | StatePersistenceService.cs | Cross-session state persistence |
| `UndoRedoService` | UndoRedoService.cs | Undo/redo stack with action coalescing |
| `MacroRecorderService` | MacroRecorderService.cs | Record user actions as macros |
| `SelectionBroadcastService` | SelectionBroadcastService.cs | Cross-panel selection sync |
| `SynchronizedScrollService` | SynchronizedScrollService.cs | Linked scrolling between panels |
| `MultiSelectService` | MultiSelectService.cs | Multi-item selection coordination |
| `ContextManager` | ContextManager.cs | Active context tracking (what's focused) |

### 14.9 Error & Recovery Services

| Service | File | Purpose |
|---------|------|---------|
| `ErrorCoordinator` | ErrorCoordinator.cs | Centralized error routing |
| `ErrorDialogService` | ErrorDialogService.cs | Error dialog presentation |
| `ErrorLoggingService` | ErrorLoggingService.cs | Structured error logging |
| `ErrorPresentationService` | ErrorPresentationService.cs | User-friendly error messages |
| `ErrorReportingService` | ErrorReportingService.cs | Crash report generation |
| `CrashRecoveryService` | CrashRecoveryService.cs | Auto-save recovery after crash |
| `GracefulDegradationService` | GracefulDegradationService.cs | Feature disable when backend offline |
| `DiagnosticExport` | DiagnosticExport.cs | Export diagnostic bundle |

### 14.10 Security & Auth Services

| Service | File | Purpose |
|---------|------|---------|
| `AuthService` | AuthService.cs | Authentication management |
| `SecureStorage` | SecureStorage.cs | Encrypted local storage |
| `DataEncryption` | DataEncryption.cs | Data encryption utilities |
| `DevVaultSecretsService` | DevVaultSecretsService.cs | Development secrets management |
| `WindowsCredentialManagerSecretsService` | WindowsCredentialManagerSecretsService.cs | Windows Credential Manager integration |
| `DataBackupService` | DataBackupService.cs | Automated data backup |
| `AuditLoggingService` | AuditLoggingService.cs | Security audit trail logging |
| `AuditLogWatcher` | AuditLogWatcher.cs | Audit log file monitoring |

### 14.11 Analytics & Telemetry

| Service | File | Purpose |
|---------|------|---------|
| `AnalyticsService` | AnalyticsService.cs | Usage analytics collection |
| `StatusBarActivityService` | StatusBarActivityService.cs | Status bar metric updates |
| `FeatureFlagsService` | FeatureFlagsService.cs | Feature toggle management |
| `CapabilityService` | CapabilityService.cs | Backend capability detection |

### 14.12 Plugin & Collaboration Services

| Service | File | Purpose |
|---------|------|---------|
| `PluginManager` | PluginManager.cs | Plugin lifecycle management |
| `PluginBridgeService` | PluginBridgeService.cs | Plugin ↔ host communication |
| `PluginGateway` | PluginGateway.cs | Plugin API gateway |
| `PluginPermissionManager` | PluginPermissionManager.cs | Plugin permission enforcement |
| `CollaborationService` | CollaborationService.cs | Multi-user real-time collaboration |

### 14.13 Event & Messaging Infrastructure

| Service | File | Purpose |
|---------|------|---------|
| `EventAggregator` | EventAggregator.cs | Pub/sub event bus |
| `EventReplayService` | EventReplayService.cs | Event replay for debugging |
| `ThrottledEventPublisher` | ThrottledEventPublisher.cs | Rate-limited event publishing |
| Services/Messaging/ | (directory) | Message bus infrastructure |
| Services/IPC/ | (directory) | Inter-process communication (incl. `HmacSigningHandler`) |
| Services/AgentGovernance/ | (directory) | MCP agent safety governance |

### 14.14 Workflow & Job Services

| Service | File | Purpose |
|---------|------|---------|
| `JobService` | JobService.cs | Job queue management |
| `WorkflowCoordinatorService` | WorkflowCoordinatorService.cs | Multi-step workflow orchestration |
| `OperationQueueService` | OperationQueueService.cs | Sequential operation execution |

### 14.15 ViewModel Infrastructure

| Service | File | Purpose |
|---------|------|---------|
| `ViewModelFactory` | ViewModelFactory.cs | ViewModel instantiation from DI |
| `ViewModelLocator` | ViewModels/ViewModelLocator.cs | XAML-bindable ViewModel resolution |
| `ViewModelContext` | ViewModels/ViewModelContext.cs | Shared context for ViewModels |
| `BaseViewModel` | ViewModels/BaseViewModel.cs | Base class: INotifyPropertyChanged, commands, busy state |

---

## 15. BACKEND ROUTE FILES — ADDITIONAL INVENTORY

Routes found in actual `backend/api/routes/` directory but not listed in original Section 6:

| Route File | Category | Purpose |
|------------|----------|---------|
| `adr.py` | System | Architecture Decision Record API |
| `advanced_spectrogram.py` | Audio Processing | Advanced spectrogram generation |
| `ai_production_assistant.py` | AI | AI production assistant chat/guidance |
| `assistant_run.py` | AI | Long-running assistant task execution |
| `audio_audit.py` | Quality | Audio quality audit pipeline |
| `docs.py` | System | API documentation serving |
| `engine_audit.py` | System | Engine configuration audit |
| `experiments.py` | System | A/B experiment management |
| `gateway_aliases.py` | Infrastructure | Route aliasing/gateway mapping |
| `huggingface_fix.py` | Infrastructure | HuggingFace model download fixes |
| `img_sampler.py` | Media | Image sampling/selection |
| `integrations.py` | System | Third-party integration management |
| `lexicon.py` | Voice | Pronunciation lexicon CRUD |
| `metrics.py` | System | Prometheus-style metrics endpoint |
| `ml_optimization.py` | Training | ML model optimization utilities |
| `pdf.py` | Media | PDF generation from scripts |
| `realtime_settings.py` | System | Real-time processing configuration |
| `text_speech_editor.py` | Editing | Text-based speech editing API |
| `training_audit.py` | Training | Training run audit/history |
| `translation.py` | Voice | Text translation for multilingual |
| `ultimate_dashboard.py` | System | Aggregated dashboard data endpoint |
| `version.py` | System | API version information |

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `v2/` | API v2 route overrides/additions |
| `ROUTE_SECURITY_MATRIX.md` | Security classification for all routes |

---

## 16. SOURCE-VS-DOCUMENT DELTA AUDIT

### 16.1 Views With No Matching ViewModel or Incomplete Files

| View | Issue | Status |
|------|-------|--------|
| `AdvancedSpectrogramVisualizationView` | Code-behind only (.cs), no .xaml file | ⚠ Incomplete |
| `AdvancedWaveformVisualizationView` | Code-behind only (.cs), no .xaml file | ⚠ Incomplete |
| `PluginDetailView` | No ViewModel found in ViewModels/ directory | ⚠ Missing VM |
| `LexiconView` | Exists alongside `PronunciationLexiconView` — likely duplicate | ⚠ Overlap |

### 16.2 Duplicate/Overlapping Panel Concerns

| Pair | Issue |
|------|-------|
| `LexiconView` vs `PronunciationLexiconView` | Two lexicon panels — likely one is legacy |
| `TextSpeechEditorView` vs `TextBasedSpeechEditorView` | Both exist — different UX paradigms or one is old |
| `KeyboardShortcutsView` (root) vs `KeyboardShortcutsView` (Panels/) | Root is overlay, Panels/ is dockable panel |
| `StyleTransferView` vs `VoiceStyleTransferView` | General audio vs voice-specific style transfer |

### 16.3 Panel ID Normalization Needed

| Current ID (Advanced) | Suggested Normalized ID |
|----------------------|------------------------|
| `text-speech-editor` | `TextSpeechEditor` |
| `prosody` | `Prosody` |
| `spatial-audio` | `SpatialAudio` |
| `ai-mixing-mastering` | `AIMixingMastering` |
| `voice-style-transfer` | `VoiceStyleTransfer` |
| `embedding-explorer` | `EmbeddingExplorer` |
| `ai-production-assistant` | `AIProductionAssistant` |
| `pronunciation-lexicon` | `PronunciationLexicon` |
| `voice-morphing-blending` | `VoiceMorphingBlending` |
| `plugin-gallery` | `PluginGallery` |
| `theme-editor` | `ThemeEditor` |

---

## 17. TOTAL COUNTS SUMMARY

| Category | Count |
|----------|-------|
| **Panels (total unique)** | ~95 (37 core + 11 advanced + ~47 legacy) |
| **ViewModels** | 78 (in ViewModels/ dir) + ~20 co-located in Panels/ |
| **Custom Controls** | 59 |
| **Backend Route Files** | 141 |
| **Services** | 130+ |
| **Command Handlers** | 5 handler classes, ~35 registered commands |
| **Keyboard Shortcuts** | 40+ |
| **Dialogs/Wizards** | 9 |
| **WebSocket Clients** | 5 |
| **Menu Items** | 65+ (Modules menu alone) |
| **Feature Subsystems** | 17 directories |
| **Overlay Views** | 4 |

---

## 18. UPDATED ENGINEERING PRIORITY: PANEL MIGRATION BATCHES

Based on the delta audit (Section 13.4), the most impactful single task is migrating all 47 legacy-only panels to `CorePanelRegistrationService`. Recommended batch order:

**Batch 1 — High-traffic panels (do first):**
Spectrogram, RealTimeAudioVisualizer, MiniTimeline, JobProgress, PresetLibrary, MultiVoiceGenerator, RealTimeVoiceConverter, EmotionStyleControl, MarkerManager

**Batch 2 — Dashboard panels:**
HealthCheck, MCPDashboard, SLODashboard, AudioMonitoringDashboard, AnalyticsDashboard, UltimateDashboard, ProfileHealthDashboard, PluginHealthDashboard

**Batch 3 — Media & editing panels:**
Upscaling, VideoEdit, ImageSearch, ImageVideoEnhancementPipeline, TextHighlighting, TextBasedSpeechEditor, SonographyVisualization, AdvancedRealTimeVisualization, SpatialStage

**Batch 4 — Management & automation panels:**
BackupRestore, PluginManagement, PluginDetail, TemplateLibrary, TagManager, TagOrganization, VoiceBrowser, Automation, PipelineConversation, AdvancedSearch

**Batch 5 — Settings & specialized panels:**
EngineParameterTuning, EngineRecommendation, EmotionStylePresetEditor, MultilingualSupport, AssistantView, AIProductionAssistant, MixAssistant, ProfileComparison, ABTesting, QualityOptimizationWizard, TrainingQualityVisualization, LexiconView
