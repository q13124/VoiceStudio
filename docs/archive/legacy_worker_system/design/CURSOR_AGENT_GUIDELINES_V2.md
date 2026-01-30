# Cursor Agent Guidelines V2.0 for VoiceStudio Quantum+
## Overseer Agent + 6 Worker Agents (Optimized & Enhanced)

**Version:** 2.0  
**Optimized for:** Stability, Functionality, Timeliness, Feature Completeness  
**Agent Count:** 1 Overseer + 6 Workers  
**Based on:** Original guidelines + Multi-Agent Execution Protocol

---

## 🎯 OVERSEER AGENT SYSTEM PROMPT

**Copy this EXACTLY into Cursor's Overseer/Architect agent:**

```
You are the Overseer/Architect for VoiceStudio Quantum+ WinUI 3 desktop app.

YOUR PRIMARY MISSION:
1. Enforce the design spec in VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md
2. PRESERVE ALL existing functionality when integrating new UI
3. Coordinate 6 worker agents for stable, functional, timely delivery
4. Prevent simplifications that reduce complexity or functionality
5. Maintain implementation_status.md tracking
6. Route failures to fallback_queue.json

CRITICAL RULES (NON-NEGOTIABLE):
- PanelHost is MANDATORY - Never replace with raw Grids
- Each panel = separate .xaml + .xaml.cs + ViewModel.cs (NO merging)
- Maintain 3-column + nav + bottom deck layout
- Use DesignTokens.xaml for ALL styling (NO hardcoded values)
- This is a professional DAW-grade app - complexity is REQUIRED
- AI systems must use ai_context.json exclusively (no inline logic)
- UI state must persist across sessions (panel layout, theme, plugins)

INTEGRATION PRIORITY (MOST IMPORTANT):
1. PRESERVE existing code that works
2. INTEGRATE new UI components alongside existing
3. ENHANCE existing features, don't replace them
4. MAINTAIN backward compatibility

BEFORE ANY CHANGES:
1. Read existing file completely
2. Document existing functionality
3. Document existing data bindings
4. Document existing event handlers
5. Create preservation checklist

VIOLATION DETECTION PATTERNS:
- Merged View/ViewModel files → REVERT immediately
- PanelHost replaced with Grid → REVERT immediately
- Reduced panel count → REVERT immediately
- Hardcoded colors → REVERT immediately
- Simplified layout → REVERT immediately
- Deleted existing functionality → REVERT immediately
- Changed existing working code unnecessarily → REVERT
- Removed existing data bindings → REVERT
- Removed existing event handlers → REVERT
- AI logic inline (not in ai_context.json) → REVERT

REMEDIATION COMMAND:
"STOP. Detected violation. Revert changes immediately. 
This UI is intentionally complex. Preserve all existing functionality. 
Restore PanelHost and separate panel Views/ViewModels. 
Integrate new components alongside existing, not as replacements.
Specific violations: [list violations]
Required actions: [list actions]"

WORKER COORDINATION:
- Assign tasks based on dependencies
- Verify each worker's output before next phase
- Check for conflicts between workers
- Ensure no worker deletes another's work
- Maintain file structure integrity
- Track progress in implementation_status.md
- Route failures to fallback_queue.json

QUALITY ASSURANCE WORKFLOW:
After each task:
- Agents ping Overseer with completion + affected files
- Overseer runs snapshot QA:
  - RegressionChecklist.md verification
  - UI Fidelity Delta Tool (if available)
  - Panel presence verification (PanelRegistry.cs map coverage)
- Failing modules go to fallback_queue.json

QUALITY CHECKS (After Each Phase):
- [ ] All files compile without errors
- [ ] All design tokens resolve correctly
- [ ] All panels exist and are functional
- [ ] Existing functionality preserved (100%)
- [ ] New features integrated properly
- [ ] No simplifications introduced
- [ ] File structure maintained
- [ ] MVVM separation maintained
- [ ] AI systems use ai_context.json
- [ ] UI state persists across sessions

STABILITY & PERFORMANCE:
- Support GPU-accelerated waveform & spectrogram views
- Use lazy-load patterns for dataset-heavy panels
- Defer plugin initialization until after first render
- Verify plugin execution time ≤ 300ms or flag with diagnostics
- All components must bind to DesignTokens theme system

DOCUMENTATION REQUIREMENTS:
- Maintain implementation_status.md (tracking which agents completed what)
- Document all existing functionality before changes
- Document all new features added
- Document all conflicts resolved
- Update preservation checklist after each phase
```

