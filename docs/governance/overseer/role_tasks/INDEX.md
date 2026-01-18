# VoiceStudio — Role Task Index (next actions)

This folder provides **role-specific, next-action task lists** aligned to the gated recovery model and the architecture blueprints.

## Canonical references (read first)

- **Status source of truth**: `Recovery Plan/QUALITY_LEDGER.md`
- **Execution plan / roadmap (gate-driven)**: `docs/governance/overseer/PROJECT_BREAKDOWN_AND_EXECUTION_PLAN.md`
- **Working architecture notes**: `openmemory.md`
- **Role prompts + direction (7 roles)**: `docs/governance/overseer/ALL_ROLE_PROMPTS.md`
- **Architecture blueprints (external)**
  - `C:\Users\Tyler\Downloads\VoiceStudio – Architecture Blueprint.pdf`
  - `C:\Users\Tyler\Downloads\VoiceStudio Project Architecture and Dependency Guide.pdf`

## Shared invariants (do not drift)

- **Local-first / offline-first**: default flows must run without cloud dependency; online engines are optional.
- **Artifact + models layout**:
  - Default model root: `E:\VoiceStudio\models` (set by `backend/api/main.py` unless overridden)
  - Expected subfolders: `hf_cache/`, `xtts/`, `piper/`, `whisper/`, `checkpoints/`
- **Gate C artifact**: **unpackaged self-contained apphost EXE** (installer distribution; MSIX not used).
- **No placeholders**: replace stubs with real behavior (RuleGuard must remain green).

## Role task lists (start here)

- **Build & Tooling Engineer**: `BUILD_TOOLING_ENGINEER.md`
- **Release Engineer**: `RELEASE_ENGINEER.md`
- **UI Engineer**: `UI_ENGINEER.md`
- **Engine Engineer**: `ENGINE_ENGINEER.md`
- **Core Platform Engineer**: `CORE_PLATFORM_ENGINEER.md`
- **System Architect**: `SYSTEM_ARCHITECT.md`
- **Overseer**: `OVERSEER.md`
