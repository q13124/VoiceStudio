# ADR-003: Agent Governance Framework

## Status

Accepted

## Date

2026-01-25

## Context

VoiceStudio uses AI agents for both development assistance (Cursor/AI agents working on codebase) and runtime automation (user-facing automation within the app). Without proper governance, these agents could:

1. **Security risks**: Access sensitive files, execute arbitrary commands, leak data
2. **Reliability risks**: Make uncontrolled changes, cause cascading failures
3. **Audit risks**: Actions untraceable, no accountability, no replay capability
4. **Control risks**: No emergency stop, no approval gates for dangerous actions

We need a unified governance framework that provides:
- Agent identity and lifecycle management
- Policy-based access control
- Audit logging with replay capability
- Human-in-the-loop approval for high-risk actions
- Circuit breakers and kill switches for emergencies

## Decision

### 1. Architecture

We implement a layered governance architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     C# Frontend (WinUI 3)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Permissions  │  │   Approval   │  │     Log Viewer       │  │
│  │     UI       │  │   Dialogs    │  │   + Replay Export    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ IPC (Named Pipes / gRPC)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Python Backend                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Tool Gateway                           │  │
│  │  (The ONLY place side effects happen)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Policy  │ │ Approval│ │ Circuit │ │  Kill   │ │  Audit  │  │
│  │ Engine  │ │ Manager │ │ Breaker │ │ Switch  │ │ Logger  │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Key Components

#### Agent Identity System (`tools/overseer/agent/identity.py`)
- Unique agent ID per run
- Machine ID (hardware fingerprint)
- User ID
- Role declaration (Coder, Tester, Support, Updater, DataImporter, Overseer)
- Lifecycle states (Created → Running → Paused → AwaitingApproval → Completed → Quarantined)
- Config hash for version pinning

#### Policy Engine (`tools/overseer/agent/policy_engine.py`)
- Central policy file in YAML (`policies/base_policy.yaml`)
- Risk tiers (low, medium, high, critical)
- Tool restrictions by path/executable/domain
- Role-based overrides
- Safe zone definitions

#### Tool Gateway (`tools/overseer/agent/tool_gateway.py`)
- Single point of enforcement for all agent actions
- Policy evaluation before execution
- Automatic audit logging
- Approval flow integration

#### Approval System (`tools/overseer/agent/approval_manager.py`)
- Human-in-the-loop for high-risk actions
- Request/approve/deny workflow
- Timeout and expiration handling
- C# approval dialog integration

#### Circuit Breaker (`tools/overseer/agent/circuit_breaker.py`)
- Automatic quarantine on repeated failures/denials
- Exponential backoff
- Half-open state for recovery testing

#### Kill Switch (`tools/overseer/agent/kill_switch.py`)
- Emergency stop at agent/session/machine/global levels
- Persistent state
- Immediate enforcement

#### Safe Zones (`tools/overseer/agent/safe_zones.py`)
- Protected paths (Program Files, Windows, startup folders)
- Protected registry keys
- Automatic violation detection

#### Manifest Signing (`tools/overseer/agent/manifest_signer.py`)
- HMAC-SHA256 signing of configurations
- Tamper detection
- Release channels (stable/beta/nightly)

### 3. Risk Tiers

| Tier | Description | Requires Approval | Examples |
|------|-------------|-------------------|----------|
| Low | Read-only analysis | No | ReadFile, AnalyzeCode |
| Medium | Project file writes | No | WriteFile, RunTests |
| High | Process execution, network | Yes | RunProcess, HttpRequest |
| Critical | System modifications | Yes + explicit consent | RegistryWrite, service changes |

### 4. Integration Points

#### C# Frontend
- `IApprovalService` / `ApprovalService` for approval handling
- `AgentApprovalDialog.xaml` for user interaction
- Log viewer and replay bundle export

#### Python Backend
- Tool Gateway as the enforcement layer
- Audit Logger with append-only storage
- Policy Engine for access control

#### IPC
- Named pipes or gRPC over localhost
- Correlation IDs for end-to-end tracing

## Consequences

### Positive

1. **Security**: All agent actions go through policy enforcement
2. **Auditability**: Complete trail of all actions with replay capability
3. **Control**: Emergency stops at multiple levels
4. **Flexibility**: Policy-as-code enables runtime configuration
5. **Extensibility**: New tools easily added via Tool Gateway

### Negative

1. **Complexity**: Significant new code surface
2. **Performance**: Gateway adds latency to every action
3. **Maintenance**: Policies need ongoing tuning

### Mitigation

1. Phased rollout with comprehensive testing
2. Async audit logging to minimize latency impact
3. Policy validation in CI to catch issues early

## Alternatives Considered

### 1. Simple Allowlist
Just a list of allowed tools/paths. Rejected because:
- No risk-based differentiation
- No approval workflow
- No circuit breaker / kill switch

### 2. External Governance Service
Separate microservice for governance. Rejected because:
- Adds deployment complexity
- Network latency for every action
- Single point of failure

### 3. Per-Agent Policies
Each agent has its own policy file. Rejected because:
- Duplication
- Inconsistent enforcement
- Harder to audit

## References

- [Implementation Plan](../../../.cursor/plans/agent_governance_framework_d95bce1a.plan.md)
- [Base Policy](../../../tools/overseer/agent/policies/base_policy.yaml)
- [Governance Tests](../../../tests/governance/)
