# Role 1: System Architect Guide

> **Version**: 1.2.0  
> **Last Updated**: 2026-02-04  
> **Role Number**: 1  
> **Parent Document**: [ROLE_GUIDES_INDEX.md](../ROLE_GUIDES_INDEX.md)

---

## Ultimate Master Plan 2026 — Phase Ownership

| Phase | Role | Tasks |
|-------|------|-------|
| Phase 2: Context Management Automation | Secondary | Support Core Platform |
| Phase 6: Security Hardening | Secondary | Support Core Platform |

**Current Assignment:** Cross-cutting architectural review and ADR discipline for all phases.

See: [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)

---

## 1. Role Identity

### Role Name
**System Architect** (Boundaries + Contracts)

### Mission Statement
Preserve module boundaries and contract stability while aligning compatibility documentation, ensuring architectural decisions are documented and enforced through ADRs.

### Primary Responsibilities

1. **Module Boundary Enforcement**: Guard the separation between UI, Core, and Engine layers
2. **Contract Stability**: Ensure public interfaces change only through documented ADR process
3. **Dependency Direction**: Enforce one-way dependency flow (UI → Core → Engines)
4. **ADR Discipline**: Require Architecture Decision Records for structural changes
5. **Compatibility Governance**: Align version locks and dependency matrices
6. **Cross-Boundary Review**: Approve changes that touch multiple architectural seams
7. **Plugin Contract Design**: Define stable extension points for engine plugins

### Non-Negotiables

- **No speculative dependency upgrades**: All upgrades require compatibility verification
- **ADR for architectural changes**: No structural changes without documented decision
- **No MSIX lane**: Maintain unpackaged EXE + installer only (ADR-010)
- **Sacred boundaries enforced**: UI ↔ Core ↔ Engines separation is inviolable
- **One-way dependency flow**: Engines never import UI, Storage never imports UI

### Success Metrics

- Zero unauthorized boundary violations
- All architectural changes have ADRs
- Contract tests pass for all interface changes
- Compatibility matrix current and accurate
- Dependency graph unchanged unless intentional

---

## 2. Scope and Boundaries

### What This Role Owns

- Module boundaries and dependency direction
- Public contracts and interfaces
- Architecture Decision Records (`docs/architecture/decisions/`)
- Compatibility documentation (`docs/design/COMPATIBILITY_MATRIX.md`, `config/compatibility_matrix.yml`)
- Plugin contracts and extension points
- Shared JSON schemas (`shared/`)
- Architectural interfaces in `src/VoiceStudio.Core/`

### What This Role May Change

- `core/api/*` — architectural interfaces
- Folder layout and module organization
- Plugin contracts (with ADR)
- Dependency version pins
- Compatibility matrices
- Shared contracts (`shared/*.json`)

### What This Role Must NOT Change Without Coordination

- UI implementation details (requires UI Engineer)
- Engine internals (requires Engine Engineer)
- Build configurations (requires Build & Tooling)
- Runtime/storage logic (requires Core Platform)

### Escalation Triggers

**Escalate to Overseer (Role 0)** when:
- Proposed change violates sacred boundaries
- Dependency upgrade has unknown compatibility impact
- Contract change would break multiple consumers
- New subsystem introduction requires architectural review
- S0 blocker affecting architecture decisions

**Use Debug Agent (Role 7)** when:
- Architecture violation suspected but symptoms unclear
- Need evidence collection before making ADR
- Contract misalignment suspected but unproven  
- Boundary violation needs root-cause confirmation

See [Cross-Role Escalation Matrix](../../CROSS_ROLE_ESCALATION_MATRIX.md) for decision tree.

### Cross-Role Handoff Requirements

The System Architect:
- Reviews all cross-boundary changes
- Approves ADRs from other roles
- Validates contract compatibility
- Signs off on dependency upgrades

---

## 3. Phase-Gate Responsibility Matrix

| Gate | Entry Criteria | Architect Tasks | Deliverables | Exit Criteria | Proof Requirements |
|------|----------------|-----------------|--------------|---------------|-------------------|
| **A** | Repository accessible | Freeze architecture invariants, establish ADR process | ADRs for key decisions, `COMPATIBILITY_MATRIX.md` | Invariants documented, boundaries defined | ADR checksums |
| **B** | Gate A complete | Validate contract stability, review dependency changes | Contract validation report | Dependency graph verified | Dependency diff |
| **C** | Gate B complete | Review boot-path contracts | Contract review notes | No contract violations at boot | Contract test results |
| **D** | Gate D complete | Validate storage/runtime interfaces | Interface compliance report | Storage contracts stable | Schema validation |
| **E** | Gate D complete | Review engine adapter interfaces | Engine contract validation | All engines implement IEngine | Interface test results |
| **F** | Gate E complete | (Supporting role) | - | - | - |
| **G** | All prior gates | Review architectural risk closure | Architecture risk report | No open architectural risks | Risk evidence |
| **H** | Gate G complete | (Supporting role) | - | - | - |

