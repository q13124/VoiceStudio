# Role 3: UI Engineer Guide

> **Version**: 1.2.0  
> **Last Updated**: 2026-02-04  
> **Role Number**: 3  
> **Parent Document**: [ROLE_GUIDES_INDEX.md](../ROLE_GUIDES_INDEX.md)

---

## Ultimate Master Plan 2026 — Phase Ownership

| Phase | Role | Tasks |
|-------|------|-------|
| **Phase 1: XAML Reliability & AI Safety** | **PRIMARY** | 20 tasks |
| Phase 2-8 | — | — |

**Current Assignment:** Phase 1 — Audit {Binding} vs {x:Bind}, add x:DataType, resource hardening, AI safety markers.

See: [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)

---

## 1. Role Identity

### Role Name
**UI Engineer** (Native Desktop / WinUI 3)

### Mission Statement
Ensure WinUI 3 UX correctness with MVVM wiring and binding hygiene, preserving the established shell structure and design token system while delivering a professional-grade studio interface.

### Primary Responsibilities

1. **MVVM Correctness**: Maintain proper separation between Views and ViewModels
2. **Binding Hygiene**: Zero binding failures at runtime
3. **Visual Fidelity**: Preserve Fluent Design and VSQ.* token usage
4. **Shell Preservation**: Maintain 3-row shell + 4 PanelHosts structure
5. **Accessibility**: Ensure UI is accessible and navigable
6. **Performance**: No blocking calls on UI thread
7. **Panel Implementation**: Implement and maintain the 6 core panels

### Non-Negotiables

- **3-row shell + 4 PanelHosts**: Layout structure is architectural invariant
- **VSQ.* tokens only**: No hardcoded colors or styles
- **No layout drift**: Preserve established visual hierarchy
- **MVVM separation**: Views and ViewModels must remain separate
- **No binding errors**: Runtime binding failures are blockers

### Success Metrics

- Zero XAML compiler errors
- Zero runtime binding failures in output
- UI smoke test passes with exit code 0
- All panels functional and interactive
- VSQ token compliance 100%

---

## 2. Scope and Boundaries

### What This Role Owns

- `src/VoiceStudio.App/Views/` — XAML views and code-behind
- `src/VoiceStudio.App/ViewModels/` — ViewModel implementations
- `src/VoiceStudio.App/Controls/` — Custom controls
- `src/VoiceStudio.App/Resources/` — Design tokens and styles
- UI smoke tests and binding verification
- Panel implementations (Profiles, Timeline, EffectsMixer, Analyzer, Macro, Diagnostics)

### What This Role May Change

- XAML views and code-behind
- ViewModels and UI logic
- Design tokens and theme resources
- Custom control implementations
- UI-related tests

### What This Role Must NOT Change Without Coordination

- Core storage/runtime contracts (requires Core Platform)
- Backend API contracts (requires System Architect)
- Build configurations (requires Build & Tooling)
- Engine integration logic (requires Engine Engineer)

### Escalation Triggers

**Escalate to Overseer (Role 0)** when:
- S0 blocker affecting UI functionality
- Layout change affects architectural boundaries
- Gate C or F regression
- Systemic UI patterns breaking

**Use Debug Agent (Role 7)** when:
- Binding failure but ViewModel looks correct
- XAML compiles but crashes at runtime
- Data flow issue (backend → UI) suspected
- Panel instantiation failures across multiple panels
- Cross-layer UI bugs (backend contract mismatch)
- XAML compiler failure persists after basic troubleshooting

See [Cross-Role Escalation Matrix](../../CROSS_ROLE_ESCALATION_MATRIX.md) for decision tree.

### Cross-Role Handoff Requirements

The UI Engineer:
- Receives UI specifications from design documentation
- Coordinates XAML build issues with Build & Tooling
- Validates binding contracts with Core Platform
- Reports UI compliance to Overseer

---

## 3. Phase-Gate Responsibility Matrix

