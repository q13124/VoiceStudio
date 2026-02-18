# Phase 3 Audio Effects Inventory and Prioritization

## Objective

Inventory existing audio effect implementations and prioritize migration order for
Phase 3 pluginization work.

## Sources Audited

- `backend/voice/effects/`
- `app/core/audio/`
- `backend/api/routes/voice_effects.py`

## Effect Candidate Matrix

| Effect | Primary Source | Dependencies | Complexity | Self-Containment | User Value | Migration Priority |
|---|---|---|---|---|---|---|
| Normalize (Peak/LUFS) | `app/core/audio/post_fx.py`, `app/core/audio/lufs_meter.py` | `numpy`, optional `pyloudnorm` | Low | High | High | P1 |
| Compressor | `backend/voice/effects/compressor.py` | `numpy` | Medium | High | High | P2 |
| Reverb | `backend/voice/effects/reverb.py` | `numpy` | Medium-High | High | High | P3 |
| Parametric EQ | `backend/voice/effects/equalizer.py` | `numpy` | Medium | High | Medium-High | P4 |
| Noise Reduction | `backend/voice/effects/noise.py` | `numpy` (FFT spectral path) | High | Medium | Medium-High | P5 |
| Pitch Shift | `backend/voice/effects/pitch.py` | `numpy` | Medium | High | Medium | P6 |

## Scoring Method

Each effect is scored against:

- **Simplicity** (1-5): algorithm and dependency complexity
- **Independence** (1-5): coupling to unrelated systems
- **User Value** (1-5): practical frequency/impact

Weighted total:

- Simplicity: 35%
- Independence: 35%
- User Value: 30%

## Prioritization Rationale

1. **Normalize** first to prove end-to-end plugin path with minimal algorithmic risk.
2. **Compressor** next to validate stateful parameterized DSP behavior.
3. **Reverb** third to validate heavier DSP with more tuning parameters.
4. **EQ** after initial pattern is hardened.
5. **Noise reduction** deferred due to spectral complexity and higher regression risk.

## Migration Constraints

- Keep DSP logic extracted from existing modules to avoid behavior drift.
- Build plugin wrappers around stable processing contracts.
- Add regression tests comparing migrated plugin output against original module
  output using float-tolerant array comparisons.

## Acceptance Criteria for Inventory Task

- Candidate list documented with source files and dependencies.
- Prioritized order established with explicit rationale.
- Week 1 migrations aligned to P1-P3 effects (Normalize, Compressor, Reverb).
