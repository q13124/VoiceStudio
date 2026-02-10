# Voice AI Pipeline Guide

## Overview

VoiceStudio implements a modular Voice AI pipeline that chains Speech-to-Text (STT), Large Language Model (LLM), and Text-to-Speech (TTS) components. The pipeline supports three modes:

1. **Streaming** -- Low-latency conversational mode with buffer-ahead synthesis
2. **Batch** -- High-quality sequential processing
3. **Half-Cascade** -- S2S audio input + Traditional TTS output

## Architecture

```
Audio Input → [STT Engine] → Text → [LLM Provider] → Response → [TTS Engine] → Audio Output
                                        ↓
                                  [Function Calling]
                                        ↓
                                  [VoiceStudio Services]
```

## Pipeline Components

### STT Engines (app/core/engines/)
- **Whisper** -- Local, high-accuracy transcription
- **whisper.cpp** -- Fast C++ implementation

### LLM Providers (app/core/engines/llm_*)
- **Ollama** (local, preferred) -- `llm_local_adapter.py`
- **LocalAI** (local) -- `llm_local_adapter.py`  
- **OpenAI** (cloud, optional) -- `llm_openai_adapter.py`

### TTS Engines (app/core/engines/)
- **XTTS v2** -- High-quality voice cloning
- **Piper** -- Fast, lightweight synthesis
- **OpenAI TTS** -- Cloud-based synthesis

## Usage

### REST API

```bash
# Process text through the pipeline
POST /api/pipeline/process
{
  "text": "Hello, what can you help me with?",
  "mode": "batch",
  "llm_provider": "ollama"
}
```

### WebSocket (Streaming)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/pipeline/stream');

ws.send(JSON.stringify({
  type: "text",
  content: "Tell me about voice synthesis"
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "token") console.log(data.content);
  if (data.type === "complete") console.log("Done:", data.content);
};
```

### Python

```python
from app.core.pipeline.orchestrator import PipelineOrchestrator, PipelineConfig

config = PipelineConfig(
    llm_provider="ollama",
    tts_engine="xtts_v2",
)
pipeline = PipelineOrchestrator(config)
await pipeline.initialize()

result = await pipeline.process_text("Hello!")
print(result["response"])
```

## Configuration

Pipeline configuration is in `engines/config.json`:

```json
{
  "pipeline": {
    "default_stt": "whisper",
    "default_llm": "ollama",
    "default_tts": "xtts_v2",
    "streaming_buffer_tokens": 10,
    "max_conversation_turns": 50
  }
}
```

## Latency Targets

| Metric | Target | Mode |
|--------|--------|------|
| Time to First Token | < 100ms | Streaming |
| End-to-End | < 600ms | Streaming |
| End-to-End | < 2000ms | Batch |
| P90 Total | < 800ms | Streaming |

## Function Calling

The LLM can invoke VoiceStudio functions:

- `synthesize_voice(text, voice_id)` -- Generate speech
- `list_voices()` -- List available voices
- `list_engines()` -- List available engines
- `get_project_status()` -- Get project info

Register custom functions in `backend/services/llm_function_calling.py`.

## Key Files

| File | Purpose |
|------|---------|
| `app/core/engines/llm_interface.py` | LLM provider protocol |
| `app/core/engines/llm_local_adapter.py` | Ollama/LocalAI adapters |
| `app/core/pipeline/orchestrator.py` | Pipeline orchestrator |
| `app/core/pipeline/streaming_pipeline.py` | Streaming mode |
| `app/core/pipeline/batch_pipeline.py` | Batch mode |
| `app/core/pipeline/metrics.py` | Performance metrics |
| `app/core/pipeline/buffer_ahead.py` | Buffer-ahead TTS |
| `backend/api/routes/pipeline.py` | API endpoints |
| `backend/services/llm_function_calling.py` | Function calling |