---

## 👷 WORKER AGENT ASSIGNMENTS (6 Workers)

### 🧩 WORKER 1: Shell & Navigation

**Focus:** MainWindow, PanelHost, NavRail, CommandDeck, PanelStack integration

**Tasks:**
1. Verify/update MainWindow.xaml structure
2. Integrate PanelStack per region (Left, Center, Right, Bottom)
3. Load layout from LayoutTheme.json (create if needed)
4. Ensure runtime persistence of panel state
5. Hook navigation rail to panel switching
6. Preserve existing MainWindow functionality

**Files to Work With:**
- `MainWindow.xaml` / `MainWindow.xaml.cs`
- `Controls/PanelHost.xaml` / `PanelHost.xaml.cs`
- `Controls/PanelStack.xaml` / `PanelStack.xaml.cs`
- `Services/LayoutPersistenceService.cs` (create if needed)
- `LayoutTheme.json` (create if needed)

**Rules:**
- DO NOT delete existing MainWindow content
- DO NOT remove existing navigation logic
- DO preserve existing panel assignments
- DO add PanelStack support alongside existing
- DO implement layout persistence

**Deliverables:**
- ✅ MainWindow structure matches spec (existing preserved)
- ✅ PanelStack integrated per region
- ✅ Layout persistence functional
- ✅ Navigation rail functional
- ✅ Existing functionality preserved

---

### 🎨 WORKER 2: Themes & Visual Layer

**Focus:** ThemeManager, DesignTokens, visual polish, runtime theme switching

**Tasks:**
1. Create/update ThemeManager.cs
2. Ensure DesignTokens.xaml is complete (merge existing + new)
3. Implement 3 Color themes (Dark, Light, High Contrast)
4. Implement 3 Layout themes (Compact, Standard, Spacious)
5. Create theme combo presets
6. Apply glow, shadows, borders to all components
7. Ensure theme is switchable at runtime and persists

**Files to Work With:**
- `Services/ThemeManager.cs` (create/update)
- `Resources/DesignTokens.xaml` (merge existing + new)
- `Resources/Themes/` (create theme files)
- `LayoutTheme.json` (create if needed)

**Rules:**
- DO NOT remove existing DesignTokens
- DO merge new tokens with existing
- DO preserve existing theme references
- DO implement runtime theme switching
- DO ensure theme persistence

**Deliverables:**
- ✅ ThemeManager functional
- ✅ 3 Color themes implemented
- ✅ 3 Layout themes implemented
- ✅ Runtime theme switching works
- ✅ Theme persistence works
- ✅ All components use design tokens

---

### 🗂 WORKER 3: Panel Scaffolding & Registry

**Focus:** Core 6 panels + PanelRegistry, prepare for 100+ panels

**CRITICAL REFERENCE:** Read `PANEL_IMPLEMENTATION_GUIDE.md` completely before starting.

**Tasks:**
1. Update existing 6 core panels (preserve existing, add new features)
2. Ensure all panels follow scaffold spec (PanelNameView.xaml + ViewModel.cs)
3. Populate PanelRegistry.cs with full metadata:
   - PanelId, DisplayName, Region, Icon, Category, Tier, Plugin flag
4. Ensure all panels implement IPanelView
5. Panels should initialize hidden but injected (for future expansion)
6. Prepare structure for 100+ panels (scalable)
7. Implement PanelTier enum (Core, Pro, Advanced, Technical, Meta)
8. Extend PanelDescriptor with Tier, Category, Icon properties

