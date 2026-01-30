# Document Governance

> **Version**: 1.0  
> **Last Updated**: 2026-01-30  
> **Owner**: Overseer (Role 0)  
> **Status**: ACTIVE

This document defines the file creation, lifecycle, and archiving policy for VoiceStudio documentation.

---

## 1. Document Lifecycle

### 1.1 Before Creating Any Document

**MANDATORY**: Run the 4-gate check before creating new documentation.

#### Gate 1: Necessity Check

Check [CANONICAL_REGISTRY.md](CANONICAL_REGISTRY.md):

- Topic already exists? → **UPDATE existing doc, do NOT create new**
- Topic not listed? → Proceed to Gate 2

#### Gate 2: Type Classification

Is the document one of these allowed types?

- Architecture Decision (ADR)
- Roadmap (project-wide)
- Plan (feature/phase)
- Technical Spec
- API/Domain Reference
- Developer Guide
- Report (build/test)
- Release Notes

**YES** → Proceed to Gate 3  
**NO** → BLOCKED. Request user approval.

#### Gate 3: Location Validation

Use the correct location per type:

| Type | Location |
|----|-----|
| ADR | `docs/architecture/decisions/` |
| Roadmap | `docs/governance/` |
| Plan/Spec | `docs/design/` |
| Reference | `docs/REFERENCE/` |
| Developer Guide | `docs/developer/` |
| Report | `docs/reports/{category}/` |
| Release Notes | `docs/release/` |

#### Gate 4: Naming Compliance

Follow naming conventions:

- ADRs: `ADR-NNN-short-title.md`
- Plans: `{SCOPE}_PLAN.md`
- Specs: `{FEATURE}_SPEC.md`
- References: `{DOMAIN}_REFERENCE.md`

### 1.2 After Creating a Canonical Document

Update [CANONICAL_REGISTRY.md](CANONICAL_REGISTRY.md) to include the new document.

---

## 2. Versioning Rules

**NEVER create file variants** like `spec_v2.md` or `plan_final.md`.

Instead:

- Use ADRs for decision changes (create new ADR that supersedes old)
- Add `## Changelog` section to living documents
- Rely on git history for version tracking
- Archive obsolete docs to `docs/archive/{category}/`

---

## 3. Archive Workflow

When superseding a document:

1. Add "Superseded by X" note at top of old doc
2. Move to `docs/archive/{category}/`
3. Update [CANONICAL_REGISTRY.md](CANONICAL_REGISTRY.md)

### Archive Locations

| Category | Archive Path |
|----------|--------------|
| Governance | `docs/archive/governance/` |
| Design | `docs/archive/design/` |
| Reports | `docs/archive/reports/` |
| Plans | `docs/archive/plans/` |

See [ARCHIVE_POLICY.md](ARCHIVE_POLICY.md) for detailed archiving policy.

---

## 4. Quick Decision Tree

```text
Creating a doc?
├── Topic exists in registry? → Update existing
├── Architectural decision? → Create ADR
├── Project-wide plan/roadmap? → docs/governance/
├── Feature plan/spec? → docs/design/
├── Reference doc? → docs/REFERENCE/
├── Developer guide? → docs/developer/
├── Build/test report? → docs/reports/
└── None of above? → Request user approval
```

---

## 5. References

- [CANONICAL_REGISTRY.md](CANONICAL_REGISTRY.md) — Document registry
- [ARCHIVE_POLICY.md](ARCHIVE_POLICY.md) — Archive policy (when created)
- [.cursor/rules/workflows/document-lifecycle.mdc](../../.cursor/rules/workflows/document-lifecycle.mdc) — Agent rule for document lifecycle
- [ADR-002](../architecture/decisions/ADR-002-document-governance.md) — Architecture decision for document governance
