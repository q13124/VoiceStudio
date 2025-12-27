# Cursor Guardrails for VoiceStudio Migration
## Strict Rules for Overseer Agent

**Purpose:** Ensure Cursor/Overseer maintains premium UI contract and does not simplify during migration.

---

## 🚨 CRITICAL RULES

### 1. Do NOT Simplify

- ❌ **DO NOT** collapse panels or merge views
- ❌ **DO NOT** reduce panel count
- ❌ **DO NOT** hide "unused" panels
- ❌ **DO NOT** remove placeholder areas
- ❌ **DO NOT** merge Views and ViewModels
- ❌ **DO NOT** replace PanelHost with raw Grids
- ❌ **DO NOT** simplify layout density

### 2. Maintain Lattice Layout

- ✅ **DO** preserve 3-column + nav + bottom deck layout
- ✅ **DO** maintain PanelHost controls
- ✅ **DO** keep dense, dockable panels
- ✅ **DO** preserve panel hierarchy
- ✅ **DO** maintain Adobe/Resolve/FL-style layout

### 3. Load ALL Panels

- ✅ **DO** load all panels found under `ui/Views/Panels`
- ✅ **DO** include panels from `PanelRegistry.Auto.cs`
- ✅ **DO** merge auto-discovered panels with manual registry
- ✅ **DO** scaffold missing ViewModels (no-throw stubs)
- ✅ **DO** log TODO for missing ViewModels

### 4. Path Updates

- ✅ **DO** rewrite `C:\VoiceStudio` → `E:\VoiceStudio`
- ✅ **DO** update dataset paths to `E:\VoiceStudio\library\`
- ✅ **DO** update model paths to `E:\VoiceStudio\models\` or `%PROGRAMDATA%\VoiceStudio\models\`
- ✅ **DO** preserve relative paths where appropriate

### 5. Preserve Core Systems

- ✅ **DO** keep Governor + learners intact
- ✅ **DO** maintain Engine Router integration
- ✅ **DO** preserve A/B test recording
- ✅ **DO** keep reward model guidance
- ✅ **DO** maintain EngineHook for Governor

### 6. UI Resources

- ✅ **DO** load themes from `ui/Resources/Theme.*.xaml`
- ✅ **DO** load density from `ui/Resources/Density.*.xaml`
- ✅ **DO** use design tokens from `DesignTokens.xaml`
- ✅ **DO** preserve theme switching
- ✅ **DO** maintain density presets

---

## 📋 Panel Registry Rules

### Auto-Discovery

```csharp
// PanelRegistry.Auto.cs (auto-generated)
public static IEnumerable<string> AllXaml() => new [] {
  "ui/Views/Panels/Panel1View.xaml",
  "ui/Views/Panels/Panel2View.xaml",
  // ... all discovered panels
};
```

### Manual Registry

```csharp
// PanelRegistry.cs (manual)
public class PanelRegistry {
  public static void RegisterAll() {
    // Merge auto-discovered panels
    foreach (var xaml in PanelRegistryAuto.AllXaml()) {
      RegisterPanel(xaml);
    }
    
    // Add hand-picked defaults
    RegisterDefaultPanel("Profiles", PanelRegion.Left);
    RegisterDefaultPanel("Timeline", PanelRegion.Center);
    // ...
  }
}
```

### Missing ViewModels

```csharp
// If ViewModel missing, scaffold stub:
public class MissingPanelViewModel : ObservableObject {
  // No-throw stub
  public MissingPanelViewModel() {
    Logger.LogWarning("TODO: Implement MissingPanelViewModel");
  }
}
```

---

## 🎨 Premium UI Contract

### Must Preserve

1. **Dense, Docked Panels**
   - Maintain panel density
   - Keep docking system
   - Preserve panel hierarchy

2. **Visual Components**
   - Waveform controls
   - Spectrogram displays
   - Mixer interfaces
   - GPU/CPU meters

3. **Micro-Interactions**
   - Hover effects
   - Focus states
   - Button animations
   - Panel transitions

4. **Consistency**
   - Design tokens usage
   - Typography hierarchy
   - Color scheme consistency
   - Spacing rules

5. **Visual Hierarchy**
   - Panel importance levels
   - Information density
   - Visual grouping
   - Focus indicators

6. **Adaptive Personalization**
   - Theme switching
   - Density presets
   - Layout persistence
   - User preferences

7. **Polished Motion**
   - Smooth animations
   - Transitions
   - Loading states
   - Feedback animations

8. **Command-Center Layout**
   - Premiere/Resolve/FL-style
   - Keyboard efficiency
   - Real-time feedback
   - Non-destructive workflows

---

## 🔍 Verification Checklist

After migration, verify:

- [ ] All panels loaded (count matches ~90+)
- [ ] No panels deleted or hidden
- [ ] PanelHost controls preserved
- [ ] Layout density maintained
- [ ] Design tokens applied
- [ ] Theme switching works
- [ ] Governor + learners intact
- [ ] Engine Router functional
- [ ] Paths updated correctly
- [ ] No `C:\VoiceStudio` references remain

---

## 📝 Common Violations to Watch For

### Simplification Violations

- ❌ "Merged 3 panels into 1 for simplicity"
- ❌ "Removed unused panels"
- ❌ "Simplified layout to reduce complexity"
- ❌ "Collapsed ViewModels into Views"

### Path Violations

- ❌ Hardcoded `C:\VoiceStudio` paths
- ❌ Missing path updates in configs
- ❌ Broken dataset/model paths

### System Violations

- ❌ Modified Governor logic
- ❌ Changed learner algorithms
- ❌ Removed A/B test recording
- ❌ Disconnected Engine Router

---

## 🛡️ Remediation Commands

If violations detected:

```powershell
# Re-run panel discovery
.\tools\Discover-Panels.ps1

# Verify panel count
Get-ChildItem -Path "ui\Views\Panels" -Filter "*View.xaml" | Measure-Object

# Check for C: paths
Select-String -Path "**\*.cs","**\*.py","**\*.json" -Pattern "C:\\VoiceStudio"

# Verify Governor exists
Test-Path "app\core\runtime\governor.py"

# Verify learners exist
Test-Path "app\core\learners\quality_scorer.py"
Test-Path "app\core\learners\prosody_tuner.py"
Test-Path "app\core\learners\dataset_curator.py"
```

---

**These guardrails ensure the premium UI contract and core systems are preserved during migration.**

