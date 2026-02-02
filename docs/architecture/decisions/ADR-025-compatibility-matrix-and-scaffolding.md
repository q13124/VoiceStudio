# ADR-025: Compatibility Matrix and Scaffolding System

## Status

**Accepted** - 2026-02-02

## Context

VoiceStudio had version pins scattered across multiple files (`requirements.txt`, `requirements_engines.txt`, `version_lock.json`, `global.json`, `Directory.Build.props`). This created several challenges:

1. **Drift risk**: Versions could change in one file without updating others
2. **No enforcement**: Protected dependencies (torch, numpy, librosa) could be accidentally upgraded
3. **Tribal knowledge**: Reasons for version constraints existed only in developers' heads
4. **Inconsistent patterns**: New panels, routes, and engines were created without standard templates
5. **CODEOWNERS absent**: No formalized protected surface ownership

This situation was identified during integration of comprehensive architecture recommendations (Claude recommendations analysis, 2026-02-02).

## Decision

We adopt a **Compatibility Matrix and Scaffolding System** with these components:

### 1. Compatibility Matrix (`config/compatibility_matrix.yml`)

A single YAML file defining:
- Platform requirements (SDK versions, Python runtime)
- Python dependency pins with reasons and tech debt references
- .NET dependency pins
- API contracts and engine protocols
- UI invariants (design tokens, panel registry)
- Protected surfaces with owners

### 2. Validation Tooling

- `scripts/check_compatibility_matrix.py`: Validates project files match matrix
- Pre-commit hook: Runs matrix validation on version-related files
- CI job: `compatibility-matrix-validation` in `.github/workflows/test.yml`
- Integration with `scripts/run_verification.py`

### 3. Scaffolding Tools (`tools/scaffolds/`)

CLI tools that generate new components with correct patterns:
- `generate_panel.py`: UI panels (XAML + ViewModel + tests)
- `generate_route.py`: FastAPI routes (router + models + tests)
- `generate_engine.py`: Engine adapters (manifest + adapter + tests)

### 4. CODEOWNERS (`.github/CODEOWNERS`)

Maps protected surfaces to role-based owners for automated PR review assignment.

### 5. AI Agent Safety Rule (`.cursor/rules/workflows/auto-mode-safety.mdc`)

Ensures AI agents check the matrix before proposing dependency changes and use scaffolds for new components.

## Consequences

### Positive

- **Single source of truth**: Version constraints centralized with documented reasons
- **Automated validation**: CI catches version drift before merge
- **Consistent code generation**: Scaffolds enforce MVVM, FastAPI, and engine patterns
- **Formalized ownership**: CODEOWNERS auto-assigns reviewers for protected paths
- **AI-safe development**: Agents cannot bypass locked dependencies without escalation

### Negative

- **Learning curve**: Developers must understand matrix structure and use scaffolds
- **Maintenance overhead**: Matrix requires updates when versions change
- **Scaffold limitations**: Not all components fit scaffold patterns; manual creation needs justification

### Neutral

- **Validation speed**: Matrix check adds ~100ms to verification; acceptable
- **CI duration**: New job adds ~1-2 minutes; parallelizes with other jobs
- **Template evolution**: Scaffold templates will need updates as patterns evolve

## Implementation

Phase 1 (Foundation):
- [x] `config/compatibility_matrix.yml` created
- [x] `scripts/check_compatibility_matrix.py` implemented
- [x] `.github/CODEOWNERS` created
- [x] Pre-commit hook added
- [x] `docs/developer/COMPATIBILITY_MATRIX_GUIDE.md` written

Phase 2 (Scaffolding):
- [x] `tools/scaffolds/generate_panel.py` implemented
- [x] `tools/scaffolds/generate_route.py` implemented
- [x] `tools/scaffolds/generate_engine.py` implemented
- [x] Templates in `tools/scaffolds/templates/`

Phase 3 (CI Integration):
- [x] `compatibility-matrix-validation` job in test.yml
- [x] Integration with `run_verification.py`

Phase 4 (AI Agent Safety):
- [x] `.cursor/rules/workflows/auto-mode-safety.mdc` created
- [x] `docs/developer/AI_AGENT_DEVELOPMENT_GUIDE.md` written

Phase 5 (Documentation):
- [x] This ADR (ADR-025)
- [ ] `CANONICAL_REGISTRY.md` update
- [ ] Training materials

## References

- Compatibility Matrix: `config/compatibility_matrix.yml`
- Matrix Guide: `docs/developer/COMPATIBILITY_MATRIX_GUIDE.md`
- AI Agent Guide: `docs/developer/AI_AGENT_DEVELOPMENT_GUIDE.md`
- Scaffolds: `tools/scaffolds/`
- CODEOWNERS: `.github/CODEOWNERS`
- Tech Debt Register: `docs/governance/TECH_DEBT_REGISTER.md`
