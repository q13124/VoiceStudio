# VoiceStudio Bounded Contexts

**Task 3.1.1: Domain-Driven Design Bounded Context Mapping**

This document defines the bounded contexts in VoiceStudio, their responsibilities, and how they interact.

---

## Overview

VoiceStudio follows Domain-Driven Design (DDD) principles with clearly defined bounded contexts. Each context owns its domain model and exposes well-defined interfaces to other contexts.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VoiceStudio System                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   Voice     │   │   Project   │   │   Engine    │   │   Audio     │     │
│  │   Context   │◄─►│   Context   │◄─►│   Context   │◄─►│   Context   │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│         │                 │                 │                 │             │
│         └─────────────────┼─────────────────┼─────────────────┘             │
│                           │                 │                               │
│                    ┌──────▼─────┐    ┌──────▼─────┐                         │
│                    │  Pipeline  │    │  Plugin    │                         │
│                    │  Context   │    │  Context   │                         │
│                    └────────────┘    └────────────┘                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Voice Context

**Purpose:** Manages voice profiles, cloning, and voice identity.

### Aggregate Roots
- **VoiceProfile** - A voice identity with trained model data

### Entities
- VoiceTraining - Training job for voice model
- VoiceSample - Reference audio sample for cloning

### Value Objects
- VoiceSettings - Pitch, speed, emotion parameters
- AudioFormat - Sample rate, channels, bit depth

### Domain Events
- `VoiceProfileCreated`
- `VoiceTrainingCompleted`
- `VoiceCloneRequested`

### Repository
- `IVoiceProfileRepository` → `backend/data/repositories/voice_profile_repository.py`

### External Dependencies
- Engine Context (for synthesis)
- Audio Context (for processing)

---

## 2. Project Context

**Purpose:** Manages projects, tracks, and timeline editing.

### Aggregate Roots
- **Project** - A complete voice production project

### Entities
- Track - An audio track within a project
- Clip - An audio clip on a track
- Marker - Timeline marker for navigation

### Value Objects
- TimeRange - Start/end time span
- ProjectSettings - Export and playback configuration

### Domain Events
- `ProjectCreated`
- `TrackAdded`
- `ClipMoved`
- `ProjectExported`

### Repository
- `IProjectRepository` → `backend/data/repositories/project_repository.py`

### External Dependencies
- Voice Context (for voice selection)
- Audio Context (for clip audio data)

---

## 3. Engine Context

**Purpose:** Manages AI engines for synthesis, transcription, and processing.

### Aggregate Roots
- **Engine** - An AI engine instance (XTTS, RVC, Whisper, etc.)

### Entities
- EngineConfiguration - Engine-specific settings
- ModelFile - Trained model data

### Value Objects
- EngineCapability - What an engine can do
- EngineStatus - Ready, loading, error states
- QualityPreset - Quality/speed tradeoff setting

### Domain Events
- `EngineLoaded`
- `EngineError`
- `SynthesisCompleted`
- `TranscriptionCompleted`

### Services
- `IEngineService` → `backend/services/engine_service.py`
- `EnginePool` → `backend/services/engine_pool.py`

### External Dependencies
- Audio Context (for input/output audio)
- Plugin Context (for plugin engines)

---

## 4. Audio Context

**Purpose:** Manages audio files, processing, and format conversion.

### Aggregate Roots
- **AudioClip** - An audio file with metadata

### Entities
- AudioProcessingJob - Async audio processing task
- WaveformData - Cached waveform visualization

### Value Objects
- AudioFormat - wav, mp3, flac, etc.
- AudioSettings - Sample rate, channels, bit depth
- AudioDuration - Length in samples and seconds

### Domain Events
- `AudioUploaded`
- `AudioProcessed`
- `AudioExported`

### Services
- `IAudioProcessingService` → `backend/services/audio_processing.py`
- `ArtifactRefCounter` → `backend/services/artifact_ref_counter.py`

### External Dependencies
- Engine Context (for AI processing)

---

## 5. Pipeline Context

**Purpose:** Orchestrates multi-step AI workflows (STT→LLM→TTS).

### Aggregate Roots
- **PipelineSession** - An active pipeline execution

### Entities
- PipelineStep - A step in the pipeline
- ConversationMessage - Chat message in S2S session

### Value Objects
- PipelineConfig - Pipeline configuration
- MessageRole - user/assistant/system

