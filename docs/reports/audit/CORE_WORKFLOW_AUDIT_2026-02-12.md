# Core Workflow Audit — Audio Import → Voice Cloning → Transcription → Playback

**Date**: 2026-02-12
**Author**: Lead/Principal Architect (AI-assisted audit)
**Scope**: End-to-end user workflow tracing every panel, feature, function, backend route, engine, and service
**Branch**: `release/1.0.1`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Complete Workflow Trace](#3-complete-workflow-trace)
   - 3.1 [Phase 1: Audio Import](#31-phase-1-audio-import)
   - 3.2 [Phase 2: Voice Cloning](#32-phase-2-voice-cloning)
   - 3.3 [Phase 3: Voice Synthesis](#33-phase-3-voice-synthesis-using-cloned-profile)
   - 3.4 [Phase 4: Transcription](#34-phase-4-transcription)
   - 3.5 [Phase 5: Audio Playback](#35-phase-5-audio-playback)
4. [Gap Register](#4-gap-register)
   - 4.1 [CRITICAL — Workflow-Breaking](#41-critical--workflow-breaking)
   - 4.2 [HIGH — Functional Gaps](#42-high--functional-gaps)
   - 4.3 [MEDIUM — Quality / Robustness](#43-medium--quality--robustness)
   - 4.4 [LOW — Polish / Documentation](#44-low--polish--documentation)
5. [Cross-Workflow Integration Gaps](#5-cross-workflow-integration-gaps)
6. [Panel-by-Panel Feature Audit](#6-panel-by-panel-feature-audit)
7. [Prioritized Remediation Roadmap](#7-prioritized-remediation-roadmap)
8. [Dependency Map](#8-dependency-map)
9. [Risks](#9-risks)
10. [Success Criteria](#10-success-criteria)

---

## 1. Executive Summary

This report traces the complete user workflow through VoiceStudio — from importing an audio file, through voice cloning, transcription, and audio playback — and identifies every gap, stub, missing implementation, and broken path. The audit covers every panel, service, backend endpoint, and engine involved.

**Bottom line:** The backend engine and service layers are broadly functional. The critical gaps are in the **UI layer** (stubbed panels, disconnected import paths) and in **cross-workflow integration** (transcription not connected to timeline, no unified audio asset management).

**35 discrete issues** were identified and categorized:

| Severity | Count | Summary |
|----------|-------|---------|
| CRITICAL | 3 | Import no-op, Transcribe UI stub, Transcription persistence volatile |
| HIGH | 7 | Upload validation, Library upload, drag-drop, Quick Clone API, transcript save, WhisperX, recording |
| MEDIUM | 7 | Timeline transcript, profile audio lookup, wizard race, playback service duplication, loop, manifests, multi-reference |
| LOW | 5 | Unified asset manager, temp cleanup, streaming usage, model download UX, format docs |
| CROSS-WORKFLOW | 6 | Import→Library, Clone→Library, Transcribe→Timeline, Audio→Clone shortcut, Clone→Synthesis, Synthesis→Timeline |
| **TOTAL** | **28 unique + 7 cross-workflow** | |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI Layer — WinUI 3 (C#)                       │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ Toolbar   │  │ Library      │  │ VoiceSynth   │  │ Timeline│ │
│  │ Transport │  │ Panel        │  │ Panel        │  │ Panel   │ │
│  └─────┬─────┘  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │
│        │               │                 │                │      │
│  ┌─────┴──────┐  ┌─────┴──────┐  ┌──────┴───────┐  ┌────┴────┐ │
│  │ Cloning    │  │ Quick      │  │ Transcribe   │  │ TextSpe │ │
│  │ Wizard     │  │ Clone      │  │ Panel        │  │ Editor  │ │
│  └─────┬──────┘  └─────┬──────┘  └──────┬───────┘  └────┬────┘ │
│        │               │                 │                │      │
│        └───────────┬────┴─────────────────┴────────────────┘      │
│                    │                                              │
│              BackendClient (HTTP + WebSocket)                     │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────────────────┐
│                  Backend Layer — FastAPI (Python)                  │
│                                                                   │
│  /api/audio/*     /api/voice/*      /api/transcribe/              │
│  /api/profiles/*  /api/projects/*   /api/voice/clone/wizard/*     │
│                                                                   │
│  Services: EngineService, ProjectStoreService, AudioArtifactReg   │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────────────────┐
│                   Engine Layer — Python                            │
│                                                                   │
│  TTS/Clone:  XTTS v2, Chatterbox, OpenVoice, Tortoise, Bark,    │
│              Fish Speech, Higgs Audio, GPT-SoVITS                 │
│                                                                   │
│  STT:        Whisper (faster-whisper), WhisperCPP, Vosk           │
│              WhisperX (REFERENCED BUT NOT IMPLEMENTED)            │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────────────────┐
│                       Storage Layer                               │
│                                                                   │
│  data/audio_uploads/{uuid}.{ext}        — Temporary uploads       │
│  ~/.voicestudio/projects/{id}/audio/    — Project audio files     │
│  ~/.voicestudio/profiles/{id}/          — Voice profiles + ref    │
│  In-memory _transcriptions dict         — VOLATILE (lost restart) │
│  SQLite voicestudio.db (migration exists, UNUSED for transcripts) │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Complete Workflow Trace

### 3.1 Phase 1: Audio Import

#### File Inventory

| Layer | File | Purpose |
|-------|------|---------|
| UI | `src/VoiceStudio.App/MainWindow.xaml.cs:1939` | `ImportAudioFile()` method (Ctrl+I) |
| UI | `src/VoiceStudio.App/Commands/FileOperationsHandler.cs:338` | `ImportAudioAsync()` method |
| UI | `src/VoiceStudio.App/Services/BackendClient.cs:908` | `UploadAudioFileAsync()` |
| UI | `src/VoiceStudio.App/ViewModels/LibraryViewModel.cs` | Library asset management |
| UI | `src/VoiceStudio.App/Views/Panels/LibraryView.xaml.cs:1074` | Drag-drop (reorder only) |
| Backend | `backend/api/routes/audio.py:950` | `POST /api/audio/upload` |
| Backend | `backend/api/routes/voice.py:1358` | `POST /api/voice/analyze` |
| Backend | `backend/api/routes/voice.py:2725` | `POST /api/voice/clone` |
| Backend | `backend/api/routes/profiles.py:444` | `POST /api/profiles/{id}/preprocess-reference` |
| Backend | `backend/api/routes/projects.py:217` | `POST /api/projects/{id}/audio/save` |
| Backend | `backend/core/security/file_validation.py` | `validate_audio_file()` |
| Service | `backend/services/AudioArtifactRegistry.py` | Content-addressed audio cache |
| Service | `backend/services/ContentAddressedAudioCache.py` | Dedup layer |
| Service | `backend/services/ProjectStoreService.py` | Project file persistence |

#### Workflow Paths

**Path A: FileOperationsHandler (WORKING)**

```
User: File → Import Audio
  → FileOperationsHandler.ImportAudioAsync()
    → DialogService.ShowOpenFilesAsync() [file picker]
      → BackendClient.UploadAudioFileAsync(filePath)
        → HTTP POST /api/audio/upload (multipart)
          → audio.py:upload_audio()
            ├─ Reads file content
            ├─ Generates UUID file_id
            ├─ Saves to: data/audio_uploads/{file_id}.{ext}
            └─ Returns AudioUploadResponse { id, filename, path, size }
      → BackendClient.SaveAudioToProjectAsync() [if project active]
        → POST /api/projects/{project_id}/audio/save?audio_id={id}
          → ProjectStoreService.save_audio_file()
            └─ Copies to: ~/.voicestudio/projects/{project_id}/audio/{filename}.wav
```

**Status: ✅ WORKING** — complete upload, validation (at project save), storage.

**Path B: MainWindow.ImportAudioFile (BROKEN)**

```
User: Ctrl+I or Import Audio toolbar button
  → MainWindow.ImportAudioFile()
    → FileOpenPicker shown
    → File selected
    → Shows toast "Audio Imported"
    ❌ DOES NOT UPLOAD TO BACKEND
    ❌ Just switches to Voice Synthesis panel
```

**Status: ❌ BROKEN** — cosmetic only; no actual import occurs.

**Path C: Library Panel Drag-Drop (NOT IMPLEMENTED FOR IMPORT)**

```
User: Drags file from Windows Explorer to Library panel
  → LibraryView.Asset_DragOver / Asset_Drop
    → Handles INTERNAL reordering only
    ❌ No DataPackage.GetStorageItemsAsync() handler
    ❌ Cannot import external files
```

**Status: ❌ NOT IMPLEMENTED** for external file import.

#### Import Issues Found

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| C-1 | `MainWindow.ImportAudioFile()` is a no-op (shows toast, no upload) | **CRITICAL** | `MainWindow.xaml.cs:1939` |
| H-1 | `/api/audio/upload` does not call `validate_audio_file()` | **HIGH** | `audio.py:950` |
| H-2 | Library API has no file upload endpoint (metadata-only POST) | **HIGH** | `library.py` |
| H-3 | LibraryView drag-drop only reorders; cannot import external files | **HIGH** | `LibraryView.xaml.cs:1074` |
| X-1 | Imported audio not automatically visible in Library panel | **CROSS** | Import → Library |

---

### 3.2 Phase 2: Voice Cloning

#### File Inventory

| Layer | File | Purpose |
|-------|------|---------|
| UI | `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs` | 4-step wizard ViewModel |
| UI | `src/VoiceStudio.App/ViewModels/VoiceQuickCloneViewModel.cs` | One-click clone ViewModel |
| UI | `src/VoiceStudio.App/Views/Panels/VoiceCloningWizardView.xaml.cs` | Wizard UI |
| UI | `src/VoiceStudio.App/Views/Panels/VoiceQuickCloneView.xaml.cs` | Quick Clone UI |
| UI | `src/VoiceStudio.App/Views/Panels/VoiceSynthesisViewModel.cs` | Synthesis panel (uses profiles) |
| Backend | `backend/api/routes/voice_cloning_wizard.py` | Wizard endpoints |
| Backend | `backend/api/routes/voice.py:2725` | `/api/voice/clone` |
| Backend | `backend/api/routes/voice.py` | `/api/voice/synthesize` |
| Backend | `backend/api/routes/profiles.py` | Profile CRUD |
| Backend | `backend/api/v3/voices.py` | V3 voice API |
| Backend | `backend/api/v3/synthesis.py` | V3 synthesis |
| Engine | `app/core/engines/xtts_engine.py` | XTTS v2 (primary clone engine) |
| Engine | `app/core/engines/chatterbox_engine.py` | Chatterbox |
| Engine | `app/core/engines/openvoice_engine.py` | OpenVoice |
| Engine | `app/core/engines/tortoise_engine.py` | Tortoise |
| Engine | `app/core/engines/router.py` | Engine routing |
| Service | `backend/services/engine_service.py` | Engine orchestration |
| Service | `backend/services/engine_loader.py` | Engine loading |

#### Wizard Workflow (4-Step)

```
Step 1 — Upload:
  VoiceCloningWizardViewModel.BrowseAudioAsync()
    → File picker → Upload via /api/audio/upload
    → Stores audio_id in wizard state

Step 2 — Validate:
  POST /api/voice/clone/wizard/validate-audio
    → Analyzes: duration, sample rate, channels, quality score
    → Returns validation result

Step 3 — Process:
  POST /api/voice/clone/wizard/start
    → Creates WizardJob with reference_audio_id
  POST /api/voice/clone/wizard/{job_id}/process
    → Background task (asyncio.create_task):
      ├─ Creates profile via profiles.create_profile()
      ├─ Generates test synthesis via voice.synthesize()
      └─ Calculates quality metrics via voice.analyze_audio()

Step 4 — Review:
  GET /api/voice/clone/wizard/{job_id}/status (polling)
    → Returns completion state
  POST /api/voice/clone/wizard/{job_id}/finalize
    → Updates profile name/description
```

**Status: ✅ WORKING** — full 4-step flow functional.

#### Quick Clone Workflow

```
VoiceQuickCloneViewModel
  → Upload audio
    → _backendClient.CloneVoiceAsync()
      → POST /api/voice/clone
        → Validates reference audio
        → Gets engine via engine_router.get_engine(engine_id)
        → Calls engine.clone_voice() or engine.synthesize()
        → Returns VoiceCloneResponse { profile_id, audio_id, quality }
```

**Status: ⚠️ SUSPECT** — `CloneVoiceAsync()` method signature may not match the `/api/voice/clone` endpoint contract (stream vs `List[UploadFile]`).

#### Engine Cloning Support Matrix

| Engine | `clone_voice()` | `synthesize(speaker_wav=)` | Multi-Reference | Status |
|--------|-----------------|---------------------------|-----------------|--------|
| XTTS v2 | ✅ | ✅ | ✅ Ensemble | Working |
| Chatterbox | ✅ | ✅ | ❌ First only | Working |
| OpenVoice | ❌ | ✅ (embedding) | ❌ First only | Working |
| Tortoise | ✅ | ✅ | ❌ First only | Working |
| Bark | ❌ | ✅ (ref param) | ❌ | Working |
| Fish Speech | ✅ | ✅ | ❌ First only | Working |
| Higgs Audio | ❌ | ✅ | ❌ | Working |
| GPT-SoVITS | ❌ | Profile-based | N/A | Working (training required) |

#### Reference Audio Storage Flow

```
Upload → data/audio_uploads/{uuid}.wav (temporary)
    ↓ (profile creation)
Profile → ~/.voicestudio/profiles/{profile_id}/reference_audio.wav (persistent)
    ↓ (synthesis time)
Engine → Loads from profile path → speaker embedding cached
```

**Reference audio IS actually used** — engines receive file paths and load audio during synthesis. Evidence:
- `xtts_engine.py:475` — `self.tts.tts_to_file(speaker_wav=speaker_wav, ...)`
- `chatterbox_engine.py:390` — `self.tts.get_speaker_embedding(speaker_wav[0])`
- `openvoice_engine.py:439` — `speaker_embedding = se_extractor.get_se(reference_audio_path, ...)`

#### Cloning Issues Found

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| H-4 | Quick Clone `CloneVoiceAsync()` may not match `/api/voice/clone` signature | **HIGH** | `VoiceQuickCloneViewModel.cs:246` |
| M-3 | Wizard processing is async background task; status polling may race | **MEDIUM** | `voice_cloning_wizard.py:559` |
| M-6 | Engine manifests don't declare capabilities (clone/synthesize/transcribe) | **MEDIUM** | `engines/*.json` |
| M-7 | Only XTTS supports multi-reference ensemble; others silently use first | **MEDIUM** | All engines |
| M-2 | Profile reference audio lookup has multiple fallbacks; silent failure | **MEDIUM** | `voice.py:633-648` |
| X-2 | Cloned voice sample audio not added to Library | **CROSS** | Clone → Library |
| X-5 | After cloning, user must manually navigate to Synthesis + select profile | **CROSS** | Clone → Synthesis |

---

### 3.3 Phase 3: Voice Synthesis (Using Cloned Profile)

#### Workflow

```
VoiceSynthesisViewModel
  → User selects profile from dropdown
  → User enters text
  → SynthesizeAsync()
    → POST /api/voice/synthesize { text, profile_id, engine_id }
      → Backend loads profile
      → Gets reference_audio_url or checks profiles/{id}/reference_audio.wav
      → Calls engine.synthesize(text, speaker_wav=profile_audio_path)
      → Returns { AudioUrl, AudioId, Duration }
  → Download audio from AudioUrl
  → Save to %TEMP%\voicestudio_{guid}.wav
  → AudioPlayerService.PlayFileAsync(tempPath)
```

**Status: ✅ WORKING** — full synthesis + playback functional.

#### Synthesis Issues Found

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| X-6 | Synthesized audio stays in panel; no "Add to Timeline" action | **CROSS** | Synthesis → Timeline |
| L-2 | Temp files (%TEMP%\voicestudio_*.wav) not cleaned up on exit | **LOW** | `VoiceSynthesisViewModel.cs` |

---

### 3.4 Phase 4: Transcription

#### File Inventory

| Layer | File | Purpose |
|-------|------|---------|
| UI | `src/VoiceStudio.App/Views/Panels/TranscribeView.xaml` | Panel UI (**STUB — header only**) |
| UI | `src/VoiceStudio.App/Views/Panels/TranscribeView.xaml.cs` | Code-behind |
| UI | `src/VoiceStudio.App/Views/Panels/TranscribeViewModel.cs` | ViewModel (fully implemented) |
| UI | `src/VoiceStudio.App/ViewModels/TextBasedSpeechEditorViewModel.cs` | Text editor with transcription |
| UI | `src/VoiceStudio.App/Services/BackendClient.cs` | `TranscribeAudioAsync()` |
| UI | `src/VoiceStudio.App/Core/Models/Transcription.cs` | C# data models |
| Backend | `backend/api/routes/transcribe.py` | `/api/transcribe/` endpoint |
| Backend | `backend/api/routes/pipeline.py` | STT→LLM→TTS pipeline |
| Backend | `backend/api/routes/text_speech_editor.py` | Text editor API |
| Backend | `backend/data/migrations/v001_core_persistence_tables.py:215` | Transcriptions table migration |
| Engine | `app/core/engines/whisper_engine.py` | faster-whisper (functional) |
| Engine | `app/core/engines/whisper_cpp_engine.py` | whisper.cpp (functional) |
| Engine | `app/core/engines/vosk_engine.py` | Vosk STT (functional) |
| Engine | `engines/whisper/engine.manifest.json` | Whisper manifest |

#### Transcription Workflow

```
TranscribeViewModel.TranscribeAsync()
  → BackendClient.TranscribeAudioAsync()
    → POST /api/transcribe/ { audio_id, engine, language, word_timestamps, diarization, use_vad }
      → transcribe.py:
        ├─ Checks STT_ENGINE_AVAILABLE flag
        ├─ Gets engine via EngineService.get_engine(engine_id)
        ├─ Falls back to get_whisper_engine() for whisper/whisper_cpp
        ├─ Resolves audio_id to file path via _get_audio_path()
        ├─ Calls stt_engine.initialize() if needed
        ├─ Calls stt_engine.transcribe(audio=audio_path, ...)
        ├─ Normalizes result to TranscriptionResponse
        └─ Stores in _transcriptions[transcription_id] dict (IN-MEMORY)
      → Returns { id, audio_id, text, language, duration, segments[], word_timestamps[] }
```

**Status: ⚠️ Backend WORKING but UI is STUB; persistence is VOLATILE.**

#### Engine Support Matrix (STT)

| Engine | Implementation | Word Timestamps | Languages | GPU | Status |
|--------|---------------|-----------------|-----------|-----|--------|
| Whisper (faster-whisper) | `whisper_engine.py` | ✅ | 99+ | ✅ CUDA | ✅ Working |
| WhisperCPP | `whisper_cpp_engine.py` | ✅ | Multi | ✅ Optional | ✅ Working |
| Vosk | `vosk_engine.py` | ✅ | Multi | ❌ CPU only | ✅ Working |
| WhisperX | **NOT IMPLEMENTED** | ✅ + Diarization | Multi | ✅ | ❌ Missing |

#### Persistence Architecture (Current vs Required)

**Current (BROKEN):**
```python
# transcribe.py:33
_transcriptions: dict[str, dict] = {}  # Lost on backend restart
```

**Database migration EXISTS but UNUSED:**
```sql
-- v001_core_persistence_tables.py:215-229
CREATE TABLE IF NOT EXISTS transcriptions (
    id TEXT PRIMARY KEY,
    audio_path TEXT NOT NULL,
    language TEXT,
    text TEXT,
    segments TEXT,         -- JSON array
    word_timestamps TEXT,  -- JSON array
    duration REAL,
    confidence REAL,
    engine_id TEXT,
    user_id TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,
    deleted_at TEXT
);
```

**Required:** Implement `TranscriptionRepository` class; replace in-memory dict with DB calls using existing migration.

#### TranscribeView UI State

The **XAML is a stub** — contains only a header/title. The **ViewModel is fully implemented** with:
- Engine selection (whisper, whisperx, whisper-cpp, vosk)
- Language selection (auto-detect + 20+ languages)
- Word timestamps toggle
- Diarization toggle (WhisperX — engine missing)
- VAD toggle
- Transcription list display
- Multi-select support
- Delete transcription
- Drag-and-drop reordering

The disconnect: a complete ViewModel exists with no visual surface to interact with it.

#### Transcription Issues Found

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| C-2 | TranscribeView.xaml is a stub (header only); ViewModel is complete but invisible | **CRITICAL** | `TranscribeView.xaml` |
| C-3 | Transcription persistence is in-memory dict; lost on backend restart | **CRITICAL** | `transcribe.py:33` |
| H-5 | TextBasedSpeechEditor supports editing but no save endpoint exists | **HIGH** | `text_speech_editor.py` |
| H-6 | WhisperX engine referenced in UI dropdown but not implemented | **HIGH** | `TranscribeViewModel.cs:79` |
| M-1 | Timeline has no transcript display (no subtitle track or segment overlay) | **MEDIUM** | TimelineView |
| X-3 | Transcription results not linked to Timeline panel | **CROSS** | Transcribe → Timeline |

---

### 3.5 Phase 5: Audio Playback

#### File Inventory

| Layer | File | Purpose |
|-------|------|---------|
| Service | `src/VoiceStudio.App/Services/AudioPlayerService.cs` | Primary NAudio player |
| Service | `src/VoiceStudio.App/Services/StreamingAudioPlayer.cs` | WebSocket streaming player |
| Service | `src/VoiceStudio.App/Services/AudioPlaybackService.cs` | Alternative player (IAudioPlaybackService) |
| Interface | `src/VoiceStudio.App/Core/Services/IAudioPlayerService.cs` | Primary interface |
| Interface | `src/VoiceStudio.App/Core/Services/IAudioPlaybackService.cs` | Alternative interface |
| UI | `src/VoiceStudio.App/Views/Panels/TimelineViewModel.cs` | Timeline playback controls |
| UI | `src/VoiceStudio.App/Features/Timeline/TimelineViewModel.cs` | Feature-level timeline |
| UI | `src/VoiceStudio.App/Controls/CustomizableToolbar.xaml.cs` | Transport buttons |
| UI | `src/VoiceStudio.App/MainWindow.xaml.cs:2645-2679` | Global playback handlers |
| Command | `src/VoiceStudio.App/Commands/PlaybackOperationsHandler.cs` | Unified command handler |
| Command | `src/VoiceStudio.App/Services/KeyboardShortcutService.cs` | Keyboard shortcuts |
| Backend | `backend/api/routes/voice.py:3799-3983` | WebSocket streaming endpoint |
| Backend | `backend/api/routes/audio_analysis.py` | Waveform/spectrogram |

#### Playback Flows

**Flow A: File-Based Playback (Most Common)**
```
VoiceSynthesisViewModel.PlayAudioAsync()
  → Downloads audio from backend AudioUrl via HttpClient
  → Saves to %TEMP%\voicestudio_{guid}.wav
  → AudioPlayerService.PlayFileAsync(tempPath)
    → NAudio.Wave.AudioFileReader(path)
    → NAudio.Wave.WaveOutEvent (WASAPI)
    → _waveOut.Play()
    → Windows Audio Output
```

**Flow B: Streaming Playback (Real-Time Synthesis)**
```
StreamingAudioPlayer
  → Connects to ws://backend/api/voice/synthesize/stream
  → Backend yields audio chunks via Engine.synthesize_stream()
  → Receives JSON: { type: "audio_chunk", data: base64, chunk_index, sample_rate }
  → Decodes base64 → ConcurrentQueue<AudioChunk>
  → PlaybackLoopAsync dequeues → BufferedWaveProvider
  → WaveOutEvent plays buffered audio
```

**Flow C: Timeline Playback**
```
TimelineViewModel.PlayProjectAudioAsync()
  → GET /api/projects/{id}/audio/{filename}
  → AudioPlayerService.PlayStreamAsync(stream, sampleRate: 22050, channels: 1)
    → Copies to MemoryStream → RawSourceWaveStream (16-bit PCM)
    → WaveOutEvent plays audio
```

#### Transport Controls Wiring

```
Toolbar Button Click (CustomizableToolbar.xaml.cs:381)
  → Maps button ID to command ID:
      "play" → "playback.play"
      "pause" → "playback.play" (toggle)
      "stop" → "playback.stop"
      "record" → "playback.record"
  → KeyboardShortcutService.ExecuteShortcut(commandId)
    → PlaybackOperationsHandler:
        PlayAsync() → _audioPlayer.Resume()
        PauseAsync() → _audioPlayer.Pause()
        StopAsync() → _audioPlayer.Stop()

Keyboard Shortcuts:
  Space → MainWindow.TogglePlayback()
    → Finds TimelineView → TimelineViewModel.IsPlaying?
      → True: PauseAudioCommand
      → False: PlayAudioCommand
  Escape → MainWindow.StopPlayback()
    → AudioPlayerService.Stop()
```

#### Timeline Scrubbing & Preview

```
TimelineViewModel.SeekToPosition(pixelPosition)
  → time = pixels / (PIXELS_PER_SECOND * zoom)
  → AudioPlayerService.Seek(timeInSeconds)
    → _audioFileReader.CurrentTime = TimeSpan.FromSeconds(position)
  → If preview enabled:
    → AudioPlayerService.PlayPreviewSnippetAsync()
      → Plays 150ms snippet at 60% volume
      → Configurable via ISettingsService.Timeline settings
```

**Status: ✅ WORKING** — file, stream, and timeline playback functional.

#### Playback Issues Found

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| H-7 | Record button is stub — state management only; no mic capture | **HIGH** | `PlaybackOperationsHandler.cs:306` |
| M-4 | Two playback services (`AudioPlayerService` + `AudioPlaybackService`) | **MEDIUM** | Services/ |
| M-5 | Loop playback toggle button exists but no loop logic implemented | **MEDIUM** | Toolbar + AudioPlayerService |
| L-3 | Streaming synthesis not used in all views (most use file-based) | **LOW** | StreamingAudioPlayer |

---

## 4. Gap Register

### 4.1 CRITICAL — Workflow-Breaking

| ID | Gap | Location | Description | Remediation |
|----|-----|----------|-------------|-------------|
| **C-1** | MainWindow.ImportAudioFile is a no-op | `MainWindow.xaml.cs:1939` | Shows toast "Audio Imported" but does **not** upload to backend. Ctrl+I does nothing useful. Users believe they imported audio when they did not. | Delegate to `FileOperationsHandler.ImportAudioAsync()`. Remove duplicate toast. |
| **C-2** | TranscribeView is a UI stub | `Views/Panels/TranscribeView.xaml` | Header only; no controls, no text display. The ViewModel is fully implemented with engine selection, language, timestamps, VAD, list management — but has no visual surface. Users **cannot transcribe audio** through the panel. | Build complete XAML: engine ComboBox, language ComboBox, toggle switches, ListBox for transcriptions, TextBlock for output. Wire all bindings to existing TranscribeViewModel properties and commands. |
| **C-3** | Transcription persistence is volatile | `transcribe.py:33` | `_transcriptions` dict in-memory; all transcriptions **lost on backend restart**. Database migration for `transcriptions` table exists (`v001:215-229`) but route doesn't use it. | Implement `TranscriptionRepository` (follow existing repository pattern in `backend/data/repositories/`). Inject into route. Replace all `_transcriptions` dict operations with DB calls. |

### 4.2 HIGH — Functional Gaps

| ID | Gap | Location | Description | Remediation |
|----|-----|----------|-------------|-------------|
| **H-1** | Audio upload missing validation | `audio.py:950` | `/api/audio/upload` saves files without calling `validate_audio_file()`. Other endpoints (voice.py, profiles.py) validate properly. A malicious or corrupt file could be stored. | Add `validate_audio_file(content, filename=file.filename)` with appropriate `HTTPException(400)` on failure, before the save step. |
| **H-2** | Library has no file upload endpoint | `library.py` | `POST /api/library/assets` creates metadata only. No endpoint to upload binary audio files directly into the library. Library panel cannot add new assets from files. | Add `POST /api/library/assets/upload` endpoint: validate audio → store file → create asset entry → return asset. |
| **H-3** | Library drag-drop is internal only | `LibraryView.xaml.cs:1074` | Drag-drop handlers (`Asset_Drop`, `Asset_DragOver`) handle internal reordering. No handler for `DataPackageOperation.Copy` from Windows Explorer. | Add `DragOver` handler that accepts `StorageItems`; add `Drop` handler that reads files, validates extensions/size, uploads via BackendClient, creates library entry, and refreshes the list. |
| **H-4** | Quick Clone API mismatch | `VoiceQuickCloneViewModel.cs:246` | `_backendClient.CloneVoiceAsync()` sends a stream, but `/api/voice/clone` expects `List[UploadFile]` (FastAPI multipart). May cause 422 validation error at runtime. | Verify BackendClient method matches endpoint contract. If mismatch, update BackendClient to use `MultipartFormDataContent` with proper `UploadFile` semantics. |
| **H-5** | Transcript edit save missing | `text_speech_editor.py` | TextBasedSpeechEditor supports rich editing (waveform, segments, alignment) but no `PUT` or `PATCH` endpoint exists to save edited transcripts. All edits are session-local. | Add `PUT /api/transcribe/{id}` endpoint accepting updated text and segments. Update TranscriptionRepository (after C-3) to persist changes. |
| **H-6** | WhisperX engine not implemented | `TranscribeViewModel.cs:79` | Listed as engine option in UI dropdown. No `whisperx_engine.py` exists. Diarization feature (speaker separation) requires WhisperX. Selecting it would fail. | Option A: Implement WhisperX engine adapter. Option B: Remove from dropdown and add to tech debt register as deferred. Option B recommended for v1.0.x. |
| **H-7** | Recording is stubbed | `PlaybackOperationsHandler.cs:306` | Record button exists in toolbar; state management (`IsRecording` flag) works but actual microphone capture is not implemented. Comment in code: "Full implementation requires WebSocket audio streaming from microphone." | Implement NAudio `WaveInEvent` microphone capture → save to file → upload via `/api/audio/upload`. WebSocket streaming optional for v1. |

### 4.3 MEDIUM — Quality / Robustness

| ID | Gap | Location | Description | Remediation |
|----|-----|----------|-------------|-------------|
| **M-1** | Timeline has no transcript display | TimelineView | No integration between transcription results and timeline panel. Users cannot see transcript aligned to audio waveform. | Add transcript/subtitle track to TimelineView. Display segments with timestamps aligned to audio waveform. Allow click-to-seek on transcript segments. |
| **M-2** | Profile reference audio lookup fragile | `voice.py:633-648` | Multiple fallback paths: direct file, URL, profile directory scan. Silent failure if all paths miss. No user feedback when reference audio is unavailable. | Consolidate to authoritative path: `~/.voicestudio/profiles/{id}/reference_audio.wav`. Log warning on fallback. Return `400` with message if all paths fail. |
| **M-3** | Wizard async processing race | `voice_cloning_wizard.py:559` | `asyncio.create_task(process_voice_cloning())` runs background; client polls status. Possible: client reads "complete" before results are fully written. | Add state gate: task writes status ONLY after all data is persisted. Use `asyncio.Event` or status enum with "writing" intermediate state. |
| **M-4** | Two playback service implementations | Services/ | `AudioPlayerService` (IAudioPlayerService) and `AudioPlaybackService` (IAudioPlaybackService) both exist. Maintenance burden; unclear which to use. | Consolidate to `AudioPlayerService` as canonical. Deprecate `AudioPlaybackService` or document its distinct purpose (if any). |
| **M-5** | Loop playback not implemented | Toolbar + AudioPlayerService | Toggle button exists in toolbar (`CustomizableToolbar.xaml.cs:101`) but no loop logic in AudioPlayerService or PlaybackOperationsHandler. Button does nothing. | Add `IsLooping` property to `IAudioPlayerService`. On playback completion, check flag; if set, seek to 0 and play again. Wire toolbar toggle to set the flag. |
| **M-6** | Engine capability manifests incomplete | `engines/*.json` | Only `engines/config.json` exists listing installed engines. Individual manifests don't declare capabilities (`tts`, `clone`, `stt`, `style_transfer`). UI cannot dynamically show/hide features per engine. | Add `"capabilities": ["tts", "clone"]` to each engine manifest. Load at startup to populate UI dropdowns dynamically. |
| **M-7** | Multi-reference audio limited to XTTS | All engines | Only XTTS uses multiple reference files for ensemble quality. Other engines silently use the first file. Users may upload multiple files expecting quality improvement but see no benefit. | Document per-engine behavior in UI tooltip. Optionally warn in Wizard Step 2 when selected engine ignores additional reference files. |

### 4.4 LOW — Polish / Documentation

| ID | Gap | Location | Description | Remediation |
|----|-----|----------|-------------|-------------|
| **L-1** | No unified audio asset manager | Cross-cutting | Audio files scattered: `data/audio_uploads/`, project dirs, profile dirs, temp dirs. No single view of all audio. | Consider unifying under `AudioArtifactRegistry`. Expose consolidated view in Library panel with source indicators. |
| **L-2** | Temp playback files not cleaned up | `VoiceSynthesisViewModel.cs` | Synthesized audio saved to `%TEMP%\voicestudio_{guid}.wav`. No cleanup on app exit. Accumulates disk usage. | Add cleanup in `App.OnSuspending()` or synthesis ViewModel `Dispose()`. Delete matching temp files on startup. |
| **L-3** | Streaming synthesis underutilized | StreamingAudioPlayer | Infrastructure exists (WebSocket + buffered playback) but most views use file-based download + play. First-word latency not optimized. | Document when to use streaming vs file-based. Wire streaming as option in Synthesis panel for low-latency mode. |
| **L-4** | Transcription model auto-download UX | whisper_engine.py | Whisper model download conditional on config. First-time user may lack models; transcription would fail without helpful error. | Add first-run check: detect missing models → show progress dialog during download → allow cancel → remember preference. |
| **L-5** | Audio format support undocumented | audio.py / UI | Supported upload formats (WAV, MP3, FLAC, OGG, etc.) not documented in API docs or file picker filter strings. | Add format list to upload endpoint OpenAPI description. Set file picker filters to supported formats. Show tooltip in UI. |

---

## 5. Cross-Workflow Integration Gaps

These gaps span multiple phases and prevent a seamless end-to-end experience:

| ID | Gap | Phases | Description | Remediation |
|----|-----|--------|-------------|-------------|
| **X-1** | Imported audio not visible in Library | Import → Library | `FileOperationsHandler` uploads audio but Library panel does not refresh or show new asset. User must manually navigate. | After upload completes: (1) create Library asset entry via API, (2) publish event via EventAggregator, (3) Library subscribes and refreshes. |
| **X-2** | Cloned voice output not in Library | Clone → Library | After cloning, generated sample audio and profile are created but not added to Library as reusable assets. | After successful clone: create Library asset entries for both the reference audio and generated sample audio. |
| **X-3** | Transcription not linked to Timeline | Transcribe → Timeline | Transcription results live only in Transcribe panel and TextSpeechEditor. No subtitle track or segment overlay in Timeline. | Add "Send to Timeline" action on transcription. Timeline creates subtitle track displaying segments aligned to audio duration. |
| **X-4** | No audio-to-clone shortcut | Import → Clone | After importing audio, user must manually open Cloning Wizard and re-select the same file. No context action to bridge. | Add right-click context action "Use as Clone Reference" on Library assets and import results. Auto-populates Wizard Step 1 and navigates. |
| **X-5** | No clone-to-synthesis shortcut | Clone → Synthesis | After Wizard Step 4 finalizes a profile, user must manually open Synthesis panel and select the new profile from dropdown. | After finalize: offer dialog "Use this voice now?" → switches to Synthesis panel with new profile pre-selected. |
| **X-6** | No synthesis-to-timeline shortcut | Synthesis → Timeline | Synthesized audio stays in Synthesis panel. User must export/download and manually import to timeline for editing/mixing. | Add "Add to Timeline" button on synthesis results. Creates clip at current playhead position in Timeline. |

---

## 6. Panel-by-Panel Feature Audit

| Panel | Panel ID | Key Features | Status | Issues | Priority Fix |
|-------|----------|--------------|--------|--------|--------------|
| **Library** | `Library` | Asset browse, search, tags, metadata, preview | **Partial** | No upload EP (H-2); no drag-drop import (H-3); no refresh after upload (X-1) | Phase B |
| **VoiceSynthesis** | `VoiceSynthesis` | Profile select, text input, engine select, synthesize, playback | **Working** | No "Add to Timeline" (X-6); temp files not cleaned (L-2) | Phase C/D |
| **VoiceCloningWizard** | `VoiceCloningWizard` | 4-step: upload, validate, process, review/finalize | **Working** | Async race (M-3); no clone→synthesis shortcut (X-5) | Phase C/D |
| **VoiceQuickClone** | `VoiceQuickClone` | One-click clone with engine/quality settings | **Partial** | API mismatch (H-4) | Phase B |
| **Transcribe** | `Transcribe` | Engine select, language, timestamps, VAD, diarization, list | **STUB** | View is header-only (C-2); persistence volatile (C-3); WhisperX missing (H-6) | **Phase A** |
| **TextSpeechEditor** | `TextSpeechEditor` | Transcript edit, waveform, segment alignment, A/B compare | **Working** | No save endpoint for edits (H-5) | Phase B |
| **Timeline** | `Timeline` | Multi-track, playback, scrubbing, preview, markers, position tracking | **Working** | No transcript display (M-1); no clip creation from synthesis (X-6) | Phase C |
| **Recording** | `Recording` | Record from microphone | **STUB** | Record button no-op (H-7) | Phase B |
| **EffectsMixer** | `EffectsMixer` | Effects chain, faders, routing | **Working** | N/A | — |
| **Analyzer** | `Analyzer` | Waveform, spectrogram, LUFS, RMS | **Working** | N/A | — |
| **Training** | `Training` | Dataset management, model training, progress | **Working** | N/A | — |
| **Profiles** | `Profiles` | Profile CRUD, reference audio, metadata | **Working** | Reference audio lookup fragile (M-2) | Phase D |
| **BatchProcessing** | `BatchProcessing` | Batch synthesis/transcription jobs | **Working** | N/A | — |
| **Diagnostics** | `Diagnostics` | System info, logs, correlation IDs, health check | **Working** | N/A | — |

---

## 7. Prioritized Remediation Roadmap

### Phase A: Critical Path Fixes (Unblock Core Workflow)

**Goal:** Make the core workflow functional end-to-end.

| # | Item | Files | Effort |
|---|------|-------|--------|
| A.1 | **C-1: Fix MainWindow.ImportAudioFile** — delegate to `FileOperationsHandler.ImportAudioAsync()` | `MainWindow.xaml.cs` | Small |
| A.2 | **C-2: Build TranscribeView UI** — full XAML layout wired to existing ViewModel | `TranscribeView.xaml` | Medium |
| A.3 | **C-3: Transcription DB persistence** — implement `TranscriptionRepository`; replace in-memory dict | `transcribe.py`, new `backend/data/repositories/transcription_repository.py` | Medium |
| A.4 | **H-1: Audio upload validation** — add `validate_audio_file()` to `/api/audio/upload` | `audio.py` | Small |

**Entry Criteria:** None — can start immediately.
**Exit Criteria:** User can import audio (Ctrl+I works), transcribe it (Transcribe panel has UI), and transcriptions survive restart.

### Phase B: High-Priority Functional Gaps

**Goal:** Complete all functional features in the core workflow.

| # | Item | Files | Effort |
|---|------|-------|--------|
| B.1 | **H-2 + H-3: Library upload and drag-drop** | `library.py`, `LibraryView.xaml.cs` | Medium |
| B.2 | **H-4: Quick Clone API alignment** | `VoiceQuickCloneViewModel.cs`, `BackendClient.cs` | Small |
| B.3 | **H-5: Transcript edit persistence** | `text_speech_editor.py` or `transcribe.py`, `TranscriptionRepository` | Small |
| B.4 | **H-6: WhisperX decision** — remove from dropdown (defer engine to TD register) | `TranscribeViewModel.cs`, `TECH_DEBT_REGISTER.md` | Small |
| B.5 | **H-7: Recording implementation** — NAudio mic capture to file | `PlaybackOperationsHandler.cs`, new recording service | Large |

**Entry Criteria:** Phase A complete (TranscriptionRepository available for B.3).
**Exit Criteria:** Library accepts uploads; Quick Clone works; transcript edits persist; record button captures audio.

### Phase C: Cross-Workflow Integration

**Goal:** Connect workflow phases for seamless user experience.

| # | Item | Files | Effort |
|---|------|-------|--------|
| C.1 | **X-1: Import → Library refresh** | `FileOperationsHandler.cs`, `LibraryViewModel.cs`, EventAggregator | Medium |
| C.2 | **X-4 + X-5: Context actions** — "Use as Clone Reference"; auto-select profile after clone | `LibraryView`, `VoiceCloningWizardViewModel`, `VoiceSynthesisViewModel` | Medium |
| C.3 | **X-6: Synthesis → Timeline** — "Add to Timeline" button | `VoiceSynthesisViewModel`, `TimelineViewModel` | Medium |
| C.4 | **M-1 + X-3: Transcript in Timeline** — subtitle track with segment overlay | `TimelineView.xaml`, `TimelineViewModel.cs` | Large |

**Entry Criteria:** Phase A and B complete (persistence, upload endpoints available).
**Exit Criteria:** Audio flows seamlessly between panels without manual re-navigation.

### Phase D: Quality and Polish

**Goal:** Robustness, maintainability, and polish.

| # | Item | Files | Effort |
|---|------|-------|--------|
| D.1 | **M-2: Profile reference audio consolidation** | `voice.py` | Small |
| D.2 | **M-3: Wizard async synchronization** | `voice_cloning_wizard.py` | Small |
| D.3 | **M-4: Playback service consolidation** | `AudioPlayerService`, `AudioPlaybackService` | Medium |
| D.4 | **M-5: Loop playback** | `AudioPlayerService`, `PlaybackOperationsHandler` | Small |
| D.5 | **M-6: Engine capability manifests** | `engines/*.json` | Small |
| D.6 | **M-7: Multi-reference documentation/warning** | Wizard UI, engine docs | Small |
| D.7 | **L-1 through L-5: Cleanup, docs, model UX** | Various | Small each |

**Entry Criteria:** Phase C complete.
**Exit Criteria:** No silent failures; documented behaviors; temp files managed; formats documented.

---

## 8. Dependency Map

```
Phase A (Critical):
  C-1 (Fix Import) ─────────────────────→ X-1 (Import → Library) [Phase C]
  C-2 (Transcribe UI) ──→ C-3 (Transcribe DB) ──→ H-5 (Edit Save) [Phase B]
                                                ──→ M-1 (Timeline Transcript) [Phase C]
  H-1 (Upload Validation) ──→ H-2 (Library Upload) ──→ H-3 (Drag-Drop) [Phase B]

Phase B (High):
  H-2 (Library Upload) ──→ X-1 (Import → Library) [Phase C]
  H-5 (Edit Save) depends on C-3 (TranscriptionRepository)
  H-7 (Recording) is independent

Phase C (Integration):
  X-1 depends on C-1, H-2
  X-4/X-5 (Context actions) depend on working Clone + Library
  X-6 (Synthesis → Timeline) is semi-independent
  M-1/X-3 (Transcript in Timeline) depends on C-3

Phase D (Quality):
  All items are independent of each other
  M-4 (Playback consolidation) is standalone
  M-5 (Loop) is standalone
```

---

## 9. Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| TranscribeView XAML complexity introduces compiler issues | HIGH | Medium | Follow XAML Change Protocol; use UserControl extraction; incremental build after each section |
| TranscriptionRepository schema change affects existing data | MEDIUM | Low | Migration is idempotent (`CREATE TABLE IF NOT EXISTS`); test with fresh + existing DB |
| Quick Clone API change breaks existing callers | HIGH | Medium | Add backward-compatible parameter handling; test both old and new signatures |
| Recording requires microphone capability in app manifest | MEDIUM | Low | Add `microphone` device capability to Package.appxmanifest; handle permission denial |
| WhisperX removal disappoints users expecting diarization | LOW | Low | Document as "coming soon" in tooltip; add tech debt entry with timeline |
| Timeline transcript overlay is architecturally complex | MEDIUM | Medium | Start with simple text overlay; defer rich subtitle editing to later release |
| Playback service consolidation may break existing consumers | MEDIUM | Medium | Map all current consumers before consolidation; adapter pattern for transition |

---

## 10. Success Criteria

### End-to-End Workflow Test

A user performing the following sequence should succeed without errors or dead ends:

1. **Import**: File → Import Audio → audio file is uploaded and visible in Library panel
2. **Clone**: Right-click audio → "Use as Clone Reference" → Wizard opens with audio pre-loaded → complete wizard → voice profile created
3. **Synthesize**: After wizard, navigate to Synthesis panel → new profile is selectable → enter text → synthesize → audio plays
4. **Add to Timeline**: Click "Add to Timeline" on synthesized audio → clip appears at playhead
5. **Transcribe**: Select audio clip → open Transcribe panel → select engine → transcribe → text appears with timestamps
6. **Edit Transcript**: Open TextSpeechEditor → edit transcript → save → changes persist across restart
7. **Playback**: Use toolbar transport controls → play/pause/stop work → timeline scrubbing with preview works
8. **Record**: Click record → microphone captures audio → recording saved and available for use

### Quality Gates

- [ ] `MainWindow.ImportAudioFile()` delegates to backend upload (C-1)
- [ ] TranscribeView has functional UI with engine selector, language, text display (C-2)
- [ ] Transcriptions survive backend restart (C-3)
- [ ] `/api/audio/upload` validates files before saving (H-1)
- [ ] Library accepts file uploads via API and drag-drop (H-2, H-3)
- [ ] Quick Clone completes without API error (H-4)
- [ ] Edited transcripts can be saved (H-5)
- [ ] Record button captures microphone audio (H-7)
- [ ] No silent failures in any workflow step
- [ ] Build succeeds: `dotnet build VoiceStudio.sln -c Debug -p:Platform=x64`
- [ ] Python tests pass: `python -m pytest tests`

---

## Appendix A: Complete File Inventory

### Files Touched by Audio Import

| File | Role |
|------|------|
| `src/VoiceStudio.App/MainWindow.xaml.cs` | Import entry point (BROKEN) |
| `src/VoiceStudio.App/Commands/FileOperationsHandler.cs` | Working import flow |
| `src/VoiceStudio.App/Services/BackendClient.cs` | HTTP upload client |
| `src/VoiceStudio.App/ViewModels/LibraryViewModel.cs` | Library management |
| `src/VoiceStudio.App/Views/Panels/LibraryView.xaml.cs` | Drag-drop (internal only) |
| `backend/api/routes/audio.py` | Upload endpoint |
| `backend/api/routes/projects.py` | Project audio save |
| `backend/core/security/file_validation.py` | Audio validation |
| `backend/services/AudioArtifactRegistry.py` | Content-addressed cache |
| `backend/services/ProjectStoreService.py` | Project file storage |

### Files Touched by Voice Cloning

| File | Role |
|------|------|
| `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs` | Wizard UI logic |
| `src/VoiceStudio.App/ViewModels/VoiceQuickCloneViewModel.cs` | Quick clone logic |
| `src/VoiceStudio.App/Views/Panels/VoiceSynthesisViewModel.cs` | Synthesis with profiles |
| `backend/api/routes/voice_cloning_wizard.py` | Wizard endpoints |
| `backend/api/routes/voice.py` | Clone + synthesize endpoints |
| `backend/api/routes/profiles.py` | Profile CRUD |
| `app/core/engines/xtts_engine.py` | XTTS clone implementation |
| `app/core/engines/chatterbox_engine.py` | Chatterbox clone |
| `app/core/engines/openvoice_engine.py` | OpenVoice clone |
| `app/core/engines/tortoise_engine.py` | Tortoise clone |
| `app/core/engines/router.py` | Engine routing |
| `backend/services/engine_service.py` | Engine orchestration |

### Files Touched by Transcription

| File | Role |
|------|------|
| `src/VoiceStudio.App/Views/Panels/TranscribeView.xaml` | UI (STUB) |
| `src/VoiceStudio.App/Views/Panels/TranscribeViewModel.cs` | ViewModel (complete) |
| `src/VoiceStudio.App/ViewModels/TextBasedSpeechEditorViewModel.cs` | Transcript editor |
| `src/VoiceStudio.App/Core/Models/Transcription.cs` | C# models |
| `backend/api/routes/transcribe.py` | Transcription endpoint |
| `backend/api/routes/text_speech_editor.py` | Editor API |
| `backend/data/migrations/v001_core_persistence_tables.py` | DB migration (unused) |
| `app/core/engines/whisper_engine.py` | Whisper STT |
| `app/core/engines/whisper_cpp_engine.py` | WhisperCPP STT |
| `app/core/engines/vosk_engine.py` | Vosk STT |

### Files Touched by Audio Playback

| File | Role |
|------|------|
| `src/VoiceStudio.App/Services/AudioPlayerService.cs` | Primary player (NAudio) |
| `src/VoiceStudio.App/Services/StreamingAudioPlayer.cs` | WebSocket streaming |
| `src/VoiceStudio.App/Services/AudioPlaybackService.cs` | Alternative player |
| `src/VoiceStudio.App/Commands/PlaybackOperationsHandler.cs` | Command handler |
| `src/VoiceStudio.App/Services/KeyboardShortcutService.cs` | Keyboard shortcuts |
| `src/VoiceStudio.App/Controls/CustomizableToolbar.xaml.cs` | Transport buttons |
| `src/VoiceStudio.App/MainWindow.xaml.cs` | Global play/pause/stop |
| `src/VoiceStudio.App/Views/Panels/TimelineViewModel.cs` | Timeline playback |
| `backend/api/routes/voice.py` | WebSocket streaming endpoint |

---

*End of audit. This document is peer-reviewable and traceable to specific files, line numbers, and code paths.*
