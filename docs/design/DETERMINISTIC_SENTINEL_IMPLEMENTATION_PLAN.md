# Deterministic Sentinel Audio Workflow Implementation Plan

> **Version**: 1.0  
> **Author**: Lead/Principal Architect  
> **Date**: 2026-02-13  
> **Status**: Draft for Peer Review  
> **Classification**: Technical Implementation Plan  

---

## 1. High-Level Goal Clarification

### Goal Statement

Implement a deterministic, reproducible audio workflow system that exercises the complete VoiceStudio pipeline (import → storage → synthesis → effects → async jobs → A/B evaluation → diagnostics) using a sentinel voice audio file, producing peer-reviewable proof artifacts per run. This system serves as both a quality gate and a contract verification mechanism between UI and backend layers.

### Assumptions

| ID | Assumption | Risk if Invalid | Mitigation |
|----|------------|-----------------|------------|
| A1 | Backend FastAPI server runs on configurable port (default 8001) | Tests fail to connect | Environment variable override |
| A2 | WinAppDriver 1.2 available for UI automation | UI tests cannot run | Skip UI tests with clear reporting |
| A3 | Voice cloning engines (XTTS, Chatterbox, Tortoise) are installable | Engine tests skip | Engine availability checks in preflight |
| A4 | Sentinel audio file meets quality requirements (16kHz+, clean speech) | Training fails | Provide synthetic fallback fixture |
| A5 | CI runners have GPU access for engine tests | GPU tests skip | CPU-only fallback mode |
| A6 | API contracts between UI and backend are documented | Contract drift undetected | Generate OpenAPI spec on each build |

### Stakeholders

| Role | Responsibility | Review Gate |
|------|---------------|-------------|
| Lead Architect | Overall design, contract definitions | Technical Review |
| Backend Engineer | API implementation, engine integration | Code Review |
| UI Engineer | WinUI panel automation, contract compliance | Code Review |
| QA Engineer | Test automation, CI integration | Test Plan Review |
| DevOps Engineer | CI/CD pipeline, artifact management | Pipeline Review |
| Product Owner | Acceptance criteria approval | Business Review |

### Constraints

- **Technical**: Windows-only UI testing (WinAppDriver), Python 3.9+ backend, .NET 8 frontend
- **Business**: Must not introduce breaking changes to existing workflows
- **Legal**: Sentinel voice files are biometric data—never commit personal voice samples
- **Resource**: CI runners limited to 2-hour job timeout, 16GB RAM, optional GPU

### Scope

**In Scope (MVP - Phases 1-3)**:
- Sentinel runner with deterministic repro packets
- Backend API contract hardening and validation
- UI automation framework with stable AutomationIds
- CI integration with artifact upload on failure
- Health check and preflight validation
- API/UI contract drift detection

**In Scope (Future - Phases 4-6)**:
- Advanced observability with distributed tracing
- Horizontal scalability infrastructure
- Plugin system and external integrations
- ML quality improvement pipeline

**Out of Scope**:
- Third-party connector implementations (Hugging Face, Airtable, etc.)
- Multi-region deployment
- Real-time collaboration features
- Mobile or web client support

---

## 2. System Architecture Design

### Architecture Pattern

**Hybrid Layered + Event-Driven** — The system follows a layered architecture (UI → API → Services → Engines) with event-driven patterns for async operations and real-time updates via WebSocket.

### Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | WinUI 3 / Windows App SDK | Native Windows performance, Fluent Design |
| Backend API | FastAPI (Python 3.9+) | High performance, automatic OpenAPI, async support |
| Engine Layer | Process isolation with IPC | Engine independence, fault isolation, GPU resource management |
| Database | SQLite (local), PostgreSQL (production) | Schema-driven, migration support |
| Message Queue | In-process asyncio (MVP), Redis (scale) | Async job management |
| Testing | pytest (backend), MSTest (frontend), WinAppDriver (UI) | Comprehensive coverage |
| CI/CD | GitHub Actions | Native GitHub integration, artifact support |

