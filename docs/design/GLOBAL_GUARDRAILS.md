# Global Guardrails for VoiceStudio

## 🚦 Critical Rules (Remind Cursor Constantly)

**Put this near the top of any big instruction you give Cursor:**

```
Do NOT simplify the UI layout or collapse panels.

Keep the 3-column + nav + bottom deck layout and PanelHost controls.

Do NOT merge Views and ViewModels. Each panel = .xaml + .xaml.cs + ViewModel.cs.

Do NOT remove placeholder areas (waveform, spectrogram, analyzers, macros, logs). 
Those are future advanced controls, not decoration.

Use DesignTokens.xaml for all colors/typography; no hardcoded one-off values unless clearly temporary.

Treat this as a professional DAW-grade app, not a sample or tutorial.
```

## Why These Rules Exist

**You already saw how Cursor will happily "optimize away" the complexity; these rules are your seatbelt.**

### Common Violations to Watch For

1. **Layout Simplification**
   - ❌ Reducing 3-column grid to 2 columns
   - ❌ Removing bottom deck
   - ❌ Collapsing nav rail into menu
   - ✅ **Correct:** Maintain 3-column + nav + bottom deck

2. **File Merging**
   - ❌ Combining View and ViewModel into one file
   - ❌ Creating "God files" with multiple panels
   - ❌ Removing code-behind files
   - ✅ **Correct:** Separate .xaml, .xaml.cs, ViewModel.cs for each panel

3. **PanelHost Replacement**
   - ❌ Replacing PanelHost with raw Grid
   - ❌ Inlining panel content in MainWindow
   - ❌ Removing PanelHost abstraction
   - ✅ **Correct:** Use PanelHost for all panels

4. **Placeholder Removal**
   - ❌ Removing waveform placeholder
   - ❌ Hiding spectrogram area
   - ❌ Collapsing analyzer chart regions
   - ✅ **Correct:** Keep all placeholders visible

5. **Design Token Violations**
   - ❌ Hardcoded colors like `Background="#FF0000"`
   - ❌ Random font sizes
   - ❌ Inline styles instead of resources
   - ✅ **Correct:** Use VSQ.* resources only

## Enforcement

### When to Apply

- **Before starting any phase**
- **During code review**
- **When violations detected**
- **In all instructions to Cursor**

### Remediation Command

When violations detected:

```
Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to CIS. Do not merge or collapse.

Specific violations:
- [List violations]

Required actions:
1. Restore PanelHost control (if replaced)
2. Separate merged View/ViewModel files
3. Restore panel count to 6
4. Restore 3×2 grid layout
5. Restore all placeholder regions
6. Use VSQ.* design tokens only
```

## Phase-Specific Reminders

### Phase 2 (Styling)
- Don't change MainWindow's layout grid
- Do not add more "helper windows"
- Implement NavIconButton as reusable control
- Apply styles via StaticResource, not inline

### Phase 3 (Docking)
- Do not introduce drag-docking yet
- Keep PanelHost as the only container
- PanelRegistry controls which panel goes inside

### Phase 4 (Data Models)
- Focus only on local model and serialization
- Panels must use real ViewModels & models
- No more pure dummy text

### Phase 5 (Backend)
- Treat backend as local microservice, not optional
- Implement interfaces in Core, implementation in App

### Phase 6 (MCP)
- Keep MCP integration inside backend, not UI
- UI only talks to backend API client

### Phase 7 (Audio)
- Do not try to implement full DAW-level editing yet
- Focus on end-to-end flow, even if crude

## Success Indicators

You know the guardrails are working when:
- ✅ Layout complexity maintained
- ✅ All 6 panels exist separately
- ✅ PanelHost used everywhere
- ✅ Placeholders visible
- ✅ VSQ.* tokens used consistently
- ✅ No "helpful" simplifications

## Remember

**This is a professional DAW-grade app, not a sample or tutorial.**

Complexity is the feature, not a bug.

