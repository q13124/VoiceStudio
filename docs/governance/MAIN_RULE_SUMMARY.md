# Main Rule Summary - NO Stubs, Placeholders, Bookmarks, or Tags
## VoiceStudio Quantum+ - The Absolute Rule

**Status:** 🚨 **CRITICAL - HIGHEST PRIORITY - MANDATORY**  
**Applies To:** EVERYTHING in the VoiceStudio project  
**Last Updated:** 2025-01-28

---

## 🎯 The Rule

**EVERY task must be 100% complete before moving to the next task.**

**NO exceptions. NO shortcuts. NO placeholders. NO bookmarks. NO tags. NO stubs.**

**This applies to:**
- ✅ All code files (C#, Python, XAML, JSON, etc.)
- ✅ All documentation files (Markdown, text, etc.)
- ✅ All configuration files
- ✅ All comments in code
- ✅ All UI text and labels
- ✅ All error messages
- ✅ **EVERYTHING**

---

## 📋 Quick Reference - Forbidden Patterns

### Bookmarks (FORBIDDEN):
- `TODO`, `FIXME`, `NOTE`, `HACK`, `REMINDER`, `XXX`, `WARNING`, `CAUTION`, `BUG`, `ISSUE`, `REFACTOR`, `OPTIMIZE`, `REVIEW`, `CHECK`, `VERIFY`, `TEST`, `DEBUG`, `DEPRECATED`, `OBSOLETE`

### Placeholders (FORBIDDEN):
- `NotImplementedException`, `NotImplementedError`, `[PLACEHOLDER]`, `{"mock": true}`, `return {}`, `return []`, `return null` (without implementation)

### Stubs (FORBIDDEN):
- `pass`-only functions (Python), empty methods, functions that just return

### Tags (FORBIDDEN):
- `#TODO`, `#FIXME`, `#PLACEHOLDER`, `[IN PROGRESS]`, `[PENDING]`, `[WIP]`

### Status Words/Phrases (FORBIDDEN):
- "pending", "incomplete", "unfinished", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc"
- "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress"

---

## 📚 Complete Documentation

**For the complete, expanded rule with ALL forbidden terms, patterns, synonyms, and variations, see:**
- **`docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md`** - **COMPREHENSIVE RULE**

**For enforcement recommendations, see:**
- **`docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md`** - How to guarantee 100% compliance

**For summary rules, see:**
- `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - Summary rule
- `docs/governance/NO_MOCK_OUTPUTS_RULE.md` - Mock outputs rule
- `docs/governance/ALL_PROJECT_RULES.md` - All project rules

---

## ✅ What is Required

- ✅ Full implementation of all methods
- ✅ All functionality working and tested
- ✅ All error cases handled
- ✅ All edge cases considered
- ✅ Production-ready code
- ✅ Real values, real file I/O, real API wiring
- ✅ Complete function bodies, classes, or components
- ✅ UI and backend wired together with real bindings or API calls
- ✅ Verifiable and testable functionality

---

## 🚨 Consequences

**If violations found:**
1. Task marked as INCOMPLETE
2. Worker must complete before moving on
3. Commit rejected (if using automated checks)
4. Release blocked (if found in release candidate)
5. No credit for partial work

---

## 🔧 Enforcement

**Automated:**
- Pre-commit hooks
- CI/CD pipeline checks
- Verification scripts

**Manual:**
- Overseer review
- Worker self-verification
- Code reviews

**See:** `docs/governance/RULE_ENFORCEMENT_RECOMMENDATIONS.md` for complete enforcement strategy.

---

## 🎯 Remember

**If it's not 100% complete and tested, it's NOT done.**

**Don't move on. Complete it first.**

**Quality over speed. Completeness over progress.**

**This rule applies to ALL workers, ALL tasks, ALL the time.**

**NO EXCEPTIONS.**

---

**This is the MAIN RULE for the entire VoiceStudio project.**

