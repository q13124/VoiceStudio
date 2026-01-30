# Cursor Master Instructions for VoiceStudio Quantum+
## Complete Integration & Implementation Guide

> **Deprecation (2026-01-30):** This document describes the legacy ChatGPT-era "Overseer + 6 Workers" setup. For current governance use `.cursor/rules/*.mdc`, [ROLE_GUIDES_INDEX](../governance/ROLE_GUIDES_INDEX.md), and [PROJECT_HANDOFF_GUIDE](../governance/PROJECT_HANDOFF_GUIDE.md). Legacy prompts (CURSOR_AGENT_GUIDELINES_V2, OVERSEER_SYSTEM_PROMPT_V2, WORKER_AGENT_PROMPTS) are in `docs/archive/legacy_worker_system/design/`.

**Version:** 2.0  
**Date:** 2025  
**Purpose:** Master document for Cursor to integrate new UI with existing code

---

## 🎯 YOUR MISSION

**Integrate the new VoiceStudio Quantum+ UI design with existing VoiceStudio code while preserving 100% of existing functionality.**

**Key Principle:** INTEGRATE, DON'T REPLACE

---

## 📚 START HERE - READ THESE FIRST

### 1. Critical Documents (Read in Order)

1. **.cursor/rules/*.mdc** - **CRITICAL** - Current operational rules
2. **[ROLE_GUIDES_INDEX](../governance/ROLE_GUIDES_INDEX.md)** - Current 8-role governance system
3. **SKELETON_INTEGRATION_GUIDE.md** - Step-by-step guide to integrate skeleton code
4. **SKELETON_FILES_MAPPING.md** - Complete file-by-file mapping reference
5. **VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md** - Master specification

**Archived legacy documents** (historical reference only):
- [MEMORY_BANK.md](../archive/legacy_worker_system/design/MEMORY_BANK.md) - Legacy critical info
- [COMPLETE_INTEGRATION_SUMMARY.md](../archive/legacy_worker_system/design/COMPLETE_INTEGRATION_SUMMARY.md) - Legacy integration overview
- [CURSOR_AGENT_GUIDELINES_V2.md](../archive/legacy_worker_system/design/CURSOR_AGENT_GUIDELINES_V2.md) - Legacy agent system
- [INTEGRATION_GUIDE.md](../archive/legacy_worker_system/design/INTEGRATION_GUIDE.md) - Legacy integration patterns
- [CURSOR_INTEGRATION_INSTRUCTIONS.md](../archive/legacy_worker_system/design/CURSOR_INTEGRATION_INSTRUCTIONS.md) - Legacy integration process

### 2. Reference Documents

- **PANEL_IMPLEMENTATION_GUIDE.md** - Complete guide for implementing 100+ panels
- **INNOVATIVE_ADVANCED_PANELS_CATALOG.md** - 9 advanced panels catalog
- **VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md** - Master specification
- **OVERSEER_SYSTEM_PROMPT_V2.md** (archived: [legacy_worker_system/design/](../archive/legacy_worker_system/design/)) - Legacy Overseer prompt
- **WORKER_AGENT_PROMPTS.md** (archived) - Legacy worker prompts
- **ADVANCED_UI_UX_FEATURES.md** - Advanced features roadmap
- **AI_INTEGRATION_GUIDE.md** - AI integration (3 AIs + Overseer)
- **ENGINE_RECOMMENDATIONS.md** - Backend engine choices

---

## 🚨 CRITICAL RULES (NON-NEGOTIABLE)

### Preservation Rules
1. **NEVER delete existing files**
2. **NEVER remove existing functionality**
3. **NEVER remove existing data bindings**
4. **NEVER remove existing event handlers**
5. **NEVER replace existing code unnecessarily**

### Architecture Rules
1. **PanelHost is MANDATORY** - Never replace with raw Grids
2. **MVVM separation is MANDATORY** - Each panel = .xaml + .xaml.cs + ViewModel.cs
3. **Design tokens are MANDATORY** - Use VSQ.* resources, no hardcoded values
4. **Complexity is REQUIRED** - This is a professional DAW-grade app

### Integration Rules
1. **ADD new alongside existing** - Don't replace
2. **PRESERVE existing structure** - Enhance, don't rebuild
3. **TEST existing after each change** - Verify nothing broke
4. **REPORT conflicts immediately** - Don't proceed with conflicts

---

## 👥 AGENT SETUP

### Overseer Agent

**Copy this prompt into Cursor's Overseer/Architect agent:**
- See: `CURSOR_AGENT_GUIDELINES_V2.md` → Overseer System Prompt section (copy entire contents)
- Alternative: `OVERSEER_SYSTEM_PROMPT_V2.md` (use if V2 guidelines not available)

**Key Responsibilities:**
- Enforce design spec
- Preserve existing functionality
- Coordinate 6 workers
- Prevent simplifications
- Verify integration quality

### Worker Agents (6 Workers)

**Copy individual prompts into each worker:**
- **Worker 1:** See `CURSOR_AGENT_GUIDELINES_V2.md` → Worker 1: Shell & Navigation section
- **Worker 2:** See `CURSOR_AGENT_GUIDELINES_V2.md` → Worker 2: Themes & Visual Layer section
- **Worker 3:** See `CURSOR_AGENT_GUIDELINES_V2.md` → Worker 3: Panel Scaffolding & Registry section
- **Worker 4:** See `CURSOR_AGENT_GUIDELINES_V2.md` → Worker 4: Plugin System & MCP section
- **Worker 5:** See `CURSOR_AGENT_GUIDELINES_V2.md` → Worker 5: AI Coordination + HUD section
- **Worker 6:** See `CURSOR_AGENT_GUIDELINES_V2.md` → Worker 6: Backend API & Persistence section

**Alternative:** `WORKER_AGENT_PROMPTS.md` (original version, use if V2 not available)

---

## 🔄 INTEGRATION WORKFLOW

### Phase 0: Pre-Integration (Overseer)

**Command:**
```
"Before making any changes, create a complete inventory:
1. List all existing .xaml files with full paths
2. List all existing .cs files with full paths
3. Document all existing ViewModels and their properties
4. Document all existing services and their methods
5. Document all existing data bindings
6. Document all existing event handlers
7. Save inventory to PRESERVATION_INVENTORY.md"
```

### Phase 1: Foundation (Worker 1)

**Tasks:**
- Merge DesignTokens.xaml (ADD new, KEEP existing)
- Update MainWindow.xaml (ADD new structure, PRESERVE existing)
- Preserve App.xaml.cs initialization
- Verify compilation

**See:** `INTEGRATION_GUIDE.md` → Step 2 & 3

### Phase 2-4: Panels (Workers 2-4)

**Tasks:**
- Update each panel (PRESERVE existing, ADD new)
- Update ViewModels (PRESERVE existing, ADD IPanelView)
- Verify existing functionality works
- Verify new features work

**See:** `INTEGRATION_GUIDE.md` → Step 4

### Phase 5: Advanced Controls (Worker 5)

**Tasks:**
- Integrate PanelStack (new file, no conflicts)
- Integrate CommandPalette (new file, overlay)
- Wire keyboard shortcuts
- Test integration

**See:** `INTEGRATION_GUIDE.md` → Step 5

### Phase 6: Services (Worker 6)

**Tasks:**
- Add new services (new files)
- Register services (preserve existing registration)
- Integrate AI services
- Add automation hooks

**See:** `INTEGRATION_GUIDE.md` → Step 6

---

## ✅ VERIFICATION CHECKLIST

### After Each Phase

**Overseer Must Verify:**

**Compilation:**
- [ ] Solution builds without errors
- [ ] All design tokens resolve
- [ ] All references resolve

**Functionality:**
- [ ] All existing features work
- [ ] All new features work
- [ ] No runtime errors

**Preservation:**
- [ ] All existing files exist
- [ ] All existing controls exist
- [ ] All existing bindings work
- [ ] All existing handlers work

**Structure:**
- [ ] File structure maintained
- [ ] MVVM separation maintained
- [ ] PanelHost system intact

---

## 🎯 SUCCESS CRITERIA

**Integration is successful when:**

- ✅ 100% of existing files preserved
- ✅ 100% of existing functionality works
- ✅ 100% of new features work
- ✅ Zero compilation errors
- ✅ Zero runtime errors
- ✅ Design tokens resolve
- ✅ File structure maintained
- ✅ MVVM separation maintained
- ✅ PanelHost system intact

---

## 🚨 EMERGENCY PROTOCOL

**If existing functionality breaks:**

1. **STOP** all workers immediately
2. **REVERT** to last known good state
3. **INVESTIGATE** what broke
4. **FIX** while preserving existing
5. **VERIFY** existing works before proceeding

**Overseer Command:**
```
"EMERGENCY STOP. All workers halt.
Issue: [describe]
Action: Revert to [commit/state]
Investigation: [what to check]
Resolution: [how to fix]"
```

---

## 📋 QUICK REFERENCE

### Do's ✅
- ✅ Read existing files first
- ✅ Document existing functionality
- ✅ Preserve existing code
- ✅ Add new alongside existing
- ✅ Test after each change
- ✅ Report conflicts immediately
- ✅ Use design tokens
- ✅ Maintain MVVM separation
- ✅ Keep PanelHost system

### Don'ts ❌
- ❌ Delete existing files
- ❌ Remove existing functionality
- ❌ Replace existing code
- ❌ Remove existing bindings
- ❌ Remove existing handlers
- ❌ Simplify or collapse
- ❌ Hardcode values
- ❌ Merge View/ViewModel
- ❌ Replace PanelHost with Grid

---

## 🔗 DOCUMENT RELATIONSHIPS

```
CURSOR_MASTER_INSTRUCTIONS.md (THIS FILE)
├── CURSOR_AGENT_GUIDELINES.md (Agent system overview)
│   ├── OVERSEER_SYSTEM_PROMPT_V2.md (Overseer prompt)
│   └── WORKER_AGENT_PROMPTS.md (Worker prompts)
├── INTEGRATION_GUIDE.md (Integration patterns)
├── PRESERVATION_CHECKLIST.md (Preservation guide)
├── CURSOR_INTEGRATION_INSTRUCTIONS.md (Step-by-step)
├── VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md (Master spec)
├── MEMORY_BANK.md (Critical information)
├── ADVANCED_UI_UX_FEATURES.md (Future features)
├── AI_INTEGRATION_GUIDE.md (AI integration)
└── ENGINE_RECOMMENDATIONS.md (Backend engines)
```

---

## 💡 KEY REMINDERS

1. **Preservation is Priority #1** - Never lose existing functionality
2. **Integration = Merging** - Add new alongside existing, don't replace
3. **When in doubt, preserve** - Better to have duplicate than lose existing
4. **Test existing after each change** - Verify nothing broke
5. **Quality and stability > speed** - Professional app requires quality

**Remember:** The goal is to have BOTH existing functionality AND new UI working together seamlessly.

---

## 🚀 GETTING STARTED

### For Cursor (Overseer)

1. Read `MEMORY_BANK.md` completely
2. Read `CURSOR_AGENT_GUIDELINES.md` completely
3. Read `INTEGRATION_GUIDE.md` completely
4. Set up 6 worker agents with prompts from `WORKER_AGENT_PROMPTS.md`
5. Start with Phase 0: Pre-Integration Audit
6. Proceed phase by phase, verifying after each

### For Each Worker

1. Read your specific prompt from `WORKER_AGENT_PROMPTS.md`
2. Read `PRESERVATION_CHECKLIST.md`
3. Read relevant section in `INTEGRATION_GUIDE.md`
4. Document existing code before changes
5. Preserve existing, add new alongside
6. Test after each change
7. Report to Overseer

---

## 📞 SUPPORT DOCUMENTS

**If you need clarification:**
- Architecture: `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`
- Guardrails: `MEMORY_BANK.md` → Critical Guardrails section
- Integration patterns: `INTEGRATION_GUIDE.md`
- Preservation: `PRESERVATION_CHECKLIST.md`
- Agent coordination: `CURSOR_AGENT_GUIDELINES.md`

**Remember:** When in doubt, preserve existing functionality and ask for clarification.

---

## ✅ FINAL CHECKLIST

**Before starting integration:**

- [ ] Read all critical documents
- [ ] Set up Overseer agent with prompt
- [ ] Set up 6 worker agents with prompts
- [ ] Understand preservation requirements
- [ ] Understand integration patterns
- [ ] Have access to all reference documents

**You're ready to begin integration!**

