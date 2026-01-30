# ADR-015: Architecture Integration Contract

**Status:** Accepted  
**Date:** 2026-01-28  
**Decision Makers:** System Architect (Role 1), Overseer (Role 0)  
**Related ADRs:** ADR-005 (Context Management), ADR-014 (Agent Skills), ADR-003 (Agent Governance)  
**Source:** [ARCHITECTURE_INTEGRATION_REVIEW_2026-01-28.md](../../reports/verification/ARCHITECTURE_INTEGRATION_REVIEW_2026-01-28.md)

## Context

VoiceStudio has four major subsystems (Context Manager, Role System, Onboarding, Agent Governance) that operate semi-independently. The Architecture Integration Plan wires them together. This ADR defines the integration contract: responsibilities, boundaries, and failure modes so peers can approve execution and future changes stay consistent.

## Responsibilities

| System | Primary Responsibility | Owning Role |
|--------|------------------------|-------------|
| **Context Manager** | Assemble and budget context bundles from sources (state, task, ledger, rules, memory, git, telemetry). | N/A (tooling) |
| **Role System** | Provide role prompts, guides, and config (0–6 + Skeptical Validator) as source of truth for identity. | Overseer |
| **Onboarding** | Assemble role onboarding packets; optionally register agents with AgentRegistry when enabled. | Overseer |
| **Agent Governance** | Enforce policies per agent identity; PolicyEngine uses VoiceStudio role id via a single mapping layer to AgentRole. | Overseer |

## Boundaries

- **Context Manager** does not own role semantics; it accepts `role` as an opaque hint for budget profiles and optional registry validation. It does not call Onboarding or Skills.
- **Onboarding** calls RoleRegistry and, when enabled, AgentRegistry. It does not call Context Manager or PolicyEngine.
- **Agent Governance** (PolicyEngine, ToolGateway) consumes VoiceStudio role id and maps to AgentRole via `tools/overseer/agent/role_mapping.py` only. It does not depend on Onboarding or Context Manager for identity.
- **Hooks** orchestrate: detect role → optionally onboard → build AllocationContext with role → call ContextManager.allocate. Hooks do not enforce policy; they only inject context.

## Failure Modes

| Failure | Behavior | Contract |
|---------|----------|----------|
| **AgentRegistry unavailable** | Onboarding and Context Manager treat registry as optional. No hard failure; log and continue. Offline/local-first preserved. | All registry use behind explicit flag or env. |
| **Role id unknown to mapping** | `role_to_agent_role` returns a safe default (e.g. CODER) or raises a documented exception; callers handle. | Mapping module is the single place for role id → AgentRole. |
| **MCP (e.g. OpenMemory) unavailable** | Memory adapter falls back to file/openmemory.md; log once and continue. | Adapter returns same shape; no behavioral change for bundle consumers. |
| **Legacy context code removed** | Only the path `core/manager` + `*_adapter.py` is used. No imports of `allocator/` or `*_reader.py`. | Grep and CI confirm no references; removal is irreversible without re-adding code. |

## Options Considered

1. **No contract (implicit boundaries only)**  
   Pros: No doc overhead. Cons: Divergence and unclear failure handling.

2. **One-page Integration Contract as ADR (chosen)**  
   Pros: Single source of truth; peer approval gate; traceable. Cons: One extra ADR to maintain.

3. **Appendix to ADR-005 or ADR-014**  
   Pros: Fewer files. Cons: ADR-005 is context-only; ADR-014 is skills-only; this contract spans four subsystems.

## Decision

Adopt **ADR-015 as the Architecture Integration Contract**. It defines responsibilities, boundaries, and failure modes for Context Manager, Role System, Onboarding, and Agent Governance. The plan in [ARCHITECTURE_INTEGRATION_REVIEW_2026-01-28.md](../../reports/verification/ARCHITECTURE_INTEGRATION_REVIEW_2026-01-28.md) is executed under this contract. All integration work (role mapping, ContextBundle extensions, legacy removal, onboarding–registry, hook split, OpenMemory MCP, context–registry, MCP health script, Proof Index) conforms to these boundaries and failure modes.

## Consequences

- Clear ownership and boundaries reduce drift between subsystems.
- Failure modes are explicit; offline and local-first behavior are preserved.
- Peer review can use this ADR as the approval checklist for the integration plan.