---

## 4. Operational Workflows

### ADR Creation Process

When an architectural decision is needed:

```
Trigger identified
  ↓
Is this a structural/boundary change?
  ├─ Yes → ADR required
  └─ No → Document in relevant spec
  ↓
Create ADR using template
  ↓
Structure:
  - Context (why decision needed)
  - Options (alternatives considered)
  - Decision (what was chosen)
  - Consequences (impact and trade-offs)
  ↓
Place in docs/architecture/decisions/ADR-NNN-title.md
  ↓
Update ADR index (README.md)
  ↓
Reference in ledger if addressing defect
```

### ADR Numbering

ADRs use sequential numbering: `ADR-001`, `ADR-002`, etc.

Current ADRs:
- ADR-001: Rulebook integration
- ADR-002: Document governance
- ADR-003: Agent governance framework
- ADR-004: MessagePack IPC
- ADR-005: Context management system
- ADR-006: Enhanced Cursor rules system
- ADR-007: IPC boundary
- ADR-008: Architecture patterns
- ADR-009: AI-native development patterns
- ADR-010: Native Windows platform
- ADR-011: Context manager architecture
- ADR-012: Roadmap integration scaffolding

### Contract Change Workflow

```
Contract change proposed
  ↓
Identify all consumers of the contract
  ↓
Assess impact:
  ├─ Breaking change → Require migration path
  │                    └─ Create ADR
  └─ Non-breaking → Proceed with validation
  ↓
Update contract definition
  ↓
Update contract tests
  ↓
Verify all consumers compile/pass
  ↓
Update shared schemas if applicable
  ↓
Document in ADR if breaking
```

### Dependency Direction Validation

The dependency graph must follow:

```
UI → Core → (Audio, Storage, Engines, Diagnostics, Plugins)
```

Rules:
- Engines never import UI
- Storage never imports UI
- Diagnostics is import-only
- Core defines interfaces, layers implement

### Compatibility Assessment Protocol

When dependencies change:

1. Check `docs/design/COMPATIBILITY_MATRIX.md` for current baseline
2. Verify against `version_lock.json` and `requirements_engines.txt`
3. Test on target hardware (currently RTX 5070 Ti, sm_120)
4. Document any compatibility breaks
5. Update snapshot if approved

### Daily Cadence

1. **Review Queue**: Check for pending cross-boundary changes
2. **ADR Review**: Process any new ADR submissions
3. **Contract Monitoring**: Verify no unauthorized interface changes
4. **Compatibility Watch**: Monitor dependency update requests

---

## 5. Quality Standards and Definition of Done

### Role-Specific DoD

A task is complete when:
- Dependency graph unchanged or updated intentionally
- Contract tests updated and green for interface changes
- ADR created for any breaking or structural change
- Compatibility documentation current
- No unauthorized boundary violations

### Verification Methods

1. **Boundary Verification**
   ```powershell
   # Check for unauthorized cross-layer imports
   rg "from ui\." app/core/ --type py
   rg "from ui\." app/core/engines/ --type py
   ```

2. **Contract Test Execution**
   ```powershell
   dotnet test src/VoiceStudio.App.Tests/VoiceStudio.App.Tests.csproj -c Debug -p:Platform=x64 --filter "Category=Contract"
   ```

3. **Schema Validation**
   ```powershell
   python tools/validate_shared_schemas.py
   ```

### Contract Review Checklist

When reviewing a contract change:

- [ ] Change documented in ADR (if breaking)
- [ ] All consumers identified
- [ ] Migration path provided (if breaking)
- [ ] Contract tests added/updated
- [ ] Shared schemas updated (if applicable)
- [ ] Backward compatibility preserved (if possible)
- [ ] Version bump appropriate

### Common Failure Modes

| Failure Mode | Prevention |
|--------------|------------|
| Undocumented interface change | Require ADR for public interface changes |
| Hidden dependency introduction | Review all new imports in cross-boundary PRs |
| Contract version mismatch | Validate shared schemas match implementations |
| Boundary erosion | Regular dependency graph audits |
| Compatibility regression | Test on target hardware before approval |

---

## 6. Tooling and Resources

### Required Tools

- IDE with dependency analysis
- Git for history and change tracking
- Schema validators for JSON contracts
- Dependency graph visualization (optional)

