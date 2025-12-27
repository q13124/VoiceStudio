# VoiceStudio Quick Reference

## Execution Plan Overview

**7 Phases** with **Overseer + 8 Workers**

### Phase 0: Ground Rules
- Overseer sets context and rules
- No simplifications allowed

### Phase 1: Project + Tokens
- **Worker 1**: Create solution, DesignTokens.xaml, merge into App.xaml

### Phase 2: PanelHost Control
- **Worker 2**: Create PanelHost.xaml + .xaml.cs with header and content area

### Phase 3: MainWindow Shell
- **Worker 3**: Wire MainWindow.xaml with 4 PanelHosts, nav rail, command deck, status bar

### Phase 4: Views & ViewModels
- **Worker 4**: ProfilesView
- **Worker 5**: TimelineView
- **Worker 6**: EffectsMixerView
- **Worker 7**: AnalyzerView
- **Worker 8**: MacroView + DiagnosticsView
- **Overseer**: Assign panels to PanelHosts, verify all 6 exist

### Phase 5: Navigation & Registry
- **Worker 1**: Nav rail logic, panel switching
- **Worker 2**: PanelRegistry skeleton in Core

### Phase 6: Styles
- **Worker 3**: Organize styles, create nav button style, apply VSQ.* tokens

### Phase 7: Sanity Pass
- **Overseer**: Final verification, anti-simplification check

## Critical Rules (Never Violate)

1. ✅ **6 panels** - Never reduce
2. ✅ **Separate files** - Never merge View/ViewModel
3. ✅ **PanelHost control** - Never replace with Grid
4. ✅ **3×2 grid** - Never simplify layout
5. ✅ **VSQ.* tokens** - Never hardcode colors
6. ✅ **Placeholders visible** - Never collapse

## Violation Detection

Watch for:
- ❌ Merged files
- ❌ Reduced panel count
- ❌ PanelHost replaced
- ❌ Hardcoded colors
- ❌ Simplified layout
- ❌ Missing placeholders

## Remediation Command

```
Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to CIS. Do not merge or collapse.
```

## File Structure

```
src/VoiceStudio.App/
  MainWindow.xaml ✅
  Controls/PanelHost.xaml ✅
  Views/Panels/
    ProfilesView.xaml + .cs + ViewModel.cs
    TimelineView.xaml + .cs + ViewModel.cs
    EffectsMixerView.xaml + .cs + ViewModel.cs
    AnalyzerView.xaml + .cs + ViewModel.cs
    MacroView.xaml + .cs + ViewModel.cs
    DiagnosticsView.xaml + .cs + ViewModel.cs
  Resources/DesignTokens.xaml ✅

src/VoiceStudio.Core/
  Panels/ (registry system) ✅
  Models/ ✅
  Services/ ✅
```

## Overseer Checklist

After each phase:
- [ ] Files exist as separate entities
- [ ] No simplifications detected
- [ ] VSQ.* tokens used
- [ ] PanelHost used (not replaced)
- [ ] Layout complexity maintained
- [ ] All 6 panels exist

## Success Criteria

✅ All checks pass  
✅ No simplifications  
✅ Application runs  
✅ Layout matches spec  
✅ Ready for next phase  

