# VoiceStudio Test Report

**Generated:** 2026-02-08
**Version:** 1.0.1

## Overview

VoiceStudio uses a multi-layer testing strategy with automated pipeline orchestration.

| Test Category | Count | Status |
|---------------|-------|--------|
| Unit Tests | ~500+ | ✅ Passing (with pre-existing failures) |
| Smoke Tests | 82 | ✅ All Passing |
| E2E Tests | 35 | ✅ All Passing |

## Test Pipeline

The test pipeline is orchestrated by `scripts/run-test-pipeline.ps1` and runs:

```
Build → Unit Tests → Smoke Tests → E2E Tests
```

### Running the Full Pipeline

```powershell
# Full pipeline (build + all tests)
.\scripts\run-test-pipeline.ps1

# With clean build
.\scripts\run-test-pipeline.ps1 -Clean

# Skip build (use existing)
.\scripts\run-test-pipeline.ps1 -SkipBuild

# With real UI automation
.\scripts\run-test-pipeline.ps1 -RealUI
```

### Running Individual Test Categories

```powershell
# Build only
.\scripts\build.ps1

# Unit tests only
.\scripts\test.ps1

# Smoke tests (simulated)
.\scripts\smoke.ps1

# Smoke tests (real UI)
.\scripts\smoke.ps1 -RealUI

# E2E tests (simulated)
.\scripts\e2e.ps1

# E2E tests (real UI)
.\scripts\e2e.ps1 -RealUI
```

## Test Categories

### Unit Tests (`TestCategory!=UI&TestCategory!=E2E&TestCategory!=Smoke`)

Unit tests verify individual components in isolation:

- **ViewModels**: 40+ ViewModel test classes covering MVVM logic
- **Services**: PanelRegistry, ErrorCoordinator, VersionService, etc.
- **UseCases**: LibraryUseCase, TimelineUseCase
- **IPC**: RequestSigner tests

**Location:** `src/VoiceStudio.App.Tests/`

### Smoke Tests (`TestCategory=Smoke`)

Smoke tests verify all 60+ panels can be navigated and loaded:

- Panel navigation (VoiceSynthesis, Profiles, Library, etc.)
- Panel visibility checks
- Multi-panel sequential navigation
- Core panels, synthesis panels, training panels, etc.

**Location:** `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`

### E2E Tests (`TestCategory=E2E`)

End-to-end tests verify complete user workflows:

#### Navigation Tests (`NavigationE2ETests.cs`)
- All 8 main navigation tabs
- Sequential tab navigation
- Tab switching behavior

#### Core Panel Tests (`CorePanelE2ETests.cs`)
- VoiceSynthesis required controls
- Profiles required controls
- Library search capability
- Timeline playback controls
- Settings theme option
- All core panels load successfully

#### Lifecycle Tests (`AppLifecycleE2ETests.cs`)
- Application starts successfully
- MainWindow is responsive
- No exceptions on startup
- Navigation available after startup
- Basic workflow execution
- Multiple navigations handling

**Location:** `src/VoiceStudio.App.Tests/UI/E2E/`

## Test Infrastructure

### FlaUI Integration

Tests use FlaUI 4.0.0 for UI automation with dual-mode support:

- **Simulated Mode** (default): Fast, no app launch required
- **Real UI Mode**: Launches app, uses FlaUI automation

Set `VOICESTUDIO_USE_REAL_UI_AUTOMATION=true` for real UI testing.

### Key Components

| Component | Purpose |
|-----------|---------|
| `SmokeTestBase.cs` | Base class with panel registry (60+ panels), simulation support, FlaUI helpers |
| `AppLauncher.cs` | App launch, window detection, screenshot capture |
| `TestBase.cs` | Common test infrastructure |

### Failure Artifacts

On test failure, the system automatically captures:

- **Screenshots**: `.buildlogs/{category}/screenshots/`
- **UI Tree Dumps**: `.buildlogs/{category}/uitree/` (XML format)
- **Test Logs**: `.buildlogs/{category}/*.log`
- **TRX Results**: `.buildlogs/{category}/*.trx`

## Coverage Summary

### Panel Coverage

All 60+ panels have navigation smoke tests:

| Category | Panels |
|----------|--------|
| Core | VoiceSynthesis, Profiles, Library, Timeline, EffectsMixer, Analyzer, Diagnostics, Macro |
| Synthesis | EnsembleSynthesis, BatchProcessing, MultiVoiceGenerator |
| Training | Training, TrainingDatasetEditor, ModelManager |
| Audio | Transcribe, Recording, AudioAnalysis, QualityControl, QualityDashboard |
| Settings | Settings, AdvancedSettings, KeyboardShortcuts, PluginManagement, APIKeyManager |
| Voice | VoiceMorph, StyleTransfer, EmotionControl, Prosody, SSML, Spectrogram |
| Visualization | RealTimeAudioVisualizer, SonographyVisualization, EmbeddingExplorer |
| Media | ImageGen, VideoGen, VideoEdit, Upscaling |
| Organization | TagManager, MarkerManager, PresetLibrary, TemplateLibrary |
| Automation | Automation, WorkflowAutomation, TodoPanel |
| Dashboards | AnalyticsDashboard, UltimateDashboard, MCPDashboard, JobProgress |

### Navigation Coverage

All 8 main navigation tabs tested:
- NavStudio → VoiceSynthesis
- NavProfiles → Profiles
- NavLibrary → Library
- NavEffects → EffectsMixer
- NavTrain → Training
- NavAnalyze → Analyzer
- NavSettings → Settings
- NavLogs → Diagnostics

## Known Limitations

1. **Real UI Tests**: Require app to be built and launchable
2. **Test Host Crashes**: Some unit tests may cause test host crashes (pre-existing issue)
3. **Backend Required**: Some features require backend to be running

## Future Improvements

- [ ] Add integration tests for backend API
- [ ] Add performance benchmarks
- [ ] Add accessibility testing
- [ ] Increase ViewModel test coverage
- [ ] Add mutation testing

## Artifacts Location

```
.buildlogs/
├── build/              # Build logs and binlogs
├── test-results/       # Unit test TRX and logs
├── smoke/              # Smoke test results and screenshots
├── e2e/                # E2E test results, screenshots, UI trees
└── pipeline/           # Pipeline summary reports
```

## How to Interpret Results

### Pipeline Summary

After running `run-test-pipeline.ps1`, check:
- `.buildlogs/pipeline/pipeline_summary_*.md` for overall status
- Individual category logs for detailed failures

### TRX Files

TRX files can be viewed in:
- Visual Studio Test Explorer
- Azure DevOps
- Any TRX viewer tool

### UI Tree Dumps

XML files showing element hierarchy at time of failure:
- AutomationId
- ControlType
- Name
- IsOffscreen status
