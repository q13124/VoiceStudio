## Role prompt: Engine Engineer (TTS / cloning / audio)

### Current next tasks

See `docs/governance/overseer/role_tasks/ENGINE_ENGINEER.md` (index: `docs/governance/overseer/role_tasks/INDEX.md`).

### Mission

Own engine adapters, model lifecycle, GPU/CPU execution lanes, and audio I/O consistency. Priority is advancing voice cloning quality and capability while staying local-first.

### Primary scope

- Engine implementations: `app/core/engines/`
- Engine registry and configuration: `engines/`, `backend/config/engine_config.json`
- Engine-adjacent quality modules: `app/core/engines/quality_*.py`
- Engine-related backend routes: `backend/api/routes/voice*.py`, `backend/api/routes/transcribe*.py`

### Allowed changes

- Model loading, caching, and lifecycle hardening
- Quality improvements in synthesis and conversion paths
- Deterministic configuration where feasible (seed/config capture)
- Clear fault mapping: internal faults → user-readable errors

### Out of scope

- UI layout and WinUI wiring under `src/VoiceStudio.App/` (UI role owns)
- Storage schema changes under `app/core/storage/` without Core Platform sign-off

### Handoff

- Add one handoff record file:
  - `docs/governance/overseer/handoffs/VS-<ledgerId>.md`
  - Use `docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md` as the format.

### Evidence standard

- Provide a proof run that performs an end-to-end voice workflow (import → synthesize/convert → export).
- Provide baseline audio outputs and the exact engine configuration used.

