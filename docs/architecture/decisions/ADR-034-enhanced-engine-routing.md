# ADR-034: Enhanced Engine Routing

## Status
Accepted

## Date
2026-02-11

## Context

The existing `EngineRouter` provided basic engine selection and quality-based routing. However, it lacked:

1. **Language-aware routing**: No automatic selection based on input language
2. **A/B testing**: No framework for comparing engine performance
3. **Load-based selection**: No consideration of engine load when selecting

These gaps meant:
- Users had to manually select engines for non-English content
- No data-driven engine comparison
- Potential bottlenecks when one engine was overloaded

## Decision

Enhance `EngineRouter` with three new capabilities:

### 1. Language Detection and Routing

```python
def select_engine(
    self,
    task_type: str = "tts",
    text: Optional[str] = None,
    language: Optional[str] = None,
    quality_mode: str = "balanced",
    ...
) -> Optional[EngineProtocol]:
```

- Automatic language detection using `langdetect` library
- Language-to-engine mapping in `config/engines.config.yaml`
- Fallback to default engine if no mapping exists

Configuration example:
```yaml
routing_policy:
  language_mapping:
    en: xtts_v2
    zh: gpt_sovits
    ja: gpt_sovits
```

### 2. A/B Testing Framework

```python
ab_testing:
  enabled: true
  experiments:
    - id: tts_quality_compare
      engines: [xtts_v2, openvoice]
      weights: [0.5, 0.5]
      active: true
      metrics: [mos_score, latency_ms]
```

Features:
- Weighted random selection between engine variants
- Experiment tracking with `ABTestResult` dataclass
- Integration with existing metrics collection
- Enable/disable via feature flag

### 3. Load-Based Selection

```python
def _get_lower_load_alternative(
    self,
    current_engine_id: str,
    task_type: str
) -> Optional[str]:
```

- Query engine load statistics from performance metrics
- Switch to alternative engine if load is 30%+ lower
- Respects fallback chain for alternatives

## Unified Selection API

The new `select_engine()` method provides a single entry point:

```python
engine = router.select_engine(
    task_type="tts",
    text="Hello, world",  # For language detection
    quality_mode="balanced",
    ab_test_group=None,  # Optional forced group
    prefer_low_load=True
)
```

Selection order:
1. A/B test selection (if enabled and active)
2. Language-based selection (if text or language provided)
3. Quality tier selection (if quality_mode specified)
4. Load-based adjustment (if prefer_low_load=True)
5. Default engine fallback

## Consequences

### Positive
- Automatic optimal engine selection for multilingual content
- Data-driven engine comparison via A/B testing
- Better resource utilization with load balancing
- Single unified API for engine selection
- Configurable via YAML without code changes

### Negative
- Additional complexity in routing logic
- `langdetect` dependency (optional, degrades gracefully)
- A/B testing requires metric collection infrastructure

### Performance Impact

- Language detection: ~1-5ms per call
- A/B selection: <1ms (simple weighted random)
- Load checking: <1ms (reads cached metrics)

## Alternatives Considered

### Option A: External Routing Service
Rejected: Over-engineered for desktop application.

### Option B: User-Selected Engine Only
Rejected: Poor UX for multilingual users.

### Option C: Static Language Configuration
Rejected: Less flexible than runtime detection.

## Related ADRs

- ADR-017: Engine subprocess model
- ADR-019: Python backend orchestration
- ADR-033: Configuration consolidation

## Implementation Notes

Files modified:
- `app/core/engines/router.py` - Enhanced with new methods
- `config/engines.config.yaml` - Language mappings and A/B config

New dataclasses:
- `ABTestResult` - A/B test selection result
- `EngineLoadStats` - Engine load statistics

Dependencies:
- `langdetect` (optional, for language detection)
