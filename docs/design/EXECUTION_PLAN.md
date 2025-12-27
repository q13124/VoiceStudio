# VoiceStudio Execution Plan
## Overseer + 8 Worker Agents

## Overview

This document provides a step-by-step implementation plan for building VoiceStudio using an Overseer agent (architect) coordinating 8 worker agents (implementers).

**Critical Principle**: This is a professional-grade studio application. Complexity is intentional. Do NOT simplify.

---

## Phase 0 – Ground Rules (Overseer Only)

### Overseer System Prompt

**Copy this into Cursor's architect agent:**

```
You are the Overseer/Architect for the VoiceStudio Quantum+ WinUI 3 desktop app.

Your job is to enforce the design spec in UI_IMPLEMENTATION_SPEC.md.

Do NOT allow any worker to simplify or collapse the UI, file structure, or component count.

PanelHost is mandatory and must not be replaced with raw grids.

Each panel (Profiles, Timeline, EffectsMixer, Analyzer, Macro, Diagnostics) must have its own .xaml, .xaml.cs, and ViewModel.cs.

Maintain the main window layout:
- Top: MenuBar + Command Toolbar
- Center: 4-column grid (Nav rail + 3 PanelHosts)
- Bottom: Status bar

Maintain the workspace grid with 2 rows (main + bottom deck) and 4 columns (nav + left + center + right).

Make sure DesignTokens.xaml exists and all visuals use VSQ.* resources.

Reject any attempt to "simplify for speed" or "merge files for convenience".

This application is a pro-grade studio UI, not a demo or toy; high density and complexity are required.

VIOLATION DETECTION:
- If you see merged View/ViewModel files → REVERT
- If you see PanelHost replaced with Grid → REVERT
- If you see reduced panel count → REVERT
- If you see hardcoded colors → REVERT
- If you see simplified layout → REVERT

REMEDIATION COMMAND:
"Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to CIS. Do not merge or collapse."
```

### Overseer Responsibilities

- **Verify** each phase completion
- **Check** for simplifications
- **Enforce** guardrails
- **Coordinate** worker dependencies
- **Review** file structure compliance

---

## Phase 1 – Project + Tokens

### Worker 1: Project & Tokens

#### Tasks

1. **Create Solution**
   - Create `VoiceStudio.sln` solution file
   - Add `VoiceStudio.App` project (WinUI 3 Desktop Application)
   - Target: .NET 8, Windows 10 version 1809 or later

2. **Create DesignTokens.xaml**
   - Location: `src/VoiceStudio.App/Resources/DesignTokens.xaml`
   - Include all color definitions:
     - `VSQ.Background.Darker`, `VSQ.Background.Dark`
     - `VSQ.Accent.Cyan`, `VSQ.Accent.Lime`, `VSQ.Accent.Magenta`
     - `VSQ.Text.Primary`, `VSQ.Text.Secondary`
     - `VSQ.Border.Subtle`, `VSQ.Warn`, `VSQ.Error`
   - Include brushes:
     - `VSQ.Window.Background` (LinearGradientBrush)
     - All solid color brushes
   - Include typography:
     - Font sizes: Caption (10), Body (12), Title (16), Heading (20)
     - TextBlock styles: `VSQ.Text.Body`, `VSQ.Text.Caption`, `VSQ.Text.Title`, `VSQ.Text.Heading`
   - Include constants:
     - `VSQ.CornerRadius.Panel` (8), `VSQ.CornerRadius.Button` (4)
     - `VSQ.Animation.Duration.Fast` (100), `VSQ.Animation.Duration.Medium` (150)

3. **Merge DesignTokens into App.xaml**
   - Open `App.xaml`
   - Add ResourceDictionary with MergedDictionaries
   - Reference: `ms-appx:///Resources/DesignTokens.xaml`

4. **Set MainWindow Background**
   - In `MainWindow.xaml`, set `Background="{StaticResource VSQ.Window.Background}"`

#### Deliverables

- ✅ Solution file created
- ✅ DesignTokens.xaml with all resources
- ✅ App.xaml merges DesignTokens
- ✅ MainWindow uses VSQ.Window.Background

### Overseer Checks

- [ ] Solution builds without errors
- [ ] All VSQ.* resources resolve (no XAML errors)
- [ ] MainWindow displays with gradient background
- [ ] No hardcoded colors in XAML

**If checks fail**: Worker 1 fixes issues before proceeding.

---

## Phase 2 – PanelHost Control

### Worker 2: PanelHost

