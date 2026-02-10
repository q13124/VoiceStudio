# ADR-021: Voice AI Pipeline Architecture

## Status

**Accepted** - 2026-02-10

## Context

VoiceStudio implements a Voice AI Pipeline that enables:

1. **Speech-to-Text (STT)** → **LLM Processing** → **Text-to-Speech (TTS)** flow
2. Real-time Speech-to-Speech (S2S) conversational AI
3. Integration with multiple providers (OpenAI, Gemini, local models)

The pipeline needs a unified architecture that:
- Supports multiple provider backends
- Handles streaming for real-time interactions
- Maintains graceful degradation when providers are unavailable
- Integrates with the existing engine layer

## Options Considered

### Option A: Monolithic Pipeline

Single service handling all pipeline stages.

- **Pros**: Simple implementation, easy to reason about
- **Cons**: Hard to swap providers, no parallel processing, single point of failure

### Option B: Microservices Pipeline

Each stage as a separate microservice.

- **Pros**: Independent scaling, provider isolation
- **Cons**: Overhead for desktop app, complex coordination

### Option C: Modular Pipeline with Provider Abstraction

Unified pipeline service with pluggable provider backends.

- **Pros**: Clean abstraction, provider flexibility, desktop-friendly
- **Cons**: Requires careful interface design

## Decision

Adopt **Option C: Modular Pipeline with Provider Abstraction**.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PipelineOrchestrator                 │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │   STT   │ -> │   LLM   │ -> │   TTS   │             │
│  │ Provider│    │ Provider│    │ Provider│             │
│  └─────────┘    └─────────┘    └─────────┘             │
│       │              │              │                   │
│       v              v              v                   │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │ Whisper │    │  GPT-4  │    │  XTTS   │             │
│  │ DeepSpeech│  │ Gemini  │    │  Piper  │             │
│  │ Vosk    │    │ Ollama  │    │  Coqui  │             │
│  └─────────┘    └─────────┘    └─────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Components

1. **PipelineOrchestrator** (`backend/services/pipeline_orchestrator.py`)
   - Coordinates STT → LLM → TTS flow
   - Handles streaming for real-time mode
   - Manages provider selection and fallback

2. **Provider Abstractions**
   - `ISttProvider`: Speech-to-text interface
   - `ILlmProvider`: Language model interface  
   - `ITtsProvider`: Text-to-speech interface

3. **S2S Integration** (`backend/services/s2s_integration.py`)
   - OpenAI Realtime API adapter
   - Gemini Live adapter
   - WebSocket streaming for real-time voice

4. **Pipeline API Routes** (`backend/api/routes/pipeline.py`)
   - `/api/pipeline/process` - Full pipeline processing
   - `/api/pipeline/providers` - Available providers
   - `/api/pipeline/stream` - WebSocket streaming

### Graceful Degradation

1. **Provider Unavailable**: Fall back to next available provider
2. **Network Failure**: Use local models (Whisper, Ollama, Piper)
3. **No Audio**: Return text-only response
4. **Timeout**: Return partial results with status

## Consequences

### Positive

- Flexible provider selection per stage
- Local-first with cloud enhancement
- Streaming support for real-time conversations
- Clean separation between orchestration and providers

### Negative

- Interface complexity for multiple providers
- Testing matrix grows with provider count
- Version compatibility across providers

### Implementation Evidence

- Orchestrator: `backend/services/pipeline_orchestrator.py`
- S2S Integration: `backend/services/s2s_integration.py`
- API Routes: `backend/api/routes/pipeline.py`
- ViewModel: `src/VoiceStudio.App/ViewModels/PipelineConversationViewModel.cs`

## Related ADRs

- ADR-007: IPC Boundary
- ADR-017: Engine Subprocess Model
- ADR-019: Orchestration in Python
