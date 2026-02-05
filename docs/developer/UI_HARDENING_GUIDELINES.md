# UI Hardening Guidelines

This document codifies best practices for WinUI 3 XAML development in VoiceStudio, focusing on patterns that reduce XAML compiler fragility and improve build reliability.

## Background

VoiceStudio uses WinUI 3 with Windows App SDK 1.8. The XAML compiler (XamlCompiler.exe) has known fragility issues that can cause silent build failures (exit code 1, no output.json). These guidelines help prevent such issues.

**Related Documentation:**
- [XAML Change Protocol](XAML_CHANGE_PROTOCOL.md) - Mandatory procedures for XAML changes
- [GitHub #10027](https://github.com/microsoft/microsoft-ui-xaml/issues/10027) - Can't get error output from XamlCompiler.exe
- [GitHub #10947](https://github.com/microsoft/microsoft-ui-xaml/issues/10947) - XamlCompiler.exe exits code 1 for Views subfolders

---

## 1. Project Structure

### 1.1 Flat Views Directory Structure

**Rule:** XAML files should be at most 2 levels deep under Views/.

```
✅ GOOD (flat structure):
Views/
├── Panels/
│   ├── SettingsView.xaml
│   ├── ProfilesView.xaml
│   └── TimelineView.xaml
├── Shell/
│   └── NavigationView.xaml
└── Dialogs/
    └── ToolbarCustomizationDialog.xaml

❌ BAD (nested structure - triggers GitHub #10947):
Views/
├── UI/
│   └── Panels/           <- Third level - XamlCompiler may fail silently
│       └── SettingsView.xaml
└── Features/
    └── Voice/
        └── CloneWizard.xaml  <- Fourth level - definitely problematic
```

**Rationale:** The WinAppSDK XAML compiler (as of Jan 2026) can fail silently when processing XAML files in deeply nested `Views/` subfolders.

### 1.2 Directory.Build.targets Protection

VoiceStudio has a build target `DetectNestedViewsXaml` that warns when deeply nested Views XAML is detected. To fail the build instead of warning:

```xml
<PropertyGroup>
  <EnableViewsSubfolderError>true</EnableViewsSubfolderError>
</PropertyGroup>
```

---

## 2. UserControl Extraction Patterns

### 2.1 When to Extract UserControls

Extract a section into a UserControl when:
- The section exceeds **150 lines** of XAML
- The section has **complex bindings** (3+ nested levels)
- The section is **reusable** across multiple views
- The section has **independent visual state** (hover, selected, disabled)

### 2.2 Extraction Guidelines

**Before (monolithic):**

```xml
<!-- SettingsView.xaml - 600+ lines -->
<StackPanel>
    <TextBlock Text="General Settings" Style="{StaticResource VSQ.Text.Title}" />
    <StackPanel Orientation="Horizontal">
        <TextBlock Text="Theme" />
        <ComboBox ItemsSource="{Binding Themes}" SelectedItem="{Binding SelectedTheme}" />
    </StackPanel>
    <StackPanel Orientation="Horizontal">
        <TextBlock Text="Language" />
        <ComboBox ItemsSource="{Binding Languages}" SelectedItem="{Binding SelectedLanguage}" />
    </StackPanel>
    <!-- ... 200 more lines of settings ... -->
    
    <TextBlock Text="Audio Settings" Style="{StaticResource VSQ.Text.Title}" />
    <!-- ... 200 more lines ... -->
</StackPanel>
```

**After (modular):**

```xml
<!-- SettingsView.xaml - orchestrator only -->
<ScrollViewer>
    <StackPanel>
        <local:GeneralSettingsSection DataContext="{Binding GeneralSettings}" />
        <local:AudioSettingsSection DataContext="{Binding AudioSettings}" />
        <local:EngineSettingsSection DataContext="{Binding EngineSettings}" />
    </StackPanel>
</ScrollViewer>
```

```xml
<!-- Controls/GeneralSettingsSection.xaml - focused, testable -->
<UserControl x:Class="VoiceStudio.App.Controls.GeneralSettingsSection">
    <StackPanel>
        <TextBlock Text="General Settings" Style="{StaticResource VSQ.Text.Title}" />
        <local:SettingRow Label="Theme" Value="{Binding Theme}" />
        <local:SettingRow Label="Language" Value="{Binding Language}" />
    </StackPanel>
</UserControl>
```

### 2.3 Large File Candidates for Extraction

Current large files that could benefit from extraction:

| File | Lines | Suggested Extraction |
|------|-------|---------------------|
| `Views/Panels/SettingsView.xaml` | 602 | Split by category: General, Audio, Engine, Performance |
| `Views/Panels/EffectsMixerView.xaml` | 552 | Extract: ChannelStrip, EffectsRack, MasterBus |
| `Views/Panels/QualityControlView.xaml` | 454 | Extract: MetricsPanel, QualityChart, AlertsPanel |
| `Views/Panels/VoiceCloningWizardView.xaml` | 451 | Extract each wizard step as UserControl |

---

## 3. ResourceDictionary Organization

### 3.1 Current Structure

VoiceStudio uses a consolidated design token approach:

```
Resources/
├── DesignTokens.xaml        # All tokens (colors, typography, spacing)
├── Theme.Dark.xaml          # Dark theme overrides
├── Theme.Light.xaml         # Light theme overrides
├── Theme.SciFi.xaml         # SciFi theme overrides
├── Density.Comfort.xaml     # Comfort density
├── Density.Compact.xaml     # Compact density
└── Styles/
    ├── Controls.xaml        # Control styles
    ├── Text.xaml            # Typography styles
    └── Panels.xaml          # Panel-specific styles
```

### 3.2 Splitting Guidelines (If Needed)

If XAML compiler instability persists, consider splitting `DesignTokens.xaml`:

```
Resources/
├── Tokens/
│   ├── Colors.xaml          # Color palette only
│   ├── Typography.xaml      # Font sizes, weights, families
│   ├── Spacing.xaml         # Margins, padding
│   └── CornerRadius.xaml    # Border radius values
└── DesignTokens.xaml        # Merge point (imports all Tokens/)
```

**Trade-off:** This adds complexity. Only implement if compiler issues recur.

### 3.3 ResourceDictionary Anti-Patterns

```xml
<!-- ❌ BAD: Circular reference (A merges B, B merges A) -->
<ResourceDictionary>
    <ResourceDictionary.MergedDictionaries>
        <ResourceDictionary Source="Styles.xaml" />  <!-- Styles.xaml also merges this -->
    </ResourceDictionary.MergedDictionaries>
</ResourceDictionary>

<!-- ❌ BAD: One giant merged dictionary -->
<ResourceDictionary>
    <ResourceDictionary.MergedDictionaries>
        <ResourceDictionary Source="Styles1.xaml" />
        <ResourceDictionary Source="Styles2.xaml" />
        <!-- 20+ merged dictionaries -->
    </ResourceDictionary.MergedDictionaries>
</ResourceDictionary>

<!-- ✅ GOOD: Hierarchical merge (leaf dictionaries merged into category dictionaries) -->
<ResourceDictionary>
    <ResourceDictionary.MergedDictionaries>
        <ResourceDictionary Source="Tokens/Colors.xaml" />
        <ResourceDictionary Source="Tokens/Typography.xaml" />
    </ResourceDictionary.MergedDictionaries>
    <!-- Additional resources at this level -->
</ResourceDictionary>
```

---

## 4. Binding Anti-Patterns

### 4.1 Deep RelativeSource Chains

```xml
<!-- ❌ BAD: Deep ancestor traversal (fragile, slow) -->
<TextBlock Text="{Binding DataContext.ParentViewModel.GrandparentViewModel.Settings.Name, 
                  RelativeSource={RelativeSource AncestorType=ListView, AncestorLevel=3}}" />

<!-- ✅ GOOD: Direct binding via DataContext -->
<TextBlock Text="{Binding SettingsName}" />

<!-- ✅ GOOD: Named element binding if needed -->
<TextBlock Text="{Binding ElementName=SettingsListView, Path=DataContext.SettingsName}" />
```

### 4.2 Complex Converter Chains

```xml
<!-- ❌ BAD: Multiple converters chained -->
<TextBlock Visibility="{Binding IsEnabled, 
                        Converter={StaticResource BoolToNot},
                        ConverterParameter={Binding OtherValue, Converter={StaticResource ValueToString}}}" />

<!-- ✅ GOOD: Single converter with logic in code-behind or ViewModel -->
<TextBlock Visibility="{Binding ComputedVisibility}" />
```

### 4.3 TemplateBinding Limitations

```xml
<!-- ❌ BAD: TemplateBinding in nested template (doesn't work reliably) -->
<ControlTemplate>
    <ContentPresenter>
        <ContentPresenter.ContentTemplate>
            <DataTemplate>
                <Border Background="{TemplateBinding Background}" />  <!-- FAILS -->
            </DataTemplate>
        </ContentPresenter.ContentTemplate>
    </ContentPresenter>
</ControlTemplate>

<!-- ✅ GOOD: Use Binding with RelativeSource -->
<ControlTemplate>
    <ContentPresenter>
        <ContentPresenter.ContentTemplate>
            <DataTemplate>
                <Border Background="{Binding Background, 
                        RelativeSource={RelativeSource TemplatedParent}}" />
            </DataTemplate>
        </ContentPresenter.ContentTemplate>
    </ContentPresenter>
</ControlTemplate>
```

---

## 5. XAML Compiler Configuration

### 5.1 UseXamlCompilerExecutable

VoiceStudio uses the external XAML compiler (not the in-process task):

```xml
<!-- Directory.Build.targets -->
<PropertyGroup>
  <UseXamlCompilerExecutable>true</UseXamlCompilerExecutable>
</PropertyGroup>
```

**Rationale:** The external compiler goes through our wrapper (`tools/xaml-compiler-wrapper.cmd`) which handles:
- False-positive exit code 1 detection (VS-0001 fix)
- Retry logic for transient file locks
- Debug logging for diagnosis

**Do NOT set `UseXamlCompilerExecutable=false`** unless you're prepared to resolve .NET loading issues with `System.Security.Permissions`.

### 5.2 Why External Compiler is Required

VoiceStudio requires `UseXamlCompilerExecutable=true` for three technical reasons:

**1. net472 Path Hardcoding**

The Windows App SDK build task hard-codes paths to `net472\XamlCompiler.exe` when resolving dependencies. When the task loader attempts to run the compiler in-process, it cannot find these assemblies because the net472 SDK path is not in the assembly probing path.

**2. System.Security.Permissions Loading Failure**

The in-process loader fails to resolve `System.Security.Permissions.dll`, a .NET Framework 4.7.2 dependency. This failure manifests as:
- WMC9999 errors ("Unknown error")
- Silent build failures (exit code 1, no output)
- Intermittent failures that appear non-deterministic

**3. Process Isolation**

Running XamlCompiler.exe as a separate process:
- Isolates assembly loading to the compiler process
- Avoids polluting MSBuild with net472 dependencies
- Enables VoiceStudio's wrapper to handle false-positive exit codes

**References:**
- [GitHub #10027](https://github.com/microsoft/microsoft-ui-xaml/issues/10027) - Can't get error output from XamlCompiler.exe
- [GitHub #10947](https://github.com/microsoft/microsoft-ui-xaml/issues/10947) - XamlCompiler.exe exits code 1 for Views subfolders
- [Stack Overflow: UseXamlCompilerExecutable=false issue](https://stackoverflow.com/questions/76851177/)

### 5.3 Single-Threaded Builds for Diagnosis

When debugging XAML compiler issues, always use single-threaded builds:

```powershell
# Single-threaded build eliminates race conditions
dotnet build VoiceStudio.sln -c Debug -p:Platform=x64 -m:1

# Or use the diagnostic script
.\scripts\build-with-binlog.ps1
```

Multi-threaded builds can mask or introduce race conditions that make XAML compiler problems appear intermittent.

---

## 6. Performance Considerations

### 6.1 Lazy Loading Complex Sections

For panels with multiple heavy sections, consider lazy loading:

```csharp
// ViewModel
public ICommand LoadAdvancedSettingsCommand => new RelayCommand(async () =>
{
    if (AdvancedSettings == null)
    {
        AdvancedSettings = await LoadAdvancedSettingsAsync();
    }
});
```

```xml
<!-- XAML -->
<Expander Header="Advanced Settings" Expanding="OnAdvancedExpanding">
    <ContentControl Content="{Binding AdvancedSettings}" />
</Expander>
```

### 6.2 Virtualization for Lists

Always use virtualization for lists with more than 20 items:

```xml
<!-- ✅ GOOD: Virtualized -->
<ListView ItemsSource="{Binding LargeCollection}"
          VirtualizingStackPanel.IsVirtualizing="True"
          VirtualizingStackPanel.VirtualizationMode="Recycling" />

<!-- ❌ BAD: StackPanel doesn't virtualize -->
<ItemsControl ItemsSource="{Binding LargeCollection}">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <StackPanel />  <!-- No virtualization! -->
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
</ItemsControl>
```

---

## 7. Quick Reference Checklist

Before committing XAML changes:

- [ ] XAML files are at most 2 levels deep under Views/
- [ ] No file exceeds 300 lines without justification
- [ ] No circular ResourceDictionary merges
- [ ] No deep RelativeSource chains (3+ levels)
- [ ] No TextElement.* attached properties on ContentPresenter
- [ ] No ObjectAnimationUsingKeyFrames targeting (Property.SubProperty)
- [ ] Build succeeds with single-threaded build: `dotnet build -m:1`
- [ ] XAML lint passes: `python scripts/lint_xaml.py`

---

## 8. Related Documentation

- [XAML Change Protocol](XAML_CHANGE_PROTOCOL.md) - Mandatory change procedures
- [Directory.Build.targets](../../Directory.Build.targets) - Build configuration
- [xaml-compiler-wrapper.cmd](../../tools/xaml-compiler-wrapper.cmd) - Compiler wrapper
- [build-with-binlog.ps1](../../scripts/build-with-binlog.ps1) - Diagnostic build script
- [analyze-binlog.ps1](../../scripts/analyze-binlog.ps1) - Binlog analysis tool
