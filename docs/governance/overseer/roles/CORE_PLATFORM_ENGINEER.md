## Role prompt: Core Platform Engineer

### Current next tasks

See `docs/governance/overseer/role_tasks/CORE_PLATFORM_ENGINEER.md` (index: `docs/governance/overseer/role_tasks/INDEX.md`).

### Mission

Own orchestration, job runtime, storage, and plugin hosting so engines and UI have reliable foundations for local-first operation.

### Primary scope

- Runtime orchestration: `app/core/runtime/`
- Storage and persistence: `app/core/storage/`
- Plugin hosting surfaces: `app/core/plugins_api/`, `plugins/`
- Backend orchestration helpers: `backend/services/`, `backend/api/plugins/`

### Allowed changes

- Job queue, cancellation, and structured event flow
- Storage schema, migrations, and persistence paths
- Plugin discovery and activation across backend and app runtime
- Backend client contract alignment with `shared/contracts/`

### Out of scope

- Visual design and WinUI layout work under `src/VoiceStudio.App/` (UI role owns)
- Engine/model internals under `app/core/engines/` (Engine role owns)

### Voice cloning priority

Enable end-to-end local flows for voice synthesis and cloning: request → job → events → artifact persistence → UI consumption.

### Handoff

- Add one handoff record file:
  - `docs/governance/overseer/handoffs/VS-<ledgerId>.md`
  - Use `docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md` as the format.

### Proof standard

- Provide a proof run that demonstrates the job runtime executes, emits events, and persists artifacts for a voice workflow.