#### Tasks

1. **Create PanelHost.xaml**
   - Location: `src/VoiceStudio.App/Controls/PanelHost.xaml`
   - Structure:
     ```xml
     <UserControl>
       <Grid>
         <Grid.RowDefinitions>
           <RowDefinition Height="32"/>  <!-- Header -->
           <RowDefinition Height="*"/>    <!-- Body -->
         </Grid.RowDefinitions>
         
         <!-- Header: Icon + Title + Action Buttons -->
         <Grid Grid.Row="0">
           <!-- Icon, Title, Pop-out, Collapse, Options buttons -->
         </Grid>
         
         <!-- Body: ContentPresenter in Border -->
         <Border Grid.Row="1" CornerRadius="8" BorderBrush="..." BorderThickness="1">
           <ContentPresenter Content="{Binding Content, ...}"/>
         </Border>
       </Grid>
     </UserControl>
     ```

2. **Create PanelHost.xaml.cs**
   - Location: `src/VoiceStudio.App/Controls/PanelHost.xaml.cs`
   - Dependency Properties:
     - `Title` (string)
     - `IconGlyph` (string)
     - `PanelContent` (UIElement) - for content binding
   - Event handlers for header buttons (stub for now)

3. **Style Header Elements**
   - Use VSQ design tokens for colors
   - Apply VSQ.Button.Icon style to action buttons
   - Use VSQ.Text.Body for title

#### Deliverables

- ✅ PanelHost.xaml with header and content area
- ✅ PanelHost.xaml.cs with dependency properties
- ✅ Header buttons (pop-out, collapse, options) - stubbed
- ✅ ContentPresenter properly bound

### Overseer Checks

- [ ] PanelHost compiles
- [ ] Can drop dummy content into test window
- [ ] Header displays with icon, title, buttons
- [ ] Content area displays assigned content
- [ ] Styling uses VSQ.* tokens

**Test**: Create a simple test window, assign content to PanelHost, verify it displays.

---

## Phase 3 – MainWindow Shell Wiring

### Worker 3: MainWindow Integration

#### Tasks

1. **Replace/Augment MainWindow.xaml**
   - Use the provided MainWindow.xaml skeleton exactly
   - Ensure structure:
     - 3-row main grid (Command Deck, Workspace, Status Bar)
     - Top Command Deck: MenuBar + Toolbar (4 columns)
     - Main Workspace: 4 columns (Nav rail 64px + Left 20% + Center 55% + Right 25%)
     - Main Workspace: 2 rows (Top * + Bottom 18%)
     - Left Nav Rail: 8 toggle buttons
     - 4 PanelHosts: LeftPanelHost, CenterPanelHost, RightPanelHost, BottomPanelHost
     - Status Bar: 3-column layout

2. **Create MainWindow.xaml.cs**
   - Location: `src/VoiceStudio.App/MainWindow.xaml.cs`
   - Minimal implementation:
     ```csharp
     public sealed partial class MainWindow : Window
     {
         public MainWindow()
         {
             this.InitializeComponent();
             
             // Dummy content assignment (temporary)
             // LeftPanelHost.Content = new ProfilesView();
             // CenterPanelHost.Content = new TimelineView();
             // etc.
         }
     }
     ```
   - **Note**: Panel content assignment will be done in Phase 4

3. **Verify Namespaces**
   - `xmlns:controls="using:VoiceStudio.App.Controls"`
   - All references resolve

#### Deliverables

- ✅ MainWindow.xaml matches skeleton exactly
- ✅ All 4 PanelHosts declared and named
- ✅ Navigation rail with 8 buttons
- ✅ Command deck with menu and toolbar
- ✅ Status bar with 3 columns
- ✅ MainWindow.xaml.cs compiles

### Overseer Checks

- [ ] MainWindow.xaml structure matches specification
- [ ] All PanelHosts exist and are properly named
- [ ] Grid layout: 3 rows, workspace has 4 columns + 2 rows
- [ ] Navigation rail visible
- [ ] Command deck visible
- [ ] Status bar visible
- [ ] Application runs (even with empty PanelHosts)
- [ ] No layout simplifications

**Visual Check**: Layout should look like the specification even with placeholder content.

---

## Phase 4 – Views & ViewModels (6 Panels)

### Worker 4: ProfilesView

#### Tasks