### Domain Events
- `PipelineStarted`
- `PipelineStepCompleted`
- `ConversationTurnCompleted`

### Services
- `PipelineOrchestrator` → `app/core/pipeline/orchestrator.py`
- `LLMAdapter` → `app/core/engines/llm_interface.py`

### External Dependencies
- Engine Context (for STT/TTS engines)
- Voice Context (for voice selection)

---

## 6. Plugin Context

**Purpose:** Manages plugin lifecycle, discovery, and hot-reloading.

### Aggregate Roots
- **Plugin** - An installed plugin

### Entities
- PluginManifest - Plugin metadata and requirements
- PluginSettings - User configuration

### Value Objects
- PluginVersion - Semantic version
- PluginDependency - Required plugin/version

### Domain Events
- `PluginInstalled`
- `PluginActivated`
- `PluginDeactivated`
- `PluginUpdated`

### Services
- `PluginService` → `backend/services/plugin_service.py`

### External Dependencies
- Engine Context (plugin engines register here)

---

## Context Mapping

### Relationships

| Upstream Context | Downstream Context | Relationship Type |
|-----------------|-------------------|------------------|
| Voice           | Project           | Customer-Supplier |
| Engine          | Voice             | Customer-Supplier |
| Engine          | Audio             | Customer-Supplier |
| Audio           | Project           | Shared Kernel    |
| Plugin          | Engine            | Open Host Service |
| Pipeline        | Engine            | Customer-Supplier |

### Anti-Corruption Layers

1. **API Layer → Domain**
   - FastAPI routes translate HTTP to domain commands
   - DTOs prevent domain model leakage
   - Location: `backend/api/routes/`

2. **Engine Layer → Domain**
   - EngineService abstracts raw engine access
   - Provides stable interface for engine evolution
   - Location: `backend/services/engine_service.py`

3. **Plugin → Core**
   - PluginBase defines contract
   - Sandboxing prevents plugin interference
   - Location: `backend/services/plugin_service.py`

---

## Integration Patterns

### Event-Driven Integration

Contexts communicate via domain events published through an event bus:

```python
# Example: Voice synthesis flow
1. Voice Context: VoiceCloneRequested event
2. Engine Context: Receives event, performs synthesis
3. Engine Context: SynthesisCompleted event
4. Audio Context: Receives event, stores audio
5. Voice Context: Updates profile with new sample
```

### Synchronous Integration

For real-time operations, contexts expose service interfaces:

```python
# Direct service call for synthesis
engine_service = get_engine_service()
result = engine_service.synthesize(
    engine_id="xtts_v2",
    text="Hello world",
    voice_id="user-voice-1"
)
```

---

## Directory Mapping

| Context | Primary Location | Domain Model |
|---------|-----------------|--------------|
| Voice | `backend/voice/` | `backend/domain/entities/voice_profile.py` |
| Project | `backend/services/` | `backend/domain/entities/project.py` |
| Engine | `backend/services/engine_*.py` | `app/core/engines/` |
| Audio | `backend/services/audio_*.py` | `backend/domain/entities/audio_clip.py` |
| Pipeline | `app/core/pipeline/` | `app/core/supervisor/` |
| Plugin | `backend/plugins/` | `backend/services/plugin_service.py` |

---

## Ubiquitous Language

### Voice Context
- **Voice Profile**: A stored voice identity with trained model
- **Clone**: Create a new voice from reference audio
- **Reference Audio**: Sample audio used for voice cloning

### Project Context
- **Track**: A horizontal lane in the timeline for clips
- **Clip**: A piece of audio placed on a track
- **Timeline**: The main editing interface showing tracks over time

### Engine Context
- **Engine**: An AI model that performs synthesis/processing
- **Synthesize**: Generate speech from text
- **Transcribe**: Convert speech to text

### Audio Context
- **Artifact**: A generated audio file
- **Waveform**: Visual representation of audio
- **Format**: The encoding (WAV, MP3, etc.)

---

## Context Evolution Guidelines

1. **Adding New Features**
   - Determine which context owns the feature
   - Add entities/events to that context
   - Expose via context's public interface

2. **Cross-Context Features**
   - Identify primary owning context
   - Use events for async communication
   - Use service interfaces for sync communication

3. **Refactoring Contexts**
   - Never break public interfaces without versioning
   - Deprecate old interfaces before removal
   - Document changes in ADRs