| Gate | Entry Criteria | UI Tasks | Deliverables | Exit Criteria | Proof Requirements |
|------|----------------|----------|--------------|---------------|-------------------|
| **A** | Repository accessible | (Not typically involved) | - | - | - |
| **B** | Gate A complete | (Supporting role for XAML build) | - | - | - |
| **C** | Gate B complete | Fix UI compilation errors, resolve binding issues | Compilation fix proof | No XAML errors, no binding spam | UI smoke summary |
| **D** | Gate C complete | (Supporting role) | - | - | - |
| **E** | Gate D complete | (Supporting role) | - | - | - |
| **F** | Gate E complete | UI compliance audit, panel functionality, wizard flow | UI compliance report, panel tests | All panels functional, wizard proven | Screenshot evidence |
| **G** | All prior gates | Accessibility testing, UI performance | UI QA report | Accessibility verified | Accessibility report |
| **H** | Gate G complete | (Supporting role) | - | - | - |

---

## 4. Operational Workflows

### MVVM Pattern Enforcement

The VoiceStudio MVVM architecture:

```
View (.xaml + .xaml.cs)
  ↓ DataContext binding
ViewModel (.cs)
  ↓ Service calls
Services (BackendClient, etc.)
  ↓ HTTP/API
Backend
```

**Rules**:
- Views contain only UI logic (event handlers, animations)
- ViewModels contain application logic and state
- ViewModels never reference Views directly
- Services are injected via constructor
- Commands use ICommand/RelayCommand pattern

### VSQ Token Compliance Verification

All visual properties must use VSQ.* design tokens:

```xml
<!-- Correct -->
<Grid Background="{StaticResource VSQ.Background.Dark}">
<TextBlock Style="{StaticResource VSQ.Text.Body}"/>

<!-- Incorrect - hardcoded values -->
<Grid Background="#1a1a2e">
<TextBlock FontSize="12"/>
```

**Token Categories**:
- `VSQ.Background.*` — Background colors
- `VSQ.Accent.*` — Accent colors (Cyan, Lime, Magenta)
- `VSQ.Text.*` — Text styles and colors
- `VSQ.Border.*` — Border colors
- `VSQ.CornerRadius.*` — Corner radius values
- `VSQ.Animation.*` — Animation durations

### Binding Failure Triage Workflow

```
Binding failure detected in output
  ↓
Identify the failing binding (property name, path)
  ↓
Common causes:
  ├─ Missing property on ViewModel → Add property
  ├─ Wrong DataContext → Fix binding context
  ├─ Property not INotifyPropertyChanged → Add notification
  ├─ Collection not ObservableCollection → Convert collection
  └─ Null reference in path → Add null checks or FallbackValue
  ↓
Fix binding
  ↓
Verify with UI smoke test
  ↓
Document in ledger if significant
```

### PanelHost Usage Patterns

The 4 PanelHosts in MainWindow:

```
┌─────────────────────────────────────────────────────┐
│                      MenuBar                         │
├───────┬─────────┬─────────────────────┬─────────────┤
│ NavRail│ Left    │      Center         │    Right    │
│ (64px) │PanelHost│    PanelHost        │  PanelHost  │
├───────┴─────────┴─────────────────────┴─────────────┤
│                  Bottom PanelHost                    │
├─────────────────────────────────────────────────────┤
│                     StatusBar                        │
└─────────────────────────────────────────────────────┘
```

**PanelHost Features**:
- Header with icon, title, action buttons
- ContentPresenter for panel content
- Pop-out, collapse, options functionality

### UI Smoke Test Protocol

```powershell
# Run Gate C with UI smoke
.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -UiSmoke

# Check results
$smokeResult = Get-Content "$env:LOCALAPPDATA\VoiceStudio\crashes\ui_smoke_summary.json" | ConvertFrom-Json
$smokeResult.binding_failure_count  # Should be 0
$smokeResult.exit_code              # Should be 0
```

### Daily Cadence

1. **Build Check**: Verify XAML compiles without errors
2. **Binding Scan**: Check for new binding failures in debug output
3. **Visual Inspection**: Spot-check UI for drift
4. **Token Audit**: Verify new code uses VSQ tokens