1. **Create ProfilesView.xaml**
   - Location: `src/VoiceStudio.App/Views/Panels/ProfilesView.xaml`
   - Use provided XAML skeleton exactly
   - Structure: Tabs (Profiles/Library) + Grid (Profiles + Detail panel)
   - ToggleButtons for Profiles/Library tabs
   - WrapGrid for profile cards (180×120)
   - Detail inspector panel (260px width)

2. **Create ProfilesView.xaml.cs**
   - Location: `src/VoiceStudio.App/Views/Panels/ProfilesView.xaml.cs`
   - Basic code-behind
   - Comment for DataContext wiring later

3. **Create ProfilesViewModel.cs**
   - Location: `src/VoiceStudio.App/Views/Panels/ProfilesViewModel.cs`
   - Implements `IPanelView` from VoiceStudio.Core
   - PanelId: "profiles"
   - DisplayName: "Profiles"
   - Region: PanelRegion.Left
   - Can start empty, will add properties later

#### Deliverables

- ✅ ProfilesView.xaml (matches skeleton)
- ✅ ProfilesView.xaml.cs
- ✅ ProfilesViewModel.cs (implements IPanelView)
- ✅ DataContext wired

---

### Worker 5: TimelineView

#### Tasks

1. **Create TimelineView.xaml**
   - Location: `src/VoiceStudio.App/Views/Panels/TimelineView.xaml`
   - Use provided XAML skeleton exactly
   - Structure: Toolbar (32px) + Tracks (*) + Visualizer (160px)

2. **Create TimelineView.xaml.cs**
   - Location: `src/VoiceStudio.App/Views/Panels/TimelineView.xaml.cs`

3. **Create TimelineViewModel.cs**
   - Location: `src/VoiceStudio.App/Views/Panels/TimelineViewModel.cs`
   - Implements `IPanelView`

4. **Wire DataContext**

#### Deliverables

- ✅ TimelineView.xaml (matches skeleton)
- ✅ TimelineView.xaml.cs
- ✅ TimelineViewModel.cs
- ✅ DataContext wired

---

### Worker 6: EffectsMixerView

#### Tasks

1. **Create EffectsMixerView.xaml**
   - Location: `src/VoiceStudio.App/Views/Panels/EffectsMixerView.xaml`
   - Use provided XAML skeleton exactly
   - Structure: Mixer (*) + FX Chain (0.4*)
   - Horizontal ScrollViewer with ItemsControl
   - Mixer strips with fader placeholder (140px height)
   - FX Chain placeholder at bottom

2. **Create EffectsMixerView.xaml.cs**
   - Basic code-behind
   - Comment for DataContext wiring later

3. **Create EffectsMixerViewModel.cs**
   - Implements `IPanelView`
   - PanelId: "effectsmixer"
   - DisplayName: "Effects & Mixer"
   - Region: PanelRegion.Right

#### Deliverables

- ✅ EffectsMixerView.xaml (matches skeleton)
- ✅ EffectsMixerView.xaml.cs
- ✅ EffectsMixerViewModel.cs
- ✅ DataContext wired

---

### Worker 7: AnalyzerView

#### Tasks

1. **Create AnalyzerView.xaml**
   - Location: `src/VoiceStudio.App/Views/Panels/AnalyzerView.xaml`
   - Use provided XAML skeleton exactly
   - Structure: TabControl (32px) + Chart area (*)
   - Tabs: Waveform, Spectral, Radar, Loudness, Phase
   - Chart placeholder with opacity 0.6

2. **Create AnalyzerView.xaml.cs**
   - Basic code-behind
   - Comment for DataContext wiring later

3. **Create AnalyzerViewModel.cs**
   - Implements `IPanelView`
   - PanelId: "analyzer"
   - DisplayName: "Analyzer"
   - Region: PanelRegion.Right

#### Deliverables

- ✅ AnalyzerView.xaml (matches skeleton)
- ✅ AnalyzerView.xaml.cs
- ✅ AnalyzerViewModel.cs
- ✅ DataContext wired

---

### Worker 8: MacroView + DiagnosticsView

#### Tasks

**MacroView:**
1. Create `MacroView.xaml`
   - Tabs: Macros / Automation (ToggleButtons)
   - Node graph placeholder with opacity 0.6
2. Create `MacroView.xaml.cs`
   - Basic code-behind
   - Comment for DataContext wiring later
3. Create `MacroViewModel.cs`
   - Implements `IPanelView`
   - PanelId: "macro"
   - DisplayName: "Macros"
   - Region: PanelRegion.Bottom

