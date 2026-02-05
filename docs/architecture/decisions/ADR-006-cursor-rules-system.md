# ADR-006: Enhanced Cursor Rules System

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio uses Cursor IDE with agent-based development. A comprehensive rules system is needed to:
- Guide agent behavior consistently
- Enforce coding conventions
- Maintain quality standards
- Prevent anti-patterns

Without structured rules:
- Agents may make inconsistent decisions
- Code quality varies across sessions
- Architectural boundaries may be violated
- Security practices may be overlooked

## Options Considered

1. **Single AGENTS.md** - All rules in one file
   - Pros: Single source, easy to find
   - Cons: Large file, hard to maintain, no categorization

2. **Modular .mdc rules** - Categorized rules in `.cursor/rules/`
   - Pros: Organized, maintainable, focused rules
   - Cons: Harder to discover, multiple files

3. **Hybrid approach** - AGENTS.md index with modular rules
   - Pros: Best of both - discoverable index + modular details
   - Cons: Need to maintain both

## Decision

**Option 3: Hybrid approach** with the following structure:

### AGENTS.md (Index)
- Lists all required rules with paths
- Professional standard section
- Build/test commands
- Project structure overview

### Modular Rules (`.cursor/rules/`)

| Category | Purpose | Examples |
|----------|---------|----------|
| `core/` | Fundamental project rules | architecture, anti-drift, project-context |
| `workflows/` | Process and lifecycle rules | git-conventions, closure-protocol, testing |
| `security/` | Security and safety rules | secure-coding, api-key-management, mcp-security |
| `quality/` | Code quality rules | no-suppression, repo-hygiene, linting |
| `mcp/` | MCP server usage rules | mcp-usage, tool-selection |
| `languages/` | Language-specific rules | csharp, python, xaml |

### Rule Format (.mdc)

```markdown
# Rule Title

## Description
What this rule covers

## Requirements
- Specific requirements
- DO and DON'T patterns

## Examples
Good and bad examples

## Integration
How this rule relates to others
```

### alwaysApply vs Agent-Requestable

- **alwaysApply**: Core rules loaded for every interaction
- **Agent-Requestable**: Contextual rules loaded on demand

## Implementation Evidence

- `AGENTS.md` - Rule index (root)
- `.cursor/rules/core/` - 7 core rules
- `.cursor/rules/workflows/` - 15 workflow rules
- `.cursor/rules/security/` - 3 security rules
- `.cursor/rules/quality/` - 5 quality rules
- `.cursor/rules/mcp/` - 2 MCP rules

## Consequences

### Positive
- Rules organized by concern
- Easy to maintain individual rules
- AGENTS.md provides quick reference
- New rules easily added to appropriate category
- Rules can be toggled per-interaction

### Negative
- Multiple files to maintain
- Need to sync AGENTS.md with rule changes
- Agents must read multiple files

### Neutral
- Learning curve for rule system
- Rule governance needed (who can modify)
