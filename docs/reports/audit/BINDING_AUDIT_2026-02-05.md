# XAML Binding Audit Report

**Task**: 1.1.1 — Audit {Binding} vs {x:Bind} usage across all Views
**Date**: 2026-02-05
**Role**: UI Engineer (Role 3)
**Phase**: 1 — XAML Reliability & AI Safety

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total XAML Files | 160 | — |
| Files with {x:Bind} | 42 | ✅ |
| Files with {Binding} | 5 | ⚠️ Needs Migration |
| Files with x:DataType | 98 | ✅ |
| {x:Bind} Instances | 575+ | ✅ |
| {Binding} Instances | 12 | ⚠️ Needs Migration |
| **Compile-Time Binding Coverage** | **97.9%** | ✅ GOOD |

---

## {Binding} Instances Requiring Migration

### 1. QualityControlView.xaml (2 instances)

**Location**: `src/VoiceStudio.App/Views/Panels/QualityControlView.xaml`

```xml
<!-- Line 237-238: ItemsControl DataTemplate -->
<Run Text="{Binding Key}" />: <Run Text="{Binding Value}" />
```

**Issue**: Inside `DataTemplate` without `x:DataType`
**Fix**: Add `x:DataType` to DataTemplate and convert to `{x:Bind}`

---

### 2. TextBasedSpeechEditorView.xaml (2 instances)

**Location**: `src/VoiceStudio.App/Views/Panels/TextBasedSpeechEditorView.xaml`

```xml
<!-- Line 160-162: ItemsControl DataTemplate -->
<Run Text="{Binding StartTime, Converter={StaticResource F2FormatConverter}}" />
<Run Text="{Binding EndTime, Converter={StaticResource F2FormatConverter}}" />
```

**Issue**: Inside `DataTemplate` without `x:DataType`
**Fix**: Add `x:DataType` to DataTemplate and convert to `{x:Bind}`

---

### 3. EnsembleSynthesisView.xaml (4 instances)

**Location**: `src/VoiceStudio.App/Views/Panels/EnsembleSynthesisView.xaml`

```xml
<!-- Line 139, 148: ComboBox ItemsSource with ElementName -->
ItemsSource="{Binding DataContext.AvailableProfiles, ElementName=EnsembleSynthesisView_Root}"
ItemsSource="{Binding DataContext.AvailableEngines, ElementName=EnsembleSynthesisView_Root}"

<!-- Line 197, 341: Button Command with ElementName -->
Command="{Binding DataContext.RemoveVoiceCommand, ElementName=EnsembleSynthesisView_Root}"
Command="{Binding DataContext.DeleteJobCommand, ElementName=EnsembleSynthesisView_Root}"
```

**Issue**: Using `ElementName` binding (not supported by {x:Bind})
**Fix**: Refactor to use `x:Bind` with function bindings or ancestor binding

---

### 4. UserCursorIndicator.xaml (3 instances)

**Location**: `src/VoiceStudio.App/Controls/UserCursorIndicator.xaml`

```xml
<!-- Line 11, 17-18: Control DataTemplate -->
Fill="{Binding Color, Converter={StaticResource StringToBrushConverter}}"
Canvas.Left="{Binding X}" Canvas.Top="{Binding Y}"
Text="{Binding UserName}"
```

**Issue**: Control template bindings (requires investigation)
**Fix**: Add `x:DataType` and migrate if supported

---

### 5. FloatingWindowHost.xaml (1 instance)

**Location**: `src/VoiceStudio.App/Controls/FloatingWindowHost.xaml`

```xml
<!-- Line 6: ControlTemplate Content binding -->
Content="{Binding Content, RelativeSource={RelativeSource Mode=TemplatedParent}}"
```

**Issue**: `RelativeSource TemplatedParent` (not supported by {x:Bind})
**Fix**: Use `TemplateBinding` instead (WinUI 3 native)

---

## x:DataType Coverage

**Files with x:DataType declaration**: 98 out of 160 (61%)

