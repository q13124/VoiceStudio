# ADR-005: Context Management System

## Status

**Accepted** (2026-02-04)

## Context

AI agents require structured context injection for effective operation. Context includes:
- Project state (phase, active task, blockers)
- Task briefs and acceptance criteria
- Quality ledger and issues
- Rules and memory
- Git context

Without a context manager:
- Agents may receive irrelevant or excessive context
- Context budget overruns degrade model performance
- Role-specific context not optimized
- No progressive disclosure based on task needs

## Options Considered

1. **Static context** - Fixed context per role
   - Pros: Simple, predictable
   - Cons: No adaptability, wastes budget on irrelevant context

2. **Dynamic context manager** - Adaptive context based on task and role
   - Pros: Optimal context per task, respects budgets, role-aware
   - Cons: More complex implementation

3. **External context service** - Separate MCP-based context service
   - Pros: Decoupled, reusable across tools
   - Cons: Network overhead, additional infrastructure

## Decision

**Option 2: Dynamic context manager** with the following architecture:

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│              Context Management System                   │
│                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│  │ Context       │  │ Source        │  │ Bundle      │ │
│  │ Allocator     │→ │ Adapters      │→ │ Composer    │ │
│  │ (budget mgmt) │  │ (state,task,  │  │ (P.A.R.T.)  │ │
│  │               │  │  rules,git)   │  │             │ │
│  └───────────────┘  └───────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 1. Context Allocator (`tools/context/core/allocator.py`)
- Priority-aware budget allocation
- Progressive disclosure based on context levels:
  - **HIGH**: state, task (always loaded)
  - **MID**: brief, ledger, issues (if budget allows)
  - **LOW**: rules, memory, git (if budget allows)
- Role-specific weights for source prioritization

### 2. Source Adapters (`tools/context/sources/`)
- Modular adapters for each context source
- Standardized `SourceResult` output
- Supports: state, task, ledger, rules, git, memory, telemetry

### 3. Bundle Composer
- Composes P.A.R.T. context bundles:
  - **P**roject state
  - **A**ctive task
  - **R**ules
  - **T**elemetry
- Role-specific composition rules

### Role Configuration

Roles defined in `tools/context/config/roles/*.json`:
- Overseer, System Architect, Build Tooling
- UI Engineer, Core Platform, Engine Engineer
- Release Engineer, Debug Agent

Each role has:
- Maximum token budget
- Source weights (priority per source)
- Required context sources

## Implementation Evidence

- `tools/context/` - Context management module
- `tools/context/core/allocator.py` - Budget allocation with progressive disclosure
- `tools/context/core/models.py` - ContextBundle, SourceResult models
- `tools/context/sources/` - Source adapters (state, task, ledger, etc.)
- `tools/context/config/roles/` - Role-specific configurations
- `.cursor/rules/workflows/context-strategy.mdc` - Usage guidance

## Consequences

### Positive
- Optimal context allocation per task and role
- Budget enforcement prevents context overruns
- Progressive disclosure loads most relevant context first
- Role-specific optimization improves agent effectiveness
- Extensible via new source adapters

### Negative
- Increased complexity in context pipeline
- Role configuration requires maintenance
- Debugging context issues more difficult

### Neutral
- Learning curve for understanding context system
- Requires periodic tuning of weights and budgets
