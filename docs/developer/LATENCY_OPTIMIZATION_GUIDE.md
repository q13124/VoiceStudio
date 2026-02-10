# Latency Optimization Guide

## Overview

VoiceStudio targets the following latency SLAs for conversational AI:

| Metric | Target | Current Architecture |
|--------|--------|---------------------|
| STT Time to First Token | < 100ms | Whisper streaming |
| LLM Time to First Token | < 200ms | Ollama local |
| TTS Time to First Byte | < 200ms | Buffer-ahead synthesis |
| E2E Streaming | < 600ms | Full pipeline |
| E2E Batch | < 2000ms | Sequential pipeline |
| S2S Response | < 500ms | OpenAI Realtime/Gemini |
| Supervisor Classification | < 50ms | Keyword heuristics |
| P90 Total | < 800ms | Production target |

## Optimization Strategies

### 1. Buffer-Ahead Synthesis

TTS begins synthesizing before the LLM completes generating:

```
LLM:  [token1][token2][token3][...][complete]
TTS:           [synth sentence 1]  [synth sentence 2]
Play:                   [play 1]        [play 2]
```

Implementation: `app/core/pipeline/buffer_ahead.py`

### 2. Sentence Boundary Detection

The `SentenceDetector` accumulates tokens and flushes on sentence boundaries (`.`, `!`, `?`) to produce natural TTS segments.

### 3. Streaming Pipeline

All three stages operate concurrently:
- STT emits partial transcripts
- LLM starts generating on partial input
- TTS begins on first complete sentence

### 4. Local-First Model Selection

| Component | Local (Preferred) | Cloud (Fallback) |
|-----------|-------------------|------------------|
| STT | Whisper | AssemblyAI |
| LLM | Ollama (llama3.2) | OpenAI GPT-4o-mini |
| TTS | XTTS v2, Piper | OpenAI TTS |
| S2S | N/A | OpenAI Realtime |

### 5. Metrics Collection

Monitor latency via `PipelineMetricsCollector`:

```python
from app.core.pipeline.metrics import get_metrics_collector

collector = get_metrics_collector()
summary = collector.get_summary()
sla = collector.check_sla(target_p90_ms=800.0)
```

## Benchmarking

Run latency benchmarks:

```bash
python -m pytest tests/performance/test_pipeline_latency.py -v
```

Check SLA compliance:

```bash
curl http://localhost:8000/api/pipeline/metrics
```

## Key Files

| File | Purpose |
|------|---------|
| `app/core/pipeline/metrics.py` | Metrics collection |
| `app/core/pipeline/buffer_ahead.py` | Buffer-ahead TTS |
| `app/core/pipeline/streaming_pipeline.py` | Streaming mode |
| `app/core/supervisor/classifier.py` | < 50ms classification |
