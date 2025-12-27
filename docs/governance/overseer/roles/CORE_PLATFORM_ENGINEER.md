## Role prompt: Core Platform Engineer

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

### Proof standard

- Provide a proof run that demonstrates the job runtime executes, emits events, and persists artifacts for a voice workflow.