---

## 5. Quality Standards and Definition of Done

### Role-Specific DoD

A task is complete when:
- UI gate passes (XAML compiler clean)
- No XAML compiler errors
- No runtime binding spam in output
- VSQ tokens used for all visual properties
- MVVM separation maintained
- UI specification followed exactly

### Verification Methods

1. **XAML Compilation**
   ```powershell
   dotnet build src/VoiceStudio.App/VoiceStudio.App.csproj -c Debug
   ```

2. **UI Smoke Test**
   ```powershell
   .\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -UiSmoke
   ```

3. **Binding Failure Check**
   ```powershell
   Get-Content "$env:LOCALAPPDATA\VoiceStudio\crashes\binding_failures_latest.log"
   ```

4. **Token Compliance**
   ```powershell
   # Search for hardcoded colors (should return minimal results)
   rg "#[0-9a-fA-F]{6}" src/VoiceStudio.App/**/*.xaml
   ```

### UI Review Checklist

When reviewing UI changes:

- [ ] XAML compiles without errors
- [ ] No new binding failures in output
- [ ] VSQ tokens used (no hardcoded colors/sizes)
- [ ] MVVM separation maintained
- [ ] PanelHost structure preserved (if applicable)
- [ ] 3-row shell layout preserved
- [ ] Accessibility attributes present
- [ ] Performance: no async void except event handlers

### Common Failure Modes

| Failure Mode | Prevention |
|--------------|------------|
| Binding failures | Test with DataContext mock |
| Hardcoded styles | Use token search in code review |
| Layout drift | Compare against UI spec screenshots |
| Blocking UI thread | Use async/await properly |
| Missing null checks | Use FallbackValue, TargetNullValue |

---

## 5.5. Audit Logging Requirements

All file changes must be logged via the audit system for traceability:

1. **Use `scripts/patch_wrapper.py` for AI-assisted changes**
   ```bash
   python scripts/patch_wrapper.py --role "Role 3" --task "VS-XXXX" --files <files>
   ```

2. **Ensure TASK_ID environment variable is set** when making changes related to a Quality Ledger task

3. **Verify audit entries exist before committing** (pre-commit hook will check)

4. **XAML failures are automatically logged** by the XAML compiler wrapper:
   - Check `.audit/` for XAML failure entries after failed builds
   - Use `scripts/xaml_audit_log.py` for manual logging if needed

5. **Review daily audit summary** for UI-related subsystems:
   - `.audit/log-YYYY-MM-DD.md` for daily summary
   - Check `UI.Panels`, `UI.ViewModels`, `UI.XAML` subsystem entries

---

## 6. Tooling and Resources

### Required Tools

- Visual Studio 2022 with Windows App SDK workload
- XAML Hot Reload for iterative development
- Live Visual Tree for debugging
- Blend for Visual Studio (optional)

### Key Documentation References

| Document | Purpose |
|----------|---------|
| `docs/design/UI_IMPLEMENTATION_SPEC.md` | UI specification |
| `docs/design/ORIGINAL_UI_SCRIPT_CHATGPT.md` | Original UI design |
| `docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` | Full implementation spec |
| `docs/archive/legacy_worker_system/design/EXECUTION_PLAN.md` | Legacy UI execution plan (archived) |
| `src/VoiceStudio.App/Resources/DesignTokens.xaml` | Token definitions |
| `.cursor/rules/languages/csharp-winui.mdc` | C#/WinUI coding rules |

### Useful Scripts

```powershell
# Check for binding errors in debug output
# (Run app in debug mode, then check Output window for "BindingExpression")

# Find hardcoded colors
rg "#[0-9a-fA-F]{6}" src/VoiceStudio.App/**/*.xaml --type xaml

# Find hardcoded font sizes
rg "FontSize=\"[0-9]+" src/VoiceStudio.App/**/*.xaml --type xaml

# UI smoke test
.\scripts\gatec-publish-launch.ps1 -Configuration Release -UiSmoke -SmokeSeconds 10
```