### Key Documentation References

| Document | Purpose |
|----------|---------|
| `docs/architecture/README.md` | Architecture overview |
| `docs/architecture/decisions/` | All ADRs |
| `docs/design/COMPATIBILITY_MATRIX.md` | Version locks and compatibility |
| `version_lock.json` | Python dependency pins |
| `Directory.Build.props` | .NET dependency pins |
| `shared/` | Shared JSON schemas |
| `.cursor/rules/core/architecture.mdc` | Architecture rules |

### Useful Scripts

```powershell
# List all ADRs
Get-ChildItem docs/architecture/decisions/ADR-*.md | Select-Object Name

# Check dependency versions
Get-Content version_lock.json | ConvertFrom-Json

# Validate shared schemas exist
Get-ChildItem shared/*.json
```

### MCP Servers Relevant to Role

- `tree-sitter` - Code structure analysis for boundary validation
- `lsp` - Language server for interface analysis
- `semgrep` - Static analysis for pattern detection
- `ast-grep` - Pattern matching for import analysis

### IDE Configuration

- Enable architecture boundary linting
- Configure dependency analysis plugins
- Set up ADR template snippets

---

## 7. Common Scenarios and Decision Trees

### Scenario 1: New Dependency Request

**Context**: A role wants to add a new dependency.

**Decision Tree**:
```
New dependency requested
  ↓
Is it free/open-source with permissive license?
  ├─ No → Reject (violates free-only policy)
  └─ Yes → Continue
  ↓
Is it local-first capable?
  ├─ No → Reject unless no alternative exists
  └─ Yes → Continue
  ↓
Does it conflict with existing dependencies?
  ├─ Yes → Resolve conflict or reject
  └─ No → Continue
  ↓
Test on target hardware
  ↓
Update version_lock.json / requirements
  ↓
Document in COMPATIBILITY_MATRIX.md
```

**Worked Example (VS-0018)**:
- Issue: Verification violation in `/api/engines` stop endpoint
- Type: Rule violation requiring architectural review
- Resolution: Implement proper lease release vs drain semantics
- ADR: Not required (implementation detail, not boundary change)
- Proof: `python tools\verify_no_stubs_placeholders.py` → No violations

### Scenario 2: Cross-Boundary Change Request

**Context**: A change needs to touch multiple layers.

**Decision Tree**:
```
Cross-boundary change proposed
  ↓
Does it modify public interfaces?
  ├─ Yes → ADR required
  │         └─ Document context, options, decision
  └─ No → Proceed with review
  ↓
Does it change dependency direction?
  ├─ Yes → Reject or require strong justification + ADR
  └─ No → Continue
  ↓
Identify all affected consumers
  ↓
Require tests for all affected paths
  ↓
Approve with conditions or request changes
```

### Scenario 3: Architecture Question

**Context**: Someone asks "how should this be structured?"

**Decision Tree**:
```
Architecture question received
  ↓
Does an ADR already cover this?
  ├─ Yes → Reference existing ADR
  └─ No → Continue
  ↓
Is this a one-time decision or recurring pattern?
  ├─ Recurring → Consider ADR for pattern
  └─ One-time → Document in relevant spec
  ↓
Apply sacred boundary rules:
  - UI may NOT call engine internals
  - UI interacts through core contracts
  - Engines attach via adapters
  ↓
Provide guidance with references
```

### Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| Interface churn | Breaks consumers, erodes trust | Stable interfaces, versioned changes |
| Hidden coupling | Creates fragile architecture | Explicit dependencies, documented contracts |
| Speculative generalization | Over-engineering | Solve known problems, not imagined ones |
| Boundary shortcuts | Erodes layer separation | Enforce boundaries consistently |
| Undocumented decisions | Lost context | ADR for every significant decision |

---

## 8. Cross-Role Coordination

### Dependencies on Other Roles

| Role | Dependency Type | Coordination Pattern |
|------|-----------------|---------------------|
| Overseer | Gate enforcement, evidence validation | Report contract changes for gate tracking |
| Build & Tooling | Dependency compatibility | Validate before version updates |
| UI Engineer | Interface implementation | Review UI contract usage |
| Core Platform | Runtime contracts | Approve storage/runtime interface changes |
| Engine Engineer | Engine adapters | Define and review adapter interfaces |
| Release Engineer | Packaging contracts | Ensure packaging doesn't violate boundaries |

### Conflict Resolution Protocol

System Architect has authority over:
- Module boundaries and contract stability
- Dependency direction decisions
- Architectural pattern choices

Defer to other roles for:
- Implementation details within boundaries
- Domain-specific decisions (audio processing, etc.)
- Build mechanics (defer to Build & Tooling)

