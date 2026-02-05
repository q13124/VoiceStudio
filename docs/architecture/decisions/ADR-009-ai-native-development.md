# ADR-009: AI-Native Development Patterns

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio is developed with AI agent assistance. Patterns are needed to:
- Maximize AI effectiveness on complex tasks
- Maintain code quality and consistency
- Preserve human oversight and control
- Enable specialized AI capabilities per domain

Traditional development approaches don't leverage AI capabilities fully, while unrestricted AI can introduce quality issues.

## Options Considered

1. **Traditional development** - AI as code completion only
   - Pros: Full human control, predictable
   - Cons: Slow, doesn't leverage AI reasoning

2. **AI-assisted** - AI suggests, human implements
   - Pros: Human in loop, quality maintained
   - Cons: Bottleneck on human implementation

3. **AI-native** - Role-based agents with governance
   - Pros: Leverages AI fully, specialized expertise, scalable
   - Cons: Requires governance, validation, oversight

## Decision

**Option 3: AI-native development** with role-based specialization and governance.

### Role System

8 specialized roles with distinct responsibilities:

| Role | ID | Focus Area |
|------|-----|------------|
| Overseer | 0 | Coordination, state management, task assignment |
| System Architect | 1 | Boundaries, contracts, ADRs |
| Build & Tooling | 2 | CI/CD, build system, tooling |
| UI Engineer | 3 | WinUI 3, MVVM, accessibility |
| Core Platform | 4 | Storage, jobs, runtime |
| Engine Engineer | 5 | ML inference, quality metrics |
| Release Engineer | 6 | Installer, packaging, releases |
| Debug Agent | 7 | Error diagnosis, debugging |

### Governance Mechanisms

1. **State Protocol** (`.cursor/STATE.md`)
   - Tracks phase, active task, blockers
   - Agents must read state before modifications
   - Context acknowledgment required

2. **Closure Protocol**
   - Tasks require proof before closure
   - Build/test verification
   - Skeptical Validator review

3. **Skeptical Validator**
   - Independent verification of completion claims
   - Runs acceptance criteria checks
   - Reports PASS/FAIL with evidence

4. **Rule Governance**
   - Only humans can modify `.cursor/rules/`
   - Agents propose, humans approve rule changes

### Implementation Patterns

**Onboarding Packets**: Each role receives context bundle (P.A.R.T.)
- **P**roject state
- **A**ctive task
- **R**ules relevant to role
- **T**elemetry and issues

**Role Invocation**: Via skills or prompts
```
/role-overseer   # Switch to Overseer context
/role-debug      # Switch to Debug Agent context
```

**Quality Gates**: Proof required at each phase
- Build succeeds
- Tests pass
- Lints clean
- Acceptance criteria met

## Implementation Evidence

- `docs/governance/roles/ROLE_*_GUIDE.md` - Role documentation
- `.cursor/prompts/ROLE_*_PROMPT.md` - Role prompts
- `.cursor/skills/roles/*/SKILL.md` - Role skills
- `.cursor/STATE.md` - Session state protocol
- `tools/overseer/` - Governance tooling

## Consequences

### Positive
- Specialized expertise per domain
- Scalable AI development capacity
- Quality maintained via governance
- Human oversight preserved
- Clear responsibility assignment

### Negative
- Complexity of role system
- Learning curve for role switching
- Governance overhead
- Context management needed

### Neutral
- Requires role documentation maintenance
- Validation processes take time
- Some tasks may span multiple roles
