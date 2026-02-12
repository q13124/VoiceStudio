# Schema Ownership and Sync Workflow

This document defines ownership, validation, and synchronization workflows for VoiceStudio's shared schemas.

> **Last Updated**: 2026-02-11

---

## Schema Locations

| Location | Purpose | Owner |
| --- | --- | --- |
| `shared/schemas/` | Shared JSON schemas defining contracts | System Architect (Role 1) |
| `shared/contracts/` | API operation contracts | System Architect (Role 1) |
| `backend/api/models*.py` | Backend Pydantic models | Core Platform (Role 4) |
| `docs/api/openapi.json` | Generated OpenAPI spec | Build & Tooling (Role 2) |
| `src/VoiceStudio.App/Services/BackendClient.g.cs` | Generated C# client | Build & Tooling (Role 2) |
| `engines/*.json` | Engine manifests | Engine Engineer (Role 5) |

---

## Schema Registry

The schema registry at `shared/schemas/_registry.json` is the single source of truth for available schemas:

```json
{
  "schemas": [
    {
      "id": "voice_profile.schema.json",
      "path": "schemas/voice_profile.schema.json",
      "description": "Voice profile schema with avatar support"
    },
    // ... additional schemas
  ]
}
```

**Registry Maintenance:**
- Add new schemas to the registry when created
- Update version in registry when schemas change
- Remove deprecated schemas from registry

---

## Core Schemas

### voice_profile.schema.json
- **Owner**: System Architect (Role 1)
- **Consumers**: Backend (ProfileService), Frontend (VoiceProfileViewModel)
- **Sync**: Manual; validate against Pydantic models

### engine_manifest_v3.schema.json
- **Owner**: Engine Engineer (Role 5)
- **Consumers**: Runtime (engine loader), Frontend (engine display)
- **Sync**: Manual; engines must conform to schema

### unified_config.schema.json
- **Owner**: System Architect (Role 1)
- **Consumers**: Configuration services across all layers
- **Sync**: Created per ADR-033; authoritative for config structure

### issue.schema.json
- **Owner**: System Architect (Role 1)
- **Consumers**: Overseer tooling, Debug Agent
- **Sync**: Manual; used by issue tracking system

---

## Sync Workflow

### 1. Schema Change Procedure

When modifying a shared schema:

1. **Notify Owners**: Inform affected role owners before changes
2. **Update Schema**: Modify the schema file with backward-compatible changes when possible
3. **Update Registry**: Bump version in `_registry.json`
4. **Update Consumers**:
   - Backend Pydantic models
   - Frontend DTOs (if manually maintained)
   - Engine manifests (if applicable)
5. **Validate**: Run schema validation against existing data
6. **Document**: Update this document if ownership changes

### 2. Breaking Changes

Breaking schema changes require:

1. **ADR**: Create an Architecture Decision Record
2. **Migration**: Provide migration script or path
3. **Version Bump**: Major version increment in registry
4. **Deprecation**: Mark old schema version as deprecated

### 3. Validation Scripts

| Script | Purpose |
| --- | --- |
| `scripts/check_contract_validation.py` | Validates OpenAPI against backend models |
| `scripts/validate_engine_manifests.py` | Validates engine manifests against schema |

### 4. CI Integration

The pre-commit hook `contract-validation` runs on changes to:
- `openapi.json`
- `BackendClient.g.cs`
- `backend/api/*.py`

---

## OpenAPI Sync Workflow

The OpenAPI specification is generated from backend routes:

```bash
# Generate OpenAPI spec
cd backend
python -c "from api.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > ../docs/api/openapi.json
```

**Regeneration Triggers**:
- New API routes added
- Route parameters changed
- Response models modified

**C# Client Regeneration**:
```bash
# Using NSwag (if configured)
nswag run nswag.json
```

---

## Ownership Matrix

| Schema File | Primary Owner | Secondary Owner | Approval Required |
| --- | --- | --- | --- |
| voice_profile.schema.json | Role 1 | Role 4 | Role 1 |
| engine_manifest_v3.schema.json | Role 5 | Role 1 | Role 5 |
| unified_config.schema.json | Role 1 | Role 4 | Role 1 |
| issue.schema.json | Role 1 | Role 7 | Role 1 |
| openapi.json | Role 2 | Role 4 | Role 2 |
| BackendClient.g.cs | Role 2 | Role 3 | Role 2 |

---

## Validation Checklist

Before merging schema changes:

- [ ] Schema passes JSON Schema validation
- [ ] Registry version updated
- [ ] Affected Pydantic models updated
- [ ] Affected C# DTOs updated (if applicable)
- [ ] Contract validation hook passes
- [ ] ADR created (if breaking change)

---

## Related Documents

- [Architecture Contract (ADR-015)](../architecture/decisions/ADR-015-architecture-integration-contract.md)
- [Compatibility Matrix](../governance/COMPATIBILITY_MATRIX.md)
- [API Versioning (ADR-031)](../architecture/decisions/ADR-031-api-versioning-strategy.md)