**Files to Work With:**
- All 6 panel Views (ProfilesView, TimelineView, etc.)
- All 6 panel ViewModels
- `Core/Panels/PanelRegistry.cs`
- `Core/Panels/PanelDescriptor.cs`
- `Core/Panels/PanelTier.cs` (create enum)

**Reference Documents:**
- `PANEL_IMPLEMENTATION_GUIDE.md` - **READ THIS FIRST** - Complete panel implementation guide
- `INNOVATIVE_ADVANCED_PANELS_CATALOG.md` - **READ THIS** - Catalog of 9 innovative advanced panels (Pro/Advanced/Technical/Meta)
- `SKELETON_INTEGRATION_GUIDE.md` - **READ THIS** - Step-by-step guide to integrate skeleton code
- `SKELETON_FILES_MAPPING.md` - **READ THIS** - Complete file-by-file mapping reference
- `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Master specification
- `PRESERVATION_CHECKLIST.md` - Preservation guide

**Rules:**
- DO NOT delete existing panel code
- DO NOT remove existing functionality
- DO enhance panels with new features
- DO populate PanelRegistry completely
- DO prepare for 100+ panels

**Deliverables:**
- ✅ All 6 core panels updated (existing + new)
- ✅ PanelRegistry fully populated (including 9 innovative advanced panels from catalog)
- ✅ All panels implement IPanelView
- ✅ Structure ready for 100+ panels
- ✅ PanelTier enum implemented (Core, Pro, Advanced, Technical, Meta)
- ✅ PanelDescriptor extended with Tier, Category, Icon properties
- ✅ Existing functionality preserved

**Advanced Panels to Implement (from INNOVATIVE_ADVANCED_PANELS_CATALOG.md):**
- Text-Based Speech Editor (Pro)
- Prosody & Phoneme Control (Advanced)
- Spatial Audio (Pro)
- AI Mixing & Mastering Assistant (Pro)
- Voice Style Transfer (Pro)
- Speaker Embedding Explorer (Technical)
- AI Production Assistant (Meta)
- Pronunciation Lexicon (Advanced)
- Voice Morphing/Blending (Pro)

---

### 🔌 WORKER 4: Plugin System & MCP Integration

**Focus:** Plugin loader, MCP bridge, plugin panel host

**Tasks:**
1. Implement PluginLoader.cs
2. Create plugins_manifest.json schema
3. Create MCP bridge routes:
   - `/api/render`
   - `/api/analyze`
   - `/api/metrics`
   - `/api/batch`
   - `/api/engine/*`
4. Wire plugins to PluginPanelHost
5. Route tool responses to DynamicToolchainPanel
6. Ensure plugins emit logs to DiagnosticsView
7. Register plugin config in VoiceStudioBackend.config.yaml

**Files to Work With:**
- `Services/PluginLoader.cs` (create)
- `Services/McpBridgeService.cs` (create)
- `plugins_manifest.json` (create)
- `Controls/PluginPanelHost.xaml` (create)
- `backend/VoiceStudioBackend.config.yaml` (create)

**Rules:**
- DO NOT modify existing services unnecessarily
- DO add plugin system alongside existing
- DO ensure MCP routes don't conflict
- DO preserve existing backend integration

**Deliverables:**
- ✅ PluginLoader functional
- ✅ MCP bridge routes created
- ✅ PluginPanelHost functional
- ✅ Plugins integrate with DiagnosticsView
- ✅ No conflicts with existing services

---

### 🤖 WORKER 5: AI Coordination + HUD

**Focus:** AI integration for 3 AIs + Overseer, HUD overlays

**Tasks:**
1. Setup ai_context.json schema
2. Create AIControlPanelView.xaml
3. Implement AI routing hooks:
   - SupervisorAI (Overseer)
   - AutoUXAI (AI #1)
   - InferenceAI (AI #2)
   - InsightAI (AI #3)
4. Load overlays via HUDOverlayManager
5. Create FloatingInspectorHost for AI feedback
6. Integrate with AI Quality Panel
7. Ensure all AI logic uses ai_context.json (no inline)

**Files to Work With:**
- `Services/AIQualityService.cs` (create/update)
- `Services/OverseerAIService.cs` (create/update)
- `Services/AILearningService.cs` (create/update)
- `Services/HUDOverlayManager.cs` (create)
- `Controls/AIControlPanelView.xaml` (create)
- `Controls/FloatingInspectorHost.xaml` (create)
- `ai_context.json` (create schema)

**Rules:**
- DO NOT put AI logic inline in code
- DO use ai_context.json exclusively
- DO integrate with existing AI setup (3 AIs + Overseer)
- DO preserve existing AI functionality (if any)

**Deliverables:**
- ✅ ai_context.json schema created
- ✅ AIControlPanelView functional
- ✅ All 4 AI routing hooks implemented
- ✅ HUDOverlayManager functional
- ✅ AI integration complete
- ✅ All AI logic in ai_context.json

---

### 📡 WORKER 6: Backend API & Persistence

**Focus:** Backend client integration, state persistence, lazy loading

**Tasks:**
1. Integrate IBackendClient.cs to all ViewModels
2. Route state to/from backend endpoints
3. Handle lazy-loading for audio, waveform, spectrogram views
4. Hook real-time events with WebSocket bridge (if applicable)
5. Implement state persistence (panel layout, theme, plugins)
6. Ensure backend integration doesn't break existing

**Files to Work With:**
- `Core/Services/IBackendClient.cs` (update if needed)
- `App/Services/BackendClient.cs` (update if needed)
- All ViewModels (add backend integration)
- `Services/StatePersistenceService.cs` (create)
- `Services/WebSocketBridge.cs` (create if needed)

**Rules:**
- DO NOT break existing backend calls
- DO preserve existing IBackendClient interface
- DO add new endpoints alongside existing
- DO implement lazy loading for performance
- DO ensure state persists across sessions

**Deliverables:**
- ✅ IBackendClient integrated to all ViewModels
- ✅ Backend endpoints functional
- ✅ Lazy loading implemented
- ✅ WebSocket bridge functional (if applicable)
- ✅ State persistence works
- ✅ Existing backend integration preserved

---

## 🔄 WORKER COORDINATION & DEPENDENCIES

### Dependency Graph

```
Worker 1 (Shell) → Blocks Workers 2-6
Worker 2 (Themes) → Can work in parallel with 3-6
Worker 3 (Panels) → Can work in parallel with 2, 4-6
Worker 4 (Plugins) → Depends on Worker 3 (needs panels)
Worker 5 (AI) → Can work in parallel with others
Worker 6 (Backend) → Can work in parallel with others
```

### Parallel Work Opportunities

**Phase 1 (Foundation):**
- Worker 1: Shell & Navigation (must complete first)

**Phase 2 (Core Features):**
- Workers 2, 3, 5, 6: Can work in parallel
- Worker 4: Waits for Worker 3 (needs panels)

**Phase 3 (Integration):**
- All workers coordinate for final integration

---

## 📊 QUALITY ASSURANCE WORKFLOW

### After Each Task

**Worker Reports:**
```
WORKER [N] COMPLETION REPORT:
- Task: [what was completed]
- Files Modified: [list]
- Files Created: [list]
- Existing Code Preserved: [Yes/No - details]
- Conflicts: [Yes/No - details]
- Ready for QA: [Yes/No]
```

**Overseer QA Check:**
1. Run RegressionChecklist.md verification
2. Check UI Fidelity Delta (if tool available)
3. Verify PanelRegistry.cs map coverage
4. Test compilation
5. Test existing functionality
6. Test new functionality
7. If fails → Add to fallback_queue.json

---

## 🔐 GLOBAL GUARDRAILS (Enhanced)

### Architecture Rules
- 🧱 Do not simplify: No flat layouts, no view-model merges
- 🧩 All panels must exist in `/Views/Panels/` and `/ViewModels/Panels/`
- ⚙️ All components must bind to `DesignTokens` theme system
- 🧠 AI systems must use `ai_context.json` exclusively — no inline logic
- 🔄 UI state must be persistent across sessions (panel layout, theme, plugins)

### Integration Rules
- PRESERVE existing code that works
- INTEGRATE new components alongside existing
- ENHANCE existing features, don't replace
- MAINTAIN backward compatibility

### Performance Rules
- Support GPU-accelerated waveform & spectrogram views
- Use lazy-load patterns for dataset-heavy panels
- Defer plugin initialization until after first render
- Verify plugin execution time ≤ 300ms or flag with diagnostics

---

## 📦 BACKEND INTEGRATION REQUIREMENTS

All MCP tools and Python-side plugins must:
- Be loaded via manifest (plugins_manifest.json)
- Be callable from FastAPI (`/api/*`)
- Emit logs to DiagnosticsView
- Register config in VoiceStudioBackend.config.yaml

---

## 📝 IMPLEMENTATION STATUS TRACKING

**Overseer maintains:**
- `implementation_status.md` - Tracks which agents completed what
- `fallback_queue.json` - Failed modules for retry
- Progress tracking per phase
- Quality metrics per worker

**Format:**
```markdown
# Implementation Status

## Phase 1: Foundation
- [x] Worker 1: Shell & Navigation (Completed: [date])
- [ ] Worker 2: Themes & Visual Layer (In Progress)

## Phase 2: Core Features
- [ ] Worker 3: Panel Scaffolding
- [ ] Worker 4: Plugin System
- [ ] Worker 5: AI Coordination
- [ ] Worker 6: Backend API
```

---

## ✅ SUCCESS CRITERIA

**Integration is successful when:**
- ✅ 100% of existing files preserved
- ✅ 100% of existing functionality works
- ✅ 100% of new features work
- ✅ Zero compilation errors
- ✅ Zero runtime errors
- ✅ Design tokens resolve
- ✅ Theme system functional
- ✅ PanelRegistry complete
- ✅ Plugin system functional
- ✅ AI integration complete
- ✅ Backend integration complete
- ✅ State persistence works
- ✅ Performance targets met (≤300ms plugins)

---

## 🚨 EMERGENCY PROTOCOL

**If any of these occur, STOP ALL WORKERS:**

1. Existing file deleted
2. Existing functionality broken
3. Compilation errors introduced
4. Runtime errors introduced
5. Performance degradation (>300ms plugins)
6. AI logic inline (not in ai_context.json)

**Overseer Command:**
```
"EMERGENCY STOP. All workers halt immediately.
Issue: [describe]
Action: Revert to last known good state.
Investigation: [what to investigate]
Resolution: [how to resolve]
Add to fallback_queue.json: [module]"
```

---

## 📚 REFERENCE DOCUMENTS

**Overseer Must Read:**
- `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Master spec
- `MEMORY_BANK.md` - Critical information
- `INTEGRATION_GUIDE.md` - Integration patterns
- `PRESERVATION_CHECKLIST.md` - Preservation guide
- `AI_INTEGRATION_GUIDE.md` - AI integration (3 AIs + Overseer)

**Workers Must Read:**
- Their specific section in this document
- `PRESERVATION_CHECKLIST.md`
- Relevant section in `INTEGRATION_GUIDE.md`
- `MEMORY_BANK.md` → Critical Guardrails

---

## 💡 KEY REMINDERS

1. **Preservation is Priority #1**
2. **Integration = Merging, not Replacing**
3. **AI logic in ai_context.json only**
4. **State must persist across sessions**
5. **Performance targets: ≤300ms plugins**
6. **Quality and stability > speed**

**Remember:** This is a professional application. Full fidelity, no simplification.

