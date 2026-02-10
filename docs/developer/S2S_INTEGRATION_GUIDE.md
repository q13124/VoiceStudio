# Speech-to-Speech (S2S) Integration Guide

## Overview

VoiceStudio supports end-to-end speech-to-speech models that convert audio directly to audio without intermediate text representation. These models preserve tone, emotion, and speaker identity.

## Supported Providers

| Provider | Type | Latency | Cost | Offline |
|----------|------|---------|------|---------|
| OpenAI Realtime | Cloud | < 500ms | High | No |
| Gemini Live | Cloud | < 500ms | Medium | No |
| Cascade Fallback | Local | 600-2000ms | Free | Yes |

## Architecture

```
User Audio → [S2S Provider] → AI Audio Response
                    ↕
            [WebSocket Connection]
                    ↕
           [Audio Token Stream]
```

## Token Ceiling Strategy

S2S APIs charge for context accumulation -- costs increase exponentially with conversation length. VoiceStudio implements a "Token Ceiling" that automatically switches to the cheaper cascade pipeline after a threshold:

- **Soft ceiling** (50K tokens): Warning notification
- **Hard ceiling** (100K tokens): Auto-switch to cascade
- **Time limit** (15 minutes): Auto-switch to cascade
- **Cost limit** ($1.00): Auto-switch to cascade

## Configuration

```python
from app.core.engines.s2s_protocol import S2SConfig

config = S2SConfig(
    model="gpt-4o-realtime-preview",
    voice="alloy",
    language="en",
    token_ceiling=100000,
    enable_interruption=True,
)
```

## Environment Variables

- `OPENAI_API_KEY` -- Required for OpenAI Realtime
- `GOOGLE_API_KEY` -- Required for Gemini Live

## Key Files

| File | Purpose |
|------|---------|
| `app/core/engines/s2s_protocol.py` | S2S provider protocol |
| `app/core/engines/openai_realtime_engine.py` | OpenAI Realtime adapter |
| `app/core/engines/gemini_live_engine.py` | Gemini Live adapter |
| `app/core/infrastructure/s2s_connection.py` | WebSocket management |
| `app/core/pipeline/token_ceiling.py` | Cost management |
| `app/core/pipeline/cost_tracker.py` | Usage analytics |
