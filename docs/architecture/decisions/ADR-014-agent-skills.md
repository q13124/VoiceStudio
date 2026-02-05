# ADR-014: Agent Skills Integration

## Status

**Accepted** (2026-02-04)

## Context

Cursor agents can use skills to enhance their capabilities. Skills are needed for:
- Role-specific onboarding and context
- Project-specific verification workflows
- Reusable tool invocation patterns
- Specialized domain knowledge

Without skills:
- Each session requires manual context setup
- Verification steps are repeated manually
- Role switching is cumbersome

## Options Considered

1. **No skills** - Agents use only built-in tools
   - Pros: Simple, no maintenance
   - Cons: Repeated context setup, no specialization

2. **SKILL.md pattern** - Skills as markdown with instructions
   - Pros: Human-readable, version-controlled, easy to modify
   - Cons: Agents must read and follow instructions

3. **MCP tools** - Skills as MCP server tools
   - Pros: Programmatic, type-safe, integrated
   - Cons: More complex to create, requires MCP server

## Decision

**Option 2: SKILL.md pattern** for project skills.

### Skill Structure

Each skill is a markdown file with:

```markdown
# Skill Title

## Trigger
When to invoke this skill

## Instructions
Step-by-step instructions for the agent

## Prerequisites
Required context or tools

## Outputs
Expected artifacts or results
```

### Skill Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Roles | `.cursor/skills/roles/*/SKILL.md` | Role onboarding and context |
| Tools | `.cursor/skills/tools/*/SKILL.md` | Verification and tooling |

### Role Skills

Each role has a skill that:
1. Reads the role prompt
2. Generates onboarding packet
3. Sets role-specific context
4. Activates role capabilities

### Tool Skills

| Skill | Purpose |
|-------|---------|
| `verify` | Run verification script |
| `gate-status` | Check gate status |
| `ledger-validate` | Validate quality ledger |
| `completion-guard` | Check completion evidence |
| `onboard` | Generate role packets |

### Discovery

Skills are discovered via `<available_skills>` in system context:
- Agent sees skill descriptions
- Reads full skill when relevant
- Follows instructions immediately

## Implementation Evidence

- `.cursor/skills/roles/*/SKILL.md` - 9 role skills
- `.cursor/skills/tools/*/SKILL.md` - 5 tool skills
- `.cursor/prompts/ROLE_*_PROMPT.md` - Role prompts
- `tools/overseer/` - Skill implementations

## Consequences

### Positive
- Skills are version-controlled and reviewable
- Easy to modify without code changes
- Human-readable format
- Role switching is streamlined
- Verification is consistent

### Negative
- Agents must read and interpret instructions
- Skills depend on agent comprehension
- No type safety for inputs/outputs

### Neutral
- Skills can call MCP tools for execution
- Skill quality affects agent effectiveness
- Need to maintain skill documentation
