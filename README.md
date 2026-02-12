# VoiceStudio

Professional voice cloning and audio production software built with WinUI 3, Python/Node backend, and MCP integration.

**🎙️ Quality Focus:** State-of-the-art voice cloning with comprehensive quality metrics. Professional DAW-grade studio for voice synthesis, cloning, and audio production.

**🚀 Migration Ready:** All systems ready for migration from C:\VoiceStudio → E:\VoiceStudio. See [MIGRATION_STATUS.md](MIGRATION_STATUS.md) and [docs/governance/SYSTEM_READY_SUMMARY.md](docs/governance/SYSTEM_READY_SUMMARY.md).

## Architecture

```
[WinUI 3 App (C#)]
      |
      |  JSON over HTTP/WebSocket
      v
[Backend API (Python FastAPI)]
      |
      |  internal calls
      v
[Engine Layer (EngineProtocol)]
      |
      +---> [XTTS] [Chatterbox] [Tortoise] [Piper] [etc.]
      |
      v
[MCP Bridge Layer] ---> [PDF Unlock (implemented)]
                   ---> [Design Tokens, AI Engines (future)]
```

> **Note**: Full MCP integration for design tokens and AI engines is planned for future releases.
> Currently, the MCP bridge supports PDF unlocking only. See [FUTURE_WORK.md](docs/governance/FUTURE_WORK.md).