### Component Interaction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SENTINEL RUNNER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Preflight   │→│ API Tests   │→│ UI Tests    │→│ Repro Packet Gen    │ │
│  │ Validation  │  │ (Backend)   │  │ (WinApp)    │  │ (Artifacts)         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌─────────────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     WinUI Frontend      │  │  FastAPI Backend │  │  Engine Layer   │
│  ┌───────────────────┐  │  │  ┌─────────────┐ │  │  ┌───────────┐  │
│  │ IBackendClient    │──┼──┼─▶│ API Routes  │ │  │  │ XTTS      │  │
│  │ (HTTP/WebSocket)  │  │  │  │ ┌─────────┐ │ │  │  │ Chatterbox│  │
│  └───────────────────┘  │  │  │ │/v1/...  │ │ │  │  │ Tortoise  │  │
│  ┌───────────────────┐  │  │  │ │/tts     │ │ │  │  └───────────┘  │
│  │ ViewModels        │  │  │  │ │/jobs    │ │ │  │       ▲         │
│  │ (MVVM Pattern)    │  │  │  │ │/upload  │ │ │  │       │         │
│  └───────────────────┘  │  │  │ └─────────┘ │ │  │  IPC Protocol   │
│  ┌───────────────────┐  │  │  │      │      │ │  │       │         │
│  │ Panels (96+)      │  │  │  │      ▼      │ │  │       │         │
│  │ AutomationIds     │  │  │  │ Services    │─┼──┼───────┘         │
│  └───────────────────┘  │  │  └─────────────┘ │  └─────────────────┘
└─────────────────────────┘  └─────────────────┘
```

### System Boundaries

**Internal Components**:
- VoiceStudio.App (WinUI 3 frontend)
- VoiceStudio.Core (contracts, interfaces)
- Backend API (FastAPI)
- Backend Services (business logic)
- Engine Adapters (XTTS, Chatterbox, Tortoise)
- Sentinel Runner (test infrastructure)

**External Integrations**:
- WinAppDriver (UI automation)
- FFmpeg/FFprobe (audio processing)
- PyTorch (ML inference)
- GitHub Actions (CI/CD)

### Integration Points

| System | Protocol | Purpose | Contract Location |
|--------|----------|---------|-------------------|
| UI ↔ Backend | HTTP REST + WebSocket | Control plane, real-time updates | `shared/schemas/*.json` |
| Backend ↔ Engine | Subprocess IPC | Data plane, synthesis execution | `app/core/engines/base.py` |
| Sentinel ↔ Backend | HTTP REST | Test validation | `tests/sentinel/contracts/*.schema.json` |
| CI ↔ Artifacts | GitHub Actions | Proof storage | `.github/workflows/*.yml` |

---

## 3. Detailed Phase Breakdown

### Phase 1: Sentinel Infrastructure (Weeks 1-2)

**Objective**: Establish the deterministic sentinel runner with backend API validation and repro packet generation.

#### Milestones

- [ ] P1.1: Sentinel runner core implementation
- [ ] P1.2: Contract schema definitions
- [ ] P1.3: Repro packet generation
- [ ] P1.4: Local execution verification
- [ ] P1.5: CI workflow integration

#### Time Estimate

2 weeks (10 working days)

#### Team Roles

| Role | Responsibility |
|------|---------------|
| Backend Engineer | Runner implementation, API call matrix |
| DevOps Engineer | CI workflow, artifact upload |
| QA Engineer | Test data preparation, verification |

#### Dependencies

- Backend API endpoints operational
- Synthetic sentinel audio fixture created
- pytest infrastructure available

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API endpoints not stable | Medium | High | Contract-first development, schema validation |
| Flaky async job polling | Medium | Medium | Configurable timeouts, exponential backoff |
| Large artifact size | Low | Low | Compression, selective inclusion |

#### Entry Criteria

- [ ] Backend API running on localhost:8001
- [ ] Health endpoint `/v1/health/metrics` responding
- [ ] Synthetic audio fixture `fixtures/audio/sentinel_16k_mono.wav` committed

#### Exit Criteria

- [ ] Sentinel runner executes all 7 API call matrix steps
- [ ] Repro packet contains all required artifacts
- [ ] CI workflow uploads artifacts on failure
- [ ] Documentation updated with usage instructions

#### Deliverables

1. `scripts/proof_runs/sentinel_audio_workflow.py` - Main runner
2. `tests/sentinel/test_sentinel_audio_workflow.py` - pytest integration
3. `tests/sentinel/contracts/*.schema.json` - Contract schemas
4. `fixtures/audio/sentinel_16k_mono.wav` - Synthetic test audio
5. `.github/workflows/sentinel_backend_smoke.yml` - CI workflow

---

### Phase 2: API Contract Hardening (Weeks 3-4)

**Objective**: Harden API contracts to ensure UI/backend alignment and prevent drift.

#### Milestones

- [ ] P2.1: OpenAPI spec generation and validation
- [ ] P2.2: Contract schema enforcement with Pydantic
- [ ] P2.3: Multipart upload standardization
- [ ] P2.4: Error response standardization
- [ ] P2.5: API versioning implementation

#### Time Estimate

2 weeks (10 working days)

#### Team Roles

| Role | Responsibility |
|------|---------------|
| Backend Engineer | Contract implementation, validation |
| UI Engineer | Contract consumption verification |
| Architect | Schema review and approval |

#### Dependencies

- Phase 1 complete (sentinel runner validates contracts)
- Existing API endpoints documented

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing UI | High | High | Versioned endpoints, parallel deployment |
| Multipart/JSON confusion | Medium | Medium | Clear documentation, validation |
| Schema drift over time | Medium | Medium | CI schema validation gate |

#### Entry Criteria

- [ ] Phase 1 complete with green CI
- [ ] Current API endpoint inventory documented
- [ ] UI endpoint usage mapped

#### Exit Criteria

- [ ] All endpoints have Pydantic request/response models
- [ ] OpenAPI spec generated automatically on build
- [ ] Contract validation tests passing
- [ ] API v1/v2 coexisting where needed
- [ ] StandardResponse envelope applied to all v3 endpoints

#### Deliverables

1. `docs/api/openapi.json` - Generated OpenAPI spec
2. `backend/api/models/` - Pydantic models for all contracts
3. `backend/api/v3/` - Versioned API with StandardResponse
4. `tests/integration/test_api_contracts.py` - Contract validation tests
5. ADR documenting versioning strategy

---

### Phase 3: UI Automation Framework (Weeks 5-7)

**Objective**: Establish UI automation infrastructure with stable AutomationIds and smoke tests.

#### Milestones

- [ ] P3.1: AutomationId audit and standardization
- [ ] P3.2: WinAppDriver integration hardening
- [ ] P3.3: Page Object Model implementation
- [ ] P3.4: Critical workflow automation
- [ ] P3.5: CI nightly workflow integration

#### Time Estimate

3 weeks (15 working days)

#### Team Roles

| Role | Responsibility |
|------|---------------|
| UI Engineer | AutomationId implementation, XAML updates |
| QA Engineer | Test automation, Page Objects |
| DevOps Engineer | Nightly CI workflow |

#### Dependencies

- Phase 2 complete (contracts stable for UI testing)
- WinAppDriver installed on CI runners
- Application build available

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| UI test flakiness | High | Medium | Retry logic, explicit waits, screenshots |
| AutomationId conflicts | Medium | Low | Naming convention, uniqueness validation |
| WinAppDriver compatibility | Low | High | Version pinning, fallback to manual |

#### Entry Criteria

- [ ] Phase 2 complete with contract validation passing
- [ ] Application builds successfully
- [ ] WinAppDriver accessible on test machines

#### Exit Criteria

- [ ] All critical panels have stable AutomationIds
- [ ] 4 smoke workflows automated (Import, Clone, Analyze, Effects)
- [ ] Nightly CI runs with screenshot capture
- [ ] Page Object Model documented
- [ ] Test stability > 95% over 10 runs

#### Deliverables

1. `tests/ui/page_objects/` - Page Object implementations
2. `tests/ui/test_smoke_workflows.py` - Smoke test suite
3. `src/VoiceStudio.App/*/AutomationIds.cs` - Centralized ID definitions
4. `.github/workflows/sentinel_ui_smoke_nightly.yml` - Nightly workflow
5. `docs/testing/UI_AUTOMATION_GUIDE.md` - Usage documentation

---

### Phase 4: Security and Stability (Weeks 8-10)

**Objective**: Address critical security vulnerabilities and stability issues per architectural assessment.

#### Milestones

- [ ] P4.1: Secure credential storage (DPAPI)
- [ ] P4.2: Comprehensive error boundaries
- [ ] P4.3: Enhanced health check endpoints
- [ ] P4.4: Graceful shutdown handling
- [ ] P4.5: Structured logging with correlation IDs

#### Time Estimate

3 weeks (15 working days)

#### Team Roles

| Role | Responsibility |
|------|---------------|
| Backend Engineer | Health checks, shutdown, logging |
| UI Engineer | Error boundaries, error dialogs |
| Security Engineer | Credential storage review |

#### Dependencies

- Phase 3 complete (UI automation validates fixes)
- Sentinel runner validates security improvements

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| DPAPI platform dependency | Low | Medium | Abstraction layer, cross-platform fallback |
| Logging performance impact | Medium | Low | Async logging, sampling |
| Shutdown timeout exceeded | Medium | Medium | Configurable timeouts, force kill fallback |

#### Entry Criteria

- [ ] Phase 3 complete with stable UI automation
- [ ] Current credential storage audited
- [ ] Current error handling patterns documented

#### Exit Criteria

- [ ] All credentials in secure storage (no plaintext in config)
- [ ] No application crashes from unhandled exceptions
- [ ] Health checks report accurate dependency status
- [ ] Graceful shutdown completes within 30 seconds
- [ ] All requests have correlation IDs in logs

#### Deliverables

1. `src/VoiceStudio.Core/Security/SecureConfigurationProvider.cs`
2. `backend/services/health_check_service.py`
3. `backend/middleware/correlation.py` - Enhanced correlation middleware
4. `docs/operations/SECURITY_CONFIGURATION.md`
5. ADR documenting security architecture

---

### Phase 5: Architecture Foundations (Weeks 11-14)

**Objective**: Establish architectural patterns that enable sustainable development velocity.

#### Milestones

- [ ] P5.1: Dependency injection standardization
- [ ] P5.2: API versioning (v1/v2/v3 coexistence)
- [ ] P5.3: Caching layer implementation
- [ ] P5.4: Message queue for async operations
- [ ] P5.5: Database migration system

#### Time Estimate

4 weeks (20 working days)

#### Team Roles

| Role | Responsibility |
|------|---------------|
| Architect | Pattern design, review |
| Backend Engineer | Queue, caching, migrations |
| UI Engineer | DI refactoring |

#### Dependencies

- Phase 4 complete (security foundation stable)
- Database schema documented

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| DI migration breaks functionality | Medium | High | Incremental migration, comprehensive tests |
| Cache invalidation bugs | Medium | Medium | Conservative TTLs, manual invalidation |
| Migration rollback needed | Low | High | Rollback scripts, staging validation |

#### Entry Criteria

- [ ] Phase 4 complete with security improvements verified
- [ ] Current service dependencies mapped
- [ ] Database schema fully documented

#### Exit Criteria

- [ ] All services resolved through DI container
- [ ] API v1/v2/v3 coexisting with version negotiation
- [ ] Cache hit rate > 70% for identified hot paths
- [ ] Async operations using message queue
- [ ] Migrations apply automatically during deployment

#### Deliverables

1. `src/VoiceStudio.Core/DI/` - DI infrastructure
2. `backend/api/v1/`, `backend/api/v2/`, `backend/api/v3/` - Versioned APIs
3. `backend/services/cache_service.py`
4. `backend/services/job_queue_service.py`
5. `backend/data/migrations/` - Alembic migrations
6. ADR for each architectural decision

---

### Phase 6: Scalability and Resilience (Weeks 15-18)

**Objective**: Prepare the system for production scale and implement resilience patterns.

#### Milestones

- [ ] P6.1: Circuit breaker implementation
- [ ] P6.2: Request rate limiting
- [ ] P6.3: Retry logic with exponential backoff
- [ ] P6.4: Request timeout standardization
- [ ] P6.5: Horizontal scalability preparation

#### Time Estimate

4 weeks (20 working days)

#### Team Roles

| Role | Responsibility |
|------|---------------|
| Backend Engineer | Circuit breakers, rate limiting, retries |
| DevOps Engineer | Load balancing, scaling |
| Architect | Resilience pattern review |

#### Dependencies

- Phase 5 complete (architecture foundations in place)
- Load testing infrastructure available

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Circuit breaker tuning incorrect | Medium | Medium | Production metrics, gradual tuning |
| Rate limiting too aggressive | Medium | Medium | Configurable limits, monitoring |
| Horizontal scaling complexity | High | High | Incremental approach, stateless services first |

#### Entry Criteria

- [ ] Phase 5 complete with architecture foundations
- [ ] Load testing baseline established
- [ ] External dependency SLOs documented

#### Exit Criteria

- [ ] Circuit breakers prevent cascading failures
- [ ] Rate limiting protects resources without impacting legitimate usage
- [ ] Transient failures recover through retries
- [ ] No operations hang indefinitely
- [ ] System handles 10x baseline load through scaling

#### Deliverables

1. `backend/services/circuit_breaker.py` - Enhanced circuit breaker
2. `backend/middleware/rate_limiter.py`
3. `backend/services/retry_service.py`
4. `docs/operations/SCALABILITY_GUIDE.md`
5. Load testing results and analysis

---

## 4. Code Organization Strategy

### Directory Structure

```
E:\VoiceStudio\
├── .cursor/                    # Cursor IDE configuration
│   ├── rules/                  # MDC rules
│   └── STATE.md                # Project state
├── .github/                    # GitHub configuration
│   └── workflows/              # CI/CD workflows
│       ├── sentinel_backend_smoke.yml
│       └── sentinel_ui_smoke_nightly.yml
├── artifacts/                  # Build and test artifacts
│   └── sentinel_runs/          # Repro packets (gitignored)
├── backend/                    # Python backend
│   ├── api/
│   │   ├── v1/                 # Legacy API
│   │   ├── v2/                 # Transitional API
│   │   ├── v3/                 # Current API with StandardResponse
│   │   └── routes/             # Route handlers
│   ├── config/                 # Configuration
│   ├── data/                   # Data access
│   │   └── migrations/         # Alembic migrations
│   ├── middleware/             # Request/response middleware
│   └── services/               # Business logic
├── docs/                       # Documentation
│   ├── api/                    # OpenAPI specs
│   ├── architecture/decisions/ # ADRs
│   ├── design/                 # Design documents
│   ├── governance/             # Process documents
│   └── testing/                # Testing guides
├── fixtures/                   # Test fixtures
│   └── audio/                  # Audio test files
│       └── sentinel_16k_mono.wav
├── scripts/                    # Utility scripts
│   └── proof_runs/             # Sentinel runner
├── shared/                     # Shared schemas
│   └── schemas/                # JSON schemas
├── src/                        # C# source
│   ├── VoiceStudio.App/        # WinUI application
│   │   ├── Commands/           # Command handlers
│   │   ├── Controls/           # Custom controls
│   │   ├── Services/           # App services
│   │   ├── ViewModels/         # MVVM ViewModels
│   │   └── Views/              # XAML views
│   └── VoiceStudio.Core/       # Core contracts
│       ├── DI/                 # Dependency injection
│       └── Security/           # Security infrastructure
├── tests/                      # Test suites
│   ├── integration/            # Integration tests
│   ├── sentinel/               # Sentinel tests
│   │   ├── contracts/          # Contract schemas
│   │   └── test_sentinel_audio_workflow.py
│   ├── ui/                     # UI automation tests
│   │   ├── page_objects/       # Page Object Models
│   │   └── fixtures/           # UI test fixtures
│   └── unit/                   # Unit tests
└── tools/                      # Development tools
    └── overseer/               # Governance tooling