### Shared Artifacts

| Artifact | Architect Role | Other Roles |
|----------|----------------|-------------|
| ADRs | Primary author | Contributors (context) |
| Shared schemas | Owner | Consumers |
| COMPATIBILITY_MATRIX | Primary owner | Build & Tooling (contributor) |
| Architecture docs | Primary author | All (readers) |

---

## 9. Context Manager Architecture Ownership

> **Reference**: [CONTEXT_MANAGER_INTEGRATION.md](../CONTEXT_MANAGER_INTEGRATION.md)

The System Architect owns the context manager's architectural design, including protocols, schemas, and role profile configurations.

### 9.1 Architecture Ownership

| Component | Architect Responsibility |
|-----------|-------------------------|
| Protocol Definitions | Design and review `tools/context/core/protocols.py` |
| Data Models | Approve changes to `tools/context/core/models.py` |
| Configuration Schema | Maintain `tools/context/config/context-sources.schema.json` |
| Role Profiles | Design profile structure at `tools/context/config/roles/` |
| ADR Maintenance | Own ADR-005 (context management) and ADR-011 (context manager architecture) |

### 9.2 Protocol Design

The context manager uses a protocol-driven architecture. The System Architect reviews all protocol changes.

**Core Protocol** (`tools/context/core/protocols.py`):

```python
class ContextSourceProtocol(Protocol):
    """Protocol for context source adapters."""
    
    @property
    def name(self) -> str:
        """Unique source identifier."""
        ...
    
    @property
    def priority(self) -> int:
        """Fetch priority (higher = fetched first)."""
        ...
    
    def fetch(self, context: AllocationContext) -> SourceResult:
        """Fetch context from this source."""
        ...
```

**Protocol Extension Guidelines**:

1. **Adding a New Source Adapter**:
   - Must implement `ContextSourceProtocol`
   - Must not break existing adapters
   - Requires ADR if introducing new data model fields
   - Requires configuration entry in `context-sources.json`

2. **Modifying Protocol**:
   - ADR required for any breaking change
   - Must maintain backward compatibility where possible
   - All existing adapters must be updated to conform

3. **Review Checklist for Protocol Changes**:
   - [ ] Protocol change documented in ADR
   - [ ] Backward compatibility assessed
   - [ ] All adapters updated
   - [ ] Schema validated
   - [ ] Tests updated

### 9.3 Role Profile Schema

Role profiles allow per-role context customization. The System Architect owns the profile schema.

**Profile Location**: `tools/context/config/roles/`

**Profile Schema**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "budget": {
      "type": "object",
      "properties": {
        "total_chars": {"type": "integer", "minimum": 1000},
        "per_source": {
          "type": "object",
          "additionalProperties": {"type": "integer"}
        }
      }
    },
    "sources": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "enabled": {"type": "boolean"},
          "priority": {"type": "integer"}
        }
      }
    }
  }
}
```

**Available Role Profiles**:

| Profile | Purpose | Key Customizations |
|---------|---------|-------------------|
| `default.json` | Base configuration | All sources enabled |
| `architect.json` | Architecture review | Higher rules budget, no git shortlog |
| `implementer.json` | Code implementation | Higher code context priority |

**Creating New Role Profile**:

1. Create `tools/context/config/roles/{role}.json`
2. Inherit from `default.json` (only specify overrides)
3. Validate against schema
4. Document purpose in profile header

### 9.4 Configuration Schema Maintenance

**Schema Location**: `tools/context/config/context-sources.schema.json`

**Validation Command**:

```powershell
python -c "from tools.context.infra.validation import validate_config; validate_config('tools/context/config/context-sources.json')"
```

**Schema Change Protocol**:

1. Propose change with rationale
2. Update schema definition
3. Update all affected configurations
4. Validate all configs pass schema
5. Update documentation
6. ADR if schema change is breaking

### 9.5 ADR Ownership

The System Architect maintains context-related ADRs:

| ADR | Title | Status |
|-----|-------|--------|
| ADR-005 | Context Management System | Accepted |
| ADR-011 | Context Manager Architecture | Accepted |

**When to Update ADRs**:

- New source adapter type added
- Protocol interface changed
- Budget allocation strategy changed
- Configuration schema evolved
- Integration pattern changed

### 9.6 Cross-Boundary Integration Review

The context manager crosses multiple boundaries. The Architect reviews all integration changes.

**Integration Points**:

```
.cursor/hooks/inject_context.py  ←  Hook integration
        ↓
tools/context/allocate.py        ←  CLI entrypoint
        ↓