## Project Structure

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/      # WinUI 3 frontend
│   └── VoiceStudio.Core/     # Shared core library
├── backend/                   # Python FastAPI backend
│   ├── api/                  # FastAPI routes
│   └── mcp_bridge/           # MCP integration
├── app/
│   └── core/                 # Engine system
├── engines/                   # Engine manifests
├── docs/
│   ├── user/                 # User documentation
│   ├── api/                  # API documentation
│   ├── developer/            # Developer documentation
│   └── design/               # Architecture docs
└── installer/                 # Windows installer
```

## Documentation

Complete documentation is available in the `docs/` directory:

- **[User Documentation](docs/user/)** - Getting started, user manual, tutorials, troubleshooting
- **[API Documentation](docs/api/)** - Complete API reference with 133+ endpoints
- **[Developer Documentation](docs/developer/)** - Architecture, contributing, setup, testing
- **[Documentation Index](docs/README.md)** - Complete documentation index

### Quick Links

- [Getting Started](docs/user/GETTING_STARTED.md) - New user guide
- [User Manual](docs/user/USER_MANUAL.md) - Complete feature guide
- [API Reference](docs/api/API_REFERENCE.md) - API documentation
- [HuggingFace Setup](HUGGINGFACE_SETUP_GUIDE.md) - Fix rate limiting issues
- [Contributing](docs/developer/CONTRIBUTING.md) - How to contribute
- [Architecture](docs/developer/ARCHITECTURE.md) - System architecture

## Features

- **🎙️ Voice Cloning Engines**: 
  - **XTTS v2** (Coqui TTS) - High-quality multilingual voice cloning (14 languages) ✅ Integrated
  - **Chatterbox TTS** (Resemble AI) ⭐ **RECOMMENDED** - State-of-the-art quality, outperforms ElevenLabs (23 languages, emotion control) ✅ Integrated
  - **Tortoise TTS** 🔥 **HQ MODE** - Ultra-realistic HQ mode for maximum quality (quality presets) ✅ Integrated
- **🔊 Audio Playback**: 
  - Full audio I/O integration ✅ Complete
- **📚 Complete Documentation**: 
  - User documentation, API reference, developer guides ✅ Complete
- **📦 Windows Installer**: 
  - Professional installer with automatic dependency installation ✅ Complete
- **🔄 Update System**: 
  - Automatic update checking and installation ✅ Complete
  - Timeline playback controls (Play/Pause/Stop/Resume) ✅ Complete
  - Profile preview functionality ✅ Complete
  - Voice synthesis playback ✅ Complete
  - Audio file persistence to projects ✅ Complete
  - Automatic saving after synthesis ✅ Complete
- **📊 Visual Components**: 
  - WaveformControl (Win2D) ✅ Complete
  - SpectrogramControl (Win2D) ✅ Complete
  - Timeline clip waveforms ✅ Complete
  - Timeline spectrogram visualization ✅ Complete
  - Zoom controls ✅ Complete
  - AnalyzerView basic tabs ✅ Complete
  - NAudio-based high-quality playback ✅ Complete
- **📊 Quality Metrics**: Comprehensive quality assessment system ✅ Complete
  - **MOS Score** (1.0-5.0) - Audio quality estimation
  - **Voice Similarity** (0.0-1.0) - Reference vs generated comparison
  - **Naturalness** (0.0-1.0) - Prosody and speech-like characteristics
  - **SNR** (dB) - Signal-to-noise ratio
  - **Artifact Detection** - Clicks, pops, distortion detection
  - **Quality Enhancement** - Automatic denoising, normalization, artifact removal
  - **Voice Profile Matching** - F0, formants, MFCC analysis
- **🧪 Comprehensive Test Suite**: Production-ready testing infrastructure ✅ Complete
  - **264 test files** with ~94% code coverage (exceeds 80% target)
  - **~2,000+ test cases** across the entire suite
  - **100% backend API route coverage** (103 route test files covering all 87+ routes)
  - **100% CLI coverage** (all CLI utilities tested)
  - **Complete optimized module coverage** (LRU caches, batch processing, connection pooling, etc.)
  - **487+ engine test cases** across all voice cloning engines
  - See [Testing Guide](docs/developer/TESTING.md) for complete details
- **Modular Panel System**: Extensible panel architecture supporting 100+ panels
- **MVVM Pattern**: Clean separation of concerns
- **Design System**: Comprehensive design tokens and styles
- **MCP Integration**: PDF unlock support implemented; design tokens and AI engines planned for future
- **Backend API**: REST/WebSocket communication

## Documentation

### 🚀 Quick Start
- **[QUICK_START_NEXT_STEPS.md](docs/governance/QUICK_START_NEXT_STEPS.md)** - **⭐ IMMEDIATE** - Next steps after foundation complete
- **[QUICK_START_FOR_CURSOR.md](docs/design/QUICK_START_FOR_CURSOR.md)** - **5-minute quick start guide**
- **[CURSOR_SETUP_COMPLETE.md](docs/design/CURSOR_SETUP_COMPLETE.md)** - **Setup status and answers to common questions**
- **[NAUDIO_SETUP_GUIDE.md](docs/governance/NAUDIO_SETUP_GUIDE.md)** - **NAudio package setup instructions**

### 🔧 Engine System
- **[ENGINE_MANIFEST_SYSTEM.md](docs/design/ENGINE_MANIFEST_SYSTEM.md)** - Class-based engine manifests
- **[RUNTIME_ENGINE_SYSTEM.md](docs/design/RUNTIME_ENGINE_SYSTEM.md)** - Process-based runtime engines
- **[ENGINE_CONFIG_SYSTEM.md](docs/design/ENGINE_CONFIG_SYSTEM.md)** - Engine defaults and configuration

### 🛡️ Migration & Guardrails
- **[GOVERNOR_LEARNERS_PRESERVATION.md](docs/governance/GOVERNOR_LEARNERS_PRESERVATION.md)** - Governor + learners preservation rules
- **[CURSOR_GUARDRAILS.md](docs/governance/CURSOR_GUARDRAILS.md)** - Strict rules for Cursor/Overseer
- **[PANEL_REGISTRY_MERGE.md](docs/governance/PANEL_REGISTRY_MERGE.md)** - Auto-merge panel discovery system
- **[POST_MIGRATION_CHECKS.md](docs/governance/POST_MIGRATION_CHECKS.md)** - 2-minute verification checklist

### 🔍 Panel Discovery Tools (Missing Panels?)
- **[PANEL_DISCOVERY_QUICK_REF.md](docs/governance/PANEL_DISCOVERY_QUICK_REF.md)** - **QUICK FIX** - Find missing panels in 30 seconds
- **[PANEL_DISCOVERY_SUMMARY.md](docs/governance/PANEL_DISCOVERY_SUMMARY.md)** - Complete panel discovery system overview
- **[Find-AllPanels.ps1](tools/Find-AllPanels.ps1)** - Comprehensive panel discovery script
- **[verify_panels.py](app/cli/verify_panels.py)** - Panel verification and comparison tool
- **[MIGRATION_COMPLETE_CHECKLIST.md](docs/governance/MIGRATION_COMPLETE_CHECKLIST.md)** - Complete verification checklist

### 🚀 Migration Execution
- **[MIGRATION_EXECUTION_GUIDE.md](docs/governance/MIGRATION_EXECUTION_GUIDE.md)** - **START HERE** - Step-by-step migration execution
- **[Test-Migration.ps1](tools/Test-Migration.ps1)** - Verify prerequisites before migration
- **[VS_MigrateToE.ps1](tools/VS_MigrateToE.ps1)** - Production migration script
- **[MIGRATION_READY.md](docs/governance/MIGRATION_READY.md)** - System readiness status

### ⚛️ React/Electron Conversion
- **[REACT_ELECTRON_CONVERSION_GUIDE.md](docs/governance/REACT_ELECTRON_CONVERSION_GUIDE.md)** - **CONVERSION GUIDE** - Convert React/Electron panels to WinUI 3
- **[Discover-ReactPanels.ps1](tools/Discover-ReactPanels.ps1)** - Find all React/Electron panels in C:\VoiceStudio
- **[Convert-ReactPanel.ps1](tools/Convert-ReactPanel.ps1)** - Convert single React panel to WinUI 3
- **[REACT_PANEL_CATALOG.md](docs/governance/REACT_PANEL_CATALOG.md)** - Catalog of discovered React panels

### 🎯 Cursor Integration (NEW)
- **[CURSOR_WORKSPACE_SETUP.md](docs/governance/CURSOR_WORKSPACE_SETUP.md)** - **START HERE** - Workspace setup and quick start for Cursor
- **[PORT_TASKS_BATCH_1.md](docs/governance/PORT_TASKS_BATCH_1.md)** - **NEW** - First 3 PORT tasks with detailed instructions
- **[PANEL_MIGRATION_STRATEGY.md](docs/governance/PANEL_MIGRATION_STRATEGY.md)** - **NEW** - Comprehensive strategy for migrating ~200 panels
- **[WORKSPACE_MIGRATION_GUIDE.md](docs/governance/WORKSPACE_MIGRATION_GUIDE.md)** - Complete workspace migration guide (C:\VoiceStudio → E:\VoiceStudio)
- **[VS_MigrateToE.ps1](tools/VS_MigrateToE.ps1)** - **RECOMMENDED** - Production-ready migration script (uses Robocopy, efficient, safe)
- **[BULK_PANEL_MIGRATION_GUIDE.md](docs/governance/BULK_PANEL_MIGRATION_GUIDE.md)** - Step-by-step guide for bulk panel migration
- **[PANEL_CATALOG.md](docs/governance/PANEL_CATALOG.md)** - Complete inventory of all panels (run `tools\Discover-Panels.ps1` to generate)
- **[Cursor-Migration-Ruleset.md](docs/governance/Cursor-Migration-Ruleset.md)** - **CRITICAL** - Migration rules and PORT command workflow
- **[Migration-Log.md](docs/governance/Migration-Log.md)** - **TRACKING** - Log of all code migrations from C:\VoiceStudio to E:\VoiceStudio
- **[CURSOR_OPERATIONAL_RULESET.md](docs/design/CURSOR_OPERATIONAL_RULESET.md)** - **CRITICAL** - Complete operational rules and guidelines for Cursor - **READ THIS FIRST**
- **[COMPLETE_INTEGRATION_SUMMARY.md](docs/design/COMPLETE_INTEGRATION_SUMMARY.md)** - **NEW** - Complete overview of all integration work - **START HERE**
- **[SKELETON_INTEGRATION_GUIDE.md](docs/design/SKELETON_INTEGRATION_GUIDE.md)** - **NEW** - Step-by-step guide to integrate skeleton code - **READ THIS FIRST**
- **[SKELETON_FILES_MAPPING.md](docs/design/SKELETON_FILES_MAPPING.md)** - **NEW** - Complete file-by-file mapping reference
- **[CURSOR_MASTER_INSTRUCTIONS.md](docs/design/CURSOR_MASTER_INSTRUCTIONS.md)** - **Master guide for Cursor integration**
- **[CURSOR_AGENT_GUIDELINES_V2.md](docs/design/CURSOR_AGENT_GUIDELINES_V2.md)** - **PRIMARY** - Complete agent system (1 Overseer + 6 Workers) - **USE V2**
- **[CURSOR_AGENT_GUIDELINES.md](docs/design/CURSOR_AGENT_GUIDELINES.md)** - Original agent guidelines (use V2 instead)
- **[OVERSEER_SYSTEM_PROMPT_V2.md](docs/design/OVERSEER_SYSTEM_PROMPT_V2.md)** - **Ready-to-use Overseer agent prompt**
- **[WORKER_AGENT_PROMPTS.md](docs/design/WORKER_AGENT_PROMPTS.md)** - **Ready-to-use prompts for all 6 workers**
- **[INTEGRATION_GUIDE.md](docs/design/INTEGRATION_GUIDE.md)** - **How to merge new UI with existing code**
- **[PRESERVATION_CHECKLIST.md](docs/design/PRESERVATION_CHECKLIST.md)** - **Ensure no existing functionality is lost**
- **[CURSOR_INTEGRATION_INSTRUCTIONS.md](docs/design/CURSOR_INTEGRATION_INSTRUCTIONS.md)** - **Step-by-step integration process**
- **[REGRESSION_CHECKLIST.md](docs/design/REGRESSION_CHECKLIST.md)** - **QA verification checklist**

### 📋 Core Specifications
- **[MEMORY_BANK.md](docs/design/MEMORY_BANK.md)** - **Critical information that must never be forgotten**
- **[VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md](docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md)** - **Master implementation specification**
- **[UI_IMPLEMENTATION_SPEC.md](docs/design/UI_IMPLEMENTATION_SPEC.md)** - **Complete UI implementation specification**
- **[GUARDRAILS.md](docs/design/GUARDRAILS.md)** - **CRITICAL: Read before making changes**
- **[GLOBAL_GUARDRAILS.md](docs/design/GLOBAL_GUARDRAILS.md)** - **Global guardrails to prevent simplification**

### 🏗️ Architecture
- **[VoiceStudio-Architecture.md](docs/design/VoiceStudio-Architecture.md)** - **CURRENT** - Definitive architecture reference
- [Architecture Overview](docs/design/architecture.md)
- [Detailed Architecture](docs/design/architecture-detailed.md)
- [Architecture Data Flow](docs/design/ARCHITECTURE_DATA_FLOW.md) - Data flow and contract schemas
- [File Structure](docs/design/file-structure.md)
- [Migration Guide](docs/design/architecture-migration.md)

### 🎨 UI & Design
- **[PANEL_IMPLEMENTATION_GUIDE.md](docs/design/PANEL_IMPLEMENTATION_GUIDE.md)** - **CRITICAL** - Complete guide for implementing 100+ panels
- **[INNOVATIVE_ADVANCED_PANELS_CATALOG.md](docs/design/INNOVATIVE_ADVANCED_PANELS_CATALOG.md)** - **NEW** - Complete catalog of 9 innovative advanced panels (Pro/Advanced/Technical/Meta tiers)
- **[SKELETON_INTEGRATION_GUIDE.md](docs/design/SKELETON_INTEGRATION_GUIDE.md)** - **NEW** - Step-by-step guide to integrate skeleton code with existing codebase
- **[SKELETON_FILES_MAPPING.md](docs/design/SKELETON_FILES_MAPPING.md)** - **NEW** - Complete file-by-file mapping reference
- [MainWindow Structure](docs/design/MAINWINDOW_STRUCTURE.md)
- [Panel System](docs/design/panel-system.md)
- [Panel Skeletons Reference](docs/design/PANEL_SKELETONS_REFERENCE.md)
- [Canonical Files](docs/design/CANONICAL_FILES.md)
- [Advanced UI/UX Features](docs/design/ADVANCED_UI_UX_FEATURES.md) - 21 advanced features roadmap

### 🤖 AI Integration
- **[AI_INTEGRATION_GUIDE.md](docs/design/AI_INTEGRATION_GUIDE.md)** - **Integration for 3 AIs + Overseer setup**
- **[ENGINE_RECOMMENDATIONS.md](docs/design/ENGINE_RECOMMENDATIONS.md)** - **Backend engine choices (Chatterbox, Coqui, Whisper)**
- **[TECHNICAL_STACK_SPECIFICATION.md](docs/design/TECHNICAL_STACK_SPECIFICATION.md)** - **NEW** - Complete technical stack specification (Python, .NET, WinUI 3, dependencies)

### 📅 Roadmap & Planning
- **[COMPREHENSIVE_STATUS_SUMMARY.md](docs/governance/COMPREHENSIVE_STATUS_SUMMARY.md)** - **⭐ CURRENT** - Complete status summary of all completed work
- **[DEVELOPMENT_ROADMAP.md](docs/governance/DEVELOPMENT_ROADMAP.md)** - Comprehensive development plan & priorities
- **[VOICE_CLONING_QUALITY_STATUS.md](docs/governance/VOICE_CLONING_QUALITY_STATUS.md)** - Voice cloning quality tracking and benchmarks
- [Phase Roadmap Complete](docs/design/PHASE_ROADMAP_COMPLETE.md) - 10-phase roadmap
- [Phase 2 Roadmap](docs/design/PHASE_2_ROADMAP.md)
- [Execution Plan](docs/design/EXECUTION_PLAN.md) - Step-by-step plan
- [Roadmap](docs/design/roadmap.md) - Basic roadmap
- [Deep Research Prompts](docs/design/DEEP_RESEARCH_PROMPTS.md)
- [Deep Research Recommendations](docs/design/DEEP_RESEARCH_RECOMMENDATIONS.md)

### ✅ Implementation Status
- [Implementation Complete](docs/design/IMPLEMENTATION_COMPLETE.md)
- [Implementation Status](docs/design/IMPLEMENTATION_STATUS.md)
- [Implementation Milestones](docs/design/implementation-milestones.md)
- [Implementation Checklist](docs/design/IMPLEMENTATION_CHECKLIST.md)
- [Final Verification](docs/design/FINAL_VERIFICATION.md)
- [Ready for Implementation](docs/design/READY_FOR_IMPLEMENTATION.md)
- [What You Get](docs/design/WHAT_YOU_GET.md)

### 🛠️ Advanced Features
- [Pre-Cursor Add-Ins](docs/design/PRE_CURSOR_ADDINS.md) - PanelStack, CommandPalette, etc.
- [PanelStack Usage](docs/design/PANELSTACK_USAGE.md)
- [Command Palette Usage](docs/design/COMMAND_PALETTE_USAGE.md)
- [UI Test Hooks](docs/design/UI_TEST_HOOKS.md)

### 📖 Legacy Documentation
- [Cursor Instructions](docs/design/CURSOR_INSTRUCTIONS.md) - Original implementation guide
- [Overseer Context](docs/design/OVERSEER_CONTEXT.md) - Original Overseer instructions
- [Overseer System Prompt](docs/design/OVERSEER_SYSTEM_PROMPT.md) - Original prompt (use V2 instead)

## Development Status

✅ Architecture defined
✅ Core library structure created
✅ Panel system implemented
✅ Design tokens and styles
✅ Panel views with MVVM
✅ **MainWindow shell complete** - Full skeleton with nav rail, panel hosts, command deck, status bar
✅ **All 6 panels implemented** - ProfilesView, TimelineView, EffectsMixerView, AnalyzerView, MacroView, DiagnosticsView
✅ **All ViewModels created** - All implement IPanelView interface
✅ **Panel content wired** - MainWindow assigns panels to PanelHosts
✅ **Voice Cloning Engines** - XTTS v2, Chatterbox TTS (state-of-the-art), Tortoise TTS (ultra-realistic HQ mode)
✅ **Quality Metrics Framework** - Comprehensive quality assessment (MOS score, similarity, naturalness, SNR, artifact detection)
✅ **Quality Metrics Integration** - All engines support `enhance_quality` and `calculate_quality` parameters
✅ **Quality Testing Suite** - Comprehensive test framework (`test_quality_metrics.py` with 9 test functions)
✅ **Backend API** - FastAPI with voice cloning endpoints + detailed quality metrics (QualityMetrics model)
✅ **UI-Backend Integration** - IBackendClient (C#) + ProfilesView/DiagnosticsView wired to backend
✅ **Engine Manifests** - All engines have manifests with quality capabilities documented
✅ **Engine Registry** - Complete documentation (`engines/README.md`) with quality features and standards
✅ **Audio Utilities** - 8 functions ported with quality enhancements (core + voice cloning quality functions)
✅ **Panel Discovery** - 8 panels discovered and registered (voice cloning panels identified)
✅ **Quality Testing Suite** - Comprehensive test framework (`test_quality_metrics.py` with 9 test functions)
✅ **Engine Benchmark Script** - Quality comparison tool (`app/cli/benchmark_engines.py`) for measuring engine performance
✅ **TimelineView Audio Playback** - Play/Pause/Stop controls integrated with IAudioPlayerService
✅ **VoiceSynthesisView** - Complete UI with quality metrics display and audio playback
✅ **Quality-Based Engine Selection** - Intelligent engine routing based on quality requirements
✅ **Profile Preview** - Quick synthesis and playback in ProfilesView
✅ **Comprehensive Status** - See [COMPREHENSIVE_STATUS_SUMMARY.md](docs/governance/COMPREHENSIVE_STATUS_SUMMARY.md) for complete status
⏳ MCP bridge implementation (pending)
⏳ Full workspace migration (pending)

## Troubleshooting WinUI XAML Compiler Errors

VoiceStudio uses WinUI 3 with Windows App SDK 1.8. The XAML compiler can sometimes fail silently with exit code 1 and no error output.

**For comprehensive troubleshooting, see the [XAML Compiler Playbook](docs/build/XAML_COMPILER_PLAYBOOK.md)** - a consolidated runbook with decision trees, copy-paste commands, and emergency recovery procedures.

Use the following workflow for quick diagnosis:

### Quick Diagnostic Build

For silent XAML compiler failures (exit code 1, no output), use:

1. Run reproducible single-threaded diagnostic build:

   ```powershell
   .\scripts\build-with-binlog.ps1
   ```

2. Analyze the binlog:

   ```powershell
   .\scripts\analyze-binlog.ps1 -BinlogPath .buildlogs\build_diagnostic_*.binlog
   ```

3. If the issue persists, use binary search to isolate the problematic XAML file:

   ```powershell
   .\scripts\xaml-binary-search.ps1
   ```

### Common XAML Compiler Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Exit code 1, no output.json | Attached property on ContentPresenter | Remove `TextElement.*` attached properties |
| Exit code 1 for nested Views | XAML in `Views/subfolder/` | Flatten to `Views/` root |
| Missing output.json intermittently | File lock contention | Build single-threaded with `-m:1` |
| WMC9999 in-process error | Task-based compiler issue | Use `UseXamlCompilerExecutable=true` |

### Key Resources

- **[XAML Compiler Playbook](docs/build/XAML_COMPILER_PLAYBOOK.md)** - Single operational runbook for all XAML troubleshooting
- **[XAML Change Protocol](docs/developer/XAML_CHANGE_PROTOCOL.md)** - Mandatory procedures for XAML changes
- **[UI Hardening Guidelines](docs/developer/UI_HARDENING_GUIDELINES.md)** - Best practices for XAML stability
- **[GitHub #10027](https://github.com/microsoft/microsoft-ui-xaml/issues/10027)** - Can't get error output from XamlCompiler.exe
- **[GitHub #10947](https://github.com/microsoft/microsoft-ui-xaml/issues/10947)** - XamlCompiler.exe exits code 1 for Views subfolders

### Diagnostic Scripts

| Script | Purpose |
|--------|---------|
| `scripts/build-with-binlog.ps1` | Clean single-threaded build with binlog capture |
| `scripts/analyze-binlog.ps1` | Extract XamlCompiler invocations from binlog |
| `scripts/xaml-binary-search.ps1` | Binary search to isolate problematic XAML |
| `scripts/build/diagnose_xaml_compiler.ps1` | Comprehensive XAML diagnostics |
| `tools/xaml-compiler-wrapper.cmd` | Wrapper handling false-positive exit code 1 |

## License

[To be determined]

