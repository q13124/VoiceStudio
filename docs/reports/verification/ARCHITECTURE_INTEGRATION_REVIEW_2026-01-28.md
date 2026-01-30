# VoiceStudio Architecture Integration Review

**Date**: 2026-01-28  
**Prepared By**: Overseer (Role 0) + System Architect (Role 1)  
**Status**: COMPREHENSIVE REVIEW COMPLETE  
**Purpose**: Identify gaps, integration issues, and recommendations for architectural alignment

---

## Executive Summary

VoiceStudio has accumulated multiple architectural layers that operate semi-independently. This review identifies:

- **16 Critical Integration Gaps** requiring attention
- **7 Legacy/Duplicate Systems** that should be consolidated
- **4 Major Disconnected Subsystems** that need wiring
- **12 Recommendations** prioritized by impact

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Context Manager System](#2-context-manager-system)
3. [Role and Agent Governance](#3-role-and-agent-governance)
4. [Overseer Tooling](#4-overseer-tooling)
5. [MCP and Skills Integration](#5-mcp-and-skills-integration)
6. [Integration Gap Matrix](#6-integration-gap-matrix)
7. [Legacy Code Audit](#7-legacy-code-audit)
8. [Recommendations](#8-recommendations)
9. [Risk Assessment](#9-risk-assessment)
10. [Action Items](#10-action-items)

---

## 1. System Architecture Overview

### Current Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER / CURSOR IDE                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────────────┐
│   Skills System      │ │   Hook System    │ │   MCP Servers (26+)          │
│ .cursor/skills/      │ │ .cursor/hooks/   │ │ cursor.mcp.json              │
│                      │ │                  │ │                              │
│ - Role skills (7)    │ │ - inject_context │ │ - openmemory (PARTIAL)       │
│ - Tool skills (4)    │ │ - validate_state │ │ - sequential-thinking ✓      │
│                      │ │ - ensure_update  │ │ - chroma ✓                   │
└──────────┬───────────┘ └────────┬─────────┘ └──────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      CONTEXT MANAGER SYSTEM                                  │
│                      tools/context/                                          │
│  ┌─────────────────┬─────────────────┬─────────────────┐                    │
│  │ ContextManager  │ SourceRegistry  │ ContextAllocator│                    │
│  │ (facade)        │ (priority)      │ (budget)        │                    │
│  └────────┬────────┴────────┬────────┴────────┬────────┘                    │
│           │                 │                 │                              │
│  ┌────────▼────────┬────────▼────────┬────────▼────────┐                    │
│  │ StateAdapter    │ TaskAdapter     │ RulesAdapter    │                    │
│  │ (P:100) ✓       │ (P:90) ✓        │ (P:70) ✓        │                    │
│  ├─────────────────┼─────────────────┼─────────────────┤                    │
│  │ LedgerAdapter   │ MemoryAdapter   │ GitAdapter      │                    │
│  │ (P:85) ✓        │ (P:50) PARTIAL  │ (P:30) ✓        │                    │
│  └─────────────────┴─────────────────┴─────────────────┘                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      ROLE SYSTEM                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 7 Roles: Overseer, Architect, Build, UI, Platform, Engine, Release │    │
│  │ + Skeptical Validator                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────┬─────────────────┬─────────────────┐                    │
│  │ Role Prompts    │ Role Guides     │ Role Skills     │                    │
│  │ .cursor/prompts/│ docs/governance/│ .cursor/skills/ │                    │
│  │ ✓ (8 files)     │ ✓ (8 files)     │ ✓ (8 folders)   │                    │
│  └─────────────────┴─────────────────┴─────────────────┘                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────────────┐
│  Onboarding System   │ │ Overseer CLI     │ │ Agent Governance             │
│  tools/onboarding/   │ │ tools/overseer/  │ │ tools/overseer/agent/        │
│                      │ │ cli/             │ │                              │
│  - Assembler ✓       │ │ - gate ✓         │ │ - registry.py ✓              │
│  - RoleRegistry ✓    │ │ - ledger ✓       │ │ - tool_gateway.py ✓          │
│  - RoleContext ✓     │ │ - report ✓       │ │ - policy_engine.py ✓         │
│                      │ │ - handoff ✓      │ │ - approval_mgr.py ✓          │
│  DISCONNECTED ⚠️     │ │ - phase ✓        │ │ DISCONNECTED ⚠️              │
└──────────────────────┘ └──────────────────┘ └──────────────────────────────┘
```

### Key Finding: Four Major Subsystems Operate Independently

| System | Location | Status | Integrated With |
|--------|----------|--------|-----------------|
| Context Manager | `tools/context/` | ✅ Functional | Hooks only |
| Role System | `.cursor/prompts/` + `docs/governance/roles/` | ✅ Functional | Skills only |
| Onboarding | `tools/onboarding/` | ✅ Functional | Nothing |
| Agent Governance | `tools/overseer/agent/` | ✅ Functional | Nothing |

---

## 2. Context Manager System

### Architecture Status

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| `ContextManager` | `core/manager.py` | ✅ Complete | Facade with caching |
| `ContextAllocator` | `core/allocator.py` | ✅ Complete | Budget enforcement |
| `SourceRegistry` | `core/registry.py` | ✅ Complete | Priority ordering |
| `StateSourceAdapter` | `sources/state_adapter.py` | ✅ Complete | Reads STATE.md |
| `TaskSourceAdapter` | `sources/task_adapter.py` | ✅ Complete | Reads task briefs |
| `LedgerSourceAdapter` | `sources/ledger_adapter.py` | ✅ Complete | Parses QUALITY_LEDGER |
| `RulesSourceAdapter` | `sources/rules_adapter.py` | ✅ Complete | Reads .mdc files |
| `MemorySourceAdapter` | `sources/memory_adapter.py` | ⚠️ Partial | MCP integration stubbed |
| `GitSourceAdapter` | `sources/git_adapter.py` | ✅ Complete | Git status/shortlog |
| `TelemetrySourceAdapter` | `sources/telemetry_adapter.py` | ✅ Complete | Disabled by default |
| `GitKrakenAdapter` | `sources/gitkraken_adapter.py` | ✅ Complete | Disabled by default |

### Critical Gaps

#### Gap C1: ContextBundle Model Incomplete

**Issue**: `LedgerSourceAdapter` and `TelemetrySourceAdapter` return data that doesn't map to `ContextBundle` fields.

**Location**: 
- `tools/context/core/models.py` (ContextBundle class)
- `tools/context/sources/ledger_adapter.py` (returns `ledger` key)
- `tools/context/sources/telemetry_adapter.py` (returns `telemetry` key)

**Impact**: Fetched data is lost during bundle assembly.

**Fix**: Add `ledger` and `telemetry` fields to `ContextBundle` model.

#### Gap C2: Legacy Code Duplication

**Issue**: Two parallel systems exist:

| New System (Used) | Legacy System (Unused) |
|-------------------|------------------------|
| `core/manager.py` | `allocator/allocator.py` |
| `core/models.py` | `allocator/model.py` |
| `sources/*_adapter.py` | `sources/*_reader.py` |

**Files to Remove**:
- `tools/context/allocator/allocator.py`
- `tools/context/allocator/model.py`
- `tools/context/sources/openmemory_reader.py`
- `tools/context/sources/git_reader.py`
- `tools/context/sources/rules_reader.py`
- `tools/context/sources/task_reader.py`
- `tools/context/sources/state_reader.py`

**Impact**: Confusion, maintenance burden, dead code.

#### Gap C3: Memory Adapter MCP Not Wired

**Issue**: `MemorySourceAdapter._call_openmemory_mcp()` is a placeholder.

**Location**: `tools/context/sources/memory_adapter.py:79-106`

**Current Behavior**: Falls back to reading `openmemory.md` file only.

**Impact**: OpenMemory MCP server configured but never actually called.

#### Gap C4: Inject Context Hook Too Complex

**Issue**: `.cursor/hooks/inject_context.py` is 400+ lines mixing:
- Role detection
- Onboarding packet generation
- Context injection
- Sentinel file management

**Impact**: Hard to maintain, test, debug.

**Recommendation**: Split into focused modules.

---

## 3. Role and Agent Governance

### Role System Status

| Component | Location | Status |
|-----------|----------|--------|
| Role Prompts (8) | `.cursor/prompts/ROLE_*_PROMPT.md` | ✅ Complete |
| Role Guides (8) | `docs/governance/roles/ROLE_*_GUIDE.md` | ✅ Complete |
| Role Skills (8) | `.cursor/skills/roles/*/SKILL.md` | ✅ Complete |
| Role Registry | `tools/onboarding/core/role_registry.py` | ✅ Complete |
| Role Config | `tools/onboarding/config/roles.json` | ✅ Complete |

### Agent Governance Status

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| `AgentRegistry` | `tools/overseer/agent/registry.py` | ✅ Complete | Persistent storage |
| `ToolGateway` | `tools/overseer/agent/tool_gateway.py` | ✅ Complete | Policy enforcement |
| `PolicyEngine` | `tools/overseer/agent/policy_engine.py` | ✅ Complete | Risk tiers |
| `ApprovalManager` | `tools/overseer/agent/approval_manager.py` | ✅ Complete | Approval workflow |
| `AuditLogger` | `tools/overseer/agent/audit_logger.py` | ✅ Complete | Audit trail |
| `CircuitBreaker` | `tools/overseer/agent/circuit_breaker.py` | ✅ Complete | Failure protection |
| `KillSwitch` | `tools/overseer/agent/kill_switch.py` | ✅ Complete | Emergency shutdown |

### Critical Gaps

#### Gap R1: AgentRole Enum vs RoleConfig Mismatch

**Issue**: Two incompatible role systems exist.

| Agent Governance | VoiceStudio Roles |
|------------------|-------------------|
| `AgentRole.CODER` | Role 0: Overseer |
| `AgentRole.TESTER` | Role 1: System Architect |
| `AgentRole.SUPPORT` | Role 2: Build & Tooling |
| `AgentRole.UPDATER` | Role 3: UI Engineer |
| `AgentRole.DATA_IMPORTER` | Role 4: Core Platform |
| `AgentRole.OVERSEER` | Role 5: Engine Engineer |
| `AgentRole.REVIEWER` | Role 6: Release Engineer |
| `AgentRole.BUILDER` | Skeptical Validator |

**Location**:
- `tools/overseer/agent/identity.py` (AgentRole enum)
- `tools/onboarding/config/roles.json` (VoiceStudio roles 0-6)

**Impact**: PolicyEngine cannot enforce VoiceStudio role-specific policies.

**Fix**: Create mapping between AgentRole and RoleConfig.

#### Gap R2: Onboarding Not Connected to AgentRegistry

**Issue**: When onboarding generates a packet, it doesn't register the agent.

**Location**: `tools/onboarding/core/assembler.py`

**Impact**: Agents aren't tracked in governance system.

**Fix**: Call `AgentRegistry.register()` during onboarding.

#### Gap R3: Context Manager Not Connected to AgentRegistry

**Issue**: `ContextManager` accepts `role` parameter but doesn't validate against `AgentRegistry`.

**Location**: `tools/context/core/models.py` (AllocationContext)

**Impact**: Context allocation isn't governed by agent identity/state.

#### Gap R4: Context Manager Not Connected to Role Profiles

**Issue**: Role profiles exist in `tools/context/config/roles/` but aren't used by role system.

**Location**:
- `tools/context/config/roles/architect.json`
- `tools/context/config/roles/implementer.json`
- `tools/context/config/roles/default.json`

**Impact**: Role-based context customization not leveraged.

---

## 4. Overseer Tooling

### CLI Status

| Command | Subcommands | Status |
|---------|-------------|--------|
| `gate` | status, blockers, next, dashboard, export | ✅ Complete |
| `ledger` | validate, status, gaps, entry, list | ✅ Complete |
| `handoff` | validate, reconcile, index, show, create, list | ✅ Complete |
| `report` | daily, gate, comprehensive, export | ✅ Complete |
| `agent` | list, stats, approvals, audit | ✅ Complete |
| `phase` | status, export, markdown, json | ✅ Complete |

### Verification Scripts

| Script | Status | Notes |
|--------|--------|-------|
| `scripts/run_verification.py` | ✅ Functional | Gate + Ledger + optional Build |
| `scripts/run-verification.ps1` | ✅ Functional | PowerShell wrapper |

### Gaps

#### Gap O1: No Programmatic Context Manager API

**Issue**: Overseer CLI and Context Manager communicate via files only.

**Impact**: No real-time context injection from overseer tools.

#### Gap O2: No Role Invocation Command

**Issue**: No CLI command to invoke role skills.

**Impact**: Roles must be invoked manually via Cursor.

#### Gap O3: Overseer Monitor Not Integrated

**Issue**: `overseer_monitor.py` exists but no CLI command.

**Impact**: No real-time monitoring command.

---

## 5. MCP and Skills Integration

### MCP Server Status

| Category | Servers | Status |
|----------|---------|--------|
| Memory/Context | openmemory, mem0, context7 | ⚠️ Partially wired |
| AI Reasoning | sequential-thinking, thought-chain, deepseek-* | ✅ Configured |
| Code Intelligence | tree-sitter, lsp, ast-grep, semgrep | ✅ Configured |
| Git/GitHub | git, github, GitKraken | ✅ Configured |
| Voice/Audio | elevenlabs, hume | ✅ Configured |
| Dev Tools | docker-mcp, playwright, sonarqube | ✅ Configured |

### Skills System Status

| Type | Count | Status |
|------|-------|--------|
| Role Skills | 8 | ✅ Complete |
| Tool Skills | 4 | ✅ Complete |

### Gaps

#### Gap M1: OpenMemory MCP Not Actually Called

**Issue**: MCP server configured but code uses file fallback.

**Location**: `tools/context/sources/memory_adapter.py`

**Evidence**:
```python
def _call_openmemory_mcp(self, query: str) -> List[MemoryMatch]:
    """MCP protocol integration can be added when an MCP client is available."""
    return []  # Placeholder
```

**Impact**: OpenMemory rules assume MCP usage but code doesn't.

#### Gap M2: Skills Not Exposed as MCP Tools

**Issue**: Skills are Python scripts, not MCP tools.

**Impact**: Cannot invoke skills via MCP protocol.

#### Gap M3: No MCP Health Checks

**Issue**: No verification that configured MCPs are functional.

**Impact**: Failures may be silent.

---

## 6. Integration Gap Matrix

### System Connections Status

| From → To | Context | Roles | Onboarding | Agent Gov | Overseer CLI | MCP |
|-----------|---------|-------|------------|-----------|--------------|-----|
| **Context** | - | ⚠️ Partial | ❌ None | ❌ None | ❌ None | ⚠️ Partial |
| **Roles** | ⚠️ Partial | - | ✅ Via Skills | ❌ None | ❌ None | ❌ None |
| **Onboarding** | ❌ None | ✅ Complete | - | ❌ None | ❌ None | ❌ None |
| **Agent Gov** | ❌ None | ❌ None | ❌ None | - | ⚠️ CLI only | ❌ None |
| **Overseer CLI** | ❌ None | ❌ None | ❌ None | ⚠️ CLI only | - | ❌ None |
| **MCP** | ⚠️ Partial | ❌ None | ❌ None | ❌ None | ❌ None | - |

### Legend

- ✅ Complete: Full integration
- ⚠️ Partial: Some integration, gaps remain
- ❌ None: No integration

---

## 7. Legacy Code Audit

### Files to Remove

| File | Reason | Risk |
|------|--------|------|
| `tools/context/allocator/allocator.py` | Replaced by `core/allocator.py` | Low |
| `tools/context/allocator/model.py` | Replaced by `core/models.py` | Low |
| `tools/context/sources/openmemory_reader.py` | Replaced by `memory_adapter.py` | Low |
| `tools/context/sources/git_reader.py` | Replaced by `git_adapter.py` | Low |
| `tools/context/sources/rules_reader.py` | Replaced by `rules_adapter.py` | Low |
| `tools/context/sources/task_reader.py` | Replaced by `task_adapter.py` | Low |
| `tools/context/sources/state_reader.py` | Replaced by `state_adapter.py` | Low |

### Files with Excessive Complexity

| File | Lines | Issue | Recommendation |
|------|-------|-------|----------------|
| `.cursor/hooks/inject_context.py` | 400+ | Mixed concerns | Split into 3 modules |

---

## 8. Recommendations

### Priority 1: Critical (Fix Now)

#### R1: Create AgentRole ↔ RoleConfig Mapping

**What**: Create adapter to map VoiceStudio roles (0-6) to AgentRole enum.

**Why**: Unify governance systems.

**How**:
```python
# tools/overseer/agent/role_mapping.py
ROLE_MAPPING = {
    0: AgentRole.OVERSEER,
    1: AgentRole.REVIEWER,  # Architect reviews
    2: AgentRole.BUILDER,   # Build & Tooling
    3: AgentRole.CODER,     # UI Engineer
    4: AgentRole.CODER,     # Platform
    5: AgentRole.CODER,     # Engine
    6: AgentRole.BUILDER,   # Release
}
```

#### R2: Add Ledger/Telemetry to ContextBundle

**What**: Extend ContextBundle model with missing fields.

**How**:
```python
# tools/context/core/models.py
@dataclass
class ContextBundle:
    # Existing fields...
    ledger: Optional[List[Dict]] = None
    telemetry: Optional[Dict] = None
```

#### R3: Remove Legacy Code

**What**: Delete 7 legacy files in `tools/context/`.

**Why**: Reduce confusion and maintenance.

### Priority 2: High (This Sprint)

#### R4: Wire Onboarding to AgentRegistry

**What**: Register agents when generating onboarding packets.

**How**: Add `AgentRegistry.register()` call in `OnboardingAssembler`.

#### R5: Split inject_context.py

**What**: Separate concerns into focused modules.

**How**:
- `detect_role.py` - Role detection logic
- `inject_context.py` - Pure context injection
- `onboard_role.py` - Onboarding packet generation

#### R6: Implement OpenMemory MCP Client

**What**: Replace placeholder with actual MCP calls.

**Why**: Rules assume MCP usage but code doesn't.

### Priority 3: Medium (Next Sprint)

#### R7: Connect Context Manager to AgentRegistry

**What**: Validate agent identity before context allocation.

#### R8: Add MCP Health Check Script

**What**: Create script to verify MCP server availability.

**How**:
```python
# scripts/verify-mcp-servers.py
# Check each configured MCP server is reachable
```

#### R9: Add Proof Index Extraction

**What**: Extract Proof Index from STATE.md into context bundle.

### Priority 4: Low (Backlog)

#### R10: Expand Role Profile Configurations

**What**: Add role-specific context budgets for all 7 roles.

#### R11: Add Role Invocation CLI Command

**What**: `overseer role invoke <role_id>` command.

#### R12: Expose Skills as MCP Tools

**What**: Allow skill invocation via MCP protocol.

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent governance not enforcing VoiceStudio policies | High | Medium | R1: Create role mapping |
| Legacy code causing confusion | Medium | Low | R3: Remove legacy files |
| OpenMemory integration incomplete | High | Medium | R6: Implement MCP client |
| Context allocation not governed | Medium | Medium | R7: Connect to AgentRegistry |
| Systems diverging further | Medium | High | Establish integration contracts |

---

## 10. Action Items

### Immediate (This Week)

- [ ] **TASK-0009**: Create AgentRole ↔ RoleConfig mapping (R1)
- [ ] **TASK-0010**: Add ledger/telemetry fields to ContextBundle (R2)
- [ ] **TASK-0011**: Remove legacy context manager files (R3)

### Short-Term (This Sprint)

- [ ] **TASK-0012**: Wire onboarding to AgentRegistry (R4)
- [ ] **TASK-0013**: Split inject_context.py into focused modules (R5)

### Medium-Term (Next Sprint)

- [ ] **TASK-0014**: Implement OpenMemory MCP client integration (R6)
- [ ] **TASK-0015**: Connect ContextManager to AgentRegistry (R7)
- [ ] **TASK-0016**: Add MCP health check script (R8)

---

## Appendix A: Architecture Diagram Key

```
✅ Complete - Fully implemented and tested
⚠️ Partial - Some functionality missing
❌ None - Not implemented
```

## Appendix B: File Locations Summary

| System | Primary Location | Config Location |
|--------|------------------|-----------------|
| Context Manager | `tools/context/` | `tools/context/config/` |
| Role System | `.cursor/prompts/` | `tools/onboarding/config/roles.json` |
| Agent Governance | `tools/overseer/agent/` | YAML policies |
| Onboarding | `tools/onboarding/` | `tools/onboarding/config/` |
| Overseer CLI | `tools/overseer/cli/` | N/A |
| Skills | `.cursor/skills/` | N/A |
| MCP | `cursor.mcp.json` | N/A |
| Hooks | `.cursor/hooks/` | `.cursor/hooks.json` |

---

**Document Status**: COMPLETE  
**Next Review**: After Priority 1 items completed  
**Owner**: Overseer (Role 0) + System Architect (Role 1)