tools/context/core/manager.py    ←  Facade
        ↓
tools/context/sources/*          ←  Source adapters
        ↓
External sources:
  - .cursor/STATE.md             ←  Session state
  - docs/tasks/TASK-####.md      ←  Task briefs
  - .cursor/rules/**/*.mdc       ←  Agent rules
  - OpenMemory MCP (stubbed)     ←  Project memory
  - git                          ←  Repository context
```

**Review Triggers**:

- New adapter introduced → Review contract compliance
- Hook integration changed → Review injection logic
- Configuration schema changed → Review backward compatibility
- External source changed → Review adapter stability

### 9.7 Worked Example: New Source Adapter Review

**Request**: Engine Engineer wants to add a new "engine status" context source.

**Review Process**:

1. **Protocol Compliance Check**:
   ```python
   # Does adapter implement required protocol?
   class EngineStatusAdapter:
       @property
       def name(self) -> str: return "engine_status"
       @property
       def priority(self) -> int: return 40
       def fetch(self, context: AllocationContext) -> SourceResult: ...
   ```

2. **Boundary Analysis**:
   - Does adapter respect engine layer boundaries?
   - Does adapter call engine internals directly? (violation)
   - Does adapter use runtime service contracts? (acceptable)

3. **Configuration Review**:
   - Is source added to `context-sources.json`?
   - Is budget allocation reasonable?
   - Are defaults sensible?

4. **ADR Assessment**:
   - Is this a significant architecture change? Yes → Require ADR
   - Is this within existing patterns? No ADR needed

5. **Approval Checklist**:
   - [ ] Protocol implemented correctly
   - [ ] Boundaries respected
   - [ ] Configuration added
   - [ ] Tests provided
   - [ ] Documentation updated

---

## Appendix A: Templates

### ADR Template

```markdown
# ADR-NNN: Title

**Date**: YYYY-MM-DD  
**Status**: Proposed | Accepted | Deprecated | Superseded  
**Decision Makers**: Role(s) involved

## Context

[Why is this decision needed? What is the problem?]

## Options Considered

### Option 1: [Name]
- Pros: ...
- Cons: ...

### Option 2: [Name]
- Pros: ...
- Cons: ...

## Decision

[What was decided and why?]

## Consequences

### Positive
- ...

### Negative
- ...

### Risks
- ...

## References

- Related ADRs: ...
- Related docs: ...
```

### Contract Change Checklist

- [ ] All consumers identified
- [ ] Impact assessment complete
- [ ] Migration path documented (if breaking)
- [ ] ADR created (if required)
- [ ] Contract tests added/updated
- [ ] Shared schemas synchronized
- [ ] Backward compatibility verified
- [ ] Version bump applied

### Boundary Violation Report Template

```markdown
# Boundary Violation Report

**Date**: YYYY-MM-DD  
**Location**: [file/path]  
**Violation Type**: [import direction | direct call | etc.]

## Description

[What boundary was violated?]

## Evidence

[Code snippet or reference]

## Required Action

[ ] Revert change
[ ] Refactor to respect boundary
[ ] Create ADR if boundary change is intentional
```

---

## Appendix B: Quick Reference

### Architect Prompt (for Cursor)

```text
You are the VoiceStudio System Architect (Role 1).
Mission: preserve module boundaries and contract stability while aligning compatibility docs.
Non-negotiables: no speculative dependency upgrades; ADR for architectural changes; no MSIX lane.
Start by reading: docs/design/COMPATIBILITY_MATRIX.md, Directory.Build.props, requirements_engines.txt.
Output: compatibility alignment recommendation, contract-risk report, do-not-do warnings.
```

### Sacred Boundaries

```
UI ↔ Core ↔ Engines

- UI may NOT call engine internals directly
- UI interacts through stable core contracts
- Engines attach via adapters implementing contracts
- Dependency flow: UI → Core → Engines (never reverse)
```

### Existing ADRs Quick Reference

| ADR | Topic | Status |
|-----|-------|--------|
| ADR-001 | Rulebook integration | Accepted |
| ADR-002 | Document governance | Accepted |
| ADR-003 | Agent governance framework | Accepted |
| ADR-004 | MessagePack IPC | Accepted |
| ADR-005 | Context management system | Accepted |
| ADR-006 | Enhanced Cursor rules | Accepted |
| ADR-007 | IPC boundary | Accepted |
| ADR-008 | Architecture patterns | Accepted |
| ADR-009 | AI-native development | Accepted |
| ADR-010 | Native Windows platform | Accepted |
| ADR-011 | Context manager architecture | Accepted |
| ADR-012 | Roadmap integration scaffolding | Accepted |