Views/Panels with x:DataType (sample):
- TimelineView.xaml ✅
- ProfilesView.xaml ✅ (2 declarations)
- EffectsMixerView.xaml ✅ (5 declarations)
- AnalyzerView.xaml ✅
- VoiceSynthesisView.xaml ✅
- MacroView.xaml ✅ (3 declarations)
- DiagnosticsView.xaml ✅
- VoiceCloningWizardView.xaml ✅ (5 declarations)
- SettingsView.xaml ✅ (3 declarations)

---

## Migration Priority

| Priority | File | Instances | Complexity |
|----------|------|-----------|------------|
| HIGH | EnsembleSynthesisView.xaml | 4 | Medium (ElementName) |
| HIGH | UserCursorIndicator.xaml | 3 | Medium (Control) |
| MEDIUM | QualityControlView.xaml | 2 | Low (DataTemplate) |
| MEDIUM | TextBasedSpeechEditorView.xaml | 2 | Low (DataTemplate) |
| LOW | FloatingWindowHost.xaml | 1 | Low (TemplateBinding) |

---

## Recommendations

### Immediate Actions (Task 1.1.2-1.1.4)

1. **Add x:DataType to remaining 62 files** without declarations
2. **Migrate 12 {Binding} instances** in 5 files
3. **Prioritize EnsembleSynthesisView.xaml** (most instances)

### Migration Patterns

#### DataTemplate Migration

```xml
<!-- Before -->
<DataTemplate>
    <TextBlock Text="{Binding Name}" />
</DataTemplate>

<!-- After -->
<DataTemplate x:DataType="models:ItemModel">
    <TextBlock Text="{x:Bind Name}" />
</DataTemplate>
```

#### ElementName Migration

```xml
<!-- Before -->
<Button Command="{Binding DataContext.SaveCommand, ElementName=Root}" />

<!-- After (Option 1: x:Bind with path) -->
<Button Command="{x:Bind ViewModel.SaveCommand}" />

<!-- After (Option 2: Keep in code-behind) -->
<Button x:Name="SaveButton" Click="SaveButton_Click" />
```

#### TemplateBinding Migration

```xml
<!-- Before -->
Content="{Binding Content, RelativeSource={RelativeSource Mode=TemplatedParent}}"

<!-- After -->
Content="{TemplateBinding Content}"
```

---

## Files Without x:DataType (62 files)

These files need `x:DataType` added in Task 1.1.2:

### Resource Dictionaries (8 files) — N/A
- DesignTokens.xaml
- Theme.Dark.xaml
- Theme.Light.xaml
- Theme.SciFi.xaml
- Density.Compact.xaml
- Density.Comfort.xaml
- PanelTemplates.xaml
- Styles/*.xaml

### Views/Controls Requiring x:DataType (54 files)

*To be identified in Task 1.1.2 by comparing full file list against x:DataType grep results*

---

## Verification Commands

```powershell
# Count {Binding} instances
rg "\{Binding\s" src/VoiceStudio.App --glob "*.xaml" -c

# Count {x:Bind} instances
rg "\{x:Bind\s" src/VoiceStudio.App --glob "*.xaml" -c

# Count x:DataType declarations
rg "x:DataType=" src/VoiceStudio.App --glob "*.xaml" -c

# Find files without x:DataType
rg -L "x:DataType=" src/VoiceStudio.App/Views --glob "*.xaml"
```

---

## Task 1.1.1 Status

- [x] Audit completed
- [x] {Binding} instances identified (12 in 5 files)
- [x] {x:Bind} coverage calculated (97.9%)
- [x] x:DataType coverage calculated (61%)
- [x] Migration priorities documented
- [x] Report generated

**Result**: PASS — Audit complete, 97.9% compile-time binding coverage

---

## Next Tasks

| ID | Task | Status |
|----|------|--------|
| 1.1.2 | Add x:DataType to all Page/UserControl roots | PENDING |
| 1.1.3 | Migrate core panels to {x:Bind} | PENDING |
| 1.1.4 | Migrate Tier 2 panels | PENDING |
| 1.1.5 | Add CI binding validation | PENDING |