**DiagnosticsView:**
1. Create `DiagnosticsView.xaml`
   - Logs (0.6*): ListView with log entry template
   - Metrics (0.4*): CPU, GPU, RAM progress bars (160px width, 6px height)
2. Create `DiagnosticsView.xaml.cs`
   - Basic code-behind
   - Comment for DataContext wiring later
3. Create `DiagnosticsViewModel.cs`
   - Implements `IPanelView`
   - PanelId: "diagnostics"
   - DisplayName: "Diagnostics"
   - Region: PanelRegion.Bottom

#### Deliverables

- ✅ MacroView.xaml, .xaml.cs, MacroViewModel.cs
- ✅ DiagnosticsView.xaml, .xaml.cs, DiagnosticsViewModel.cs
- ✅ Both DataContexts wired

---

### Overseer: Phase 4 Completion

#### Tasks

1. **Update MainWindow.xaml.cs**
   - Assign panel content to hosts:
     ```csharp
     public MainWindow()
     {
         this.InitializeComponent();
         
         // Temporary content assignment (will be replaced with panel registry later)
         LeftPanelHost.Content = new ProfilesView();
         CenterPanelHost.Content = new TimelineView();
         RightPanelHost.Content = new EffectsMixerView();
         BottomPanelHost.Content = new MacroView();
     }
     ```
   - **Note:** This is temporary. Later, panel switching will go through PanelRegistry.

2. **Verify All Panels**
   - All 6 panels exist (separate files)
   - All ViewModels exist (separate files)
   - All implement IPanelView

3. **Build & Run**
   - Solution builds without errors
   - Application runs
   - All panel regions are filled
   - Scrollables work
   - Visual density matches spec (no huge unused voids)

#### Overseer Checks

- [ ] All 6 panels exist as separate files
- [ ] All 6 ViewModels exist as separate files
- [ ] No merged View/ViewModel files
- [ ] MainWindow assigns content to all 4 PanelHosts
- [ ] Application runs successfully
- [ ] All panel regions display content
- [ ] Layout matches specification
- [ ] No simplifications detected

**If simplifications detected**: Issue remediation command immediately.

---

## Phase 5 – Navigation Behavior & Panel Registry

### Worker 1: Nav Rail Logic

#### Tasks

1. **Create NavIconButton Control** (optional, can use ToggleButton for now)
   - Location: `src/VoiceStudio.App/Controls/NavIconButton.xaml`
   - Style: VSQ.Button.NavToggle
   - IconGlyph property

2. **Wire Navigation Handlers**
   - In MainWindow.xaml.cs, add Click handlers for nav buttons:
     ```csharp
     private void OnNavStudioClick(object sender, RoutedEventArgs e)
     {
         // Switch LeftPanelHost content
     }
     
     private void OnNavProfilesClick(object sender, RoutedEventArgs e)
     {
         LeftPanelHost.Content = new ProfilesView();
     }
     
     // etc. for each nav button
     ```

3. **Implement Panel Switching**
   - Each nav button switches appropriate PanelHost content
   - For now, simple switch statement (no registry yet)

#### Deliverables

- ✅ Navigation buttons wired with Click handlers
- ✅ Panel switching works
- ✅ Only one nav button active at a time

### Worker 2: PanelRegistry Skeleton

#### Tasks

1. **Create Core Library Project** (if not exists)
   - Location: `src/VoiceStudio.Core/`
   - Class library project

2. **Implement Panel System**
   - `PanelRegion.cs` (enum)
   - `IPanelView.cs` (interface)
   - `PanelDescriptor.cs` (class)
   - `IPanelRegistry.cs` (interface)
   - `PanelRegistry.cs` (implementation)

3. **Add Project Reference**
   - VoiceStudio.App references VoiceStudio.Core

#### Deliverables

- ✅ VoiceStudio.Core project created
- ✅ All panel registry interfaces/classes exist
- ✅ Project reference added
- ✅ Registry ready (not fully wired yet)

### Overseer Checks

- [ ] Navigation switching works
- [ ] PanelHost content changes correctly
- [ ] Layout does not break during switching
- [ ] PanelRegistry structure exists in Core
- [ ] No simplifications (complexity maintained)

---

## Phase 6 – Styles & Micro-Interactions

### Worker 3: Styles

#### Tasks

1. **Create Style Files**
   - `Resources/Styles/Controls.xaml`
   - `Resources/Styles/Text.xaml`
   - `Resources/Styles/Panels.xaml`

2. **Move Styles from DesignTokens**
   - Button styles → Controls.xaml
   - Text styles → Text.xaml
   - Panel-specific styles → Panels.xaml

