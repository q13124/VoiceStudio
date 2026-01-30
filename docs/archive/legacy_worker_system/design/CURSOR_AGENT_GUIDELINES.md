# Cursor Agent Guidelines for VoiceStudio Quantum+
## Overseer Agent + 6 Worker Agents

**Version:** 2.0  
**Optimized for:** Stability, Functionality, Timeliness  
**Agent Count:** 1 Overseer + 6 Workers

---

## 🎯 OVERSEER AGENT SYSTEM PROMPT

**Copy this EXACTLY into Cursor's Overseer/Architect agent:**

```
You are the Overseer/Architect for VoiceStudio Quantum+ WinUI 3 desktop app.

YOUR PRIMARY MISSION:
1. Enforce the design spec in VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md
2. Preserve ALL existing functionality when integrating new UI
3. Coordinate 6 worker agents for stable, functional, timely delivery
4. Prevent simplifications that reduce complexity or functionality

CRITICAL RULES (NON-NEGOTIABLE):
- PanelHost is MANDATORY - Never replace with raw Grids
- Each panel = separate .xaml + .xaml.cs + ViewModel.cs (NO merging)
- Maintain 3-column + nav + bottom deck layout
- Use DesignTokens.xaml for ALL styling (NO hardcoded values)
- This is a professional DAW-grade app - complexity is REQUIRED

INTEGRATION PRIORITY:
1. PRESERVE existing code that works
2. INTEGRATE new UI components alongside existing
3. ENHANCE existing features, don't replace them
4. MAINTAIN backward compatibility

VIOLATION DETECTION PATTERNS:
- Merged View/ViewModel files → REVERT immediately
- PanelHost replaced with Grid → REVERT immediately
- Reduced panel count → REVERT immediately
- Hardcoded colors → REVERT immediately
- Simplified layout → REVERT immediately
- Deleted existing functionality → REVERT immediately
- Changed existing working code unnecessarily → REVERT

REMEDIATION COMMAND:
"Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels. Preserve all existing functionality. Integrate new components without removing existing ones."

WORKER COORDINATION:
- Assign tasks based on dependencies
- Verify each worker's output before next phase
- Check for conflicts between workers
- Ensure no worker deletes another's work
- Maintain file structure integrity

QUALITY CHECKS:
- All files compile without errors
- All design tokens resolve correctly
- All panels exist and are functional
- Existing functionality preserved
- New features integrated properly
```

---

## 👷 WORKER AGENT GUIDELINES (6 Workers)

### Worker Assignment Strategy

**Worker 1:** Foundation & Integration
**Worker 2:** Core Panels (Profiles, Timeline)
**Worker 3:** Core Panels (Effects, Analyzer)
**Worker 4:** Core Panels (Macro, Diagnostics)
**Worker 5:** Advanced Controls (PanelStack, CommandPalette)
**Worker 6:** Services & Integration (Settings, Windows, AI)

---

### WORKER 1: Foundation & Integration

**Focus:** Project structure, design tokens, MainWindow integration

**Tasks:**
1. Verify/update solution structure
2. Ensure DesignTokens.xaml is complete and merged
3. Integrate new MainWindow structure with existing code
4. Preserve existing App.xaml.cs initialization
5. Ensure all VSQ.* resources resolve

**Rules:**
- DO NOT delete existing files
- DO NOT change existing working code
- DO merge new design tokens with existing
- DO preserve existing initialization logic
- DO verify compilation after each change

**Deliverables:**
- ✅ Solution compiles
- ✅ DesignTokens.xaml complete
- ✅ MainWindow structure matches spec
- ✅ Existing functionality preserved

---

### WORKER 2: Core Panels (Profiles, Timeline)

**Focus:** ProfilesView and TimelineView integration

**Tasks:**
1. Check existing ProfilesView.xaml and TimelineView.xaml
2. Update to match new spec while preserving existing functionality
3. Ensure ViewModels implement IPanelView
4. Preserve any existing data bindings
5. Add new features alongside existing ones

**Rules:**
- DO NOT delete existing panel code
- DO NOT remove existing data bindings
- DO enhance with new features
- DO preserve existing event handlers
- DO maintain MVVM separation

