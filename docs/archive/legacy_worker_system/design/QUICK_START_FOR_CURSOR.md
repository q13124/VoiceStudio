# Quick Start Guide for Cursor
## VoiceStudio Quantum+ UI Integration

**TL;DR:** Integrate new UI with existing code. Preserve everything. Use 1 Overseer + 6 Workers.

---

## 🚀 START HERE (5 Minutes)

### Step 1: Read These 3 Documents
1. **MEMORY_BANK.md** - Critical rules (5 min read)
2. **CURSOR_AGENT_GUIDELINES.md** - Agent system (10 min read)
3. **INTEGRATION_GUIDE.md** - How to integrate (15 min read)

### Step 2: Set Up Agents

**Overseer Agent:**
- Copy entire contents of `OVERSEER_SYSTEM_PROMPT_V2.md` into Overseer

**6 Worker Agents:**
- Worker 1: Copy "Worker 1" section from `WORKER_AGENT_PROMPTS.md`
- Worker 2: Copy "Worker 2" section from `WORKER_AGENT_PROMPTS.md`
- Worker 3: Copy "Worker 3" section from `WORKER_AGENT_PROMPTS.md`
- Worker 4: Copy "Worker 4" section from `WORKER_AGENT_PROMPTS.md`
- Worker 5: Copy "Worker 5" section from `WORKER_AGENT_PROMPTS.md`
- Worker 6: Copy "Worker 6" section from `WORKER_AGENT_PROMPTS.md`

### Step 3: Start Integration

**Overseer First Command:**
```
"Create a complete inventory of all existing VoiceStudio files:
- List all .xaml files with full paths
- List all .cs files with full paths
- Document all existing ViewModels and their properties
- Document all existing services and their methods
- Document all existing data bindings
- Document all existing event handlers
- Save inventory to PRESERVATION_INVENTORY.md"
```

---

## 🎯 THE GOLDEN RULES

1. **PRESERVE FIRST** - Never delete existing code
2. **INTEGRATE, DON'T REPLACE** - Add new alongside existing
3. **TEST EXISTING** - Verify nothing broke after each change
4. **REPORT CONFLICTS** - Don't proceed with conflicts

---

## 📋 WORKER ASSIGNMENTS

- **Worker 1:** Foundation (DesignTokens, MainWindow)
- **Worker 2:** ProfilesView, TimelineView
- **Worker 3:** EffectsMixerView, AnalyzerView
- **Worker 4:** MacroView, DiagnosticsView
- **Worker 5:** PanelStack, CommandPalette
- **Worker 6:** Services, AI integration

---

## ✅ SUCCESS = EXISTING WORKS + NEW WORKS

**Integration is successful when:**
- ✅ All existing features work
- ✅ All new features work
- ✅ Zero errors
- ✅ Everything preserved

---

## 📚 FULL DOCUMENTATION

See `CURSOR_MASTER_INSTRUCTIONS.md` for complete guide.

**Key Documents:**
- `CURSOR_AGENT_GUIDELINES.md` - Complete agent system
- `INTEGRATION_GUIDE.md` - Integration patterns
- `PRESERVATION_CHECKLIST.md` - Preservation guide
- `OVERSEER_SYSTEM_PROMPT_V2.md` - Overseer prompt
- `WORKER_AGENT_PROMPTS.md` - Worker prompts

---

**Ready? Start with the Overseer inventory command above!**

