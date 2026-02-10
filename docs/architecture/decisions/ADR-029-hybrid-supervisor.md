# ADR-029: Hybrid Supervisor Architecture

## Status

Accepted

## Date

2026-02-09

## Context

VoiceStudio needs to support both real-time conversational AI (low latency) and complex task execution (tool calling, reasoning) within the same conversation. These two capabilities require fundamentally different pipeline architectures:

- **S2S (Speech-to-Speech)**: Sub-500ms latency, preserves emotion, but limited tool calling and expensive for long sessions
- **Cascade (STT → LLM → TTS)**: 600-2000ms latency, full tool calling, cheaper, but loses non-verbal cues

Users expect seamless switching between these modes without manual configuration.

## Options Considered

### Option A: S2S Only
Always use S2S. Pros: simplest, lowest latency. Cons: expensive, poor tool calling, no DSP chain integration.

### Option B: Cascade Only
Always use STT → LLM → TTS. Pros: full control, cheapest. Cons: higher latency, loses emotional context.

### Option C: Manual Mode Switch
Let users toggle between modes. Pros: user control. Cons: poor UX, interrupts conversation flow.

### Option D: Hybrid Supervisor (Selected)
Use a lightweight classifier to automatically route between S2S and Cascade based on intent complexity, with context preservation across switches.

## Decision

Implement a Hybrid Supervisor architecture with:

1. **Intent Classifier** (< 50ms) -- Keyword-based + optional LLM classification to determine complexity
2. **State Machine** -- Idle → Analyzing → CasualMode/ReasoningMode → Responding → Idle
3. **Filler Phrases** -- Generated during S2S → Cascade handoffs (1.5-3s delay)
4. **Context Sync** -- Conversation synopsis injected when switching modes
5. **Pragmatic Interruption FSM** -- Distinguishes cooperative interruptions, topic changes, and disfluencies
6. **Token Ceiling** -- Auto-switches to cascade when S2S costs exceed threshold
7. **Half-Cascade Mode** -- S2S audio input + Traditional TTS output for balanced latency/quality

## Consequences

### Positive
- Seamless user experience across conversation types
- Cost optimization via automatic downgrade
- Full tool calling capability when needed
- DSP effects chain accessible via half-cascade/cascade modes
- Extensible to new S2S providers

### Negative
- Additional complexity in routing logic
- Classification errors may route to wrong pipeline
- Context may lose nuance during switches
- Requires maintenance of two parallel processing paths

### Mitigations
- Classifier is conservative (defaults to cascade on uncertainty)
- Context sync preserves conversation synopsis
- Filler phrases maintain conversational flow during handoffs
- Token ceiling prevents runaway costs

## Key Files

- `app/core/supervisor/classifier.py` -- Intent classification
- `app/core/supervisor/state_machine.py` -- State machine
- `app/core/supervisor/router.py` -- Routing logic
- `app/core/supervisor/filler_generator.py` -- Filler phrases
- `app/core/supervisor/context_sync.py` -- Context preservation
- `app/core/supervisor/interruption_fsm.py` -- Interruption handling
- `app/core/supervisor/barge_in.py` -- Barge-in handler
- `app/core/pipeline/half_cascade.py` -- Half-cascade mode
- `app/core/pipeline/token_ceiling.py` -- Cost management