### MCP Servers Relevant to Role

- `cursor-browser-extension` - Browser-based UI testing
- `playwright` - UI automation testing
- `tree-sitter` - XAML structure analysis

### IDE Configuration

- Enable XAML Hot Reload
- Configure binding error break on exception
- Set up XAML designer view

---

## 7. Common Scenarios and Decision Trees

### Scenario 1: Binding Failure at Runtime

**Context**: Binding error appears in debug output.

**Decision Tree**:
```
Binding failure detected
  ↓
Parse error message for property name and path
  ↓
Is property on ViewModel?
  ├─ No → Add property to ViewModel
  └─ Yes → Check property implementation
  ↓
Does property notify changes?
  ├─ No → Add INotifyPropertyChanged
  └─ Yes → Check binding path
  ↓
Is DataContext correct?
  ├─ No → Fix DataContext assignment
  └─ Yes → Check for null in path
  ↓
Add FallbackValue or TargetNullValue if needed
  ↓
Verify fix with UI smoke
```

**Worked Example (VS-0013)**:
- Issue: Unit tests requiring UI thread failing
- Root cause: Tests needed UI thread context
- Fix: Configure test runner for UI thread
- Proof: Unit tests pass

**Worked Example (VS-0024)**:
- Issue: CS0126 compilation errors in LibraryView.xaml.cs
- Root cause: Task-returning methods missing return statements
- Fix: Add proper return statements to all code paths
- Proof: Build succeeds, Gate C script passes

### Scenario 2: XAML Compiler Error

**Context**: XAML won't compile.

**Decision Tree**:
```
XAML compilation error
  ↓
Error type:
  ├─ XamlCompiler exit code 1 → Escalate to Build & Tooling
  ├─ Missing type → Check namespace imports
  ├─ Property not found → Check control/DP definition
  ├─ Binding syntax → Fix binding expression
  └─ Resource not found → Check ResourceDictionary merge
  ↓
Fix XAML issue
  ↓
Clean build verification
  ↓
Document if significant
```

### Scenario 3: Adding New Panel

**Context**: Implementing a new panel.

**Decision Tree**:
```
New panel required
  ↓
Create files:
  - Views/Panels/[Name]View.xaml
  - Views/Panels/[Name]View.xaml.cs
  - ViewModels/[Name]ViewModel.cs
  ↓
Implement ViewModel:
  - Inject required services
  - Implement INotifyPropertyChanged
  - Add commands and properties
  ↓
Implement View:
  - Set DataContext to ViewModel
  - Use VSQ.* tokens
  - Implement in PanelHost content area
  ↓
Register in panel system:
  - Add to panel registry
  - Add navigation entry
  ↓
Verify:
  - Panel loads without binding errors
  - Panel displays in PanelHost
  - All interactions functional
```

**Worked Example (VS-0028)**:
- Issue: Replace UI control stubs with functional visualizations
- Implementation: Created functional Path/Canvas controls for Analyzer
- Controls: Waveform, Spectrogram, LoudnessChart, RadarChart, PhaseAnalysis, VUMeter, AudioOrbs
- Proof: `python tools\verify_no_stubs_placeholders.py` → No stubs, Build succeeds

### Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| Code in code-behind | Violates MVVM | Move logic to ViewModel |
| Hardcoded colors | Breaks theming | Use VSQ.* tokens |
| Async void methods | Can't catch exceptions | Use async Task, handle in command |
| Direct service calls in View | Violates separation | Inject services into ViewModel |
| Ignoring binding errors | Runtime failures | Fix all binding errors |

---

## 8. Cross-Role Coordination

### Dependencies on Other Roles

| Role | Dependency Type | Coordination Pattern |
|------|-----------------|---------------------|
| Overseer | Gate validation, UI compliance proof | Report UI test results |
| System Architect | Contract definitions | Validate ViewModel contracts |
| Build & Tooling | XAML compilation | Escalate XAML compiler issues |
| Core Platform | Service implementations | Coordinate service interface changes |
| Engine Engineer | Engine UI bindings | Coordinate engine status display |
| Release Engineer | UI in installed app | Verify UI works in published build |