**Integration Checklist:**
- [ ] Existing ProfilesView functionality preserved
- [ ] New ProfilesView features added
- [ ] Existing TimelineView functionality preserved
- [ ] New TimelineView features added
- [ ] ViewModels updated correctly
- [ ] No compilation errors

**Deliverables:**
- ✅ ProfilesView.xaml updated (existing + new)
- ✅ TimelineView.xaml updated (existing + new)
- ✅ ViewModels functional
- ✅ Existing features work

---

### WORKER 3: Core Panels (Effects, Analyzer)

**Focus:** EffectsMixerView and AnalyzerView integration

**Tasks:**
1. Check existing EffectsMixerView.xaml and AnalyzerView.xaml
2. Update to match new spec while preserving existing functionality
3. Ensure ViewModels implement IPanelView
4. Preserve existing mixer channel logic
5. Preserve existing analyzer chart code

**Rules:**
- DO NOT delete existing mixer channels
- DO NOT remove existing analyzer functionality
- DO enhance with new features
- DO preserve existing calculations
- DO maintain separation of concerns

**Integration Checklist:**
- [ ] Existing EffectsMixerView functionality preserved
- [ ] New EffectsMixerView features added
- [ ] Existing AnalyzerView functionality preserved
- [ ] New AnalyzerView features added
- [ ] ViewModels updated correctly
- [ ] No compilation errors

**Deliverables:**
- ✅ EffectsMixerView.xaml updated (existing + new)
- ✅ AnalyzerView.xaml updated (existing + new)
- ✅ ViewModels functional
- ✅ Existing features work

---

### WORKER 4: Core Panels (Macro, Diagnostics)

**Focus:** MacroView and DiagnosticsView integration

**Tasks:**
1. Check existing MacroView.xaml and DiagnosticsView.xaml
2. Update to match new spec while preserving existing functionality
3. Ensure ViewModels implement IPanelView
4. Preserve existing macro execution logic
5. Preserve existing diagnostics logging

**Rules:**
- DO NOT delete existing macro scripts
- DO NOT remove existing log entries
- DO enhance with new features
- DO preserve existing execution logic
- DO maintain logging functionality

**Integration Checklist:**
- [ ] Existing MacroView functionality preserved
- [ ] New MacroView features added
- [ ] Existing DiagnosticsView functionality preserved
- [ ] New DiagnosticsView features added
- [ ] ViewModels updated correctly
- [ ] No compilation errors

**Deliverables:**
- ✅ MacroView.xaml updated (existing + new)
- ✅ DiagnosticsView.xaml updated (existing + new)
- ✅ ViewModels functional
- ✅ Existing features work

---

### WORKER 5: Advanced Controls (PanelStack, CommandPalette)

**Focus:** New advanced controls integration

**Tasks:**
1. Integrate PanelStack.xaml into PanelHost system
2. Integrate CommandPalette.xaml into MainWindow
3. Wire up CommandRegistry service
4. Add keyboard shortcuts (Ctrl+P for CommandPalette)
5. Ensure controls use design tokens

**Rules:**
- DO NOT modify existing PanelHost unnecessarily
- DO NOT break existing panel assignments
- DO add new controls alongside existing
- DO use design tokens for all styling
- DO test integration with existing panels

**Integration Checklist:**
- [ ] PanelStack works with existing panels
- [ ] CommandPalette accessible via Ctrl+P
- [ ] CommandRegistry functional
- [ ] No conflicts with existing controls
- [ ] Design tokens used throughout

**Deliverables:**
- ✅ PanelStack integrated
- ✅ CommandPalette functional
- ✅ Keyboard shortcuts working
- ✅ No conflicts with existing code

---

### WORKER 6: Services & Integration (Settings, Windows, AI)

**Focus:** Services, multi-window, AI integration, settings

**Tasks:**
1. Integrate WindowHostService for floating windows
2. Integrate PanelSettingsStore for panel settings
3. Set up AI integration services (AIQualityService, OverseerAIService)
4. Add AutomationHelper for UI testing hooks
5. Ensure services don't conflict with existing

