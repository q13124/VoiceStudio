# Multi-Phase Reasoning (Plan → Execute → Reflect)

**Purpose**: Formalize the three-phase pattern for agent workflows. Complements [closure-protocol](../../.cursor/rules/workflows/closure-protocol.mdc) Step 0 (invoke Skeptical Validator).

---

## Three-Phase Pattern

1. **Plan**: Break the task into steps (use Planning mode or outline first).
2. **Execute**: Implement steps (Agent mode; use tools, read files, run commands).
3. **Reflect**: Self-critique and verify (Validator or self-check; compare to acceptance criteria).

---

## Integration

- **Closure Protocol**: Before marking a task complete, run Phase 3 (Reflect) via Skeptical Validator (Step 0) or a self-check against the task brief.
- **Role Prompts**: Each role prompt includes a ReAct reasoning pattern (Thought → Action → Observation); use it within Execute and Reflect.
- **Documentation**: This doc is the canonical description of the three-phase pattern; a rule file may be added by the user if desired.

---

## Changelog

| Date       | Change |
|------------|--------|
| 2026-01-28 | Initial: Plan → Execute → Reflect pattern documented. |