3. **Create Nav Button Style**
   - `VSQ.Button.NavToggle` style
   - Hover state: lighter background + cyan border
   - Active state: cyan accent
   - Pressed state: darker background

4. **Apply Styles**
   - Nav buttons use VSQ.Button.NavToggle
   - All text uses VSQ.Text.* styles
   - All buttons use VSQ.Button.* styles
   - Panel borders use VSQ.Panel.BorderBrush

5. **Merge Style Files**
   - Add to App.xaml MergedDictionaries

#### Deliverables

- ✅ Style files created and organized
- ✅ Nav button style with hover/active states
- ✅ All styles use VSQ.* tokens
- ✅ Styles merged into App.xaml

### Overseer Checks

- [ ] Styles are used, not inline formatting
- [ ] Nav buttons have hover/active states
- [ ] All colors come from VSQ.* tokens
- [ ] No hardcoded styles
- [ ] Visual consistency maintained

---

## Phase 7 – Sanity Pass & Anti-Simplification

### Overseer: Final Verification

#### File Structure Check

- [ ] File tree matches specification exactly
- [ ] No merged "God files"
- [ ] Each panel has separate .xaml, .xaml.cs, ViewModel.cs
- [ ] PanelHost exists as separate control
- [ ] Core library separate from App

#### Panel Verification

- [ ] All 6 panels exist and are visually distinct
- [ ] Placeholder regions visible (waveform, spectrogram, node graph, charts)
- [ ] Each panel has its own ViewModel
- [ ] No panels merged or collapsed

#### MainWindow Verification

- [ ] 3-row main grid structure maintained
- [ ] Workspace has 4 columns (nav + left + center + right)
- [ ] Workspace has 2 rows (main + bottom)
- [ ] All 4 PanelHosts exist and are used
- [ ] Navigation rail present with 8 buttons
- [ ] Command deck present
- [ ] Status bar present

#### PanelHost Verification

- [ ] PanelHost is a UserControl, not replaced with Grid
- [ ] PanelHost has header (icon, title, buttons)
- [ ] PanelHost has content area
- [ ] PanelHost used for all panel regions

#### Design System Verification

- [ ] All colors use VSQ.* tokens
- [ ] All typography uses VSQ.Text.* styles
- [ ] All buttons use VSQ.Button.* styles
- [ ] No hardcoded values

#### Complexity Check

- [ ] Layout complexity maintained (3×2 grid)
- [ ] Panel count maintained (6 panels)
- [ ] File separation maintained (no merging)
- [ ] Control abstraction maintained (PanelHost not replaced)

### If Simplifications Detected

**Issue this command immediately:**

```
Revert simplifications. This UI is intentionally complex. Restore PanelHost and separate panel Views/ViewModels according to CIS. Do not merge or collapse.

Specific violations:
- [List specific violations found]

Required actions:
1. Restore PanelHost control (if replaced)
2. Separate merged View/ViewModel files
3. Restore panel count to 6
4. Restore 3×2 grid layout
5. Restore all placeholder regions
6. Use VSQ.* design tokens only
```

### Final Sign-Off

- [ ] All checks pass
- [ ] No simplifications detected
- [ ] Application runs successfully
- [ ] Visual layout matches specification
- [ ] File structure matches specification
- [ ] Ready for next phase (backend integration)

---

## Worker Assignment Summary

| Phase | Worker | Task |
|-------|--------|------|
| 1 | Worker 1 | Project + Tokens |
| 2 | Worker 2 | PanelHost Control |
| 3 | Worker 3 | MainWindow Shell |
| 4 | Worker 4 | ProfilesView |
| 4 | Worker 5 | TimelineView |
| 4 | Worker 6 | EffectsMixerView |
| 4 | Worker 7 | AnalyzerView |
| 4 | Worker 8 | MacroView + DiagnosticsView |
| 5 | Worker 1 | Nav Rail Logic |
| 5 | Worker 2 | PanelRegistry Skeleton |
| 6 | Worker 3 | Styles & Micro-Interactions |
| 7 | Overseer | Sanity Pass |

---

## Critical Reminders

1. **Never simplify** - Complexity is intentional
2. **Never merge** - Keep files separate
3. **Never replace PanelHost** - It's a reusable control
4. **Always use VSQ.* tokens** - No hardcoded values
5. **Always verify** - Overseer checks at each phase
6. **Always revert** - If simplifications detected

**This is a professional studio application. Treat it as such.**