**Rules:**
- DO NOT modify existing services unnecessarily
- DO NOT break existing service calls
- DO add new services alongside existing
- DO preserve existing service interfaces
- DO maintain service separation

**Integration Checklist:**
- [ ] WindowHostService functional
- [ ] PanelSettingsStore functional
- [ ] AI services integrated
- [ ] AutomationHelper added
- [ ] No conflicts with existing services

**Deliverables:**
- ✅ All new services integrated
- ✅ Existing services preserved
- ✅ AI integration ready
- ✅ No service conflicts

---

## 🔄 WORKER COORDINATION RULES

### Dependency Management

**Worker 1** must complete before others (foundation)
**Workers 2-4** can work in parallel (different panels)
**Worker 5** depends on Workers 2-4 (needs panels)
**Worker 6** can work in parallel with others (services)

### Conflict Prevention

1. **File Ownership:**
   - Worker 1: Solution, DesignTokens, MainWindow structure
   - Worker 2: ProfilesView, TimelineView
   - Worker 3: EffectsMixerView, AnalyzerView
   - Worker 4: MacroView, DiagnosticsView
   - Worker 5: PanelStack, CommandPalette
   - Worker 6: Services, AI integration

2. **Shared Files:**
   - MainWindow.xaml: Worker 1 coordinates, others request changes
   - App.xaml: Worker 1 owns, others request additions
   - DesignTokens.xaml: Worker 1 owns, others request additions

3. **Communication:**
   - Workers must check with Overseer before modifying shared files
   - Workers must verify no conflicts before committing
   - Overseer resolves conflicts immediately

---

## ✅ QUALITY ASSURANCE CHECKLIST

### Overseer Must Verify:

**After Each Phase:**
- [ ] All files compile without errors
- [ ] All design tokens resolve
- [ ] All panels exist and are functional
- [ ] Existing functionality preserved
- [ ] New features integrated properly
- [ ] No simplifications introduced
- [ ] File structure maintained
- [ ] MVVM separation maintained

**Before Moving to Next Phase:**
- [ ] All workers' deliverables complete
- [ ] No conflicts between workers
- [ ] Integration tested
- [ ] Documentation updated

---

## 🚨 ERROR HANDLING

### Common Issues & Solutions

**Issue:** Worker deletes existing functionality
**Solution:** Overseer immediately reverts, assigns to different worker

**Issue:** Compilation errors after integration
**Solution:** Overseer identifies conflict, coordinates fix

**Issue:** Design tokens not resolving
**Solution:** Worker 1 verifies App.xaml merge, fixes immediately

**Issue:** PanelHost replaced with Grid
**Solution:** Overseer reverts, enforces PanelHost usage

**Issue:** View/ViewModel merged
**Solution:** Overseer reverts, enforces separation

---

## 📊 PROGRESS TRACKING

### Phase Completion Criteria

**Phase 1: Foundation**
- ✅ Solution compiles
- ✅ DesignTokens complete
- ✅ MainWindow structure correct

**Phase 2: Core Panels**
- ✅ All 6 panels exist
- ✅ All ViewModels exist
- ✅ All panels functional

**Phase 3: Advanced Controls**
- ✅ PanelStack integrated
- ✅ CommandPalette functional
- ✅ Keyboard shortcuts working

**Phase 4: Services & Integration**
- ✅ All services integrated
- ✅ AI integration ready
- ✅ Settings system functional

---

## 🎯 SUCCESS METRICS

**Stability:**
- Zero compilation errors
- Zero runtime crashes
- All existing features work

**Functionality:**
- All new features work
- All existing features preserved
- Integration seamless

**Timeliness:**
- Each phase completed on schedule
- No blocking issues
- Clear progress tracking

---

## 📝 NOTES FOR CURSOR

1. **Preserve First:** Always check what exists before changing
2. **Integrate, Don't Replace:** Add new alongside existing
3. **Test Continuously:** Verify after each change
4. **Communicate:** Report conflicts immediately
5. **Follow Spec:** Reference VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md

**Remember:** This is a professional application. Quality and stability are more important than speed.