```

### Repository Layout

**Monorepo** — All components (frontend, backend, engines, tests, docs) in a single repository. Justification: Atomic commits across layers, unified CI/CD, simplified dependency management, easier contract synchronization.

### Module Boundaries

| Module | Responsibility | Allowed Dependencies |
|--------|---------------|---------------------|
| VoiceStudio.App | UI presentation, user interaction | VoiceStudio.Core |
| VoiceStudio.Core | Contracts, interfaces, shared types | None (leaf) |
| backend/api | HTTP routing, request/response | backend/services |
| backend/services | Business logic, orchestration | backend/data, app/core/engines |
| app/core/engines | Engine adapters, synthesis | External engines |
| tests/sentinel | Validation, proof generation | backend/api (via HTTP) |

### Standards

- **Linting**: Roslynator (C#), Black/Pylint/MyPy (Python)
- **Formatting**: .editorconfig (unified)
- **Commits**: Conventional Commits (`feat`, `fix`, `refactor`, etc.)

---

## 5. Collaboration & Workflow Guidelines

### Branching Strategy

**Trunk-Based Development with Feature Flags** — Main branch always deployable, short-lived feature branches (< 3 days), feature flags for incomplete features.

Justification: Faster integration, reduced merge conflicts, continuous deployment capability.

### Code Review Rules

- **Minimum approvers**: 1 (2 for architectural changes)
- **Review turnaround**: 24 hours (business days)
- **Required checks**: Build, tests, linting, sentinel smoke (must pass)
- **No self-merge**: Authors cannot approve their own PRs

### Feature Flag Policy

- Use for features spanning multiple PRs
- Naming: `feature_<name>_enabled`
- Default: disabled in production
- Cleanup: Remove within 2 sprints of full rollout

### Documentation Practices

- Issues tracked in: GitHub Issues
- Decisions logged in: ADRs (`docs/architecture/decisions/`)
- API docs: Auto-generated OpenAPI at `/docs`
- Design docs: `docs/design/` (this document)

---

## 6. Scalability & Maintenance Plan

### Technical Debt Management

| Known Debt | Priority | Resolution Plan |
|------------|----------|-----------------|
| Empty catch blocks in legacy code | P2 | Systematic remediation (TD-018 pattern) |
| Inconsistent error handling | P1 | Phase 4 error boundaries |
| API contract drift | P1 | Phase 2 contract hardening |
| Manual deployment steps | P2 | CI/CD automation |

### Scaling Strategy

- **Approach**: Horizontal (stateless services first, then stateful)
- **Bottlenecks**: Engine processes (GPU-bound), file storage (I/O-bound)
- **Scaling triggers**: CPU > 70% for 5 minutes, queue depth > 100

### Migration & Backward Compatibility

- **Versioning strategy**: URI path versioning (`/api/v1/`, `/api/v2/`, `/api/v3/`)
- **Deprecation policy**: 6-month notice, dual-running during transition
- **Migration tooling**: Alembic (Python), EF Migrations (C#)

### Refactoring Checkpoints

| Checkpoint | Timing | Focus Areas |
|------------|--------|-------------|
| Phase 2 Complete | Week 4 | Contract compliance, API consistency |
| Phase 4 Complete | Week 10 | Security posture, error handling |
| Phase 6 Complete | Week 18 | Scalability, resilience patterns |
| Quarterly Review | Every 12 weeks | Technical debt, architecture evolution |

---

## 7. Sentinel Runner Specification

### API Call Matrix

| Step | Endpoint | Method | Request | Expected | Timeout |
|------|----------|--------|---------|----------|---------|
| 1. Preflight | `/v1/health/metrics` | GET | — | 200 JSON with ffmpeg presence | 5s |
| 2. Import ref | `/upload_ref` | POST | multipart file=@sentinel.wav | 200 `{id, path}` | 30s |
| 3. Sync synth | `/tts_enhanced` | POST | JSON TTSRequest + post_chain | 200 `{result_b64_wav}` | 120s |
| 4. Async synth | `/tts_async` | POST | JSON TTSRequest | 200 `{job_id}` | 10s |
| 5. Poll job | `/jobs/{job_id}` | GET | — | `status=done` + audio | 180s |
| 6. A/B summary | `/v1/ab/summary` | POST | ratings payload | 200 summary | 30s |
| 7. Eval ingest | `/v1/evals/ingest` | POST | run metrics | 200/401/404 | 10s |

### Repro Packet Structure

```
artifacts/sentinel_runs/<run_id>/
├── summary.json              # Pass/fail per invariant
├── steps.jsonl               # Step-by-step log
├── requests/                 # Raw request payloads
│   ├── 01_health.json
│   ├── 02_upload.json
│   ├── 03_tts_enhanced.json
│   ├── 04_tts_async.json
│   ├── 05_poll.json
│   ├── 06_ab_summary.json
│   └── 07_eval_ingest.json
├── responses/                # Raw response payloads
│   ├── 01_health.json
│   ├── 02_upload.json
│   ├── 03_tts_enhanced.json
│   ├── 04_tts_async.json
│   ├── 05_poll.json
│   ├── 06_ab_summary.json
│   └── 07_eval_ingest.json
├── outputs/                  # Generated artifacts
│   ├── synth_sync.wav
│   ├── synth_async.wav
│   └── metrics.json
└── screenshots/              # UI run screenshots (if applicable)
```

### Logging Schema (JSONL)

```json
{
  "ts_utc": "2026-02-13T12:34:56.789Z",
  "run_id": "20260213-123456-abc123",
  "step_id": "03_tts_enhanced",
  "component": "sentinel_runner",
  "endpoint": "/tts_enhanced",
  "method": "POST",
  "status": 200,
  "dur_ms": 1234,
  "corr_id": "req-abc-123",
  "req_hash": "sha256:...",
  "resp_hash": "sha256:...",
  "artifact_paths": ["outputs/synth_sync.wav"],
  "error_code": null,
  "error_msg": null
}
```

### Determinism Requirements

1. **Hash all outputs**: SHA256 of response bodies and generated files
2. **ML variability handling**: Assert metric tolerances, not exact equality
3. **Timestamp isolation**: Use fixed seeds for reproducible randomness where possible
4. **Environment capture**: Log Python version, package versions, GPU info

---

## 8. UI Automation Specification

### Critical Smoke Workflows

| Workflow | Steps | AutomationIds Required |
|----------|-------|----------------------|
| 1. Import | Launch → Import button → File picker bypass → Verify Library | `NavStudio`, `Btn_Import`, `List_Library` |
| 2. Clone | Open Clone panel → Select file → Run clone → Verify status | `NavProfiles`, `Panel_Clone`, `Btn_RunClone`, `Status_Clone` |
| 3. Analyze | Open Analyze panel → Run analyze → Verify artifact | `NavAnalyze`, `Panel_Analyze`, `Btn_Analyze`, `Output_Artifact` |
| 4. Effects | Open Effects → Apply chain → Export → Verify file | `NavEffects`, `Panel_Mixer`, `Btn_Apply`, `Btn_Export` |

### AutomationId Naming Convention

```
<Category>_<Component>_<Action>
```

Examples:
- `Nav_Studio` - Navigation to Studio section
- `Panel_Clone_RunButton` - Run button in Clone panel
- `List_Library_Items` - Library item list
- `Status_Training_Progress` - Training progress indicator

### Page Object Model Structure

```python
class StudioPage:
    """Page Object for Studio section."""
    
    AUTOMATION_IDS = {
        "nav_button": "NavStudio",
        "import_button": "Btn_Import",
        "library_list": "List_Library",
    }
    
    def __init__(self, driver: WinAppDriverSession):
        self._driver = driver
    
    def navigate(self) -> None:
        """Navigate to Studio section."""
        self._driver.find_element("accessibility id", self.AUTOMATION_IDS["nav_button"]).click()
    
    def import_file(self, filepath: str) -> None:
        """Import audio file (dev bypass for file picker)."""
        # Implementation
    
    def verify_library_item(self, name: str) -> bool:
        """Verify item appears in library."""
        # Implementation