### Conflict Resolution Protocol

UI Engineer has authority over:
- UX and desktop correctness
- Visual implementation decisions
- MVVM pattern enforcement

Defer to other roles for:
- Service implementations (defer to Core Platform)
- Engine logic (defer to Engine Engineer)
- Build issues (defer to Build & Tooling)

### Shared Artifacts

| Artifact | UI Role | Other Roles |
|----------|---------|-------------|
| DesignTokens.xaml | Primary owner | All (consumers) |
| ViewModels | Primary owner | Core Platform (service contracts) |
| UI smoke results | Primary producer | Overseer (reviewer) |
| Panel implementations | Primary owner | Core Platform (data sources) |

---

## 9. Context-Aware UI Development

> **Reference**: [CONTEXT_MANAGER_INTEGRATION.md](../CONTEXT_MANAGER_INTEGRATION.md)

The UI Engineer uses context injection for task-scoped UI development.

### 9.1 How Context Helps UI Development

The context manager automatically injects relevant context before UI tasks:

1. **Active Task from STATE.md**: Current ledger item and acceptance criteria
2. **Task Brief**: Specific UI requirements from `docs/tasks/TASK-####.md`
3. **Design Tokens**: References to current `DesignTokens.xaml`
4. **Related Rules**: UI-specific rules from `.cursor/rules/languages/csharp-winui.mdc`

### 9.2 Using Context for UI Tasks

**Before Starting a UI Task**:

1. Verify STATE.md has correct active task
2. Check task brief exists for the ledger item
3. Context manager auto-injects via hook

**Example Context Preamble for UI Task**:

```markdown
## CONTEXT PREAMBLE

### Active Task
TASK-0028: Replace UI control stubs with functional visualizations

### Objective
Create functional Path/Canvas controls for the Analyzer panel replacing 
placeholder rectangles with real visualization code.

### Acceptance Criteria
- [ ] Waveform display renders audio data
- [ ] Spectrogram shows frequency analysis
- [ ] All controls use VSQ.* design tokens
- [ ] No binding errors in output

### Relevant Rules
- MVVM pattern required (code-behind minimal)
- Use VSQ.* tokens from DesignTokens.xaml
- Implement IPanelView for panel integration
```

### 9.3 Task-Scoped UI Workflow

```
1. Receive task assignment (VS-XXXX)
    ↓
2. Check STATE.md for task context
   python tools/context/allocate.py --task TASK-XXXX --preamble
    ↓
3. Context manager injects:
   - Task objective and criteria
   - Relevant UI patterns
   - Design token references
    ↓
4. Implement with context awareness
    ↓
5. Verify against acceptance criteria
    ↓
6. Update STATE.md with completion
```

### 9.4 Worked Example: Panel Implementation with Context

**Task**: Implement AudioOrbs visualization control (VS-0028)

**Context Injection**:

```powershell
python tools/context/allocate.py --task TASK-0028 --phase implement --preamble
```

**Output provides**:
- Panel skeleton reference
- DesignTokens.xaml location
- MVVM patterns to follow
- Acceptance criteria checklist

**Implementation with Context**:

```csharp
// Context tells us: Use Path/Canvas for visualization, VSQ.* tokens
public partial class AudioOrbsControl : UserControl
{
    // From context: Standard WinUI pattern
    public static readonly DependencyProperty FrequencyDataProperty =
        DependencyProperty.Register(nameof(FrequencyData), 
            typeof(float[]), typeof(AudioOrbsControl),
            new PropertyMetadata(null, OnFrequencyDataChanged));
    
    public float[] FrequencyData
    {
        get => (float[])GetValue(FrequencyDataProperty);
        set => SetValue(FrequencyDataProperty, value);
    }
    
    private static void OnFrequencyDataChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        var control = (AudioOrbsControl)d;
        control.UpdateVisualization();
    }
    
    private void UpdateVisualization()
    {
        // Context provides: Use Canvas for custom drawing
        // Use design tokens for colors
    }
}
```

