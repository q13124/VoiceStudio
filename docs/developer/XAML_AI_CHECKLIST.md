# XAML AI Checklist

## Purpose

This checklist provides AI assistants with a quick reference for XAML changes in VoiceStudio. Use this before and after making any XAML modifications.

## Pre-Change Checklist

### Before Touching ANY XAML File

- [ ] **Create checkpoint**: `git stash push -u -m "pre-xaml-change"` or `git commit -m "WIP: checkpoint"`
- [ ] **Identify the change scope**: How many XAML files will be modified?
- [ ] **Read existing AI GUIDELINES**: Check the file header for any `AI GUIDELINES` comments
- [ ] **Verify x:DataType exists**: Every UserControl must have `x:DataType` on root element

### Before Modifying ResourceDictionary Files

- [ ] **Read the AI GUIDELINES comment block** at the top of the file
- [ ] **DO NOT DELETE** existing resource keys
- [ ] **DO NOT RENAME** existing resource keys
- [ ] **Verify merge order** if adding new ResourceDictionary (see §3.2 in UI_HARDENING_GUIDELINES.md)

### Before Modifying Panel Views

- [ ] **Confirm `x:DataType`** is present on `<UserControl>`
- [ ] **Confirm `d:DataContext`** is present for design-time support
- [ ] **Check for `d:Visibility`** on loading overlays, error displays, help overlays

## During-Change Checklist

### When Adding New Bindings

- [ ] **Use `{x:Bind}` over `{Binding}`** unless:
  - Element is a `<Run>` (Run.Text doesn't support x:Bind)
  - Binding uses `ElementName` (still requires Binding)
  - Binding is to `TemplatedParent` in a ControlTemplate
- [ ] **Specify `Mode=`** explicitly: `Mode=OneWay` or `Mode=TwoWay`
- [ ] **Add `FallbackValue`** for text bindings that may be null:
  - ErrorMessage bindings → `FallbackValue='An error occurred'`
  - StatusMessage bindings → `FallbackValue='Ready'`
  - Name bindings → `FallbackValue='Unnamed'`
  - Count bindings → `FallbackValue='0'`

### When Adding New DataTemplates

- [ ] **Always add `x:DataType`**:
  ```xml
  <DataTemplate x:DataType="models:VoiceProfile">
  ```
- [ ] **Use correct namespace alias** for the model type
- [ ] **All bindings inside use `{x:Bind}`**

### When Adding New Resources

- [ ] **Follow VSQ naming convention**: `VSQ.{Category}.{Name}` or `VSQ.{Category}.{Subcategory}.{Name}`
- [ ] **Add to correct file**:
  - Colors/Brushes/Sizes → `DesignTokens.xaml`
  - Text styles → `Styles/Text.xaml`
  - Button/Control styles → `Styles/Controls.xaml`
- [ ] **Run validation**: `python scripts/validate_xaml_resources.py`

### When Adding New UserControls

- [ ] **Add `x:DataType` on root `<UserControl>`**
- [ ] **Add design-time namespaces**:
  ```xml
  xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  mc:Ignorable="d"
  ```
- [ ] **Add `d:DataContext`** for ViewModel:
  ```xml
  d:DataContext="{d:DesignInstance Type=local:ExampleViewModel, IsDesignTimeCreatable=False}"
  ```
- [ ] **Add `d:Visibility` guards** to overlays and conditional content

## Post-Change Checklist

### After Every XAML Change

- [ ] **Build immediately**: `dotnet build VoiceStudio.sln -c Debug -p:Platform=x64`
- [ ] **Build succeeded?** If exit code 1 with no error → run diagnostics (see below)
- [ ] **No new warnings?** Check build output for new warnings

### After ResourceDictionary Changes

- [ ] **Run resource validation**: `python scripts/validate_xaml_resources.py`
- [ ] **Validation passed?** 0 missing resources

### Before Committing

- [ ] **Run XAML lint**: `python scripts/lint_xaml.py`
- [ ] **Run resource validation**: `python scripts/validate_xaml_resources.py`
- [ ] **Build clean**: 0 errors
- [ ] **Tests pass** (if applicable)

## Diagnostic Workflow

### When Build Exits Code 1 with No Error

```powershell
# Step 1: Create binlog
.\scripts\build-with-binlog.ps1

# Step 2: Analyze binlog
.\scripts\analyze-binlog.ps1

# Step 3: Binary search for problematic file
.\scripts\xaml-binary-search.ps1
```

**DO NOT** make additional changes until the issue is identified.

## Quick Reference: Forbidden Patterns

| Pattern | Why Forbidden | Alternative |
|---------|---------------|-------------|
| `TextElement.Foreground` on ContentPresenter | Crashes XAML compiler | Use `Foreground` directly |
| Animations targeting attached properties | Crashes XAML compiler | Target direct properties |
| Views/UI/Panels/*.xaml (3+ levels) | XamlCompiler bug #10947 | Max 2 levels under Views/ |
| `{Binding}` without Mode | Ambiguous binding | Always specify `Mode=` |
| DataTemplate without x:DataType | No compile-time checking | Always add x:DataType |
| Deleting VSQ.* resource keys | Breaks dependent XAML | Never delete, add aliases if needed |

## Quick Reference: Common Namespaces

| Purpose | Declaration |
|---------|-------------|
| Design-time blend | `xmlns:d="http://schemas.microsoft.com/expression/blend/2008"` |
| Markup compatibility | `xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"` |
| Local panels | `xmlns:local="using:VoiceStudio.App.Views.Panels"` |
| ViewModels | `xmlns:vm="using:VoiceStudio.App.ViewModels"` |
| Core models | `xmlns:models="using:VoiceStudio.Core.Models"` |
| Converters | `xmlns:converters="using:VoiceStudio.App.Converters"` |
| DesignTime data | `xmlns:designTime="using:VoiceStudio.App.DesignTime"` |

## Related Documentation

- `.cursor/rules/quality/xaml-safety.mdc` - Full XAML safety rules
- `docs/developer/XAML_CHANGE_PROTOCOL.md` - Change procedures
- `docs/developer/UI_HARDENING_GUIDELINES.md` - Best practices & merge order
- `docs/developer/XAML_DESIGN_TIME_GUIDE.md` - Design-time patterns

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-02-05 | Phase 1 XAML Reliability | Initial creation |