```

---

## 9. CI/CD Integration

### Workflow: sentinel_backend_smoke.yml

```yaml
name: Sentinel Backend Smoke

on:
  push:
    branches: [main, release/*]
  pull_request:
    branches: [main]

jobs:
  sentinel-smoke:
    runs-on: windows-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: pip install -r requirements.txt
        
      - name: Start backend
        run: |
          Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "backend.api.main:app", "--host", "127.0.0.1", "--port", "8001" -NoNewWindow
          Start-Sleep -Seconds 10
          
      - name: Run sentinel
        run: python scripts/proof_runs/sentinel_audio_workflow.py
        env:
          VOICESTUDIO_API_BASE: http://127.0.0.1:8001
          
      - name: Upload artifacts on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: sentinel-repro-${{ github.run_id }}
          path: artifacts/sentinel_runs/
          retention-days: 30
```

### Workflow: sentinel_ui_smoke_nightly.yml

```yaml
name: Sentinel UI Smoke (Nightly)

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:

jobs:
  ui-smoke:
    runs-on: windows-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build application
        run: dotnet build VoiceStudio.sln -c Debug -p:Platform=x64
        
      - name: Start WinAppDriver
        run: |
          Start-Process -FilePath "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe" -NoNewWindow
          Start-Sleep -Seconds 5
          
      - name: Run UI smoke tests
        run: pytest tests/ui/test_smoke_workflows.py -v --screenshots
        
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ui-smoke-${{ github.run_id }}
          path: |
            .buildlogs/ui_tests/screenshots/
            artifacts/sentinel_runs/
          retention-days: 14
```

---

## 10. Verification & Acceptance Criteria

### Phase 1 Acceptance Criteria

| Criterion | Verification Method | Pass Condition |
|-----------|-------------------|----------------|
| Sentinel executes all steps | Run `sentinel_audio_workflow.py` | Exit code 0, all 7 steps logged |
| Repro packet complete | Inspect `artifacts/sentinel_runs/<id>/` | All required files present |
| CI uploads artifacts | Trigger workflow with forced failure | Artifact downloadable from Actions |
| Timeouts respected | Inject delays in mock API | Graceful timeout handling |

### Phase 2 Acceptance Criteria

| Criterion | Verification Method | Pass Condition |
|-----------|-------------------|----------------|
| OpenAPI spec generated | Run `python -m backend.api.openapi_gen` | Valid OpenAPI 3.0 JSON |
| Pydantic validation | Send malformed requests | 422 with detailed errors |
| StandardResponse format | Call v3 endpoints | Response matches schema |
| Version coexistence | Call v1, v2, v3 endpoints | All return expected format |

### Phase 3 Acceptance Criteria

| Criterion | Verification Method | Pass Condition |
|-----------|-------------------|----------------|
| AutomationIds present | Inspect XAML | All critical panels have IDs |
| Smoke tests pass | Run `pytest tests/ui/test_smoke_workflows.py` | 4/4 workflows pass |
| Test stability | Run 10 times | > 95% pass rate |
| Screenshots captured | Check `screenshots/` | Failure screenshots present |

### Phase 4 Acceptance Criteria

| Criterion | Verification Method | Pass Condition |
|-----------|-------------------|----------------|
| No plaintext credentials | Grep config files | Zero matches |
| Error boundaries active | Force exceptions | No crashes, user-friendly errors |
| Health checks accurate | Kill dependencies | Health endpoint reflects status |
| Graceful shutdown | Send SIGTERM | Clean exit within 30s |
| Correlation IDs | Check logs | All requests have `corr_id` |

### Phase 5 Acceptance Criteria

| Criterion | Verification Method | Pass Condition |
|-----------|-------------------|----------------|
| DI resolution | Run application | No static service access |
| Cache effectiveness | Performance test | > 70% hit rate |
| Queue processing | Submit async jobs | Jobs complete via queue |
| Migrations apply | Fresh database | Schema matches models |

### Phase 6 Acceptance Criteria

| Criterion | Verification Method | Pass Condition |
|-----------|-------------------|----------------|
| Circuit breakers | Kill dependency | No cascading failures |
| Rate limiting | Burst requests | 429 after threshold |
| Retry success | Inject transient failures | Recovery within retry limit |
| Timeout enforcement | Inject delays | Operations timeout, no hangs |

---

## 11. Risk Assessment

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| API contract drift | High | High | Schema validation in CI, contract tests | Backend Lead |
| UI test flakiness | High | Medium | Explicit waits, retry logic, stable IDs | QA Lead |
| Engine unavailability | Medium | High | Mock engine mode, availability checks | Engine Lead |
| CI timeout exceeded | Medium | Medium | Optimize tests, parallel execution | DevOps |
| Security regression | Low | Critical | Security scanning in CI, code review | Security Lead |
| Resource exhaustion | Low | High | Rate limiting, circuit breakers | Backend Lead |

---

## 12. Quality Checklist

Before finalizing this plan, verify:

- [x] All six planning sections present (per planning.mdc)
- [x] Each phase has entry/exit criteria, risks, and milestones
- [x] Diagrams included for architecture
- [x] Scope boundaries explicit (in/out of scope)
- [x] Dependencies mapped across phases
- [x] Plan understandable by non-implementers
- [x] Verification criteria measurable and testable
- [x] Timeline realistic for team capacity

---

## Document Control

**Version History:**
- Version 1.0 (2026-02-13): Initial release for peer review

**Review Required:**
- Technical Architecture Review Board
- Backend Engineering Lead
- UI Engineering Lead
- QA Lead
- DevOps Lead

**Approval Required:**
- VP of Engineering
- Product Owner

**Next Review Date:** 2026-02-20 (7 days post-creation)

---

## Appendix A: Reference Documents

1. **Deterministic Sentinel Audio Workflow Plan** (PDF) - Original sentinel specification
2. **ARCHITECTURAL_ASSESSMENT_AND_REMEDIATION_PLAN.md** - 5-phase remediation roadmap
3. **VOICESTUDIO_COMPLETE_SYSTEM_REPORT.md** - Complete system architecture documentation
4. **ADR-007** - UI/Backend communication architecture
5. **ADR-010** - Platform identity (native Windows application)

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| Sentinel | Deterministic audio file used as test tracer through entire pipeline |
| Repro Packet | Complete artifact bundle for reproducing and debugging test runs |
| Contract Drift | Divergence between expected API behavior and actual implementation |
| AutomationId | Unique identifier for UI elements enabling automation |
| Circuit Breaker | Pattern that prevents cascading failures by failing fast |
| StandardResponse | Generic API response envelope with consistent structure |

## Appendix C: Command Reference

```powershell
# Run sentinel smoke test
python scripts/proof_runs/sentinel_audio_workflow.py

# Run with custom API base
$env:VOICESTUDIO_API_BASE = "http://127.0.0.1:8002"
python scripts/proof_runs/sentinel_audio_workflow.py

# Run UI smoke tests
pytest tests/ui/test_smoke_workflows.py -v

# Run all verification
.\scripts\verify.ps1

# Generate OpenAPI spec
python -m backend.api.openapi_gen > docs/api/openapi.json
```