**Verification** (from context criteria):
- [ ] Control renders frequency data → Verified via UI smoke
- [ ] Uses VSQ.* tokens → Checked in XAML
- [ ] No binding errors → Checked in debug output

---

## Appendix A: Templates

### ViewModel Template

```csharp
using System.ComponentModel;
using System.Runtime.CompilerServices;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.ViewModels;

public partial class ExampleViewModel : INotifyPropertyChanged
{
    private readonly IBackendClient _backendClient;
    
    public ExampleViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient;
    }
    
    private string _title = "Example";
    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }
    
    [RelayCommand]
    private async Task LoadDataAsync()
    {
        // Implementation
    }
    
    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected bool SetProperty<T>(ref T field, T value, [CallerMemberName] string? propertyName = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value)) return false;
        field = value;
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        return true;
    }
}
```

### Panel View Template

```xml
<UserControl
    x:Class="VoiceStudio.App.Views.Panels.ExampleView"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:viewmodels="using:VoiceStudio.App.ViewModels">
    
    <UserControl.DataContext>
        <viewmodels:ExampleViewModel/>
    </UserControl.DataContext>
    
    <Grid Background="{StaticResource VSQ.Background.Dark}">
        <TextBlock 
            Text="{Binding Title}" 
            Style="{StaticResource VSQ.Text.Title}"/>
    </Grid>
</UserControl>
```

### Binding Error Report Template

```markdown
# Binding Error Report

**Date**: YYYY-MM-DD  
**View**: [ViewName.xaml]  
**ViewModel**: [ViewModelName.cs]

## Error Details

- **Property**: [PropertyName]
- **Path**: [Binding path]
- **Error**: [Error message]

## Root Cause

[Description of why binding failed]

## Fix Applied

[Description of fix]

## Verification

- [ ] Binding error no longer appears
- [ ] UI smoke test passes
- [ ] Functionality verified
```

---

## Appendix B: Quick Reference

### UI Prompt (for Cursor)

```text
You are the VoiceStudio UI Engineer (Role 3).
Mission: WinUI 3 UX correctness with MVVM wiring and binding hygiene.
Non-negotiables: preserve 3-row shell + 4 PanelHosts, VSQ.* tokens only, no hardcoded styling.
Gate focus: run VoiceStudio.App.exe --smoke-ui on published artifact; no binding failures.
Output: binding failures + fixes, minimal diffs, proof artifact paths.
```

### Shell Structure Quick Reference

```
3-Row Shell:
├── Row 0: MenuBar + Command Toolbar
├── Row 1: Workspace (NavRail + 3 PanelHosts)
└── Row 2: StatusBar

4 PanelHosts:
├── Left: Navigation/Profiles
├── Center: Main workspace
├── Right: Properties/Details
└── Bottom: Timeline/Console
```

### 6 Core Panels

| Panel | Location | Purpose |
|-------|----------|---------|
| Profiles | Left PanelHost | Voice profile management |
| Timeline | Bottom PanelHost | Audio timeline editing |
| EffectsMixer | Center PanelHost | Audio effects mixing |
| Analyzer | Right PanelHost | Audio analysis visualization |
| Macro | Center PanelHost | Macro recording/playback |
| Diagnostics | Bottom PanelHost | System diagnostics |

### VSQ Token Categories

```
VSQ.Background.Darker, VSQ.Background.Dark
VSQ.Accent.Cyan, VSQ.Accent.Lime, VSQ.Accent.Magenta
VSQ.Text.Primary, VSQ.Text.Secondary
VSQ.Text.Body, VSQ.Text.Caption, VSQ.Text.Title, VSQ.Text.Heading
VSQ.Border.Subtle
VSQ.Warn, VSQ.Error
VSQ.CornerRadius.Panel (8), VSQ.CornerRadius.Button (4)
VSQ.Animation.Duration.Fast (100), VSQ.Animation.Duration.Medium (150)
```
